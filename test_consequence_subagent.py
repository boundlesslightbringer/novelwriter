"""
Consequence subagent integration tests for Group 5 skills.

**Primary gate (live Vertex / Gemini + MongoDB fixture):**

  uv run pytest test_consequence_subagent.py -s -v -m integration

**Fast local check (no LLM — validates required-context handling only):**

  uv run pytest test_consequence_subagent.py -q -m "not integration"

Integration tests intentionally do not mock the model; they validate the real
internal subgraph/chain paths used before full novelwriter end-to-end wiring.
"""

import json
import os
import re

import pytest

from src.agents.workers import ConsequenceSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, add_kg_edge, add_kg_node, init_kg_db

_DETONATION_CHAPTER_ANCHOR = re.compile(r"\bch(?:apter)?\.?\s*\d", re.IGNORECASE)


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    add_kg_node.invoke(
        {
            "logical_id": "char_lyra",
            "node_type": "Character",
            "properties": {
                "full_name": "Lyra Venn",
                "core_desire": "Protect her brother's claim",
                "emotional_state": "guarded",
                "active_fears": ["public disgrace"],
            },
            "chapter": 6,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "char_cael",
            "node_type": "Character",
            "properties": {
                "full_name": "Cael Venn",
                "core_desire": "Survive the council hearing",
                "emotional_state": "cornered",
                "active_fears": ["execution"],
            },
            "chapter": 6,
        }
    )

    add_kg_edge.invoke(
        {
            "logical_id": "rel_lyra_cael",
            "edge_type": "RELATIONSHIP",
            "from_node": "char_lyra",
            "to_node": "char_cael",
            "properties": {
                "relationship_type": "siblings",
                "emotional_valence": "strained",
                "trajectory": "Volatile",
            },
            "chapter": 6,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "cc_council_pressure",
            "node_type": "CascadeChain",
            "properties": {
                "sequence": [
                    "Forgery rumor leaks",
                    "Council summons both siblings",
                    "Public denunciation",
                ],
                "current_position": "Council summons both siblings",
                "remaining_links": ["Public denunciation"],
            },
            "chapter": 6,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "bomb_old_pending",
            "node_type": "Payoff",
            "properties": {
                "type": "Consequence bomb",
                "description": "A prior debt will be called in.",
                "planted_in_chapter": 3,
                "detonation_trigger": "When Lyra asks the smugglers for passage.",
                "narrative_phase_anchor": "mid",
                "resolution_status": "Pending",
                "priority_tier": "Enriching",
                "dual_register": False,
            },
            "chapter": 3,
        }
    )

    add_kg_node.invoke(
        {
            "logical_id": "magic_system_core",
            "node_type": "MagicSystem",
            "properties": {
                "prevalence": "Rare",
                "confirmed_capabilities": ["warding", "oath-bond tracing"],
                "confirmed_limits": ["requires blood relation for oath-bond tracing"],
                "confirmed_costs": ["fatigue", "nosebleeds"],
                "recent_magical_events": ["A ward flare at the south gate."],
            },
            "chapter": 6,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "faction_regency_council",
            "node_type": "Faction",
            "properties": {
                "name": "Regency Council",
                "resources": ["city guard", "treasury control"],
            },
            "chapter": 6,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "loc_high_council_hall",
            "node_type": "Location",
            "properties": {
                "name": "High Council Hall",
                "security_level": "High",
            },
            "chapter": 6,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "culture_valen",
            "node_type": "Culture",
            "properties": {
                "name": "Valen Court Culture",
                "tone_register": "low fantasy, high political realism, earned darkness",
            },
            "chapter": 6,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "chapter_6",
            "node_type": "Chapter",
            "properties": {
                "chapter_number": 6,
                "summary": "Lyra and Cael prepare for the hearing while old wards are reinforced.",
            },
            "chapter": 6,
        }
    )

    yield


