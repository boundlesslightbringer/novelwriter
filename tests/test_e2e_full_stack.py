"""
End-to-end full-stack integration test (real brain + real workers + Mongo KG).

Run:
  uv run pytest tests/test_e2e_full_stack.py -s -v -m e2e

Turn-by-turn progress (brain delegations, worker completions, streaming respond text):
  NOVELWRITER_E2E_VERBOSE=1 uv run pytest tests/test_e2e_full_stack.py -s -v -m e2e
"""

import os
import uuid
from typing import Any

import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from src.config import NovelWriterConfig
from src.orchestrator import GRRMOrchestrator
from src.world_bible_tools import _get_db, init_kg_db

BOOTSTRAP_INPUT = "genre: High Fantasy, themes: legitimacy and the cost of inheritance"
FIRST_SCENE_INPUT = "write the first scene"

_E2E_KG_TYPES_FOR_LOG = (
    "PlotThread",
    "Payoff",
    "Faction",
    "Location",
    "Culture",
    "Event",
    "MagicSystem",
    "Character",
    "Chapter",
)


def _e2e_verbose_enabled() -> bool:
    return str(os.environ.get("NOVELWRITER_E2E_VERBOSE", "")).strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _render_worker_history(worker_history: Any) -> str:
    if not isinstance(worker_history, list) or not worker_history:
        return "No worker history recorded."

    lines: list[str] = []
    for idx, entry in enumerate(worker_history, start=1):
        row = entry if isinstance(entry, dict) else {}
        result = row.get("result", {}) if isinstance(row.get("result"), dict) else {}
        lines.append(
            f"{idx}. {row.get('worker', 'unknown')} -> {result.get('status', 'unknown')}: "
            f"{result.get('summary', '')}"
        )
    return "\n".join(lines)


def _print_graph_progress(orchestrator: GRRMOrchestrator, event_type: str, event_data: Any) -> None:
    """Same visibility as mvp_poc_novel.py: brain delegations and worker completions."""
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
    elif event_type == "messages":
        chunk, metadata = event_data
        if metadata.get("langgraph_node") == "respond" and getattr(chunk, "content", None):
            content = chunk.content
            if isinstance(content, str) and content:
                print(content, end="", flush=True)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, str) and part:
                        print(part, end="", flush=True)
                    elif isinstance(part, dict) and part.get("type") == "text":
                        print(part.get("text", ""), end="", flush=True)


def _log_kg_counts(label: str, db: Any) -> None:
    parts = []
    for node_type in _E2E_KG_TYPES_FOR_LOG:
        n = db.nodes.count_documents({"type": node_type, "valid_to": None})
        parts.append(f"{node_type}={n}")
    print(f"\n[E2E] {label}: " + ", ".join(parts), flush=True)


def _log_turn_footer(
    *,
    turn_title: str,
    state: dict[str, Any],
    db: Any,
) -> None:
    print(f"\n[E2E] --- End {turn_title} ---", flush=True)
    fr = str(state.get("final_response") or "").strip()
    if fr:
        preview = fr[:400] + ("…" if len(fr) > 400 else "")
        print(f"[E2E] final_response ({len(fr)} chars): {preview}", flush=True)
    print(f"[E2E] worker_history entries: {len(state.get('worker_history') or [])}", flush=True)
    print(_render_worker_history(state.get("worker_history")), flush=True)
    _log_kg_counts(f"Mongo after {turn_title}", db)
    print(flush=True)


@pytest.fixture(autouse=True)
def setup_e2e_kg() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")

    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})
    yield
    db.nodes.delete_many({})
    db.edges.delete_many({})


def _turn_input(user_text: str) -> dict:
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


def _run_turn(
    orchestrator: GRRMOrchestrator,
    thread_id: str,
    user_text: str,
    *,
    turn_title: str,
    db: Any,
) -> dict:
    run_config = {"configurable": {"thread_id": thread_id}}
    turn_input = _turn_input(user_text)

    if _e2e_verbose_enabled():
        print(f"\n[E2E] ========== {turn_title} ==========", flush=True)
        print(f"[E2E] User: {user_text!r}", flush=True)
        print("(Live graph stream; disable with unset NOVELWRITER_E2E_VERBOSE)\n", flush=True)
        for event_type, event_data in orchestrator.graph.stream(
            turn_input,
            config=run_config,
            stream_mode=["messages", "updates"],
        ):
            _print_graph_progress(orchestrator, event_type, event_data)
        print(flush=True)
        state = dict(orchestrator.graph.get_state(run_config).values)
        _log_turn_footer(turn_title=turn_title, state=state, db=db)
        return state

    orchestrator.graph.invoke(turn_input, config=run_config)
    return orchestrator.graph.get_state(run_config).values


@pytest.mark.e2e
@pytest.mark.integration
def test_e2e_bootstrap_then_first_scene() -> None:
    config = NovelWriterConfig(max_brain_iterations=80, max_rejection_budget=3)
    orchestrator = GRRMOrchestrator(
        config=config,
        worker_impls=GRRMOrchestrator.real_worker_impls(),
        checkpointer=InMemorySaver(),
    )

    db = _get_db()
    thread_id = f"e2e-{uuid.uuid4()}"

    # Turn 1 — bootstrap
    state_after_bootstrap = _run_turn(
        orchestrator,
        thread_id,
        BOOTSTRAP_INPUT,
        turn_title="Turn 1 (bootstrap)",
        db=db,
    )
    worker_history_after_bootstrap = state_after_bootstrap.get("worker_history", [])

    expected_types = [
        "PlotThread",
        "Payoff",
        "Faction",
        "Location",
        "Culture",
        "Event",
        "MagicSystem",
        "Character",
    ]
    for node_type in expected_types:
        count = db.nodes.count_documents({"type": node_type, "valid_to": None})
        assert count > 0, f"Missing {node_type} nodes after bootstrap"

    assert 8 <= len(worker_history_after_bootstrap) <= 12, (
        f"Unexpected worker_history length after bootstrap: {len(worker_history_after_bootstrap)}"
    )
    assert not any(
        entry.get("result", {}).get("status") == "failed" for entry in worker_history_after_bootstrap
    ), "Bootstrap includes failed worker results"

    # Turn 2 — first scene, same checkpoint thread/session
    state_after_scene = _run_turn(
        orchestrator,
        thread_id,
        FIRST_SCENE_INPUT,
        turn_title="Turn 2 (first scene)",
        db=db,
    )
    worker_history_after_scene = state_after_scene.get("worker_history", [])

    chapter_count = db.nodes.count_documents({"type": "Chapter", "valid_to": None})
    assert chapter_count > 0, "No Chapter nodes after first scene"

    writing_results = [
        entry for entry in worker_history_after_scene if entry.get("worker") == "writing_subagent"
    ]
    assert any(
        entry.get("result", {}).get("artifacts", {}).get("draft_prose") for entry in writing_results
    ), "No draft_prose found in writing_subagent history"
