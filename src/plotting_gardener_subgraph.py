import json
from typing import Any, Dict, List, Literal
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_edges, query_kg_nodes


class ObstacleComponents(BaseModel):
    external: str = ""
    interpersonal: str = ""
    internal: str = ""


class Obstacle(BaseModel):
    description: str = ""
    components: ObstacleComponents = Field(default_factory=ObstacleComponents)


class Choice(BaseModel):
    description: str = ""
    option_a: str = ""
    option_b: str = ""
    tests_core_contradiction: bool = False


class SceneParameters(BaseModel):
    pov_character_id: str = ""
    pov_character_name: str = ""
    arc_stage: str = ""
    dominant_emotional_state: str = ""
    scene_goal: str = ""
    obstacle: Obstacle = Field(default_factory=Obstacle)
    the_choice: Choice = Field(default_factory=Choice)
    projected_consequence_shape: str = ""
    character_logic_audit: str = ""


class SceneSynthesis(BaseModel):
    scene_parameters: SceneParameters


class GardenerPlottingState(TypedDict, total=False):
    pov_character_id: str
    chapter_context: int
    last_scene_outcome: str
    pacing_guidance: Dict[str, Any]
    include_foreshadowing_check: bool
    simultaneous_events: List[Dict[str, Any]]
    missing_required_fields: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    character_node: Dict[str, Any]
    knows_edges: List[Dict[str, Any]]
    involves_edges: List[Dict[str, Any]]
    plot_threads: List[Dict[str, Any]]
    cascade_chains: List[Dict[str, Any]]
    pending_payoffs: List[Dict[str, Any]]
    scene_parameters: Dict[str, Any]
    active_thread_flags: List[Dict[str, Any]]
    active_consequence_flags: List[Dict[str, Any]]
    foreshadowing_opportunity: Dict[str, Any]
    parameter_discrepancy_flag: str | None
    kg_context_used: Dict[str, Any]
    errors: List[str]
    summary: str


