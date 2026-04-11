from unittest.mock import MagicMock

import pytest
from langchain_core.messages import HumanMessage

from src.brain import BrainNode
from src.config import NovelWriterConfig
from src.state import BrainDecision, BrainDecisionFallback, QualityVerdict


@pytest.fixture
def config():
    return NovelWriterConfig(max_brain_iterations=15, max_rejection_budget=2)


@pytest.fixture
def brain_node(config):
    return BrainNode(config)


@pytest.fixture
def initial_state():
    return {
        "messages": [HumanMessage(content="start a new novel")],
        "iteration_count": 0,
        "rejection_count": 0,
        "final_response": None,
        "active_worker": None,
        "worker_request": None,
        "latest_worker_result": None,
        "worker_history": [],
    }


def _mock_llm_decision(brain_node: BrainNode, decision: BrainDecision) -> None:
    mock_llm = MagicMock()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = decision
    mock_llm.with_structured_output.return_value = mock_chain
    brain_node.llm = mock_llm


def test_normal_delegate_routing(brain_node, initial_state):
    decision = BrainDecision(
        reasoning="Start bootstrap.",
        action="delegate",
        worker="planning_subagent",
        task="Find a seed for this novel.",
        context={"skill": "finding-a-seed", "genre": "high fantasy"},
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(initial_state)

    assert updates["iteration_count"] == 1
    assert updates["final_response"] is None
    assert updates["active_worker"] == "planning_subagent"
    assert updates["worker_request"]["task"] == "Find a seed for this novel."
    assert updates["worker_request"]["context"]["genre"] == "high fantasy"


def test_invalid_delegate_contract_escalates_clarify(brain_node, initial_state):
    decision = BrainDecision(
        reasoning="Do something next.",
        action="delegate",
        worker=None,
        task="",
        context={},
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(initial_state)

    assert updates["active_worker"] is None
    assert "Which part should I work on next" in updates["final_response"]


def test_missing_quality_assessment_rejects_by_default(brain_node, initial_state):
    state = initial_state.copy()
    state["latest_worker_result"] = {
        "worker": "planning_subagent",
        "task": "Find a seed",
        "context": {"skill": "finding-a-seed"},
        "result": {
            "status": "success",
            "summary": "Generated seed.",
            "artifacts": {"seed_document": {"seed": "A fallen empire and contested heir."}},
        },
    }
    decision = BrainDecision(
        reasoning="Persist to story state.",
        action="delegate",
        worker="story_state_manager",
        task="Persist accepted records to story state",
        context={},
        quality_assessment=None,
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(state)

    assert updates["active_worker"] == "planning_subagent"
    assert "Retry requirement" in updates["worker_request"]["task"]
    assert updates["rejection_count"] == 1


def test_reject_budget_exhaustion_escalates_clarify(brain_node, initial_state):
    state = initial_state.copy()
    state["rejection_count"] = 2
    state["latest_worker_result"] = {
        "worker": "planning_subagent",
        "task": "Find a seed",
        "context": {"skill": "finding-a-seed"},
        "result": {
            "status": "success",
            "summary": "Generated seed.",
            "artifacts": {"seed_document": {"seed": "A brittle peace before civil war."}},
        },
    }
    decision = BrainDecision(
        reasoning="Proceed.",
        action="delegate",
        worker="story_state_manager",
        task="Persist accepted records to story state",
        context={},
        quality_assessment=None,
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(state)

    assert updates["active_worker"] is None
    assert "cannot validate the latest worker output" in updates["final_response"]


def test_accept_routes_to_story_state_manager_with_payload(brain_node, initial_state):
    state = initial_state.copy()
    state["latest_worker_result"] = {
        "worker": "planning_subagent",
        "task": "Find a seed",
        "context": {"skill": "finding-a-seed", "chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Generated seed.",
            "artifacts": {
                "seed_document": {"seed": "A kingdom fractured by inheritance law."},
                "plot_thread_seeds": [
                    {
                        "logical_id": "thread_claim_throne",
                        "node_type": "PlotThread",
                        "properties": {"name": "Claim the throne"},
                    }
                ],
            },
        },
    }
    decision = BrainDecision(
        reasoning="Looks good.",
        action="respond",
        response="Proceeding.",
        quality_assessment=QualityVerdict(verdict="accept", reason="Artifacts are complete."),
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(state)

    assert updates["active_worker"] == "story_state_manager"
    assert updates["worker_request"]["task"] == "Persist accepted records to story state"
    context = updates["worker_request"]["context"]
    assert context["chapter_context"] == 1
    assert len(context["nodes_to_add"]) >= 1


def test_story_state_manager_blocked_routes_to_resolution(brain_node, initial_state):
    state = initial_state.copy()
    state["latest_worker_result"] = {
        "worker": "story_state_manager",
        "task": "Persist accepted records to story state",
        "context": {
            "chapter_context": 4,
            "nodes_to_update": [
                {"logical_id": "char_missing", "updated_properties": {"name": "Ghost"}},
            ],
        },
        "result": {
            "status": "blocked",
            "summary": "Write blocked due to KG contradictions.",
            "artifacts": {
                "operation": "write",
                "status": "blocked",
                "contradiction_record": {
                    "has_contradictions": True,
                    "contradictions": ["Cannot update node 'char_missing': no active node found."],
                },
            },
        },
    }
    wrong = BrainDecision(
        reasoning="Incorrectly respond to user.",
        action="respond",
        response="Everything is fine.",
    )
    _mock_llm_decision(brain_node, wrong)

    updates = brain_node(state)

    assert updates["active_worker"] == "resolution_subagent"
    req = updates["worker_request"]
    assert req["task"] == "Analyse KG contradiction blocking persistence"
    assert req["context"]["mode"] == "ANALYSE"
    assert req["context"]["contradiction_record"]["has_contradictions"] is True


def test_resolution_analyse_success_forces_user_response(brain_node, initial_state):
    state = initial_state.copy()
    state["latest_worker_result"] = {
        "worker": "resolution_subagent",
        "task": "Analyse KG contradiction blocking persistence",
        "context": {"mode": "ANALYSE"},
        "result": {
            "status": "success",
            "summary": "Options prepared.",
            "artifacts": {
                "briefing": "Two canonical options exist to resolve this contradiction.",
                "resolution_options": [
                    {"option_id": "A", "label": "Retcon detail", "description": "Adjust historical note."},
                    {"option_id": "B", "label": "Accept ambiguity", "description": "Keep contradiction intentional."},
                ],
            },
        },
    }
    decision = BrainDecision(
        reasoning="Continue planning.",
        action="delegate",
        worker="planning_subagent",
        task="Continue planning",
        context={},
    )
    _mock_llm_decision(brain_node, decision)

    updates = brain_node(state)

    assert updates["active_worker"] is None
    assert "Two canonical options exist" in updates["final_response"]
    assert "A: Retcon detail" in updates["final_response"]


def test_iteration_limit(brain_node, initial_state):
    state = initial_state.copy()
    state["iteration_count"] = 15

    updates = brain_node(state)

    assert "Iteration limit reached" in updates["final_response"]
    assert updates["active_worker"] is None


def test_nested_model_fallback(brain_node, initial_state):
    fallback_decision = BrainDecisionFallback(
        reasoning="Fallback reasoning.",
        action="respond",
        response="Fallback response.",
        quality_verdict="accept",
        quality_reason="Looks acceptable.",
    )

    mock_llm = MagicMock()
    primary = MagicMock()
    primary.invoke.side_effect = Exception("Nested model parsing failed")
    fallback = MagicMock()
    fallback.invoke.return_value = fallback_decision
    mock_llm.with_structured_output.side_effect = [primary, fallback]
    brain_node.llm = mock_llm

    updates = brain_node(initial_state)

    assert updates["final_response"] == "Fallback response."
    assert updates["active_worker"] is None


def test_mvp_mode_kickoff_routes_to_planning(brain_node, initial_state):
    state = initial_state.copy()
    state["messages"] = [HumanMessage(content="genre: fantasy\nthemes: honor, betrayal")]
    state["mvp_mode"] = True
    state["mvp_requirements"] = {
        "genre": "fantasy",
        "themes": ["honor", "betrayal"],
        "chapter_context": 1,
        "max_major_characters": 5,
        "target_scene_pages": "1-2",
    }
    brain_node.llm = MagicMock()

    updates = brain_node(state)

    assert updates["active_worker"] == "planning_subagent"
    assert updates["worker_request"]["context"]["skill"] == "finding-a-seed"
    brain_node.llm.with_structured_output.assert_not_called()


def test_mvp_mode_advances_planning_to_character(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {"genre": "fantasy", "themes": ["loyalty"], "chapter_context": 1}
    state["latest_worker_result"] = {
        "worker": "planning_subagent",
        "task": "Run finding-a-seed",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Seed complete.",
            "artifacts": {},
        },
    }

    updates = brain_node(state)

    assert updates["active_worker"] == "character_subagent"
    assert updates["worker_request"]["context"]["skill"] == "character-creation"
    concept = updates["worker_request"]["context"]["character_concept"]
    assert isinstance(concept, dict)
    assert concept.get("genre") == "fantasy"
    assert concept.get("themes") == ["loyalty"]
    assert str(concept.get("mvp_brief") or "").strip()


def test_mvp_mode_character_concept_user_brief_merges_into_context(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {
        "genre": "fantasy",
        "themes": ["loyalty"],
        "chapter_context": 1,
        "character_concept": "Focus on a disgraced chaplain as the moral center.",
    }
    planning_record = {
        "worker": "planning_subagent",
        "task": "Run finding-a-seed",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Seed complete.",
            "artifacts": {},
        },
    }
    persistence_record = {
        "worker": "story_state_manager",
        "task": "Persist accepted records to story state",
        "context": {"chapter_context": 1},
        "result": {"status": "success", "summary": "Persisted planning outputs.", "artifacts": {}},
    }
    state["worker_history"] = [planning_record, persistence_record]
    state["latest_worker_result"] = persistence_record

    updates = brain_node(state)

    assert updates["active_worker"] == "character_subagent"
    concept = updates["worker_request"]["context"]["character_concept"]
    assert concept.get("user_brief") == "Focus on a disgraced chaplain as the moral center."
    assert "User direction (highest priority)" in str(concept.get("mvp_brief") or "")


def test_mvp_mode_plotting_includes_gardener_required_context(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {
        "genre": "fantasy",
        "themes": ["loyalty"],
        "chapter_context": 1,
        "pov_character_id": "char_hero_01",
    }
    state["latest_worker_result"] = {
        "worker": "character_subagent",
        "task": "Run character-creation",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Characters ready.",
            "artifacts": {},
        },
    }

    updates = brain_node(state)

    assert updates["active_worker"] == "plotting_subagent"
    ctx = updates["worker_request"]["context"]
    assert ctx["skill"] == "gardener-plotting-system"
    assert ctx["pov_character_id"] == "char_hero_01"
    assert "Cold open" in ctx["last_scene_outcome"]


def test_mvp_mode_writing_uses_scene_construction_with_scene_parameters(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {"genre": "fantasy", "themes": ["loyalty"], "chapter_context": 1}

    character_record = {
        "worker": "character_subagent",
        "task": "Run character-creation",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Characters ready.",
            "artifacts": {
                "character_node": {"logical_id": "char_hero_01", "node_type": "Character", "properties": {"name": "Hero"}},
            },
        },
    }
    plotting_record = {
        "worker": "plotting_subagent",
        "task": "Run gardener plotting",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Scene parameters ready.",
            "artifacts": {
                "scene_parameters": {
                    "pov_character_id": "char_hero_01",
                    "scene_goal": "Survive the first night under new divine law.",
                }
            },
        },
    }
    state["worker_history"] = [character_record, plotting_record]
    state["latest_worker_result"] = plotting_record

    updates = brain_node(state)

    assert updates["active_worker"] == "writing_subagent"
    ctx = updates["worker_request"]["context"]
    assert ctx["skill"] == "scene-construction"
    assert ctx["operation"] == "scene-construction"
    assert ctx["pov_character_id"] == "char_hero_01"
    assert "MVP request" in str(ctx.get("problem_description") or "")
    assert ctx["scene_parameters"]["scene_goal"] == "Survive the first night under new divine law."


def test_mvp_mode_enforces_character_cap(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {
        "genre": "fantasy",
        "themes": ["ambition"],
        "chapter_context": 1,
        "max_major_characters": 5,
    }
    state["latest_worker_result"] = {
        "worker": "character_subagent",
        "task": "Run character-creation",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Created character cast.",
            "artifacts": {"major_characters": [{}, {}, {}, {}, {}, {}]},
        },
    }

    updates = brain_node(state)

    assert updates["active_worker"] is None
    assert "exceeded the cap of 5" in updates["final_response"]


def test_mvp_mode_writing_success_returns_scene_text(brain_node, initial_state):
    state = initial_state.copy()
    state["mvp_mode"] = True
    state["mvp_requirements"] = {"genre": "fantasy", "themes": ["loss"], "chapter_context": 1}
    state["latest_worker_result"] = {
        "worker": "writing_subagent",
        "task": "Write chapter opening scene",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Scene drafted.",
            "artifacts": {"scene_text": "The bells rang once as winter rain hit the battlements."},
        },
    }

    updates = brain_node(state)

    assert updates["active_worker"] is None
    assert "winter rain hit the battlements" in updates["final_response"]
