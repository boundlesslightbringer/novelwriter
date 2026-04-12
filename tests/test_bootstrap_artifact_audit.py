"""Tests for bootstrap artifact validators and trace helpers."""

import json
from pathlib import Path

import pytest

from src.bootstrap_artifact_audit import (
    audit_worker_artifacts,
    validate_character_conception_artifacts,
    validate_character_creation_artifacts,
    validate_defining_rough_endpoints_pass2,
    validate_finding_a_seed_artifacts,
)
from src.bootstrap_trace import append_ssm_worker_trace, fingerprint_logical_ids, trace_path


def test_validate_seed_minimal_ok() -> None:
    artifacts = {
        "seed_document": {
            "seed": "A crown shatters in silence.",
            "generation_method": "Vivid Image",
            "validation_record": {
                "concreteness": "PASS — concrete image.",
                "generative_tension": "PASS — tension clear.",
                "emotional_necessity": "PASS — emotional stakes.",
                "open_architecture": "PASS — room to grow.",
            },
            "genre_theme_fit": "Fits genre.",
            "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"],
        },
        "candidate_seeds_log": [
            {
                "seed_statement": "Alt",
                "method": "What If?",
                "strengths": "x",
                "failure_point": "y",
                "status": "Rejected",
            }
        ],
        "genre": "High Fantasy",
        "themes": ["inheritance"],
    }
    assert validate_finding_a_seed_artifacts(artifacts) == []


def test_validate_seed_missing_validation_record() -> None:
    artifacts = {
        "seed_document": {"seed": "x", "generation_method": "m", "validation_record": None},
        "candidate_seeds_log": [{"seed_statement": "a", "method": "m", "strengths": "s", "failure_point": "f", "status": "Rejected"}],
        "genre": "Fantasy",
        "themes": ["t"],
    }
    errs = validate_finding_a_seed_artifacts(artifacts)
    assert any("validation_record" in e for e in errs)


def test_validate_pass2_threads_and_payoffs() -> None:
    art = {
        "pass": 2,
        "plot_thread_seeds": [
            {
                "node_type": "PlotThread",
                "properties": {"name": "Thread A", "status": "Active", "originating_chapter": 0},
            }
        ],
        "payoff_seeds": [
            {
                "node_type": "Payoff",
                "properties": {
                    "type": "Foreshadowing",
                    "description": "Early plant",
                    "planted_in_chapter": 0,
                    "resolution_status": "Pending",
                },
            }
        ],
    }
    assert validate_defining_rough_endpoints_pass2(art) == []


def test_character_concept_must_not_be_string() -> None:
    errs = validate_character_conception_artifacts({"character_concept": "just a string"})
    assert any("structured object" in e for e in errs)


def test_character_conception_ok() -> None:
    art = {
        "character_concept": {
            "assigned_narrative_role": "Heir",
            "generation_method": "role-first",
            "core_contradiction": "Duty vs desire",
            "sketch": "A paragraph long enough to qualify as a sketch for tests.",
            "open_questions": ["Q1", "Q2", "Q3"],
        },
        "provisional_flag": {"present": False, "world_context_assumptions": [], "most_likely_to_change": "", "key_information_needed": ""},
        "kg_context_used": {"factions_found": 0, "existing_characters_found": 0, "active_threads_found": 0, "notes": ""},
    }
    assert validate_character_conception_artifacts(art) == []


def test_character_creation_requires_voice_and_response_patterns() -> None:
    art = {
        "character_node": {
            "logical_id": "char_test",
            "node_type": "Character",
            "properties": {
                "full_name": "Test",
                "voice_profile": None,
                "response_patterns": None,
            },
        }
    }
    errs = validate_character_creation_artifacts(art)
    assert any("voice_profile" in e for e in errs)
    assert any("response_patterns" in e for e in errs)


def test_audit_worker_planning_worldbuilding_skill() -> None:
    art = {
        "political_power_map": [
            {
                "node_type": "Faction",
                "properties": {"name": "F1", "core_values": []},
                "iceberg_notes": {},
            }
        ],
        "geography": [
            {
                "node_type": "Location",
                "properties": {"name": "L1", "description": "", "climate": "", "seasonal_weather_state": ""},
                "iceberg_notes": {},
            }
        ],
        "cultures_customs_religion": [
            {
                "node_type": "Culture",
                "properties": {
                    "name": "C1",
                    "core_values": [],
                    "core_fears": [],
                    "key_customs": [],
                    "languages_dialects": [],
                },
                "iceberg_notes": {},
            }
        ],
        "history_and_legends": [
            {
                "node_type": "Event",
                "properties": {
                    "name": "E1",
                    "summary": "Past war",
                    "is_historical": True,
                },
            }
        ],
        "magic_system": {"node_type": "MagicSystem", "properties": {"name": "M1"}, "iceberg_notes": {}},
        "location_connections": [{"edge_type": "CONNECTED_TO", "from": "loc_a", "to": "loc_b", "properties": {}}],
    }
    ctx = {"skill": "worldbuilding"}
    assert audit_worker_artifacts("planning_subagent", art, ctx) == []


def test_fingerprint_logical_ids_stable() -> None:
    nodes = [{"logical_id": "b"}, {"logical_id": "a"}]
    assert fingerprint_logical_ids(nodes) == fingerprint_logical_ids([{"logical_id": "a"}, {"logical_id": "b"}])


def test_append_ssm_trace_only_when_env_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trace_file = tmp_path / "t.jsonl"
    monkeypatch.delenv("NOVELWRITER_BOOTSTRAP_TRACE", raising=False)
    append_ssm_worker_trace(
        "story_state_manager",
        {
            "latest_worker_result": {
                "task": "persist",
                "result": {"status": "success", "summary": "ok", "artifacts": {"records_updated": ["a"]}},
            }
        },
    )
    assert not trace_file.exists()

    monkeypatch.setenv("NOVELWRITER_BOOTSTRAP_TRACE", str(trace_file))
    assert trace_path() == str(trace_file)
    append_ssm_worker_trace(
        "story_state_manager",
        {
            "latest_worker_result": {
                "task": "persist",
                "result": {"status": "success", "summary": "ok", "artifacts": {"records_updated": ["n1"]}},
            }
        },
    )
    lines = trace_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["event"] == "story_state_manager_complete"
    assert row["result_status"] == "success"
