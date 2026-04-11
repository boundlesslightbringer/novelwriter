import json
from typing import Any, Dict, List, Literal

from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_nodes


class WorldNodeRecord(BaseModel):
    node_type: str = ""
    properties: Dict[str, Any] = Field(default_factory=dict)
    iceberg_notes: Dict[str, Any] = Field(default_factory=dict)


class HistoryEventRecord(BaseModel):
    node_type: str = "Event"
    properties: Dict[str, Any] = Field(default_factory=dict)


class MagicSystemRecord(BaseModel):
    node_type: str = "MagicSystem"
    properties: Dict[str, Any] = Field(default_factory=dict)
    iceberg_notes: Dict[str, Any] = Field(default_factory=dict)


class LocationConnectionRecord(BaseModel):
    edge_type: str = "CONNECTED_TO"
    from_node: str = ""
    to_node: str = ""
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeoPoliticsBundleOutput(BaseModel):
    geography: List[WorldNodeRecord] = Field(default_factory=list)
    political_power_map: List[WorldNodeRecord] = Field(default_factory=list)


class CultureHistoryBundleOutput(BaseModel):
    cultures_customs_religion: List[WorldNodeRecord] = Field(default_factory=list)
    history_and_legends: List[HistoryEventRecord] = Field(default_factory=list)


class MagicOutput(BaseModel):
    magic_system: MagicSystemRecord = Field(default_factory=MagicSystemRecord)


class ConnectionsOutput(BaseModel):
    location_connections: List[LocationConnectionRecord] = Field(default_factory=list)


class WorldbuildingState(TypedDict, total=False):
    context: Dict[str, Any]
    skill_contract: str
    chapter_context: int
    targeted_expansion: bool
    missing_required_fields: List[str]
    follow_up_questions: List[str]
    terminal_status: str | None
    terminal_summary: str | None
    warnings: List[str]
    existing_factions: List[Dict[str, Any]]
    existing_locations: List[Dict[str, Any]]
    existing_cultures: List[Dict[str, Any]]
    existing_magic_systems: List[Dict[str, Any]]
    existing_historical_events: List[Dict[str, Any]]
    bundle_a: Dict[str, Any]
    bundle_b: Dict[str, Any]
    geography: List[Dict[str, Any]]
    political_power_map: List[Dict[str, Any]]
    cultures_customs_religion: List[Dict[str, Any]]
    history_and_legends: List[Dict[str, Any]]
    magic_system: Dict[str, Any]
    location_connections: List[Dict[str, Any]]
    kg_context_used: Dict[str, Any]
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


def _summarize_kg_nodes(nodes: List[Dict[str, Any]], limit: int = 15) -> List[Dict[str, Any]]:
    summarized: List[Dict[str, Any]] = []
    for node in nodes[:limit]:
        props = node.get("properties") if isinstance(node.get("properties"), dict) else {}
        summarized.append(
            {
                "logical_id": node.get("logical_id", ""),
                "type": node.get("type", ""),
                "name": props.get("name", ""),
            }
        )
    return summarized


def _build_skill_contract(full_skill: str) -> str:
    lines = full_skill.splitlines()
    max_lines = 130
    head = "\n".join(lines[:max_lines])
    trailer = ""
    if len(lines) > max_lines:
        trailer = (
            "\n\n[Contract: Remaining SKILL.md lines omitted for token budget. "
            "Still enforce: no prose, no character records, iceberg depth, causal "
            "links geography→politics→culture→history→magic, KG-ready node shapes, "
            "historical Event.properties.is_historical=true.]"
        )
    return "## Worldbuilding authoritative excerpt (from official SKILL.md)\n" + head + trailer


def _default_magic_system() -> Dict[str, Any]:
    return {
        "node_type": "MagicSystem",
        "properties": {
            "prevalence": "Stable",
            "confirmed_capabilities": [],
            "confirmed_limits": [],
            "confirmed_costs": [],
            "unexplained_phenomena": [],
            "recent_magical_events": [],
        },
        "iceberg_notes": {
            "nature_of_magic": "",
            "known_practitioners": "",
            "institutional_relationship": "",
        },
    }


def _default_geography() -> List[Dict[str, Any]]:
    return [
        {
            "node_type": "Location",
            "properties": {
                "name": "Primary Locale",
                "description": "",
                "climate": "",
                "seasonal_weather_state": "",
            },
            "iceberg_notes": {
                "adjacent_locations": "",
                "what_the_geography_makes_difficult": "",
                "cultural_meaning": "",
            },
        }
    ]


