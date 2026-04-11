import re
from typing import Any, Dict, List, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from src.agents.base import WorkerResponse
from src.story_state_temporal_chain import (
    run_edge_temporal_update_chain,
    run_node_temporal_update_chain,
)
from src.world_bible_tools import (
    add_kg_edge,
    add_kg_node,
    detect_kg_contradiction,
    query_kg_edges,
    query_kg_nodes,
)


class StoryStatePersistState(TypedDict, total=False):
    task: str
    context: Dict[str, Any]
    chapter: int
    is_batch: bool
    nodes_to_add: List[Dict[str, Any]]
    nodes_to_update: List[Dict[str, Any]]
    edges_to_add: List[Dict[str, Any]]
    edges_to_update: List[Dict[str, Any]]
    proposed_updates: List[Dict[str, Any]]
    contradiction_record: Dict[str, Any]
    records_updated: List[str]
    records_failed: List[Dict[str, str]]
    errors: List[str]
    verification: Dict[str, Any]
    response_status: str
    response_summary: str
    response_artifacts: Dict[str, Any]


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_context_lists(context: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    direct = _ensure_list(context.get(key))
    artifacts = _ensure_dict(context.get("artifacts"))
    artifact_list = _ensure_list(artifacts.get(key))
    source = direct if direct else artifact_list
    return [_ensure_dict(entry) for entry in source if isinstance(entry, dict)]


def _extract_context_lists_any(context: Dict[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    combined: List[Dict[str, Any]] = []
    for key in keys:
        combined.extend(_extract_context_lists(context, key))
    return combined


def _extract_chapter(context: Dict[str, Any]) -> int:
    chapter_value = context.get("chapter")
    if chapter_value is None:
        chapter_value = context.get("chapter_context")
    if chapter_value is None:
        chapter_value = _ensure_dict(context.get("artifacts")).get("chapter_context")
    return _to_int(chapter_value, default=0)


def _slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _make_logical_id(prefix: str, props: Dict[str, Any], fallback_index: int) -> str:
    for key in ("logical_id", "name", "title", "description", "seed"):
        slug = _slugify(props.get(key))
        if slug:
            return f"{prefix}_{slug[:40]}"
    return f"{prefix}_{fallback_index}"


def _coerce_node_record(
    raw: Dict[str, Any],
    fallback_type: str,
    logical_prefix: str,
    chapter: int,
    fallback_index: int,
) -> Dict[str, Any]:
    properties = _ensure_dict(raw.get("properties"))
    node_type = str(raw.get("node_type") or raw.get("type") or fallback_type or "").strip()
    logical_id = str(raw.get("logical_id") or "").strip()
    if not logical_id:
        logical_id = _make_logical_id(logical_prefix, properties, fallback_index)
    return {
        "logical_id": logical_id,
        "node_type": node_type,
        "properties": properties,
        "chapter": _to_int(raw.get("chapter"), default=chapter),
    }


def _coerce_edge_record(
    raw: Dict[str, Any],
    fallback_type: str,
    logical_prefix: str,
    chapter: int,
    fallback_index: int,
) -> Dict[str, Any]:
    properties = _ensure_dict(raw.get("properties"))
    edge_type = str(raw.get("edge_type") or raw.get("type") or fallback_type or "").strip()
    from_node = str(raw.get("from_node") or raw.get("from") or "").strip()
    to_node = str(raw.get("to_node") or raw.get("to") or "").strip()
    logical_id = str(raw.get("logical_id") or "").strip()
    if not logical_id:
        logical_id = _make_logical_id(
            logical_prefix,
            {"name": f"{from_node}_{to_node}", "description": properties.get("description", "")},
            fallback_index,
        )
    return {
        "logical_id": logical_id,
        "edge_type": edge_type,
        "from_node": from_node,
        "to_node": to_node,
        "properties": properties,
        "chapter": _to_int(raw.get("chapter"), default=chapter),
    }


def _derive_write_payload_from_artifacts(
    context: Dict[str, Any], chapter: int
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    artifacts = _ensure_dict(context.get("artifacts"))
    nodes_to_add: List[Dict[str, Any]] = []
    nodes_to_update: List[Dict[str, Any]] = []
    edges_to_add: List[Dict[str, Any]] = []
    edges_to_update: List[Dict[str, Any]] = []

    node_specs = [
        ("plot_thread_seeds", "PlotThread", "thread"),
        ("payoff_seeds", "Payoff", "payoff"),
        ("political_power_map", "Faction", "faction"),
        ("geography", "Location", "location"),
        ("cultures_customs_religion", "Culture", "culture"),
        ("history_and_legends", "Event", "event"),
    ]
    edge_specs = [
        ("location_connections", "CONNECTED_TO", "conn"),
        ("new_relationship_edges", "RELATIONSHIP", "rel"),
    ]

    idx = 1
    for key, fallback_type, prefix in node_specs:
        for record in _ensure_list(artifacts.get(key)):
            if isinstance(record, dict):
                nodes_to_add.append(
                    _coerce_node_record(record, fallback_type, prefix, chapter, idx)
                )
                idx += 1

    magic_system = artifacts.get("magic_system")
    if isinstance(magic_system, dict):
        nodes_to_add.append(
            _coerce_node_record(magic_system, "MagicSystem", "magic", chapter, idx)
        )
        idx += 1

    # Seed bootstrap fallback: convert validated seed into a persisted PlotThread seed.
    seed_document = artifacts.get("seed_document")
    if isinstance(seed_document, dict):
        seed_text = str(seed_document.get("seed") or "bootstrap_seed").strip()
        seed_props = {
            "name": seed_text[:120],
            "status": "Seed",
            "originating_chapter": chapter,
            "seed_document": seed_document,
        }
        nodes_to_add.append(
            {
                "logical_id": _make_logical_id("thread_seed", {"seed": seed_text}, idx),
                "node_type": "PlotThread",
                "properties": seed_props,
                "chapter": chapter,
            }
        )
        idx += 1

    edge_idx = 1
    for key, fallback_type, prefix in edge_specs:
        for record in _ensure_list(artifacts.get(key)):
            if isinstance(record, dict):
                edges_to_add.append(
                    _coerce_edge_record(record, fallback_type, prefix, chapter, edge_idx)
                )
                edge_idx += 1

    for record in _ensure_list(artifacts.get("updated_relationship_edges")):
        if isinstance(record, dict):
            edges_to_update.append(_normalize_update_edge(record, chapter))

    return nodes_to_add, nodes_to_update, edges_to_add, edges_to_update


def _normalize_add_node(record: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    node_type = str(record.get("node_type") or record.get("type") or "").strip()
    properties = _ensure_dict(record.get("properties"))
    logical_id = str(record.get("logical_id") or "").strip()
    if not logical_id:
        prefix = _slugify(node_type) or "node"
        logical_id = _make_logical_id(prefix, properties, chapter)
    return {
        "logical_id": logical_id,
        "node_type": node_type,
        "properties": properties,
        "chapter": _to_int(record.get("chapter"), default=chapter),
    }


def _normalize_update_node(record: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    updated_properties = _ensure_dict(record.get("updated_properties"))
    if not updated_properties:
        updated_properties = _ensure_dict(record.get("properties"))
    return {
        "logical_id": str(record.get("logical_id") or ""),
        "updated_properties": updated_properties,
        "chapter": _to_int(record.get("chapter"), default=chapter),
    }


def _normalize_add_edge(record: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    from_node = str(record.get("from_node") or record.get("from") or "")
    to_node = str(record.get("to_node") or record.get("to") or "")
    edge_type = str(record.get("edge_type") or record.get("type") or "").strip()
    logical_id = str(record.get("logical_id") or "").strip()
    if not logical_id:
        prefix = _slugify(edge_type) or "edge"
        logical_id = _make_logical_id(
            prefix,
            {"name": f"{from_node}_{to_node}", "description": _ensure_dict(record.get("properties")).get("description", "")},
            chapter,
        )
    return {
        "logical_id": logical_id,
        "edge_type": edge_type,
        "from_node": from_node,
        "to_node": to_node,
        "properties": _ensure_dict(record.get("properties")),
        "chapter": _to_int(record.get("chapter"), default=chapter),
    }


def _normalize_update_edge(record: Dict[str, Any], chapter: int) -> Dict[str, Any]:
    updated_properties = _ensure_dict(record.get("updated_properties"))
    if not updated_properties:
        updated_properties = _ensure_dict(record.get("properties"))
    return {
        "logical_id": str(record.get("logical_id") or ""),
        "updated_properties": updated_properties,
        "chapter": _to_int(record.get("chapter"), default=chapter),
    }


def _tool_error_message(result: Any) -> str:
    if isinstance(result, str) and result.lower().startswith("error:"):
        return result
    return ""


def _dedupe_records(
    records: List[Dict[str, Any]], step_name: str
) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    seen: set[str] = set()
    deduped: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []
    for record in records:
        logical_id = str(record.get("logical_id") or "")
        if not logical_id:
            failures.append(
                {
                    "logical_id": "",
                    "step": step_name,
                    "error": "Missing logical_id during dedupe.",
                }
            )
            continue
        if logical_id in seen:
            failures.append(
                {
                    "logical_id": logical_id,
                    "step": step_name,
                    "error": "Duplicate logical_id skipped.",
                }
            )
            continue
        seen.add(logical_id)
        deduped.append(record)
    return deduped, failures


def _build_story_state_subgraph() -> Any:
    graph = StateGraph(StoryStatePersistState)

    def validate_payload(state: StoryStatePersistState) -> StoryStatePersistState:
        context = _ensure_dict(state.get("context"))
        chapter = _extract_chapter(context)
        if chapter <= 0:
            chapter = 1
        nodes_to_add = _extract_context_lists(context, "nodes_to_add")
        nodes_to_update = _extract_context_lists(context, "nodes_to_update")
        edges_to_add = _extract_context_lists_any(context, ["edges_to_add", "new_relationship_edges"])
        edges_to_update = _extract_context_lists_any(context, ["edges_to_update", "updated_relationship_edges"])

        if not any([nodes_to_add, nodes_to_update, edges_to_add, edges_to_update]):
            (
                derived_nodes_to_add,
                derived_nodes_to_update,
                derived_edges_to_add,
                derived_edges_to_update,
            ) = _derive_write_payload_from_artifacts(context, chapter)
            nodes_to_add = derived_nodes_to_add
            nodes_to_update = derived_nodes_to_update
            edges_to_add = derived_edges_to_add
            edges_to_update = derived_edges_to_update
        is_batch = bool(context.get("batch_mode")) or (
            len(nodes_to_add) + len(nodes_to_update) + len(edges_to_add) + len(edges_to_update) > 1
        )

        errors: List[str] = []
        if not any([nodes_to_add, nodes_to_update, edges_to_add, edges_to_update]):
            errors.append("No write records provided. Expected at least one write list in context.")

        return {
            "chapter": chapter,
            "is_batch": is_batch,
            "nodes_to_add": nodes_to_add,
            "nodes_to_update": nodes_to_update,
            "edges_to_add": edges_to_add,
            "edges_to_update": edges_to_update,
            "errors": errors,
            "records_updated": [],
            "records_failed": [],
            "verification": {"verified_nodes": 0, "verified_edges": 0},
        }

    def route_after_validation(
        state: StoryStatePersistState,
    ) -> Literal["finalize_terminal_failed", "validate_batch", "plan_writes"]:
        if state.get("errors"):
            return "finalize_terminal_failed"
        if state.get("is_batch"):
            return "validate_batch"
        return "plan_writes"

    def validate_batch(state: StoryStatePersistState) -> StoryStatePersistState:
        chapter = int(state.get("chapter", 0))
        normalized_nodes_to_add = [_normalize_add_node(record, chapter) for record in state.get("nodes_to_add", [])]
        normalized_nodes_to_update = [
            _normalize_update_node(record, chapter) for record in state.get("nodes_to_update", [])
        ]
        normalized_edges_to_add = [_normalize_add_edge(record, chapter) for record in state.get("edges_to_add", [])]
        normalized_edges_to_update = [
            _normalize_update_edge(record, chapter) for record in state.get("edges_to_update", [])
        ]

        nodes_to_add, failed_nodes_add = _dedupe_records(normalized_nodes_to_add, "dedupe_and_normalize_ids")
        nodes_to_update, failed_nodes_update = _dedupe_records(normalized_nodes_to_update, "dedupe_and_normalize_ids")
        edges_to_add, failed_edges_add = _dedupe_records(normalized_edges_to_add, "dedupe_and_normalize_ids")
        edges_to_update, failed_edges_update = _dedupe_records(normalized_edges_to_update, "dedupe_and_normalize_ids")

        return {
            "nodes_to_add": nodes_to_add,
            "nodes_to_update": nodes_to_update,
            "edges_to_add": edges_to_add,
            "edges_to_update": edges_to_update,
            "records_failed": list(state.get("records_failed", []))
            + failed_nodes_add
            + failed_nodes_update
            + failed_edges_add
            + failed_edges_update,
        }

    def plan_writes(state: StoryStatePersistState) -> StoryStatePersistState:
        chapter = int(state.get("chapter", 0))
        normalized_nodes_to_add = [_normalize_add_node(record, chapter) for record in state.get("nodes_to_add", [])]
        normalized_nodes_to_update = [
            _normalize_update_node(record, chapter) for record in state.get("nodes_to_update", [])
        ]
        normalized_edges_to_add = [_normalize_add_edge(record, chapter) for record in state.get("edges_to_add", [])]
        normalized_edges_to_update = [
            _normalize_update_edge(record, chapter) for record in state.get("edges_to_update", [])
        ]

        proposed_updates: List[Dict[str, Any]] = []
        proposed_updates.extend(
            {"action": "add_node", "logical_id": record.get("logical_id", "")}
            for record in normalized_nodes_to_add
        )
        proposed_updates.extend(
            {"action": "update_node", "logical_id": record.get("logical_id", "")}
            for record in normalized_nodes_to_update
        )
        proposed_updates.extend(
            {"action": "add_edge", "logical_id": record.get("logical_id", "")}
            for record in normalized_edges_to_add
        )
        proposed_updates.extend(
            {"action": "update_edge", "logical_id": record.get("logical_id", "")}
            for record in normalized_edges_to_update
        )

        errors: List[str] = list(state.get("errors", []))
        for record in normalized_nodes_to_add + normalized_nodes_to_update + normalized_edges_to_add + normalized_edges_to_update:
            if not record.get("logical_id"):
                errors.append("All write records must include non-empty logical_id.")

        return {
            "nodes_to_add": normalized_nodes_to_add,
            "nodes_to_update": normalized_nodes_to_update,
            "edges_to_add": normalized_edges_to_add,
            "edges_to_update": normalized_edges_to_update,
            "proposed_updates": proposed_updates,
            "errors": errors,
        }

    def route_after_batch_validation(
        state: StoryStatePersistState,
    ) -> Literal["finalize_terminal_failed", "detect_contradictions"]:
        if not any(
            [
                state.get("nodes_to_add"),
                state.get("nodes_to_update"),
                state.get("edges_to_add"),
                state.get("edges_to_update"),
            ]
        ):
            return "finalize_terminal_failed"
        return "detect_contradictions"

    def route_after_plan(
        state: StoryStatePersistState,
    ) -> Literal["finalize_terminal_failed", "detect_contradictions"]:
        if state.get("errors"):
            return "finalize_terminal_failed"
        return "detect_contradictions"

    def detect_contradictions(state: StoryStatePersistState) -> StoryStatePersistState:
        chapter = int(state.get("chapter", 0))
        proposed_updates = state.get("proposed_updates", [])
        try:
            contradiction_record = detect_kg_contradiction.invoke(
                {"proposed_updates": proposed_updates, "chapter": chapter}
            )
        except Exception as error:
            contradiction_record = {
                "has_contradictions": True,
                "contradictions": [f"Contradiction detection failed: {error}"],
                "can_proceed": False,
            }
        return {"contradiction_record": _ensure_dict(contradiction_record)}

    def route_after_contradictions(state: StoryStatePersistState) -> Literal["finalize_blocked", "write_nodes"]:
        contradiction_record = _ensure_dict(state.get("contradiction_record"))
        if contradiction_record.get("has_contradictions"):
            return "finalize_blocked"
        return "write_nodes"

    def write_nodes(state: StoryStatePersistState) -> StoryStatePersistState:
        records_updated: List[str] = list(state.get("records_updated", []))
        records_failed: List[Dict[str, str]] = list(state.get("records_failed", []))
        errors: List[str] = list(state.get("errors", []))

        for record in state.get("nodes_to_add", []):
            try:
                result = add_kg_node.invoke(record)
                error_message = _tool_error_message(result)
                if error_message:
                    errors.append(error_message)
                    records_failed.append(
                        {
                            "logical_id": str(record.get("logical_id") or ""),
                            "step": "write_nodes",
                            "error": error_message,
                        }
                    )
                else:
                    records_updated.append(str(record.get("logical_id")))
            except Exception as error:
                errors.append(f"add_kg_node failed for {record.get('logical_id', '')}: {error}")
                records_failed.append(
                    {
                        "logical_id": str(record.get("logical_id") or ""),
                        "step": "write_nodes",
                        "error": str(error),
                    }
                )

        for record in state.get("nodes_to_update", []):
            try:
                chain_result = run_node_temporal_update_chain(
                    logical_id=str(record.get("logical_id") or ""),
                    updated_properties=_ensure_dict(record.get("updated_properties")),
                    chapter=_to_int(record.get("chapter"), default=int(state.get("chapter", 0))),
                )
                if not chain_result.get("ok"):
                    error_message = (
                        f"Temporal node update failed at {chain_result.get('step')}: {chain_result.get('error')}"
                    )
                    errors.append(error_message)
                    records_failed.append(
                        {
                            "logical_id": str(record.get("logical_id") or ""),
                            "step": str(chain_result.get("step") or "write_nodes"),
                            "error": str(chain_result.get("error") or error_message),
                        }
                    )
                else:
                    records_updated.append(str(record.get("logical_id")))
            except Exception as error:
                errors.append(f"update_kg_node failed for {record.get('logical_id', '')}: {error}")
                records_failed.append(
                    {
                        "logical_id": str(record.get("logical_id") or ""),
                        "step": "write_nodes",
                        "error": str(error),
                    }
                )

        return {"records_updated": records_updated, "records_failed": records_failed, "errors": errors}

    def write_edges(state: StoryStatePersistState) -> StoryStatePersistState:
        records_updated: List[str] = list(state.get("records_updated", []))
        records_failed: List[Dict[str, str]] = list(state.get("records_failed", []))
        errors: List[str] = list(state.get("errors", []))

        for record in state.get("edges_to_add", []):
            try:
                result = add_kg_edge.invoke(record)
                error_message = _tool_error_message(result)
                if error_message:
                    errors.append(error_message)
                    records_failed.append(
                        {
                            "logical_id": str(record.get("logical_id") or ""),
                            "step": "write_edges",
                            "error": error_message,
                        }
                    )
                else:
                    records_updated.append(str(record.get("logical_id")))
            except Exception as error:
                errors.append(f"add_kg_edge failed for {record.get('logical_id', '')}: {error}")
                records_failed.append(
                    {
                        "logical_id": str(record.get("logical_id") or ""),
                        "step": "write_edges",
                        "error": str(error),
                    }
                )

        for record in state.get("edges_to_update", []):
            try:
                chain_result = run_edge_temporal_update_chain(
                    logical_id=str(record.get("logical_id") or ""),
                    updated_properties=_ensure_dict(record.get("updated_properties")),
                    chapter=_to_int(record.get("chapter"), default=int(state.get("chapter", 0))),
                )
                if not chain_result.get("ok"):
                    error_message = (
                        f"Temporal edge update failed at {chain_result.get('step')}: {chain_result.get('error')}"
                    )
                    errors.append(error_message)
                    records_failed.append(
                        {
                            "logical_id": str(record.get("logical_id") or ""),
                            "step": str(chain_result.get("step") or "write_edges"),
                            "error": str(chain_result.get("error") or error_message),
                        }
                    )
                else:
                    records_updated.append(str(record.get("logical_id")))
            except Exception as error:
                errors.append(f"update_kg_edge failed for {record.get('logical_id', '')}: {error}")
                records_failed.append(
                    {
                        "logical_id": str(record.get("logical_id") or ""),
                        "step": "write_edges",
                        "error": str(error),
                    }
                )

        return {"records_updated": records_updated, "records_failed": records_failed, "errors": errors}

    def post_verify(state: StoryStatePersistState) -> StoryStatePersistState:
        chapter = int(state.get("chapter", 0))
        node_ids = [
            record.get("logical_id", "")
            for record in state.get("nodes_to_add", []) + state.get("nodes_to_update", [])
            if record.get("logical_id")
        ]
        edge_ids = [
            record.get("logical_id", "")
            for record in state.get("edges_to_add", []) + state.get("edges_to_update", [])
            if record.get("logical_id")
        ]

        verification = {"verified_nodes": 0, "verified_edges": 0}

        if node_ids:
            try:
                node_docs = query_kg_nodes.invoke(
                    {"query": {"logical_id": {"$in": node_ids}}, "as_of_chapter": chapter}
                )
                verification["verified_nodes"] = len(node_docs)
            except Exception:
                verification["verified_nodes"] = 0

        if edge_ids:
            try:
                edge_docs = query_kg_edges.invoke(
                    {"query": {"logical_id": {"$in": edge_ids}}, "as_of_chapter": chapter}
                )
                verification["verified_edges"] = len(edge_docs)
            except Exception:
                verification["verified_edges"] = 0

        return {"verification": verification}

    def summarize_results(state: StoryStatePersistState) -> StoryStatePersistState:
        records_updated = state.get("records_updated", [])
        records_failed = state.get("records_failed", [])
        errors = state.get("errors", [])
        has_failures = bool(records_failed or errors)

        artifacts = {
            "operation": "write",
            "status": "failed" if has_failures else "success",
            "records_updated": records_updated,
            "records_failed": records_failed,
            "errors": errors,
            "verification": state.get("verification", {"verified_nodes": 0, "verified_edges": 0}),
            "contradiction_record": {"has_contradictions": False, "contradictions": [], "can_proceed": True},
        }
        summary = (
            f"Batch persistence completed with {len(records_updated)} successes and {len(records_failed)} failures."
            if has_failures
            else f"Persisted {len(records_updated)} records to the Story State KG."
        )
        return {
            "response_status": "failed" if has_failures else "success",
            "response_summary": summary,
            "response_artifacts": artifacts,
        }

    def finalize_blocked(state: StoryStatePersistState) -> StoryStatePersistState:
        contradiction_record = _ensure_dict(state.get("contradiction_record"))
        artifacts = {
            "operation": "write",
            "status": "blocked",
            "records_updated": [],
            "records_failed": [],
            "errors": [],
            "verification": state.get("verification", {"verified_nodes": 0, "verified_edges": 0}),
            "contradiction_record": contradiction_record,
        }
        return {
            "response_status": "blocked",
            "response_summary": "Write blocked due to KG contradictions.",
            "response_artifacts": artifacts,
        }

    def finalize_terminal_failed(state: StoryStatePersistState) -> StoryStatePersistState:
        errors = state.get("errors", [])
        artifacts = {
            "operation": "write",
            "status": "failed",
            "records_updated": state.get("records_updated", []),
            "records_failed": state.get("records_failed", []),
            "errors": errors,
            "verification": state.get("verification", {"verified_nodes": 0, "verified_edges": 0}),
            "contradiction_record": _ensure_dict(state.get("contradiction_record")),
        }
        return {
            "response_status": "failed",
            "response_summary": "Story State persistence failed before completing all writes.",
            "response_artifacts": artifacts,
        }

    graph.add_node("validate_payload", validate_payload)
    graph.add_node("validate_batch", validate_batch)
    graph.add_node("plan_writes", plan_writes)
    graph.add_node("detect_contradictions", detect_contradictions)
    graph.add_node("write_nodes", write_nodes)
    graph.add_node("write_edges", write_edges)
    graph.add_node("post_verify", post_verify)
    graph.add_node("summarize_results", summarize_results)
    graph.add_node("finalize_blocked", finalize_blocked)
    graph.add_node("finalize_terminal_failed", finalize_terminal_failed)

    graph.add_edge(START, "validate_payload")
    graph.add_conditional_edges(
        "validate_payload",
        route_after_validation,
        {
            "validate_batch": "validate_batch",
            "plan_writes": "plan_writes",
            "finalize_terminal_failed": "finalize_terminal_failed",
        },
    )
    graph.add_conditional_edges(
        "validate_batch",
        route_after_batch_validation,
        {"detect_contradictions": "detect_contradictions", "finalize_terminal_failed": "finalize_terminal_failed"},
    )
    graph.add_conditional_edges(
        "plan_writes",
        route_after_plan,
        {"detect_contradictions": "detect_contradictions", "finalize_terminal_failed": "finalize_terminal_failed"},
    )
    graph.add_conditional_edges(
        "detect_contradictions",
        route_after_contradictions,
        {"write_nodes": "write_nodes", "finalize_blocked": "finalize_blocked"},
    )
    graph.add_edge("write_nodes", "write_edges")
    graph.add_edge("write_edges", "post_verify")
    graph.add_edge("post_verify", "summarize_results")
    graph.add_edge("summarize_results", END)
    graph.add_edge("finalize_blocked", END)
    graph.add_edge("finalize_terminal_failed", END)

    return graph.compile()


def run_story_state_manager_subgraph(
    subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None
) -> Dict[str, Any]:
    worker_request = _ensure_dict(state.get("worker_request"))
    context = _ensure_dict(worker_request.get("context"))
    task = str(worker_request.get("task", ""))
    initial_state: StoryStatePersistState = {
        "task": task,
        "context": context,
    }

    try:
        graph = _build_story_state_subgraph()
        graph_result = graph.invoke(initial_state, config=config or {})
        structured_result = WorkerResponse(
            status=str(graph_result.get("response_status") or "failed"),
            summary=str(graph_result.get("response_summary") or "Story State persistence subgraph failed."),
            artifacts=_ensure_dict(graph_result.get("response_artifacts")),
        ).model_dump()
    except Exception as error:
        structured_result = WorkerResponse(
            status="failed",
            summary=f"Worker execution failed: {error}",
            artifacts={"error": str(error)},
        ).model_dump()

    worker_record = {
        "worker": subagent.name,
        "task": task,
        "context": context,
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }
