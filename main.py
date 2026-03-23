from typing import Any

from langchain_core.messages import HumanMessage


def _normalize_message_content(content: Any) -> str:
    """Normalize LangChain message content into printable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_chunks: list[str] = []
        for part in content:
            if isinstance(part, str):
                text_chunks.append(part)
            elif isinstance(part, dict) and part.get("type") == "text":
                text_chunks.append(str(part.get("text", "")))
        return "\n".join(chunk for chunk in text_chunks if chunk.strip())
    return str(content)


def _extract_last_assistant_message_text(response: dict[str, Any]) -> str:
    """Extract the latest assistant-visible message from graph output."""
    messages = response.get("messages", [])
    if not messages:
        return ""
    last_message = messages[-1]
    content = getattr(last_message, "content", "")
    return _normalize_message_content(content).strip()


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
        from src.deepagent import create_grrm_orchestrator, create_initial_state
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Could not import the LangGraph orchestrator. Install the project dependencies first."
        ) from error

    orchestrator = create_grrm_orchestrator()
    session_state = create_initial_state()
    print("GRRM orchestrator initialized.")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nUser> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue

            response = orchestrator.invoke(_build_turn_input(session_state, user_input))
            session_state = {
                "messages": response.get("messages", session_state.get("messages", [])),
                "worker_history": response.get("worker_history", session_state.get("worker_history", [])),
                "latest_worker_result": response.get("latest_worker_result"),
                "worker_request": response.get("worker_request"),
                "active_worker": response.get("active_worker"),
                "final_response": response.get("final_response"),
                "iteration_count": response.get("iteration_count", 0),
            }

            assistant_text = _extract_last_assistant_message_text(response)
            if assistant_text:
                print(f"\nOrchestrator> {assistant_text}")
        except KeyboardInterrupt:
            break
        except Exception as error:
            print(f"\nError: {error}")

if __name__ == "__main__":
    main()
