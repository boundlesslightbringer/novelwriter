"""
Integration test: runs the real writing subagent path (Vertex / Gemini).

Run with output visible:
  uv run pytest test_writing_subagent.py -s -v -m integration
"""

import json
import os

import pytest

from src.agents.workers import WritingSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, add_kg_edge, add_kg_node, init_kg_db


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    add_kg_node.invoke(
        {
            "logical_id": "char_maera",
            "node_type": "Character",
            "properties": {
                "full_name": "Maera Voss",
                "core_contradiction": "She wants control but keeps choosing loyalty.",
                "core_fear": "Abandonment during crisis.",
                "core_wound": "Betrayed by her first command.",
                "self_deception": "She believes attachment does not affect her decisions.",
                "response_patterns": {
                    "under_pressure": "Appears cold, then makes protective sacrifices."
                },
                "voice_profile": {
                    "lexicon": "precise and tactical",
                    "sentence_shape": "short declaratives under stress",
                },
            },
            "chapter": 1,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "cc_border_reprisals",
            "node_type": "CascadeChain",
            "properties": {
                "name": "Border Reprisals",
                "involved_character_ids": ["char_maera"],
                "current_position": "Town officials deny supplies",
                "remaining_links": ["Militia mutiny", "Civilian evacuation"],
            },
            "chapter": 4,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "chapter_3",
            "node_type": "Chapter",
            "properties": {
                "chapter_number": 3,
                "summary": "Maera loses half her scouts near the eastern ridge.",
            },
            "chapter": 3,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "chapter_4",
            "node_type": "Chapter",
            "properties": {
                "chapter_number": 4,
                "summary": "Supply lines collapse after the council vote.",
            },
            "chapter": 4,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "ki_militia_shortage",
            "node_type": "KnowledgeItem",
            "properties": {
                "description": "The militia food reserve will fail in three days.",
            },
            "chapter": 4,
        }
    )
    add_kg_edge.invoke(
        {
            "logical_id": "edge_maera_knows_shortage",
            "edge_type": "KNOWS",
            "from_node": "char_maera",
            "to_node": "ki_militia_shortage",
            "properties": {"status": "KNOWS"},
            "chapter": 4,
        }
    )

    yield


@pytest.mark.integration
def test_professional_writing_techniques_success() -> None:
    config = NovelWriterConfig()
    subagent = WritingSubagent(config)

    state = {
        "worker_request": {
            "task": "Use professional-writing-techniques to resolve a stuck scene choice.",
            "context": {
                "skill": "professional-writing-techniques",
                "problem_description": (
                    "The scene choice feels arbitrary. Both options seem equally available and the "
                    "character motivation does not feel earned."
                ),
                "pov_character_id": "char_maera",
                "chapter_context": 5,
                "stuck_draft": "Maera stared at both exits and picked one without conviction.",
                "technique_hint": "Character Interview",
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== Phase: invoke WritingSubagent (professional-writing-techniques) ===")
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

    for required_key in (
        "technique_applied",
        "problem_diagnosis",
        "path_forward",
        "scene_construction_context",
        "kg_context_used",
    ):
        assert required_key in artifacts, f"Missing '{required_key}' in artifacts"

    assert artifacts["technique_applied"] != ""
    assert artifacts["scene_construction_context"] != ""
    assert artifacts["problem_diagnosis"].get("problem_type", "") != ""
    assert artifacts["problem_diagnosis"].get("root_cause", "") != ""
    assert artifacts["path_forward"].get("primary_recommendation", "") != ""
    assert artifacts["path_forward"].get("worked_application", "") != ""
    assert isinstance(artifacts["path_forward"].get("alternatives"), list)

    kg_context = artifacts["kg_context_used"]
    assert kg_context.get("character_node_found") is True
    assert kg_context.get("cascade_chains_checked") is True
    assert kg_context.get("recent_chapters_checked") is False


def test_professional_writing_techniques_missing_context() -> None:
    config = NovelWriterConfig()
    subagent = WritingSubagent(config)

    state = {
        "worker_request": {
            "task": "Use professional-writing-techniques to resolve a stuck scene choice.",
            "context": {
                "skill": "professional-writing-techniques",
                "pov_character_id": "char_maera",
                "chapter_context": 5,
            },
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    artifacts = structured_result.get("artifacts", {})
    assert structured_result.get("status") == "need_input"
    assert artifacts.get("error") == "missing_required_context"
    assert "problem_description" in artifacts.get("missing_fields", [])


@pytest.mark.integration
def test_pov_consistency_maintenance_success() -> None:
    config = NovelWriterConfig()
    subagent = WritingSubagent(config)

    state = {
        "worker_request": {
            "task": "Run pov-consistency-maintenance on this draft scene.",
            "context": {
                "skill": "pov-consistency-maintenance",
                "pov_character_id": "char_maera",
                "chapter_context": 5,
                "draft_scene": (
                    "Maera counted each ration crate and noted the chalk marks near the hinge. "
                    "The quartermaster's hands shook as he reached for the ledger."
                ),
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== Phase: invoke WritingSubagent (pov-consistency-maintenance) ===")
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

    for required_key in ("audit_header", "violation_log", "summary_pattern_note", "kg_context_used"):
        assert required_key in artifacts, f"Missing '{required_key}' in artifacts"

    audit_header = artifacts["audit_header"]
    assert audit_header.get("pov_character_id") == "char_maera"
    assert audit_header.get("overall_status") in {"CLEAN", "VIOLATIONS FOUND"}
    assert isinstance(audit_header.get("violation_types_found", []), list)
    assert isinstance(artifacts.get("violation_log", []), list)

    kg_context = artifacts["kg_context_used"]
    assert kg_context.get("character_node_found") is True
    assert kg_context.get("voice_profile_found") is True
    assert kg_context.get("knows_edges_found", 0) >= 1


def test_pov_consistency_maintenance_missing_context() -> None:
    config = NovelWriterConfig()
    subagent = WritingSubagent(config)

    state = {
        "worker_request": {
            "task": "Run pov-consistency-maintenance on this draft scene.",
            "context": {
                "skill": "pov-consistency-maintenance",
                "pov_character_id": "char_maera",
                "chapter_context": 5,
            },
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    artifacts = structured_result.get("artifacts", {})
    assert structured_result.get("status") == "need_input"
    assert artifacts.get("error") == "missing_required_context"
    assert "draft_scene" in artifacts.get("missing_fields", [])
