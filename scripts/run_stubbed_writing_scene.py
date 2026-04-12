"""Run stubbed replay for non-writing workers with real writing + KG persistence."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from src.agents.workers import StoryStateManager, WritingSubagent
from src.config import NovelWriterConfig
from src.brain_persistence_mapper import PersistPayloadMapper
from src.e2e_stub_replay import (
    DEFAULT_CANONICAL_TRACE,
    DEFAULT_RUNTIME_TRACE,
    StubReplayEngine,
    load_fixture_from_trace,
    make_replay_stub_worker,
)
from src.orchestrator import GRRMOrchestrator
from src.world_bible_tools import _get_db, init_kg_db

BOOTSTRAP_INPUT = "genre: High Fantasy, themes: legitimacy and the cost of inheritance"
FIRST_SCENE_INPUT = "write the first scene"
DEFAULT_POLISH_PROBLEM = (
    "Improve scene-level craft quality, sharpen clarity and emotional throughline, "
    "and strengthen prose rhythm while preserving story intent."
)
DEFAULT_POLISH_HINT = "professional-writing-techniques"
REPLAY_STUB_WORKERS = (
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "consequence_subagent",
    "resolution_subagent",
)


def _slugify(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(text or "").strip().lower()).strip("_")
    return value or "item"


def _fallback_payload_from_high_level_artifacts(
    *,
    worker: str,
    artifacts: dict[str, Any],
    chapter_context: int,
) -> dict[str, Any]:
    nodes_to_add: list[dict[str, Any]] = []
    edges_to_add: list[dict[str, Any]] = []

    if worker == "planning_subagent":
        conflict = str(artifacts.get("draft_core_conflict_question") or "").strip()
        if conflict:
            logical_id = f"synthetic_plot_thread_{_slugify(conflict)[:24]}"
            nodes_to_add.append(
                {
                    "logical_id": logical_id,
                    "node_type": "PlotThread",
                    "properties": {"name": "Preseeded compass conflict", "description": conflict, "status": "Active"},
                    "chapter": chapter_context,
                }
            )

    if worker == "character_subagent":
        protagonist_name = "protagonist_seed"
        concept = artifacts.get("character_concept")
        if isinstance(concept, dict):
            protagonist_name = str(concept.get("name") or concept.get("assigned_narrative_role") or protagonist_name)
        protagonist_id = f"char_{_slugify(protagonist_name)[:28]}"
        nodes_to_add.append(
            {
                "logical_id": protagonist_id,
                "node_type": "Character",
                "properties": {"name": protagonist_name, "pov_eligible": True},
                "chapter": chapter_context,
            }
        )
        antagonists = artifacts.get("antagonist_concepts")
        if isinstance(antagonists, list):
            for idx, antagonist in enumerate(antagonists, start=1):
                if not isinstance(antagonist, dict):
                    continue
                ant_name = str(antagonist.get("name") or f"antagonist_{idx}")
                ant_id = f"char_{_slugify(ant_name)[:28]}"
                nodes_to_add.append(
                    {
                        "logical_id": ant_id,
                        "node_type": "Character",
                        "properties": {"name": ant_name},
                        "chapter": chapter_context,
                    }
                )
                edges_to_add.append(
                    {
                        "logical_id": f"rel_{_slugify(protagonist_id)}_{_slugify(ant_id)}",
                        "edge_type": "RELATIONSHIP",
                        "from_node": protagonist_id,
                        "to_node": ant_id,
                        "properties": {
                            "relationship_status": "contested",
                            "source": "force_preseed_high_level_fallback",
                        },
                        "chapter": chapter_context,
                    }
                )

    if worker == "plotting_subagent":
        pov_assignment = artifacts.get("pov_assignment")
        pov_name = ""
        if isinstance(pov_assignment, dict):
            pov_name = str(pov_assignment.get("selected_pov") or "").strip()
        pov_id = f"char_{_slugify(pov_name)[:28]}" if pov_name else "char_plotting_pov_seed"
        nodes_to_add.append(
            {
                "logical_id": pov_id,
                "node_type": "Character",
                "properties": {"name": pov_name or "plotting_pov_seed", "pov_eligible": True},
                "chapter": chapter_context,
            }
        )
        thread_status = artifacts.get("thread_status")
        if isinstance(thread_status, list):
            for idx, thread in enumerate(thread_status, start=1):
                if not isinstance(thread, dict):
                    continue
                thread_id = str(thread.get("thread_id") or f"thread_plotting_{idx}").strip()
                logical_id = thread_id if thread_id else f"thread_plotting_{idx}"
                nodes_to_add.append(
                    {
                        "logical_id": logical_id,
                        "node_type": "PlotThread",
                        "properties": {
                            "name": thread.get("thread_id") or f"Plot Thread {idx}",
                            "status": thread.get("status") or "Active",
                            "note": thread.get("note") or "",
                        },
                        "chapter": chapter_context,
                    }
                )
                edges_to_add.append(
                    {
                        "logical_id": f"involves_{_slugify(logical_id)}_{_slugify(pov_id)}",
                        "edge_type": "INVOLVES",
                        "from_node": logical_id,
                        "to_node": pov_id,
                        "properties": {"source": "force_preseed_high_level_fallback"},
                        "chapter": chapter_context,
                    }
                )

    if worker == "consequence_subagent":
        consequence_map = artifacts.get("consequence_map")
        if isinstance(consequence_map, dict):
            ev_id = f"event_consequence_{_slugify(str(consequence_map))[:24]}"
            nodes_to_add.append(
                {
                    "logical_id": ev_id,
                    "node_type": "Event",
                    "properties": {
                        "name": "Preseeded consequence event",
                        "description": str(consequence_map.get("immediate") or consequence_map),
                    },
                    "chapter": chapter_context,
                }
            )

    return {
        "nodes_to_add": nodes_to_add,
        "edges_to_add": edges_to_add,
    }


def _turn_input(user_text: str) -> dict[str, Any]:
    return {
        "messages": [HumanMessage(content=user_text)],
        "iteration_count": 0,
        "rejection_count": 0,
        "final_response": None,
        "active_worker": None,
        "worker_request": None,
        "latest_worker_result": None,
        "worker_history": [],
    }


def _render_worker_history(worker_history: Any) -> str:
    if not isinstance(worker_history, list) or not worker_history:
        return "No worker history recorded."
    lines: list[str] = []
    for idx, entry in enumerate(worker_history, start=1):
        row = entry if isinstance(entry, dict) else {}
        result = row.get("result", {}) if isinstance(row.get("result"), dict) else {}
        lines.append(
            f"{idx}. {row.get('worker', 'unknown')} -> {result.get('status', 'unknown')}: {result.get('summary', '')}"
        )
    return "\n".join(lines)


def _print_graph_progress(orchestrator: GRRMOrchestrator, event_type: str, event_data: Any) -> None:
    if event_type == "updates":
        for node_name, state_update in event_data.items():
            if node_name == "brain":
                worker = state_update.get("active_worker")
                if worker:
                    print(f"\n[Brain] Delegating to: {worker}", flush=True)
                    task = (state_update.get("worker_request") or {}).get("task", "")
                    if task:
                        print(f"[Brain] Task: {task}", flush=True)
            elif node_name in orchestrator.workers:
                print(f"\n[{node_name}] Completed.", flush=True)
                result = (state_update.get("latest_worker_result") or {}).get("result", {})
                if isinstance(result, dict):
                    print(f"[{node_name}] Status: {result.get('status')}", flush=True)
                    summary = str(result.get("summary") or "").strip()
                    if summary:
                        print(f"[{node_name}] Summary: {summary}", flush=True)


def _run_turn(
    orchestrator: GRRMOrchestrator,
    thread_id: str,
    user_text: str,
    *,
    turn_title: str,
    verbose_turns: bool,
) -> dict[str, Any]:
    run_config = {"configurable": {"thread_id": thread_id}}
    turn_input = _turn_input(user_text)

    if verbose_turns:
        print(f"\n[E2E] ========== {turn_title} ==========", flush=True)
        print(f"[E2E] User: {user_text!r}", flush=True)

    for event_type, event_data in orchestrator.graph.stream(
        turn_input,
        config=run_config,
        stream_mode=["messages", "updates"],
    ):
        if verbose_turns:
            _print_graph_progress(orchestrator, event_type, event_data)

    state = dict(orchestrator.graph.get_state(run_config).values)
    if verbose_turns:
        print(f"[E2E] --- End {turn_title} ---", flush=True)
        print(f"[E2E] worker_history entries: {len(state.get('worker_history') or [])}", flush=True)
        print(_render_worker_history(state.get("worker_history")), flush=True)
    return state


def _extract_scene_prose(state: dict[str, Any]) -> str:
    worker_history = state.get("worker_history")
    if isinstance(worker_history, list):
        for entry in reversed(worker_history):
            if not isinstance(entry, dict) or entry.get("worker") != "writing_subagent":
                continue
            result = entry.get("result")
            if not isinstance(result, dict):
                continue
            artifacts = result.get("artifacts")
            if isinstance(artifacts, dict):
                prose = str(artifacts.get("draft_prose") or "").strip()
                if prose:
                    return prose
    return str(state.get("final_response") or "").strip()


def _latest_writing_entry(state: dict[str, Any]) -> dict[str, Any] | None:
    worker_history = state.get("worker_history")
    if not isinstance(worker_history, list):
        return None
    for entry in reversed(worker_history):
        if isinstance(entry, dict) and entry.get("worker") == "writing_subagent":
            return entry
    return None


def _extract_pov_character_id(writing_entry: dict[str, Any]) -> str:
    result = writing_entry.get("result")
    if not isinstance(result, dict):
        return ""
    artifacts = result.get("artifacts")
    if isinstance(artifacts, dict):
        scene_metadata = artifacts.get("scene_metadata")
        if isinstance(scene_metadata, dict):
            pov_id = str(scene_metadata.get("pov_character_id") or "").strip()
            if pov_id:
                return pov_id
    context = writing_entry.get("context")
    if isinstance(context, dict):
        return str(context.get("pov_character_id") or "").strip()
    return ""


def _extract_chapter_context(writing_entry: dict[str, Any]) -> int:
    context = writing_entry.get("context")
    if isinstance(context, dict):
        try:
            value = int(context.get("chapter_context") or 1)
            if value > 0:
                return value
        except (TypeError, ValueError):
            return 1
    return 1


def _extract_polished_scene_prose(worker_result: dict[str, Any], fallback: str) -> str:
    result = worker_result.get("latest_worker_result")
    if not isinstance(result, dict):
        return fallback
    payload = result.get("result")
    if not isinstance(payload, dict):
        return fallback
    artifacts = payload.get("artifacts")
    if isinstance(artifacts, dict):
        prose = str(artifacts.get("draft_prose") or "").strip()
        if prose:
            return prose
    return fallback


def _run_second_pass_polish(
    *,
    config: NovelWriterConfig,
    scene_state: dict[str, Any],
    scene_text: str,
    verbose_turns: bool,
) -> tuple[str, dict[str, Any]]:
    writing_entry = _latest_writing_entry(scene_state)
    if not isinstance(writing_entry, dict):
        return scene_text, {
            "enabled": True,
            "status": "skipped",
            "reason": "No writing_subagent record found in scene state.",
        }

    base_context = writing_entry.get("context") if isinstance(writing_entry.get("context"), dict) else {}
    pov_character_id = _extract_pov_character_id(writing_entry)
    chapter_context = _extract_chapter_context(writing_entry)
    writing_worker = WritingSubagent(config)

    polish_context = {
        "problem_description": DEFAULT_POLISH_PROBLEM,
        "pov_character_id": pov_character_id,
        "chapter_context": chapter_context,
        "stuck_draft": scene_text,
        "technique_hint": DEFAULT_POLISH_HINT,
        "skill": "professional-writing-techniques",
        "operation": "professional-writing-techniques",
    }
    polish_state = {
        "worker_request": {
            "task": "Apply professional-writing-techniques to improve the opening-scene draft.",
            "context": polish_context,
        },
        "messages": [],
        "worker_history": [],
    }
    if verbose_turns:
        print("\n[Polish] Running professional-writing-techniques pass.", flush=True)
    polish_result = writing_worker.invoke(polish_state, config={})
    polish_latest = polish_result.get("latest_worker_result")
    polish_payload = polish_latest.get("result") if isinstance(polish_latest, dict) else {}
    polish_status = str(polish_payload.get("status") or "failed") if isinstance(polish_payload, dict) else "failed"

    guidance_artifacts = polish_payload.get("artifacts") if isinstance(polish_payload, dict) else {}
    if not isinstance(guidance_artifacts, dict):
        guidance_artifacts = {}

    if polish_status != "success":
        return scene_text, {
            "enabled": True,
            "status": "failed",
            "polish_summary": str(polish_payload.get("summary") or "") if isinstance(polish_payload, dict) else "",
            "rewrite_summary": "",
            "warning": "Professional-techniques pass failed; keeping first-pass scene.",
        }

    rewrite_context: dict[str, Any] = dict(base_context)
    rewrite_context.update(
        {
            "chapter_context": chapter_context,
            "pov_character_id": pov_character_id,
            "previous_draft": scene_text,
            "quality_polish_guidance": guidance_artifacts,
        }
    )
    rewrite_state = {
        "worker_request": {
            "task": (
                "Revise the opening scene draft using the provided professional-writing-techniques "
                "guidance while preserving plot intent, POV integrity, and thematic focus."
            ),
            "context": rewrite_context,
        },
        "messages": [],
        "worker_history": [],
    }
    if verbose_turns:
        print("[Polish] Running rewrite pass with guidance.", flush=True)
    rewrite_result = writing_worker.invoke(rewrite_state, config={})
    polished_text = _extract_polished_scene_prose(rewrite_result, scene_text)

    rewrite_latest = rewrite_result.get("latest_worker_result")
    rewrite_payload = rewrite_latest.get("result") if isinstance(rewrite_latest, dict) else {}
    rewrite_summary = str(rewrite_payload.get("summary") or "") if isinstance(rewrite_payload, dict) else ""
    polish_summary = str(polish_payload.get("summary") or "")
    return polished_text, {
        "enabled": True,
        "status": "success",
        "polish_summary": polish_summary,
        "rewrite_summary": rewrite_summary,
        "pov_character_id": pov_character_id,
        "chapter_context": chapter_context,
    }


def _write_scene_outputs(
    *,
    scene_output: Path,
    polished_scene_output: Path,
    trace_source: Path,
    state: dict[str, Any],
    scene_text: str,
    polished_scene_text: str,
    polish_info: dict[str, Any],
) -> Path:
    scene_output.parent.mkdir(parents=True, exist_ok=True)
    scene_output.write_text(scene_text, encoding="utf-8")
    polished_scene_output.parent.mkdir(parents=True, exist_ok=True)
    polished_scene_output.write_text(polished_scene_text, encoding="utf-8")

    metadata_path = scene_output.with_suffix(scene_output.suffix + ".meta.json")
    writing_summary = ""
    worker_history = state.get("worker_history")
    if isinstance(worker_history, list):
        for entry in reversed(worker_history):
            if isinstance(entry, dict) and entry.get("worker") == "writing_subagent":
                result = entry.get("result")
                if isinstance(result, dict):
                    writing_summary = str(result.get("summary") or "")
                break
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trace_source": str(trace_source),
        "worker_history_count": len(worker_history) if isinstance(worker_history, list) else 0,
        "writing_summary": writing_summary,
        "polished_scene_output": str(polished_scene_output),
        "second_pass_polish": polish_info,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=True, indent=2), encoding="utf-8")
    return metadata_path


def _capture_mode(trace_file: Path, verbose_turns: bool) -> int:
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["NOVELWRITER_E2E_TRACE_FILE"] = str(trace_file)
    if verbose_turns:
        env["NOVELWRITER_E2E_VERBOSE"] = "1"
    command = ["uv", "run", "pytest", "tests/test_e2e_full_stack.py", "-s", "-v", "-m", "e2e"]
    print(f"[capture] running: {' '.join(command)}", flush=True)
    completed = subprocess.run(command, env=env, check=False)
    return completed.returncode


def _force_preseed_kg_from_fixture(
    *,
    config: NovelWriterConfig,
    fixture_records: list[Any],
    verbose_turns: bool,
) -> dict[str, Any]:
    story_state_manager = StoryStateManager(config)
    mapper = PersistPayloadMapper()
    persisted = 0
    failed = 0
    skipped = 0
    records_updated_total = 0
    records_failed_total = 0
    failures: list[dict[str, Any]] = []

    for replay_record in fixture_records:
        artifacts = replay_record.result.artifacts if isinstance(replay_record.result.artifacts, dict) else {}
        chapter_context_raw = replay_record.context.get("chapter_context") if isinstance(replay_record.context, dict) else 1
        try:
            chapter_context = int(chapter_context_raw or 1)
        except (TypeError, ValueError):
            chapter_context = 1
        latest_worker_result = {
            "worker": replay_record.worker,
            "task": replay_record.task,
            "context": replay_record.context if isinstance(replay_record.context, dict) else {},
            "result": {"artifacts": artifacts},
        }
        mapper_result = mapper.build_context(latest_worker_result, {})
        context_payload = dict(mapper_result.context)
        payload_has_records = any(context_payload.get(key) for key in ("nodes_to_add", "nodes_to_update", "edges_to_add", "edges_to_update"))
        if not payload_has_records:
            fallback_payload = _fallback_payload_from_high_level_artifacts(
                worker=replay_record.worker,
                artifacts=artifacts,
                chapter_context=chapter_context,
            )
            for key in ("nodes_to_add", "edges_to_add"):
                if fallback_payload.get(key):
                    context_payload[key] = fallback_payload[key]
            payload_has_records = any(context_payload.get(key) for key in ("nodes_to_add", "nodes_to_update", "edges_to_add", "edges_to_update"))
        if not payload_has_records:
            skipped += 1
            if verbose_turns:
                print(
                    f"[preseed] skipped {replay_record.record_id} from {replay_record.worker}: "
                    "no writable payload after mapper and fallback synthesis",
                    flush=True,
                )
            continue

        persist_state = {
            "worker_request": {
                "task": (
                    "Persist accepted records to story state "
                    f"(force preseed from trace {replay_record.record_id} / {replay_record.worker})"
                ),
                "context": {
                    "chapter_context": chapter_context,
                    **context_payload,
                    "artifacts": artifacts,
                    "force_preseed_from_trace": True,
                    "source_worker": replay_record.worker,
                    "source_task_hash": replay_record.task_hash,
                    "source_record_id": replay_record.record_id,
                    "mapper_errors": mapper_result.errors,
                },
            }
        }
        invoke_result = story_state_manager.invoke(persist_state, config={})
        latest = invoke_result.get("latest_worker_result")
        result = latest.get("result") if isinstance(latest, dict) else {}
        status = str(result.get("status") or "")
        result_artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
        records_updated = result_artifacts.get("records_updated", [])
        records_failed = result_artifacts.get("records_failed", [])
        records_updated_total += len(records_updated) if isinstance(records_updated, list) else 0
        records_failed_total += len(records_failed) if isinstance(records_failed, list) else 0

        if status == "success":
            persisted += 1
            if verbose_turns:
                print(
                    f"[preseed] persisted {replay_record.record_id} from {replay_record.worker}: "
                    f"{len(records_updated) if isinstance(records_updated, list) else 0} records",
                    flush=True,
                )
        else:
            failed += 1
            failures.append(
                {
                    "record_id": replay_record.record_id,
                    "worker": replay_record.worker,
                    "status": status or "failed",
                    "summary": str(result.get("summary") or ""),
                    "records_failed": records_failed if isinstance(records_failed, list) else [],
                    "mapper_errors": mapper_result.errors,
                }
            )
            if verbose_turns:
                print(
                    f"[preseed] failed {replay_record.record_id} from {replay_record.worker}: {status}",
                    flush=True,
                )

    return {
        "persisted_records": persisted,
        "failed_records": failed,
        "skipped_records": skipped,
        "records_updated_total": records_updated_total,
        "records_failed_total": records_failed_total,
        "failures": failures,
    }


def _reset_kg_if_requested(db_name: str, reset_kg: bool) -> None:
    if not reset_kg:
        return
    os.environ["MONGODB_DB_NAME"] = db_name
    init_kg_db(db_name)
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stubbed replay flow with real writing worker.")
    parser.add_argument("--trace-file", type=Path, default=DEFAULT_CANONICAL_TRACE)
    parser.add_argument("--mode", choices=("capture", "replay"), default="replay")
    parser.add_argument("--runtime-trace-output", type=Path, default=DEFAULT_RUNTIME_TRACE)
    parser.add_argument("--scene-output", type=Path, default=Path("tmp/stubbed_scene_output.txt"))
    parser.add_argument(
        "--polished-scene-output",
        type=Path,
        default=Path("tmp/stubbed_scene_output.polished.txt"),
    )
    parser.add_argument("--bootstrap-input", type=str, default=BOOTSTRAP_INPUT)
    parser.add_argument("--scene-input", type=str, default=FIRST_SCENE_INPUT)
    parser.add_argument("--verbose-turns", action="store_true")
    parser.add_argument("--second-pass-polish", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--allow-synthetic", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--persist-synthetic-to-kg", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--force-preseed-kg-from-trace", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--reset-kg", action="store_true", help="Initialize and clear test KG before replay")
    parser.add_argument("--kg-db-name", type=str, default="novelwriter_test_kg")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    trace_file: Path = args.trace_file

    if args.mode == "capture":
        return _capture_mode(trace_file, args.verbose_turns)

    if not trace_file.exists():
        print(f"error: replay trace file not found: {trace_file}", file=sys.stderr)
        return 2

    runtime_trace_path: Path = args.runtime_trace_output
    runtime_trace_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_trace_path.write_text("", encoding="utf-8")

    _reset_kg_if_requested(args.kg_db_name, args.reset_kg)

    fixture, stats = load_fixture_from_trace(
        trace_file,
        exclude_workers={"writing_subagent", "story_state_manager"},
    )
    print(
        (
            "[replay] extracted_after_filter={after} extracted_before_filter={before} "
            "matched_update_events={matched}"
        ).format(
            after=fixture.meta.extracted_record_count,
            before=stats["extracted_record_count_before_filter"],
            matched=fixture.meta.matched_update_events,
        ),
        flush=True,
    )

    config = NovelWriterConfig(max_brain_iterations=80, max_rejection_budget=3)
    if args.force_preseed_kg_from_trace:
        print("[preseed] force preseed from trace enabled", flush=True)
        preseed_result = _force_preseed_kg_from_fixture(
            config=config,
            fixture_records=fixture.records,
            verbose_turns=bool(args.verbose_turns),
        )
        print(
            (
                "[preseed] persisted_records={persisted} failed_records={failed} "
                "skipped_records={skipped} records_updated_total={updated} records_failed_total={records_failed}"
            ).format(
                persisted=preseed_result["persisted_records"],
                failed=preseed_result["failed_records"],
                skipped=preseed_result["skipped_records"],
                updated=preseed_result["records_updated_total"],
                records_failed=preseed_result["records_failed_total"],
            ),
            flush=True,
        )
        if preseed_result["failed_records"] > 0:
            print(
                "[preseed] error: one or more force-preseed writes failed; aborting replay run.",
                file=sys.stderr,
            )
            return 4

    ssm_instance = StoryStateManager(config)
    replay_engine = StubReplayEngine(
        fixture=fixture,
        runtime_trace_path=runtime_trace_path,
        allow_synthetic=bool(args.allow_synthetic),
        persist_synthetic_to_kg=bool(args.persist_synthetic_to_kg),
        story_state_manager=ssm_instance if args.persist_synthetic_to_kg else None,
    )
    worker_impls: dict[str, Any] = {
        "writing_subagent": WritingSubagent,
        "story_state_manager": StoryStateManager,
    }
    for worker_name in REPLAY_STUB_WORKERS:
        worker_impls[worker_name] = make_replay_stub_worker(
            worker_name=worker_name,
            replay_engine=replay_engine,
        )

    orchestrator = GRRMOrchestrator(
        config=config,
        worker_impls=worker_impls,
        checkpointer=InMemorySaver(),
    )

    thread_id = f"stubbed-replay-{uuid.uuid4()}"
    _run_turn(
        orchestrator,
        thread_id,
        args.bootstrap_input,
        turn_title="Turn 1 (bootstrap)",
        verbose_turns=bool(args.verbose_turns),
    )
    scene_state = _run_turn(
        orchestrator,
        thread_id,
        args.scene_input,
        turn_title="Turn 2 (first scene)",
        verbose_turns=bool(args.verbose_turns),
    )

    scene_text = _extract_scene_prose(scene_state)
    if not scene_text:
        print("error: writing scene prose is empty after replay flow", file=sys.stderr)
        return 3

    polished_scene_text = scene_text
    polish_info: dict[str, Any] = {"enabled": bool(args.second_pass_polish), "status": "skipped"}
    if args.second_pass_polish:
        polished_scene_text, polish_info = _run_second_pass_polish(
            config=config,
            scene_state=scene_state,
            scene_text=scene_text,
            verbose_turns=bool(args.verbose_turns),
        )

    metadata_path = _write_scene_outputs(
        scene_output=args.scene_output,
        polished_scene_output=args.polished_scene_output,
        trace_source=trace_file,
        state=scene_state,
        scene_text=scene_text,
        polished_scene_text=polished_scene_text,
        polish_info=polish_info,
    )
    print(f"[replay] scene output: {args.scene_output}", flush=True)
    print(f"[replay] polished scene output: {args.polished_scene_output}", flush=True)
    print(f"[replay] metadata output: {metadata_path}", flush=True)
    print(f"[replay] runtime trace: {runtime_trace_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