def _default_political() -> List[Dict[str, Any]]:
    return [
        {
            "node_type": "Faction",
            "properties": {
                "name": "Primary Power Bloc",
                "core_values": [],
                "military_assets": "",
                "economic_assets": "",
            },
            "iceberg_notes": {
                "current_controller": "",
                "allegiances": "",
                "active_enmities": "",
                "internal_tensions": "",
                "what_this_power_does_not_know": "",
            },
        }
    ]


def _default_cultures() -> List[Dict[str, Any]]:
    return [
        {
            "node_type": "Culture",
            "properties": {
                "name": "Primary Culture",
                "core_values": [],
                "core_fears": [],
                "key_customs": [],
                "class_structure": "",
                "gender_dynamics": "",
                "religious_beliefs": "",
                "political_power": "",
                "languages_dialects": [],
            },
            "iceberg_notes": {"internal_contradictions": ""},
        }
    ]


def _default_history() -> List[Dict[str, Any]]:
    return [
        {
            "node_type": "Event",
            "properties": {
                "name": "Foundational Upheaval",
                "summary": "",
                "is_historical": True,
                "true_account": "",
                "believed_account": "",
                "factional_interpretations": {},
                "physical_remnants": [],
                "story_significance": "",
                "referenced_in_chapters": [],
            },
        }
    ]


def _default_location_connections(geography: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if len(geography) >= 2:
        first = geography[0].get("properties", {}).get("name", "loc_a")
        second = geography[1].get("properties", {}).get("name", "loc_b")
        return [
            {
                "edge_type": "CONNECTED_TO",
                "from": str(first),
                "to": str(second),
                "properties": {"distance": "", "travel_times": {"foot": "", "horse": "", "ship": ""}},
            }
        ]
    return []


def _normalize_world_node(record: Dict[str, Any]) -> Dict[str, Any]:
    record = dict(record)
    record.setdefault("node_type", "")
    record.setdefault("properties", {})
    record.setdefault("iceberg_notes", {})
    if not isinstance(record["properties"], dict):
        record["properties"] = {}
    if not isinstance(record["iceberg_notes"], dict):
        record["iceberg_notes"] = {}
    return record


def _normalize_history_event(record: Dict[str, Any]) -> Dict[str, Any]:
    record = dict(record)
    record.setdefault("node_type", "Event")
    props = record.get("properties")
    if not isinstance(props, dict):
        props = {}
    props.setdefault("is_historical", True)
    record["properties"] = props
    return record


def _build_subgraph(subagent: Any) -> Any:
    llm = _build_llm(subagent)
    geo_pol_llm = llm.with_structured_output(GeoPoliticsBundleOutput)
    cult_hist_llm = llm.with_structured_output(CultureHistoryBundleOutput)
    magic_llm = llm.with_structured_output(MagicOutput)
    connections_llm = llm.with_structured_output(ConnectionsOutput)

    graph = StateGraph(WorldbuildingState)

    def ingest_context(state: WorldbuildingState) -> WorldbuildingState:
        context = state.get("context", {}) or {}
        expansion_scope = context.get("expansion_scope")
        targeted_expansion = bool(expansion_scope)
        chapter_context = int(context.get("chapter_context", 0) or 0)
        missing: List[str] = []
        follow_up_questions: List[str] = []

        if not isinstance(context.get("endpoint_compass"), dict):
            missing.append("endpoint_compass")
            follow_up_questions.append(
                "Please provide endpoint_compass from defining-rough-endpoints before running worldbuilding."
            )

        if targeted_expansion and chapter_context <= 0:
            missing.append("chapter_context")
            follow_up_questions.append(
                "Please provide chapter_context for targeted world expansion KG reads."
            )

        return {
            "targeted_expansion": targeted_expansion,
            "chapter_context": chapter_context,
            "missing_required_fields": missing,
            "follow_up_questions": follow_up_questions,
            "terminal_status": "need_input" if missing else None,
            "terminal_summary": (
                f"Missing required context for worldbuilding: {', '.join(missing)}."
                if missing
                else None
            ),
            "warnings": [],
            "kg_context_used": {
                "targeted_expansion": targeted_expansion,
                "factions_found": 0,
                "locations_found": 0,
                "cultures_found": 0,
                "magic_systems_found": 0,
                "historical_events_found": 0,
            },
        }

    def fetch_existing_world_context(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        if not state.get("targeted_expansion"):
            return {
                "existing_factions": [],
                "existing_locations": [],
                "existing_cultures": [],
                "existing_magic_systems": [],
                "existing_historical_events": [],
            }

        chapter_context = int(state.get("chapter_context", 0))
        warnings: List[str] = list(state.get("warnings", []))
        factions: List[Dict[str, Any]] = []
        locations: List[Dict[str, Any]] = []
        cultures: List[Dict[str, Any]] = []
        magic_systems: List[Dict[str, Any]] = []
        historical_events: List[Dict[str, Any]] = []

        try:
            factions = query_kg_nodes.invoke(
                {"query": {"type": "Faction"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            warnings.append(f"Worldbuilding Faction query failed: {error}")

        try:
            locations = query_kg_nodes.invoke(
                {"query": {"type": "Location"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            warnings.append(f"Worldbuilding Location query failed: {error}")

        try:
            cultures = query_kg_nodes.invoke(
                {"query": {"type": "Culture"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            warnings.append(f"Worldbuilding Culture query failed: {error}")

        try:
            magic_systems = query_kg_nodes.invoke(
                {"query": {"type": "MagicSystem"}, "as_of_chapter": chapter_context}
            )
        except Exception as error:
            warnings.append(f"Worldbuilding MagicSystem query failed: {error}")

        try:
            historical_events = query_kg_nodes.invoke(
                {
                    "query": {"type": "Event", "properties.is_historical": True},
                    "as_of_chapter": chapter_context,
                }
            )
        except Exception as error:
            warnings.append(f"Worldbuilding historical Event query failed: {error}")

        return {
            "existing_factions": factions,
            "existing_locations": locations,
            "existing_cultures": cultures,
            "existing_magic_systems": magic_systems,
            "existing_historical_events": historical_events,
            "warnings": warnings,
            "kg_context_used": {
                "targeted_expansion": True,
                "factions_found": len(factions),
                "locations_found": len(locations),
                "cultures_found": len(cultures),
                "magic_systems_found": len(magic_systems),
                "historical_events_found": len(historical_events),
            },
        }

    def build_skill_contract(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        full_skill = progressive_skill_loader.invoke({"skill_name": "worldbuilding", "load_type": "full"})
        if not isinstance(full_skill, str):
            full_skill = str(full_skill)
        contract = _build_skill_contract(full_skill)
        return {"skill_contract": contract}

    def bundle_geo_politics(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        context = state.get("context", {})
        payload = {
            "bundle": "geography_plus_political_power_map",
            "mode": "targeted_expansion" if state.get("targeted_expansion") else "initial_build",
            "endpoint_compass": context.get("endpoint_compass", {}),
            "research_output": context.get("research_output", {}),
            "expansion_scope": context.get("expansion_scope", {}),
            "existing_locations_summary": _summarize_kg_nodes(state.get("existing_locations", [])),
            "existing_factions_summary": _summarize_kg_nodes(state.get("existing_factions", [])),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Generate ONLY this bundle as structured JSON: `geography` (Location nodes) and "
            "`political_power_map` (Faction nodes). Respect existing summaries as hard constraints "
            "in targeted expansion mode.\n\n"
            f"{_safe_json(payload)}"
        )
        output: GeoPoliticsBundleOutput = geo_pol_llm.invoke([HumanMessage(content=prompt)])
        geography = [_normalize_world_node(r.model_dump()) for r in output.geography]
        political = [_normalize_world_node(r.model_dump()) for r in output.political_power_map]
        return {"bundle_a": {"geography": geography, "political_power_map": political}}

    def bundle_culture_history(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        context = state.get("context", {})
        payload = {
            "bundle": "cultures_customs_religion_plus_history_and_legends",
            "mode": "targeted_expansion" if state.get("targeted_expansion") else "initial_build",
            "endpoint_compass": context.get("endpoint_compass", {}),
            "research_output": context.get("research_output", {}),
            "expansion_scope": context.get("expansion_scope", {}),
            "existing_cultures_summary": _summarize_kg_nodes(state.get("existing_cultures", [])),
            "existing_historical_events_summary": _summarize_kg_nodes(
                state.get("existing_historical_events", [])
            ),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Generate ONLY this bundle as structured JSON: `cultures_customs_religion` (Culture nodes) "
            "and `history_and_legends` (Event nodes with is_historical=true in properties).\n\n"
            f"{_safe_json(payload)}"
        )
        output: CultureHistoryBundleOutput = cult_hist_llm.invoke([HumanMessage(content=prompt)])
        cultures = [_normalize_world_node(r.model_dump()) for r in output.cultures_customs_religion]
        history = [_normalize_history_event(r.model_dump()) for r in output.history_and_legends]
        return {"bundle_b": {"cultures_customs_religion": cultures, "history_and_legends": history}}

    def join_merge_validate(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        warnings = list(state.get("warnings", []))
        targeted = bool(state.get("targeted_expansion"))
        bundle_a = state.get("bundle_a") or {}
        bundle_b = state.get("bundle_b") or {}

        geography: List[Dict[str, Any]] = list(bundle_a.get("geography") or [])
        political: List[Dict[str, Any]] = list(bundle_a.get("political_power_map") or [])
        cultures: List[Dict[str, Any]] = list(bundle_b.get("cultures_customs_religion") or [])
        history: List[Dict[str, Any]] = list(bundle_b.get("history_and_legends") or [])

        if not geography:
            if targeted:
                warnings.append("join: empty geography from bundle A; applying default geography skeleton.")
            geography = _default_geography()
        if not political:
            if targeted:
                warnings.append("join: empty political_power_map from bundle A; applying default faction skeleton.")
            political = _default_political()
        if not cultures:
            if targeted:
                warnings.append("join: empty cultures_customs_religion from bundle B; applying default culture skeleton.")
            cultures = _default_cultures()
        if not history:
            if targeted:
                warnings.append("join: empty history_and_legends from bundle B; applying default historical event skeleton.")
            history = _default_history()

        return {
            "geography": geography,
            "political_power_map": political,
            "cultures_customs_religion": cultures,
            "history_and_legends": history,
            "warnings": warnings,
        }

    def build_magic_system(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        context = state.get("context", {})
        payload = {
            "mode": "targeted_expansion" if state.get("targeted_expansion") else "initial_build",
            "endpoint_compass": context.get("endpoint_compass", {}),
            "research_output": context.get("research_output", {}),
            "geography": state.get("geography", []),
            "political_power_map": state.get("political_power_map", []),
            "cultures_customs_religion": state.get("cultures_customs_religion", []),
            "history_and_legends": state.get("history_and_legends", []),
            "existing_magic_systems_summary": _summarize_kg_nodes(state.get("existing_magic_systems", [])),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Generate only the `magic_system` object as structured JSON (single MagicSystem node + iceberg_notes).\n\n"
            f"{_safe_json(payload)}"
        )
        output: MagicOutput = magic_llm.invoke([HumanMessage(content=prompt)])
        magic_system = output.magic_system.model_dump() if output.magic_system else _default_magic_system()
        if not magic_system.get("node_type"):
            magic_system["node_type"] = "MagicSystem"
        magic_system.setdefault("properties", {})
        magic_system.setdefault("iceberg_notes", {})
        return {"magic_system": magic_system}

    def package_location_connections(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        context = state.get("context", {})
        payload = {
            "mode": "targeted_expansion" if state.get("targeted_expansion") else "initial_build",
            "endpoint_compass": context.get("endpoint_compass", {}),
            "geography": state.get("geography", []),
            "expansion_scope": context.get("expansion_scope", {}),
        }
        prompt = (
            f"{state.get('skill_contract', '')}\n\n"
            "Generate only location_connections as structured JSON records. "
            "Use CONNECTED_TO edge type and fill from_node/to_node in fields.\n\n"
            f"{_safe_json(payload)}"
        )
        output: ConnectionsOutput = connections_llm.invoke([HumanMessage(content=prompt)])
        connections: List[Dict[str, Any]] = []
        for edge in output.location_connections:
            edge_dict = edge.model_dump()
            connections.append(
                {
                    "edge_type": edge_dict.get("edge_type", "CONNECTED_TO"),
                    "from": edge_dict.get("from_node", ""),
                    "to": edge_dict.get("to_node", ""),
                    "properties": edge_dict.get("properties", {}),
                }
            )
        if not connections:
            connections = _default_location_connections(state.get("geography", []))
        return {"location_connections": connections}

    def package_response(state: WorldbuildingState) -> WorldbuildingState:
        if state.get("terminal_status"):
            return {}
        summary = "Constructed worldbuilding domains via planning worldbuilding subgraph."
        if state.get("targeted_expansion"):
            summary = "Constructed targeted worldbuilding expansion using KG constraints."
        if state.get("warnings"):
            summary = "Constructed worldbuilding domains with recoverable KG warning(s)."
        return {"summary": summary}

    def package_need_input(state: WorldbuildingState) -> WorldbuildingState:
        return {
            "summary": state.get("terminal_summary", "Missing required context for worldbuilding.")
        }

    def route_fan_out(state: WorldbuildingState) -> List[Send]:
        return [
            Send("bundle_geo_politics", state),
            Send("bundle_culture_history", state),
        ]

    graph.add_node("ingest_context", ingest_context)
    graph.add_node("fetch_existing_world_context", fetch_existing_world_context)
    graph.add_node("build_skill_contract", build_skill_contract)
    graph.add_node("bundle_geo_politics", bundle_geo_politics)
    graph.add_node("bundle_culture_history", bundle_culture_history)
    graph.add_node("join_merge_validate", join_merge_validate)
    graph.add_node("build_magic_system", build_magic_system)
    graph.add_node("package_location_connections", package_location_connections)
    graph.add_node("package_response", package_response)
    graph.add_node("package_need_input", package_need_input)

    graph.add_edge(START, "ingest_context")

    def route_after_ingest(
        state: WorldbuildingState,
    ) -> Literal["package_need_input", "fetch_existing_world_context"]:
        if state.get("terminal_status"):
            return "package_need_input"
        return "fetch_existing_world_context"

    graph.add_conditional_edges(
        "ingest_context",
        route_after_ingest,
        {
            "package_need_input": "package_need_input",
            "fetch_existing_world_context": "fetch_existing_world_context",
        },
    )
    graph.add_edge("fetch_existing_world_context", "build_skill_contract")
    graph.add_conditional_edges(
        "build_skill_contract",
        route_fan_out,
        ["bundle_geo_politics", "bundle_culture_history"],
    )
    graph.add_edge("bundle_geo_politics", "join_merge_validate")
    graph.add_edge("bundle_culture_history", "join_merge_validate")
    graph.add_edge("join_merge_validate", "build_magic_system")
    graph.add_edge("build_magic_system", "package_location_connections")
    graph.add_edge("package_location_connections", "package_response")
    graph.add_edge("package_response", END)
    graph.add_edge("package_need_input", END)
    return graph.compile()


def run_worldbuilding_subgraph(
    subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}
    initial_state: WorldbuildingState = {"context": context}

    try:
        graph = _build_subgraph(subagent)
        graph_result = graph.invoke(initial_state, config=config or {})

        missing = graph_result.get("missing_required_fields", [])
        if missing:
            structured_result = WorkerResponse(
                status="need_input",
                summary=graph_result.get("terminal_summary", "Missing required worldbuilding context."),
                artifacts={
                    "skill_attempted": "worldbuilding",
                    "error": "missing_required_context",
                    "missing_fields": missing,
                },
                follow_up_questions=graph_result.get("follow_up_questions", []),
            ).model_dump()
        else:
            artifacts = {
                "political_power_map": graph_result.get("political_power_map", _default_political()),
                "geography": graph_result.get("geography", _default_geography()),
                "cultures_customs_religion": graph_result.get(
                    "cultures_customs_religion", _default_cultures()
                ),
                "history_and_legends": graph_result.get(
                    "history_and_legends", _default_history()
                ),
                "magic_system": graph_result.get("magic_system", _default_magic_system()),
                "location_connections": graph_result.get("location_connections", []),
                "kg_context_used": graph_result.get(
                    "kg_context_used",
                    {
                        "targeted_expansion": False,
                        "factions_found": 0,
                        "locations_found": 0,
                        "cultures_found": 0,
                        "magic_systems_found": 0,
                        "historical_events_found": 0,
                    },
                ),
                "warnings": graph_result.get("warnings", []),
            }
            structured_result = WorkerResponse(
                status="success",
                summary=graph_result.get(
                    "summary",
                    "Constructed worldbuilding domains via planning worldbuilding subgraph.",
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
