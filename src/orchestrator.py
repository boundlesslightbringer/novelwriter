import json
import sqlite3
from operator import add
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.agents.workers import (
    CharacterSubagent,
    ConsequenceSubagent,
    PlanningSubagent,
    PlottingSubagent,
    ResolutionSubagent,
    WorldBibleManager,
    WritingSubagent,
)
from src.config import NovelWriterConfig

WorkerName = Literal[
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
    "resolution_subagent",
    "worldbible_manager",
]

WORKER_DESCRIPTIONS: Dict[WorkerName, str] = {
    "planning_subagent": "Story foundation worker for seed generation, rough endpoints, worldbuilding, and research integration.",
    "character_subagent": "Character worker for conception, creation, voice differentiation, and plot integration.",
    "plotting_subagent": "Plotting worker for scene planning, POV structure, braiding, conflict, and thread tracking.",
    "writing_subagent": "Writing worker for scene drafting, POV consistency, pacing, history integration, and local craft fixes.",
    "consequence_subagent": "Consequence worker for cascade analysis and realism-vs-fantasy audits.",
    "resolution_subagent": "Infrastructure worker for contradiction analysis, resolution option generation, and targeted contradiction fixes.",
    "worldbible_manager": "Infrastructure worker for all World Bible and knowledge-graph reads/writes.",
}


class BrainDecision(BaseModel):
    """Structured routing decision produced by the orchestrator brain."""
    reasoning: str = Field(description="Short internal justification for the next action.")
    action: Literal["delegate", "respond"] = Field(description="Whether to delegate or answer the user.")
    worker: WorkerName | None = Field(default=None, description="Worker to delegate to when action=delegate.")
    task: str | None = Field(default=None, description="Concrete worker task when action=delegate.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Structured context payload for the delegated worker.")


class WorkerRequest(TypedDict):
    worker: WorkerName
    task: str
    context: Dict[str, Any]
    reasoning: str


class WorkerRecord(TypedDict):
    worker: WorkerName
    task: str
    context: Dict[str, Any]
    result: Dict[str, Any]


class ContradictionContext(TypedDict, total=False):
    """Holds the full BLOCKED payload between ANALYSE and IMPLEMENT calls."""

    contradiction_record: Dict[str, Any]
    blocked_write: Dict[str, Any]
    prefetched_docs: List[Any]
    analyse_result: Dict[str, Any]


class DeferredContradiction(TypedDict):
    """A contradiction deferred to a future session."""

    contradiction_id: str
    deferral_note: str


def limit_worker_history(left: List[WorkerRecord] | None, right: List[WorkerRecord] | None) -> List[WorkerRecord]:
    """Custom reducer to keep only the last 5 worker records in state."""
    if not left:
        left = []
    if not right:
        right = []
    return (left + right)[-5:]


class OrchestratorState(TypedDict, total=False):
    messages: Annotated[List[AnyMessage], add_messages]
    worker_history: Annotated[List[WorkerRecord], limit_worker_history]
    latest_worker_result: WorkerRecord | None
    worker_request: WorkerRequest | None
    active_worker: WorkerName | None
    final_response: str | None
    iteration_count: int
    # Contradiction resolution lifecycle fields
    pending_contradiction: ContradictionContext | None
    deferred_contradictions: List[DeferredContradiction]
    pending_re_issue: Dict[str, Any] | None


