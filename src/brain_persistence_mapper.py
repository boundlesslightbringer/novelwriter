from dataclasses import dataclass, field
import re
from typing import Any, Dict, List


WRITE_LIST_KEYS: tuple[str, ...] = (
    "nodes_to_add",
    "nodes_to_update",
    "edges_to_add",
    "edges_to_update",
)

# Must match ``AddNodeArgs`` in ``kg_models.py`` so ``add_kg_node`` never receives invalid types.
ALLOWED_KG_NODE_TYPES: frozenset[str] = frozenset(
    {
        "Character",
        "Location",
        "Event",
        "Faction",
        "Culture",
        "KnowledgeItem",
        "PlotThread",
        "Payoff",
        "Chapter",
        "MagicSystem",
        "CascadeChain",
        "PhysicalDetail",
        "Contradiction",
    }
)

ALLOWED_KG_EDGE_TYPES: frozenset[str] = frozenset(
    {
        "KNOWS",
        "RELATIONSHIP",
        "LOCATED_AT",
        "CAUSES",
        "CONTROLS",
        "INVOLVES",
        "PAYS_OFF_IN",
        "ALLIED_WITH",
        "AT_WAR_WITH",
        "CONNECTED_TO",
        "BELONGS_TO_CULTURE",
        "DEPENDS_ON",
        "DESCRIBES",
        "INFORMED",
        "CONFLICTS_WITH",
    }
)

NODE_META_KEYS: frozenset[str] = frozenset(
    {
        "logical_id",
        "node_type",
        "type",
        "properties",
        "chapter",
        "valid_from",
        "valid_to",
    }
)


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any, default: int = 1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _make_logical_id(prefix: str, seed: Any, fallback_index: int) -> str:
    slug = _slugify(seed)
    if slug:
        return f"{prefix}_{slug[:40]}"
    return f"{prefix}_{fallback_index}"


def _extract_chapter(*sources: Dict[str, Any]) -> int:
    for source in sources:
        if not source:
            continue
        for key in ("chapter_context", "chapter", "as_of_chapter"):
            if source.get(key) is not None:
                return max(1, _to_int(source.get(key), default=1))
    return 1


@dataclass
class PersistPayloadMapperResult:
    context: Dict[str, Any]
    has_payload: bool
    errors: List[str] = field(default_factory=list)


