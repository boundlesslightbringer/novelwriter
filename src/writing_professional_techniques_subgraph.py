import json
from typing import Any, Dict, List, Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_nodes


class ProblemDiagnosis(BaseModel):
    problem_type: str = ""
    root_cause: str = ""
    what_is_available: str = ""


class PathForward(BaseModel):
    primary_recommendation: str = ""
    worked_application: str = ""
    alternatives: List[str] = Field(default_factory=list)


class TechniqueArtifacts(BaseModel):
    technique_applied: str = ""
    problem_diagnosis: ProblemDiagnosis = Field(default_factory=ProblemDiagnosis)
    path_forward: PathForward = Field(default_factory=PathForward)
    scene_construction_context: str = ""
    kg_context_used: Dict[str, Any] = Field(
        default_factory=lambda: {
            "character_node_found": False,
            "cascade_chains_checked": False,
            "recent_chapters_checked": False,
        }
    )


class ProfessionalTechniquesOutput(BaseModel):
    artifacts: TechniqueArtifacts = Field(default_factory=TechniqueArtifacts)


class ProfessionalWritingTechniquesState(TypedDict, total=False):
    problem_description: str
    pov_character_id: str
    chapter_context: int
    stuck_draft: str
    technique_hint: str
    missing_required_fields: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    problem_type: str
    selected_technique: str
    query_mode: str
    character_node: Dict[str, Any]
    cascade_chains: List[Dict[str, Any]]
    recent_chapters: List[Dict[str, Any]]
    kg_context_used: Dict[str, Any]
    skill_contract: str
    warnings: List[str]
    artifacts: Dict[str, Any]
    summary: str


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _default_kg_context() -> Dict[str, Any]:
    return {
        "character_node_found": False,
        "cascade_chains_checked": False,
        "recent_chapters_checked": False,
    }


def _default_artifacts() -> Dict[str, Any]:
    return TechniqueArtifacts().model_dump()


def _build_llm(subagent: Any) -> ChatGoogleGenerativeAI:
    kwargs: Dict[str, Any] = {"temperature": subagent.llm_config.temperature}
    if subagent.llm_config.top_p is not None:
        kwargs["top_p"] = subagent.llm_config.top_p
    if subagent.llm_config.top_k is not None:
        kwargs["top_k"] = subagent.llm_config.top_k
    return ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        **kwargs,
    )


def _classify_problem(problem_description: str, technique_hint: str) -> tuple[str, str, str]:
    text = f"{problem_description} {technique_hint}".lower()

    if any(token in text for token in ("timeline", "chronology", "causal sequence", "too early", "too late")):
        return ("timeline_or_continuity", "Timeline Realignment", "timeline")
    if any(token in text for token in ("unearned", "disconnected", "trace-back", "trace back", "consequence")):
        return ("causal_gap", "Consequence Trace-Back", "choice_or_consequence")
    if any(token in text for token in ("arbitrary", "both options", "implausible", "motivation", "choice")):
        return ("choice_arbitrariness", "Character Interview", "choice_or_consequence")
    if any(token in text for token in ("pov", "head-hop", "head hopping", "voice drift")):
        return ("pov_or_voice_limit", "Change POV", "character_only")
    if any(token in text for token in ("ending", "cannot finish", "stuck ending")):
        return ("missing_scene_ending", "Skip and Return", "character_only")
    if any(token in text for token in ("safe", "low stakes", "no stakes", "costless")):
        return ("insufficient_stakes", "The Worse Choice Trick", "choice_or_consequence")
    if any(token in text for token in ("everything failed", "resists analysis", "cannot diagnose")):
        return ("analysis_deadlock", "Freewrite the Tangle", "character_only")
    return ("local_craft_tangle", "Character Interview", "character_only")


def _normalize_artifacts(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    merged = TechniqueArtifacts().model_dump()
    merged.update({k: v for k, v in artifacts.items() if k in merged})

    diagnosis = merged.get("problem_diagnosis")
    if not isinstance(diagnosis, dict):
        diagnosis = {}
    diagnosis_merged = ProblemDiagnosis().model_dump()
    diagnosis_merged.update(diagnosis)
    merged["problem_diagnosis"] = diagnosis_merged

    path_forward = merged.get("path_forward")
    if not isinstance(path_forward, dict):
        path_forward = {}
    path_forward_merged = PathForward().model_dump()
    path_forward_merged.update(path_forward)
    if not isinstance(path_forward_merged.get("alternatives"), list):
        path_forward_merged["alternatives"] = []
    merged["path_forward"] = path_forward_merged

    kg_context = merged.get("kg_context_used")
    if not isinstance(kg_context, dict):
        kg_context = {}
    kg_default = _default_kg_context()
    kg_default.update(kg_context)
    merged["kg_context_used"] = kg_default

    if not isinstance(merged.get("scene_construction_context"), str):
        merged["scene_construction_context"] = ""
    if not isinstance(merged.get("technique_applied"), str):
        merged["technique_applied"] = ""
    return merged


def _build_subgraph(subagent: Any) -> Any:
    llm = _build_llm(subagent).with_structured_output(ProfessionalTechniquesOutput)
    graph = StateGraph(ProfessionalWritingTechniquesState)

    def ingest_context(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        missing: List[str] = []
        for required_key in ("problem_description", "pov_character_id", "chapter_context"):
            value = state.get(required_key)
            if value is None or value == "" or value == 0:
                missing.append(required_key)
        return {
            "missing_required_fields": missing,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required professional-writing-techniques context fields: {', '.join(missing)}."
                if missing
                else None
            ),
            "warnings": [],
            "kg_context_used": _default_kg_context(),
        }

    def classify_problem(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        problem_type, selected_technique, query_mode = _classify_problem(
            state.get("problem_description", ""),
            state.get("technique_hint", ""),
        )
        return {
            "problem_type": problem_type,
            "selected_technique": selected_technique,
            "query_mode": query_mode,
        }

    def fetch_character(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        chapter_context = int(state["chapter_context"])
        warnings: List[str] = list(state.get("warnings", []))
        try:
            character_nodes = query_kg_nodes.invoke(
                {
                    "query": {
                        "logical_id": state["pov_character_id"],
                        "type": "Character",
                    },
                    "as_of_chapter": chapter_context,
                }
            )
            character_node = character_nodes[0] if character_nodes else {}
        except Exception as error:
            character_node = {}
            warnings.append(f"Character query failed: {error}")

        kg_context = dict(state.get("kg_context_used", _default_kg_context()))
        kg_context["character_node_found"] = bool(character_node)
        return {
            "character_node": character_node,
            "kg_context_used": kg_context,
            "warnings": warnings,
        }

    def fetch_cascade_chains(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        chapter_context = int(state["chapter_context"])
        warnings: List[str] = list(state.get("warnings", []))
        pov_character_id = state.get("pov_character_id", "")
        cascade_chains: List[Dict[str, Any]] = []

        try:
            chain_nodes = query_kg_nodes.invoke(
                {"query": {"type": "CascadeChain"}, "as_of_chapter": chapter_context}
            )
            for node in chain_nodes:
                properties = node.get("properties") if isinstance(node.get("properties"), dict) else {}
                participants = properties.get("involved_character_ids", [])
                if not isinstance(participants, list):
                    participants = []
                if not pov_character_id or pov_character_id in participants:
                    cascade_chains.append(node)
        except Exception as error:
            warnings.append(f"CascadeChain query failed: {error}")

        kg_context = dict(state.get("kg_context_used", _default_kg_context()))
        kg_context["cascade_chains_checked"] = True
        return {
            "cascade_chains": cascade_chains,
            "kg_context_used": kg_context,
            "warnings": warnings,
        }

    def fetch_recent_chapters(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        chapter_context = int(state["chapter_context"])
        warnings: List[str] = list(state.get("warnings", []))
        lower_bound = max(chapter_context - 3, 0)
        try:
            recent_chapters = query_kg_nodes.invoke(
                {
                    "query": {
                        "type": "Chapter",
                        "properties.chapter_number": {"$gte": lower_bound},
                    },
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            recent_chapters = []
            warnings.append(f"Recent Chapter query failed: {error}")

        kg_context = dict(state.get("kg_context_used", _default_kg_context()))
        kg_context["recent_chapters_checked"] = True
        return {
            "recent_chapters": recent_chapters,
            "kg_context_used": kg_context,
            "warnings": warnings,
        }

    def load_skill(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        skill_contract = progressive_skill_loader.invoke(
            {"skill_name": "professional-writing-techniques", "load_type": "full"}
        )
        if not isinstance(skill_contract, str):
            skill_contract = str(skill_contract)
        return {"skill_contract": skill_contract}

    def apply_technique(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        payload = {
            "problem_description": state.get("problem_description", ""),
            "problem_type": state.get("problem_type", ""),
            "selected_technique": state.get("selected_technique", ""),
            "technique_hint": state.get("technique_hint", ""),
            "stuck_draft": state.get("stuck_draft", ""),
            "kg_context": {
                "character_node": state.get("character_node", {}),
                "cascade_chains": state.get("cascade_chains", []),
                "recent_chapters": state.get("recent_chapters", []),
                "kg_context_used": state.get("kg_context_used", _default_kg_context()),
            },
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "You are executing professional-writing-techniques for a local craft problem.\n"
            "Return only structured JSON in the required artifacts shape. Keep nested fields non-null.\n"
            "If the provided technique_hint is mismatched, choose a better technique and explain in root_cause.\n"
            "Write scene_construction_context as one paragraph in second person for scene-construction.\n\n"
            f"{_safe_json(payload)}"
        )
        llm_result: ProfessionalTechniquesOutput = llm.invoke([HumanMessage(content=prompt)])
        artifacts = llm_result.artifacts.model_dump() if llm_result and llm_result.artifacts else _default_artifacts()
        return {"artifacts": artifacts}

    def validate_artifacts(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        artifacts = _normalize_artifacts(state.get("artifacts", {}))
        kg_context = dict(state.get("kg_context_used", _default_kg_context()))
        artifacts["kg_context_used"] = {**artifacts.get("kg_context_used", {}), **kg_context}
        return {"artifacts": artifacts}

    def package_success(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        summary = "Applied professional-writing-techniques to unblock a local writing problem."
        if state.get("warnings"):
            summary = "Applied professional-writing-techniques with recoverable KG warning(s)."
        return {"summary": summary}

    def package_need_input(state: ProfessionalWritingTechniquesState) -> ProfessionalWritingTechniquesState:
        return {
            "summary": state.get(
                "terminal_summary",
                "Missing required context for professional-writing-techniques.",
            )
        }

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("classify_problem", classify_problem)
    graph.add_node("fetch_character", fetch_character)
    graph.add_node("fetch_cascade_chains", fetch_cascade_chains)
    graph.add_node("fetch_recent_chapters", fetch_recent_chapters)
    graph.add_node("load_skill", load_skill)
    graph.add_node("apply_technique", apply_technique)
    graph.add_node("validate_artifacts", validate_artifacts)
    graph.add_node("package_success", package_success)
    graph.add_node("package_need_input", package_need_input)

    graph.add_edge(START, "ingest_context")

    def route_after_ingest(
        state: ProfessionalWritingTechniquesState,
    ) -> Literal["package_need_input", "classify_problem"]:
        if state.get("terminal_status"):
            return "package_need_input"
        return "classify_problem"

    graph.add_conditional_edges(
        "ingest_context",
        route_after_ingest,
        {
            "package_need_input": "package_need_input",
            "classify_problem": "classify_problem",
        },
    )
    graph.add_edge("classify_problem", "fetch_character")

    def route_after_character(
        state: ProfessionalWritingTechniquesState,
    ) -> Literal["fetch_cascade_chains", "fetch_recent_chapters", "load_skill"]:
        query_mode = state.get("query_mode", "character_only")
        if query_mode == "choice_or_consequence":
            return "fetch_cascade_chains"
        if query_mode == "timeline":
            return "fetch_recent_chapters"
        return "load_skill"

    graph.add_conditional_edges(
        "fetch_character",
        route_after_character,
        {
            "fetch_cascade_chains": "fetch_cascade_chains",
            "fetch_recent_chapters": "fetch_recent_chapters",
            "load_skill": "load_skill",
        },
    )
    graph.add_edge("fetch_cascade_chains", "load_skill")
    graph.add_edge("fetch_recent_chapters", "load_skill")
    graph.add_edge("load_skill", "apply_technique")
    graph.add_edge("apply_technique", "validate_artifacts")
    graph.add_edge("validate_artifacts", "package_success")
    graph.add_edge("package_success", END)
    graph.add_edge("package_need_input", END)

    return graph.compile()


def run_professional_writing_techniques_subgraph(
    subagent: Any,
    state: Dict[str, Any],
    config: RunnableConfig | None = None,
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}

    initial_state: ProfessionalWritingTechniquesState = {
        "problem_description": str(context.get("problem_description", "") or ""),
        "pov_character_id": str(context.get("pov_character_id", "") or ""),
        "chapter_context": int(context.get("chapter_context", 0) or 0),
        "stuck_draft": str(context.get("stuck_draft", "") or ""),
        "technique_hint": str(context.get("technique_hint", "") or ""),
    }

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})

        missing = graph_result.get("missing_required_fields", [])
        if missing:
            structured_result = WorkerResponse(
                status="need_input",
                summary=graph_result.get(
                    "summary",
                    "Missing required context for professional-writing-techniques.",
                ),
                artifacts={
                    "error": "missing_required_context",
                    "missing_fields": missing,
                    "technique_applied": "",
                    "problem_diagnosis": ProblemDiagnosis().model_dump(),
                    "path_forward": PathForward().model_dump(),
                    "scene_construction_context": "",
                    "kg_context_used": _default_kg_context(),
                },
                follow_up_questions=[
                    "Please provide problem_description, pov_character_id, and chapter_context for professional-writing-techniques."
                ],
            ).model_dump()
        else:
            artifacts = _normalize_artifacts(graph_result.get("artifacts", {}))
            artifacts["warnings"] = graph_result.get("warnings", [])
            structured_result = WorkerResponse(
                status="success",
                summary=graph_result.get(
                    "summary",
                    "Applied professional-writing-techniques to unblock a local writing problem.",
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
