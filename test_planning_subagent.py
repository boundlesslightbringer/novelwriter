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
from src.world_bible_tools import _get_db, add_kg_node, init_kg_db


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
    validation_record = seed_doc["validation_record"]
    assert set(validation_record.keys()) == {
        "concreteness",
        "generative_tension",
        "emotional_necessity",
        "open_architecture",
    }, "validation_record must contain exactly the four required criteria"
    assert all(
        str(validation_record[key]).startswith(("PASS", "FAIL"))
        for key in validation_record
    ), "Each validation criterion must begin with PASS or FAIL"

    assert "candidate_seeds_log" in artifacts, "Missing 'candidate_seeds_log' in artifacts"
    candidate_log = artifacts["candidate_seeds_log"]
    assert isinstance(candidate_log, list) and candidate_log, "candidate_seeds_log is empty"
    logged_methods = {entry.get("method") for entry in candidate_log}
    assert logged_methods == {
        "Vivid Image",
        "What If?",
        "Character-First",
        "Historical Inspiration",
    }, "candidate_seeds_log must include one entry per generation method"
    assert all(
        entry.get("status") in {"Rejected", "Merged", "Held as alternative"}
        for entry in candidate_log
    ), "candidate_seeds_log contains invalid status values"

    assert artifacts.get("genre") == "High Fantasy", "genre must be echoed in artifacts"
    assert artifacts.get("themes") == [
        "divinity vs reality",
        "the cost of immortality",
    ], "themes must be echoed in artifacts"

    print("\n=== Test gate passed ===\n")


