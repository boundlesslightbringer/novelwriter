"""
GRRM Novel Writer - DeepAgent orchestration skeleton.

This module builds the top-level brain plus its session-persistent subagents.
The orchestrator delegates all domain work to subagents and routes all World
Bible I/O through the dedicated manager subagent.
"""

from pathlib import Path
from typing import Any

try:
    from src.tools import progressive_skill_loader
    from src.world_bible_tools import (
        init_kg_db,
        query_kg_nodes,
        query_kg_edges,
        add_kg_node,
        update_kg_node,
        add_kg_edge,
        update_kg_edge,
        detect_kg_contradiction,
    )
except ModuleNotFoundError:
    from tools import progressive_skill_loader
    from world_bible_tools import (
        init_kg_db,
        query_kg_nodes,
        query_kg_edges,
        add_kg_node,
        update_kg_node,
        add_kg_edge,
        update_kg_edge,
        detect_kg_contradiction,
    )

DEFAULT_MODEL = "anthropic:claude-sonnet-4-20250514"
SRC_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = SRC_DIR / "subagent_prompts"
ORCHESTRATOR_PROMPT_PATH = SRC_DIR / "orchestrator_prompt.md"

WORLD_BIBLE_TOOLS = [
    init_kg_db,
    query_kg_nodes,
    query_kg_edges,
    add_kg_node,
    update_kg_node,
    add_kg_edge,
    update_kg_edge,
    detect_kg_contradiction,
]

SKILL_SUBAGENT_SPECS = (
    {
        "name": "planning_subagent",
        "prompt_file": "planning_subagent.md",
        "description": (
            "Handles Group 1 skills: finding-a-seed, defining-rough-endpoints, "
            "worldbuilding, and research-integration."
        ),
    },
    {
        "name": "character_subagent",
        "prompt_file": "character_subagent.md",
        "description": (
            "Handles Group 2 skills: character conception, creation, voice "
            "differentiation, and plot integration."
        ),
    },
    {
        "name": "plotting_subagent",
        "prompt_file": "plotting_subagent.md",
        "description": (
            "Handles Group 3 skills: gardener plotting, POV structure, braided "
            "narrative analysis, conflict layering, and thread tracking."
        ),
    },
    {
        "name": "writing_subagent",
        "prompt_file": "writing_subagent.md",
        "description": (
            "Handles Group 4 skills: scene construction, POV maintenance, pacing, "
            "history layering, and local craft techniques."
        ),
    },
    {
        "name": "consequence_subagent",
        "prompt_file": "consequence_subagent.md",
        "description": (
            "Handles Group 5 skills: consequence cascade implementation and "
            "realism-versus-fantasy calibration."
        ),
    },
    {
        "name": "problemsolver_subagent",
        "prompt_file": "problemsolver_subagent.md",
        "description": (
            "Handles Group 6 problem-solving diagnostics for stuck states and "
            "narrative tangles."
        ),
    },
    {
        "name": "refinement_subagent",
        "prompt_file": "refinement_subagent.md",
        "description": (
            "Handles Group 7 refinement passes such as self-editing and "
            "chapter-level POV auditing."
        ),
    },
)

FIRST_DRAFT_SUBAGENT_NAMES = (
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
    "consequence_subagent",
)
SHELVED_SUBAGENT_NAMES = ("problemsolver_subagent", "refinement_subagent")


def _read_prompt(prompt_path: Path) -> str:
    """Read a prompt file from disk.

    Args:
        prompt_path: Absolute or project-relative prompt path.

    Returns:
        The prompt contents as UTF-8 text.
    """
    return prompt_path.read_text(encoding="utf-8")


def _build_skill_subagent(
    *,
    name: str,
    description: str,
    prompt_file: str,
    model: str,
) -> dict[str, Any]:
    """Build a skill-group subagent configuration.

    Args:
        name: Stable subagent identifier used by the orchestrator.
        description: Human-readable domain description.
        prompt_file: Prompt filename in `src/subagent_prompts/`.
        model: Model identifier used by the DeepAgent runtime.

    Returns:
        A DeepAgent-compatible subagent configuration dictionary.
    """
    return {
        "name": name,
        "description": description,
        "model": model,
        "tools": [progressive_skill_loader],
        "system_prompt": _read_prompt(PROMPTS_DIR / prompt_file),
    }


def _build_worldbible_manager(model: str) -> dict[str, Any]:
    """Build the World Bible manager subagent configuration.

    Args:
        model: Model identifier used by the DeepAgent runtime.

    Returns:
        A DeepAgent-compatible subagent configuration dictionary with the full
        World Bible toolset attached.
    """
    return {
        "name": "worldbible_manager",
        "description": (
            "Handles all World Bible read/write operations and acts as the sole "
            "gateway to persisted story state."
        ),
        "model": model,
        "tools": WORLD_BIBLE_TOOLS,
        "system_prompt": _read_prompt(PROMPTS_DIR / "worldbiblemanager.md"),
    }


def get_registered_subagent_names(include_shelved_subagents: bool = False) -> list[str]:
    """Return the ordered list of registered subagent names.

    Args:
        include_shelved_subagents: Whether to include the first-draft-shelved
            problem-solver and refinement subagents.

    Returns:
        The ordered list of subagent identifiers exposed by the skeleton.
    """
    names = list(FIRST_DRAFT_SUBAGENT_NAMES)
    if include_shelved_subagents:
        names.extend(SHELVED_SUBAGENT_NAMES)
    names.append("worldbible_manager")
    return names


def build_subagents(
    *,
    include_shelved_subagents: bool = False,
    model: str = DEFAULT_MODEL,
) -> list[dict[str, Any]]:
    """Build the subagent registry for the orchestrator.

    Args:
        include_shelved_subagents: Whether to include the shelved Group 6 and
            Group 7 subagents in the registry.
        model: Model identifier used by all subagents in this skeleton.

    Returns:
        A list of DeepAgent-compatible subagent configuration dictionaries.
    """
    selected_names = set(FIRST_DRAFT_SUBAGENT_NAMES)
    if include_shelved_subagents:
        selected_names.update(SHELVED_SUBAGENT_NAMES)

    subagents = [
        _build_skill_subagent(
            name=spec["name"],
            description=spec["description"],
            prompt_file=spec["prompt_file"],
            model=model,
        )
        for spec in SKILL_SUBAGENT_SPECS
        if spec["name"] in selected_names
    ]
    subagents.append(_build_worldbible_manager(model))
    return subagents


def create_grrm_orchestrator(
    *,
    model: str = DEFAULT_MODEL,
    include_shelved_subagents: bool = False,
) -> Any:
    """Create the top-level GRRM orchestrator agent.

    Args:
        model: Model identifier used by the DeepAgent runtime.
        include_shelved_subagents: Whether to register the shelved problem
            solver and refinement subagents.

    Returns:
        The DeepAgent orchestrator instance.
    """
    from deepagents import create_deep_agent

    return create_deep_agent(
        name="orchestrator",
        model=model,
        tools=[],
        subagents=build_subagents(
            include_shelved_subagents=include_shelved_subagents,
            model=model,
        ),
        system_prompt=_read_prompt(ORCHESTRATOR_PROMPT_PATH),
    )


__all__ = [
    "DEFAULT_MODEL",
    "FIRST_DRAFT_SUBAGENT_NAMES",
    "SHELVED_SUBAGENT_NAMES",
    "WORLD_BIBLE_TOOLS",
    "build_subagents",
    "create_grrm_orchestrator",
    "get_registered_subagent_names",
]
