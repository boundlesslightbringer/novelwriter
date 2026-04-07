# Subagent Prompts

This directory contains the initialization prompts for the 8 session-persistent subagents in the GRRM Novel Writer DeepAgent system.

## Architecture Overview

The system uses a **skill-group subagent** architecture where:
- **1 brain** (main agent) orchestrates
- **7 skill-group subagents** handle skill domains
- **1 WorldBibleManager** handles all World Bible I/O

## Subagent Mapping

| Subagent | File | Skill Group | Skills Count | Primary Domain |
|----------|------|-------------|--------------|----------------|
| Planning Subagent | `planning_subagent.md` | Group 1 – Planning | 4 skills | Story foundation |
| Character Subagent | `character_subagent.md` | Group 2 – Character | 4 skills | Character lifecycle |
| Plotting Subagent | `plotting_subagent.md` | Group 3 – Plotting & Structure | 5 skills | Scene planning |
| Writing Subagent | `writing_subagent.md` | Group 4 – Writing Execution | 5 skills | Draft prose |
| Consequence Subagent | `consequence_subagent.md` | Group 5 – Consequence & Realism | 2 skills | Impact analysis |
| ProblemSolver Subagent | `problemsolver_subagent.md` | Group 6 – Problem-Solving | 1 skill | Diagnostics |
| Refinement Subagent | `refinement_subagent.md` | Group 7 – Refinement | 2 skills | Final polish |
| StoryStateManager | `story_state_manager.md` | Infrastructure | All modules | World Bible I/O |

## Lifecycle

Subagents are **session-persistent**:
1. Spawned once at session start with full skill group content
2. Receive ALL skills in their group at initialization
3. Make internal routing decisions about which skill(s) to apply
4. Maintain context across requests within session
5. Destroyed when session ends

## Delegation Pattern

```
Brain receives user request
    ↓
Brain identifies required domain(s)
    ↓
Brain delegates to appropriate subagent(s)
    ↓
Subagent internally routes to specific skill(s)
    ↓
Subagent returns structured output
    ↓
Brain coordinates next step or returns to user
```

## Benefits

1. **Reduced Overhead**: 8 persistent subagents vs. 24+ ephemeral spawns
2. **Natural Composition**: Skills within a domain naturally chain
3. **Context Retention**: Subagents remember state across requests
4. **Clean Architecture**: Brain delegates by domain, not individual skill

## Files

- `planning_subagent.md` - Story foundation and world construction
- `character_subagent.md` - Character development lifecycle
- `plotting_subagent.md` - Scene planning and structure
- `writing_subagent.md` - Draft prose generation
- `consequence_subagent.md` - Event impact and realism
- `problemsolver_subagent.md` - Diagnostic and resolution
- `refinement_subagent.md` - Final quality passes
- `story_state_manager.md` - World Bible I/O gateway
