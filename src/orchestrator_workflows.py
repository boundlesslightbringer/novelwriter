"""
Workflow skeletons for orchestrator-to-subagent delegation.

These helpers do not execute subagent calls. They return structured request
envelopes that match the architecture in `grrm_agent_specs.md` and the logical
knowledge-graph context defined in `kg_schema_design.md`.
"""

from typing import Any

DEFAULT_SUBAGENT_CONSTRAINTS = [
    "Return structured output matching the target subagent prompt.",
    "Do not access the World Bible directly unless target=worldbible_manager.",
    "Do not invoke other subagents.",
]

# The brain persists chapter results in the order mandated by the spec.
WORLD_BIBLE_UPDATE_ORDER = [
    "1.1_character_directory",
    "1.2_character_knowledge_matrix",
    "1.3_relationship_records",
    "2.1_absolute_timeline",
    "2.2_pov_chapter_log",
    "2.3_plot_thread_registry",
    "2.4_pending_payoffs_foreshadowing",
    "4.1_event_consequence_chains",
    "4.2_time_delayed_consequence_bombs",
    "4.3_cascade_chains",
    "5.1_physical_continuity",
    "5.2_logical_continuity",
    "5.3_contradiction_detection_log",
]


def build_subagent_request(request: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized subagent delegation envelope.

    Args:
        request: Partial request payload containing target, task, and optional
            context/constraints fields.

    Returns:
        A normalized delegation envelope for the orchestrator skeleton.
    """
    return {
        "target": request["target"],
        "task": request["task"],
        "context": request.get("context", {}),
        "constraints": request.get("constraints", DEFAULT_SUBAGENT_CONSTRAINTS),
    }


def build_story_bootstrap_workflow(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the bootstrap workflow for a new project.

    Args:
        options: Bootstrap options. Expected keys include `project_name`,
            `genre`, and `theme`, plus optional `subgenres` and
            `user_constraints` lists.

    Returns:
        An ordered list of delegation envelopes covering initialization,
        planning, character creation, and initial persistence.
    """
    project_name = options["project_name"]
    genre = options["genre"]
    theme = options["theme"]
    subgenres = options.get("subgenres", [])
    user_constraints = options.get("user_constraints", [])

    return [
        build_subagent_request(
            {
                "target": "worldbible_manager",
                "task": "Initialize the World Bible for a new project.",
                "context": {
                    "operation": "write",
                    "updates": [
                        {
                            "module": "metadata",
                            "action": "create",
                            "data": {
                                "project_name": project_name,
                                "genre": genre,
                                "theme": theme,
                                "subgenres": subgenres,
                            },
                            "chapter_context": 0,
                        }
                    ],
                },
            }
        ),
        build_subagent_request(
            {
                "target": "planning_subagent",
                "task": "Establish seed, endpoints, research, and world foundation.",
                "context": {
                    "stage": "seed_to_world",
                    "inputs": {
                        "project_name": project_name,
                        "genre": genre,
                        "theme": theme,
                        "subgenres": subgenres,
                        "constraints": user_constraints,
                    },
                    "knowledge_graph_context": {
                        "node_types": ["PlotThread", "Payoff", "Faction", "Culture", "Location", "MagicSystem"],
                        "edge_types": ["INVOLVES", "CONTROLS", "ALLIED_WITH", "AT_WAR_WITH", "CONNECTED_TO"],
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "worldbible_manager",
                "task": "Persist planning outputs into Modules 2.3, 2.4, and 3.x.",
                "context": {
                    "operation": "write",
                    "updates": [
                        {"module": "2.3", "action": "update", "data": "plot_thread_seeds", "chapter_context": 0},
                        {"module": "2.4", "action": "update", "data": "pending_payoff_seeds", "chapter_context": 0},
                        {"module": "3.1-3.5", "action": "update", "data": "world_state_bundle", "chapter_context": 0},
                    ],
                },
            }
        ),
        build_subagent_request(
            {
                "target": "character_subagent",
                "task": "Create the opening cast, voice profiles, and initial plot integration.",
                "context": {
                    "stage": "opening_cast",
                    "inputs": {
                        "required_planning_outputs": [
                            "definitive_seed",
                            "candidate_seeds_log",
                        ],
                        "required_world_modules": ["3.1_political_power_map"],
                        "expected_outputs": ["1.1", "1.2", "1.3", "4.1_initial"],
                    },
                    "knowledge_graph_context": {
                        "node_types": ["Character", "Faction", "Culture", "KnowledgeItem", "PlotThread"],
                        "edge_types": ["BELONGS_TO_CULTURE", "KNOWS", "RELATIONSHIP", "INVOLVES"],
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "worldbible_manager",
                "task": "Persist character outputs into Modules 1.x and 4.1.",
                "context": {
                    "operation": "write",
                    "updates": [
                        {"module": "1.1", "action": "update", "data": "character_directory", "chapter_context": 0},
                        {"module": "1.2", "action": "update", "data": "knowledge_matrix", "chapter_context": 0},
                        {"module": "1.3", "action": "update", "data": "relationship_records", "chapter_context": 0},
                        {"module": "4.1", "action": "update", "data": "initial_consequence_entries", "chapter_context": 0},
                    ],
                },
            }
        ),
    ]


def build_scene_cycle_workflow(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the default scene-generation workflow for a chapter.

    Args:
        options: Scene-cycle options. Expected keys include `chapter_number`
            plus optional `pov_character` and `user_instructions`.

    Returns:
        An ordered list of delegation envelopes for read context, plotting,
        writing, and consequence analysis.
    """
    chapter_number = options["chapter_number"]
    pov_character = options.get("pov_character")
    user_instructions = options.get("user_instructions", [])

    return [
        build_subagent_request(
            {
                "target": "worldbible_manager",
                "task": "Read the current chapter context required for planning the next scene.",
                "context": {
                    "operation": "read",
                    "query": {
                        "modules": ["1.1", "1.2", "2.1", "2.2", "2.3", "2.4", "4.1"],
                        "chapter_context": chapter_number,
                        "pov_character": pov_character,
                    },
                    "expected_output": "scene_cycle_context_bundle",
                },
            }
        ),
        build_subagent_request(
            {
                "target": "plotting_subagent",
                "task": "Choose POV if needed and produce scene parameters for the next scene.",
                "context": {
                    "operation": "plan_chapter",
                    "chapter_number": chapter_number,
                    "pov_preference": pov_character,
                    "user_instructions": user_instructions,
                    "required_world_context": "scene_cycle_context_bundle",
                    "expected_outputs": ["pov_assignment", "scene_parameters", "thread_status"],
                    "knowledge_graph_context": {
                        "node_types": ["Character", "Chapter", "PlotThread", "Payoff", "Event"],
                        "edge_types": ["KNOWS", "RELATIONSHIP", "INVOLVES", "CAUSES", "PAYS_OFF_IN"],
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "writing_subagent",
                "task": "Draft the scene and run the scene-level quality loop.",
                "context": {
                    "operation": "draft_scene",
                    "chapter_number": chapter_number,
                    "pov_character": pov_character,
                    "required_plotting_outputs": ["pov_assignment", "scene_parameters"],
                    "expected_outputs": ["scene_draft", "quality_report"],
                    "expected_internal_chain": [
                        "pacing_if_needed",
                        "scene_construction",
                        "pov_consistency_maintenance",
                    ],
                    "knowledge_graph_context": {
                        "node_types": ["Character", "KnowledgeItem", "Location", "Payoff", "Event"],
                        "edge_types": ["KNOWS", "LOCATED_AT", "PAYS_OFF_IN"],
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "consequence_subagent",
                "task": "If a major event occurred, project consequences before the next scene.",
                "context": {
                    "operation": "analyze_consequences",
                    "chapter_number": chapter_number,
                    "trigger_condition": "major_event_just_occurred",
                    "required_writing_outputs": ["scene_draft", "quality_report"],
                    "expected_outputs": ["consequence_analysis", "recommended_updates"],
                    "knowledge_graph_context": {
                        "node_types": ["Event", "Character", "Payoff", "CascadeChain"],
                        "edge_types": ["CAUSES", "RELATIONSHIP", "INVOLVES"],
                    },
                },
            }
        ),
    ]


def build_chapter_completion_workflow(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the chapter-completion workflow.

    Args:
        options: Completion options. Expected keys include `chapter_number` and
            optional `include_refinement`.

    Returns:
        An ordered list of delegation envelopes for post-draft passes, World
        Bible persistence, and snapshot creation.
    """
    chapter_number = options["chapter_number"]
    include_refinement = options.get("include_refinement", False)

    workflow = [
        build_subagent_request(
            {
                "target": "writing_subagent",
                "task": "Apply the chapter-level history and legend pass when relevant.",
                "context": {
                    "operation": "layer_history",
                    "chapter_number": chapter_number,
                    "knowledge_graph_context": {
                        "node_types": ["Event", "Culture", "KnowledgeItem", "Location"],
                        "edge_types": ["BELONGS_TO_CULTURE", "KNOWS", "LOCATED_AT"],
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "consequence_subagent",
                "task": "Audit realism and balance for the completed chapter.",
                "context": {
                    "operation": "audit_realism",
                    "chapter_number": chapter_number,
                    "knowledge_graph_context": {
                        "node_types": ["Faction", "Culture", "MagicSystem", "Event"],
                        "edge_types": ["CONTROLS", "ALLIED_WITH", "AT_WAR_WITH", "CAUSES"],
                    },
                },
            }
        ),
    ]

    if include_refinement:
        workflow.append(
            build_subagent_request(
                {
                    "target": "refinement_subagent",
                    "task": "Run the optional refinement and chapter-level POV audit pass.",
                    "context": {
                        "operation": "full_pass",
                        "chapter_number": chapter_number,
                    },
                }
            )
        )

    workflow.extend(
        [
            build_subagent_request(
                {
                    "target": "worldbible_manager",
                    "task": "Write all chapter deltas back to the World Bible in spec order.",
                    "context": {
                        "operation": "write",
                        "chapter_number": chapter_number,
                        "update_order": WORLD_BIBLE_UPDATE_ORDER,
                    },
                }
            ),
            build_subagent_request(
                {
                    "target": "worldbible_manager",
                    "task": "Create the chapter snapshot after all updates are committed.",
                    "context": {
                        "operation": "write",
                        "updates": [
                            {
                                "module": "snapshot",
                                "action": "create",
                                "data": {"chapter_number": chapter_number},
                                "chapter_context": chapter_number,
                            }
                        ],
                    },
                }
            ),
        ]
    )
    return workflow


def build_stuck_state_workflow(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the stuck-state diagnostic workflow.

    Args:
        options: Diagnostic options. Expected keys include `chapter_number` and
            `problem_description`.

    Returns:
        An ordered list of delegation envelopes for state retrieval and
        problem-solver diagnosis.
    """
    chapter_number = options["chapter_number"]
    problem_description = options["problem_description"]

    return [
        build_subagent_request(
            {
                "target": "worldbible_manager",
                "task": "Read the last stable chapter state plus active consequence chains.",
                "context": {
                    "operation": "read",
                    "query": {
                        "modules": ["1.1", "1.2", "1.3", "4.1", "4.2", "4.3", "5.3"],
                        "chapter_context": chapter_number,
                    },
                },
            }
        ),
        build_subagent_request(
            {
                "target": "problemsolver_subagent",
                "task": "Diagnose the tangle and propose a path forward.",
                "context": {
                    "chapter_number": chapter_number,
                    "description": problem_description,
                    "knowledge_graph_context": {
                        "node_types": ["Character", "Event", "PlotThread", "CascadeChain", "Contradiction"],
                        "edge_types": ["RELATIONSHIP", "CAUSES", "INVOLVES", "CONFLICTS_WITH"],
                    },
                },
            }
        ),
    ]


__all__ = [
    "DEFAULT_SUBAGENT_CONSTRAINTS",
    "WORLD_BIBLE_UPDATE_ORDER",
    "build_chapter_completion_workflow",
    "build_scene_cycle_workflow",
    "build_story_bootstrap_workflow",
    "build_stuck_state_workflow",
    "build_subagent_request",
]
