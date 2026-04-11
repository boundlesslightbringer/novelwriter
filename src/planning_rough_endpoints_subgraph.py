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
from src.world_bible_tools import query_kg_nodes


class PrologueSpecification(BaseModel):
    warranted: bool = False
    temporal_relationship: str = ""
    pov_or_register: str = ""
    what_it_establishes: str = ""
    what_it_withholds: str = ""
    relationship_to_milestones: str = ""


class DraftMilestone(BaseModel):
    milestone_id: str = ""
    description: str = ""
    character_slots: List[str] = Field(default_factory=list)


class CharacterSlotSketch(BaseModel):
    slot_id: str = ""
    narrative_role: str = ""
    implied_contradiction: str = ""
    stakes: str = ""
    world_context: str = ""
    open_questions: List[str] = Field(default_factory=list)


class Pass1Output(BaseModel):
    prologue_specification: PrologueSpecification = Field(default_factory=PrologueSpecification)
    starting_situation: str = ""
    draft_ending_destination: str = ""
    draft_milestones: List[DraftMilestone] = Field(default_factory=list)
    character_slot_sketches: List[CharacterSlotSketch] = Field(default_factory=list)
    draft_core_conflict_question: str = ""
    compass_notes: str = ""


class FinalMilestone(BaseModel):
    milestone_id: str = ""
    description: str = ""
    character_references: List[str] = Field(default_factory=list)


class KgNodeSeed(BaseModel):
    node_type: str = ""
    properties: Dict[str, Any] = Field(default_factory=dict)


class Pass2Output(BaseModel):
    prologue_specification: PrologueSpecification = Field(default_factory=PrologueSpecification)
    starting_situation: str = ""
    ending_destination: str = ""
    milestones: List[FinalMilestone] = Field(default_factory=list)
    core_conflict_question: str = ""
    compass_notes: str = ""
    plot_thread_seeds: List[KgNodeSeed] = Field(default_factory=list)
    payoff_seeds: List[KgNodeSeed] = Field(default_factory=list)


class RoughEndpointsState(TypedDict, total=False):
    context: Dict[str, Any]
    skill_content: str
    chapter_context: int
    reassess_mode: bool
    run_pass: int
    missing_required_fields: List[str]
    follow_up_questions: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    reassess_context: Dict[str, Any]
    warnings: List[str]
    pass_1_artifacts: Dict[str, Any]
    pass_2_artifacts: Dict[str, Any]
    summary: str


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _normalize_string_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    normalized: List[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def _build_llm(subagent: Any) -> ChatGoogleGenerativeAI:
    kwargs: Dict[str, Any] = {
        "temperature": subagent.llm_config.temperature,
    }
    if subagent.llm_config.top_p is not None:
        kwargs["top_p"] = subagent.llm_config.top_p
    if subagent.llm_config.top_k is not None:
        kwargs["top_k"] = subagent.llm_config.top_k
    return ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        **kwargs,
    )


