"""
LangGraph orchestrator-worker runtime for the GRRM Novel Writer.

The terminal talks only to the orchestrator brain. The brain decides whether
to answer directly or delegate to one domain worker at a time.
"""

from __future__ import annotations

import json
from functools import lru_cache, partial
from operator import add
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

try:
    from src.tools import progressive_skill_loader
    from src.world_bible_tools import (
        add_kg_edge,
        add_kg_node,
        detect_kg_contradiction,
        init_kg_db,
        query_kg_edges,
        query_kg_nodes,
        update_kg_edge,
        update_kg_node,
    )
except ModuleNotFoundError:
    from tools import progressive_skill_loader
    from world_bible_tools import (
        add_kg_edge,
        add_kg_node,
        detect_kg_contradiction,
        init_kg_db,
        query_kg_edges,
        query_kg_nodes,
        update_kg_edge,
        update_kg_node,
    )

DEFAULT_MODEL = "anthropic:claude-sonnet-4-20250514"
SRC_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = SRC_DIR / "subagent_prompts"
ORCHESTRATOR_PROMPT_PATH = SRC_DIR / "orchestrator_prompt.md"
MAX_BRAIN_ITERATIONS = 8

WorkerName = Literal[
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
    "worldbible_manager",
]

ACTIVE_WORKER_NAMES: tuple[WorkerName, ...] = (
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
    "worldbible_manager",
)

WORKER_DESCRIPTIONS: dict[WorkerName, str] = {
    "planning_subagent": (
        "Story foundation worker for seed generation, rough endpoints, worldbuilding, "
        "and research integration."
    ),
    "character_subagent": (
        "Character worker for conception, creation, voice differentiation, and "
        "plot integration."
    ),
    "plotting_subagent": (
        "Plotting worker for scene planning, POV structure, braiding, conflict, "
        "and thread tracking."
    ),
    "writing_subagent": (
        "Writing worker for scene drafting, POV consistency, pacing, history "
        "integration, and local craft fixes."
    ),
    "consequence_subagent": (
        "Consequence worker for cascade analysis and realism-vs-fantasy audits."
    ),
    "worldbible_manager": (
        "Infrastructure worker for all World Bible and knowledge-graph reads/writes."
    ),
}

WORKER_PROMPT_FILES: dict[WorkerName, str] = {
    "planning_subagent": "planning_subagent.md",
    "character_subagent": "character_subagent.md",
    "plotting_subagent": "plotting_subagent.md",
    "writing_subagent": "writing_subagent.md",
    "consequence_subagent": "consequence_subagent.md",
    "worldbible_manager": "worldbiblemanager.md",
}

SKILL_WORKER_NAMES: tuple[WorkerName, ...] = (
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
)

WORLD_BIBLE_TOOLS = [
    init_kg_db,
    query_kg_nodes,
    query_kg_edges,
    add_kg_node,
    update_kg_node,
    add_kg_edge,
    update_kg_edge,
    detect_kg_contradiction,
]


class BrainDecision(BaseModel):
    """Structured routing decision produced by the orchestrator brain."""

    reasoning: str = Field(description="Short internal justification for the next action.")
    action: Literal["delegate", "respond"] = Field(description="Whether to delegate or answer the user.")
    worker: WorkerName | None = Field(default=None, description="Worker to delegate to when action=delegate.")
    task: str | None = Field(default=None, description="Concrete worker task when action=delegate.")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured context payload for the delegated worker.",
    )
    response: str | None = Field(default=None, description="Final user-facing answer when action=respond.")


class WorkerResponse(BaseModel):
    """Structured response returned by every worker node."""

    status: Literal["completed", "need_input", "failed"] = Field(
        description="Overall worker execution status."
    )
    summary: str = Field(description="Concise summary of what the worker did or found.")
    artifacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific structured outputs produced by the worker.",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Questions that the orchestrator may need to relay to the user.",
    )
    recommended_next_worker: WorkerName | None = Field(
        default=None,
        description="Optional recommendation for which worker should act next.",
    )


class WorkerRequest(TypedDict):
    """Structured worker request stored in graph state."""

    worker: WorkerName
    task: str
    context: dict[str, Any]
    reasoning: str


class WorkerRecord(TypedDict):
    """Stored record of a completed worker execution."""

    worker: WorkerName
    task: str
    context: dict[str, Any]
    result: dict[str, Any]


