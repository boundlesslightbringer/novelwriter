from typing import List

from src.agents.base import BaseWorkerSubagent
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
            tools=[progressive_skill_loader],
            prompt_file="planning_subagent.md",
        )


class CharacterSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="character_subagent",
            config=config,
            tools=[progressive_skill_loader],
            prompt_file="character_subagent.md",
        )


class PlottingSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="plotting_subagent",
            config=config,
            tools=[progressive_skill_loader],
            prompt_file="plotting_subagent.md",
        )


class WritingSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="writing_subagent",
            config=config,
            tools=[progressive_skill_loader],
            prompt_file="writing_subagent.md",
        )


class ConsequenceSubagent(BaseWorkerSubagent):
    def __init__(self, config: NovelWriterConfig):
        super().__init__(
            name="consequence_subagent",
            config=config,
            tools=[progressive_skill_loader],
            prompt_file="consequence_subagent.md",
        )


class WorldBibleManager(BaseWorkerSubagent):
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
            name="worldbible_manager",
            config=config,
            tools=tools,
            prompt_file="worldbiblemanager.md",
        )


class ResolutionSubagent(BaseWorkerSubagent):
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
            name="resolution_subagent",
            config=config,
            tools=tools,
            prompt_file="resolution_subagent.md",
        )
