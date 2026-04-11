"""Optional JSONL tracing for bootstrap forensic audits.

Set ``NOVELWRITER_BOOTSTRAP_TRACE`` to a file path to append one JSON object per
logged event (brain quality gate on creative workers; story_state_manager completion).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping

_TRACE_ENV = "NOVELWRITER_BOOTSTRAP_TRACE"


def trace_path() -> str | None:
    path = os.environ.get(_TRACE_ENV, "").strip()
    return path or None


def _redact_value(key: str, value: Any, depth: int) -> Any:
    lk = key.lower()
    if any(s in lk for s in ("secret", "api_key", "apikey", "token", "password", "authorization")):
        return "***"
    if depth > 8:
        return "<max_depth>"
    if isinstance(value, dict):
        return redact_context(value, depth + 1)
    if isinstance(value, list):
        return [_redact_value(key, item, depth + 1) if isinstance(item, dict) else item for item in value[:100]]
    return value


def redact_context(context: Mapping[str, Any], depth: int = 0) -> Dict[str, Any]:
    """Return a copy of context with obvious secret fields masked."""
    out: Dict[str, Any] = {}
    for key, value in context.items():
        out[str(key)] = _redact_value(str(key), value, depth)
    return out


def _append_jsonl(record: Dict[str, Any]) -> None:
    path = trace_path()
    if not path:
        return
    parent = Path(path).parent
    if str(parent) not in (".", ""):
        parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")


def fingerprint_logical_ids(nodes: List[MutableMapping[str, Any]]) -> str:
    ids = sorted(str(n.get("logical_id") or "") for n in nodes if isinstance(n, dict))
    payload = "\n".join(ids).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()[:20]


def append_brain_quality_gate_trace(
    *,
    worker: str,
    task: str,
    result_status: str,
    quality_verdict: str | None,
    quality_reason: str | None,
    context_redacted: Mapping[str, Any],
    raw_artifacts: Mapping[str, Any],
    validation_errors: List[str],
    mapper_has_payload: bool | None = None,
    mapper_errors: List[str] | None = None,
    mapper_counts: Dict[str, int] | None = None,
    nodes_logical_id_fingerprint: str | None = None,
) -> None:
    if not trace_path():
        return
    record: Dict[str, Any] = {
        "event": "brain_quality_gate_creative",
        "worker": worker,
        "task": task,
        "result_status": result_status,
        "quality_verdict": quality_verdict,
        "quality_reason": quality_reason,
        "context": dict(context_redacted),
        "raw_artifacts": dict(raw_artifacts),
        "artifact_validation_errors": list(validation_errors),
    }
    if mapper_has_payload is not None:
        record["mapper_has_payload"] = mapper_has_payload
    if mapper_errors is not None:
        record["mapper_errors"] = list(mapper_errors)
    if mapper_counts is not None:
        record["mapper_write_counts"] = dict(mapper_counts)
    if nodes_logical_id_fingerprint:
        record["nodes_logical_id_fingerprint"] = nodes_logical_id_fingerprint
    _append_jsonl(record)


def append_ssm_worker_trace(worker_name: str, invoke_result: Mapping[str, Any]) -> None:
    if not trace_path() or worker_name != "story_state_manager":
        return
    latest = invoke_result.get("latest_worker_result")
    if not isinstance(latest, dict):
        return
    result = latest.get("result")
    if not isinstance(result, dict):
        return
    artifacts = result.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
    record: Dict[str, Any] = {
        "event": "story_state_manager_complete",
        "worker": worker_name,
        "task": str(latest.get("task") or ""),
        "result_status": str(result.get("status") or ""),
        "summary": str(result.get("summary") or "")[:800],
        "records_updated": artifacts.get("records_updated"),
        "records_failed": artifacts.get("records_failed"),
        "errors": artifacts.get("errors"),
    }
    _append_jsonl(record)
