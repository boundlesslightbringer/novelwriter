import uuid
from typing import Any

from langchain_core.messages import HumanMessage


def main() -> None:
    """Start a terminal REPL that talks only to the orchestrator graph."""
    try:
        from src.config import NovelWriterConfig
        from src.orchestrator import GRRMOrchestrator
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Could not import the LangGraph orchestrator. Install the project dependencies first."
        ) from error

    config = NovelWriterConfig()
    orchestrator = GRRMOrchestrator(config)
    
    # Generate a unique thread ID for this terminal session
    thread_id = str(uuid.uuid4())
    run_config = {"configurable": {"thread_id": thread_id}}
    
    print("GRRM orchestrator initialized.")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nUser> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue

            print("\nOrchestrator> ", end="", flush=True)
            
            turn_input = {
                "messages": [HumanMessage(content=user_input)],
                "iteration_count": 0,
                "final_response": None,
                "active_worker": None,
                "worker_request": None,
            }
            
            for event_type, event_data in orchestrator.graph.stream(
                turn_input, 
                config=run_config,
                stream_mode=["messages", "updates"]
            ):
                if event_type == "messages":
                    chunk, metadata = event_data
                    if metadata.get("langgraph_node") == "respond" and chunk.content:
                        content = chunk.content
                        if isinstance(content, str):
                            print(content, end="", flush=True)
                        elif isinstance(content, list):
                            for part in content:
                                if isinstance(part, str):
                                    print(part, end="", flush=True)
                                elif isinstance(part, dict) and part.get("type") == "text":
                                    print(part.get("text", ""), end="", flush=True)
                elif event_type == "updates":
                    # Print node transitions and worker results for debugging
                    for node_name, state_update in event_data.items():
                        if node_name == "brain":
                            worker = state_update.get("active_worker")
                            if worker:
                                print(f"\n[Brain] Delegating to: {worker}")
                                task = state_update.get("worker_request", {}).get("task", "")
                                print(f"[Brain] Task: {task}")
                        elif node_name in orchestrator.workers:
                            print(f"\n[{node_name}] Completed.")
                            result = state_update.get("latest_worker_result", {}).get("result", {})
                            print(f"[{node_name}] Status: {result.get('status')}")
                            print(f"[{node_name}] Summary: {result.get('summary')}")
            
            print() # Print a newline after the streamed response is complete
        except KeyboardInterrupt:
            break
        except Exception as error:
            print(f"\nError: {error}")

if __name__ == "__main__":
    main()
