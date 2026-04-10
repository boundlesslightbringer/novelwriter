import uuid
from typing import Any, Dict

from src.world_bible_tools import _get_edges, _get_nodes


def run_node_temporal_update_chain(logical_id: str, updated_properties: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    """Sequential temporal update chain: active check -> retire -> insert -> reread."""
    nodes = _get_nodes()
    active_node = nodes.find_one({"logical_id": logical_id, "valid_to": None})
    if not active_node:
        return {
            "ok": False,
            "step": "assert_active_exists",
            "error": f"No active node found with logical_id '{logical_id}'.",
        }

    retire_result = nodes.update_one({"_id": active_node["_id"]}, {"$set": {"valid_to": chapter}})
    if retire_result.modified_count != 1:
        return {
            "ok": False,
            "step": "retire_active",
            "error": f"Failed to retire active node '{logical_id}'.",
        }

    new_properties = dict(active_node.get("properties", {}))
    new_properties.update(updated_properties)
    new_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": active_node["type"],
        "valid_from": chapter,
        "valid_to": None,
        "properties": new_properties,
    }
    nodes.insert_one(new_doc)

    reread_doc = nodes.find_one({"logical_id": logical_id, "valid_to": None}, {"_id": 0})
    if not reread_doc:
        return {
            "ok": False,
            "step": "reread_verify",
            "error": f"Failed to verify active node after update for '{logical_id}'.",
        }

    return {"ok": True, "step": "reread_verify", "error": "", "active_record": reread_doc}


def run_edge_temporal_update_chain(logical_id: str, updated_properties: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    """Sequential temporal update chain: active check -> retire -> insert -> reread."""
    edges = _get_edges()
    active_edge = edges.find_one({"logical_id": logical_id, "valid_to": None})
    if not active_edge:
        return {
            "ok": False,
            "step": "assert_active_exists",
            "error": f"No active edge found with logical_id '{logical_id}'.",
        }

    retire_result = edges.update_one({"_id": active_edge["_id"]}, {"$set": {"valid_to": chapter}})
    if retire_result.modified_count != 1:
        return {
            "ok": False,
            "step": "retire_active",
            "error": f"Failed to retire active edge '{logical_id}'.",
        }

    new_properties = dict(active_edge.get("properties", {}))
    new_properties.update(updated_properties)
    new_doc = {
        "_id": str(uuid.uuid4()),
        "logical_id": logical_id,
        "type": active_edge["type"],
        "from": active_edge["from"],
        "to": active_edge["to"],
        "valid_from": chapter,
        "valid_to": None,
        "properties": new_properties,
    }
    edges.insert_one(new_doc)

    reread_doc = edges.find_one({"logical_id": logical_id, "valid_to": None}, {"_id": 0})
    if not reread_doc:
        return {
            "ok": False,
            "step": "reread_verify",
            "error": f"Failed to verify active edge after update for '{logical_id}'.",
        }

    return {"ok": True, "step": "reread_verify", "error": "", "active_record": reread_doc}