def _build_subgraph(subagent: Any) -> Any:
    llm = _build_llm(subagent)
    skill_content = progressive_skill_loader.invoke(
        {"skill_name": "defining-rough-endpoints", "load_type": "full"}
    )
    pass1_llm = llm.with_structured_output(Pass1Output)
    pass2_llm = llm.with_structured_output(Pass2Output)
    graph = StateGraph(RoughEndpointsState)

    def ingest_context(state: RoughEndpointsState) -> RoughEndpointsState:
        context = state.get("context", {}) or {}
        chapter_context = int(context.get("chapter_context", 0) or 0)
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        pass_hint = context.get("pass")
        reassess_mode = bool(context.get("reassess", False)) or operation_hint == "reassess"
        missing: List[str] = []
        follow_up_questions: List[str] = []

        run_pass = 0
        if str(pass_hint).strip() == "2" or skill_hint in {
            "defining-rough-endpoints-pass-2",
            "defining_rough_endpoints_pass_2",
        }:
            run_pass = 2
        elif str(pass_hint).strip() == "1":
            run_pass = 1
        elif context.get("character_concepts") and context.get("pass_1_output"):
            run_pass = 2
        else:
            run_pass = 1

        if run_pass == 1 and not isinstance(context.get("seed_document"), dict):
            missing.append("seed_document")
            follow_up_questions.append(
                "Please provide the validated seed_document from finding-a-seed to run rough endpoints Pass 1."
            )

        if run_pass == 2:
            if not isinstance(context.get("pass_1_output"), dict):
                missing.append("pass_1_output")
                follow_up_questions.append(
                    "Please provide pass_1_output from defining-rough-endpoints Pass 1."
                )
            if not isinstance(context.get("character_concepts"), list) or not context.get(
                "character_concepts"
            ):
                missing.append("character_concepts")
                follow_up_questions.append(
                    "Please provide non-empty character_concepts for Pass 2 refinement."
                )

        return {
            "skill_content": skill_content,
            "chapter_context": chapter_context,
            "reassess_mode": reassess_mode,
            "run_pass": run_pass,
            "missing_required_fields": missing,
            "follow_up_questions": follow_up_questions,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required context for defining-rough-endpoints pass {run_pass}: {', '.join(missing)}."
                if missing
                else None
            ),
            "reassess_context": {},
            "warnings": [],
        }

    def fetch_reassess_context(state: RoughEndpointsState) -> RoughEndpointsState:
        if state.get("terminal_status"):
            return {}
        if not state.get("reassess_mode"):
            return {"reassess_context": {}}

        chapter_context = int(state.get("chapter_context", 0))
        warnings: List[str] = list(state.get("warnings", []))
        reassess_context: Dict[str, Any] = {}
        try:
            reassess_context["plot_threads"] = query_kg_nodes.invoke(
                {"query": {"type": "PlotThread"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            reassess_context["plot_threads"] = []
            warnings.append(f"Reassess PlotThread query failed: {error}")

        try:
            reassess_context["chapters"] = query_kg_nodes.invoke(
                {"query": {"type": "Chapter"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            reassess_context["chapters"] = []
            warnings.append(f"Reassess Chapter query failed: {error}")

        try:
            reassess_context["characters"] = query_kg_nodes.invoke(
                {"query": {"type": "Character"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            reassess_context["characters"] = []
            warnings.append(f"Reassess Character query failed: {error}")

        return {"reassess_context": reassess_context, "warnings": warnings}

    def run_pass_1(state: RoughEndpointsState) -> RoughEndpointsState:
        if state.get("terminal_status") or state.get("run_pass") != 1:
            return {}
        context = state.get("context", {})
        prompt_payload = {
            "mode": "pass_1",
            "seed_document": context.get("seed_document", {}),
            "research_output": context.get("research_output", {}),
            "thematic_constraints": context.get("thematic_constraints", {}),
            "reassess_context": state.get("reassess_context", {}),
        }
        prompt = (
            f"{state.get('skill_content', '')}\n\n"
            "Generate Pass 1 output only. Return strict structured JSON with non-null nested fields.\n"
            "Do not run Pass 2 in this invocation.\n\n"
            f"{_safe_json(prompt_payload)}"
        )
        pass_1_output: Pass1Output = pass1_llm.invoke([HumanMessage(content=prompt)])

        milestones = pass_1_output.draft_milestones or []
        slot_sketches = pass_1_output.character_slot_sketches or []
        normalized_milestones: List[Dict[str, Any]] = []
        for index, milestone in enumerate(milestones, start=1):
            milestone_id = milestone.milestone_id.strip() or f"M{index}"
            normalized_milestones.append(
                {
                    "milestone_id": milestone_id,
                    "description": milestone.description.strip(),
                    "character_slots": _normalize_string_list(milestone.character_slots),
                }
            )
        normalized_slots: List[Dict[str, Any]] = []
        for index, slot in enumerate(slot_sketches, start=1):
            slot_id = slot.slot_id.strip() or f"slot_{index}"
            normalized_slots.append(
                {
                    "slot_id": slot_id,
                    "narrative_role": slot.narrative_role.strip(),
                    "implied_contradiction": slot.implied_contradiction.strip(),
                    "stakes": slot.stakes.strip(),
                    "world_context": slot.world_context.strip(),
                    "open_questions": _normalize_string_list(slot.open_questions),
                }
            )

        if not normalized_milestones:
            normalized_milestones = [
                {
                    "milestone_id": "M1",
                    "description": "Placeholder milestone awaiting refinement.",
                    "character_slots": ["slot_1"],
                }
            ]
        if not normalized_slots:
            normalized_slots = [
                {
                    "slot_id": "slot_1",
                    "narrative_role": "Primary viewpoint role to be conceived.",
                    "implied_contradiction": "Contradiction to be discovered.",
                    "stakes": "Stakes to be refined with character conception.",
                    "world_context": "World context pending refinement.",
                    "open_questions": ["What fear shapes this character's choices?"],
                }
            ]

        return {
            "pass_1_artifacts": {
                "pass": 1,
                "prologue_specification": pass_1_output.prologue_specification.model_dump(),
                "starting_situation": pass_1_output.starting_situation.strip(),
                "draft_ending_destination": pass_1_output.draft_ending_destination.strip(),
                "draft_milestones": normalized_milestones,
                "character_slot_sketches": normalized_slots,
                "draft_core_conflict_question": pass_1_output.draft_core_conflict_question.strip(),
                "compass_notes": pass_1_output.compass_notes.strip(),
            }
        }

    def run_pass_2(state: RoughEndpointsState) -> RoughEndpointsState:
        if state.get("terminal_status") or state.get("run_pass") != 2:
            return {}
        context = state.get("context", {})
        prompt_payload = {
            "mode": "pass_2",
            "pass_1_output": context.get("pass_1_output", {}),
            "character_concepts": context.get("character_concepts", []),
            "reassess_context": state.get("reassess_context", {}),
        }
        prompt = (
            f"{state.get('skill_content', '')}\n\n"
            "Generate Pass 2 output only. Return strict structured JSON with non-null nested fields.\n"
            "Include KG-ready plot_thread_seeds and payoff_seeds.\n\n"
            f"{_safe_json(prompt_payload)}"
        )
        pass_2_output: Pass2Output = pass2_llm.invoke([HumanMessage(content=prompt)])

        milestones = pass_2_output.milestones or []
        normalized_milestones: List[Dict[str, Any]] = []
        for index, milestone in enumerate(milestones, start=1):
            milestone_id = milestone.milestone_id.strip() or f"M{index}"
            normalized_milestones.append(
                {
                    "milestone_id": milestone_id,
                    "description": milestone.description.strip(),
                    "character_references": _normalize_string_list(
                        milestone.character_references
                    ),
                }
            )
        if not normalized_milestones:
            normalized_milestones = [
                {
                    "milestone_id": "M1",
                    "description": "Placeholder refined milestone awaiting character detail.",
                    "character_references": [],
                }
            ]

        plot_thread_seeds = [seed.model_dump() for seed in pass_2_output.plot_thread_seeds]
        payoff_seeds = [seed.model_dump() for seed in pass_2_output.payoff_seeds]
        if not plot_thread_seeds:
            plot_thread_seeds = [
                {
                    "node_type": "PlotThread",
                    "properties": {
                        "name": normalized_milestones[0]["description"] or "Initial plot thread",
                        "status": "Active",
                        "originating_chapter": 0,
                    },
                }
            ]
        if not payoff_seeds:
            payoff_seeds = [
                {
                    "node_type": "Payoff",
                    "properties": {
                        "type": "Foreshadowing",
                        "description": "Initial payoff seed from refined milestones.",
                        "planted_in_chapter": 0,
                        "resolution_status": "Pending",
                    },
                }
            ]

        return {
            "pass_2_artifacts": {
                "pass": 2,
                "prologue_specification": pass_2_output.prologue_specification.model_dump(),
                "starting_situation": pass_2_output.starting_situation.strip(),
                "ending_destination": pass_2_output.ending_destination.strip(),
                "milestones": normalized_milestones,
                "core_conflict_question": pass_2_output.core_conflict_question.strip(),
                "compass_notes": pass_2_output.compass_notes.strip(),
                "plot_thread_seeds": plot_thread_seeds,
                "payoff_seeds": payoff_seeds,
            }
        }

    def package_response(state: RoughEndpointsState) -> RoughEndpointsState:
        if state.get("terminal_status"):
            return {}
        warnings = list(state.get("warnings", []))
        pass_number = int(state.get("run_pass", 0))
        summary = (
            f"Generated defining-rough-endpoints pass {pass_number} artifacts via planning subgraph."
        )
        if warnings:
            summary = (
                f"Generated defining-rough-endpoints pass {pass_number} artifacts with reassess warnings."
            )
        return {"summary": summary}

    def package_need_input(state: RoughEndpointsState) -> RoughEndpointsState:
        return {
            "summary": state.get("terminal_summary", "Missing required context for defining-rough-endpoints.")
        }

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("fetch_reassess_context", fetch_reassess_context)
    graph.add_node("run_pass_1", run_pass_1)
    graph.add_node("run_pass_2", run_pass_2)
    graph.add_node("package_response", package_response)
    graph.add_node("package_need_input", package_need_input)

    graph.add_edge(START, "ingest_context")

    def route_after_ingest(
        state: RoughEndpointsState,
    ) -> Literal["package_need_input", "fetch_reassess_context"]:
        if state.get("terminal_status"):
            return "package_need_input"
        return "fetch_reassess_context"

    graph.add_conditional_edges(
        "ingest_context",
        route_after_ingest,
        {
            "package_need_input": "package_need_input",
            "fetch_reassess_context": "fetch_reassess_context",
        },
    )

    def route_after_reassess(
        state: RoughEndpointsState,
    ) -> Literal["run_pass_1", "run_pass_2"]:
        if int(state.get("run_pass", 1)) == 2:
            return "run_pass_2"
        return "run_pass_1"

    graph.add_conditional_edges(
        "fetch_reassess_context",
        route_after_reassess,
        {
            "run_pass_1": "run_pass_1",
            "run_pass_2": "run_pass_2",
        },
    )

    graph.add_edge("run_pass_1", "package_response")
    graph.add_edge("run_pass_2", "package_response")
    graph.add_edge("package_response", END)
    graph.add_edge("package_need_input", END)
    return graph.compile()


def run_rough_endpoints_subgraph(
    subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}
    initial_state: RoughEndpointsState = {"context": context}

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})

        missing = graph_result.get("missing_required_fields", [])
        if missing:
            structured_result = WorkerResponse(
                status="need_input",
                summary=graph_result.get(
                    "terminal_summary",
                    "Missing required context for defining-rough-endpoints.",
                ),
                artifacts={
                    "skill_attempted": "defining-rough-endpoints",
                    "error": "missing_required_context",
                    "missing_fields": missing,
                },
                follow_up_questions=graph_result.get("follow_up_questions", []),
            ).model_dump()
        else:
            run_pass = int(graph_result.get("run_pass", 1))
            artifacts = (
                graph_result.get("pass_2_artifacts", {})
                if run_pass == 2
                else graph_result.get("pass_1_artifacts", {})
            )
            artifacts["warnings"] = graph_result.get("warnings", [])
            artifacts["reassess_context_used"] = bool(graph_result.get("reassess_context"))
            structured_result = WorkerResponse(
                status="success",
                summary=graph_result.get(
                    "summary",
                    f"Generated defining-rough-endpoints pass {run_pass} artifacts.",
                ),
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
