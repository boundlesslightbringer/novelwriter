import os
import uuid
import pytest
from src.story_state_manager_subgraph import run_story_state_manager_subgraph
from src.world_bible_tools import (
    init_kg_db,
    add_kg_node,
    query_kg_nodes,
    query_kg_edges,
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
    suffix = uuid.uuid4().hex[:8]
    char_one = f"char_test_character_{suffix}"
    char_two = f"char_test_character_2_{suffix}"
    rel_id = f"rel_test_character_pair_{suffix}"

    # 1. Insert a Character node
    node_result = add_kg_node.invoke({
        "logical_id": char_one,
        "node_type": "Character",
        "properties": {"name": "Test Character"},
        "chapter": 1
    })
    assert f"Added node '{char_one}'" in node_result

    # 2. Verify it appears in query_kg_nodes
    query_result = query_kg_nodes.invoke({
        "query": {"type": "Character", "logical_id": char_one}
    })
    assert len(query_result) == 1
    assert query_result[0]["logical_id"] == char_one
    assert query_result[0]["properties"]["name"] == "Test Character"

    # 3. Insert a KNOWS edge
    # We need a second character to know
    add_kg_node.invoke({
        "logical_id": char_two,
        "node_type": "Character",
        "properties": {"name": "Test Character 2"},
        "chapter": 1
    })
    
    edge_result = add_kg_edge.invoke({
        "logical_id": rel_id,
        "edge_type": "KNOWS",
        "from_node": char_one,
        "to_node": char_two,
        "properties": {"relationship": "friends"},
        "chapter": 1
    })
    assert f"Added edge '{rel_id}'" in edge_result

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
    
    assert contradiction_result["has_contradictions"] is True
    assert len(contradiction_result["contradictions"]) > 0
    assert "Cannot update node 'char_non_existent_character'" in contradiction_result["contradictions"][0]


class _StubStoryStateManager:
    name = "story_state_manager"


def test_story_state_manager_phase1_subgraph_persists_writes():
    suffix = uuid.uuid4().hex[:8]
    char_one = f"char_phase1_arya_{suffix}"
    char_two = f"char_phase1_sansa_{suffix}"
    edge_id = f"rel_phase1_knows_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist accepted records to story state",
            "context": {
                "chapter_context": 3,
                "nodes_to_add": [
                    {
                        "logical_id": char_one,
                        "node_type": "Character",
                        "properties": {"name": "Arya"},
                    },
                    {
                        "logical_id": char_two,
                        "node_type": "Character",
                        "properties": {"name": "Sansa"},
                    },
                ],
                "edges_to_add": [
                    {
                        "logical_id": edge_id,
                        "edge_type": "KNOWS",
                        "from": char_one,
                        "to": char_two,
                        "properties": {"status": "KNOWS", "acquired_at_chapter": 3},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]

    assert payload["status"] == "success"
    assert payload["artifacts"]["operation"] == "write"
    assert payload["artifacts"]["status"] == "success"
    assert set(payload["artifacts"]["records_updated"]) == {char_one, char_two, edge_id}
    assert payload["artifacts"]["contradiction_record"]["has_contradictions"] is False

    node_docs = query_kg_nodes.invoke({"query": {"logical_id": {"$in": [char_one, char_two]}}})
    edge_docs = query_kg_edges.invoke({"query": {"logical_id": edge_id}})
    assert len(node_docs) == 2
    assert len(edge_docs) == 1


def test_story_state_manager_phase1_subgraph_blocks_contradictions():
    suffix = uuid.uuid4().hex[:8]
    missing_id = f"char_phase1_missing_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist accepted records to story state",
            "context": {
                "chapter_context": 4,
                "nodes_to_update": [
                    {
                        "logical_id": missing_id,
                        "updated_properties": {"name": "Ghost Update"},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]

    assert payload["status"] == "blocked"
    assert payload["artifacts"]["status"] == "blocked"
    assert payload["artifacts"]["records_updated"] == []
    assert payload["artifacts"]["contradiction_record"]["has_contradictions"] is True
    assert "Cannot update node" in payload["artifacts"]["contradiction_record"]["contradictions"][0]


def test_story_state_manager_phase2_batch_relationship_split():
    suffix = uuid.uuid4().hex[:8]
    char_a = f"char_phase2_a_{suffix}"
    char_b = f"char_phase2_b_{suffix}"
    char_c = f"char_phase2_c_{suffix}"
    existing_rel = f"rel_phase2_existing_{suffix}"
    new_rel = f"rel_phase2_new_{suffix}"

    add_kg_node.invoke(
        {"logical_id": char_a, "node_type": "Character", "properties": {"name": "A"}, "chapter": 5}
    )
    add_kg_node.invoke(
        {"logical_id": char_b, "node_type": "Character", "properties": {"name": "B"}, "chapter": 5}
    )
    add_kg_node.invoke(
        {"logical_id": char_c, "node_type": "Character", "properties": {"name": "C"}, "chapter": 5}
    )
    add_kg_edge.invoke(
        {
            "logical_id": existing_rel,
            "edge_type": "RELATIONSHIP",
            "from_node": char_a,
            "to_node": char_b,
            "properties": {"emotional_valence": "neutral", "power_dynamic": "balanced"},
            "chapter": 5,
        }
    )

    state = {
        "worker_request": {
            "task": "Persist batch relationship updates",
            "context": {
                "chapter_context": 6,
                "new_relationship_edges": [
                    {
                        "logical_id": new_rel,
                        "edge_type": "RELATIONSHIP",
                        "from": char_a,
                        "to": char_c,
                        "properties": {"emotional_valence": "positive", "power_dynamic": "balanced"},
                    }
                ],
                "updated_relationship_edges": [
                    {
                        "logical_id": existing_rel,
                        "updated_properties": {"emotional_valence": "hostile"},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    assert payload["status"] == "success"
    assert payload["artifacts"]["status"] == "success"
    assert set(payload["artifacts"]["records_updated"]) == {new_rel, existing_rel}
    assert payload["artifacts"]["records_failed"] == []

    new_rel_docs = query_kg_edges.invoke({"query": {"logical_id": new_rel}})
    existing_rel_docs = query_kg_edges.invoke({"query": {"logical_id": existing_rel}})
    assert len(new_rel_docs) == 1
    assert len(existing_rel_docs) == 1
    assert existing_rel_docs[0]["properties"]["emotional_valence"] == "hostile"


def test_story_state_manager_phase2_batch_duplicate_logical_ids_collapsed():
    """Same logical_id twice in one batch must not mark the run as failed (last record wins)."""
    suffix = uuid.uuid4().hex[:8]
    char_a = f"char_phase2_dup_a_{suffix}"
    char_b = f"char_phase2_dup_b_{suffix}"
    edge_dup = f"rel_phase2_dup_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist batch with duplicate logical_ids",
            "context": {
                "chapter_context": 8,
                "nodes_to_add": [
                    {
                        "logical_id": char_a,
                        "node_type": "Character",
                        "properties": {"name": "A first"},
                    },
                    {
                        "logical_id": char_a,
                        "node_type": "Character",
                        "properties": {"name": "A second wins"},
                    },
                    {"logical_id": char_b, "node_type": "Character", "properties": {"name": "B stable"}},
                ],
                "edges_to_add": [
                    {
                        "logical_id": edge_dup,
                        "edge_type": "KNOWS",
                        "from": char_a,
                        "to": char_b,
                        "properties": {"status": "KNOWS", "acquired_at_chapter": 8, "note": "a"},
                    },
                    {
                        "logical_id": edge_dup,
                        "edge_type": "KNOWS",
                        "from": char_a,
                        "to": char_b,
                        "properties": {"status": "KNOWS", "acquired_at_chapter": 8, "note": "b wins"},
                    },
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    artifacts = payload["artifacts"]

    assert payload["status"] == "success"
    assert artifacts["status"] == "success"
    assert artifacts["records_failed"] == []
    assert char_a in artifacts["records_updated"]
    assert char_b in artifacts["records_updated"]
    assert edge_dup in artifacts["records_updated"]

    node_docs = query_kg_nodes.invoke({"query": {"logical_id": char_a}})
    assert len(node_docs) == 1
    assert node_docs[0]["properties"]["name"] == "A second wins"

    edge_docs = query_kg_edges.invoke({"query": {"logical_id": edge_dup}})
    assert len(edge_docs) == 1
    assert edge_docs[0]["properties"]["note"] == "b wins"


def test_story_state_manager_phase2_batch_partial_failure_containment():
    suffix = uuid.uuid4().hex[:8]
    char_a = f"char_phase2_pf_a_{suffix}"
    char_b = f"char_phase2_pf_b_{suffix}"
    good_rel = f"rel_phase2_pf_good_{suffix}"
    bad_rel = f"rel_phase2_pf_bad_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist batch writes with partial failure",
            "context": {
                "chapter_context": 7,
                "nodes_to_add": [
                    {
                        "logical_id": char_a,
                        "node_type": "Character",
                        "properties": {"name": "Partial A"},
                    },
                    {
                        "logical_id": char_b,
                        "node_type": "Character",
                        "properties": {"name": "Partial B"},
                    },
                ],
                "edges_to_add": [
                    {
                        "logical_id": good_rel,
                        "edge_type": "KNOWS",
                        "from": char_a,
                        "to": char_b,
                        "properties": {"status": "KNOWS", "acquired_at_chapter": 7},
                    },
                    {
                        "logical_id": bad_rel,
                        "edge_type": "INVALID_EDGE_TYPE",
                        "from": char_a,
                        "to": char_b,
                        "properties": {"status": "KNOWS", "acquired_at_chapter": 7},
                    },
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    artifacts = payload["artifacts"]

    assert payload["status"] == "failed"
    assert artifacts["status"] == "failed"
    assert char_a in artifacts["records_updated"]
    assert char_b in artifacts["records_updated"]
    assert good_rel in artifacts["records_updated"]
    assert any(entry["logical_id"] == bad_rel for entry in artifacts["records_failed"])
    assert len(artifacts["records_failed"]) >= 1

    # Partial-failure containment: valid records are still persisted.
    node_docs = query_kg_nodes.invoke({"query": {"logical_id": {"$in": [char_a, char_b]}}})
    good_rel_docs = query_kg_edges.invoke({"query": {"logical_id": good_rel}})
    bad_rel_docs = query_kg_edges.invoke({"query": {"logical_id": bad_rel}})
    assert len(node_docs) == 2
    assert len(good_rel_docs) == 1
    assert len(bad_rel_docs) == 0


def test_story_state_manager_phase3_temporal_node_chain_versioning():
    suffix = uuid.uuid4().hex[:8]
    node_id = f"char_phase3_temporal_node_{suffix}"

    add_kg_node.invoke(
        {
            "logical_id": node_id,
            "node_type": "Character",
            "properties": {"name": "Before Update", "rank": "Scout"},
            "chapter": 10,
        }
    )

    state = {
        "worker_request": {
            "task": "Persist temporal node update",
            "context": {
                "chapter_context": 11,
                "nodes_to_update": [
                    {"logical_id": node_id, "updated_properties": {"name": "After Update", "rank": "Captain"}}
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    assert payload["status"] == "success"
    assert node_id in payload["artifacts"]["records_updated"]

    db = _get_db()
    all_versions = list(db.get_collection("nodes").find({"logical_id": node_id}, {"_id": 0}))
    assert len(all_versions) == 2
    retired = [doc for doc in all_versions if doc.get("valid_to") is not None]
    active = [doc for doc in all_versions if doc.get("valid_to") is None]
    assert len(retired) == 1
    assert len(active) == 1
    assert retired[0]["valid_to"] == 11
    assert active[0]["valid_from"] == 11
    assert active[0]["properties"]["name"] == "After Update"
    assert active[0]["properties"]["rank"] == "Captain"

    as_of_10 = query_kg_nodes.invoke({"query": {"logical_id": node_id}, "as_of_chapter": 10})
    as_of_11 = query_kg_nodes.invoke({"query": {"logical_id": node_id}, "as_of_chapter": 11})
    assert len(as_of_10) == 1
    assert as_of_10[0]["properties"]["name"] == "Before Update"
    assert len(as_of_11) == 1
    assert as_of_11[0]["properties"]["name"] == "After Update"


def test_story_state_manager_phase3_temporal_edge_chain_versioning():
    suffix = uuid.uuid4().hex[:8]
    char_from = f"char_phase3_edge_from_{suffix}"
    char_to = f"char_phase3_edge_to_{suffix}"
    edge_id = f"rel_phase3_temporal_edge_{suffix}"

    add_kg_node.invoke({"logical_id": char_from, "node_type": "Character", "properties": {"name": "From"}, "chapter": 12})
    add_kg_node.invoke({"logical_id": char_to, "node_type": "Character", "properties": {"name": "To"}, "chapter": 12})
    add_kg_edge.invoke(
        {
            "logical_id": edge_id,
            "edge_type": "RELATIONSHIP",
            "from_node": char_from,
            "to_node": char_to,
            "properties": {"emotional_valence": "neutral", "power_dynamic": "balanced"},
            "chapter": 12,
        }
    )

    state = {
        "worker_request": {
            "task": "Persist temporal edge update",
            "context": {
                "chapter_context": 13,
                "edges_to_update": [
                    {
                        "logical_id": edge_id,
                        "updated_properties": {"emotional_valence": "hostile"},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    assert payload["status"] == "success"
    assert edge_id in payload["artifacts"]["records_updated"]

    db = _get_db()
    all_versions = list(db.get_collection("edges").find({"logical_id": edge_id}, {"_id": 0}))
    assert len(all_versions) == 2
    retired = [doc for doc in all_versions if doc.get("valid_to") is not None]
    active = [doc for doc in all_versions if doc.get("valid_to") is None]
    assert len(retired) == 1
    assert len(active) == 1
    assert retired[0]["valid_to"] == 13
    assert active[0]["valid_from"] == 13
    assert active[0]["from"] == char_from
    assert active[0]["to"] == char_to
    assert active[0]["properties"]["emotional_valence"] == "hostile"

    as_of_12 = query_kg_edges.invoke({"query": {"logical_id": edge_id}, "as_of_chapter": 12})
    as_of_13 = query_kg_edges.invoke({"query": {"logical_id": edge_id}, "as_of_chapter": 13})
    assert len(as_of_12) == 1
    assert as_of_12[0]["properties"]["emotional_valence"] == "neutral"
    assert len(as_of_13) == 1
    assert as_of_13[0]["properties"]["emotional_valence"] == "hostile"


def test_story_state_manager_rejects_blank_edge_endpoints_pre_write():
    suffix = uuid.uuid4().hex[:8]
    char_a = f"char_blank_edge_a_{suffix}"
    char_b = f"char_blank_edge_b_{suffix}"
    invalid_edge = f"rel_blank_endpoint_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist writes with a blank edge endpoint",
            "context": {
                "chapter_context": 14,
                "nodes_to_add": [
                    {"logical_id": char_a, "node_type": "Character", "properties": {"name": "A"}},
                    {"logical_id": char_b, "node_type": "Character", "properties": {"name": "B"}},
                ],
                "edges_to_add": [
                    {
                        "logical_id": invalid_edge,
                        "edge_type": "KNOWS",
                        "from": char_a,
                        "to": "   ",
                        "properties": {"status": "KNOWS"},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    artifacts = payload["artifacts"]

    assert payload["status"] == "failed"
    assert char_a in artifacts["records_updated"]
    assert char_b in artifacts["records_updated"]
    assert any(
        entry["logical_id"] == invalid_edge and entry.get("reason") == "missing_endpoints"
        for entry in artifacts["records_failed"]
    )

    edge_docs = query_kg_edges.invoke({"query": {"logical_id": invalid_edge}})
    assert edge_docs == []


def test_story_state_manager_rejects_unsupported_edge_type_pre_write():
    suffix = uuid.uuid4().hex[:8]
    char_a = f"char_bad_edge_type_a_{suffix}"
    char_b = f"char_bad_edge_type_b_{suffix}"
    invalid_edge = f"rel_bad_type_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist writes with unsupported edge type",
            "context": {
                "chapter_context": 15,
                "nodes_to_add": [
                    {"logical_id": char_a, "node_type": "Character", "properties": {"name": "A"}},
                    {"logical_id": char_b, "node_type": "Character", "properties": {"name": "B"}},
                ],
                "edges_to_add": [
                    {
                        "logical_id": invalid_edge,
                        "edge_type": "MEMBER_OF",
                        "from": char_a,
                        "to": char_b,
                        "properties": {"relationship": "ally"},
                    }
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    artifacts = payload["artifacts"]

    assert payload["status"] == "failed"
    assert any(
        entry["logical_id"] == invalid_edge and entry.get("reason") == "invalid_edge_type"
        for entry in artifacts["records_failed"]
    )
    assert query_kg_edges.invoke({"query": {"logical_id": invalid_edge}}) == []


def test_story_state_manager_surfaces_schema_validation_failures():
    suffix = uuid.uuid4().hex[:8]
    valid_node = f"char_schema_valid_{suffix}"
    invalid_node = f"node_schema_invalid_{suffix}"

    state = {
        "worker_request": {
            "task": "Persist writes with one schema-invalid node",
            "context": {
                "chapter_context": 16,
                "nodes_to_add": [
                    {"logical_id": valid_node, "node_type": "Character", "properties": {"name": "Valid"}},
                    {"logical_id": invalid_node, "node_type": "StorySeed", "properties": {"name": "Invalid Type"}},
                ],
            },
        }
    }

    result = run_story_state_manager_subgraph(_StubStoryStateManager(), state)
    payload = result["latest_worker_result"]["result"]
    artifacts = payload["artifacts"]

    assert payload["status"] == "failed"
    assert valid_node in artifacts["records_updated"]
    assert any(
        entry["logical_id"] == invalid_node and entry.get("reason") == "schema_validation_failed"
        for entry in artifacts["records_failed"]
    )
    valid_docs = query_kg_nodes.invoke({"query": {"logical_id": valid_node}})
    invalid_docs = query_kg_nodes.invoke({"query": {"logical_id": invalid_node}})
    assert len(valid_docs) == 1
    assert invalid_docs == []
