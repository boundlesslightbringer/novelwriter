import json
from typing import Any, Dict, List, Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_nodes


class CharacterCreationArtifacts(BaseModel):
    character_node: Dict[str, Any]
    knowledge_matrix_edges: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge_items: List[Dict[str, Any]] = Field(default_factory=list)
    relationship_edges: List[Dict[str, Any]] = Field(default_factory=list)
    culture_edge: Dict[str, Any] = Field(default_factory=dict)
    arc_type_note: str = ""
    provisional_expansion_flag: bool = False
    provisional_expansion_notes: str = ""


class CharacterCreationState(TypedDict, total=False):
    character_concept: Dict[str, Any]
    chapter_context: int
    research_output: Dict[str, Any]
    feedback: Dict[str, Any]
    missing_required_fields: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    warnings: List[str]
    validation_errors: List[str]
    faction_nodes: List[Dict[str, Any]]
    culture_nodes: List[Dict[str, Any]]
    location_nodes: List[Dict[str, Any]]
    existing_character_nodes: List[Dict[str, Any]]
    knowledge_item_nodes: List[Dict[str, Any]]
    kg_context_used: Dict[str, Any]
    synthesized_artifacts: Dict[str, Any]
    hardened_artifacts: Dict[str, Any]
    response_status: str
    response_summary: str
    response_artifacts: Dict[str, Any]


def _default_response_patterns() -> Dict[str, str]:
    return {
        "betrayal": "",
        "loss": "",
        "sudden_power": "",
        "helplessness": "",
        "unwanted_intimacy": "",
        "being_correctly_seen": "",
        "unexpected_kindness_from_enemy": "",
    }


def _default_artifacts(chapter_context: int) -> Dict[str, Any]:
    return {
        "character_node": {
            "logical_id": "",
            "node_type": "Character",
            "chapter": chapter_context,
            "properties": {
                "full_name": "",
                "aliases": [],
                "age": 0,
                "gender": "",
                "physical_description": "",
                "faction": "",
                "rank": "",
                "occupation": "",
                "public_vs_private_reputation": "",
                "location": "",
                "surface_beliefs": [],
                "core_wound": "",
                "core_desire": "",
                "core_fear": "",
                "self_deception": "",
                "values_under_pressure": [],
                "contradictions": [],
                "response_patterns": _default_response_patterns(),
                "arc_type": "",
                "arc_stage": "",
                "pov_eligible": False,
                "pov_chapter_count": 0,
                "last_pov_chapter": None,
                "injuries_physical_state": [],
                "emotional_state": "",
            },
        },
        "knowledge_matrix_edges": [],
        "knowledge_items": [],
        "relationship_edges": [],
        "culture_edge": {
            "logical_id": "",
            "edge_type": "BELONGS_TO_CULTURE",
            "from": "",
            "to": "",
            "from_node": "",
            "to_node": "",
            "chapter": chapter_context,
            "properties": {"role": ""},
        },
        "arc_type_note": "",
        "provisional_expansion_flag": False,
        "provisional_expansion_notes": "",
    }


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_edge(edge: Dict[str, Any], default_edge_type: str, default_chapter: int) -> Dict[str, Any]:
    normalized = dict(edge) if isinstance(edge, dict) else {}
    from_id = normalized.get("from") or normalized.get("from_node") or ""
    to_id = normalized.get("to") or normalized.get("to_node") or ""
    normalized["from"] = str(from_id)
    normalized["to"] = str(to_id)
    normalized["from_node"] = str(from_id)
    normalized["to_node"] = str(to_id)
    normalized["edge_type"] = str(normalized.get("edge_type") or default_edge_type)
    normalized["logical_id"] = str(normalized.get("logical_id") or "")
    normalized["chapter"] = int(normalized.get("chapter") or default_chapter)
    normalized["properties"] = _ensure_dict(normalized.get("properties"))
    return normalized


