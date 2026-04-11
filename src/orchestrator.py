from typing import Any, Callable, Dict, Mapping

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

from src.agents.base import WorkerResponse
from src.brain import BrainNode
from src.config import NovelWriterConfig
from src.state import OrchestratorState, VALID_WORKERS


def route_from_brain(state: OrchestratorState) -> str:
    """Conditional routing logic based on the brain's decision."""
    if state.get("final_response") is not None:
        return "respond"
    worker = state.get("active_worker")
    if worker and worker in VALID_WORKERS:
        return worker
    return "respond"  # safe fallback; graph never gets stuck


def respond_node(state: OrchestratorState) -> Dict[str, Any]:
    """Terminal node that formats the final response."""
    response = state.get("final_response")
    if not isinstance(response, str) or not response.strip():
        response = "No response generated."
    return {"messages": [AIMessage(content=response)]}


# Global dictionary to configure stub outputs for testing
STUB_CONFIG = {}

def make_stub_worker(name: str) -> Callable[[OrchestratorState, RunnableConfig | None], Dict[str, Any]]:
    """Factory for creating stub worker nodes."""
    def stub_worker(state: OrchestratorState, config: RunnableConfig | None = None) -> Dict[str, Any]:
        worker_request = state.get("worker_request")
        task = worker_request.get("task", "unknown_task") if worker_request else "unknown_task"
        context = worker_request.get("context", {}) if worker_request else {}
        
        # Check if there's a specific configuration for this worker
        stub_conf = STUB_CONFIG.get(name, {})
        status = stub_conf.get("status", "success")
        summary = stub_conf.get("summary", f"Stub execution for {name}")
        artifacts = stub_conf.get("artifacts", {"stub": True})
        
        result = WorkerResponse(
            status=status,
            summary=summary,
            artifacts=artifacts
        )
        
        worker_record = {
            "worker": name,
            "task": task,
            "context": context,
            "result": result.model_dump(),
        }
        
        return {
            "latest_worker_result": worker_record,
            "worker_history": [worker_record],
            "worker_request": None,
            "active_worker": None,
        }
    
    return stub_worker


def _real_worker_classes() -> Dict[str, type]:
    """Return the canonical worker class mapping used for integration runs."""
    from src.agents.workers import (
        CharacterSubagent,
        ConsequenceSubagent,
        PlanningSubagent,
        PlottingSubagent,
        ResolutionSubagent,
        StoryStateManager,
        WritingSubagent,
    )

    return {
        "planning_subagent": PlanningSubagent,
        "character_subagent": CharacterSubagent,
        "plotting_subagent": PlottingSubagent,
        "writing_subagent": WritingSubagent,
        "consequence_subagent": ConsequenceSubagent,
        "story_state_manager": StoryStateManager,
        "resolution_subagent": ResolutionSubagent,
    }


class GRRMOrchestrator:
    """The main orchestrator graph for the Novel Writer."""

    def __init__(
        self,
        config: NovelWriterConfig,
        worker_impls: Mapping[str, Any] | None = None,
        checkpointer: Any | None = None,
    ):
        self.config = config

        self._worker_impls = dict(worker_impls or {})
        self.workers = list(VALID_WORKERS)

        # Initialize checkpointer (injectable for tests).
        self.mongo_client = None
        if checkpointer is None:
            self.mongo_client = MongoClient(self.config.mongodb_uri)
            self.checkpointer = MongoDBSaver(
                client=self.mongo_client,
                db_name=self.config.mongodb_checkpoint_db_name,
            )
        else:
            self.checkpointer = checkpointer

        self.graph = self._build_graph()

    @staticmethod
    def real_worker_impls() -> Dict[str, type]:
        """Provide real worker classes for full-stack orchestration tests."""
        return _real_worker_classes()

    def _resolve_worker_node(
        self,
        worker_name: str,
    ) -> Callable[[OrchestratorState, RunnableConfig | None], Dict[str, Any]]:
        worker_impl = self._worker_impls.get(worker_name)
        if worker_impl is None:
            return make_stub_worker(worker_name)

        if isinstance(worker_impl, type):
            worker_impl = worker_impl(self.config)

        if hasattr(worker_impl, "invoke") and callable(worker_impl.invoke):
            def _worker_node(
                state: OrchestratorState,
                config: RunnableConfig | None = None,
            ) -> Dict[str, Any]:
                from src.bootstrap_trace import append_ssm_worker_trace

                result = worker_impl.invoke(state, config)
                append_ssm_worker_trace(worker_name, result)
                return result

            return _worker_node

        if callable(worker_impl):
            return worker_impl

        raise TypeError(f"Unsupported worker implementation for '{worker_name}': {type(worker_impl)!r}")

    def _build_graph(self):
        """Construct and compile the StateGraph."""
        builder = StateGraph(OrchestratorState)

        # Add nodes
        builder.add_node("brain", BrainNode(self.config))
        builder.add_node("respond", respond_node)

        for worker_name in self.workers:
            builder.add_node(worker_name, self._resolve_worker_node(worker_name))

        # Add edges
        builder.add_edge(START, "brain")

        builder.add_conditional_edges(
            "brain",
            route_from_brain,
            {worker: worker for worker in self.workers} | {"respond": "respond"},
        )

        for worker_name in self.workers:
            builder.add_edge(worker_name, "brain")

        builder.add_edge("respond", END)

        # Compile
        return builder.compile(checkpointer=self.checkpointer)