def _default_foreshadowing() -> Dict[str, Any]:
    return {
        "present": False,
        "payoff_id": "",
        "payoff_description": "",
        "organic_integration_note": "",
    }


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _build_subgraph(subagent: Any) -> Any:
    skill_content = progressive_skill_loader.invoke(
        {"skill_name": "gardener-plotting-system", "load_type": "full"}
    )
    llm = ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        temperature=subagent.llm_config.temperature,
        top_p=subagent.llm_config.top_p,
        top_k=subagent.llm_config.top_k,
    ).with_structured_output(SceneSynthesis)

    graph = StateGraph(GardenerPlottingState)

    def ingest_context(state: GardenerPlottingState) -> GardenerPlottingState:
        missing: List[str] = []
        for field in ("pov_character_id", "chapter_context", "last_scene_outcome"):
            if not state.get(field):
                missing.append(field)
        return {
            "missing_required_fields": missing,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required gardener plotting context fields: {', '.join(missing)}."
                if missing
                else None
            ),
            "include_foreshadowing_check": bool(state.get("include_foreshadowing_check", False)),
            "pacing_guidance": state.get("pacing_guidance", {}) or {},
            "simultaneous_events": state.get("simultaneous_events", []) or [],
            "errors": [],
            "foreshadowing_opportunity": _default_foreshadowing(),
        }

    def fetch_core_kg(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}
        chapter_context = int(state["chapter_context"])
        pov_character_id = state["pov_character_id"]
        errors: List[str] = list(state.get("errors", []))

        try:
            character_nodes = query_kg_nodes.invoke(
                {
                    "query": {"logical_id": pov_character_id, "type": "Character"},
                    "as_of_chapter": chapter_context,
                }
            )
            character_node = character_nodes[0] if character_nodes else {}
        except Exception as error:
            character_node = {}
            errors.append(f"Character query failed: {error}")

        try:
            knows_edges = query_kg_edges.invoke(
                {
                    "query": {"from": pov_character_id, "type": "KNOWS"},
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            knows_edges = []
            errors.append(f"KNOWS query failed: {error}")

        try:
            involves_edges = query_kg_edges.invoke(
                {
                    "query": {"to": pov_character_id, "type": "INVOLVES"},
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            involves_edges = []
            errors.append(f"INVOLVES query failed: {error}")

        source_ids = [edge.get("from", "") for edge in involves_edges if edge.get("from")]
        plot_threads: List[Dict[str, Any]] = []
        cascade_chains: List[Dict[str, Any]] = []

        if source_ids:
            try:
                plot_threads = query_kg_nodes.invoke(
                    {
                        "query": {"logical_id": {"$in": source_ids}, "type": "PlotThread"},
                        "as_of_chapter": chapter_context,
                    }
                )
            except Exception as error:
                errors.append(f"PlotThread query failed: {error}")
                plot_threads = []

            try:
                cascade_chains = query_kg_nodes.invoke(
                    {
                        "query": {"logical_id": {"$in": source_ids}, "type": "CascadeChain"},
                        "as_of_chapter": chapter_context,
                    }
                )
            except Exception as error:
                errors.append(f"CascadeChain query failed: {error}")
                cascade_chains = []

        kg_context_used = {
            "character_node_found": bool(character_node),
            "knows_edges_found": len(knows_edges),
            "active_threads_found": len(plot_threads),
            "cascade_chains_found": len(cascade_chains),
            "pending_payoffs_checked": False,
        }

        return {
            "character_node": character_node,
            "knows_edges": knows_edges,
            "involves_edges": involves_edges,
            "plot_threads": plot_threads,
            "cascade_chains": cascade_chains,
            "kg_context_used": kg_context_used,
            "errors": errors,
        }

    def fetch_payoffs(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}
        chapter_context = int(state["chapter_context"])
        errors: List[str] = list(state.get("errors", []))
        try:
            pending_payoffs = query_kg_nodes.invoke(
                {
                    "query": {"type": "Payoff", "properties.resolution_status": "Pending"},
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            pending_payoffs = []
            errors.append(f"Payoff query failed: {error}")
        updated_counts = dict(state.get("kg_context_used", {}))
        updated_counts["pending_payoffs_checked"] = True
        return {
            "pending_payoffs": pending_payoffs,
            "kg_context_used": updated_counts,
            "errors": errors,
        }

    def synthesize_scene(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}
        errors: List[str] = list(state.get("errors", []))
        character_props = state.get("character_node", {}).get("properties", {})
        fallback_scene = SceneParameters(
            pov_character_id=state.get("pov_character_id", ""),
            pov_character_name=character_props.get("full_name", ""),
            arc_stage=character_props.get("arc_stage", ""),
            dominant_emotional_state=character_props.get("emotional_state", ""),
            scene_goal="",
            obstacle=Obstacle(),
            the_choice=Choice(),
            projected_consequence_shape="",
            character_logic_audit="",
        )

        synthesis_payload = {
            "context": {
                "pov_character_id": state.get("pov_character_id", ""),
                "chapter_context": state.get("chapter_context"),
                "last_scene_outcome": state.get("last_scene_outcome", ""),
                "pacing_guidance": state.get("pacing_guidance", {}),
                "simultaneous_events": state.get("simultaneous_events", []),
                "include_foreshadowing_check": state.get("include_foreshadowing_check", False),
            },
            "kg_context": {
                "character_node": state.get("character_node", {}),
                "knows_edges": state.get("knows_edges", []),
                "plot_threads": state.get("plot_threads", []),
                "cascade_chains": state.get("cascade_chains", []),
                "pending_payoffs": state.get("pending_payoffs", []),
            },
        }

        prompt = (
            f"{skill_content}\n\n"
            "Return only structured JSON for scene_parameters with all required non-null nested fields.\n"
            "Do not write prose.\n\n"
            f"{_safe_json(synthesis_payload)}"
        )

        try:
            llm_result: SceneSynthesis = llm.invoke([HumanMessage(content=prompt)])
            scene_parameters = llm_result.scene_parameters.model_dump()
        except Exception as error:
            errors.append(f"Scene synthesis failed: {error}")
            scene_parameters = fallback_scene.model_dump()

        return {
            "scene_parameters": scene_parameters,
            "errors": errors,
        }

    def audit_character_logic(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}
        scene_params = dict(state.get("scene_parameters", {}))
        character_logic_audit = str(scene_params.get("character_logic_audit", "") or "").strip()
        discrepancy: str | None = None

        if not character_logic_audit:
            character_logic_audit = (
                "Character logic audit unavailable from model output; review recommended before scene construction."
            )
            discrepancy = "Missing character_logic_audit from synthesis output."

        if not state.get("character_node"):
            discrepancy = (
                "POV character node was not found at chapter_context; scene parameters may rely on incomplete context."
            )

        scene_params["character_logic_audit"] = character_logic_audit
        if not scene_params.get("obstacle"):
            scene_params["obstacle"] = Obstacle().model_dump()
        if not scene_params.get("the_choice"):
            scene_params["the_choice"] = Choice().model_dump()
        if "projected_consequence_shape" not in scene_params:
            scene_params["projected_consequence_shape"] = ""

        return {
            "scene_parameters": scene_params,
            "parameter_discrepancy_flag": discrepancy,
        }

    def derive_flags(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}
        thread_flags: List[Dict[str, Any]] = []
        for thread in state.get("plot_threads", []):
            thread_flags.append(
                {
                    "thread_id": thread.get("logical_id", ""),
                    "thread_name": thread.get("properties", {}).get("name", ""),
                    "touched_how": "advanced",
                }
            )

        consequence_flags: List[Dict[str, Any]] = []
        for chain in state.get("cascade_chains", []):
            remaining = chain.get("properties", {}).get("remaining_links", [])
            consequence_flags.append(
                {
                    "chain_id": chain.get("logical_id", ""),
                    "current_position": chain.get("properties", {}).get("current_position", ""),
                    "approaching_detonation": bool(remaining and len(remaining) <= 1),
                    "note": "Cascade chain remains active for this POV character.",
                }
            )

        foreshadowing = dict(state.get("foreshadowing_opportunity", _default_foreshadowing()))
        if state.get("include_foreshadowing_check"):
            pending_payoffs = state.get("pending_payoffs", [])
            if pending_payoffs:
                payoff = pending_payoffs[0]
                foreshadowing = {
                    "present": True,
                    "payoff_id": payoff.get("logical_id", ""),
                    "payoff_description": payoff.get("properties", {}).get("description", ""),
                    "organic_integration_note": (
                        "Use a sensory or situational echo tied to the current pressure so foreshadowing stays organic."
                    ),
                }
            else:
                foreshadowing = _default_foreshadowing()

        return {
            "active_thread_flags": thread_flags,
            "active_consequence_flags": consequence_flags,
            "foreshadowing_opportunity": foreshadowing,
        }

    def package_response(state: GardenerPlottingState) -> GardenerPlottingState:
        if state.get("terminal_status"):
            return {}

        discrepancy = state.get("parameter_discrepancy_flag")
        summary = "Generated scene parameters using gardener-plotting-system subgraph."
        if discrepancy:
            summary = "Generated scene parameters with a discrepancy flag requiring brain review."
        if state.get("errors"):
            summary = "Generated scene parameters with recoverable subgraph warnings."
        return {"summary": summary}

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("fetch_core_kg", fetch_core_kg)
    graph.add_node("fetch_payoffs", fetch_payoffs)
    graph.add_node("synthesize_scene", synthesize_scene)
    graph.add_node("audit_character_logic", audit_character_logic)
    graph.add_node("derive_flags", derive_flags)
    graph.add_node("package_response", package_response)

    graph.add_edge(START, "ingest_context")
    graph.add_edge("ingest_context", "fetch_core_kg")

    def route_after_core_kg(state: GardenerPlottingState) -> Literal["fetch_payoffs", "synthesize_scene"]:
        if state.get("include_foreshadowing_check"):
            return "fetch_payoffs"
        return "synthesize_scene"

    graph.add_conditional_edges(
        "fetch_core_kg",
        route_after_core_kg,
        {"fetch_payoffs": "fetch_payoffs", "synthesize_scene": "synthesize_scene"},
    )
    graph.add_edge("fetch_payoffs", "synthesize_scene")
    graph.add_edge("synthesize_scene", "audit_character_logic")
    graph.add_edge("audit_character_logic", "derive_flags")
    graph.add_edge("derive_flags", "package_response")
    graph.add_edge("package_response", END)

    return graph.compile()


def run_gardener_plotting_subgraph(subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {})
    context = worker_request.get("context", {})

    initial_state: GardenerPlottingState = {
        "pov_character_id": context.get("pov_character_id", ""),
        "chapter_context": context.get("chapter_context", 0),
        "last_scene_outcome": context.get("last_scene_outcome", ""),
        "pacing_guidance": context.get("pacing_guidance", {}) or {},
        "include_foreshadowing_check": bool(context.get("include_foreshadowing_check", False)),
        "simultaneous_events": context.get("simultaneous_events", []) or [],
    }

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})

        missing_fields = graph_result.get("missing_required_fields", [])
        if missing_fields:
            structured_result = WorkerResponse(
                status="need_input",
                summary=graph_result.get("terminal_summary", "Missing required gardener plotting context."),
                artifacts={
                    "error": "missing_required_fields",
                    "missing_fields": missing_fields,
                    "scene_parameters": SceneParameters().model_dump(),
                    "active_thread_flags": [],
                    "active_consequence_flags": [],
                    "foreshadowing_opportunity": _default_foreshadowing(),
                    "kg_context_used": {
                        "character_node_found": False,
                        "knows_edges_found": 0,
                        "active_threads_found": 0,
                        "cascade_chains_found": 0,
                        "pending_payoffs_checked": False,
                    },
                    "parameter_discrepancy_flag": "",
                },
            ).model_dump()
        else:
            artifacts = {
                "skills_used": ["gardener-plotting-system"],
                "scene_parameters": graph_result.get("scene_parameters", SceneParameters().model_dump()),
                "active_thread_flags": graph_result.get("active_thread_flags", []),
                "active_consequence_flags": graph_result.get("active_consequence_flags", []),
                "foreshadowing_opportunity": graph_result.get(
                    "foreshadowing_opportunity", _default_foreshadowing()
                ),
                "kg_context_used": graph_result.get(
                    "kg_context_used",
                    {
                        "character_node_found": False,
                        "knows_edges_found": 0,
                        "active_threads_found": 0,
                        "cascade_chains_found": 0,
                        "pending_payoffs_checked": False,
                    },
                ),
                "parameter_discrepancy_flag": graph_result.get("parameter_discrepancy_flag"),
                "warnings": graph_result.get("errors", []),
            }
            structured_result = WorkerResponse(
                status="success",
                summary=graph_result.get("summary", "Generated scene parameters via gardener plotting subgraph."),
                artifacts=artifacts,
            ).model_dump()
    except Exception as error:
        structured_result = WorkerResponse(
            status="failed",
            summary=f"Worker execution failed: {error}",
            artifacts={"error": str(error)},
        ).model_dump()

    worker_record = {
        "worker": subagent.name,
        "task": worker_request.get("task", ""),
        "context": context,
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }
