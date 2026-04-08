"""
World Bible Tools - MongoDB Knowledge Graph backend for the GRRM Novel Writer.

This module implements the Knowledge Graph schema defined in `kg_schema_design.md`.
It uses a two-collection design (`nodes` and `edges`) with temporal versioning
(`valid_from` and `valid_to`) to maintain historical state immutability.
"""

import os
import uuid
from typing import Any, List, Optional

from langchain.tools import tool
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.kg_models import (
    AddEdgeArgs,
    AddNodeArgs,
    DetectContradictionArgs,
    QueryEdgesArgs,
    QueryNodesArgs,
    UpdateEdgeArgs,
    UpdateNodeArgs,
)


def _get_db() -> Database:
    """Get the MongoDB database instance.

    Returns:
        The MongoDB database for the novelwriter project.
    """
    client: MongoClient = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
    db_name = os.environ.get("MONGODB_DB_NAME", "novelwriter_kg")
    return client.get_database(db_name)


def _get_nodes() -> Collection:
    return _get_db().get_collection("nodes")


def _get_edges() -> Collection:
    return _get_db().get_collection("edges")


def init_kg_db(db_name: str) -> str:
    """Initialize the MongoDB Knowledge Graph database and create required indexes.

    Args:
        db_name: The name of the database to initialize.

    Returns:
        A confirmation message indicating successful initialization.
    """
    client: MongoClient = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
    db = client.get_database(db_name)

    nodes_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["logical_id", "type", "valid_from", "properties"],
            "properties": {
                "_id": {"bsonType": "string"},
                "logical_id": {"bsonType": "string"},
                "type": {"bsonType": "string"},
                "valid_from": {"bsonType": "int"},
                "valid_to": {"bsonType": ["int", "null"]},
                "properties": {"bsonType": "object"},
            },
        }
    }

    edges_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["logical_id", "type", "from", "to", "valid_from", "properties"],
            "properties": {
                "_id": {"bsonType": "string"},
                "logical_id": {"bsonType": "string"},
                "type": {"bsonType": "string"},
                "from": {"bsonType": "string"},
                "to": {"bsonType": "string"},
                "valid_from": {"bsonType": "int"},
                "valid_to": {"bsonType": ["int", "null"]},
                "properties": {"bsonType": "object"},
            },
        }
    }

    if "nodes" not in db.list_collection_names():
        db.create_collection("nodes", validator=nodes_schema)
    else:
        db.command("collMod", "nodes", validator=nodes_schema)

    if "edges" not in db.list_collection_names():
        db.create_collection("edges", validator=edges_schema)
    else:
        db.command("collMod", "edges", validator=edges_schema)

    nodes = db.get_collection("nodes")
    edges = db.get_collection("edges")

    # Create recommended indexes for nodes
    nodes.create_index([("type", 1), ("valid_to", 1)])
    nodes.create_index([("logical_id", 1), ("valid_to", 1)])

    # Create recommended indexes for edges
    edges.create_index([("from", 1), ("type", 1), ("valid_to", 1)])
    edges.create_index([("to", 1), ("type", 1), ("valid_to", 1)])
    edges.create_index([("type", 1), ("valid_to", 1)])
    edges.create_index([("logical_id", 1), ("valid_to", 1)])

    return f"Knowledge Graph database '{db_name}' initialized with required schemas and indexes."


@tool(args_schema=QueryNodesArgs)
def query_kg_nodes(query: dict[str, Any], as_of_chapter: int | None = None, sort: dict[str, int] | None = None) -> list[dict[str, Any]]:
    """Query nodes in the Knowledge Graph.

    Args:
        query: MongoDB query dictionary (e.g., {"type": "Character", "properties.faction": "Stark"}).
        as_of_chapter: If provided, retrieves the state of nodes as they existed at this chapter.
            If None, retrieves the currently active nodes (valid_to is null).
        sort: Optional sort dictionary (e.g., {"properties.chapter_number": 1}).

    Returns:
        A list of matching node documents.
    """
    nodes = _get_nodes()
    temporal_query = dict(query)

    if as_of_chapter is not None:
        temporal_query["valid_from"] = {"$lte": as_of_chapter}
        temporal_query["$or"] = [{"valid_to": None}, {"valid_to": {"$gt": as_of_chapter}}]
    else:
        temporal_query["valid_to"] = None

    cursor = nodes.find(temporal_query, {"_id": 0})
    if sort:
        cursor = cursor.sort(list(sort.items()))
    return list(cursor)


@tool(args_schema=QueryEdgesArgs)
def query_kg_edges(query: dict[str, Any], as_of_chapter: int | None = None, sort: dict[str, int] | None = None) -> list[dict[str, Any]]:
    """Query edges in the Knowledge Graph.

    Args:
        query: MongoDB query dictionary (e.g., {"type": "KNOWS", "from": "char_arya"}).
        as_of_chapter: If provided, retrieves the state of edges as they existed at this chapter.
            If None, retrieves the currently active edges (valid_to is null).
        sort: Optional sort dictionary (e.g., {"properties.chapter_number": 1}).

    Returns:
        A list of matching edge documents.
    """
    edges = _get_edges()
    temporal_query = dict(query)

    if as_of_chapter is not None:
        temporal_query["valid_from"] = {"$lte": as_of_chapter}
        temporal_query["$or"] = [{"valid_to": None}, {"valid_to": {"$gt": as_of_chapter}}]
    else:
        temporal_query["valid_to"] = None

    cursor = edges.find(temporal_query, {"_id": 0})
    if sort:
        cursor = cursor.sort(list(sort.items()))
    return list(cursor)


