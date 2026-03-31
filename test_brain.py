import os
from src.config import NovelWriterConfig
from src.orchestrator import GRRMOrchestrator
from langchain_core.messages import HumanMessage

def test_brain_router():
    config = NovelWriterConfig()
    orchestrator = GRRMOrchestrator(config)
    
    state = orchestrator.create_initial_state()
    state["messages"] = [HumanMessage(content="create a novel's seed for the dark fantasy genre based on the themes of the paradox of the human heart to wallow in feelings of hopelessness and self-loathing yet simultaneously dream of achieving truly great things.")]
    
    print("Invoking brain_router...")
    try:
        decision = orchestrator.brain_router.invoke(orchestrator._build_brain_messages(state), stream=False)
        print("Decision type:", type(decision))
        print("Decision:", decision)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_brain_router()