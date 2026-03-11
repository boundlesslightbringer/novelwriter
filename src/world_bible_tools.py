"""
World Bible Tools - JSONL-based filesystem backend for the GRRM Novel Writer.

The orchestrator appends operations to the JSONL file. Humans can edit any entry.
Each line is independently parseable. Current state is computed by replaying operations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from datetime import datetime, timezone
from copy import deepcopy
from langchain.tools import tool

WORLD_BIBLE_PATH = Path("data/world_bible.jsonl")
SNAPSHOTS_DIR = Path("data/snapshots")


def _ensure_paths():
    """Ensure required directories exist."""
    WORLD_BIBLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_nested_value(data: dict, path: str) -> Any:
    """Get value at dot-notation path (e.g., 'modules.1_character_state.1.1_character_directory')."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _set_nested_value(data: dict, path: str, value: Any) -> None:
    """Set value at dot-notation path, creating intermediate dicts as needed."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


def _apply_operation(state: dict, entry: dict) -> dict:
    """Apply a single changelog entry to the state."""
    op = entry.get("operation", "SET")
    path = entry.get("path", "")
    value = entry.get("value")
    
    if not path:
        return state
    
    if op == "SET":
        _set_nested_value(state, path, deepcopy(value))
    
    elif op == "MERGE":
        existing = _get_nested_value(state, path) or {}
        if isinstance(existing, dict) and isinstance(value, dict):
            _set_nested_value(state, path, {**existing, **deepcopy(value)})
        else:
            _set_nested_value(state, path, deepcopy(value))
    
    elif op == "APPEND":
        existing = _get_nested_value(state, path)
        if isinstance(existing, list):
            existing.append(deepcopy(value))
        else:
            _set_nested_value(state, path, [deepcopy(value)])
    
    elif op == "EXTEND":
        existing = _get_nested_value(state, path)
        if isinstance(existing, list) and isinstance(value, list):
            existing.extend(deepcopy(value))
        elif isinstance(existing, list):
            existing.append(deepcopy(value))
        else:
            _set_nested_value(state, path, list(deepcopy(value)) if isinstance(value, list) else [deepcopy(value)])
    
    elif op == "DELETE":
        parts = path.split(".")
        parent_path = ".".join(parts[:-1])
        key = parts[-1]
        parent = _get_nested_value(state, parent_path) if parent_path else state
        if isinstance(parent, dict) and key in parent:
            del parent[key]
        elif isinstance(parent, list) and key.isdigit() and int(key) < len(parent):
            parent.pop(int(key))
    
    return state


@tool
def read_world_bible_current_state() -> Dict[str, Any]:
    """
    Read the current state of the World Bible by replaying all operations.
    
    Returns:
        The complete current state as a dictionary.
    """
    _ensure_paths()
    
    if not WORLD_BIBLE_PATH.exists():
        return {"error": "World Bible file does not exist"}
    
    state = None
    
    with open(WORLD_BIBLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("type") == "INIT":
                    state = deepcopy(entry.get("data", {}))
                elif entry.get("type") == "UPDATE" and state is not None:
                    state = _apply_operation(state, entry)
                elif entry.get("type") == "SNAPSHOT" and entry.get("data"):
                    state = deepcopy(entry.get("data"))
            except json.JSONDecodeError:
                continue
    
    return state or {"error": "No valid INIT entry found in World Bible"}


@tool
def read_world_bible_excerpt(module_path: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Read a curated excerpt from the World Bible for passing to subagents.
    
    Args:
        module_path: Dot-notation path to the module (e.g., "modules.1_character_state.1.1_character_directory")
        filters: Optional filters for list data (e.g., {"status": "Active"})
    
    Returns:
        Filtered excerpt data.
    """
    state = read_world_bible_current_state()
    
    if "error" in state:
        return state
    
    data = _get_nested_value(state, module_path)
    
    if data is None:
        return {"error": f"Path '{module_path}' not found in World Bible"}
    
    # Apply filters if provided and data is a list
    if filters and isinstance(data, list):
        filtered = [
            item for item in data
            if isinstance(item, dict) and all(
                item.get(k) == v for k, v in filters.items()
            )
        ]
        return {"excerpt_from": module_path, "data": filtered, "filters_applied": filters}
    
    return {"excerpt_from": module_path, "data": data}


@tool
def append_world_bible_update(
    chapter: int,
    path: str,
    value: Any,
    operation: Literal["SET", "MERGE", "APPEND", "EXTEND", "DELETE"] = "SET"
) -> str:
    """
    Append an update operation to the World Bible changelog.
    This is the primary way the orchestrator modifies the World Bible.
    
    Args:
        chapter: Current chapter number
        path: Dot-notation path to the field being updated (e.g., "modules.1_character_state.1.1_character_directory.elara")
        value: The value to set/merge/append
        operation: Type of operation - SET (replace), MERGE (dict merge), APPEND (add to list), 
                   EXTEND (extend list), DELETE (remove)
    
    Returns:
        Confirmation message.
    """
    _ensure_paths()
    
    entry = {
        "type": "UPDATE",
        "chapter": chapter,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "path": path,
        "value": value
    }
    
    with open(WORLD_BIBLE_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return f"Appended {operation} operation to '{path}' for chapter {chapter}"


@tool
def create_world_bible_snapshot(chapter: int) -> str:
    """
    Create a full snapshot of the current World Bible state.
    Snapshots are saved to data/snapshots/chapter_XXX.jsonl
    
    Args:
        chapter: Chapter number for the snapshot
    
    Returns:
        Path to the created snapshot file.
    """
    _ensure_paths()
    
    state = read_world_bible_current_state()
    
    if "error" in state:
        return f"Error: {state['error']}"
    
    # Also append a SNAPSHOT entry to the main log
    snapshot_entry = {
        "type": "SNAPSHOT",
        "chapter": chapter,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": state
    }
    
    with open(WORLD_BIBLE_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(snapshot_entry, ensure_ascii=False) + '\n')
    
    # Save standalone snapshot file
    snapshot_path = SNAPSHOTS_DIR / f"chapter_{chapter:03d}.jsonl"
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(snapshot_entry, ensure_ascii=False) + '\n')
    
    return f"Snapshot created at {snapshot_path}"


