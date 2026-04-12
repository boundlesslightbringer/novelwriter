import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.world_bible_tools import init_kg_db, add_kg_node, add_kg_edge

def main():
    try:
        print("Initializing DB...")
        print(init_kg_db("test_db"))
    except Exception as e:
        print(f"Error initializing DB: {e}")

    try:
        print("Adding node...")
        # add_kg_node is a LangChain tool, so we call it with .invoke or directly if it's a function.
        # Let's check its type.
        if hasattr(add_kg_node, "invoke"):
            print(add_kg_node.invoke({"logical_id": "test_node_1", "node_type": "Character", "properties": {"name": "Test"}, "chapter": 1}))
        else:
            print(add_kg_node("test_node_1", "Character", {"name": "Test"}, 1))
    except Exception as e:
        print(f"Error adding node: {e}")

if __name__ == "__main__":
    main()
