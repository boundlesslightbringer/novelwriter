from typing import Any

from langchain_core.messages import HumanMessage


def _build_turn_input(session_state: dict[str, Any], user_input: str) -> dict[str, Any]:
    """Create the graph input state for the next terminal turn."""
    next_messages = list(session_state.get("messages", []))
    next_messages.append(HumanMessage(content=user_input))
    return {
        **session_state,
        "messages": next_messages,
        "iteration_count": 0,
        "final_response": None,
        "active_worker": None,
        "worker_request": None,
    }


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
    session_state = orchestrator.create_initial_state()
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
            
            for event_type, event_data in orchestrator.graph.stream(
                _build_turn_input(session_state, user_input), 
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
                    for node_name, response in event_data.items():
                        session_state = {
                            "messages": response.get("messages", session_state.get("messages", [])),
                            "worker_history": response.get("worker_history", session_state.get("worker_history", [])),
                            "latest_worker_result": response.get("latest_worker_result"),
                            "worker_request": response.get("worker_request"),
                            "active_worker": response.get("active_worker"),
                            "final_response": response.get("final_response"),
                            "iteration_count": response.get("iteration_count", 0),
                        }
            
            print() # Print a newline after the streamed response is complete
        except KeyboardInterrupt:
            break
        except Exception as error:
            print(f"\nError: {error}")

if __name__ == "__main__":
    main()
