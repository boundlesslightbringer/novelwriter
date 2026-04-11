"""
Tests for resolution_subagent internal subgraph.

ANALYSE integration requires Vertex / Gemini (pytest -m integration).
IMPLEMENT execute path can be tested with a patched plan node (no LLM for plan).
"""

import os
import uuid
from typing import Any, Dict, Optional

import pytest

from src.agents.workers import ResolutionSubagent
from src.config import NovelWriterConfig
from src import resolution_subgraph as rs
from src.world_bible_tools import _get_db, add_kg_node, init_kg_db, query_kg_nodes


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


def test_invalid_mode_returns_failed() -> None:
    subagent = ResolutionSubagent(NovelWriterConfig())
    out = subagent.invoke(
        {
            "worker_request": {
                "task": "resolve",
                "context": {"mode": "UNKNOWN"},
            },
            "messages": [],
            "worker_history": [],
        }
    )
    result = out["latest_worker_result"]["result"]
    assert result["status"] == "failed"
    assert "error" in result["artifacts"]


@pytest.mark.integration
def test_analyse_mode_structured_output() -> None:
    subagent = ResolutionSubagent(NovelWriterConfig())
    out = subagent.invoke(
        {
            "worker_request": {
                "task": "Analyse contradiction",
                "context": {
                    "mode": "ANALYSE",
                    "contradiction_record": {
                        "contradiction_id": "cont_test_analyse_001",
                        "detected_at_chapter": 2,
                        "nature": "Knowledge",
                        "conflicting_records": ["char_a introduction", "char_a scene_3"],
                        "description": "The character is said both to know and not to know the treaty terms.",
                        "resolution_status": "Unresolved",
                        "resolution_notes": "",
                    },
                    "blocked_write": {
                        "write_type": "update_kg_node",
                        "proposed_payload": {"logical_id": "ki_treaty", "note": "mark as KNOWN"},
                    },
                    "prefetched_docs": [],
                },
            },
            "messages": [],
            "worker_history": [],
        }
    )
    result = out["latest_worker_result"]["result"]
    if result["status"] != "success":
        pytest.fail(f"ANALYSE failed: {result}")

    art = result["artifacts"]
    assert art.get("mode") == "ANALYSE"
    assert art.get("briefing")
    opts = art.get("resolution_options") or []
    assert 2 <= len(opts) <= 4
    assert art.get("recommended_option")
    # No writes on ANALYSE
    docs = query_kg_nodes.invoke({"query": {"type": "Contradiction"}})
    assert docs == []


def test_implement_mode_updates_contradiction_with_patched_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    cont_id = f"cont_test_impl_{suffix}"
    add_kg_node.invoke(
        {
            "logical_id": cont_id,
            "node_type": "Contradiction",
            "properties": {
                "nature": "Physical",
                "description": "Height mismatch",
                "detected_at_chapter": 1,
                "resolution_status": "Unresolved",
                "resolution_notes": "",
            },
            "chapter": 1,
        }
    )

    def fake_plan(
        subagent: Any, state: Dict[str, Any], config: Optional[Any] = None
    ) -> Dict[str, Any]:
        return {
            "implement_plan": {
                "reasoning": "test patch",
                "skip_story_writes": True,
                "resolution_type": "Accepted as intentional ambiguity",
                "contradiction_logical_id": cont_id,
                "contradiction_properties_patch": {
                    "resolution_status": "Accepted as intentional ambiguity",
                    "resolution_notes": "User accepted intentional ambiguity for height.",
                },
                "additional_node_updates": [],
            }
        }

    monkeypatch.setattr(rs, "_implement_plan_node", fake_plan)

    subagent = ResolutionSubagent(NovelWriterConfig())
    out = subagent.invoke(
        {
            "worker_request": {
                "task": "Implement resolution",
                "context": {
                    "mode": "IMPLEMENT",
                    "chapter": 1,
                    "contradiction_record": {
                        "contradiction_id": cont_id,
                        "detected_at_chapter": 1,
                    },
                    "blocked_write": {
                        "write_type": "add_kg_node",
                        "proposed_payload": {},
                    },
                    "user_decision": {
                        "chosen_option_id": "A",
                        "accepted_as_intentional": True,
                    },
                },
            },
            "messages": [],
            "worker_history": [],
        }
    )
    result = out["latest_worker_result"]["result"]
    assert result["status"] == "success", result
    rr = result["artifacts"].get("resolution_result") or {}
    assert rr.get("status") == "RESOLVED"
    assert rr.get("re_issue_signal", {}).get("action") == "RE_ISSUE_BLOCKED_WRITE"

    rows = query_kg_nodes.invoke({"query": {"logical_id": cont_id}})
    assert len(rows) >= 1
    active = [r for r in rows if r.get("valid_to") is None]
    assert len(active) == 1
    props = active[0].get("properties") or {}
    assert props.get("resolution_status") == "Accepted as intentional ambiguity"
    assert props.get("resolution_notes")
