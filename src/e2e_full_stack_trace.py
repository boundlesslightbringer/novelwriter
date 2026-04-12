"""JSONL trace sink for tests/test_e2e_full_stack.py.

Writes turn boundaries, stream updates (worker_request / latest_worker_result),
and end-of-turn snapshots to a file under ``src/`` by default.

Override path with env ``NOVELWRITER_E2E_TRACE_FILE``.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

_DEFAULT_TRACE = Path(__file__).resolve().parent / "e2e_full_stack_trace.jsonl"
_MAX_DEPTH = 14
_MAX_STRING = 400_000


def trace_file_path() -> Path:
    raw = os.environ.get("NOVELWRITER_E2E_TRACE_FILE", "").strip()
    return Path(raw) if raw else _DEFAULT_TRACE


def _truncate_str(text: str) -> str:
    if len(text) <= _MAX_STRING:
        return text
    return text[: _MAX_STRING] + f"\n…[truncated, total_chars={len(text)}]"


def _serialize_message(msg: Any) -> Any:
    if msg is None:
        return None
    try:
        if hasattr(msg, "model_dump"):
            dumped = msg.model_dump()
            if isinstance(dumped, dict):
                for key in ("content", "additional_kwargs"):
                    val = dumped.get(key)
                    if isinstance(val, str):
                        dumped[key] = _truncate_str(val)
                return dumped
    except Exception:
        pass
    content = getattr(msg, "content", None)
    if isinstance(content, str):
        content = _truncate_str(content)
    return {
        "type": getattr(msg, "type", None),
        "content": content,
        "name": getattr(msg, "name", None),
    }


def sanitize_for_trace(obj: Any, depth: int = 0) -> Any:
    """Make ``obj`` JSON-serializable with depth/string caps."""
    if depth > _MAX_DEPTH:
        return "<max_depth>"
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return _truncate_str(obj)
    if isinstance(obj, bytes):
        return f"<bytes len={len(obj)}>"
    if isinstance(obj, Mapping):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            out[str(k)] = sanitize_for_trace(v, depth + 1)
        return out
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_trace(item, depth + 1) for item in obj[:500]]
    mod = type(obj).__module__
    if mod.startswith("langchain_core.messages") or "Message" in type(obj).__name__:
        return _serialize_message(obj)
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            return sanitize_for_trace(obj.model_dump(), depth + 1)
        except Exception:
            pass
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        try:
            return sanitize_for_trace(obj.dict(), depth + 1)
        except Exception:
            pass
    return str(obj)


class E2EFullStackTraceWriter:
    """Append-only JSONL writer for one test session."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or trace_file_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, record: Mapping[str, Any]) -> None:
        line = json.dumps(dict(record), ensure_ascii=True, default=str)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def session_start(self, *, thread_id: str, test_name: str) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "event": "session_start",
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "test": test_name,
                        "thread_id": thread_id,
                        "trace_file": str(self.path.resolve()),
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )

    def turn_start(
        self,
        *,
        turn_title: str,
        user_text: str,
        turn_input: Mapping[str, Any],
    ) -> None:
        payload = dict(turn_input)
        msgs = payload.get("messages")
        if isinstance(msgs, list):
            payload = {**payload, "messages": [sanitize_for_trace(m) for m in msgs]}
        self._append(
            {
                "event": "turn_start",
                "ts": datetime.now(timezone.utc).isoformat(),
                "turn_title": turn_title,
                "user_text": user_text,
                "turn_input": sanitize_for_trace(payload),
            }
        )

    def stream_updates(self, *, event_type: str, event_data: Any) -> None:
        if event_type == "updates" and isinstance(event_data, dict):
            by_node: Dict[str, Any] = {}
            for node_name, state_update in event_data.items():
                if isinstance(state_update, dict):
                    by_node[str(node_name)] = sanitize_for_trace(state_update)
                else:
                    by_node[str(node_name)] = sanitize_for_trace(state_update)
            self._append(
                {
                    "event": "graph_stream_updates",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "nodes": by_node,
                }
            )
            return
        if event_type == "messages":
            chunk, metadata = event_data
            meta = sanitize_for_trace(metadata) if isinstance(metadata, dict) else metadata
            content = getattr(chunk, "content", None)
            preview: Any
            if isinstance(content, str):
                preview = _truncate_str(content) if len(content) > 2000 else content
            elif isinstance(content, list):
                preview = sanitize_for_trace(content)
            else:
                preview = sanitize_for_trace(content)
            self._append(
                {
                    "event": "graph_stream_message",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "metadata": meta,
                    "content_preview": preview,
                }
            )
            return
        self._append(
            {
                "event": "graph_stream_other",
                "ts": datetime.now(timezone.utc).isoformat(),
                "stream_event_type": event_type,
                "data": sanitize_for_trace(event_data),
            }
        )

    def turn_end(
        self,
        *,
        turn_title: str,
        state: Mapping[str, Any],
        kg_counts: Dict[str, int],
    ) -> None:
        wh = state.get("worker_history")
        if not isinstance(wh, list):
            wh = []
        self._append(
            {
                "event": "turn_end",
                "ts": datetime.now(timezone.utc).isoformat(),
                "turn_title": turn_title,
                "final_response": state.get("final_response"),
                "iteration_count": state.get("iteration_count"),
                "rejection_count": state.get("rejection_count"),
                "active_worker": state.get("active_worker"),
                "worker_request": sanitize_for_trace(state.get("worker_request")),
                "latest_worker_result": sanitize_for_trace(state.get("latest_worker_result")),
                "worker_history": sanitize_for_trace(wh),
                "kg_counts": kg_counts,
            }
        )