@tool(args_schema=AddNodeArgs)
def add_kg_node(logical_id: str, node_type: str, properties: dict[str, Any], chapter: int) -> str:
    """Add a new node to the Knowledge Graph.

    Args:
        logical_id: The stable identifier for the entity (e.g., "char_jon_snow").
        node_type: The type of node (e.g., "Character", "Location").
        properties: The type-specific attributes of the node.
        chapter: The chapter number when this node becomes active.

    Returns:
        A confirmation message.
    """
    nodes = _get_nodes()
    node_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": node_type,
        "valid_from": chapter,
        "valid_to": None,
        "properties": properties,
    }
    nodes.insert_one(node_doc)
    return f"Added node '{logical_id}' of type '{node_type}' at chapter {chapter}."


@tool(args_schema=UpdateNodeArgs)
def update_kg_node(logical_id: str, updated_properties: dict[str, Any], chapter: int) -> str:
    """Update an existing node using temporal versioning.

    Retires the currently active node state and creates a new active state with
    the updated properties.

    Args:
        logical_id: The stable identifier for the entity.
        updated_properties: The new properties to apply (merged with existing).
        chapter: The chapter number when this update occurs.

    Returns:
        A confirmation message.
    """
    nodes = _get_nodes()
    active_node = nodes.find_one({"logical_id": logical_id, "valid_to": None})

    if not active_node:
        return f"Error: No active node found with logical_id '{logical_id}'."

    # Retire the old node
    nodes.update_one({"_id": active_node["_id"]}, {"$set": {"valid_to": chapter}})

    # Create the new node
    new_properties = dict(active_node["properties"])
    new_properties.update(updated_properties)

    new_node_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": active_node["type"],
        "valid_from": chapter,
        "valid_to": None,
        "properties": new_properties,
    }
    nodes.insert_one(new_node_doc)
    return f"Updated node '{logical_id}' at chapter {chapter}."


@tool(args_schema=AddEdgeArgs)
def add_kg_edge(
    logical_id: str,
    edge_type: str,
    from_node: str,
    to_node: str,
    properties: dict[str, Any],
    chapter: int,
) -> str:
    """Add a new edge to the Knowledge Graph.

    Args:
        logical_id: The stable identifier for the relationship.
        edge_type: The type of relationship (e.g., "KNOWS", "LOCATED_AT").
        from_node: The logical_id of the source node.
        to_node: The logical_id of the target node.
        properties: The relationship-specific attributes.
        chapter: The chapter number when this edge becomes active.

    Returns:
        A confirmation message.
    """
    edges = _get_edges()
    edge_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": edge_type,
        "from": from_node,
        "to": to_node,
        "valid_from": chapter,
        "valid_to": None,
        "properties": properties,
    }
    edges.insert_one(edge_doc)
    return f"Added edge '{logical_id}' of type '{edge_type}' from '{from_node}' to '{to_node}' at chapter {chapter}."


@tool(args_schema=UpdateEdgeArgs)
def update_kg_edge(logical_id: str, updated_properties: dict[str, Any], chapter: int) -> str:
    """Update an existing edge using temporal versioning.

    Retires the currently active edge state and creates a new active state with
    the updated properties.

    Args:
        logical_id: The stable identifier for the relationship.
        updated_properties: The new properties to apply (merged with existing).
        chapter: The chapter number when this update occurs.

    Returns:
        A confirmation message.
    """
    edges = _get_edges()
    active_edge = edges.find_one({"logical_id": logical_id, "valid_to": None})

    if not active_edge:
        return f"Error: No active edge found with logical_id '{logical_id}'."

    # Retire the old edge
    edges.update_one({"_id": active_edge["_id"]}, {"$set": {"valid_to": chapter}})

    # Create the new edge
    new_properties = dict(active_edge["properties"])
    new_properties.update(updated_properties)

    new_edge_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": active_edge["type"],
        "from": active_edge["from"],
        "to": active_edge["to"],
        "valid_from": chapter,
        "valid_to": None,
        "properties": new_properties,
    }
    edges.insert_one(new_edge_doc)
    return f"Updated edge '{logical_id}' at chapter {chapter}."


@tool(args_schema=DetectContradictionArgs)
def detect_kg_contradiction(proposed_updates: list[dict[str, Any]], chapter: int) -> dict[str, Any]:
    """Check if proposed node/edge updates conflict with established graph constraints.

    This tool acts as a safety gate before the World Bible Manager commits new
    writes to the graph. It ensures that new nodes or edges do not violate
    established physical, logical, or temporal constraints against the active state.

    Args:
        proposed_updates: A list of proposed update dictionaries. Each dictionary
            should specify the type of update ('add_node', 'update_node',
            'add_edge', 'update_edge') and the relevant parameters.
        chapter: The chapter number at which the updates are proposed.

    Returns:
        A dictionary containing the contradiction report. If 'has_contradictions'
        is False, the updates are safe to proceed.
    """
    # This is a stub implementation. In a full system, this would evaluate the
    # proposed updates against the current graph state (where valid_to is None)
    # to check for location/travel constraints, knowledge constraints, state
    # exclusivity (e.g., a character can't be in two places at once), etc.

    contradictions = []

    # Example generic check: ensure we aren't updating a non-existent logical_id
    nodes = _get_nodes()
    edges = _get_edges()

    for update in proposed_updates:
        action = update.action
        logical_id = update.logical_id

        if action == "update_node":
            if not nodes.find_one({"logical_id": logical_id, "valid_to": None}):
                contradictions.append(f"Cannot update node '{logical_id}': no active node found.")
        elif action == "update_edge":
            if not edges.find_one({"logical_id": logical_id, "valid_to": None}):
                contradictions.append(f"Cannot update edge '{logical_id}': no active edge found.")

    return {
        "has_contradictions": len(contradictions) > 0,
        "contradictions": contradictions,
        "can_proceed": len(contradictions) == 0,
    }
