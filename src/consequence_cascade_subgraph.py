import json
import re
from typing import Any, Dict, List, Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_edges, query_kg_nodes


class LinkageDecision(BaseModel):
    action: Literal["create_new", "extend_existing"] = "create_new"
    existing_chain_id: str = ""
    rationale: str = ""


class ConsequenceRecord(BaseModel):
    affected_entity: str = ""
    description: str = ""
    chapter_reference: int = 0
    projected_chapters: str = ""
    bomb_id: str = ""


class ImmediateAndShortTermOutput(BaseModel):
    immediate: List[ConsequenceRecord] = Field(default_factory=list)
    short_term: List[ConsequenceRecord] = Field(default_factory=list)
    long_term_pending: List[ConsequenceRecord] = Field(default_factory=list)


class BombProperties(BaseModel):
    type: str = "Consequence bomb"
    description: str = ""
    planted_in_chapter: int = 0
    detonation_trigger: str = ""
    narrative_phase_anchor: Literal["early", "mid", "convergence", "final act"] = "mid"
    resolution_status: str = "Pending"
    priority_tier: Literal["Essential", "Enriching", "Unclassified"] = "Unclassified"
    dual_register: bool = False


class ConsequenceBomb(BaseModel):
    logical_id: str = ""
    node_type: str = "Payoff"
    chapter: int = 0
    properties: BombProperties = Field(default_factory=BombProperties)


class BombsOutput(BaseModel):
    consequence_bombs: List[ConsequenceBomb] = Field(default_factory=list)


class CharacterStateUpdate(BaseModel):
    logical_id: str = ""
    updated_properties: Dict[str, Any] = Field(default_factory=dict)
    chapter: int = 0


class RelationshipUpdate(BaseModel):
    logical_id: str = ""
    updated_properties: Dict[str, Any] = Field(default_factory=dict)
    chapter: int = 0


class KnowledgeEdge(BaseModel):
    logical_id: str = ""
    edge_type: str = "KNOWS"
    from_: str = Field(default="", alias="from")
    to: str = ""
    chapter: int = 0
    properties: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class KnowledgeItem(BaseModel):
    logical_id: str = ""
    node_type: str = "KnowledgeItem"
    chapter: int = 0
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeMatrixUpdate(BaseModel):
    character_id: str = ""
    new_knows_edges: List[KnowledgeEdge] = Field(default_factory=list)
    new_knowledge_items: List[KnowledgeItem] = Field(default_factory=list)


class StateRelKnowledgeOutput(BaseModel):
    character_state_updates: List[CharacterStateUpdate] = Field(default_factory=list)
    relationship_updates: List[RelationshipUpdate] = Field(default_factory=list)
    knowledge_matrix_updates: List[KnowledgeMatrixUpdate] = Field(default_factory=list)


class ConsequenceCascadeState(TypedDict, total=False):
    task: str
    context: Dict[str, Any]
    triggering_event: str
    chapter_context: int
    affected_character_ids: List[str]
    missing_required_fields: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    character_nodes: List[Dict[str, Any]]
    relationship_edges: List[Dict[str, Any]]
    cascade_chains: List[Dict[str, Any]]
    existing_bombs: List[Dict[str, Any]]
    missing_character_ids: List[str]
    skill_contract: str
    linkage_decision: Dict[str, Any]
    immediate_short: Dict[str, Any]
    bombs_payload: Dict[str, Any]
    state_rel_knowledge_payload: Dict[str, Any]
    artifacts: Dict[str, Any]
    kg_context_used: Dict[str, Any]
    warnings: List[str]
    validation_errors: List[str]
    summary: str


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _build_llm(subagent: Any) -> ChatGoogleGenerativeAI:
    kwargs: Dict[str, Any] = {"temperature": subagent.llm_config.temperature}
    if subagent.llm_config.top_p is not None:
        kwargs["top_p"] = subagent.llm_config.top_p
    if subagent.llm_config.top_k is not None:
        kwargs["top_k"] = subagent.llm_config.top_k
    return ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        **kwargs,
    )


