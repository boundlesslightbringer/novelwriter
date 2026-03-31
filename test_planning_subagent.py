import json
import os
from dotenv import load_dotenv
from src.config import NovelWriterConfig
from src.agents.workers import PlanningSubagent

def main() -> None:
    # Load environment variables
    load_dotenv()
    
    """Test the PlanningSubagent in isolation."""
    # Initialize configuration
    print("Initializing configuration...")
    config = NovelWriterConfig()
    
    # Initialize the Planning Subagent
    print("Initializing PlanningSubagent...")
    planning_subagent = PlanningSubagent(config)
    
    # Construct the mock state with the detailed orchestrator task
    mock_state = {
        "messages": [],
        "worker_history": [],
        "worker_request": {
            "worker": "planning_subagent",
            "task": "Generate a rich conceptual seed for a High Fantasy novel that explores what happens when high divinity comes into contact with baser material reality. Include: core thematic premise, central tension/conflict, tonal register, suggested narrative scope, key worldbuilding pillars, and 2–3 rough story endpoint possibilities. Make it evocative, philosophically layered, and generative — something a novelist can build a full world from.",
            "context": {},
            "reasoning": "Testing the planning subagent in isolation."
        }
    }
    
    # Invoke the subagent
    print("Invoking PlanningSubagent with mock state (this may take a moment)...")
    result_state = planning_subagent.invoke(mock_state)
    print(result_state)
    
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
    print("ARTIFACTS (Conceptual Seed):")
    print(json.dumps(artifacts, indent=2))
    print("="*80)

if __name__ == "__main__":
    main()
