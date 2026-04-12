"""Unit tests for Pass 2 rough-endpoints artifact assembly (no LLM)."""

from src.planning_rough_endpoints_subgraph import _assemble_pass2_artifacts


def test_assemble_pass2_empty_seeds_get_fallbacks_and_warnings() -> None:
    compass = {
        "prologue_specification": {"warranted": False},
        "starting_situation": "Start",
        "ending_destination": "End",
        "milestones": [
            {
                "milestone_id": "M1",
                "description": "First beat",
                "character_references": ["char_a"],
            }
        ],
        "core_conflict_question": "Will it hold?",
        "compass_notes": "Notes",
    }
    artifacts, warnings = _assemble_pass2_artifacts(compass, [], [])
    assert artifacts["pass"] == 2
    assert len(artifacts["plot_thread_seeds"]) == 1
    assert artifacts["plot_thread_seeds"][0]["node_type"] == "PlotThread"
    assert str(artifacts["plot_thread_seeds"][0]["properties"].get("name") or "").strip()
    assert len(artifacts["payoff_seeds"]) == 1
    assert artifacts["payoff_seeds"][0]["node_type"] == "Payoff"
    assert str(artifacts["payoff_seeds"][0]["properties"].get("description") or "").strip()
    assert any("plot_thread_seeds" in w for w in warnings)
    assert any("payoff_seeds" in w for w in warnings)


def test_assemble_pass2_empty_milestones_get_placeholder() -> None:
    compass = {
        "prologue_specification": {},
        "starting_situation": "",
        "ending_destination": "",
        "milestones": [],
        "core_conflict_question": "",
        "compass_notes": "",
    }
    artifacts, warnings = _assemble_pass2_artifacts(compass, [], [])
    assert len(artifacts["milestones"]) == 1
    assert artifacts["milestones"][0]["milestone_id"] == "M1"
    assert any("milestone" in w.lower() for w in warnings)


def test_assemble_pass2_missing_compass_warns() -> None:
    artifacts, warnings = _assemble_pass2_artifacts(None, [], [])
    assert artifacts["pass"] == 2
    assert any("pass_2_compass" in w for w in warnings)
    assert artifacts["milestones"][0]["milestone_id"] == "M1"


def test_assemble_pass2_preserves_provided_seeds() -> None:
    compass = {
        "milestones": [{"milestone_id": "M1", "description": "X", "character_references": []}],
    }
    plot = [
        {
            "node_type": "PlotThread",
            "properties": {"name": "Thread A", "status": "Active", "originating_chapter": 1},
        }
    ]
    payoff = [
        {
            "node_type": "Payoff",
            "properties": {
                "type": "Reveal",
                "description": "Payoff text",
                "planted_in_chapter": 1,
                "resolution_status": "Pending",
            },
        }
    ]
    artifacts, warnings = _assemble_pass2_artifacts(compass, plot, payoff)
    assert artifacts["plot_thread_seeds"] == plot
    assert artifacts["payoff_seeds"] == payoff
    assert not any("empty plot_thread" in w for w in warnings)
    assert not any("empty payoff" in w for w in warnings)
