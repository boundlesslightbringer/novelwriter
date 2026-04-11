import json
import re
from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_nodes


class FlaggedPassage(BaseModel):
    text_reference: str = ""
    issue_description: str = ""
    recommended_adjustment: str = ""


class DimensionReport(BaseModel):
    status: Literal["Pass", "Flag", "Concern"] = "Pass"
    flagged_passages: List[FlaggedPassage] = Field(default_factory=list)


class MagicDimensionReport(BaseModel):
    status: Literal["Pass", "Flag", "Concern", "Not applicable"] = "Not applicable"
    magic_acts_in_chapter: int = 0
    current_prevalence_level: Literal[
        "Rare", "Increasing", "Decreasing", "Stable", "Not applicable"
    ] = "Not applicable"
    flagged_passages: List[FlaggedPassage] = Field(default_factory=list)


class DimensionReports(BaseModel):
    political_realism: DimensionReport = Field(default_factory=DimensionReport)
    magic_prevalence_and_consistency: MagicDimensionReport = Field(
        default_factory=MagicDimensionReport
    )
    violence_framing: DimensionReport = Field(default_factory=DimensionReport)
    dark_content_justification: DimensionReport = Field(default_factory=DimensionReport)
    tonal_consistency: DimensionReport = Field(default_factory=DimensionReport)


class PrioritySummary(BaseModel):
    high: List[str] = Field(default_factory=list)
    medium: List[str] = Field(default_factory=list)
    low: List[str] = Field(default_factory=list)


class MagicSystemUpdateRecommendation(BaseModel):
    update_type: Literal[
        "add_confirmed_capability",
        "add_confirmed_limit",
        "add_unexplained_phenomenon",
    ] = "add_unexplained_phenomenon"
    description: str = ""
    justification: str = ""


class AuditHeader(BaseModel):
    chapter_context: int = 0
    audit_scope: Literal["full_chapter", "flagged_scene"] = "full_chapter"
    pov_character_audited: str = ""


class RealismAuditArtifacts(BaseModel):
    audit_header: AuditHeader = Field(default_factory=AuditHeader)
    dimension_reports: DimensionReports = Field(default_factory=DimensionReports)
    priority_summary: PrioritySummary = Field(default_factory=PrioritySummary)
    magic_system_updates_recommended: List[MagicSystemUpdateRecommendation] = Field(
        default_factory=list
    )
    kg_context_used: Dict[str, Any] = Field(default_factory=dict)


class DraftSignals(BaseModel):
    magic_like_signals_present: bool = False
    violence_like_signals_present: bool = False
    dark_content_like_signals_present: bool = False
    estimated_magic_acts: int = 0
    estimated_violent_acts: int = 0
    tonal_register_note: str = ""


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


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


def _default_kg_context() -> Dict[str, Any]:
    return {
        "magic_system_found": False,
        "faction_nodes_found": 0,
        "location_nodes_found": 0,
        "culture_nodes_found": 0,
        "pov_character_found": False,
        "recent_chapter_nodes_found": 0,
    }


def _text_has_magic_signals(text: str) -> bool:
    if not text.strip():
        return False
    return bool(
        re.search(
            r"\b(magic|spell|sorcer|witch|wizard|rune|ritual|curse|enchanted|arcane|dragonfire)\b",
            text,
            re.IGNORECASE,
        )
    )


def _ensure_non_null_dimension_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    template = RealismAuditArtifacts().model_dump()
    merged = dict(template)
    merged.update({k: v for k, v in payload.items() if k in merged})

    if not isinstance(merged.get("audit_header"), dict):
        merged["audit_header"] = template["audit_header"]
    else:
        header = dict(template["audit_header"])
        header.update(merged["audit_header"])
        merged["audit_header"] = header

    if not isinstance(merged.get("dimension_reports"), dict):
        merged["dimension_reports"] = template["dimension_reports"]
    else:
        reports = dict(template["dimension_reports"])
        reports.update(merged["dimension_reports"])
        merged["dimension_reports"] = reports

    for key in (
        "political_realism",
        "magic_prevalence_and_consistency",
        "violence_framing",
        "dark_content_justification",
        "tonal_consistency",
    ):
        report_payload = merged["dimension_reports"].get(key)
        if not isinstance(report_payload, dict):
            merged["dimension_reports"][key] = template["dimension_reports"][key]
            continue
        default_payload = dict(template["dimension_reports"][key])
        default_payload.update(report_payload)
        if not isinstance(default_payload.get("flagged_passages"), list):
            default_payload["flagged_passages"] = []
        merged["dimension_reports"][key] = default_payload

    if not isinstance(merged.get("priority_summary"), dict):
        merged["priority_summary"] = template["priority_summary"]
    else:
        priority = dict(template["priority_summary"])
        priority.update(merged["priority_summary"])
        for bucket in ("high", "medium", "low"):
            if not isinstance(priority.get(bucket), list):
                priority[bucket] = []
        merged["priority_summary"] = priority

    if not isinstance(merged.get("magic_system_updates_recommended"), list):
        merged["magic_system_updates_recommended"] = []

    if not isinstance(merged.get("kg_context_used"), dict):
        merged["kg_context_used"] = {}

    return merged