class OrchestratorState(TypedDict, total=False):
    """LangGraph state for the orchestrator-worker loop."""

    messages: Annotated[list[AnyMessage], add_messages]
    worker_history: Annotated[list[WorkerRecord], add]
    latest_worker_result: WorkerRecord | None
    worker_request: WorkerRequest | None
    active_worker: WorkerName | None
    final_response: str | None
    iteration_count: int


def create_initial_state() -> OrchestratorState:
    """Create the initial terminal session state.

    Returns:
        Empty graph state suitable for the first user turn.
    """
    return {
        "messages": [],
        "worker_history": [],
        "latest_worker_result": None,
        "worker_request": None,
        "active_worker": None,
        "final_response": None,
        "iteration_count": 0,
    }


def _read_prompt(prompt_path: Path) -> str:
    """Read a prompt file from disk."""
    return prompt_path.read_text(encoding="utf-8")


def _build_chat_model(model: str) -> Any:
    """Build a LangChain chat model from a provider-prefixed identifier."""
    if ":" in model:
        provider, model_name = model.split(":", maxsplit=1)
        return init_chat_model(model=model_name, model_provider=provider)
    return init_chat_model(model=model)


def _serialize_for_prompt(payload: Any) -> str:
    """Serialize arbitrary data for prompt injection."""
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _message_content_to_text(content: Any) -> str:
    """Normalize message content into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict) and part.get("type") == "text":
                chunks.append(str(part.get("text", "")))
        return "\n".join(chunk for chunk in chunks if chunk.strip())
    return str(content)


def _messages_to_transcript(messages: list[BaseMessage], max_messages: int = 10) -> str:
    """Render recent conversation as a compact transcript."""
    transcript_lines: list[str] = []
    for message in messages[-max_messages:]:
        role = message.type.upper()
        content = _message_content_to_text(message.content).strip()
        if content:
            transcript_lines.append(f"{role}: {content}")
    return "\n\n".join(transcript_lines)


def _extract_last_message_text(messages: list[BaseMessage]) -> str:
    """Extract the final message text from an agent result."""
    if not messages:
        return ""
    return _message_content_to_text(messages[-1].content).strip()


def _build_brain_runtime_prompt() -> str:
    """Create the orchestrator brain prompt."""
    worker_catalog = "\n".join(
        f"- `{worker_name}`: {description}" for worker_name, description in WORKER_DESCRIPTIONS.items()
    )
    return (
        f"{_read_prompt(ORCHESTRATOR_PROMPT_PATH)}\n\n"
        "## LangGraph Runtime Contract\n"
        "You are the only user-facing agent in this system. The human speaks only to you in the terminal.\n"
        "You may either:\n"
        "1. respond directly to the user, or\n"
        "2. delegate one concrete task to exactly one worker.\n\n"
        "Rules:\n"
        "- Never ask the human to call workers or workflows.\n"
        "- Never expose internal routing unless it genuinely helps the user.\n"
        "- Delegate whenever specialized domain work or World Bible I/O is needed.\n"
        "- Always route World Bible reads and writes through `worldbible_manager`.\n"
        "- Delegate to only one worker at a time.\n"
        "- After a worker returns, either delegate again or respond to the user.\n\n"
        f"Available workers:\n{worker_catalog}\n"
    )


def _build_worker_runtime_prompt(worker_name: WorkerName) -> str:
    """Create the system prompt for a worker node."""
    base_prompt = _read_prompt(PROMPTS_DIR / WORKER_PROMPT_FILES[worker_name])
    if worker_name in SKILL_WORKER_NAMES:
        tool_instruction = (
            "You have access to `progressive_skill_loader`. Before performing specialized "
            "domain work, load the relevant skill instructions from the skills directory."
        )
    else:
        tool_instruction = (
            "You have direct access to the World Bible knowledge-graph tools. Use them "
            "for reads and writes instead of inventing persisted state."
        )

    return (
        f"{base_prompt}\n\n"
        "## LangGraph Runtime Contract\n"
        "You are an internal worker node. The human user never speaks to you directly.\n"
        "- Execute only the task provided by the orchestrator brain.\n"
        "- Do not answer as the top-level assistant.\n"
        f"- {tool_instruction}\n"
        "- Place domain-specific structured outputs in the `artifacts` field.\n"
        "- Keep `summary` concise and factual.\n"
    )


@lru_cache(maxsize=1)
def _build_brain_router(model: str = DEFAULT_MODEL) -> Any:
    """Create the structured-output router used by the orchestrator brain."""
    return _build_chat_model(model).with_structured_output(BrainDecision)


@lru_cache(maxsize=16)
def _build_worker_agent(worker_name: WorkerName, model: str = DEFAULT_MODEL) -> Any:
    """Create a LangGraph worker agent for a specific domain."""
    tools = [progressive_skill_loader] if worker_name in SKILL_WORKER_NAMES else WORLD_BIBLE_TOOLS
    return create_react_agent(
        model=_build_chat_model(model),
        tools=tools,
        prompt=_build_worker_runtime_prompt(worker_name),
        response_format=WorkerResponse,
        name=worker_name,
    )


def _coerce_worker_response(result: dict[str, Any]) -> WorkerResponse:
    """Normalize worker output into the shared structured schema."""
    structured_response = result.get("structured_response")
    if isinstance(structured_response, WorkerResponse):
        return structured_response
    if isinstance(structured_response, dict):
        return WorkerResponse.model_validate(structured_response)

    fallback_text = _extract_last_message_text(result.get("messages", []))
    artifacts = {"raw_output": fallback_text} if fallback_text else {}
    return WorkerResponse(
        status="completed",
        summary=fallback_text or "Worker completed without structured output.",
        artifacts=artifacts,
    )


def _build_brain_messages(state: OrchestratorState) -> list[BaseMessage]:
    """Assemble the orchestrator brain input messages."""
    messages: list[BaseMessage] = [SystemMessage(content=_build_brain_runtime_prompt())]

    worker_history = state.get("worker_history", [])
    if worker_history:
        messages.append(
            SystemMessage(
                content=(
                    "Recent worker history:\n"
                    f"{_serialize_for_prompt(worker_history[-4:])}"
                )
            )
        )

    latest_worker_result = state.get("latest_worker_result")
    if latest_worker_result:
        messages.append(
            SystemMessage(
                content=(
                    "Latest worker result available for routing:\n"
                    f"{_serialize_for_prompt(latest_worker_result)}"
                )
            )
        )

    messages.extend(state.get("messages", []))
    return messages


def brain_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Decide whether to respond directly or delegate to a worker."""
    iteration_count = state.get("iteration_count", 0)
    if iteration_count >= MAX_BRAIN_ITERATIONS:
        return {
            "final_response": (
                "I hit my internal delegation limit before reaching a stable answer. "
                "Please restate the task more narrowly or continue from the most recent result."
            ),
            "active_worker": None,
            "worker_request": None,
        }

    try:
        decision = _build_brain_router(model).invoke(_build_brain_messages(state))
    except Exception as error:  # pragma: no cover - defensive runtime guard
        return {
            "final_response": f"I could not route the request because the orchestrator model failed: {error}",
            "active_worker": None,
            "worker_request": None,
        }

    if decision.action == "delegate" and decision.worker and decision.task:
        return {
            "active_worker": decision.worker,
            "worker_request": {
                "worker": decision.worker,
                "task": decision.task,
                "context": decision.context,
                "reasoning": decision.reasoning,
            },
            "final_response": None,
            "iteration_count": iteration_count + 1,
        }

    final_response = decision.response or "I do not have a complete answer yet."
    return {
        "active_worker": None,
        "worker_request": None,
        "final_response": final_response,
        "iteration_count": iteration_count + 1,
    }


def _run_worker(worker_name: WorkerName, state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute a single worker node and store its structured result."""
    worker_request = state.get("worker_request")
    if not worker_request:
        return {
            "latest_worker_result": {
                "worker": worker_name,
                "task": "missing_request",
                "context": {},
                "result": WorkerResponse(
                    status="failed",
                    summary="Worker was invoked without an active request.",
                ).model_dump(),
            },
            "worker_request": None,
            "active_worker": None,
        }

    worker_payload = {
        "task": worker_request["task"],
        "context": worker_request.get("context", {}),
        "reasoning_from_brain": worker_request.get("reasoning", ""),
        "conversation_transcript": _messages_to_transcript(state.get("messages", [])),
        "recent_worker_history": state.get("worker_history", [])[-3:],
    }

    try:
        result = _build_worker_agent(worker_name, model).invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Execute the following orchestrator request and return a structured worker result.\n\n"
                            f"{_serialize_for_prompt(worker_payload)}"
                        )
                    )
                ]
            }
        )
        structured_result = _coerce_worker_response(result).model_dump()
    except Exception as error:  # pragma: no cover - defensive runtime guard
        structured_result = WorkerResponse(
            status="failed",
            summary=f"Worker execution failed: {error}",
        ).model_dump()

    worker_record: WorkerRecord = {
        "worker": worker_name,
        "task": worker_request["task"],
        "context": worker_request.get("context", {}),
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }


def planning_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the planning worker."""
    return _run_worker("planning_subagent", state, model=model)


def character_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the character worker."""
    return _run_worker("character_subagent", state, model=model)


def plotting_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the plotting worker."""
    return _run_worker("plotting_subagent", state, model=model)


def writing_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the writing worker."""
    return _run_worker("writing_subagent", state, model=model)


def consequence_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the consequence worker."""
    return _run_worker("consequence_subagent", state, model=model)


def worldbible_worker_node(state: OrchestratorState, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Execute the World Bible worker."""
    return _run_worker("worldbible_manager", state, model=model)


def respond_node(state: OrchestratorState) -> dict[str, Any]:
    """Append the orchestrator's final response to the public message history."""
    final_response = state.get("final_response") or "I do not have a final response."
    return {
        "messages": [AIMessage(content=final_response)],
        "final_response": None,
        "latest_worker_result": None,
        "active_worker": None,
        "worker_request": None,
    }


def _route_from_brain(state: OrchestratorState) -> str:
    """Select the next graph edge after the brain node."""
    active_worker = state.get("active_worker")
    if active_worker in ACTIVE_WORKER_NAMES:
        return active_worker
    return "respond"


def get_registered_subagent_names(include_shelved_subagents: bool = False) -> list[str]:
    """Return registered worker names exposed to the orchestrator runtime.

    Args:
        include_shelved_subagents: Retained for compatibility. Shelved workers are
            not currently wired into the active LangGraph runtime.

    Returns:
        The list of active worker names.
    """
    del include_shelved_subagents
    return list(ACTIVE_WORKER_NAMES)


def create_grrm_orchestrator(*, model: str = DEFAULT_MODEL, include_shelved_subagents: bool = False) -> Any:
    """Create the compiled LangGraph orchestrator-worker runtime.

    Args:
        model: Provider-prefixed chat model identifier.
        include_shelved_subagents: Retained for compatibility. Shelved workers are
            not currently part of the active graph.

    Returns:
        A compiled LangGraph state machine for terminal interaction.
    """
    del include_shelved_subagents

    graph = StateGraph(OrchestratorState)
    graph.add_node("brain", partial(brain_node, model=model))
    graph.add_node("respond", respond_node)
    graph.add_node("planning_subagent", partial(planning_worker_node, model=model))
    graph.add_node("character_subagent", partial(character_worker_node, model=model))
    graph.add_node("plotting_subagent", partial(plotting_worker_node, model=model))
    graph.add_node("writing_subagent", partial(writing_worker_node, model=model))
    graph.add_node("consequence_subagent", partial(consequence_worker_node, model=model))
    graph.add_node("worldbible_manager", partial(worldbible_worker_node, model=model))

    graph.add_edge(START, "brain")
    graph.add_conditional_edges(
        "brain",
        _route_from_brain,
        {
            "respond": "respond",
            "planning_subagent": "planning_subagent",
            "character_subagent": "character_subagent",
            "plotting_subagent": "plotting_subagent",
            "writing_subagent": "writing_subagent",
            "consequence_subagent": "consequence_subagent",
            "worldbible_manager": "worldbible_manager",
        },
    )
    graph.add_edge("planning_subagent", "brain")
    graph.add_edge("character_subagent", "brain")
    graph.add_edge("plotting_subagent", "brain")
    graph.add_edge("writing_subagent", "brain")
    graph.add_edge("consequence_subagent", "brain")
    graph.add_edge("worldbible_manager", "brain")
    graph.add_edge("respond", END)

    return graph.compile()


__all__ = [
    "ACTIVE_WORKER_NAMES",
    "DEFAULT_MODEL",
    "OrchestratorState",
    "WORLD_BIBLE_TOOLS",
    "create_grrm_orchestrator",
    "create_initial_state",
    "get_registered_subagent_names",
]
