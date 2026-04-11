import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_edges, query_kg_nodes


class AuditHeader(BaseModel):
    pov_character_id: str = ""
    scene_summary: str = ""
    overall_status: str = "CLEAN"
    violation_count: int = 0
    violation_types_found: List[str] = Field(default_factory=list)


class ViolationEntry(BaseModel):
    violation_type: str = ""
    offending_text: str = ""
    description: str = ""
    correction_note: str = ""


class PovAuditArtifacts(BaseModel):
    audit_header: AuditHeader = Field(default_factory=AuditHeader)
    violation_log: List[ViolationEntry] = Field(default_factory=list)
    summary_pattern_note: str = ""
    kg_context_used: Dict[str, Any] = Field(
        default_factory=lambda: {
            "character_node_found": False,
            "voice_profile_found": False,
            "knows_edges_found": 0,
        }
    )


class PovAuditOutput(BaseModel):
    artifacts: PovAuditArtifacts = Field(default_factory=PovAuditArtifacts)


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _default_kg_context() -> Dict[str, Any]:
    return {
        "character_node_found": False,
        "voice_profile_found": False,
        "knows_edges_found": 0,
    }


def _default_artifacts() -> Dict[str, Any]:
    return PovAuditArtifacts().model_dump()


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


def _normalize_artifacts(artifacts: Dict[str, Any], kg_context: Dict[str, Any]) -> Dict[str, Any]:
    merged = _default_artifacts()
    merged.update({k: v for k, v in artifacts.items() if k in merged})

    audit_header = merged.get("audit_header")
    if not isinstance(audit_header, dict):
        audit_header = {}
    normalized_header = AuditHeader().model_dump()
    normalized_header.update(audit_header)
    if normalized_header.get("overall_status") not in {"CLEAN", "VIOLATIONS FOUND"}:
        normalized_header["overall_status"] = "CLEAN"
    if not isinstance(normalized_header.get("violation_types_found"), list):
        normalized_header["violation_types_found"] = []
    if not isinstance(normalized_header.get("violation_count"), int):
        normalized_header["violation_count"] = len(merged.get("violation_log", []))
    merged["audit_header"] = normalized_header

    raw_violations = merged.get("violation_log")
    if not isinstance(raw_violations, list):
        raw_violations = []
    normalized_violations: List[Dict[str, Any]] = []
    for violation in raw_violations:
        record = ViolationEntry().model_dump()
        if isinstance(violation, dict):
            record.update(violation)
        normalized_violations.append(record)
    merged["violation_log"] = normalized_violations
    merged["audit_header"]["violation_count"] = len(normalized_violations)
    if normalized_violations and merged["audit_header"]["overall_status"] != "VIOLATIONS FOUND":
        merged["audit_header"]["overall_status"] = "VIOLATIONS FOUND"
    if not normalized_violations and merged["audit_header"]["overall_status"] != "CLEAN":
        merged["audit_header"]["overall_status"] = "CLEAN"

    summary_pattern_note = merged.get("summary_pattern_note")
    merged["summary_pattern_note"] = summary_pattern_note if isinstance(summary_pattern_note, str) else ""

    normalized_context = _default_kg_context()
    merged_context = merged.get("kg_context_used")
    if isinstance(merged_context, dict):
        normalized_context.update(merged_context)
    normalized_context.update(kg_context)
    merged["kg_context_used"] = normalized_context
    return merged


