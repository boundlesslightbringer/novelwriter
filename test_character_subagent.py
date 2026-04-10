"""
Integration tests for character-creation subgraph behavior in CharacterSubagent.

Run with output visible:
  uv run pytest test_character_subagent.py -s -v -m integration
"""

import json
import os

import pytest

from src.agents.workers import CharacterSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, add_kg_node, init_kg_db


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    add_kg_node.invoke(
        {
            "logical_id": "faction_royal_intelligence",
            "node_type": "Faction",
            "properties": {"name": "Royal Intelligence Office"},
            "chapter": 0,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "culture_river_kingdom",
            "node_type": "Culture",
            "properties": {"name": "River Kingdom Court Culture"},
            "chapter": 0,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "loc_glass_harbor",
            "node_type": "Location",
            "properties": {"name": "Glass Harbor"},
            "chapter": 0,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "char_mira_vale",
            "node_type": "Character",
            "properties": {"full_name": "Mira Vale"},
            "chapter": 0,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "ki_harbor_ward_schedule",
            "node_type": "KnowledgeItem",
            "properties": {"description": "Wardens rotate every third bell."},
            "chapter": 0,
        }
    )

    yield

    db.nodes.delete_many({})
    db.edges.delete_many({})


def _assert_required_artifact_shape(artifacts: dict) -> None:
    assert "character_node" in artifacts
    assert "knowledge_items" in artifacts
    assert "knowledge_matrix_edges" in artifacts
    assert "relationship_edges" in artifacts
    assert "culture_edge" in artifacts

    character_node = artifacts["character_node"]
    assert isinstance(character_node, dict)
    assert isinstance(character_node.get("properties"), dict)

    props = character_node["properties"]
    assert props.get("response_patterns") is not None
    assert isinstance(props.get("response_patterns"), dict)
    assert props.get("values_under_pressure") is not None
    assert props.get("contradictions") is not None

    for edge in artifacts.get("knowledge_matrix_edges", []):
        assert edge.get("properties") is not None
    for edge in artifacts.get("relationship_edges", []):
        assert edge.get("properties") is not None
    assert artifacts.get("culture_edge", {}).get("properties") is not None

    assert "kg_context_used" in artifacts
    assert "warnings" in artifacts


@pytest.mark.integration
def test_character_creation_subgraph_success() -> None:
    config = NovelWriterConfig()
    subagent = CharacterSubagent(config)

    state = {
        "worker_request": {
            "task": "Use character-creation to build full character records from this concept.",
            "context": {
                "skill": "character-creation",
                "chapter_context": 1,
                "character_concept": {
                    "assigned_narrative_role": "Secondary POV and reluctant informer",
                    "generation_method": "Archetype-subversion",
                    "core_contradiction": "Swears loyalty publicly while secretly feeding truths to enemies.",
                    "sketch": "A meticulous court cipher clerk whose empathy keeps undermining her assignments.",
                    "open_questions": [
                        "What wound made loyalty feel dangerous?",
                        "Who does she fear disappointing more: her faction or her sister?",
                        "What belief keeps her from admitting she is choosing a side?",
                    ],
                    "provisional_flag": {"present": False, "notes": ""},
                    "kg_context_used": {"standard_mode": True},
                },
            },
        },
        "messages": [],
        "worker_history": [],
    }

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

    print("\n=== Full artifacts (truncated) ===")
    print(json.dumps(artifacts, indent=2, default=str)[:12000])
    _assert_required_artifact_shape(artifacts)


@pytest.mark.integration
def test_character_creation_subgraph_need_input_on_missing_context() -> None:
    config = NovelWriterConfig()
    subagent = CharacterSubagent(config)

    state = {
        "worker_request": {
            "task": "Use character-creation with missing required fields.",
            "context": {"skill": "character-creation"},
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    assert structured_result.get("status") == "need_input"
    artifacts = structured_result.get("artifacts", {})
    assert artifacts.get("error") == "missing_required_fields"
    missing_fields = artifacts.get("missing_fields", [])
    assert "character_concept" in missing_fields
    assert "chapter_context" in missing_fields
