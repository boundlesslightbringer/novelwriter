"""Unit tests for deterministic bootstrap sequencing in BrainNode (no LLM)."""

from __future__ import annotations

from langchain_core.messages import HumanMessage

from src.brain import BrainNode
from src.config import NovelWriterConfig


def _bootstrap_state(
    *,
    messages: list,
    worker_history: list[dict],
    latest_worker_result: dict | None,
    iteration_count: int = 1,
) -> dict:
    return {
        "messages": messages,
        "worker_history": worker_history,
        "latest_worker_result": latest_worker_result,
        "iteration_count": iteration_count,
        "mvp_mode": False,
        "mvp_requirements": None,
        "rejection_count": 0,
        "final_response": None,
        "active_worker": None,
        "worker_request": None,
    }


def test_bootstrap_after_seed_persist_delegates_rough_pass1() -> None:
    brain = BrainNode(NovelWriterConfig())
    seed_planning = {
        "worker": "planning_subagent",
        "task": "Run finding-a-seed for novel bootstrap.",
        "context": {"skill": "finding-a-seed", "genre": "High Fantasy", "themes": ["legitimacy"]},
        "result": {
            "status": "success",
            "summary": "seed ok",
            "artifacts": {
                "seed_document": {
                    "seed": "A cartographer maps forbidden borders.",
                    "generation_method": "Character-First",
                    "validation_record": {},
                    "genre_theme_fit": "ok",
                    "questions": ["q1"],
                }
            },
        },
    }
    ssm = {
        "worker": "story_state_manager",
        "task": "Persist accepted records to story state",
        "context": {},
        "result": {"status": "success", "summary": "persisted", "artifacts": {}},
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[seed_planning, ssm],
        latest_worker_result=ssm,
        iteration_count=2,
    )
    decision = brain._bootstrap_progression_decision(state)
    assert decision is not None
    assert decision.action == "delegate"
    assert decision.worker == "planning_subagent"
    ctx = decision.context
    assert ctx.get("skill") == "defining-rough-endpoints"
    assert isinstance(ctx.get("seed_document"), dict)
    assert ctx["seed_document"].get("seed")


def test_bootstrap_after_pass1_delegates_first_slot_character() -> None:
    brain = BrainNode(NovelWriterConfig())
    pass1 = {
        "worker": "planning_subagent",
        "task": "Pass 1",
        "context": {"skill": "defining-rough-endpoints", "pass": "1"},
        "result": {
            "status": "success",
            "summary": "pass1",
            "artifacts": {
                "pass": 1,
                "starting_situation": "Sit A",
                "draft_ending_destination": "End B",
                "draft_core_conflict_question": "Conflict?",
                "compass_notes": "notes",
                "character_slot_sketches": [
                    {
                        "slot_id": "slot_a",
                        "narrative_role": "Lead",
                        "implied_contradiction": "x/y",
                        "stakes": "high",
                        "world_context": "kingdom",
                        "open_questions": ["oq1"],
                    }
                ],
                "draft_milestones": [{"milestone_id": "M1", "description": "d", "character_slots": ["slot_a"]}],
                "prologue_specification": {},
            },
        },
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass1],
        latest_worker_result=pass1,
        iteration_count=3,
    )
    decision = brain._bootstrap_progression_decision(state)
    assert decision is not None
    assert decision.worker == "character_subagent"
    assert decision.context.get("skill") == "character-conception"
    assert isinstance(decision.context.get("character_slot_sketch"), dict)
    assert decision.quality_assessment is not None
    assert decision.quality_assessment.verdict == "accept"


def test_bootstrap_after_pass2_persist_delegates_worldbuilding_with_compass() -> None:
    brain = BrainNode(NovelWriterConfig())
    pass2 = {
        "worker": "planning_subagent",
        "task": "Pass 2",
        "context": {"skill": "defining-rough-endpoints-pass-2"},
        "result": {
            "status": "success",
            "summary": "pass2",
            "artifacts": {
                "pass": 2,
                "starting_situation": "S",
                "ending_destination": "E",
                "milestones": [{"milestone_id": "M1", "description": "d", "character_references": []}],
                "core_conflict_question": "Q?",
                "compass_notes": "n",
                "prologue_specification": {},
                "plot_thread_seeds": [
                    {
                        "node_type": "PlotThread",
                        "properties": {"name": "T1", "status": "Active", "originating_chapter": 0},
                    }
                ],
                "payoff_seeds": [
                    {
                        "node_type": "Payoff",
                        "properties": {
                            "type": "Foreshadowing",
                            "description": "p",
                            "planted_in_chapter": 0,
                            "resolution_status": "Pending",
                        },
                    }
                ],
            },
        },
    }
    ssm = {
        "worker": "story_state_manager",
        "task": "Persist accepted records to story state",
        "context": {},
        "result": {"status": "success", "summary": "ok", "artifacts": {}},
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass2, ssm],
        latest_worker_result=ssm,
        iteration_count=5,
    )
    decision = brain._bootstrap_progression_decision(state)
    assert decision is not None
    assert decision.worker == "planning_subagent"
    assert decision.context.get("skill") == "worldbuilding"
    assert isinstance(decision.context.get("endpoint_compass"), dict)
    assert decision.context["endpoint_compass"].get("pass") == 2


