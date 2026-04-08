import os
import pytest
from src.world_bible_tools import (
    init_kg_db,
    add_kg_node,
    query_kg_nodes,
    add_kg_edge,
    detect_kg_contradiction,
    _get_db,
)

# Use a test database
TEST_DB_NAME = "novelwriter_kg"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Set environment variable to use the test database
    os.environ["MONGODB_DB_NAME"] = TEST_DB_NAME
    
    # Initialize the database and collections
    init_kg_db(TEST_DB_NAME)
    
    yield
    
    # Teardown: we don't drop the database anymore since it might be the main one
    # db = _get_db()
    # db.client.drop_database(TEST_DB_NAME)

def test_story_state_manager_infrastructure():
    # 1. Insert a Character node
    node_result = add_kg_node.invoke({
        "logical_id": "char_test_character",
        "node_type": "Character",
        "properties": {"name": "Test Character"},
        "chapter": 1
    })
    assert "Added node 'char_test_character'" in node_result

    # 2. Verify it appears in query_kg_nodes
    query_result = query_kg_nodes.invoke({
        "query": {"type": "Character", "logical_id": "char_test_character"}
    })
    assert len(query_result) == 1
    assert query_result[0]["logical_id"] == "char_test_character"
    assert query_result[0]["properties"]["name"] == "Test Character"

    # 3. Insert a KNOWS edge
    # We need a second character to know
    add_kg_node.invoke({
        "logical_id": "char_test_character_2",
        "node_type": "Character",
        "properties": {"name": "Test Character 2"},
        "chapter": 1
    })
    
    edge_result = add_kg_edge.invoke({
        "logical_id": "rel_test_character_test_character_2",
        "edge_type": "KNOWS",
        "from_node": "char_test_character",
        "to_node": "char_test_character_2",
        "properties": {"relationship": "friends"},
        "chapter": 1
    })
    assert "Added edge 'rel_test_character_test_character_2'" in edge_result

    # 4. Verify detect_kg_contradiction returns a BLOCKED result for a non-existent node
    proposed_updates = [
        {
            "action": "update_node",
            "logical_id": "char_non_existent_character",
            "properties": {"name": "Ghost"}
        }
    ]
    contradiction_result = detect_kg_contradiction.invoke({
        "proposed_updates": proposed_updates,
        "chapter": 1
    })
    
    print(contradiction_result)
    assert contradiction_result["has_contradictions"] is True
    assert len(contradiction_result["contradictions"]) > 0
    assert "Cannot update node 'char_non_existent_character'" in contradiction_result["contradictions"][0]
