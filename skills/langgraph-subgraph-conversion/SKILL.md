
---

# 3. Agent Skill

**File:** `skills/langgraph-subgraph-conversion/SKILL.md`

```md id="z1t8dq"
---
name: langgraph-subgraph-conversion
description: Converts an agent skill specification into a LangGraph-compatible orchestration model (chain or subgraph) with explicit nodes, edges, and state schema.
---

# LangGraph Subgraph Conversion Skill

## Purpose

Transform an agent skill into a **concrete LangGraph design** that is:

- explicit
- inspectable
- reliable under failure
- structurally aligned with its control flow

---

## Core

Given a skill specification:

1. Detect control flow complexity
2. Determine architecture (chain vs subgraph)
3. Produce LangGraph-compatible structure

---

## Output Contract

### Chain Output

- Linear step list
- Step responsibilities
- Failure handling

---

### Subgraph Output

Must include:

- `state_schema`
- `nodes`
- `edges`
- `conditional_edges`
- `entry_point`
- `exit_node`
- `subgraph_usage`
- `reliability_rationale`

---

## State Schema Guidelines

Include:

- input fields
- intermediate fields
- flags (mode, validation, errors)
- output fields

State must:
- support branching decisions
- preserve intermediate reasoning where needed

---

## Node Design Rules

Each node must:
- have a single responsibility
- produce structured output
- be independently testable

Avoid:
- monolithic nodes
- hidden control flow

---

## Edge Design Rules

Use:

- direct edges for linear flow
- conditional edges for:
  - mode selection
  - validation gates
  - optional steps

---

## Subgraph Usage Decision

Choose:

### `node_call`
- if subgraph has isolated state
- if used as a reusable component

### `direct_node`
- if state must be shared with parent graph

---

## Reliability Rules

Prefer subgraph when:
- branching exists
- validation gates exist
- missing data must be handled
- different execution modes exist

Prefer chain when:
- fully linear
- no branching
- no validation gating

---

## Anti-Patterns

Do NOT:
- flatten branching into prompt logic
- hide routing inside LLM calls
- skip validation nodes
- assume perfect input

---

## Quality Checklist

- [ ] Architecture matches control flow
- [ ] Nodes are minimal and composable
- [ ] State supports decisions
- [ ] Conditional edges are explicit
- [ ] Failure paths are represented
- [ ] Output is directly implementable in LangGraph