"""
Integration test: runs the real character integration chain (Vertex / Gemini).

Requires working Application Default Credentials and Vertex AI permission
``aiplatform.endpoints.predict`` on the configured model (see ORCHESTRATOR_SPEC §13.3).
If you see ``403 PERMISSION_DENIED``, fix IAM / project / model availability.

Run with output visible:
  uv run pytest test_character_integration_chain.py -s -v -m integration
"""

import json
import os
from typing import Any

import pytest

from src.agents.workers import CharacterSubagent
from src.config import NovelWriterConfig
from src.world_bible_tools import _get_db, add_kg_edge, add_kg_node, init_kg_db, query_kg_edges, query_kg_nodes


def _edge_endpoints(edge: dict[str, Any]) -> tuple[str, str]:
    """Normalize skill/LLM edge dicts to (from_id, to_id)."""
    from_id = edge.get("from_node") or edge.get("from")
    to_id = edge.get("to_node") or edge.get("to")
    if not from_id or not to_id:
        raise AssertionError(f"Edge missing from/to: {edge}")
    return str(from_id), str(to_id)


def _knows_status(edge: dict[str, Any]) -> str:
    props = edge.get("properties") or {}
    status = props.get("status") or ""
    return str(status).strip().upper()


@pytest.fixture(autouse=True)
def setup_test_db() -> None:
    os.environ["MONGODB_DB_NAME"] = "novelwriter_test_kg"
    init_kg_db("novelwriter_test_kg")
    db = _get_db()
    db.nodes.delete_many({})
    db.edges.delete_many({})

    add_kg_node.invoke(
        {
            "logical_id": "char_alice",
            "node_type": "Character",
            "properties": {
                "full_name": "Alice",
                "core_desire": "To uncover the truth about the ancient ruins.",
                "core_fear": "Being forgotten by history.",
                "core_wound": "Her mentor betrayed her.",
                "self_deception": "She believes she doesn't need anyone's help.",
                "response_patterns": {"betrayal": "Withdrawal and intense suspicion."},
            },
            "chapter": 0,
        }
    )
    add_kg_node.invoke(
        {
            "logical_id": "char_bob",
            "node_type": "Character",
            "properties": {
                "full_name": "Bob",
                "core_desire": "To protect the secrets of the ancient ruins at all costs.",
                "core_fear": "Failing his ancestors.",
                "core_wound": "He accidentally caused the destruction of a sacred artifact.",
                "self_deception": "He believes violence is always justified if it protects the ruins.",
                "response_patterns": {"betrayal": "Immediate retaliation."},
            },
            "chapter": 0,
        }
    )

    yield

    db.nodes.delete_many({})
    db.edges.delete_many({})