def _default_kg_context() -> Dict[str, Any]:
    return {
        "character_nodes_found": 0,
        "relationship_edges_found": 0,
        "existing_cascade_chains_found": 0,
        "existing_pending_bombs_found": 0,
        "missing_character_ids": [],
        "chain_action": "create_new",
    }


def _build_subgraph(subagent: Any) -> Any:
    llm = _build_llm(subagent)
    graph = StateGraph(ConsequenceCascadeState)

    def ingest_context(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        missing: List[str] = []
        for field in ("triggering_event", "chapter_context", "affected_character_ids"):
            value = state.get(field)
            if value is None or value == "" or value == 0 or value == []:
                missing.append(field)
        return {
            "missing_required_fields": missing,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required consequence cascade context fields: {', '.join(missing)}."
                if missing
                else None
            ),
            "kg_context_used": _default_kg_context(),
            "warnings": [],
            "validation_errors": [],
        }

    def prefetch_kg(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        chapter_context = int(state["chapter_context"])
        affected_ids = state.get("affected_character_ids", [])
        warnings = list(state.get("warnings", []))

        character_nodes: List[Dict[str, Any]] = []
        relationship_edges: List[Dict[str, Any]] = []
        cascade_chains: List[Dict[str, Any]] = []
        existing_bombs: List[Dict[str, Any]] = []

        try:
            character_nodes = query_kg_nodes.invoke(
                {
                    "query": {
                        "type": "Character",
                        "logical_id": {"$in": affected_ids},
                    },
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            warnings.append(f"Character query failed: {error}")

        try:
            relationship_edges = query_kg_edges.invoke(
                {
                    "query": {
                        "type": "RELATIONSHIP",
                        "from": {"$in": affected_ids},
                        "to": {"$in": affected_ids},
                    },
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            warnings.append(f"RELATIONSHIP query failed: {error}")

        try:
            cascade_chains = query_kg_nodes.invoke(
                {"query": {"type": "CascadeChain"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            warnings.append(f"CascadeChain query failed: {error}")

        try:
            existing_bombs = query_kg_nodes.invoke(
                {
                    "query": {
                        "type": "Payoff",
                        "properties.type": "Consequence bomb",
                        "properties.resolution_status": "Pending",
                    },
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            warnings.append(f"Payoff query failed: {error}")

        found_ids = {
            node.get("logical_id", "")
            for node in character_nodes
            if isinstance(node, dict) and node.get("logical_id")
        }
        missing_character_ids = [cid for cid in affected_ids if cid not in found_ids]

        kg_context_used = {
            "character_nodes_found": len(character_nodes),
            "relationship_edges_found": len(relationship_edges),
            "existing_cascade_chains_found": len(cascade_chains),
            "existing_pending_bombs_found": len(existing_bombs),
            "missing_character_ids": missing_character_ids,
            "chain_action": "create_new",
        }
        return {
            "character_nodes": character_nodes,
            "relationship_edges": relationship_edges,
            "cascade_chains": cascade_chains,
            "existing_bombs": existing_bombs,
            "missing_character_ids": missing_character_ids,
            "kg_context_used": kg_context_used,
            "warnings": warnings,
        }

    def load_skill(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        skill_contract = progressive_skill_loader.invoke(
            {"skill_name": "consequence-cascade-implementation", "load_type": "full"}
        )
        return {"skill_contract": str(skill_contract)}

    def linkage_decision(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        structured_llm = llm.with_structured_output(LinkageDecision)
        payload = {
            "triggering_event": state.get("triggering_event", ""),
            "chapter_context": state.get("chapter_context", 0),
            "cascade_chains": state.get("cascade_chains", []),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Decide whether this event starts a new cascade chain or extends an existing one.\n"
            "Return only structured JSON with action, existing_chain_id, and rationale.\n\n"
            f"{_safe_json(payload)}"
        )
        result: LinkageDecision = structured_llm.invoke([HumanMessage(content=prompt)])
        linkage = result.model_dump()
        return {"linkage_decision": linkage}

    def trace_immediate_short(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        structured_llm = llm.with_structured_output(ImmediateAndShortTermOutput)
        payload = {
            "triggering_event": state.get("triggering_event", ""),
            "chapter_context": state.get("chapter_context", 0),
            "affected_character_ids": state.get("affected_character_ids", []),
            "character_nodes": state.get("character_nodes", []),
            "relationship_edges": state.get("relationship_edges", []),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Trace immediate, short-term, and long-term pending consequences.\n"
            "Keep outputs concrete and structured. No prose.\n\n"
            f"{_safe_json(payload)}"
        )
        result: ImmediateAndShortTermOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        return {"immediate_short": result.model_dump()}

    def bombs_and_tiers(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        structured_llm = llm.with_structured_output(BombsOutput)
        payload = {
            "triggering_event": state.get("triggering_event", ""),
            "chapter_context": state.get("chapter_context", 0),
            "long_term_pending": state.get("immediate_short", {}).get("long_term_pending", []),
            "existing_bombs": state.get("existing_bombs", []),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Create Payoff payloads for consequence bombs with priority tiers.\n"
            "Use condition-based detonation triggers only.\n\n"
            f"{_safe_json(payload)}"
        )
        result: BombsOutput = structured_llm.invoke([HumanMessage(content=prompt)])

        normalized_bombs: List[Dict[str, Any]] = []
        for bomb in result.consequence_bombs:
            bomb_payload = bomb.model_dump()
            props = dict(bomb_payload.get("properties", {}))
            props["dual_register"] = props.get("priority_tier") == "Essential"
            if not bomb_payload.get("chapter"):
                bomb_payload["chapter"] = int(state.get("chapter_context", 0))
            if not props.get("planted_in_chapter"):
                props["planted_in_chapter"] = int(state.get("chapter_context", 0))
            bomb_payload["properties"] = props
            normalized_bombs.append(bomb_payload)
        return {"bombs_payload": {"consequence_bombs": normalized_bombs}}

    def state_rel_knowledge(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        structured_llm = llm.with_structured_output(StateRelKnowledgeOutput)
        payload = {
            "triggering_event": state.get("triggering_event", ""),
            "chapter_context": state.get("chapter_context", 0),
            "affected_character_ids": state.get("affected_character_ids", []),
            "character_nodes": state.get("character_nodes", []),
            "relationship_edges": state.get("relationship_edges", []),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Generate character updates, relationship updates, and knowledge matrix updates.\n"
            "Return a canonical list shape for knowledge_matrix_updates.\n\n"
            f"{_safe_json(payload)}"
        )
        result: StateRelKnowledgeOutput = structured_llm.invoke([HumanMessage(content=prompt)])

        chapter_context = int(state.get("chapter_context", 0))
        output = result.model_dump(by_alias=True)
        for update in output.get("character_state_updates", []):
            if not update.get("chapter"):
                update["chapter"] = chapter_context
        for update in output.get("relationship_updates", []):
            if not update.get("chapter"):
                update["chapter"] = chapter_context
        for knowledge_update in output.get("knowledge_matrix_updates", []):
            for edge in knowledge_update.get("new_knows_edges", []):
                if not edge.get("chapter"):
                    edge["chapter"] = chapter_context
            for item in knowledge_update.get("new_knowledge_items", []):
                if not item.get("chapter"):
                    item["chapter"] = chapter_context

        return {"state_rel_knowledge_payload": output}

    def assemble(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        chapter_context = int(state.get("chapter_context", 0))
        linkage = dict(state.get("linkage_decision", {}))
        immediate_short = dict(state.get("immediate_short", {}))
        bombs = dict(state.get("bombs_payload", {}))
        updates = dict(state.get("state_rel_knowledge_payload", {}))

        cascade_chain: Dict[str, Any] = {
            "action": linkage.get("action", "create_new"),
            "existing_chain_id": linkage.get("existing_chain_id", ""),
            "node": {
                "logical_id": f"cc_ch{chapter_context}_event",
                "node_type": "CascadeChain",
                "chapter": chapter_context,
                "properties": {
                    "sequence": [
                        state.get("triggering_event", ""),
                        *[item.get("description", "") for item in immediate_short.get("immediate", [])[:1]],
                        *[item.get("description", "") for item in immediate_short.get("short_term", [])[:1]],
                        *[
                            item.get("description", "")
                            for item in immediate_short.get("long_term_pending", [])[:1]
                        ],
                    ],
                    "current_position": state.get("triggering_event", ""),
                    "remaining_links": [
                        item.get("description", "") for item in immediate_short.get("short_term", [])
                    ]
                    + [item.get("description", "") for item in immediate_short.get("long_term_pending", [])],
                },
            },
            "update_existing": {},
        }

        if cascade_chain["action"] == "extend_existing":
            cascade_chain["node"] = {}
            cascade_chain["update_existing"] = {
                "logical_id": linkage.get("existing_chain_id", ""),
                "updated_properties": {
                    "current_position": state.get("triggering_event", ""),
                },
                "chapter": chapter_context,
            }
        else:
            cascade_chain["existing_chain_id"] = ""
            cascade_chain["update_existing"] = {}

        kg_context_used = dict(state.get("kg_context_used", _default_kg_context()))
        kg_context_used["chain_action"] = cascade_chain["action"]

        artifacts = {
            "triggering_event_summary": f"{state.get('triggering_event', '')} (chapter {chapter_context})",
            "cascade_chain": cascade_chain,
            "consequence_chain_entry": {
                "node_type": "CascadeChain",
                "event_consequences": {
                    "immediate": immediate_short.get("immediate", []),
                    "short_term": immediate_short.get("short_term", []),
                    "long_term_pending": immediate_short.get("long_term_pending", []),
                },
            },
            "consequence_bombs": bombs.get("consequence_bombs", []),
            "character_state_updates": updates.get("character_state_updates", []),
            "relationship_updates": updates.get("relationship_updates", []),
            "knowledge_matrix_updates": updates.get("knowledge_matrix_updates", []),
            "kg_context_used": kg_context_used,
        }
        return {"artifacts": artifacts, "kg_context_used": kg_context_used}

    def validate(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        artifacts = dict(state.get("artifacts", {}))
        errors: List[str] = []

        action = artifacts.get("cascade_chain", {}).get("action")
        if action not in {"create_new", "extend_existing"}:
            errors.append("cascade_chain.action must be create_new or extend_existing.")

        for list_key in (
            "consequence_bombs",
            "character_state_updates",
            "relationship_updates",
            "knowledge_matrix_updates",
        ):
            if artifacts.get(list_key) is None:
                errors.append(f"{list_key} must not be null.")

        detonation_pattern = re.compile(r"\bch(?:apter)?\.?\s*\d", re.IGNORECASE)
        for bomb in artifacts.get("consequence_bombs", []):
            trigger = str(bomb.get("properties", {}).get("detonation_trigger", "")).strip()
            if not trigger:
                errors.append("Every consequence bomb must include detonation_trigger.")
            elif detonation_pattern.search(trigger):
                errors.append("Detonation triggers must be condition-based, not chapter-anchored.")

        for kmu in artifacts.get("knowledge_matrix_updates", []):
            if not isinstance(kmu, dict):
                errors.append("knowledge_matrix_updates entries must be objects.")
                continue
            if kmu.get("new_knows_edges") is None or kmu.get("new_knowledge_items") is None:
                errors.append("knowledge_matrix_updates nested lists must never be null.")

        return {"validation_errors": errors}

    def package_success(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        summary = "Executed consequence-cascade-implementation via internal subgraph."
        if state.get("warnings"):
            summary = "Executed consequence cascade with recoverable KG warning(s)."
        return {"summary": summary}

    def package_need_input(state: ConsequenceCascadeState) -> ConsequenceCascadeState:
        return {
            "summary": state.get("terminal_summary", "Missing required context for consequence cascade.")
        }

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("prefetch_kg", prefetch_kg)
    graph.add_node("load_skill", load_skill)
    graph.add_node("linkage_decision", linkage_decision)
    graph.add_node("trace_immediate_short", trace_immediate_short)
    graph.add_node("bombs_and_tiers", bombs_and_tiers)
    graph.add_node("state_rel_knowledge", state_rel_knowledge)
    graph.add_node("assemble", assemble)
    graph.add_node("validate", validate)
    graph.add_node("package_success", package_success)
    graph.add_node("package_need_input", package_need_input)

    graph.add_edge(START, "ingest_context")

    def route_after_ingest(
        state: ConsequenceCascadeState,
    ) -> Literal["package_need_input", "prefetch_kg"]:
        if state.get("terminal_status"):
            return "package_need_input"
        return "prefetch_kg"

    graph.add_conditional_edges(
        "ingest_context",
        route_after_ingest,
        {
            "package_need_input": "package_need_input",
            "prefetch_kg": "prefetch_kg",
        },
    )
    graph.add_edge("prefetch_kg", "load_skill")
    graph.add_edge("load_skill", "linkage_decision")
    graph.add_edge("linkage_decision", "trace_immediate_short")
    graph.add_edge("trace_immediate_short", "bombs_and_tiers")
    graph.add_edge("bombs_and_tiers", "state_rel_knowledge")
    graph.add_edge("state_rel_knowledge", "assemble")
    graph.add_edge("assemble", "validate")
    graph.add_edge("validate", "package_success")
    graph.add_edge("package_success", END)
    graph.add_edge("package_need_input", END)

    return graph.compile()


def run_consequence_cascade_subgraph(
    subagent: Any,
    state: Dict[str, Any],
    config: RunnableConfig | None = None,
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}
    task = str(worker_request.get("task", "") or "")
    initial_state: ConsequenceCascadeState = {
        "task": task,
        "context": context,
        "triggering_event": str(context.get("triggering_event", "") or ""),
        "chapter_context": int(context.get("chapter_context", 0) or 0),
        "affected_character_ids": context.get("affected_character_ids", []) or [],
    }

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})
        missing = graph_result.get("missing_required_fields", [])
        validation_errors = graph_result.get("validation_errors", [])

        if missing:
            structured_result = WorkerResponse(
                status="need_input",
                summary=graph_result.get("summary", "Missing required context for consequence cascade."),
                artifacts={
                    "error": "missing_required_context",
                    "missing_fields": missing,
                    "triggering_event_summary": "",
                    "cascade_chain": {
                        "action": "create_new",
                        "existing_chain_id": "",
                        "node": {},
                        "update_existing": {},
                    },
                    "consequence_chain_entry": {
                        "node_type": "CascadeChain",
                        "event_consequences": {
                            "immediate": [],
                            "short_term": [],
                            "long_term_pending": [],
                        },
                    },
                    "consequence_bombs": [],
                    "character_state_updates": [],
                    "relationship_updates": [],
                    "knowledge_matrix_updates": [],
                    "kg_context_used": _default_kg_context(),
                },
            ).model_dump()
        elif validation_errors:
            artifacts = graph_result.get("artifacts", {}) or {}
            artifacts["validation_errors"] = validation_errors
            artifacts["warnings"] = graph_result.get("warnings", [])
            structured_result = WorkerResponse(
                status="failed",
                summary="Consequence cascade validation failed.",
                artifacts=artifacts,
            ).model_dump()
        else:
            artifacts = graph_result.get("artifacts", {}) or {}
            artifacts["warnings"] = graph_result.get("warnings", [])
            structured_result = WorkerResponse(
                status="success",
                summary=graph_result.get(
                    "summary",
                    "Executed consequence-cascade-implementation via internal subgraph.",
                ),
                artifacts=artifacts,
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
