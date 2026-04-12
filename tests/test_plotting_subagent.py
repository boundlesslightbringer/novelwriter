"""
Integration test: runs the real plotting subagent chain (Vertex / Gemini).

Run with output visible:
  uv run pytest tests/test_plotting_subagent.py -s -v -m integration
"""

import json
import os
from typing import Any

import pytest

from src.agents.workers import PlottingSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, add_kg_node, add_kg_edge, init_kg_db


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    # 1. Character
    add_kg_node.invoke(
        {
            "logical_id": "char_elara",
            "node_type": "Character",
            "properties": {
                "full_name": "Elara",
                "core_desire": "To steal the cursed artifact.",
                "core_fear": "Being caught.",
                "core_wound": "Grew up on the streets.",
                "self_deception": "She thinks she can outsmart anyone.",
                "response_patterns": {"danger": "Fight or flight."},
            },
            "chapter": 0,
        }
    )

    # 2. KnowledgeItem & KNOWS edge
    add_kg_node.invoke(
        {
            "logical_id": "ki_vault_security",
            "node_type": "KnowledgeItem",
            "properties": {
                "description": "The city guard vault has a secondary, ancient drainage tunnel that is rarely guarded.",
            },
            "chapter": 1,
        }
    )
    add_kg_edge.invoke(
        {
            "logical_id": "edge_elara_knows_vault",
            "edge_type": "KNOWS",
            "from_node": "char_elara",
            "to_node": "ki_vault_security",
            "properties": {
                "status": "KNOWS",
            },
            "chapter": 1,
        }
    )

    # 3. PlotThread & INVOLVES edge
    add_kg_node.invoke(
        {
            "logical_id": "thread_cursed_artifact",
            "node_type": "PlotThread",
            "properties": {
                "name": "The Cursed Artifact",
                "status": "Active",
                "originating_chapter": 1,
            },
            "chapter": 1,
        }
    )
    add_kg_edge.invoke(
        {
            "logical_id": "edge_elara_involves_artifact",
            "edge_type": "INVOLVES",
            "from_node": "thread_cursed_artifact",
            "to_node": "char_elara",
            "properties": {
                "role": "Thief",
            },
            "chapter": 1,
        }
    )

    # 4. CascadeChain & INVOLVES edge
    add_kg_node.invoke(
        {
            "logical_id": "cc_alarm_triggered",
            "node_type": "CascadeChain",
            "properties": {
                "sequence": ["Alarm triggered", "Guards mobilized", "City locked down"],
                "current_position": "Guards mobilized",
                "remaining_links": ["City locked down"],
            },
            "chapter": 5,
        }
    )
    add_kg_edge.invoke(
        {
            "logical_id": "edge_elara_involves_cascade",
            "edge_type": "INVOLVES",
            "from_node": "cc_alarm_triggered",
            "to_node": "char_elara",
            "properties": {
                "role": "Target",
            },
            "chapter": 5,
        }
    )

    # 5. Payoff
    add_kg_node.invoke(
        {
            "logical_id": "payoff_artifact_curse",
            "node_type": "Payoff",
            "properties": {
                "type": "Consequence bomb",
                "description": "The artifact's curse binding to its user when exposed to their blood/fear.",
                "planted_in_chapter": 2,
                "narrative_phase_anchor": "mid",
                "detonation_trigger": "The user bleeds on the artifact while terrified.",
                "resolution_status": "Pending",
                "priority_tier": "Essential",
                "dual_register": True,
            },
            "chapter": 2,
        }
    )

    yield


@pytest.mark.integration
def test_gardener_plotting_system() -> None:
    config = NovelWriterConfig()
    subagent = PlottingSubagent(config)

    state = {
        "worker_request": {
            "task": "Use gardener-plotting-system to determine the next scene parameters for Elara.",
            "context": {
                "skill": "gardener-plotting-system",
                "pov_character_id": "char_elara",
                "chapter_context": 5,
                "last_scene_outcome": "Elara successfully stole the cursed artifact but triggered the alarm and is now trapped in the city guard's vault.",
                "include_foreshadowing_check": True,
                "simultaneous_events": [],
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== Phase: invoke PlottingSubagent (gardener-plotting-system) ===")
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

    assert "skills_used" in artifacts, "Missing 'skills_used' in artifacts"
    assert "gardener-plotting-system" in artifacts["skills_used"], "Expected gardener skill marker"
    assert "scene_parameters" in artifacts, "Missing 'scene_parameters' in artifacts"
    scene_params = artifacts["scene_parameters"]
    assert "character_logic_audit" in scene_params, "Missing 'character_logic_audit' in scene_parameters"
    assert scene_params["character_logic_audit"], "character_logic_audit is empty"
    assert scene_params.get("obstacle") is not None, "obstacle is null"
    assert scene_params.get("the_choice") is not None, "the_choice is null"

    kg_context_used = artifacts.get("kg_context_used", {})
    assert kg_context_used.get("character_node_found") is True, "Character node was not found"
    assert kg_context_used.get("knows_edges_found", 0) == 1, "Unexpected KNOWS edge count"
    assert kg_context_used.get("active_threads_found", 0) == 1, "Unexpected active thread count"
    assert kg_context_used.get("cascade_chains_found", 0) == 1, "Unexpected cascade chain count"
    assert kg_context_used.get("pending_payoffs_checked") is True, "Pending payoff check did not run"

    foreshadowing_opportunity = artifacts.get("foreshadowing_opportunity", {})
    assert foreshadowing_opportunity.get("present") is True, "Foreshadowing opportunity not present"
    assert foreshadowing_opportunity.get("payoff_id"), "Missing foreshadowing payoff_id"

    print("\n=== Test gate passed ===\n")