@tool
def query_world_bible(query_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Query the World Bible for specific information.
    
    Args:
        query_type: Type of query - "character_state", "character_list", "active_threads", 
                    "timeline_events", "pending_payoffs", "chapter_log", "current_chapter"
        params: Query parameters (e.g., {"character_id": "elara_venn"})
    
    Returns:
        Query results.
    """
    state = read_world_bible_current_state()
    
    if "error" in state:
        return state
    
    params = params or {}
    modules = state.get("modules", {})
    
    if query_type == "current_chapter":
        return {
            "current_chapter": state.get("metadata", {}).get("current_chapter", 0),
            "project_name": state.get("metadata", {}).get("project_name", "")
        }
    
    elif query_type == "character_state":
        char_id = params.get("character_id")
        char_dir = modules.get("1_character_state", {}).get("1.1_character_directory", {})
        if char_id:
            char = char_dir.get(char_id)
            if char:
                # Get knowledge and relationships too
                knowledge = [
                    k for k in modules.get("1_character_state", {}).get("1.2_character_knowledge_matrix", [])
                    if k.get("character") == char_id
                ]
                relationships = [
                    r for r in modules.get("1_character_state", {}).get("1.3_relationship_records", [])
                    if r.get("character_a") == char_id or r.get("character_b") == char_id
                ]
                return {
                    "character_id": char_id,
                    "character": char,
                    "knowledge": knowledge,
                    "relationships": relationships
                }
            return {"error": f"Character '{char_id}' not found"}
        return {"all_characters": list(char_dir.keys())}
    
    elif query_type == "active_threads":
        threads = modules.get("2_plot_timeline_state", {}).get("2.3_plot_thread_registry", [])
        active = [t for t in threads if t.get("status") == "Active"]
        return {"active_threads": active, "count": len(active)}
    
    elif query_type == "timeline_events":
        day = params.get("day")
        timeline = modules.get("2_plot_timeline_state", {}).get("2.1_absolute_timeline", {})
        if day is not None:
            events = timeline.get("events_by_date", {}).get(str(day), [])
            return {"day": day, "events": events}
        return {
            "current_day": timeline.get("current_day", 0),
            "all_dates": list(timeline.get("events_by_date", {}).keys())
        }
    
    elif query_type == "pending_payoffs":
        payoffs = modules.get("2_plot_timeline_state", {}).get("2.4_pending_payoffs_foreshadowing", [])
        pending = [p for p in payoffs if p.get("resolution_status") == "Pending"]
        return {"pending_payoffs": pending, "count": len(pending)}
    
    elif query_type == "chapter_log":
        log = modules.get("2_plot_timeline_state", {}).get("2.2_pov_chapter_log", [])
        chapter_num = params.get("chapter_number")
        if chapter_num:
            entry = next((e for e in log if e.get("chapter_number") == chapter_num), None)
            return {"chapter": chapter_num, "entry": entry}
        return {"chapter_log": log, "total_chapters": len(log)}
    
    return {"error": f"Unknown query type: {query_type}"}


@tool
def detect_world_bible_contradiction(module_path: str, proposed_value: Any) -> Dict[str, Any]:
    """
    Check if a proposed update contradicts existing World Bible records.
    
    Args:
        module_path: Path to the field being updated
        proposed_value: The proposed new value
    
    Returns:
        Contradiction report with conflicts if any.
    """
    state = read_world_bible_current_state()
    
    if "error" in state:
        return state
    
    existing = _get_nested_value(state, module_path)
    contradictions = []
    
    # Check for direct contradiction (same path, different value)
    if existing is not None and existing != proposed_value:
        contradictions.append({
            "type": "value_change",
            "path": module_path,
            "existing": existing,
            "proposed": proposed_value
        })
    
    # Check character-specific contradictions
    if "1.1_character_directory" in module_path:
        parts = module_path.split(".")
        if len(parts) >= 4:
            char_id = parts[-2] if parts[-1] in ["age", "location", "emotional_state"] else parts[-1]
            char_data = _get_nested_value(state, f"modules.1_character_state.1.1_character_directory.{char_id}")
            if char_data:
                # Check for impossible location changes
                if "location" in module_path:
                    travel_records = modules.get("2_plot_timeline_state", {}).get("2.1_absolute_timeline", {}).get("travel_records", [])
                    current_loc = char_data.get("location")
                    proposed_loc = proposed_value if "location" in module_path else None
                    # Could add travel time validation here
    
    return {
        "has_contradictions": len(contradictions) > 0,
        "contradictions": contradictions,
        "can_proceed": len(contradictions) == 0,
        "existing_value": existing
    }


@tool
def get_world_bible_changelog(chapter: Optional[int] = None) -> List[Dict]:
    """
    Get the changelog entries, optionally filtered to a specific chapter.
    
    Args:
        chapter: Optional chapter number to filter to
    
    Returns:
        List of changelog entries.
    """
    if not WORLD_BIBLE_PATH.exists():
        return []
    
    entries = []
    
    with open(WORLD_BIBLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if chapter is None or entry.get("chapter") == chapter:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    
    return entries


@tool
def get_world_bible_at_chapter(chapter: int) -> Dict[str, Any]:
    """
    Reconstruct the World Bible state as it was at a specific chapter.
    
    Args:
        chapter: Chapter number to reconstruct
    
    Returns:
        World Bible state at that chapter.
    """
    if not WORLD_BIBLE_PATH.exists():
        return {"error": "World Bible file does not exist"}
    
    state = None
    last_snapshot = None
    
    with open(WORLD_BIBLE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entry_chapter = entry.get("chapter", 0)
                
                if entry.get("type") == "INIT":
                    state = deepcopy(entry.get("data", {}))
                elif entry.get("type") == "SNAPSHOT" and entry_chapter <= chapter:
                    state = deepcopy(entry.get("data", {}))
                    last_snapshot = entry_chapter
                elif entry.get("type") == "UPDATE" and state is not None and entry_chapter <= chapter:
                    state = _apply_operation(state, entry)
            except json.JSONDecodeError:
                continue
    
    if state is None:
        return {"error": f"Could not reconstruct state for chapter {chapter}"}
    
    return {
        "chapter": chapter,
        "state": state,
        "based_on_snapshot": last_snapshot
    }


@tool
def initialize_world_bible(project_name: str) -> str:
    """
    Initialize a new World Bible with the given project name.
    WARNING: This will overwrite any existing World Bible!
    
    Args:
        project_name: Name of the novel project
    
    Returns:
        Confirmation message.
    """
    _ensure_paths()
    
    init_data = {
        "metadata": {
            "project_name": project_name,
            "current_chapter": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        },
        "modules": {
            "1_character_state": {
                "1.1_character_directory": {},
                "1.2_character_knowledge_matrix": [],
                "1.3_relationship_records": []
            },
            "2_plot_timeline_state": {
                "2.1_absolute_timeline": {
                    "current_day": 0,
                    "events_by_date": {},
                    "travel_records": [],
                    "seasonal_weather_state": {}
                },
                "2.2_pov_chapter_log": [],
                "2.3_plot_thread_registry": [],
                "2.4_pending_payoffs_foreshadowing": []
            },
            "3_world_state": {
                "3.1_political_power_map": {"territories": []},
                "3.2_geography": {},
                "3.3_cultures": {},
                "3.4_history_legends": {},
                "3.5_magic_system_state": {}
            },
            "4_consequence_ledger": {
                "4.1_immediate_consequences": [],
                "4.2_time_delayed_consequence_bombs": []
            },
            "5_continuity_tracking": {
                "5.1_fact_registry": {},
                "5.2_contradiction_log": []
            }
        }
    }
    
    init_entry = {
        "type": "INIT",
        "chapter": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": init_data
    }
    
    with open(WORLD_BIBLE_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(init_entry, ensure_ascii=False, indent=2) + '\n')
    
    return f"World Bible initialized for project '{project_name}'"
