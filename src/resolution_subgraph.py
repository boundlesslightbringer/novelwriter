"""LangGraph subgraph for resolution_subagent: tool-free ANALYSE; IMPLEMENT plan → execute → finalize."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from src.agents.base import WorkerResponse
from src.world_bible_tools import update_kg_node


class ResolutionSubgraphState(TypedDict, total=False):
    """Internal state for the resolution subgraph."""

    task: str
    context: Dict[str, Any]
    branch: str
    analyse_structured: Dict[str, Any]
    implement_plan: Dict[str, Any]
    writes_executed: List[Dict[str, Any]]
    errors: List[str]
    response_status: str
    response_summary: str
    response_artifacts: Dict[str, Any]


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _prompt_path(name: str) -> Path:
    src_dir = Path(__file__).resolve().parent
    return src_dir / "prompts" / name


def _load_prompt(name: str) -> str:
    return _prompt_path(name).read_text(encoding="utf-8")


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


def _normalize_mode(raw: Any) -> str:
    text = str(raw or "").strip().upper().replace(" ", "_")
    if text in {"ANALYSE", "ANALYZE"}:
        return "ANALYSE"
    if text == "IMPLEMENT":
        return "IMPLEMENT"
    return ""


# --- ANALYSE structured output (no tools) ---


class ResolutionOptionAnalyse(BaseModel):
    option_id: str = Field(default="A", description="Single letter or short id")
    label: str = ""
    description: str = ""
    affected_modules: List[str] = Field(default_factory=list)
    complexity: Literal["Low", "Medium", "High"] = "Medium"


class AnalyseStructuredOutput(BaseModel):
    briefing: str = ""
    resolution_options: List[ResolutionOptionAnalyse] = Field(default_factory=list)
    recommended_option: str = ""
    recommendation_rationale: str = ""


# --- IMPLEMENT structured plan (no tools on this call; execute is deterministic) ---


class NodeUpdatePlan(BaseModel):
    logical_id: str = ""
    chapter: int = 0
    updated_properties: Dict[str, Any] = Field(default_factory=dict)


class ImplementPlanStructured(BaseModel):
    reasoning: str = ""
    skip_story_writes: bool = False
    resolution_type: Literal["Resolved", "Accepted as intentional ambiguity"] = "Resolved"
    contradiction_logical_id: str = ""
    contradiction_properties_patch: Dict[str, Any] = Field(
        default_factory=dict,
        description="Merged into Contradiction node properties (e.g. resolution_status, resolution_notes).",
    )
    additional_node_updates: List[NodeUpdatePlan] = Field(default_factory=list)


def _route_node(state: ResolutionSubgraphState) -> Dict[str, Any]:
    context = _ensure_dict(state.get("context"))
    mode = _normalize_mode(context.get("mode"))
    if mode == "ANALYSE":
        return {"branch": "analyse"}
    if mode == "IMPLEMENT":
        return {"branch": "implement"}
    return {"branch": "invalid", "errors": [f"Invalid or missing mode: {context.get('mode')!r}"]}


def _route_edge(state: ResolutionSubgraphState) -> str:
    return str(state.get("branch") or "invalid")


def _analyse_node(subagent: Any, state: ResolutionSubgraphState, config: RunnableConfig | None) -> Dict[str, Any]:
    context = _ensure_dict(state.get("context"))
    contradiction_id = str(
        _ensure_dict(context.get("contradiction_record")).get("contradiction_id")
        or context.get("contradiction_id")
        or ""
    )
    payload = {
        "mode": "ANALYSE",
        "contradiction_record": context.get("contradiction_record"),
        "blocked_write": context.get("blocked_write"),
        "prefetched_docs": context.get("prefetched_docs"),
    }
    system = _load_prompt("resolution_analyse.md")
    llm = _build_llm(subagent)
    structured_llm = llm.with_structured_output(AnalyseStructuredOutput)
    messages = [
        SystemMessage(content=system),
        HumanMessage(
            content=(
                "Produce the structured analysis output for this orchestrator payload.\n\n"
                f"{_safe_json(payload)}"
            )
        ),
    ]
    try:
        parsed: AnalyseStructuredOutput | None = structured_llm.invoke(messages, config=config)
    except Exception as exc:
        return {
            "response_status": "failed",
            "response_summary": f"ANALYSE structured output failed: {exc}",
            "response_artifacts": {"error": str(exc), "mode": "ANALYSE"},
        }
    if parsed is None:
        return {
            "response_status": "failed",
            "response_summary": "ANALYSE produced no structured output.",
            "response_artifacts": {"error": "empty_structured_output", "mode": "ANALYSE"},
        }
    opt_count = len(parsed.resolution_options)
    if opt_count < 2 or opt_count > 4:
        return {
            "response_status": "failed",
            "response_summary": f"ANALYSE must return 2–4 resolution options; got {opt_count}.",
            "response_artifacts": {
                "error": "invalid_options_count",
                "mode": "ANALYSE",
                "count": opt_count,
            },
        }
    artifacts = {
        "mode": "ANALYSE",
        "contradiction_id": contradiction_id or "",
        "briefing": parsed.briefing,
        "resolution_options": [opt.model_dump() for opt in parsed.resolution_options],
        "recommended_option": parsed.recommended_option,
        "recommendation_rationale": parsed.recommendation_rationale,
    }
    return {
        "analyse_structured": artifacts,
        "response_status": "success",
        "response_summary": "Analysed contradiction and generated resolution options.",
        "response_artifacts": artifacts,
    }


def _implement_plan_node(subagent: Any, state: ResolutionSubgraphState, config: RunnableConfig | None) -> Dict[str, Any]:
    context = _ensure_dict(state.get("context"))
    payload = {
        "mode": "IMPLEMENT",
        "contradiction_record": context.get("contradiction_record"),
        "blocked_write": context.get("blocked_write"),
        "user_decision": context.get("user_decision"),
        "prefetched_docs": context.get("prefetched_docs"),
    }
    system = _load_prompt("resolution_implement.md")
    llm = _build_llm(subagent)
    structured_llm = llm.with_structured_output(ImplementPlanStructured)
    messages = [
        SystemMessage(content=system),
        HumanMessage(
            content=(
                "Produce the structured implementation plan (no tool calls in this step). "
                "Use logical_id values exactly as in contradiction_record or prefetched_docs.\n\n"
                f"{_safe_json(payload)}"
            )
        ),
    ]
    try:
        parsed: ImplementPlanStructured | None = structured_llm.invoke(messages, config=config)
    except Exception as exc:
        return {
            "errors": [str(exc)],
            "response_status": "failed",
            "response_summary": f"IMPLEMENT planning failed: {exc}",
            "response_artifacts": {
                "resolution_result": {
                    "mode": "IMPLEMENT",
                    "status": "RESOLUTION_FAILED",
                    "contradiction_id": _ensure_dict(context.get("contradiction_record")).get(
                        "contradiction_id", ""
                    ),
                    "failed_at_step": 0,
                    "error_details": str(exc),
                    "writes_executed_before_failure": [],
                }
            },
        }
    if parsed is None or not parsed.contradiction_logical_id.strip():
        return {
            "errors": ["Missing contradiction_logical_id in plan"],
            "response_status": "failed",
            "response_summary": "IMPLEMENT plan missing contradiction logical_id.",
            "response_artifacts": {
                "resolution_result": {
                    "mode": "IMPLEMENT",
                    "status": "RESOLUTION_FAILED",
                    "error_details": "Plan validation failed: contradiction_logical_id required",
                    "writes_executed_before_failure": [],
                }
            },
        }
    return {"implement_plan": parsed.model_dump()}


def _implement_execute_node(state: ResolutionSubgraphState) -> Dict[str, Any]:
    plan = _ensure_dict(state.get("implement_plan"))
    context = _ensure_dict(state.get("context"))
    contradiction_rec = _ensure_dict(context.get("contradiction_record"))
    default_chapter = int(contradiction_rec.get("detected_at_chapter") or context.get("chapter") or 0)

    writes: List[Dict[str, Any]] = []
    errors: List[str] = []

    skip_story = bool(plan.get("skip_story_writes"))
    additional = _ensure_list(plan.get("additional_node_updates"))
    cid = str(plan.get("contradiction_logical_id") or "")
    patch = _ensure_dict(plan.get("contradiction_properties_patch"))

    if not patch.get("resolution_status"):
        errors.append("contradiction_properties_patch must include resolution_status")
    if errors:
        return {
            "errors": errors,
            "writes_executed": writes,
            "response_status": "failed",
            "response_summary": "Invalid implementation plan.",
            "response_artifacts": {
                "resolution_result": {
                    "mode": "IMPLEMENT",
                    "status": "RESOLUTION_FAILED",
                    "contradiction_id": contradiction_rec.get("contradiction_id", ""),
                    "failed_at_step": 0,
                    "error_details": errors[0],
                    "writes_executed_before_failure": writes,
                }
            },
        }

    def _do_update(logical_id: str, updated_properties: Dict[str, Any], chapter: int) -> bool:
        if not logical_id.strip():
            errors.append("Empty logical_id in update")
            return False
        ch = chapter if chapter else default_chapter
        try:
            msg = update_kg_node.invoke(
                {"logical_id": logical_id, "updated_properties": updated_properties, "chapter": ch}
            )
        except Exception as exc:
            errors.append(f"update_kg_node {logical_id}: {exc}")
            return False
        if isinstance(msg, str) and msg.startswith("Error:"):
            errors.append(msg)
            return False
        writes.append(
            {
                "operation": "update",
                "target": "node",
                "logical_id": logical_id,
                "outcome": "success",
                "detail": str(msg)[:500],
            }
        )
        return True

    if not skip_story:
        for entry in additional:
            if not isinstance(entry, dict):
                continue
            lid = str(entry.get("logical_id") or "")
            props = _ensure_dict(entry.get("updated_properties"))
            ch = int(entry.get("chapter") or default_chapter)
            if props and not _do_update(lid, props, ch):
                return {
                    "errors": errors,
                    "writes_executed": writes,
                    "response_status": "failed",
                    "response_summary": "Implementation halted after a failed write.",
                    "response_artifacts": {
                        "resolution_result": {
                            "mode": "IMPLEMENT",
                            "status": "RESOLUTION_FAILED",
                            "contradiction_id": contradiction_rec.get("contradiction_id", ""),
                            "failed_at_step": len(writes),
                            "error_details": errors[-1] if errors else "unknown",
                            "writes_executed_before_failure": writes,
                        }
                    },
                }

    if not _do_update(cid, patch, default_chapter):
        return {
            "errors": errors,
            "writes_executed": writes,
            "response_status": "failed",
            "response_summary": "Failed to update Contradiction node.",
            "response_artifacts": {
                "resolution_result": {
                    "mode": "IMPLEMENT",
                    "status": "RESOLUTION_FAILED",
                    "contradiction_id": contradiction_rec.get("contradiction_id", ""),
                    "failed_at_step": len(writes),
                    "error_details": errors[-1] if errors else "unknown",
                    "writes_executed_before_failure": writes,
                }
            },
        }

    return {"writes_executed": writes, "errors": []}


def _implement_finalize_node(state: ResolutionSubgraphState) -> Dict[str, Any]:
    if state.get("response_status") == "failed" and state.get("response_artifacts"):
        return {}
    plan = _ensure_dict(state.get("implement_plan"))
    context = _ensure_dict(state.get("context"))
    blocked = _ensure_dict(context.get("blocked_write"))
    write_type = str(blocked.get("write_type") or "unknown_write")
    writes = list(_ensure_list(state.get("writes_executed")))
    resolution_type = str(plan.get("resolution_type") or "Resolved")
    contradiction_rec = _ensure_dict(context.get("contradiction_record"))
    cid = str(contradiction_rec.get("contradiction_id") or plan.get("contradiction_logical_id") or "")

    artifacts = {
        "resolution_result": {
            "mode": "IMPLEMENT",
            "status": "RESOLVED",
            "contradiction_id": cid,
            "resolution_type": resolution_type,
            "writes_executed": writes,
            "module_5_3_updated": True,
            "re_issue_signal": {
                "action": "RE_ISSUE_BLOCKED_WRITE",
                "originating_write_type": write_type,
                "note": (
                    "Resolution complete. The originating worker should re-issue the blocked write. "
                    "story_state_manager will re-run contradiction detection on the re-issued write."
                ),
            },
        }
    }
    return {
        "response_status": "success",
        "response_summary": "Implemented contradiction resolution successfully.",
        "response_artifacts": artifacts,
    }


def _finalize_invalid_node(state: ResolutionSubgraphState) -> Dict[str, Any]:
    errs = _ensure_list(state.get("errors"))
    detail = errs[0] if errs else "Invalid resolution request."
    return {
        "response_status": "failed",
        "response_summary": detail,
        "response_artifacts": {"error": detail, "mode": "unknown"},
    }


def _build_resolution_graph(subagent: Any) -> Any:
    def analyse_wrapper(s: ResolutionSubgraphState, config=None) -> Dict[str, Any]:
        return _analyse_node(subagent, s, config)

    def plan_wrapper(s: ResolutionSubgraphState, config=None) -> Dict[str, Any]:
        return _implement_plan_node(subagent, s, config)

    graph = StateGraph(ResolutionSubgraphState)
    graph.add_node("route", _route_node)
    graph.add_node("analyse", analyse_wrapper)
    graph.add_node("implement_plan", plan_wrapper)
    graph.add_node("implement_execute", _implement_execute_node)
    graph.add_node("implement_finalize", _implement_finalize_node)
    graph.add_node("finalize_invalid", _finalize_invalid_node)

    graph.add_edge(START, "route")
    graph.add_conditional_edges(
        "route",
        _route_edge,
        {
            "analyse": "analyse",
            "implement": "implement_plan",
            "invalid": "finalize_invalid",
        },
    )
    graph.add_edge("analyse", END)
    graph.add_edge("implement_plan", "implement_execute")

    def _after_plan(state: ResolutionSubgraphState) -> str:
        if state.get("response_status") == "failed":
            return "end_failed"
        return "execute"

    graph.add_conditional_edges(
        "implement_plan",
        _after_plan,
        {"execute": "implement_execute", "end_failed": END},
    )

    def _after_execute(state: ResolutionSubgraphState) -> str:
        if state.get("response_status") == "failed":
            return "end_failed"
        return "finalize"

    graph.add_conditional_edges(
        "implement_execute",
        _after_execute,
        {"finalize": "implement_finalize", "end_failed": END},
    )
    graph.add_edge("implement_finalize", END)
    graph.add_edge("finalize_invalid", END)

    return graph.compile()


def run_resolution_subgraph(
    subagent: Any, state: Dict[str, Any], config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    worker_request = _ensure_dict(state.get("worker_request"))
    context = _ensure_dict(worker_request.get("context"))
    task = str(worker_request.get("task", ""))

    initial: ResolutionSubgraphState = {
        "task": task,
        "context": context,
    }

    try:
        graph = _build_resolution_graph(subagent)
        graph_result = graph.invoke(initial, config=config or {})
        status = str(graph_result.get("response_status") or "failed")
        summary = str(graph_result.get("response_summary") or "Resolution subgraph completed.")
        artifacts = _ensure_dict(graph_result.get("response_artifacts"))
        if not artifacts:
            artifacts = {"error": "empty_artifacts", "mode": context.get("mode")}
        structured_result = WorkerResponse(
            status=status if status in {"success", "need_input", "blocked", "failed"} else "failed",
            summary=summary,
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
        "task": task,
        "context": context,
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }
