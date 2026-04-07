import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader
from src.world_bible_tools import query_kg_edges, query_kg_nodes


class DesireNetworkPair(BaseModel):
    character_a_id: str
    character_b_id: str
    relationship_type: str
    description: str
    convergence_note: str


class DesireNetwork(BaseModel):
    pairs: List[DesireNetworkPair]
    key_tensions: str
    notes: str


class KnowledgeExpansionOutput(BaseModel):
    new_knowledge_items: List[dict]
    new_knows_edges: List[dict]
    flags: List[dict]


class RelationshipMatrixOutput(BaseModel):
    new_relationship_edges: List[dict]
    updated_relationship_edges: List[dict]
    flags: List[dict]


def build_desire_prompt(kg_context: dict) -> str:
    skill_content = progressive_skill_loader.invoke({"skill_name": "character-desire-network", "load_type": "full"})
    context_data = {
        "character_nodes": kg_context.get("character_nodes", []),
        "faction_nodes": kg_context.get("faction_nodes", []),
        "active_plot_thread_nodes": kg_context.get("active_threads", []),
    }
    return f"{skill_content}\n\n## KG Context\n{json.dumps(context_data, indent=2)}"


def build_knowledge_prompt(kg_context: dict, desire_network: DesireNetwork) -> str:
    skill_content = progressive_skill_loader.invoke({"skill_name": "character-knowledge-expansion", "load_type": "full"})
    context_data = {
        "character_nodes": kg_context.get("character_nodes", []),
        "existing_knows_edges": kg_context.get("existing_knows_edges", []),
        "desire_network": desire_network.model_dump(),
    }
    return f"{skill_content}\n\n## KG Context\n{json.dumps(context_data, indent=2)}"


def build_relationship_prompt(kg_context: dict, desire_network: DesireNetwork) -> str:
    skill_content = progressive_skill_loader.invoke({"skill_name": "character-relationship-matrix", "load_type": "full"})
    context_data = {
        "character_nodes": kg_context.get("character_nodes", []),
        "existing_relationship_edges": kg_context.get("existing_relationship_edges", []),
        "desire_network": desire_network.model_dump(),
    }
    return f"{skill_content}\n\n## KG Context\n{json.dumps(context_data, indent=2)}"


def build_integration_chain(llm: ChatGoogleGenerativeAI):
    desire_network_llm = llm.with_structured_output(DesireNetwork)
    knowledge_llm = llm.with_structured_output(KnowledgeExpansionOutput)
    relationship_llm = llm.with_structured_output(RelationshipMatrixOutput)

    def run_chain(kg_context: dict) -> dict:
        desire_input = build_desire_prompt(kg_context)
        desire_network: DesireNetwork = desire_network_llm.invoke([HumanMessage(content=desire_input)])

        knowledge_input = build_knowledge_prompt(kg_context, desire_network)
        knowledge_output: KnowledgeExpansionOutput = knowledge_llm.invoke([HumanMessage(content=knowledge_input)])

        relationship_input = build_relationship_prompt(kg_context, desire_network)
        relationship_output: RelationshipMatrixOutput = relationship_llm.invoke([HumanMessage(content=relationship_input)])

        combined_flags = knowledge_output.flags + relationship_output.flags

        return {
            "knowledge_matrix_expansions": {
                "new_knowledge_items": knowledge_output.new_knowledge_items,
                "new_knows_edges": knowledge_output.new_knows_edges,
            },
            "relationship_records": {
                "new_relationship_edges": relationship_output.new_relationship_edges,
                "updated_relationship_edges": relationship_output.updated_relationship_edges,
            },
            "integration_flags": combined_flags,
        }

    return run_chain


def run_integration_chain(subagent, state: dict, config=None) -> dict:
    worker_request = state.get("worker_request", {})
    context = worker_request.get("context", {})
    character_ids = context.get("character_ids", [])
    chapter_context = context.get("chapter_context", 0)

    try:
        character_nodes = query_kg_nodes.invoke({
            "query": {"logical_id": {"$in": character_ids}}, "as_of_chapter": chapter_context
        }) if character_ids else []
        
        existing_relationship_edges = query_kg_edges.invoke({
            "query": {"type": "RELATIONSHIP", "from": {"$in": character_ids}},
            "as_of_chapter": chapter_context,
        }) if character_ids else []
        
        existing_knows_edges = query_kg_edges.invoke({
            "query": {"type": "KNOWS", "from": {"$in": character_ids}},
            "as_of_chapter": chapter_context,
        }) if character_ids else []
        
        faction_nodes = query_kg_nodes.invoke({"query": {"type": "Faction"}, "as_of_chapter": chapter_context})
        active_threads = query_kg_nodes.invoke({
            "query": {"type": "PlotThread", "properties.status": "Active"},
            "as_of_chapter": chapter_context,
        })

        kg_context = {
            "character_nodes": character_nodes,
            "existing_relationship_edges": existing_relationship_edges,
            "existing_knows_edges": existing_knows_edges,
            "faction_nodes": faction_nodes,
            "active_threads": active_threads,
        }

        # Initialize llm
        model_name = subagent.llm_config.model_name
        model_kwargs = {"temperature": subagent.llm_config.temperature}
        if subagent.llm_config.top_p is not None:
            model_kwargs["top_p"] = subagent.llm_config.top_p
        if subagent.llm_config.top_k is not None:
            model_kwargs["top_k"] = subagent.llm_config.top_k

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            vertexai=True,
            **model_kwargs
        )

        chain = build_integration_chain(llm)
        artifacts = chain(kg_context)

        structured_result = WorkerResponse(
            status="success",
            summary="Character integration chain completed successfully.",
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
