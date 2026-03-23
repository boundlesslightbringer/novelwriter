"""Compatibility wrapper for the LangGraph orchestrator runtime."""

try:
    from src.orchestrator_graph import (
        ACTIVE_WORKER_NAMES,
        DEFAULT_MODEL,
        WORLD_BIBLE_TOOLS,
        create_grrm_orchestrator,
        create_initial_state,
        get_registered_subagent_names,
    )
except ModuleNotFoundError:
    from orchestrator_graph import (
        ACTIVE_WORKER_NAMES,
        DEFAULT_MODEL,
        WORLD_BIBLE_TOOLS,
        create_grrm_orchestrator,
        create_initial_state,
        get_registered_subagent_names,
    )


__all__ = [
    "ACTIVE_WORKER_NAMES",
    "DEFAULT_MODEL",
    "WORLD_BIBLE_TOOLS",
    "create_grrm_orchestrator",
    "create_initial_state",
    "get_registered_subagent_names",
]