def _validate_artifacts(artifacts: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    reports = artifacts.get("dimension_reports", {})
    if not isinstance(reports, dict):
        return ["dimension_reports must be an object."]

    required_dimensions = (
        "political_realism",
        "magic_prevalence_and_consistency",
        "violence_framing",
        "dark_content_justification",
        "tonal_consistency",
    )
    for key in required_dimensions:
        report = reports.get(key)
        if not isinstance(report, dict):
            errors.append(f"{key} report must be an object.")
            continue
        status = str(report.get("status", "")).strip()
        if not status:
            errors.append(f"{key}.status is required.")
        passages = report.get("flagged_passages")
        if passages is None or not isinstance(passages, list):
            errors.append(f"{key}.flagged_passages must be a list.")
            continue
        for idx, passage in enumerate(passages):
            if not isinstance(passage, dict):
                errors.append(f"{key}.flagged_passages[{idx}] must be an object.")
                continue
            for field in ("text_reference", "issue_description", "recommended_adjustment"):
                if not str(passage.get(field, "")).strip():
                    errors.append(f"{key}.flagged_passages[{idx}].{field} must be non-empty.")

    magic_updates = artifacts.get("magic_system_updates_recommended")
    if magic_updates is None or not isinstance(magic_updates, list):
        errors.append("magic_system_updates_recommended must be a list.")

    kg_context = artifacts.get("kg_context_used")
    if not isinstance(kg_context, dict):
        errors.append("kg_context_used must be an object.")
    else:
        for key in (
            "magic_system_found",
            "faction_nodes_found",
            "location_nodes_found",
            "culture_nodes_found",
            "pov_character_found",
        ):
            if key not in kg_context:
                errors.append(f"kg_context_used.{key} is required.")

    return errors


def run_balancing_realism_chain(
    subagent: Any,
    state: Dict[str, Any],
    config: Optional[RunnableConfig] = None,
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}
    task = str(worker_request.get("task", "") or "")

    draft = str(context.get("chapter_or_scene_draft", "") or "")
    chapter_context = int(context.get("chapter_context", 0) or 0)
    audit_scope = str(context.get("audit_scope", "") or "")
    scene_description = str(context.get("scene_description", "") or "")
    tone_reference = str(context.get("tone_reference", "") or "")
    pov_character_id = str(context.get("pov_character_id", "") or "")

    missing_fields: List[str] = []
    if not draft:
        missing_fields.append("chapter_or_scene_draft")
    if chapter_context <= 0:
        missing_fields.append("chapter_context")
    if audit_scope not in {"full_chapter", "flagged_scene"}:
        missing_fields.append("audit_scope")

    if missing_fields:
        structured_result = WorkerResponse(
            status="need_input",
            summary="Missing required context for balancing-realism-and-fantasy.",
            artifacts={
                "error": "missing_required_context",
                "missing_fields": missing_fields,
                "audit_header": {
                    "chapter_context": chapter_context,
                    "audit_scope": audit_scope if audit_scope else "full_chapter",
                    "pov_character_audited": pov_character_id,
                },
                "dimension_reports": RealismAuditArtifacts().model_dump()["dimension_reports"],
                "priority_summary": {"high": [], "medium": [], "low": []},
                "magic_system_updates_recommended": [],
                "kg_context_used": _default_kg_context(),
            },
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

    warnings: List[str] = []
    kg_context_used = _default_kg_context()
    magic_system_nodes: List[Dict[str, Any]] = []
    faction_nodes: List[Dict[str, Any]] = []
    location_nodes: List[Dict[str, Any]] = []
    culture_nodes: List[Dict[str, Any]] = []
    pov_character_nodes: List[Dict[str, Any]] = []
    recent_chapter_nodes: List[Dict[str, Any]] = []

    likely_has_magic = _text_has_magic_signals(draft)

    try:
        if likely_has_magic:
            magic_system_nodes = query_kg_nodes.invoke(
                {"query": {"type": "MagicSystem"}, "as_of_chapter": chapter_context}
            )
        kg_context_used["magic_system_found"] = bool(magic_system_nodes)
    except Exception as error:
        warnings.append(f"MagicSystem query failed: {error}")

    try:
        faction_nodes = query_kg_nodes.invoke(
            {"query": {"type": "Faction"}, "as_of_chapter": chapter_context}
        )
        kg_context_used["faction_nodes_found"] = len(faction_nodes)
    except Exception as error:
        warnings.append(f"Faction query failed: {error}")

    try:
        location_nodes = query_kg_nodes.invoke(
            {"query": {"type": "Location"}, "as_of_chapter": chapter_context}
        )
        kg_context_used["location_nodes_found"] = len(location_nodes)
    except Exception as error:
        warnings.append(f"Location query failed: {error}")

    try:
        culture_nodes = query_kg_nodes.invoke(
            {"query": {"type": "Culture"}, "as_of_chapter": chapter_context}
        )
        kg_context_used["culture_nodes_found"] = len(culture_nodes)
    except Exception as error:
        warnings.append(f"Culture query failed: {error}")

    if pov_character_id:
        try:
            pov_character_nodes = query_kg_nodes.invoke(
                {
                    "query": {"logical_id": pov_character_id, "type": "Character"},
                    "as_of_chapter": chapter_context,
                }
            )
            kg_context_used["pov_character_found"] = bool(pov_character_nodes)
        except Exception as error:
            warnings.append(f"POV Character query failed: {error}")

    try:
        recent_chapter_nodes = query_kg_nodes.invoke(
            {
                "query": {
                    "type": "Chapter",
                    "properties.chapter_number": {"$gte": max(chapter_context - 5, 0)},
                },
                "as_of_chapter": chapter_context,
            }
        )
        kg_context_used["recent_chapter_nodes_found"] = len(recent_chapter_nodes)
    except Exception as error:
        warnings.append(f"Recent Chapter query failed: {error}")

    try:
        skill_contract = str(
            progressive_skill_loader.invoke(
                {"skill_name": "balancing-realism-and-fantasy", "load_type": "full"}
            )
        )
        llm = _build_llm(subagent)

        signals_llm = llm.with_structured_output(DraftSignals)
        signals_prompt = (
            f"{skill_contract}\n\n"
            "Return DraftSignals only. Detect whether the draft includes magic-like, violence-like, "
            "or dark-content-like signals and estimate rough counts.\n\n"
            f"{_safe_json({'chapter_or_scene_draft': draft, 'audit_scope': audit_scope})}"
        )
        draft_signals: DraftSignals = signals_llm.invoke(
            [HumanMessage(content=signals_prompt)], config=config
        )

        realism_llm = llm.with_structured_output(RealismAuditArtifacts)
        audit_payload = {
            "context": {
                "chapter_context": chapter_context,
                "audit_scope": audit_scope,
                "scene_description": scene_description,
                "tone_reference": tone_reference,
                "pov_character_id": pov_character_id,
            },
            "chapter_or_scene_draft": draft,
            "draft_signals": draft_signals.model_dump(),
            "kg_context": {
                "magic_system_nodes": magic_system_nodes,
                "faction_nodes": faction_nodes,
                "location_nodes": location_nodes,
                "culture_nodes": culture_nodes,
                "pov_character_nodes": pov_character_nodes,
                "recent_chapter_nodes": recent_chapter_nodes,
            },
        }
        audit_prompt = (
            f"{skill_contract}\n\n"
            "Run the five-dimension realism/fantasy calibration audit and return only "
            "the structured artifacts contract.\n\n"
            f"{_safe_json(audit_payload)}"
        )
        model_output: RealismAuditArtifacts = realism_llm.invoke(
            [HumanMessage(content=audit_prompt)], config=config
        )
        artifacts = _ensure_non_null_dimension_payload(model_output.model_dump())

        header = dict(artifacts.get("audit_header", {}))
        header["chapter_context"] = chapter_context
        header["audit_scope"] = audit_scope
        header["pov_character_audited"] = pov_character_id
        artifacts["audit_header"] = header

        magic_report = (
            artifacts.get("dimension_reports", {}).get("magic_prevalence_and_consistency", {})
        )
        if not kg_context_used.get("magic_system_found"):
            magic_report["status"] = "Not applicable"
            magic_report["current_prevalence_level"] = "Not applicable"
            if not isinstance(magic_report.get("flagged_passages"), list):
                magic_report["flagged_passages"] = []
            artifacts["dimension_reports"]["magic_prevalence_and_consistency"] = magic_report

        artifacts["kg_context_used"] = {**kg_context_used, **dict(artifacts.get("kg_context_used", {}))}
        validation_errors = _validate_artifacts(artifacts)
        artifacts["warnings"] = warnings

        if validation_errors:
            artifacts["validation_errors"] = validation_errors
            structured_result = WorkerResponse(
                status="failed",
                summary="balancing-realism-and-fantasy validation failed.",
                artifacts=artifacts,
            ).model_dump()
        else:
            summary = "Completed balancing-realism-and-fantasy audit."
            if warnings:
                summary = "Completed realism/fantasy audit with recoverable KG warning(s)."
            structured_result = WorkerResponse(
                status="success",
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
