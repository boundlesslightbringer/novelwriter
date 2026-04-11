from src.brain_persistence_mapper import PersistPayloadMapper


def test_mapper_builds_seed_and_thread_payload():
    mapper = PersistPayloadMapper()
    latest_worker_result = {
        "worker": "planning_subagent",
        "task": "Find a seed",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Seed generated.",
            "artifacts": {
                "seed_document": {"seed": "A fractured crown"},
                "plot_thread_seeds": [
                    {
                        "logical_id": "thread_crown_conflict",
                        "node_type": "PlotThread",
                        "properties": {"name": "Crown conflict"},
                    }
                ],
            },
        },
    }

    mapped = mapper.build_context(latest_worker_result)

    assert mapped.has_payload is True
    assert mapped.context["chapter_context"] == 1
    node_ids = {entry["logical_id"] for entry in mapped.context["nodes_to_add"]}
    assert "thread_crown_conflict" in node_ids
    assert any(node_id.startswith("thread_seed_") for node_id in node_ids)


def test_mapper_builds_character_integration_records():
    mapper = PersistPayloadMapper()
    latest_worker_result = {
        "worker": "character_subagent",
        "task": "Run character integration",
        "context": {"chapter_context": 4},
        "result": {
            "status": "success",
            "summary": "Integration complete.",
            "artifacts": {
                "knowledge_matrix_expansions": {
                    "new_knowledge_items": [
                        {
                            "logical_id": "ki_secret_passage",
                            "node_type": "KnowledgeItem",
                            "properties": {"name": "Secret passage"},
                        }
                    ],
                    "new_knows_edges": [
                        {
                            "logical_id": "knows_arya_secret_passage",
                            "edge_type": "KNOWS",
                            "from": "char_arya",
                            "to": "ki_secret_passage",
                            "properties": {"status": "KNOWS"},
                        }
                    ],
                },
                "relationship_records": {
                    "new_relationship_edges": [
                        {
                            "logical_id": "rel_arya_sansa",
                            "edge_type": "RELATIONSHIP",
                            "from": "char_arya",
                            "to": "char_sansa",
                            "properties": {"power_dynamic": "contested"},
                        }
                    ],
                    "updated_relationship_edges": [
                        {
                            "logical_id": "rel_sansa_arya",
                            "updated_properties": {"emotional_valence": "strained"},
                        }
                    ],
                },
            },
        },
    }

    mapped = mapper.build_context(latest_worker_result)

    assert mapped.has_payload is True
    assert len(mapped.context["nodes_to_add"]) == 1
    assert len(mapped.context["edges_to_add"]) == 2
    assert len(mapped.context["edges_to_update"]) == 1


def test_mapper_skips_non_kg_node_type_in_explicit_nodes_to_add() -> None:
    """LLMs sometimes emit fantasy types in nodes_to_add; mapper must not forward them to add_kg_node."""
    mapper = PersistPayloadMapper()
    latest_worker_result = {
        "worker": "planning_subagent",
        "task": "Run finding-a-seed",
        "context": {"chapter_context": 1},
        "result": {
            "status": "success",
            "summary": "Seed generated.",
            "artifacts": {
                "seed_document": {"seed": "A fractured crown"},
                "nodes_to_add": [
                    {
                        "logical_id": "node_1",
                        "node_type": "StorySeed",
                        "properties": {"name": "Hallucinated seed node"},
                        "chapter": 1,
                    }
                ],
            },
        },
    }
    mapped = mapper.build_context(latest_worker_result)
    assert mapped.has_payload is True
    assert all(n.get("node_type") != "StorySeed" for n in mapped.context.get("nodes_to_add", []))
    assert any("Skipped malformed node add" in err for err in mapped.errors)


def test_mapper_builds_voice_profile_update():
    mapper = PersistPayloadMapper()
    latest_worker_result = {
        "worker": "character_subagent",
        "task": "Generate voice profile",
        "context": {"chapter_context": 5},
        "result": {
            "status": "success",
            "summary": "Voice profile generated.",
            "artifacts": {
                "character_id": "char_jon_snow",
                "voice_profile": {"vocabulary_range": {"lexical_register": "lean"}},
            },
        },
    }

    mapped = mapper.build_context(latest_worker_result)

    assert mapped.has_payload is True
    assert len(mapped.context["nodes_to_update"]) == 1
    assert mapped.context["nodes_to_update"][0]["logical_id"] == "char_jon_snow"
    assert mapped.context["nodes_to_update"][0]["updated_properties"]["voice_profile"]["vocabulary_range"][
        "lexical_register"
    ] == "lean"