class GRRMOrchestrator:
    """The main orchestrator class that manages the LangGraph runtime."""

    def __init__(self, config: NovelWriterConfig):
        self.config = config
        self.llm_config = config.get_llm_config()
        
        # Initialize workers
        self.workers = {
            "planning_subagent": PlanningSubagent(config),
            "character_subagent": CharacterSubagent(config),
            "plotting_subagent": PlottingSubagent(config),
            "writing_subagent": WritingSubagent(config),
            "consequence_subagent": ConsequenceSubagent(config),
            "resolution_subagent": ResolutionSubagent(config),
            "worldbible_manager": WorldBibleManager(config),
        }

        # Load orchestrator prompt
        src_dir = Path(__file__).resolve().parent.parent
        prompt_path = src_dir / "src" / "prompts" / "orchestrator_prompt.md"
        self.base_prompt = prompt_path.read_text(encoding="utf-8")

        # Build brain router
        model_name = self.llm_config.model_name
        provider = "openrouter"
            
        model_kwargs = {"temperature": self.llm_config.temperature}
        if self.llm_config.top_p is not None:
            model_kwargs["top_p"] = self.llm_config.top_p
        if self.llm_config.top_k is not None:
            model_kwargs["top_k"] = self.llm_config.top_k

        llm = init_chat_model(model=model_name, model_provider="openrouter", **model_kwargs)
        self.llm = llm
        self.brain_router = llm.with_structured_output(BrainDecision)

        # Initialize SQLite connection and checkpointer
        self.db_conn = sqlite3.connect("orchestrator_checkpoints.db", check_same_thread=False)
        self.memory = SqliteSaver(self.db_conn)

        # Compile graph
        self.graph = self._build_graph()

    def create_initial_state(self) -> OrchestratorState:
        """Create the initial terminal session state."""
        return {
            "messages": [],
            "worker_history": [],
            "latest_worker_result": None,
            "worker_request": None,
            "active_worker": None,
            "final_response": None,
            "iteration_count": 0,
            "pending_contradiction": None,
            "deferred_contradictions": [],
            "pending_re_issue": None,
        }

    def _serialize_for_prompt(self, payload: Any) -> str:
        try:
            return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
        except TypeError:
            return str(payload)

    def _build_brain_runtime_prompt(self, state: "OrchestratorState | None" = None) -> str:
        worker_catalog = "\n".join(
            f"- `{name}`: {desc}" for name, desc in WORKER_DESCRIPTIONS.items()
        )
        pending = self._serialize_for_prompt(
            (state or {}).get("pending_contradiction")
        )
        deferred = self._serialize_for_prompt(
            (state or {}).get("deferred_contradictions", [])
        )
        return (
            f"{self.base_prompt}\n\n"
            "## LangGraph Runtime Contract\n"
            "You are the only user-facing agent in this system. The human speaks only to you in the terminal.\n"
            "You may either:\n"
            "1. respond directly to the user, or\n"
            "2. delegate one concrete task to exactly one worker.\n\n"
            "Rules:\n"
            "- Never ask the human to call workers or workflows.\n"
            "- Never expose internal routing unless it genuinely helps the user.\n"
            "- Delegate whenever specialized domain work or World Bible I/O is needed.\n"
            "- Route all routine World Bible reads/writes through `worldbible_manager`.\n"
            "  Exception: contradiction resolution writes go through `resolution_subagent` in IMPLEMENT mode.\n"
            "- When `worldbible_manager` returns status='blocked', follow the Contradiction Resolution Protocol"
            " in your system prompt: ANALYSE → user discussion → IMPLEMENT → RE_ISSUE.\n"
            "- Artifact Persistence Rule: When a creative worker returns with status='success' and non-empty artifacts, "
            "you MUST delegate a write to worldbible_manager BEFORE responding to the user or delegating to another worker. "
            "Do NOT delegate a read to verify content that was just returned — write it first.\n"
            "- Delegate to only one worker at a time.\n"
            "- After a worker returns, either delegate again or respond to the user.\n\n"
            f"Current contradiction state:\n"
            f"- pending_contradiction: {pending}\n"
            f"- deferred_contradictions: {deferred}\n\n"
            f"Available workers:\n{worker_catalog}\n"
        )

    def _build_brain_messages(self, state: OrchestratorState) -> List[BaseMessage]:
        messages: List[BaseMessage] = [SystemMessage(content=self._build_brain_runtime_prompt(state))]

        worker_history = state.get("worker_history", [])
        if worker_history:
            messages.append(
                SystemMessage(
                    content=(
                        "Recent worker history:\n"
                        f"{self._serialize_for_prompt(worker_history[-4:])}"
                    )
                )
            )

        latest_worker_result = state.get("latest_worker_result")
        if latest_worker_result:
            messages.append(
                SystemMessage(
                    content=(
                        "Latest worker result available for routing:\n"
                        f"{self._serialize_for_prompt(latest_worker_result)}"
                    )
                )
            )

        pending_re_issue = state.get("pending_re_issue")
        if pending_re_issue:
            messages.append(
                SystemMessage(
                    content=(
                        "Contradiction resolved. RE_ISSUE_BLOCKED_WRITE signal received:\n"
                        f"{self._serialize_for_prompt(pending_re_issue)}\n"
                        "Notify the originating subagent to re-issue the blocked write."
                    )
                )
            )

        deferred = state.get("deferred_contradictions", [])
        if deferred:
            messages.append(
                SystemMessage(
                    content=(
                        "Deferred contradictions from prior sessions that must be surfaced before writing resumes:\n"
                        f"{self._serialize_for_prompt(deferred)}"
                    )
                )
            )

        messages.extend(state.get("messages", []))
        return messages

    def _extract_worker_artifacts(self, state: OrchestratorState) -> Dict[str, Any]:
        """Extract artifacts dict from the latest worker result, if present."""
        latest = state.get("latest_worker_result")
        if not latest:
            return {}
        result = latest.get("result", {})
        return result.get("artifacts", {})

    def _handle_blocked_verdict(self, state: OrchestratorState) -> Dict[str, Any] | None:
        """Detect a BLOCKED verdict from worldbible_manager and store contradiction context.

        Returns a state update dict routing to resolution_subagent (ANALYSE mode), or
        None if no BLOCKED verdict is present in the latest result.
        """
        latest = state.get("latest_worker_result")
        if not latest or latest.get("worker") != "worldbible_manager":
            return None

        artifacts = self._extract_worker_artifacts(state)
        wbm_result = artifacts.get("result", {})
        if not isinstance(wbm_result, dict) or wbm_result.get("status") != "blocked":
            return None

        contradiction_record = wbm_result.get("contradiction_record", {})
        blocked_write = wbm_result.get("blocked_write", {})
        prefetched_docs = wbm_result.get("prefetched_docs", [])

        pending: ContradictionContext = {
            "contradiction_record": contradiction_record,
            "blocked_write": blocked_write,
            "prefetched_docs": prefetched_docs,
        }

        return {
            "pending_contradiction": pending,
            "active_worker": "resolution_subagent",
            "worker_request": {
                "worker": "resolution_subagent",
                "task": "Analyse the blocked contradiction and produce a plain-language briefing with resolution options.",
                "context": {
                    "mode": "ANALYSE",
                    "contradiction_record": contradiction_record,
                    "blocked_write": blocked_write,
                    "prefetched_docs": prefetched_docs,
                },
                "reasoning": "WorldBibleManager returned a BLOCKED verdict. Routing to resolution_subagent for ANALYSE.",
            },
            "final_response": None,
            "latest_worker_result": None,
        }

    def _handle_resolution_result(self, state: OrchestratorState) -> Dict[str, Any] | None:
        """Detect a RESOLVED or RESOLUTION_FAILED result from resolution_subagent.

        On RESOLVED: stores the re-issue signal and clears pending_contradiction.
        On RESOLUTION_FAILED: surfaces the failure for the LLM to relay to the user.
        Returns a state update dict, or None if not applicable.
        """
        latest = state.get("latest_worker_result")
        if not latest or latest.get("worker") != "resolution_subagent":
            return None

        artifacts = self._extract_worker_artifacts(state)
        resolution_result = artifacts.get("resolution_result", {})
        if not isinstance(resolution_result, dict):
            return None

        status = resolution_result.get("status")

        if status == "RESOLVED":
            re_issue_signal = resolution_result.get("re_issue_signal", {})
            return {
                "pending_contradiction": None,
                "pending_re_issue": re_issue_signal,
                "latest_worker_result": None,
            }

        if status == "RESOLUTION_FAILED":
            return {
                "pending_contradiction": None,
                "pending_re_issue": None,
            }

        return None

    def brain_node(self, state: OrchestratorState) -> Dict[str, Any]:
        """Route the next graph step, handling contradiction lifecycle transitions first."""
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= self.config.max_brain_iterations:
            return {
                "final_response": (
                    "I hit my internal delegation limit before reaching a stable answer. "
                    "Please restate the task more narrowly or continue from the most recent result."
                ),
                "active_worker": None,
                "worker_request": None,
            }

        # Deterministic contradiction lifecycle transitions — checked before LLM routing.
        blocked_update = self._handle_blocked_verdict(state)
        if blocked_update is not None:
            return {**blocked_update, "iteration_count": iteration_count + 1}

        resolution_update = self._handle_resolution_result(state)
        if resolution_update is not None:
            # Fall through to LLM routing so the brain can present the outcome to the user.
            state = {**state, **resolution_update}

        # Failure guard: stop if the same worker fails twice on the same task.
        latest = state.get("latest_worker_result")
        if latest:
            result = latest.get("result", {})
            if result.get("status") == "failed" and not result.get("artifacts"):
                worker_history = state.get("worker_history", [])
                failures = 0
                for record in reversed(worker_history):
                    if record.get("worker") == latest.get("worker") and record.get("task") == latest.get("task"):
                        rec_result = record.get("result", {})
                        if rec_result.get("status") == "failed" and not rec_result.get("artifacts"):
                            failures += 1
                        else:
                            break
                    else:
                        break
                
                if failures >= 2:
                    return {
                        "final_response": f"The worker `{latest.get('worker')}` failed twice on the same task. Stopping to prevent a loop.\n\nError: {result.get('summary')}",
                        "active_worker": None,
                        "worker_request": None,
                        "iteration_count": iteration_count + 1,
                    }

        try:
            decision = self.brain_router.invoke(self._build_brain_messages(state), stream=False)
        except Exception as error:
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

        return {
            "active_worker": None,
            "worker_request": None,
            "iteration_count": iteration_count + 1,
        }

    def respond_node(self, state: OrchestratorState, config: RunnableConfig) -> Dict[str, Any]:
        """Generate the final response to the user using a standard LLM call."""
        messages = self._build_brain_messages(state)
        
        # Add a system prompt instructing the model to respond to the user
        messages.append(SystemMessage(content=(
            "You have decided to respond to the user. Generate your final response now "
            "based on the conversation and worker history. DO NOT output any JSON, "
            "routing commands, or delegation tags. Speak naturally to the human."
        )))
        
        response = self.llm.invoke(messages, config)
        
        return {
            "messages": [response],
            "final_response": response.content,
            "latest_worker_result": None,
            "active_worker": None,
            "worker_request": None,
        }

    def _route_from_brain(self, state: OrchestratorState) -> str:
        active_worker = state.get("active_worker")
        if active_worker in self.workers:
            return active_worker
        return "respond"

    def _build_graph(self) -> Any:
        graph = StateGraph(OrchestratorState)
        
        graph.add_node("brain", self.brain_node)
        graph.add_node("respond", self.respond_node)
        
        # Add worker nodes
        for name, worker in self.workers.items():
            graph.add_node(name, worker.invoke)

        graph.add_edge(START, "brain")
        
        # Routing from brain
        routing_map = {"respond": "respond"}
        routing_map.update({name: name for name in self.workers})
        graph.add_conditional_edges("brain", self._route_from_brain, routing_map)
        
        # Return edges from workers back to brain
        for name in self.workers:
            graph.add_edge(name, "brain")
            
        graph.add_edge("respond", END)

        return graph.compile(checkpointer=self.memory)
