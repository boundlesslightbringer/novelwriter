"""Helpers for trace-driven worker replay in stubbed E2E runs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.agents.base import WorkerResponse
from src.agents.workers import StoryStateManager

ALLOWED_WORKER_STATUS = ("success", "need_input", "blocked", "failed")
DEFAULT_CANONICAL_TRACE = Path(__file__).resolve().parent / "e2e_full_stack_trace.jsonl"
DEFAULT_RUNTIME_TRACE = Path("tmp/stubbed_runtime_trace.jsonl")


TRACE_LATEST_WORKER_RESULT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://novelwriter.local/schema/trace-latest-worker-result.json",
    "title": "TraceLatestWorkerResult",
    "type": "object",
    "additionalProperties": False,
    "required": ["worker", "task", "context", "result"],
    "properties": {
        "worker": {"type": "string", "minLength": 1},
        "task": {"type": "string", "minLength": 1},
        "context": {"type": "object"},
        "result": {
            "type": "object",
            "additionalProperties": True,
            "required": ["status", "summary", "artifacts"],
            "properties": {
                "status": {"type": "string", "enum": list(ALLOWED_WORKER_STATUS)},
                "summary": {"type": "string"},
                "artifacts": {"type": "object"},
            },
        },
    },
}

STUB_REPLAY_FIXTURE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://novelwriter.local/schema/stub-replay-fixture.json",
    "title": "StubReplayFixture",
    "type": "object",
    "additionalProperties": False,
    "required": ["meta", "records", "queues"],
    "properties": {
        "meta": {"type": "object"},
        "records": {"type": "array"},
        "queues": {"type": "object"},
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonicalize_task(task: str) -> str:
    return " ".join(str(task).strip().split())


def task_hash(task: str) -> str:
    canonical_task = canonicalize_task(task)
    return hashlib.sha256(canonical_task.encode("utf-8")).hexdigest()


def queue_key(worker: str, task_hash_value: str) -> str:
    return f"{worker}::{task_hash_value}"


class TraceWorkerResultPayload(BaseModel):
    """Shape of nested `result` in trace latest_worker_result."""

    model_config = ConfigDict(extra="allow")

    status: str
    summary: str
    artifacts: dict[str, Any]

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in ALLOWED_WORKER_STATUS:
            raise ValueError(f"Invalid worker status: {value}")
        return value


class TraceLatestWorkerResult(BaseModel):
    """Worker record extracted from graph stream updates."""

    model_config = ConfigDict(extra="allow")

    worker: str
    task: str
    context: dict[str, Any] = Field(default_factory=dict)
    result: TraceWorkerResultPayload

    @field_validator("worker", "task")
    @classmethod
    def validate_non_empty_str(cls, value: str) -> str:
        text = str(value).strip()
        if not text:
            raise ValueError("Field must be non-empty")
        return text


class ReplayRecordResult(BaseModel):
    """Replay-ready worker result payload."""

    model_config = ConfigDict(extra="allow")

    status: str
    summary: str
    artifacts: dict[str, Any]

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in ALLOWED_WORKER_STATUS:
            raise ValueError(f"Invalid worker status: {value}")
        return value


class ReplayRecord(BaseModel):
    """Compact replay record extracted from canonical trace."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    source_line: int = Field(ge=0)
    source_ts: str
    source_event: str = "graph_stream_updates"
    node_name: str
    worker: str
    task: str
    task_hash: str
    context: dict[str, Any] = Field(default_factory=dict)
    result: ReplayRecordResult

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, value: str) -> str:
        if len(value) != 10 or not value.startswith("rec_"):
            raise ValueError("record_id must follow rec_000001 format")
        return value

    @field_validator("task_hash")
    @classmethod
    def validate_task_hash(cls, value: str) -> str:
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError("task_hash must be a 64-char lowercase hex string")
        return value


class StubReplayMeta(BaseModel):
    """Fixture-level metadata for replay extraction."""

    model_config = ConfigDict(extra="forbid")

    source_trace_file: str
    generated_at: str
    source_line_count: int = Field(ge=0)
    matched_update_events: int = Field(ge=0)
    extracted_record_count: int = Field(ge=0)
    workers_seen: list[str]


class StubReplayFixture(BaseModel):
    """Portable replay fixture for stubbed runs."""

    model_config = ConfigDict(extra="forbid")

    meta: StubReplayMeta
    records: list[ReplayRecord]
    queues: dict[str, list[int]]


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True, default=str) + "\n")