def test_consequence_cascade_missing_context_returns_need_input() -> None:
    """No LLM: subgraph ingest should reject incomplete brain context."""
    subagent = ConsequenceSubagent(NovelWriterConfig())
    state = {
        "worker_request": {
            "task": "Run consequence-cascade-implementation.",
            "context": {
                "skill": "consequence-cascade-implementation",
                "chapter_context": 7,
            },
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    structured = result["latest_worker_result"]["result"]
    artifacts = structured.get("artifacts", {})
    assert structured.get("status") == "need_input"
    assert artifacts.get("error") == "missing_required_context"
    assert "triggering_event" in artifacts.get("missing_fields", [])
    assert "affected_character_ids" in artifacts.get("missing_fields", [])


def test_balancing_realism_missing_context_returns_need_input() -> None:
    """No LLM: chain should reject missing draft and invalid scope."""
    subagent = ConsequenceSubagent(NovelWriterConfig())
    state = {
        "worker_request": {
            "task": "Run balancing-realism-and-fantasy audit.",
            "context": {
                "skill": "balancing-realism-and-fantasy",
                "chapter_context": 7,
                "audit_scope": "unknown_scope",
            },
        },
        "messages": [],
        "worker_history": [],
    }

    result = subagent.invoke(state)
    structured = result["latest_worker_result"]["result"]
    artifacts = structured.get("artifacts", {})
    assert structured.get("status") == "need_input"
    assert artifacts.get("error") == "missing_required_context"
    assert "chapter_or_scene_draft" in artifacts.get("missing_fields", [])
    assert "audit_scope" in artifacts.get("missing_fields", [])


@pytest.mark.integration
def test_consequence_cascade_live_vertex_integration() -> None:
    """Full subgraph: real skill load, KG prefetch, and multi-step structured Gemini calls."""
    subagent = ConsequenceSubagent(NovelWriterConfig())

    # Avoid "Ch. 7" / "chapter 7" style substrings in the triggering text so we do not
    # accidentally fail subgraph validation if the model echoes phrasing into triggers.
    state = {
        "worker_request": {
            "task": "Use consequence-cascade-implementation for the public denouncement event.",
            "context": {
                "skill": "consequence-cascade-implementation",
                "triggering_event": (
                    "At the scheduled council hearing, Lyra is publicly denounced as a traitor "
                    "and Cael is threatened with execution unless he confesses to forging seals."
                ),
                "chapter_context": 7,
                "affected_character_ids": ["char_lyra", "char_cael"],
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== ConsequenceSubagent: consequence-cascade-implementation (live integration) ===")
    result = subagent.invoke(state)

    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"
    structured = latest_result.get("result", {})
    status = structured.get("status")
    artifacts = structured.get("artifacts", {})

    print(f"\nWorker status: {status}")
    if status != "success":
        print(f"Failure detail: {json.dumps(artifacts, indent=2, default=str)}")
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"

    print("\n=== Artifacts (truncated) ===")
    print(json.dumps(artifacts, indent=2, default=str)[:12000])

    required_keys = (
        "triggering_event_summary",
        "cascade_chain",
        "consequence_chain_entry",
        "consequence_bombs",
        "character_state_updates",
        "relationship_updates",
        "knowledge_matrix_updates",
        "kg_context_used",
    )
    for key in required_keys:
        assert key in artifacts, f"Missing '{key}' in artifacts"

    # Skill contract: cascade_chain and consequence_chain_entry are objects, not lists.
    assert isinstance(artifacts["cascade_chain"], dict), "cascade_chain must be an object"
    assert isinstance(artifacts["consequence_chain_entry"], dict), "consequence_chain_entry must be an object"
    assert artifacts["consequence_chain_entry"].get("node_type") == "CascadeChain"
    ec_root = artifacts["consequence_chain_entry"].get("event_consequences")
    assert isinstance(ec_root, dict), "consequence_chain_entry.event_consequences must be an object"
    for bucket in ("immediate", "short_term", "long_term_pending"):
        assert isinstance(ec_root.get(bucket), list), f"event_consequences.{bucket} must be a list"

    for list_key in ("consequence_bombs", "character_state_updates", "relationship_updates", "knowledge_matrix_updates"):
        assert artifacts[list_key] is not None, f"{list_key} must not be null"
        assert isinstance(artifacts[list_key], list), f"{list_key} must be a list"

    assert isinstance(artifacts["kg_context_used"], dict), "kg_context_used must be an object"

    cascade = artifacts["cascade_chain"]
    assert cascade.get("action") in {"create_new", "extend_existing"}
    if cascade["action"] == "create_new":
        node = cascade.get("node") or {}
        assert node.get("node_type") == "CascadeChain"
        assert node.get("logical_id"), "create_new cascade must propose a CascadeChain logical_id"
        props = node.get("properties") or {}
        assert isinstance(props.get("sequence"), list) and len(props["sequence"]) >= 1
    else:
        assert (cascade.get("existing_chain_id") or "").strip(), "extend_existing requires existing_chain_id"
        upd = cascade.get("update_existing") or {}
        assert (upd.get("logical_id") or "").strip(), "update_existing must name the chain logical_id"

    ec = artifacts["consequence_chain_entry"].get("event_consequences") or {}
    immediate = ec.get("immediate") or []
    short_term = ec.get("short_term") or []
    long_term = ec.get("long_term_pending") or []
    assert len(immediate) >= 1, "Expected at least one immediate consequence entry"
    assert len(short_term) >= 1, "Expected at least one short-term consequence entry"
    for bucket_name, bucket in (("immediate", immediate), ("short_term", short_term)):
        for i, row in enumerate(bucket):
            assert isinstance(row, dict), f"{bucket_name}[{i}] must be an object"
            assert (row.get("description") or "").strip(), f"{bucket_name}[{i}].description must be non-empty"
    if long_term:
        for i, row in enumerate(long_term):
            assert isinstance(row, dict), f"long_term_pending[{i}] must be an object"
            assert (row.get("description") or "").strip(), (
                f"long_term_pending[{i}].description must be non-empty when present"
            )

    bombs = artifacts["consequence_bombs"]
    assert len(bombs) >= 1, "Expected at least one consequence bomb (Payoff) record"
    allowed_tiers = {"Essential", "Enriching", "Unclassified"}
    allowed_phases = {"early", "mid", "convergence", "final act"}
    for i, bomb in enumerate(bombs):
        assert isinstance(bomb, dict), f"consequence_bombs[{i}] must be an object"
        props = bomb.get("properties") or {}
        trig = str(props.get("detonation_trigger", "") or "").strip()
        assert trig, f"consequence_bombs[{i}].properties.detonation_trigger must be non-empty"
        assert not _DETONATION_CHAPTER_ANCHOR.search(trig), (
            f"consequence_bombs[{i}]: detonation_trigger looks chapter-anchored: {trig!r}"
        )
        tier = props.get("priority_tier")
        assert tier in allowed_tiers, f"consequence_bombs[{i}]: invalid priority_tier {tier!r}"
        assert props.get("dual_register") is (tier == "Essential"), (
            f"consequence_bombs[{i}]: dual_register must be true iff Essential; got tier={tier!r} "
            f"dual_register={props.get('dual_register')!r}"
        )
        phase = props.get("narrative_phase_anchor")
        assert phase in allowed_phases, f"consequence_bombs[{i}]: invalid narrative_phase_anchor {phase!r}"

    kmu = artifacts["knowledge_matrix_updates"]
    assert len(kmu) >= 1, "Expected at least one knowledge_matrix_updates group"
    for i, group in enumerate(kmu):
        assert isinstance(group, dict), f"knowledge_matrix_updates[{i}] must be an object"
        assert (group.get("character_id") or "").strip(), f"knowledge_matrix_updates[{i}].character_id required"
        assert group.get("new_knows_edges") is not None
        assert group.get("new_knowledge_items") is not None
        assert isinstance(group["new_knows_edges"], list)
        assert isinstance(group["new_knowledge_items"], list)

    kg = artifacts["kg_context_used"]
    assert kg.get("character_nodes_found", 0) >= 2, "Fixture should yield both affected characters at ch.7"
    assert kg.get("relationship_edges_found", 0) >= 1
    assert kg.get("existing_cascade_chains_found", 0) >= 1
    assert kg.get("existing_pending_bombs_found", 0) >= 1
    assert kg.get("chain_action") in {"create_new", "extend_existing"}

    print("\n=== Live integration gate passed ===\n")


@pytest.mark.integration
def test_balancing_realism_and_fantasy_live_vertex_integration() -> None:
    """Full chain: real skill load, KG prefetch, draft signal pass, and five-dimension audit."""
    subagent = ConsequenceSubagent(NovelWriterConfig())
    draft = (
        "The regency council orders a midnight arrest of Cael without presenting any sworn witness. "
        "Lyra invokes an old warding rite in the hall, and the sigils flare for only a heartbeat, "
        "leaving her light-headed and bleeding from the nose. A guard captain is stabbed in the chaos. "
        "The aftermath lingers as Lyra cannot steady her hands while negotiating passage with a rival faction."
    )
    state = {
        "worker_request": {
            "task": "Run balancing-realism-and-fantasy on the completed chapter draft.",
            "context": {
                "skill": "balancing-realism-and-fantasy",
                "chapter_or_scene_draft": draft,
                "chapter_context": 7,
                "audit_scope": "full_chapter",
                "tone_reference": "low fantasy, high political realism, earned darkness",
                "pov_character_id": "char_lyra",
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== ConsequenceSubagent: balancing-realism-and-fantasy (live integration) ===")
    result = subagent.invoke(state)

    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"
    structured = latest_result.get("result", {})
    status = structured.get("status")
    artifacts = structured.get("artifacts", {})

    print(f"\nWorker status: {status}")
    if status != "success":
        print(f"Failure detail: {json.dumps(artifacts, indent=2, default=str)}")
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"

    print("\n=== Artifacts (truncated) ===")
    print(json.dumps(artifacts, indent=2, default=str)[:12000])

    required = (
        "audit_header",
        "dimension_reports",
        "priority_summary",
        "magic_system_updates_recommended",
        "kg_context_used",
    )
    for key in required:
        assert key in artifacts, f"Missing '{key}' in artifacts"

    header = artifacts["audit_header"]
    assert header.get("chapter_context") == 7
    assert header.get("audit_scope") == "full_chapter"
    assert header.get("pov_character_audited") == "char_lyra"

    reports = artifacts["dimension_reports"]
    expected_dims = (
        "political_realism",
        "magic_prevalence_and_consistency",
        "violence_framing",
        "dark_content_justification",
        "tonal_consistency",
    )
    for dim_key in expected_dims:
        assert dim_key in reports, f"Missing dimension report '{dim_key}'"
        report = reports[dim_key]
        assert isinstance(report, dict), f"{dim_key} must be an object"
        assert isinstance(report.get("flagged_passages"), list), f"{dim_key}.flagged_passages must be a list"
        for i, passage in enumerate(report["flagged_passages"]):
            assert isinstance(passage, dict), f"{dim_key}.flagged_passages[{i}] must be an object"
            assert (passage.get("text_reference") or "").strip()
            assert (passage.get("issue_description") or "").strip()
            assert (passage.get("recommended_adjustment") or "").strip()

    allowed_dimension_status = {"Pass", "Flag", "Concern"}
    for dim_key in (
        "political_realism",
        "violence_framing",
        "dark_content_justification",
        "tonal_consistency",
    ):
        assert reports[dim_key].get("status") in allowed_dimension_status

    magic_report = reports["magic_prevalence_and_consistency"]
    assert magic_report.get("status") in {"Pass", "Flag", "Concern", "Not applicable"}
    assert isinstance(magic_report.get("magic_acts_in_chapter"), int)
    assert magic_report.get("current_prevalence_level") in {
        "Rare",
        "Increasing",
        "Decreasing",
        "Stable",
        "Not applicable",
    }

    priority_summary = artifacts["priority_summary"]
    assert isinstance(priority_summary.get("high"), list)
    assert isinstance(priority_summary.get("medium"), list)
    assert isinstance(priority_summary.get("low"), list)

    updates = artifacts["magic_system_updates_recommended"]
    assert isinstance(updates, list), "magic_system_updates_recommended must be a list"
    for i, update in enumerate(updates):
        assert isinstance(update, dict), f"magic_system_updates_recommended[{i}] must be an object"
        assert update.get("update_type") in {
            "add_confirmed_capability",
            "add_confirmed_limit",
            "add_unexplained_phenomenon",
        }
        assert (update.get("description") or "").strip()
        assert (update.get("justification") or "").strip()

    kg_context = artifacts["kg_context_used"]
    assert isinstance(kg_context, dict)
    assert kg_context.get("faction_nodes_found", 0) >= 1
    assert kg_context.get("location_nodes_found", 0) >= 1
    assert kg_context.get("culture_nodes_found", 0) >= 1
    assert kg_context.get("pov_character_found") is True

    print("\n=== Live realism integration gate passed ===\n")
