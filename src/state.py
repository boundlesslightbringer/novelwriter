import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


# Frozenset used by both the brain and the orchestrator router so the valid
# worker names are defined exactly once.
VALID_WORKERS: frozenset[str] = frozenset({
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
    "story_state_manager",
    "resolution_subagent",
})


class QualityVerdict(BaseModel):
    verdict: Literal["accept", "reject", "needs_clarification"]
    reason: str   # internal only; never shown to user


class BrainDecision(BaseModel):
    """Structured output schema for the orchestrator brain.

    The Literal constraint on `worker` guides the LLM to emit only valid
    worker identifiers and prevents silent routing errors.
    """

    reasoning: str
    action: Literal["delegate", "respond", "clarify"]
    worker: (
        Literal[
            "planning_subagent",
            "character_subagent",
            "plotting_subagent",
            "writing_subagent",
            "consequence_subagent",
            "story_state_manager",
            "resolution_subagent",
        ]
        | None
    ) = None
    task: str | None = None
    context: dict | None = None
    response: str | None = None
    quality_assessment: QualityVerdict | None = None


class BrainDecisionFallback(BaseModel):
    """Fallback schema for the orchestrator brain without nested models.
    
    Used when the primary LLM call fails to parse the nested QualityVerdict model.
    """

    reasoning: str
    action: Literal["delegate", "respond", "clarify"]
    worker: (
        Literal[
            "planning_subagent",
            "character_subagent",
            "plotting_subagent",
            "writing_subagent",
            "consequence_subagent",
            "story_state_manager",
            "resolution_subagent",
        ]
        | None
    ) = None
    task: str | None = None
    context: dict | None = None
    response: str | None = None
    quality_verdict: Literal["accept", "reject", "needs_clarification"] | None = None
    quality_reason: str | None = None


class OrchestratorState(TypedDict):
    """Full shared state threaded through every graph node.

    Reducer annotations:
      messages      — add_messages appends new messages; never overwrites history.
      worker_history — operator.add accumulates entries across all turns.

    All other fields are plain-assignment (last write wins).  The turn_input
    in main.py resets iteration_count, final_response, active_worker,
    worker_request, and latest_worker_result at the start of each user turn.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    iteration_count: int
    rejection_count: int
    final_response: str | None
    active_worker: str | None
    worker_request: dict | None          # {task, context, reasoning}
    latest_worker_result: dict | None    # what the most recent worker returned
    worker_history: Annotated[list[dict], operator.add]  # full audit trail