def _to_replay_record(
    *,
    raw: TraceLatestWorkerResult,
    record_id: str,
    source_line: int,
    source_ts: str,
    source_event: str,
    node_name: str,
) -> ReplayRecord:
    replay = ReplayRecord(
        record_id=record_id,
        source_line=source_line,
        source_ts=source_ts,
        source_event=source_event,
        node_name=node_name,
        worker=raw.worker,
        task=raw.task,
        task_hash=task_hash(raw.task),
        context=raw.context if isinstance(raw.context, dict) else {},
        result=ReplayRecordResult(
            status=raw.result.status,
            summary=raw.result.summary,
            artifacts=raw.result.artifacts,
        ),
    )
    expected_hash = task_hash(replay.task)
    if replay.task_hash != expected_hash:
        raise ValueError("Replay record task_hash mismatch")
    return replay


def extract_replay_fixture(
    trace_path: Path,
    *,
    exclude_workers: set[str] | None = None,
) -> tuple[StubReplayFixture, dict[str, Any]]:
    """Stream trace JSONL and build a replay fixture + extraction stats."""
    excluded = set(exclude_workers or set())
    records: list[ReplayRecord] = []
    queues: dict[str, list[int]] = {}
    workers_seen: set[str] = set()
    worker_counts_before_filter: dict[str, int] = {}

    source_line_count = 0
    invalid_json_lines = 0
    matched_update_events = 0
    extracted_before_filter = 0

    with trace_path.open("r", encoding="utf-8") as handle:
        for source_line_count, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_json_lines += 1
                continue

            if payload.get("event") != "graph_stream_updates":
                continue
            nodes = payload.get("nodes")
            if not isinstance(nodes, dict):
                continue
            matched_update_events += 1

            source_ts = str(payload.get("ts") or utc_now_iso())
            source_event = str(payload.get("event") or "graph_stream_updates")

            for node_name, node_payload in nodes.items():
                if not isinstance(node_payload, dict):
                    continue
                latest = node_payload.get("latest_worker_result")
                if not isinstance(latest, dict):
                    continue

                latest_validated = TraceLatestWorkerResult.model_validate(latest)
                worker_name = latest_validated.worker
                worker_counts_before_filter[worker_name] = (
                    worker_counts_before_filter.get(worker_name, 0) + 1
                )
                extracted_before_filter += 1

                if worker_name in excluded:
                    continue

                record = _to_replay_record(
                    raw=latest_validated,
                    record_id=f"rec_{len(records) + 1:06d}",
                    source_line=source_line_count,
                    source_ts=source_ts,
                    source_event=source_event,
                    node_name=str(node_name),
                )
                records.append(record)
                workers_seen.add(worker_name)
                key = queue_key(worker_name, record.task_hash)
                queues.setdefault(key, []).append(len(records) - 1)

    fixture = StubReplayFixture(
        meta=StubReplayMeta(
            source_trace_file=str(trace_path),
            generated_at=utc_now_iso(),
            source_line_count=source_line_count,
            matched_update_events=matched_update_events,
            extracted_record_count=len(records),
            workers_seen=sorted(workers_seen),
        ),
        records=records,
        queues=queues,
    )
    stats = {
        "invalid_json_lines": invalid_json_lines,
        "extracted_record_count_before_filter": extracted_before_filter,
        "worker_counts_before_filter": worker_counts_before_filter,
        "excluded_workers": sorted(excluded),
    }
    return fixture, stats


def dump_fixture_json(fixture: StubReplayFixture, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = fixture.model_dump()
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)


class StubReplayEngine:
    """Deterministic replay queue with optional synthetic generation."""

    def __init__(
        self,
        *,
        fixture: StubReplayFixture,
        runtime_trace_path: Path,
        allow_synthetic: bool,
        persist_synthetic_to_kg: bool,
        story_state_manager: StoryStateManager | None,
    ) -> None:
        self.fixture = fixture
        self.runtime_trace_path = runtime_trace_path
        self.allow_synthetic = allow_synthetic
        self.persist_synthetic_to_kg = persist_synthetic_to_kg
        self.story_state_manager = story_state_manager
        self._queues = {key: list(indices) for key, indices in fixture.queues.items()}

    def _pop_exact_or_fallback(self, worker: str, task: str) -> ReplayRecord | None:
        key = queue_key(worker, task_hash(task))
        candidate_indices = self._queues.get(key, [])
        if candidate_indices:
            return self.fixture.records[candidate_indices.pop(0)]

        fallback_keys = [k for k, values in self._queues.items() if k.startswith(f"{worker}::") and values]
        if not fallback_keys:
            return None
        fallback_keys.sort(key=lambda item: self._queues[item][0])
        idx = self._queues[fallback_keys[0]].pop(0)
        return self.fixture.records[idx]

    def _synthetic_artifacts(self, worker: str, context: dict[str, Any]) -> dict[str, Any]:
        chapter_context = int(context.get("chapter_context") or 1)
        if worker == "plotting_subagent":
            return {
                "skill_used": "synthetic-plotting",
                "plot_outline": {
                    "scene_intent": "opening scene",
                    "genre": context.get("genre", "High Fantasy"),
                    "themes": context.get("themes", ["legitimacy", "the cost of inheritance"]),
                },
                "scene_beats": [
                    {
                        "beat": "Opening pressure point",
                        "goal": "Introduce opening-scene conflict immediately",
                    }
                ],
                "nodes_to_add": [
                    {
                        "logical_id": f"synthetic_plot_thread_{task_hash(str(context))[:10]}",
                        "node_type": "PlotThread",
                        "properties": {
                            "name": "Synthetic opening-scene thread",
                            "status": "Active",
                        },
                        "chapter": chapter_context,
                    }
                ],
            }
        if worker == "planning_subagent":
            return {
                "skill_used": "synthetic-planning",
                "seed_document": {"seed": "Synthetic replay bootstrap seed"},
                "nodes_to_add": [
                    {
                        "logical_id": f"synthetic_planning_seed_{task_hash(str(context))[:10]}",
                        "node_type": "PlotThread",
                        "properties": {
                            "name": "Synthetic planning seed",
                            "status": "Seed",
                        },
                        "chapter": chapter_context,
                    }
                ],
            }
        if worker == "character_subagent":
            return {
                "skill_used": "synthetic-character",
                "character_profile": {"name": "Synthetic POV", "role": "protagonist"},
                "nodes_to_add": [
                    {
                        "logical_id": f"synthetic_character_{task_hash(str(context))[:10]}",
                        "node_type": "Character",
                        "properties": {"name": "Synthetic POV", "is_pov_eligible": True},
                        "chapter": chapter_context,
                    }
                ],
            }
        if worker == "consequence_subagent":
            return {
                "skill_used": "synthetic-consequence",
                "consequence_map": {"immediate": "Rising tension around inheritance"},
                "nodes_to_add": [
                    {
                        "logical_id": f"synthetic_consequence_{task_hash(str(context))[:10]}",
                        "node_type": "Event",
                        "properties": {"name": "Synthetic consequence event"},
                        "chapter": chapter_context,
                    }
                ],
            }
        return {
            "skill_used": f"synthetic-{worker}",
            "synthetic_payload": {"worker": worker, "note": "Fallback replay record"},
            "nodes_to_add": [
                {
                    "logical_id": f"synthetic_generic_{task_hash(str(context))[:10]}",
                    "node_type": "Event",
                    "properties": {"name": "Synthetic generic event"},
                    "chapter": chapter_context,
                }
            ],
        }

    def _persist_synthetic_record(self, record: ReplayRecord) -> dict[str, Any]:
        if not self.persist_synthetic_to_kg:
            return {"skipped": True, "reason": "persist_synthetic_to_kg disabled"}
        if self.story_state_manager is None:
            raise RuntimeError("StoryStateManager is required for synthetic KG persistence")

        chapter_context = int(record.context.get("chapter_context") or 1)
        persistence_request = {
            "worker_request": {
                "task": f"Persist synthetic replay artifacts for {record.worker}",
                "context": {
                    "chapter_context": chapter_context,
                    "artifacts": record.result.artifacts,
                    "synthetic": True,
                    "synthetic_source_task_hash": record.task_hash,
                    "synthetic_source_worker": record.worker,
                },
            }
        }
        invoke_result = self.story_state_manager.invoke(persistence_request, config={})
        latest = invoke_result.get("latest_worker_result")
        if not isinstance(latest, dict):
            raise RuntimeError("StoryStateManager returned invalid latest_worker_result")
        result = latest.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("StoryStateManager returned invalid result payload")
        status = str(result.get("status") or "")
        artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
        receipt = {
            "status": status,
            "summary": str(result.get("summary") or ""),
            "records_updated": artifacts.get("records_updated", []),
            "records_failed": artifacts.get("records_failed", []),
            "errors": artifacts.get("errors", []),
        }
        if status != "success":
            raise RuntimeError(f"Synthetic persistence failed with status={status}: {receipt}")
        return receipt

    def _build_synthetic_record(self, worker: str, task: str, context: dict[str, Any]) -> ReplayRecord:
        if worker == "writing_subagent":
            raise RuntimeError("Writing worker cannot be synthesized")
        latest = TraceLatestWorkerResult.model_validate(
            {
                "worker": worker,
                "task": task,
                "context": context,
                "result": {
                    "status": "success",
                    "summary": "Synthetic stub generated for missing replay record",
                    "artifacts": self._synthetic_artifacts(worker, context),
                },
            }
        )
        record = _to_replay_record(
            raw=latest,
            record_id=f"rec_{len(self.fixture.records) + 1:06d}",
            source_line=0,
            source_ts=utc_now_iso(),
            source_event="graph_stream_updates",
            node_name=worker,
        )
        key = queue_key(record.worker, record.task_hash)
        if key != f"{record.worker}::{record.task_hash}":
            raise RuntimeError("Invalid synthetic queue key format")
        return record

    def next_record(self, *, worker: str, task: str, context: dict[str, Any]) -> ReplayRecord:
        replay = self._pop_exact_or_fallback(worker, task)
        if replay is not None:
            return replay
        if not self.allow_synthetic:
            raise RuntimeError(f"No replay records left for worker={worker!r}, task={task!r}")

        record = self._build_synthetic_record(worker, task, context)
        self.fixture.records.append(record)
        key = queue_key(record.worker, record.task_hash)
        self._queues.setdefault(key, []).append(len(self.fixture.records) - 1)

        _append_jsonl(
            self.runtime_trace_path,
            {
                "event": "synthetic_stub_generated",
                "ts": utc_now_iso(),
                "source_trace_file": self.fixture.meta.source_trace_file,
                "replay_record": record.model_dump(),
                "schema_validated": True,
            },
        )

        try:
            receipt = self._persist_synthetic_record(record)
            _append_jsonl(
                self.runtime_trace_path,
                {
                    "event": "synthetic_stub_persisted",
                    "ts": utc_now_iso(),
                    "worker": record.worker,
                    "task_hash": record.task_hash,
                    "story_state_manager_status": "success",
                    "kg_persistence_receipt": receipt,
                },
            )
        except Exception as error:
            _append_jsonl(
                self.runtime_trace_path,
                {
                    "event": "synthetic_stub_persisted",
                    "ts": utc_now_iso(),
                    "worker": record.worker,
                    "task_hash": record.task_hash,
                    "story_state_manager_status": "failed",
                    "kg_persistence_receipt": {"error": str(error)},
                },
            )
            raise

        # Consume the just-enqueued record deterministically from its queue.
        replay = self._pop_exact_or_fallback(worker, task)
        if replay is None:
            raise RuntimeError("Failed to consume synthetic replay record after enqueue")
        return replay


