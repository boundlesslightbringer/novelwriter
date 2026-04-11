"""
End-to-end full-stack integration test (real brain + real workers + Mongo KG).

Run:
  uv run pytest test_e2e_full_stack.py -s -v -m e2e
"""

import os
import uuid

import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from src.config import NovelWriterConfig
from src.orchestrator import GRRMOrchestrator
from src.world_bible_tools import _get_db, init_kg_db

BOOTSTRAP_INPUT = "genre: High Fantasy, themes: legitimacy and the cost of inheritance"
FIRST_SCENE_INPUT = "write the first scene"


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


def _run_turn(orchestrator: GRRMOrchestrator, thread_id: str, user_text: str) -> dict:
    run_config = {"configurable": {"thread_id": thread_id}}
    orchestrator.graph.invoke(_turn_input(user_text), config=run_config)
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
    state_after_bootstrap = _run_turn(orchestrator, thread_id, BOOTSTRAP_INPUT)
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
    state_after_scene = _run_turn(orchestrator, thread_id, FIRST_SCENE_INPUT)
    worker_history_after_scene = state_after_scene.get("worker_history", [])

    chapter_count = db.nodes.count_documents({"type": "Chapter", "valid_to": None})
    assert chapter_count > 0, "No Chapter nodes after first scene"

    writing_results = [
        entry for entry in worker_history_after_scene if entry.get("worker") == "writing_subagent"
    ]
    assert any(
        entry.get("result", {}).get("artifacts", {}).get("draft_prose") for entry in writing_results
    ), "No draft_prose found in writing_subagent history"
