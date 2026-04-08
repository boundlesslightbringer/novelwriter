import json
import os
from dotenv import load_dotenv
from src.config import NovelWriterConfig
from src.agents.workers import CharacterSubagent

def main() -> None:
    # Load environment variables
    load_dotenv()
    
    """Test the CharacterSubagent in isolation."""
    # Initialize configuration
    print("Initializing configuration...")
    config = NovelWriterConfig()
    
    # Initialize the Character Subagent
    print("Initializing CharacterSubagent...")
    character_subagent = CharacterSubagent(config)
    
    # Construct the mock state with the detailed orchestrator task
    mock_state = {
        "messages": [],
        "worker_history": [],
        "worker_request": {
            "worker": "character_subagent",
            "task": "Generate a character concept for a rogue who steals magic artifacts but is cursed to feel the emotions of the original owners. Focus on their core contradiction and a one-paragraph sketch.",
            "context": {},
            "reasoning": "Testing the character subagent in isolation."
        }
    }
    
    # Invoke the subagent
    print("Invoking CharacterSubagent with mock state (this may take a moment)...")
    result_state = character_subagent.invoke(mock_state)
    
    # Extract results
    latest_result = result_state.get("latest_worker_result", {})
    result_data = latest_result.get("result", {})
    
    status = result_data.get("status", "UNKNOWN")
    summary = result_data.get("summary", "No summary provided.")
    artifacts = result_data.get("artifacts", {})
    
    # Print results
    print("\n" + "="*80)
    print(f"STATUS: {status}")
    print(f"SUMMARY: {summary}")
    print("="*80)
    print("ARTIFACTS (Character Concept):")
    print(json.dumps(artifacts, indent=2))
    print("="*80)

if __name__ == "__main__":
    main()