def _build_subgraph(subagent: Any) -> Any:
    skill_content = progressive_skill_loader.invoke(
        {"skill_name": "character-creation", "load_type": "full"}
    )

    model_kwargs: Dict[str, Any] = {"temperature": subagent.llm_config.temperature}
    if subagent.llm_config.top_p is not None:
        model_kwargs["top_p"] = subagent.llm_config.top_p
    if subagent.llm_config.top_k is not None:
        model_kwargs["top_k"] = subagent.llm_config.top_k

    llm = ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        **model_kwargs,
    ).with_structured_output(CharacterCreationArtifacts)

    graph = StateGraph(CharacterCreationState)

    def ingest_context(state: CharacterCreationState) -> CharacterCreationState:
        missing: List[str] = []
        chapter_context = state.get("chapter_context")
        if not _ensure_dict(state.get("character_concept")):
            missing.append("character_concept")
        if chapter_context is None or chapter_context == "":
            missing.append("chapter_context")
        try:
            normalized_chapter = int(chapter_context)
        except (TypeError, ValueError):
            normalized_chapter = 0
            if "chapter_context" not in missing:
                missing.append("chapter_context")

        return {
            "chapter_context": normalized_chapter,
            "character_concept": _ensure_dict(state.get("character_concept")),
            "research_output": _ensure_dict(state.get("research_output")),
            "feedback": _ensure_dict(state.get("feedback")),
            "missing_required_fields": missing,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required character-creation context fields: {', '.join(missing)}."
                if missing
                else None
            ),
            "warnings": [],
            "validation_errors": [],
            "kg_context_used": {
                "faction_nodes_found": 0,
                "culture_nodes_found": 0,
                "location_nodes_found": 0,
                "existing_characters_found": 0,
                "knowledge_items_found": 0,
                "query_warnings": 0,
            },
            "synthesized_artifacts": _default_artifacts(normalized_chapter),
            "hardened_artifacts": _default_artifacts(normalized_chapter),
        }

    def route_required_inputs(state: CharacterCreationState) -> Literal["need_input_exit", "fetch_kg_context"]:
        if state.get("missing_required_fields"):
            return "need_input_exit"
        return "fetch_kg_context"

    def need_input_exit(state: CharacterCreationState) -> CharacterCreationState:
        defaults = _default_artifacts(int(state.get("chapter_context", 0)))
        return {
            "response_status": "need_input",
            "response_summary": state.get("terminal_summary") or "Missing required input for character creation.",
            "response_artifacts": {
                "error": "missing_required_fields",
                "missing_fields": state.get("missing_required_fields", []),
                "warnings": state.get("warnings", []),
                "kg_context_used": state.get("kg_context_used", {}),
                **defaults,
            },
        }

    def fetch_kg_context(state: CharacterCreationState) -> CharacterCreationState:
        chapter_context = int(state.get("chapter_context", 0))
        warnings: List[str] = list(state.get("warnings", []))

        def safe_query(node_type: str) -> List[Dict[str, Any]]:
            try:
                return query_kg_nodes.invoke(
                    {"query": {"type": node_type}, "as_of_chapter": chapter_context}
                )
            except Exception as error:
                warnings.append(f"{node_type} query failed: {error}")
                return []

        faction_nodes = safe_query("Faction")
        culture_nodes = safe_query("Culture")
        location_nodes = safe_query("Location")
        existing_character_nodes = safe_query("Character")
        knowledge_item_nodes = safe_query("KnowledgeItem")

        return {
            "faction_nodes": faction_nodes,
            "culture_nodes": culture_nodes,
            "location_nodes": location_nodes,
            "existing_character_nodes": existing_character_nodes,
            "knowledge_item_nodes": knowledge_item_nodes,
            "warnings": warnings,
            "kg_context_used": {
                "faction_nodes_found": len(faction_nodes),
                "culture_nodes_found": len(culture_nodes),
                "location_nodes_found": len(location_nodes),
                "existing_characters_found": len(existing_character_nodes),
                "knowledge_items_found": len(knowledge_item_nodes),
                "query_warnings": len(warnings),
            },
        }

    def synthesize_character_creation(state: CharacterCreationState) -> CharacterCreationState:
        chapter_context = int(state.get("chapter_context", 0))
        warnings: List[str] = list(state.get("warnings", []))
        validation_errors: List[str] = list(state.get("validation_errors", []))
        fallback_artifacts = _default_artifacts(chapter_context)

        llm_payload = {
            "character_concept": state.get("character_concept", {}),
            "chapter_context": chapter_context,
            "research_output": state.get("research_output", {}),
            "feedback": state.get("feedback", {}),
            "kg_context": {
                "faction_nodes": state.get("faction_nodes", []),
                "culture_nodes": state.get("culture_nodes", []),
                "location_nodes": state.get("location_nodes", []),
                "existing_character_nodes": state.get("existing_character_nodes", []),
                "knowledge_item_nodes": state.get("knowledge_item_nodes", []),
            },
        }
        prompt = (
            f"{skill_content}\n\n"
            "Return only structured JSON for the full artifacts payload.\n"
            "Do not return null for nested required objects; use empty strings or arrays when uncertain.\n"
            "Include character_node, knowledge_matrix_edges, knowledge_items, relationship_edges, culture_edge, "
            "arc_type_note, provisional_expansion_flag, and provisional_expansion_notes.\n\n"
            f"{_safe_json(llm_payload)}"
        )

        try:
            llm_result: CharacterCreationArtifacts = llm.invoke([HumanMessage(content=prompt)])
            synthesized = llm_result.model_dump()
        except Exception as error:
            warnings.append(f"Character creation synthesis failed: {error}")
            validation_errors.append("synthesis_failed")
            synthesized = fallback_artifacts

        return {
            "synthesized_artifacts": synthesized,
            "warnings": warnings,
            "validation_errors": validation_errors,
        }

    def validate_and_harden_artifacts(state: CharacterCreationState) -> CharacterCreationState:
        chapter_context = int(state.get("chapter_context", 0))
        artifacts = _ensure_dict(state.get("synthesized_artifacts"))
        validation_errors: List[str] = list(state.get("validation_errors", []))

        hardened = _default_artifacts(chapter_context)

        character_node = _ensure_dict(artifacts.get("character_node"))
        char_props = _ensure_dict(character_node.get("properties"))
        default_props = hardened["character_node"]["properties"]
        merged_props = {**default_props, **char_props}
        merged_props["aliases"] = _ensure_list(merged_props.get("aliases"))
        merged_props["surface_beliefs"] = _ensure_list(merged_props.get("surface_beliefs"))
        merged_props["values_under_pressure"] = _ensure_list(merged_props.get("values_under_pressure"))
        merged_props["contradictions"] = _ensure_list(merged_props.get("contradictions"))
        merged_props["injuries_physical_state"] = _ensure_list(merged_props.get("injuries_physical_state"))
        response_patterns = _ensure_dict(merged_props.get("response_patterns"))
        merged_props["response_patterns"] = {**_default_response_patterns(), **response_patterns}
        if merged_props.get("last_pov_chapter", "") == "":
            merged_props["last_pov_chapter"] = None

        hardened["character_node"] = {
            **hardened["character_node"],
            **character_node,
            "logical_id": str(character_node.get("logical_id") or ""),
            "node_type": "Character",
            "chapter": int(character_node.get("chapter") or chapter_context),
            "properties": merged_props,
        }

        if not hardened["character_node"]["logical_id"]:
            validation_errors.append("character_node.logical_id is empty")

        hardened["knowledge_items"] = []
        for item in _ensure_list(artifacts.get("knowledge_items")):
            item_dict = _ensure_dict(item)
            item_props = _ensure_dict(item_dict.get("properties"))
            hardened["knowledge_items"].append(
                {
                    **item_dict,
                    "logical_id": str(item_dict.get("logical_id") or ""),
                    "node_type": str(item_dict.get("node_type") or "KnowledgeItem"),
                    "chapter": int(item_dict.get("chapter") or chapter_context),
                    "properties": {"description": str(item_props.get("description") or "")},
                }
            )

        hardened["knowledge_matrix_edges"] = [
            _normalize_edge(_ensure_dict(edge), "KNOWS", chapter_context)
            for edge in _ensure_list(artifacts.get("knowledge_matrix_edges"))
        ]
        hardened["relationship_edges"] = [
            _normalize_edge(_ensure_dict(edge), "RELATIONSHIP", chapter_context)
            for edge in _ensure_list(artifacts.get("relationship_edges"))
        ]

        culture_edge = _normalize_edge(
            _ensure_dict(artifacts.get("culture_edge")),
            "BELONGS_TO_CULTURE",
            chapter_context,
        )
        culture_edge["properties"] = {"role": str(culture_edge.get("properties", {}).get("role") or "")}
        hardened["culture_edge"] = culture_edge

        hardened["arc_type_note"] = str(artifacts.get("arc_type_note") or "")
        hardened["provisional_expansion_flag"] = bool(artifacts.get("provisional_expansion_flag", False))
        hardened["provisional_expansion_notes"] = str(artifacts.get("provisional_expansion_notes") or "")

        return {"hardened_artifacts": hardened, "validation_errors": validation_errors}

    def route_after_validation(state: CharacterCreationState) -> Literal["package_success", "package_blocked"]:
        if state.get("validation_errors"):
            return "package_blocked"
        return "package_success"

    def package_success(state: CharacterCreationState) -> CharacterCreationState:
        artifacts = {
            **state.get("hardened_artifacts", _default_artifacts(int(state.get("chapter_context", 0)))),
            "kg_context_used": state.get("kg_context_used", {}),
            "warnings": state.get("warnings", []),
            "validation_errors": [],
        }
        return {
            "response_status": "success",
            "response_summary": "Generated character records via character-creation subgraph.",
            "response_artifacts": artifacts,
        }

    def package_blocked(state: CharacterCreationState) -> CharacterCreationState:
        artifacts = {
            **state.get("hardened_artifacts", _default_artifacts(int(state.get("chapter_context", 0)))),
            "kg_context_used": state.get("kg_context_used", {}),
            "warnings": state.get("warnings", []),
            "validation_errors": state.get("validation_errors", []),
        }
        return {
            "response_status": "blocked",
            "response_summary": "Character creation produced invalid or partial artifacts that need review.",
            "response_artifacts": artifacts,
        }

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("need_input_exit", need_input_exit)
    graph.add_node("fetch_kg_context", fetch_kg_context)
    graph.add_node("synthesize_character_creation", synthesize_character_creation)
    graph.add_node("validate_and_harden_artifacts", validate_and_harden_artifacts)
    graph.add_node("package_success", package_success)
    graph.add_node("package_blocked", package_blocked)

    graph.add_edge(START, "ingest_context")
    graph.add_conditional_edges(
        "ingest_context",
        route_required_inputs,
        {"need_input_exit": "need_input_exit", "fetch_kg_context": "fetch_kg_context"},
    )
    graph.add_edge("need_input_exit", END)
    graph.add_edge("fetch_kg_context", "synthesize_character_creation")
    graph.add_edge("synthesize_character_creation", "validate_and_harden_artifacts")
    graph.add_conditional_edges(
        "validate_and_harden_artifacts",
        route_after_validation,
        {"package_success": "package_success", "package_blocked": "package_blocked"},
    )
    graph.add_edge("package_success", END)
    graph.add_edge("package_blocked", END)

    return graph.compile()


def run_character_creation_subgraph(
    subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {})
    context = worker_request.get("context", {})

    initial_state: CharacterCreationState = {
        "character_concept": _ensure_dict(context.get("character_concept")),
        "chapter_context": context.get("chapter_context"),
        "research_output": _ensure_dict(context.get("research_output")),
        "feedback": _ensure_dict(context.get("feedback")),
    }

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})
        structured_result = WorkerResponse(
            status=str(graph_result.get("response_status") or "failed"),
            summary=str(graph_result.get("response_summary") or "Character creation subgraph failed."),
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
        "task": worker_request.get("task", ""),
        "context": context,
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }
