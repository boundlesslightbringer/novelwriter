import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

from src.config import NovelWriterConfig
from src.state import OrchestratorState, BrainDecision, BrainDecisionFallback, QualityVerdict
from src.brain import BrainNode
from src.orchestrator import STUB_CONFIG

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

def test_normal_routing(brain_node, initial_state):
    """Test that a user message like 'start a new novel' delegates to planning_subagent."""
    # Mock LLM to return a delegate decision
    mock_decision = BrainDecision(
        reasoning="User wants to start a novel.",
        action="delegate",
        worker="planning_subagent",
        task="Find a seed for the novel.",
        context={"genre": "dark fantasy"}
    )
    
    with patch.object(brain_node.llm, 'with_structured_output') as mock_structured_output:
        mock_invoke = MagicMock()
        mock_invoke.invoke.return_value = mock_decision
        mock_structured_output.return_value = mock_invoke
        
        updates = brain_node(initial_state)
        
        assert updates["iteration_count"] == 1
        assert updates["final_response"] is None
        assert updates["active_worker"] == "planning_subagent"
        assert updates["worker_request"]["task"] == "Find a seed for the novel."
        assert updates["worker_request"]["context"] == {"genre": "dark fantasy"}

def test_quality_gate_and_reject_budget(brain_node, initial_state):
    """Test that the brain rejects empty artifacts, re-delegates, and eventually responds."""
    # Set up state with a failed worker result
    state = initial_state.copy()
    state["latest_worker_result"] = {
        "worker": "planning_subagent",
        "task": "Find a seed",
        "context": {},
        "result": {
            "status": "success",
            "summary": "Done",
            "artifacts": {}  # Empty artifacts trigger reject
        }
    }
    
    # Mock LLM to return a decision (the quality gate logic in BrainNode will override the verdict)
    mock_decision = BrainDecision(
        reasoning="Worker finished.",
        action="delegate",
        worker="story_state_manager",
        quality_assessment=QualityVerdict(verdict="accept", reason="Looks good") # Even if LLM accepts, empty artifacts should force reject
    )
    
    with patch.object(brain_node.llm, 'with_structured_output') as mock_structured_output:
        mock_invoke = MagicMock()
        mock_invoke.invoke.return_value = mock_decision
        mock_structured_output.return_value = mock_invoke
        
        # Attempt 1: Should reject and re-delegate
        updates = brain_node(state)
        assert updates["active_worker"] == "planning_subagent"
        assert updates["final_response"] is None
        
        # Add to history to simulate the first rejection
        state["worker_history"].append(state["latest_worker_result"])
        state["rejection_count"] = updates["rejection_count"]
        
        # Attempt 2: Should reject and re-delegate
        updates = brain_node(state)
        assert updates["active_worker"] == "planning_subagent"
        assert updates["final_response"] is None
        
        # Add to history to simulate the second rejection
        state["worker_history"].append(state["latest_worker_result"])
        state["rejection_count"] = updates["rejection_count"]
        
        # Attempt 3: Should exceed reject budget and respond
        updates = brain_node(state)
        assert updates["active_worker"] is None
        assert "failed to complete task" in updates["final_response"]

def test_iteration_limit(brain_node, initial_state):
    """Test that exceeding max_brain_iterations triggers a respond action."""
    state = initial_state.copy()
    state["iteration_count"] = 15  # Max iterations
    
    updates = brain_node(state)
    
    assert "Iteration limit reached" in updates["final_response"]
    assert updates["active_worker"] is None

def test_nested_model_fallback(brain_node, initial_state):
    """Test that the fallback model is used if the primary model fails."""
    # Mock LLM to raise exception on first invoke, then succeed on fallback
    mock_fallback_decision = BrainDecisionFallback(
        reasoning="Fallback reasoning.",
        action="respond",
        response="Fallback response.",
        quality_verdict="accept",
        quality_reason="Fallback reason."
    )
    
    with patch.object(brain_node.llm, 'with_structured_output') as mock_structured_output:
        mock_invoke_primary = MagicMock()
        mock_invoke_primary.invoke.side_effect = Exception("Nested model parsing failed")
        
        mock_invoke_fallback = MagicMock()
        mock_invoke_fallback.invoke.return_value = mock_fallback_decision
        
        # Return primary mock first, then fallback mock
        mock_structured_output.side_effect = [mock_invoke_primary, mock_invoke_fallback]
        
        updates = brain_node(initial_state)
        
        assert updates["final_response"] == "Fallback response."
        assert updates["active_worker"] is None