def run_pov_consistency_chain(
    subagent: Any,
    state: Dict[str, Any],
    config: RunnableConfig | None = None,
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}

    draft_scene = str(context.get("draft_scene", "") or "")
    pov_character_id = str(context.get("pov_character_id", "") or "")
    chapter_context = int(context.get("chapter_context", 0) or 0)

    missing_fields: List[str] = []
    if not draft_scene:
        missing_fields.append("draft_scene")
    if not pov_character_id:
        missing_fields.append("pov_character_id")
    if chapter_context <= 0:
        missing_fields.append("chapter_context")

    if missing_fields:
        structured_result = WorkerResponse(
            status="need_input",
            summary="Missing required context for pov-consistency-maintenance.",
            artifacts={
                "error": "missing_required_context",
                "missing_fields": missing_fields,
                **_default_artifacts(),
            },
            follow_up_questions=[
                "Please provide draft_scene, pov_character_id, and chapter_context for pov-consistency-maintenance."
            ],
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

    warnings: List[str] = []
    character_node: Dict[str, Any] = {}
    knows_edges: List[Dict[str, Any]] = []
    knowledge_items: List[Dict[str, Any]] = []
    kg_context = _default_kg_context()

    try:
        character_nodes = query_kg_nodes.invoke(
            {
                "query": {"logical_id": pov_character_id, "type": "Character"},
                "as_of_chapter": chapter_context,
            }
        )
        character_node = character_nodes[0] if character_nodes else {}
    except Exception as error:
        warnings.append(f"Character query failed: {error}")

    try:
        knows_edges = query_kg_edges.invoke(
            {
                "query": {"from": pov_character_id, "type": "KNOWS"},
                "as_of_chapter": chapter_context,
            }
        )
    except Exception as error:
        warnings.append(f"KNOWS edge query failed: {error}")

    knowledge_ids = [edge.get("to", "") for edge in knows_edges if edge.get("to")]
    if knowledge_ids:
        try:
            knowledge_items = query_kg_nodes.invoke(
                {
                    "query": {"logical_id": {"$in": knowledge_ids}, "type": "KnowledgeItem"},
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            warnings.append(f"KnowledgeItem query failed: {error}")

    voice_profile = (
        character_node.get("properties", {}).get("voice_profile", {})
        if isinstance(character_node.get("properties"), dict)
        else {}
    )
    kg_context["character_node_found"] = bool(character_node)
    kg_context["voice_profile_found"] = bool(voice_profile)
    kg_context["knows_edges_found"] = len(knows_edges)

    if not kg_context["voice_profile_found"]:
        structured_result = WorkerResponse(
            status="need_input",
            summary="POV character voice profile is missing for pov-consistency-maintenance.",
            artifacts={
                "error": "missing_voice_profile",
                **_normalize_artifacts(
                    {
                        "audit_header": {
                            "pov_character_id": pov_character_id,
                            "scene_summary": "",
                            "overall_status": "CLEAN",
                            "violation_count": 0,
                            "violation_types_found": [],
                        }
                    },
                    kg_context,
                ),
                "warnings": warnings,
            },
            follow_up_questions=[
                "Please run character-voice-differentiation for this POV character before pov-consistency-maintenance."
            ],
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

    try:
        skill_contract = progressive_skill_loader.invoke(
            {"skill_name": "pov-consistency-maintenance", "load_type": "full"}
        )
        if not isinstance(skill_contract, str):
            skill_contract = str(skill_contract)

        llm = _build_llm(subagent).with_structured_output(PovAuditOutput)
        audit_payload = {
            "draft_scene": draft_scene,
            "pov_character_id": pov_character_id,
            "chapter_context": chapter_context,
            "character_node": character_node,
            "knows_edges": knows_edges,
            "knowledge_items": knowledge_items,
            "kg_context_used": kg_context,
        }
        prompt = (
            f"{skill_contract}\n\n"
            "You are executing pov-consistency-maintenance. KG queries are complete.\n"
            "Audit the draft against the provided KG context and return only structured JSON artifacts.\n"
            "Do not write scene prose. Keep nested fields non-null and include quoted offending text when violations exist.\n\n"
            f"{_safe_json(audit_payload)}"
        )
        llm_result: PovAuditOutput = llm.invoke([HumanMessage(content=prompt)], config=config or {})
        raw_artifacts = (
            llm_result.artifacts.model_dump()
            if llm_result and llm_result.artifacts
            else _default_artifacts()
        )
        artifacts = _normalize_artifacts(raw_artifacts, kg_context)
        artifacts["warnings"] = warnings
        structured_result = WorkerResponse(
            status="success",
            summary="Audited scene for POV consistency using the internal chain.",
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
