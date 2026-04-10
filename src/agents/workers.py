from typing import List

from src.agents.base import BaseWorkerSubagent
from src.character_creation_subgraph import run_character_creation_subgraph
from src.character_integration_chain import run_integration_chain
from src.plotting_gardener_subgraph import run_gardener_plotting_subgraph
from src.story_state_manager_subgraph import run_story_state_manager_subgraph
from src.config import NovelWriterConfig
from src.tools import progressive_skill_loader
from src.world_bible_tools import (
    add_kg_edge,
    add_kg_node,
    detect_kg_contradiction,
    init_kg_db,
    query_kg_edges,
    query_kg_nodes,
    update_kg_edge,
    update_kg_node,
)


class PlanningSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="planning_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="planning_subagent.md",
        )


class CharacterSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="character_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="character_subagent.md",
        )

    def invoke(self, state: dict, config=None) -> dict:
        worker_request = state.get("worker_request", {}) or {}
        context = worker_request.get("context", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        skill = str(context.get("skill", "")).lower()

        if skill in {"character-integration", "character_integration"}:
            return run_integration_chain(self, state, config)

        if (
            skill in {"character-creation", "character_creation"}
            or "character-creation" in task
            or "character creation" in task
        ):
            return run_character_creation_subgraph(self, state, config)

        return super().invoke(state, config)


class PlottingSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="plotting_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="plotting_subagent.md",
        )

    @staticmethod
    def _is_gardener_plotting_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"gardener-plotting-system", "gardener_plotting_system"}
            or operation_hint in {"gardener-plotting-system", "gardener_plotting_system"}
            or "gardener-plotting-system" in task
            or "gardener plotting system" in task
        )

    def invoke(self, state: dict, config=None) -> dict:
        if self._is_gardener_plotting_request(state):
            return run_gardener_plotting_subgraph(self, state, config)
        return super().invoke(state, config)


class WritingSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="writing_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="writing_subagent.md",
        )


class ConsequenceSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="consequence_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="consequence_subagent.md",
        )


class StoryStateManager(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        tools = [
            init_kg_db,
            query_kg_nodes,
            query_kg_edges,
            add_kg_node,
            update_kg_node,
            add_kg_edge,
            update_kg_edge,
            detect_kg_contradiction,
        ]
        super().__init__(
            name="story_state_manager",
            config=config,
            tools=tools,
            prompt_file="story_state_manager.md",
        )

    @staticmethod
    def _is_persist_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        artifacts = context.get("artifacts", {}) if isinstance(context.get("artifacts"), dict) else {}
        write_keys = ("nodes_to_add", "nodes_to_update", "edges_to_add", "edges_to_update")

        has_write_payload = any(context.get(key) for key in write_keys) or any(artifacts.get(key) for key in write_keys)
        has_write_task_hint = any(token in task for token in ("persist", "write", "kg update", "knowledge graph update"))
        return has_write_payload or has_write_task_hint

    def invoke(self, state: dict, config=None) -> dict:
        if self._is_persist_request(state):
            return run_story_state_manager_subgraph(self, state, config)
        return super().invoke(state, config)


class ResolutionSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        tools = [
            query_kg_nodes,
            query_kg_edges,
            add_kg_node,
            update_kg_node,
            add_kg_edge,
            update_kg_edge,
        ]
        super().__init__(
            name="resolution_subagent",
            config=config,
            tools=tools,
            prompt_file="resolution_subagent.md",
        )