@pytest.mark.integration
def test_character_integration_chain() -> None:
    character_ids = ["char_alice", "char_bob"]
    chapter = 0

    config = NovelWriterConfig()
    subagent = CharacterSubagent(config)

    state = {
        "worker_request": {
            "task": "Integrate Alice and Bob",
            "context": {
                "skill": "character-integration",
                "character_ids": character_ids,
                "chapter_context": chapter,
            },
        },
        "messages": [],
        "worker_history": [],
    }

    print("\n=== Phase: invoke CharacterSubagent (real LLM integration chain) ===")
    result = subagent.invoke(state)

    latest_result = result.get("latest_worker_result", {})
    assert latest_result, "Worker result is empty"

    structured_result = latest_result.get("result", {})
    status = structured_result.get("status")
    artifacts = structured_result.get("artifacts", {})

    print(f"\nWorker status: {status}")
    if status != "success":
        print(f"Failure detail: {json.dumps(artifacts, indent=2, default=str)}")
    assert status == "success", f"Worker failed: {artifacts.get('error', artifacts)}"

    print("\n=== Full artifacts (truncated strings for readability) ===")
    print(json.dumps(artifacts, indent=2, default=str)[:12000])

    knowledge = artifacts.get("knowledge_matrix_expansions") or {}
    relationships = artifacts.get("relationship_records") or {}

    assert knowledge, "knowledge_matrix_expansions is empty"
    assert relationships, "relationship_records is empty"

    new_knowledge_items = knowledge.get("new_knowledge_items") or []
    new_knows_edges = knowledge.get("new_knows_edges") or []
    new_rel_edges = relationships.get("new_relationship_edges") or []
    updated_rel_edges = relationships.get("updated_relationship_edges") or []

    # Non-empty combined artifacts (test gate)
    assert new_knowledge_items, "new_knowledge_items is empty"
    assert new_knows_edges, "new_knows_edges is empty"
    assert new_rel_edges, "new_relationship_edges is empty"
    print(f"\nupdated_relationship_edges count (may be empty): {len(updated_rel_edges)}")

    print("\n=== Phase: persist expansion records to KG (observability) ===")
    for ki in new_knowledge_items:
        lid = ki.get("logical_id")
        ntype = ki.get("node_type", "KnowledgeItem")
        props = ki.get("properties") or {}
        ch = int(ki.get("chapter", chapter))
        print(f"  add_kg_node KnowledgeItem {lid}")
        add_kg_node.invoke({"logical_id": lid, "node_type": ntype, "properties": props, "chapter": ch})

    for edge in new_knows_edges:
        fr, to = _edge_endpoints(edge)
        eid = edge.get("logical_id", "edge_unknown")
        et = edge.get("edge_type", "KNOWS")
        props = edge.get("properties") or {}
        ch = int(edge.get("chapter", chapter))
        print(f"  add_kg_edge KNOWS {eid}: {fr} -> {to} status={props.get('status')}")
        add_kg_edge.invoke(
            {
                "logical_id": eid,
                "edge_type": et,
                "from_node": fr,
                "to_node": to,
                "properties": props,
                "chapter": ch,
            }
        )

    for edge in relationships.get("new_relationship_edges") or []:
        fr, to = _edge_endpoints(edge)
        eid = edge.get("logical_id", "rel_unknown")
        props = edge.get("properties") or {}
        ch = int(edge.get("chapter", chapter))
        print(f"  add_kg_edge RELATIONSHIP {eid}: {fr} -> {to}")
        add_kg_edge.invoke(
            {
                "logical_id": eid,
                "edge_type": "RELATIONSHIP",
                "from_node": fr,
                "to_node": to,
                "properties": props,
                "chapter": ch,
            }
        )

    print("\n=== Phase: query KG after writes ===")
    db_ki = query_kg_nodes.invoke({"query": {"type": "KnowledgeItem"}})
    print(f"KnowledgeItem count: {len(db_ki)}")
    for doc in db_ki:
        print(f"  {doc.get('logical_id')}: {doc.get('properties')}")

    db_knows = query_kg_edges.invoke({"query": {"type": "KNOWS"}})
    print(f"KNOWS edge count: {len(db_knows)}")
    for doc in db_knows:
        st = (doc.get("properties") or {}).get("status", "?")
        print(f"  {doc.get('logical_id')}: {doc.get('from')} -> {doc.get('to')} [{st}]")

    db_rel = query_kg_edges.invoke({"query": {"type": "RELATIONSHIP"}})
    print(f"RELATIONSHIP edge count: {len(db_rel)}")
    for doc in db_rel:
        ev = (doc.get("properties") or {}).get("emotional_valence", "?")
        print(f"  {doc.get('logical_id')}: {doc.get('from')} -> {doc.get('to')} [{ev}]")

    # --- Test gate: KNOWS <-> DOES NOT KNOW mirror for the two-character cohort ---
    id_set = set(character_ids)
    by_item: dict[str, dict[str, str]] = {}
    for edge in new_knows_edges:
        fr, to = _edge_endpoints(edge)
        if fr not in id_set:
            continue
        st = _knows_status(edge)
        by_item.setdefault(to, {})[fr] = st

    for ki_id, per_char in by_item.items():
        for a in character_ids:
            other = next((c for c in character_ids if c != a), None)
            if other is None:
                continue
            if per_char.get(a) == "KNOWS":
                assert per_char.get(other) == "DOES NOT KNOW", (
                    f"Cross-ref: for KnowledgeItem {ki_id}, {a} has KNOWS but {other} "
                    f"does not have DOES NOT KNOW (got {per_char!r})"
                )

    # --- Test gate: A->B vs B->A asymmetric (not identical property payloads) ---
    rel_by_dir: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in relationships.get("new_relationship_edges") or []:
        fr, to = _edge_endpoints(edge)
        if fr in id_set and to in id_set:
            rel_by_dir[(fr, to)] = edge.get("properties") or {}

    ab = rel_by_dir.get(("char_alice", "char_bob"))
    ba = rel_by_dir.get(("char_bob", "char_alice"))
    assert ab is not None, "Missing Alice -> Bob RELATIONSHIP in new_relationship_edges"
    assert ba is not None, "Missing Bob -> Alice RELATIONSHIP in new_relationship_edges"
    assert json.dumps(ab, sort_keys=True) != json.dumps(ba, sort_keys=True), (
        "RELATIONSHIP A->B and B->A properties are identical (expected asymmetric)"
    )

    print("\n=== Test gate passed ===\n")
