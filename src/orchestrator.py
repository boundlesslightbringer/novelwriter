from typing import Any, Callable, Dict

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
    response = state.get("final_response", "No response generated.")
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


class GRRMOrchestrator:
    """The main orchestrator graph for the Novel Writer."""
    
    def __init__(self, config: NovelWriterConfig):
        self.config = config
        
        # Initialize checkpointer
        self.mongo_client = MongoClient(self.config.mongodb_uri)
        self.checkpointer = MongoDBSaver(
            client=self.mongo_client,
            db_name=self.config.mongodb_checkpoint_db_name
        )
        
        self.workers = list(VALID_WORKERS)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Construct and compile the StateGraph."""
        builder = StateGraph(OrchestratorState)
        
        # Add nodes
        builder.add_node("brain", BrainNode(self.config))
        builder.add_node("respond", respond_node)
        
        for worker_name in self.workers:
            builder.add_node(worker_name, make_stub_worker(worker_name))
            
        # Add edges
        builder.add_edge(START, "brain")
        
        builder.add_conditional_edges(
            "brain",
            route_from_brain,
            {worker: worker for worker in self.workers} | {"respond": "respond"}
        )
        
        for worker_name in self.workers:
            builder.add_edge(worker_name, "brain")
            
        builder.add_edge("respond", END)
        
        # Compile
        return builder.compile(checkpointer=self.checkpointer)