class PersistPayloadMapper:
    """Build write-ready persistence payloads from creative worker artifacts."""

    def _extract_node_properties(self, record: Dict[str, Any]) -> Dict[str, Any]:
        properties = _ensure_dict(record.get("properties"))
        if properties:
            return properties
        synthesized = {key: value for key, value in record.items() if key not in NODE_META_KEYS}
        return _ensure_dict(synthesized)

    def _fallback_node_properties(self, node_type: str, logical_id: str) -> Dict[str, Any]:
        clean_id = str(logical_id or "").strip()
        if node_type == "KnowledgeItem":
            return {"description": clean_id or "knowledge item"}
        if node_type == "Character":
            return {"name": clean_id or "character"}
        if node_type in {"PlotThread", "Payoff"}:
            return {"name": clean_id or node_type.lower(), "status": "Seed"}
        return {"name": clean_id or node_type.lower() or "node"}

    def _append_if_dict(self, target: List[Dict[str, Any]], value: Any) -> None:
        if isinstance(value, dict):
            target.append(value)

    def _normalize_node_add(
        self,
        record: Dict[str, Any],
        chapter: int,
        *,
        fallback_type: str = "",
        fallback_prefix: str = "node",
        fallback_index: int = 1,
    ) -> Dict[str, Any] | None:
        raw_type = str(record.get("node_type") or record.get("type") or "").strip()
        fb_type = str(fallback_type or "").strip()
        if raw_type in ALLOWED_KG_NODE_TYPES:
            node_type = raw_type
        elif fb_type in ALLOWED_KG_NODE_TYPES:
            node_type = fb_type
        else:
            return None
        properties = self._extract_node_properties(record)
        logical_id = str(record.get("logical_id") or "").strip()
        if not logical_id:
            logical_id = _make_logical_id(
                fallback_prefix,
                properties.get("name") or properties.get("title") or properties.get("seed"),
                fallback_index,
            )
        if not properties:
            properties = self._fallback_node_properties(node_type, logical_id)
        return {
            "logical_id": logical_id,
            "node_type": node_type,
            "properties": properties,
            "chapter": _to_int(record.get("chapter"), default=chapter),
        }

    def _normalize_edge_add(
        self,
        record: Dict[str, Any],
        chapter: int,
        *,
        fallback_type: str = "",
        fallback_prefix: str = "edge",
        fallback_index: int = 1,
    ) -> Dict[str, Any] | None:
        edge_type = str(record.get("edge_type") or record.get("type") or fallback_type).strip()
        from_node = str(record.get("from") or record.get("from_node") or "").strip()
        to_node = str(record.get("to") or record.get("to_node") or "").strip()
        if not edge_type or edge_type not in ALLOWED_KG_EDGE_TYPES or not from_node or not to_node:
            return None
        logical_id = str(record.get("logical_id") or "").strip()
        if not logical_id:
            logical_id = _make_logical_id(fallback_prefix, f"{from_node}_{to_node}", fallback_index)
        return {
            "logical_id": logical_id,
            "edge_type": edge_type,
            "from": from_node,
            "to": to_node,
            "properties": _ensure_dict(record.get("properties")),
            "chapter": _to_int(record.get("chapter"), default=chapter),
        }

    def _normalize_node_update(self, record: Dict[str, Any], chapter: int) -> Dict[str, Any] | None:
        logical_id = str(record.get("logical_id") or "").strip()
        updated_properties = _ensure_dict(record.get("updated_properties"))
        if not updated_properties:
            updated_properties = _ensure_dict(record.get("properties"))
        if not logical_id or not updated_properties:
            return None
        return {
            "logical_id": logical_id,
            "updated_properties": updated_properties,
            "chapter": _to_int(record.get("chapter"), default=chapter),
        }

    def _normalize_edge_update(self, record: Dict[str, Any], chapter: int) -> Dict[str, Any] | None:
        logical_id = str(record.get("logical_id") or "").strip()
        updated_properties = _ensure_dict(record.get("updated_properties"))
        if not updated_properties:
            updated_properties = _ensure_dict(record.get("properties"))
        if not logical_id or not updated_properties:
            return None
        return {
            "logical_id": logical_id,
            "updated_properties": updated_properties,
            "chapter": _to_int(record.get("chapter"), default=chapter),
        }

    def build_context(
        self,
        latest_worker_result: Dict[str, Any],
        base_context: Dict[str, Any] | None = None,
    ) -> PersistPayloadMapperResult:
        base_context = _ensure_dict(base_context)
        source_context = _ensure_dict(latest_worker_result.get("context"))
        result = _ensure_dict(latest_worker_result.get("result"))
        artifacts = _ensure_dict(result.get("artifacts"))
        chapter = _extract_chapter(base_context, source_context, artifacts)

        payload: Dict[str, List[Dict[str, Any]]] = {key: [] for key in WRITE_LIST_KEYS}
        errors: List[str] = []
        fallback_index = 1

        def add_node(record: Dict[str, Any], *, fallback_type: str = "", fallback_prefix: str = "node") -> None:
            nonlocal fallback_index
            normalized = self._normalize_node_add(
                record,
                chapter,
                fallback_type=fallback_type,
                fallback_prefix=fallback_prefix,
                fallback_index=fallback_index,
            )
            fallback_index += 1
            if normalized:
                payload["nodes_to_add"].append(normalized)
            else:
                errors.append(f"Skipped malformed node add record: {record}")

        def add_edge(record: Dict[str, Any], *, fallback_type: str = "", fallback_prefix: str = "edge") -> None:
            nonlocal fallback_index
            normalized = self._normalize_edge_add(
                record,
                chapter,
                fallback_type=fallback_type,
                fallback_prefix=fallback_prefix,
                fallback_index=fallback_index,
            )
            fallback_index += 1
            if normalized:
                payload["edges_to_add"].append(normalized)
            else:
                errors.append(f"Skipped malformed edge add record: {record}")

        def add_node_update(record: Dict[str, Any]) -> None:
            normalized = self._normalize_node_update(record, chapter)
            if normalized:
                payload["nodes_to_update"].append(normalized)
            else:
                errors.append(f"Skipped malformed node update record: {record}")

        def add_edge_update(record: Dict[str, Any]) -> None:
            normalized = self._normalize_edge_update(record, chapter)
            if normalized:
                payload["edges_to_update"].append(normalized)
            else:
                errors.append(f"Skipped malformed edge update record: {record}")

        # First: prefer explicit write payloads if present.
        for source in (base_context, source_context, artifacts):
            for record in _ensure_list(source.get("nodes_to_add")):
                if isinstance(record, dict):
                    add_node(record)
            for record in _ensure_list(source.get("nodes_to_update")):
                if isinstance(record, dict):
                    add_node_update(record)
            for record in _ensure_list(source.get("edges_to_add")):
                if isinstance(record, dict):
                    add_edge(record)
            for record in _ensure_list(source.get("edges_to_update")):
                if isinstance(record, dict):
                    add_edge_update(record)

        # Worldbuilding + planning outputs.
        for record in _ensure_list(artifacts.get("plot_thread_seeds")):
            if isinstance(record, dict):
                add_node(record, fallback_type="PlotThread", fallback_prefix="thread")
        for record in _ensure_list(artifacts.get("payoff_seeds")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Payoff", fallback_prefix="payoff")
        for record in _ensure_list(artifacts.get("political_power_map")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Faction", fallback_prefix="faction")
        for record in _ensure_list(artifacts.get("geography")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Location", fallback_prefix="location")
        for record in _ensure_list(artifacts.get("cultures_customs_religion")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Culture", fallback_prefix="culture")
        for record in _ensure_list(artifacts.get("history_and_legends")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Event", fallback_prefix="event")
        if isinstance(artifacts.get("magic_system"), dict):
            add_node(artifacts["magic_system"], fallback_type="MagicSystem", fallback_prefix="magic")
        for record in _ensure_list(artifacts.get("location_connections")):
            if isinstance(record, dict):
                add_edge(record, fallback_type="CONNECTED_TO", fallback_prefix="conn")

        seed_document = _ensure_dict(artifacts.get("seed_document"))
        if seed_document:
            seed_text = str(seed_document.get("seed") or "bootstrap_seed").strip()
            add_node(
                {
                    "logical_id": _make_logical_id("thread_seed", seed_text, fallback_index),
                    "node_type": "PlotThread",
                    "properties": {
                        "name": seed_text[:120],
                        "status": "Seed",
                        "originating_chapter": chapter,
                        "seed_document": seed_document,
                    },
                    "chapter": chapter,
                },
                fallback_type="PlotThread",
                fallback_prefix="thread_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("payoff_seed", seed_text, fallback_index),
                    "node_type": "Payoff",
                    "properties": {
                        "name": f"Primary payoff for: {seed_text[:80]}",
                        "type": "Milestone",
                        "resolution_status": "Pending",
                        "registered_from_seed": seed_document,
                    },
                    "chapter": chapter,
                },
                fallback_type="Payoff",
                fallback_prefix="payoff_seed",
            )
            # Bootstrap scaffolding: ensure baseline world records exist for downstream flows.
            add_node(
                {
                    "logical_id": _make_logical_id("faction_seed", seed_text, fallback_index),
                    "node_type": "Faction",
                    "properties": {
                        "name": "Seed-era ruling faction",
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="Faction",
                fallback_prefix="faction_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("location_seed", seed_text, fallback_index),
                    "node_type": "Location",
                    "properties": {
                        "name": "Seed-era central stronghold",
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="Location",
                fallback_prefix="location_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("culture_seed", seed_text, fallback_index),
                    "node_type": "Culture",
                    "properties": {
                        "name": "Seed-era dominant culture",
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="Culture",
                fallback_prefix="culture_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("event_seed", seed_text, fallback_index),
                    "node_type": "Event",
                    "properties": {
                        "name": "Seed-era historical fracture",
                        "is_historical": True,
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="Event",
                fallback_prefix="event_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("magic_seed", seed_text, fallback_index),
                    "node_type": "MagicSystem",
                    "properties": {
                        "name": "Seed-era magic doctrine",
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="MagicSystem",
                fallback_prefix="magic_seed",
            )
            add_node(
                {
                    "logical_id": _make_logical_id("char_seed", seed_text, fallback_index),
                    "node_type": "Character",
                    "properties": {
                        "name": "Seed-era claimant",
                        "core_desire": "Secure legitimate succession",
                        "core_fear": "Dynastic collapse",
                        "self_deception": "Power alone can heal the realm",
                        "response_patterns": "Decisive under pressure",
                        "arc_type": "Provisional",
                        "pov_eligible": True,
                        "voice_profile": {
                            "vocabulary_range": {"lexical_register": "formal"},
                            "sentence_structure_patterns": {"default_sentence_length": "mixed"},
                            "observational_focus": {"primary_lens": "power shifts"},
                            "internal_thought_patterns": {"deliberative_style": "strategic"},
                            "emotional_processing_style": {"speed_of_acknowledgment": "measured"},
                        },
                        "origin_seed": seed_text,
                    },
                    "chapter": chapter,
                },
                fallback_type="Character",
                fallback_prefix="char_seed",
            )

        # Character outputs.
        character_node = _ensure_dict(artifacts.get("character_node"))
        if character_node:
            add_node(character_node, fallback_type="Character", fallback_prefix="char")
        for key in ("knowledge_items", "new_knowledge_items"):
            for record in _ensure_list(artifacts.get(key)):
                if isinstance(record, dict):
                    add_node(record, fallback_type="KnowledgeItem", fallback_prefix="ki")
        for key in ("knowledge_matrix_edges", "new_knows_edges"):
            for record in _ensure_list(artifacts.get(key)):
                if isinstance(record, dict):
                    add_edge(record, fallback_type="KNOWS", fallback_prefix="knows")
        for record in _ensure_list(artifacts.get("relationship_edges")):
            if isinstance(record, dict):
                add_edge(record, fallback_type="RELATIONSHIP", fallback_prefix="rel")
        for record in _ensure_list(artifacts.get("new_relationship_edges")):
            if isinstance(record, dict):
                add_edge(record, fallback_type="RELATIONSHIP", fallback_prefix="rel")
        for record in _ensure_list(artifacts.get("updated_relationship_edges")):
            if isinstance(record, dict):
                add_edge_update(record)
        culture_edge = _ensure_dict(artifacts.get("culture_edge"))
        if culture_edge:
            add_edge(culture_edge, fallback_type="BELONGS_TO_CULTURE", fallback_prefix="culture_rel")

        # Character integration nested payloads.
        knowledge_expansions = _ensure_dict(artifacts.get("knowledge_matrix_expansions"))
        for record in _ensure_list(knowledge_expansions.get("new_knowledge_items")):
            if isinstance(record, dict):
                add_node(record, fallback_type="KnowledgeItem", fallback_prefix="ki")
        for record in _ensure_list(knowledge_expansions.get("new_knows_edges")):
            if isinstance(record, dict):
                add_edge(record, fallback_type="KNOWS", fallback_prefix="knows")
        relationship_records = _ensure_dict(artifacts.get("relationship_records"))
        for record in _ensure_list(relationship_records.get("new_relationship_edges")):
            if isinstance(record, dict):
                add_edge(record, fallback_type="RELATIONSHIP", fallback_prefix="rel")
        for record in _ensure_list(relationship_records.get("updated_relationship_edges")):
            if isinstance(record, dict):
                add_edge_update(record)

        # Writing + consequence updates.
        for record in _ensure_list(artifacts.get("character_state_updates")):
            if isinstance(record, dict):
                add_node_update(record)
        for record in _ensure_list(artifacts.get("relationship_updates")):
            if isinstance(record, dict):
                add_edge_update(record)
        for record in _ensure_list(artifacts.get("consequence_bombs")):
            if isinstance(record, dict):
                add_node(record, fallback_type="Payoff", fallback_prefix="bomb")

        knowledge_matrix_updates = artifacts.get("knowledge_matrix_updates")
        if isinstance(knowledge_matrix_updates, dict):
            for record in _ensure_list(knowledge_matrix_updates.get("new_knowledge_items")):
                if isinstance(record, dict):
                    add_node(record, fallback_type="KnowledgeItem", fallback_prefix="ki")
            for record in _ensure_list(knowledge_matrix_updates.get("new_knows_edges")):
                if isinstance(record, dict):
                    add_edge(record, fallback_type="KNOWS", fallback_prefix="knows")

        # Voice profile update payload from character-voice-differentiation.
        character_id = str(artifacts.get("character_id") or "").strip()
        voice_profile = _ensure_dict(artifacts.get("voice_profile"))
        if character_id and voice_profile:
            add_node_update(
                {
                    "logical_id": character_id,
                    "updated_properties": {"voice_profile": voice_profile},
                    "chapter": chapter,
                }
            )

        persist_context: Dict[str, Any] = {
            "chapter_context": chapter,
            "artifacts": artifacts,
        }
        for key in WRITE_LIST_KEYS:
            if payload[key]:
                persist_context[key] = payload[key]
        if errors:
            persist_context["mapping_errors"] = errors

        has_payload = any(payload[key] for key in WRITE_LIST_KEYS)
        return PersistPayloadMapperResult(context=persist_context, has_payload=has_payload, errors=errors)
