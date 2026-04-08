"""
Integration test: runs the real planning subagent chain (Vertex / Gemini).

Run with output visible:
  uv run pytest test_planning_subagent.py -s -v -m integration
"""

import json
import os
from typing import Any

import pytest

from src.agents.workers import PlanningSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, init_kg_db


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    yield

    db.nodes.delete_many({})
    db.edges.delete_many({})


@pytest.mark.integration
def test_finding_a_seed() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    state = {
        "worker_request": {
            "task": "Use finding-a-seed to generate a rich conceptual seed for a High Fantasy novel.",
            "context": {
                "genre": "High Fantasy",
                "themes": ["divinity vs reality", "the cost of immortality"]
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== Phase: invoke PlanningSubagent (finding-a-seed) ===")
    result = subagent.invoke(state)

    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    status = structured_result.get("status")
    artifacts = structured_result.get("artifacts", {})

    print(f"\nWorker status: {status}")
    if status != "success":
        print(f"Failure detail: {json.dumps(artifacts, indent=2, default=str)}")
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"

    print("\n=== Full artifacts (truncated strings for readability) ===")
    print(json.dumps(artifacts, indent=2, default=str)[:12000])

    assert "seed_document" in artifacts, "Missing 'seed_document' in artifacts"
    seed_doc = artifacts["seed_document"]
    assert seed_doc, "seed_document is empty"
    assert "validation_record" in seed_doc, "Missing 'validation_record' in seed_document"
    assert seed_doc["validation_record"], "validation_record is empty"

    print("\n=== Test gate passed ===\n")