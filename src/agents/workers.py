from typing import List

from src.agents.base import BaseWorkerSubagent
from src.character_creation_subgraph import run_character_creation_subgraph
from src.character_integration_chain import run_integration_chain
from src.planning_rough_endpoints_subgraph import run_rough_endpoints_subgraph
from src.planning_seed_chain import run_finding_seed_chain
from src.planning_worldbuilding_subgraph import run_worldbuilding_subgraph
from src.plotting_gardener_subgraph import run_gardener_plotting_subgraph
from src.consequence_cascade_subgraph import run_consequence_cascade_subgraph
from src.consequence_realism_chain import run_balancing_realism_chain
from src.resolution_subgraph import run_resolution_subgraph
from src.story_state_manager_subgraph import run_story_state_manager_subgraph
from src.writing_pov_consistency_chain import run_pov_consistency_chain
from src.writing_professional_techniques_subgraph import (
    run_professional_writing_techniques_subgraph,
)
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

    @staticmethod
    def _is_finding_seed_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"finding-a-seed", "finding_a_seed"}
            or operation_hint in {"finding-a-seed", "finding_a_seed"}
            or "finding-a-seed" in task
            or "finding a seed" in task
        )

    @staticmethod
    def _is_rough_endpoints_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {
                "defining-rough-endpoints",
                "defining_rough_endpoints",
                "defining-rough-endpoints-pass-1",
                "defining-rough-endpoints-pass-2",
            }
            or operation_hint in {"defining-rough-endpoints", "defining_rough_endpoints"}
            or "defining-rough-endpoints" in task
            or "defining rough endpoints" in task
        )

    @staticmethod
    def _is_worldbuilding_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"worldbuilding", "world_building"}
            or operation_hint in {"worldbuilding", "world_building"}
            or "worldbuilding" in task
            or "world building" in task
        )

    def invoke(self, state: dict, config=None) -> dict:
        if self._is_finding_seed_request(state):
            return run_finding_seed_chain(self, state, config)
        if self._is_rough_endpoints_request(state):
            return run_rough_endpoints_subgraph(self, state, config)
        if self._is_worldbuilding_request(state):
            return run_worldbuilding_subgraph(self, state, config)
        return super().invoke(state, config)


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

    @staticmethod
    def _is_professional_writing_techniques_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"professional-writing-techniques", "professional_writing_techniques"}
            or operation_hint in {"professional-writing-techniques", "professional_writing_techniques"}
            or "professional-writing-techniques" in task
            or "professional writing techniques" in task
        )

    @staticmethod
    def _is_pov_consistency_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"pov-consistency-maintenance", "pov_consistency_maintenance"}
            or operation_hint in {"pov-consistency-maintenance", "pov_consistency_maintenance"}
            or "pov-consistency-maintenance" in task
            or "pov consistency maintenance" in task
        )

    def invoke(self, state: dict, config=None) -> dict:
        if self._is_professional_writing_techniques_request(state):
            return run_professional_writing_techniques_subgraph(self, state, config)
        if self._is_pov_consistency_request(state):
            return run_pov_consistency_chain(self, state, config)
        return super().invoke(state, config)


class ConsequenceSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="consequence_subagent",
            config=config,
            tools=[progressive_skill_loader, query_kg_nodes, query_kg_edges],
            prompt_file="consequence_subagent.md",
        )

    @staticmethod
    def _is_consequence_cascade_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"consequence-cascade-implementation", "consequence_cascade_implementation"}
            or operation_hint in {"consequence-cascade-implementation", "consequence_cascade_implementation"}
            or "consequence-cascade-implementation" in task
            or "consequence cascade implementation" in task
        )

    @staticmethod
    def _is_balancing_realism_request(state: dict) -> bool:
        worker_request = state.get("worker_request", {}) or {}
        task = str(worker_request.get("task", "")).lower()
        context = worker_request.get("context", {}) or {}
        skill_hint = str(context.get("skill", "")).lower()
        operation_hint = str(context.get("operation", "")).lower()
        return (
            skill_hint in {"balancing-realism-and-fantasy", "balancing_realism_and_fantasy"}
            or operation_hint in {"balancing-realism-and-fantasy", "balancing_realism_and_fantasy"}
            or "balancing-realism-and-fantasy" in task
            or "balancing realism and fantasy" in task
            or "realism-fantasy" in task
        )

    def invoke(self, state: dict, config=None) -> dict:
        if self._is_consequence_cascade_request(state):
            return run_consequence_cascade_subgraph(self, state, config)
        if self._is_balancing_realism_request(state):
            return run_balancing_realism_chain(self, state, config)
        return super().invoke(state, config)


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
    """Contradiction resolution via internal subgraph (tool-free ANALYSE; IMPLEMENT plan then KG updates)."""

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
            build_agent=False,
        )

    def invoke(self, state: dict, config=None):
        return run_resolution_subgraph(self, state, config)
