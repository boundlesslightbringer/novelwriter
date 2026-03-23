import sys

def main() -> None:
    """Initialize the orchestrator skeleton from the command line."""
    try:
        from src.deepagent import create_grrm_orchestrator, get_registered_subagent_names
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Could not import the orchestrator skeleton. Install the project dependencies first."
        ) from error

    orchestrator = create_grrm_orchestrator()
    registered_subagents = ", ".join(get_registered_subagent_names())
    print("GRRM orchestrator skeleton initialized.")
    print(f"Registered subagents: {registered_subagents}")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nUser> ")
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input.strip():
                continue
            
            response = orchestrator.invoke({"messages": [{"role": "user", "content": user_input}]})
            
            messages = response.get("messages", [])
            if messages:
                last_message = messages[-1]
                print(f"\nOrchestrator> {last_message.content}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