def test_finding_a_seed_missing_required_context() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    state = {
        "worker_request": {
            "task": "Use finding-a-seed to generate a rich conceptual seed for a High Fantasy novel.",
            "context": {
                "themes": ["identity"]
            },
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    assert structured_result.get("status") == "need_input"
    assert structured_result.get("artifacts", {}).get("error") == "missing_required_context"
    assert "genre" in structured_result.get("artifacts", {}).get("missing_fields", [])
    assert structured_result.get("follow_up_questions"), "Missing follow-up questions"


@pytest.mark.integration
def test_defining_rough_endpoints_pass_1() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    state = {
        "worker_request": {
            "task": "Use defining-rough-endpoints pass 1 to produce draft compass milestones.",
            "context": {
                "skill": "defining-rough-endpoints",
                "pass": 1,
                "seed_document": {
                    "seed": "A divine healer cannot die while a crumbling city keeps praying them back to life.",
                    "generation_method": "Character-First",
                    "validation_record": {
                        "concreteness": "PASS - The image is concrete.",
                        "generative_tension": "PASS - The contradiction is fertile.",
                        "emotional_necessity": "PASS - Human stakes are immediate.",
                        "open_architecture": "PASS - Multiple story paths remain open.",
                    },
                    "genre_theme_fit": "High fantasy with theological pressure and mortal cost.",
                    "questions": [
                        "What breaks first in the healer?",
                        "Who controls the prayers?",
                        "Can the city survive without immortality?",
                        "What truth is hidden about the plague?",
                        "What sacrifice can end the cycle?",
                    ],
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
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"
    assert artifacts.get("pass") == 1, "Expected pass=1 artifacts"
    assert isinstance(artifacts.get("prologue_specification"), dict), "prologue_specification must be an object"
    assert "draft_milestones" in artifacts and artifacts["draft_milestones"], "Missing draft_milestones"
    assert "character_slot_sketches" in artifacts and artifacts["character_slot_sketches"], "Missing character_slot_sketches"
    assert all(
        "milestone_id" in milestone and "character_slots" in milestone
        for milestone in artifacts["draft_milestones"]
    ), "Pass 1 milestone schema is incomplete"
    assert all(
        "slot_id" in slot and "narrative_role" in slot and "open_questions" in slot
        for slot in artifacts["character_slot_sketches"]
    ), "Pass 1 character slot schema is incomplete"


@pytest.mark.integration
def test_defining_rough_endpoints_pass_2() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    pass_1_output = {
        "pass": 1,
        "prologue_specification": {
            "warranted": True,
            "temporal_relationship": "One generation before chapter 1",
            "pov_or_register": "Witness account",
            "what_it_establishes": "The city binds miracles to civic control.",
            "what_it_withholds": "The origin of the binding ritual.",
            "relationship_to_milestones": "Precondition",
        },
        "starting_situation": "A holy city survives only by forcing a single immortal to remain alive.",
        "draft_ending_destination": "Either the city learns to survive without divine captivity or collapses with it.",
        "draft_milestones": [
            {"milestone_id": "M1", "description": "Ritual is challenged.", "character_slots": ["slot_A"]},
            {"milestone_id": "M2", "description": "Hidden architects are revealed.", "character_slots": ["slot_B"]},
        ],
        "character_slot_sketches": [
            {
                "slot_id": "slot_A",
                "narrative_role": "Healer under pressure",
                "implied_contradiction": "Mercy vs resentment",
                "stakes": "Life, faith, and agency",
                "world_context": "Theocratic city",
                "open_questions": ["What would make the healer choose death now?"],
            }
        ],
        "draft_core_conflict_question": "Can a society built on coerced miracles survive the truth?",
        "compass_notes": "Leave the end morally open.",
    }
    character_concepts = [
        {
            "slot_id": "slot_A",
            "character_id": "char_healer",
            "name": "Aster",
            "core_contradiction": "Compassion that now feels like complicity",
        },
        {
            "slot_id": "slot_B",
            "character_id": "char_regent",
            "name": "Regent Ilyas",
            "core_contradiction": "Public piety masking political fear",
        },
    ]

    state = {
        "worker_request": {
            "task": "Use defining-rough-endpoints pass 2 to refine milestones with character concepts.",
            "context": {
                "skill": "defining-rough-endpoints-pass-2",
                "pass": 2,
                "pass_1_output": pass_1_output,
                "character_concepts": character_concepts,
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
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"
    assert artifacts.get("pass") == 2, "Expected pass=2 artifacts"
    assert "milestones" in artifacts and artifacts["milestones"], "Missing pass 2 milestones"
    assert all(
        "milestone_id" in milestone and "character_references" in milestone
        for milestone in artifacts["milestones"]
    ), "Pass 2 milestone schema is incomplete"
    assert "plot_thread_seeds" in artifacts and artifacts["plot_thread_seeds"], "Missing plot_thread_seeds"
    assert "payoff_seeds" in artifacts and artifacts["payoff_seeds"], "Missing payoff_seeds"
    assert all(
        seed.get("node_type") == "PlotThread"
        for seed in artifacts["plot_thread_seeds"]
    ), "plot_thread_seeds must contain PlotThread records"
    assert all(
        seed.get("node_type") == "Payoff"
        for seed in artifacts["payoff_seeds"]
    ), "payoff_seeds must contain Payoff records"


def test_defining_rough_endpoints_pass_2_missing_context() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    state = {
        "worker_request": {
            "task": "Use defining-rough-endpoints pass 2 to refine milestones.",
            "context": {
                "skill": "defining-rough-endpoints-pass-2",
                "pass": 2,
                "character_concepts": [],
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
    assert set(artifacts.get("missing_fields", [])) == {
        "pass_1_output",
        "character_concepts",
    }


@pytest.mark.integration
def test_worldbuilding_initial_build() -> None:
    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)

    endpoint_compass = {
        "pass": 2,
        "starting_situation": "A sacred city clings to life through coerced miracles.",
        "ending_destination": "The city must either accept mortal limits or collapse.",
        "milestones": [
            {"milestone_id": "M1", "description": "The ritual machinery is exposed.", "character_references": ["char_healer"]},
            {"milestone_id": "M2", "description": "Competing factions force open conflict.", "character_references": ["char_regent"]},
        ],
        "core_conflict_question": "Can a society built on divine coercion survive truth?",
        "compass_notes": "Keep institutions under pressure.",
    }

    state = {
        "worker_request": {
            "task": "Use worldbuilding to construct foundational world architecture.",
            "context": {
                "skill": "worldbuilding",
                "endpoint_compass": endpoint_compass,
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
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"
    for required_key in (
        "political_power_map",
        "geography",
        "cultures_customs_religion",
        "history_and_legends",
        "magic_system",
        "location_connections",
        "kg_context_used",
    ):
        assert required_key in artifacts, f"Missing '{required_key}' in worldbuilding artifacts"
    assert isinstance(artifacts["magic_system"], dict), "magic_system must be an object"
    assert artifacts["magic_system"].get("node_type") == "MagicSystem"
    assert artifacts["kg_context_used"].get("targeted_expansion") is False
    assert isinstance(artifacts["location_connections"], list)
    if artifacts["location_connections"]:
        assert all(
            "from" in edge and "to" in edge for edge in artifacts["location_connections"]
        ), "location_connections must use from/to fields"


@pytest.mark.integration
def test_worldbuilding_targeted_expansion_uses_kg_context() -> None:
    add_kg_node.invoke(
        {
            "logical_id": "faction_sable_concord",
            "node_type": "Faction",
            "properties": {"name": "Sable Concord"},
            "chapter": 3,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "location_bastion",
            "node_type": "Location",
            "properties": {"name": "Basalt Bastion"},
            "chapter": 3,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "culture_tidemarked",
            "node_type": "Culture",
            "properties": {"name": "Tidemarked Houses"},
            "chapter": 3,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "magic_tithe",
            "node_type": "MagicSystem",
            "properties": {"prevalence": "Stable"},
            "chapter": 3,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "event_salt_uprising",
            "node_type": "Event",
            "properties": {"name": "Salt Uprising", "is_historical": True},
            "chapter": 2,
        }
    )

    config = NovelWriterConfig()
    subagent = PlanningSubagent(config)
    endpoint_compass = {
        "pass": 2,
        "starting_situation": "A coastal district becomes relevant after chapter 6.",
        "ending_destination": "The regime fractures across maritime provinces.",
        "milestones": [{"milestone_id": "M3", "description": "Maritime rebellion begins.", "character_references": []}],
        "core_conflict_question": "Who owns the sea routes under collapsing legitimacy?",
        "compass_notes": "Expand coastward institutions only.",
    }
    state = {
        "worker_request": {
            "task": "Use worldbuilding for targeted expansion of coastal region records.",
            "context": {
                "skill": "worldbuilding",
                "endpoint_compass": endpoint_compass,
                "expansion_scope": {"domains": ["geography", "political_power_map"]},
                "chapter_context": 6,
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
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"

    kg_context_used = artifacts.get("kg_context_used", {})
    assert kg_context_used.get("targeted_expansion") is True
    assert kg_context_used.get("factions_found", 0) >= 1
    assert kg_context_used.get("locations_found", 0) >= 1
    assert kg_context_used.get("cultures_found", 0) >= 1
    assert kg_context_used.get("magic_systems_found", 0) >= 1
    assert kg_context_used.get("historical_events_found", 0) >= 1