def test_merge_worldbuilding_injects_endpoint_compass_from_pass2() -> None:
    brain = BrainNode(NovelWriterConfig())
    from src.state import BrainDecision, QualityVerdict

    pass2 = {
        "worker": "planning_subagent",
        "task": "Pass 2",
        "context": {},
        "result": {
            "status": "success",
            "artifacts": {
                "pass": 2,
                "starting_situation": "S",
                "ending_destination": "E",
                "milestones": [],
                "core_conflict_question": "Q",
                "compass_notes": "",
                "prologue_specification": {},
                "plot_thread_seeds": [{"node_type": "PlotThread", "properties": {"name": "T"}}],
                "payoff_seeds": [],
            },
        },
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass2],
        latest_worker_result=None,
        iteration_count=0,
    )
    decision = BrainDecision(
        reasoning="test",
        action="delegate",
        worker="planning_subagent",
        task="Run worldbuilding for the premise.",
        context={"skill": "worldbuilding"},
        quality_assessment=QualityVerdict(verdict="accept", reason="test"),
    )
    brain._merge_bootstrap_worldbuilding_compass(decision, state)
    assert isinstance(decision.context.get("endpoint_compass"), dict)


def test_bootstrap_after_all_early_slots_delegates_pass2() -> None:
    brain = BrainNode(NovelWriterConfig())
    pass1 = {
        "worker": "planning_subagent",
        "task": "Pass 1",
        "context": {"skill": "defining-rough-endpoints"},
        "result": {
            "status": "success",
            "summary": "p1",
            "artifacts": {
                "pass": 1,
                "starting_situation": "A",
                "draft_ending_destination": "B",
                "draft_core_conflict_question": "C",
                "compass_notes": "n",
                "character_slot_sketches": [
                    {
                        "slot_id": "s1",
                        "narrative_role": "R1",
                        "implied_contradiction": "c",
                        "stakes": "s",
                        "world_context": "w",
                        "open_questions": ["o"],
                    }
                ],
                "draft_milestones": [],
                "prologue_specification": {},
            },
        },
    }
    char = {
        "worker": "character_subagent",
        "task": "conceive",
        "context": {
            "skill": "character-conception",
            "character_slot_sketch": {"slot_id": "s1"},
        },
        "result": {
            "status": "success",
            "summary": "c1",
            "artifacts": {
                "character_concept": {
                    "assigned_narrative_role": "Hero",
                    "core_contradiction": "a/b",
                    "name": "Alex",
                }
            },
        },
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass1, char],
        latest_worker_result=char,
        iteration_count=4,
    )
    decision = brain._bootstrap_progression_decision(state)
    assert decision is not None
    assert decision.worker == "planning_subagent"
    assert decision.context.get("skill") == "defining-rough-endpoints-pass-2"
    assert isinstance(decision.context.get("pass_1_output"), dict)
    assert decision.context.get("character_concepts")


def test_bootstrap_after_pass2_success_delegates_persist_with_quality_accept() -> None:
    brain = BrainNode(NovelWriterConfig())
    pass2 = {
        "worker": "planning_subagent",
        "task": "Pass 2",
        "context": {"skill": "defining-rough-endpoints-pass-2"},
        "result": {
            "status": "success",
            "summary": "pass2",
            "artifacts": {
                "pass": 2,
                "starting_situation": "S",
                "ending_destination": "E",
                "milestones": [{"milestone_id": "M1", "description": "d", "character_references": []}],
                "core_conflict_question": "Q?",
                "compass_notes": "n",
                "prologue_specification": {},
                "plot_thread_seeds": [
                    {"node_type": "PlotThread", "properties": {"name": "T1", "status": "Active", "originating_chapter": 0}}
                ],
                "payoff_seeds": [
                    {
                        "node_type": "Payoff",
                        "properties": {
                            "type": "Foreshadowing",
                            "description": "p",
                            "planted_in_chapter": 0,
                            "resolution_status": "Pending",
                        },
                    }
                ],
            },
        },
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass2],
        latest_worker_result=pass2,
        iteration_count=6,
    )
    decision = brain._bootstrap_progression_decision(state)
    assert decision is not None
    assert decision.worker == "story_state_manager"
    assert decision.quality_assessment is not None
    assert decision.quality_assessment.verdict == "accept"


def test_need_input_worldbuilding_override_when_pass2_exists() -> None:
    brain = BrainNode(NovelWriterConfig())
    pass2 = {
        "worker": "planning_subagent",
        "task": "Pass 2",
        "context": {},
        "result": {"status": "success", "artifacts": {"pass": 2, "starting_situation": "S"}},
    }
    need = {
        "worker": "planning_subagent",
        "task": "worldbuild",
        "context": {"skill": "worldbuilding"},
        "result": {
            "status": "need_input",
            "summary": "Missing endpoint_compass",
            "artifacts": {
                "skill_attempted": "worldbuilding",
                "missing_fields": ["endpoint_compass"],
                "error": "missing_required_context",
            },
            "follow_up_questions": ["Provide compass"],
        },
    }
    state = _bootstrap_state(
        messages=[HumanMessage(content="genre: High Fantasy, themes: legitimacy")],
        worker_history=[pass2, need],
        latest_worker_result=need,
        iteration_count=4,
    )
    override = brain._bootstrap_planning_need_input_override(state)
    assert override is not None
    assert override.worker == "planning_subagent"
    assert override.context.get("skill") == "worldbuilding"
    assert isinstance(override.context.get("endpoint_compass"), dict)
