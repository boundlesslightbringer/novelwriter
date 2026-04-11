"""Heuristic validators for bootstrap-critical worker artifacts.

Used by optional bootstrap tracing and by tests. These checks encode the
contracts implied by planning/character prompts and ``PersistPayloadMapper``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _non_null_dict(value: Any, path: str, errors: List[str]) -> Dict[str, Any]:
    if value is None:
        errors.append(f"{path} must not be null (use {{}}).")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object, not {type(value).__name__}.")
        return {}
    return value


def validate_finding_a_seed_artifacts(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    seed = _non_null_dict(artifacts.get("seed_document"), "artifacts.seed_document", errors)
    if not seed:
        errors.append("artifacts.seed_document is required for finding-a-seed.")
        return errors
    if not str(seed.get("seed") or "").strip():
        errors.append("seed_document.seed must be non-empty text.")
    vr = seed.get("validation_record")
    if vr is None:
        errors.append("seed_document.validation_record must not be null.")
    elif isinstance(vr, dict):
        for key in ("concreteness", "generative_tension", "emotional_necessity", "open_architecture"):
            if key not in vr or vr.get(key) is None:
                errors.append(f"seed_document.validation_record.{key} is missing or null.")
    else:
        errors.append("seed_document.validation_record must be an object with four PASS/FAIL strings.")
    log = _ensure_list(artifacts.get("candidate_seeds_log"))
    if not log:
        errors.append("artifacts.candidate_seeds_log should be a non-empty list.")
    for idx, entry in enumerate(log):
        if not isinstance(entry, dict):
            errors.append(f"candidate_seeds_log[{idx}] must be an object.")
    if not str(artifacts.get("genre") or "").strip():
        errors.append("artifacts.genre should echo the requested genre string.")
    themes = _ensure_list(artifacts.get("themes"))
    if not themes:
        errors.append("artifacts.themes should be a non-empty list.")
    return errors


def validate_defining_rough_endpoints_pass1(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    _non_null_dict(artifacts.get("prologue_specification"), "artifacts.prologue_specification", errors)
    if not str(artifacts.get("starting_situation") or "").strip():
        errors.append("artifacts.starting_situation should be non-empty.")
    if not str(artifacts.get("draft_ending_destination") or "").strip():
        errors.append("artifacts.draft_ending_destination should be non-empty.")
    slots = _ensure_list(artifacts.get("character_slot_sketches"))
    if not slots:
        errors.append("Pass 1 expects artifacts.character_slot_sketches (non-empty).")
    for idx, slot in enumerate(slots):
        if not isinstance(slot, dict):
            errors.append(f"character_slot_sketches[{idx}] must be an object.")
            continue
        for field in ("slot_id", "narrative_role", "implied_contradiction", "stakes", "world_context"):
            if not str(slot.get(field) or "").strip():
                errors.append(f"character_slot_sketches[{idx}].{field} should be populated.")
        oq = _ensure_list(slot.get("open_questions"))
        if not oq:
            errors.append(f"character_slot_sketches[{idx}].open_questions should be a non-empty list.")
    milestones = _ensure_list(artifacts.get("draft_milestones"))
    if not milestones:
        errors.append("Pass 1 expects artifacts.draft_milestones (non-empty).")
    return errors


def validate_defining_rough_endpoints_pass2(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    threads = _ensure_list(artifacts.get("plot_thread_seeds"))
    payoffs = _ensure_list(artifacts.get("payoff_seeds"))
    if not threads:
        errors.append("Pass 2 expects artifacts.plot_thread_seeds (non-empty) for persistence.")
    if not payoffs:
        errors.append("Pass 2 expects artifacts.payoff_seeds (non-empty) for persistence.")
    for label, records in (("plot_thread_seeds", threads), ("payoff_seeds", payoffs)):
        for idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                errors.append(f"{label}[{idx}] must be an object.")
                continue
            node_type = str(rec.get("node_type") or rec.get("type") or "").strip()
            if not node_type:
                errors.append(f"{label}[{idx}] missing node_type/type.")
            props = _non_null_dict(rec.get("properties"), f"{label}[{idx}].properties", errors)
            if label == "plot_thread_seeds" and not str(props.get("name") or "").strip():
                errors.append(f"{label}[{idx}].properties.name should be set for PlotThread.")
            if label == "payoff_seeds" and not str(props.get("description") or "").strip():
                errors.append(f"{label}[{idx}].properties.description should be set for Payoff.")
    return errors


def validate_worldbuilding_artifacts(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    for key, label in (
        ("political_power_map", "Faction"),
        ("geography", "Location"),
        ("cultures_customs_religion", "Culture"),
    ):
        items = _ensure_list(artifacts.get(key))
        if not items:
            errors.append(f"artifacts.{key} should be non-empty for initial worldbuild ({label}).")
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{key}[{idx}] must be an object.")
                continue
            props = _non_null_dict(item.get("properties"), f"{key}[{idx}].properties", errors)
            if not str(props.get("name") or "").strip():
                errors.append(f"{key}[{idx}].properties.name should be set.")
            _non_null_dict(item.get("iceberg_notes"), f"{key}[{idx}].iceberg_notes", errors)

    hist_key = "history_and_legends"
    hist_items = _ensure_list(artifacts.get(hist_key))
    if not hist_items:
        errors.append(f"artifacts.{hist_key} should be non-empty (historical Event nodes).")
    for idx, item in enumerate(hist_items):
        if not isinstance(item, dict):
            errors.append(f"{hist_key}[{idx}] must be an object.")
            continue
        props = _non_null_dict(item.get("properties"), f"{hist_key}[{idx}].properties", errors)
        if not str(props.get("name") or "").strip():
            errors.append(f"{hist_key}[{idx}].properties.name should be set.")
        if props.get("is_historical") is not True:
            errors.append(f"{hist_key}[{idx}].properties.is_historical should be true.")
    magic = artifacts.get("magic_system")
    if not isinstance(magic, dict):
        errors.append("artifacts.magic_system must be a single object.")
    else:
        _non_null_dict(magic.get("properties"), "magic_system.properties", errors)
        _non_null_dict(magic.get("iceberg_notes"), "magic_system.iceberg_notes", errors)
    conns = _ensure_list(artifacts.get("location_connections"))
    if not conns:
        errors.append("artifacts.location_connections should be non-empty when geography exists.")
    for idx, edge in enumerate(conns):
        if not isinstance(edge, dict):
            errors.append(f"location_connections[{idx}] must be an object.")
            continue
        from_id = str(edge.get("from") or edge.get("from_node") or "").strip()
        to_id = str(edge.get("to") or edge.get("to_node") or "").strip()
        if not from_id or not to_id:
            errors.append(f"location_connections[{idx}] needs non-empty from and to (logical_ids).")
    return errors


def validate_character_conception_artifacts(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    concept = artifacts.get("character_concept")
    if isinstance(concept, str):
        errors.append(
            "artifacts.character_concept must be a structured object (not a single string); "
            "see skills/character-conception/SKILL.md."
        )
        return errors
    concept_d = _non_null_dict(concept, "artifacts.character_concept", errors)
    if not concept_d:
        errors.append("artifacts.character_concept is required for character-conception.")
        return errors
    for field in ("assigned_narrative_role", "generation_method", "core_contradiction", "sketch"):
        if not str(concept_d.get(field) or "").strip():
            errors.append(f"character_concept.{field} should be non-empty.")
    oq = _ensure_list(concept_d.get("open_questions"))
    if not oq:
        errors.append("character_concept.open_questions should be a non-empty list.")
    _non_null_dict(artifacts.get("provisional_flag"), "artifacts.provisional_flag", errors)
    _non_null_dict(artifacts.get("kg_context_used"), "artifacts.kg_context_used", errors)
    return errors


def validate_character_creation_artifacts(artifacts: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    node = _non_null_dict(artifacts.get("character_node"), "artifacts.character_node", errors)
    if not node:
        errors.append("artifacts.character_node is required for character-creation persistence.")
        return errors
    if not str(node.get("logical_id") or "").strip():
        errors.append("character_node.logical_id is required.")
    props = _non_null_dict(node.get("properties"), "character_node.properties", errors)
    if not str(props.get("full_name") or props.get("name") or "").strip():
        errors.append("character_node.properties.full_name (or name) should be set.")
    voice = props.get("voice_profile")
    if voice is None:
        errors.append("character_node.properties.voice_profile must not be null (use {{}} if unknown).")
    elif not isinstance(voice, dict):
        errors.append("character_node.properties.voice_profile must be an object.")
    rp = props.get("response_patterns")
    if rp is None:
        errors.append("character_node.properties.response_patterns must not be null (use {{}}).")
    elif not isinstance(rp, dict):
        errors.append("character_node.properties.response_patterns must be an object.")
    for key in ("knowledge_items", "new_knowledge_items"):
        for idx, ki in enumerate(_ensure_list(artifacts.get(key))):
            if not isinstance(ki, dict):
                errors.append(f"{key}[{idx}] must be an object.")
                continue
            if not str(ki.get("logical_id") or "").strip():
                errors.append(f"{key}[{idx}].logical_id is required.")
    for key in ("knowledge_matrix_edges", "new_knows_edges"):
        for idx, edge in enumerate(_ensure_list(artifacts.get(key))):
            if not isinstance(edge, dict):
                errors.append(f"{key}[{idx}] must be an object.")
                continue
            if not str(edge.get("from") or edge.get("from_node") or "").strip():
                errors.append(f"{key}[{idx}] missing from/from_node.")
            if not str(edge.get("to") or edge.get("to_node") or "").strip():
                errors.append(f"{key}[{idx}] missing to/to_node.")
    for idx, edge in enumerate(_ensure_list(artifacts.get("new_relationship_edges"))):
        if not isinstance(edge, dict):
            errors.append(f"new_relationship_edges[{idx}] must be an object.")
            continue
        if not str(edge.get("from") or edge.get("from_node") or "").strip():
            errors.append(f"new_relationship_edges[{idx}] missing from/from_node.")
        if not str(edge.get("to") or edge.get("to_node") or "").strip():
            errors.append(f"new_relationship_edges[{idx}] missing to/to_node.")
    return errors


def audit_worker_artifacts(worker: str, artifacts: Mapping[str, Any], context: Mapping[str, Any]) -> List[str]:
    """Return human-readable validation errors; empty list means no issues detected for known shapes."""
    if worker not in {"planning_subagent", "character_subagent"}:
        return []
    art = _ensure_dict(artifacts)
    skill = str(context.get("skill") or "").lower()

    if worker == "character_subagent":
        if "character-creation" in skill or "character_creation" in skill:
            return validate_character_creation_artifacts(art)
        if "conception" in skill:
            return validate_character_conception_artifacts(art)
        if "character_node" in art:
            return validate_character_creation_artifacts(art)
        if "character_concept" in art:
            return validate_character_conception_artifacts(art)
        return []

    # planning_subagent — prefer explicit brain context.skill, then artifact shape.
    if "worldbuilding" in skill or "world_building" in skill:
        return validate_worldbuilding_artifacts(art)
    if "finding" in skill and "seed" in skill:
        return validate_finding_a_seed_artifacts(art)
    if "defining" in skill or "rough-endpoint" in skill:
        if "pass-2" in skill or "pass_2" in skill or "pass2" in skill:
            return validate_defining_rough_endpoints_pass2(art)
        if "pass-1" in skill or "pass_1" in skill or "pass1" in skill:
            return validate_defining_rough_endpoints_pass1(art)
        if art.get("pass") == 2 or art.get("plot_thread_seeds") or art.get("payoff_seeds"):
            return validate_defining_rough_endpoints_pass2(art)
        if art.get("pass") == 1 or ("draft_milestones" in art and "plot_thread_seeds" not in art):
            return validate_defining_rough_endpoints_pass1(art)

    if "political_power_map" in art or art.get("geography"):
        return validate_worldbuilding_artifacts(art)
    if art.get("pass") == 2 or art.get("plot_thread_seeds") or art.get("payoff_seeds"):
        return validate_defining_rough_endpoints_pass2(art)
    if art.get("pass") == 1 or ("draft_milestones" in art and "plot_thread_seeds" not in art):
        return validate_defining_rough_endpoints_pass1(art)
    if "seed_document" in art:
        return validate_finding_a_seed_artifacts(art)
    return []