def make_replay_stub_worker(
    *,
    worker_name: str,
    replay_engine: StubReplayEngine,
) -> Callable[[dict[str, Any], Any | None], dict[str, Any]]:
    """Create an orchestrator-compatible stub worker backed by replay records."""

    def _worker(state: dict[str, Any], config: Any | None = None) -> dict[str, Any]:
        worker_request = state.get("worker_request", {}) if isinstance(state, dict) else {}
        task = str(worker_request.get("task") or "unknown_task")
        context = worker_request.get("context")
        if not isinstance(context, dict):
            context = {}

        replay_record = replay_engine.next_record(worker=worker_name, task=task, context=context)
        result = WorkerResponse(
            status=replay_record.result.status,
            summary=replay_record.result.summary,
            artifacts=replay_record.result.artifacts,
        )
        worker_record = {
            "worker": worker_name,
            "task": task,
            "context": context,
            "result": result.model_dump(),
        }
        return {
            "latest_worker_result": worker_record,
            "worker_history": [worker_record],
            "worker_request": None,
            "active_worker": None,
        }

    return _worker


def load_fixture_from_trace(
    trace_path: Path,
    *,
    exclude_workers: set[str] | None = None,
) -> tuple[StubReplayFixture, dict[str, Any]]:
    """Load replay fixture directly from canonical JSONL trace."""
    return extract_replay_fixture(trace_path, exclude_workers=exclude_workers)


def write_fixture_or_raise(fixture: StubReplayFixture, output_path: Path) -> None:
    """Persist fixture and raise on schema failures."""
    try:
        payload = fixture.model_dump()
        StubReplayFixture.model_validate(payload)
    except ValidationError as error:
        raise RuntimeError(f"Fixture validation failed: {error}") from error
    dump_fixture_json(fixture, output_path)
