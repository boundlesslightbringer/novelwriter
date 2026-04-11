---
name: Consequence skills subgraph conversion
overview: "Split consequence-cascade-implementation into a LangGraph subgraph with KG prefetch, smaller structured LLM steps, and validation gates; split balancing-realism-and-fantasy into a sequential chain (optional subgraph later). Wire via ConsequenceSubagent.invoke while preserving WorkerResponse as the external contract."
todos:
  - id: prefetch-module
    content: "Add deterministic KG prefetch (logical_id, from/to, as_of_chapter) shared by both skills; fix SKILL.md edge examples"
    status: pending
  - id: cascade-subgraph
    content: "Implement consequence_cascade_subgraph (prefetch → linkage → trace → bombs → updates → assemble → validate → optional repair) + Pydantic schemas + tests with mocked LLM"
    status: pending
  - id: realism-chain
    content: "Implement balancing_realism_chain (prefetch → draft signals → five-dimension audit) + validation + tests"
    status: pending
  - id: worker-routing
    content: "ConsequenceSubagent.invoke routes by context.skill/task to subgraph/chain; align consequence_subagent.md artifacts with canonical shapes"
    status: pending
isProject: false
---

# Consequence worker — subgraph / chain conversion plan

## Goal

Improve reliability of **Group 5** work in `consequence_subagent` by replacing one-shot agent + monolithic skill execution with **internal** LangGraph subgraphs and/or sequential chains for:

1. [`skills/consequence-cascade-implementation/SKILL.md`](skills/consequence-cascade-implementation/SKILL.md)
2. [`skills/balancing-realism-and-fantasy/SKILL.md`](skills/balancing-realism-and-fantasy/SKILL.md)

Per [`.cursorrules`](.cursorrules): workers never call other workers; creative workers remain KG read-only; the subgraph is **internal** — the brain still sees one `ConsequenceSubagent` delegation and one `WorkerResponse`.

## Current state

- [`src/agents/workers.py`](src/agents/workers.py) — `ConsequenceSubagent` is a plain `BaseWorkerSubagent` (skill loader + `query_kg_nodes` / `query_kg_edges`), **no** `invoke` override.
- Cascade skill: **nine-step** pipeline, one large artifacts dict (`cascade_chain`, `consequence_chain_entry`, bombs, character/relationship/knowledge updates, `kg_context_used`).
- Realism skill: **five-dimension** audit, large `dimension_reports` + `priority_summary` + `magic_system_updates_recommended`.
- [`src/prompts/consequence_subagent.md`](src/prompts/consequence_subagent.md) — examples partially out of sync with the skill (e.g. `knowledge_matrix_updates` shape); cascade skill still shows **`from_node` / `to_node`** — project standard is **`from` / `to`** ([`.cursorrules`](.cursorrules)).

## Design principles

1. **Prefetch KG in Python** before LLM steps (same idea as [`src/character_integration_chain.py`](src/character_integration_chain.py)): run the query sets defined in each skill with correct Mongo field names so reliability does not depend on the model calling every tool in order.
2. **Smaller structured outputs** per step; avoid one call emitting the entire cascade or full audit until proven stable.
3. **Validation gates** between steps (non-null nested fields, `cascade_chain.action` literals, detonation triggers not chapter-anchored per HANDOFF). Optional **single repair** LLM pass with validation errors.
4. **External contract unchanged**: return value remains `WorkerResponse`-compatible dict for orchestrator / quality gate.

---

## A. `consequence-cascade-implementation` → LangGraph **subgraph** (recommended)

Rationale: clear **validate → repair-or-fail** branch and optional **create_new vs extend_existing** routing after a small linkage decision.

| Node | Responsibility |
|------|----------------|
| `prefetch_kg` | Python: Character nodes for `affected_character_ids`; RELATIONSHIP edges among pairs using `from` / `to`; CascadeChain nodes; Payoff nodes (type consequence bomb). Fill `kg_context_used` counts. |
| `linkage_decision` | LLM, **small** schema: `create_new` \| `extend_existing`, `existing_chain_id`, brief rationale. Inputs: prefetch + `triggering_event`. |
| `trace_immediate_short` | LLM: structured immediate + short-term consequence entries (skill steps 4–5). |
| `bombs_and_tiers` | LLM: Payoff payloads + `priority_tier` + `dual_register`. **Code**: `dual_register` true only if tier is Essential. |
| `state_rel_knowledge` | LLM: `character_state_updates`, `relationship_updates`, `knowledge_matrix_updates` — **one canonical list shape** aligned with [`story_state_manager`](src/story_state_manager_subgraph.py) batch expectations. |
| `assemble` | Python: merge into final `cascade_chain`, `consequence_chain_entry`, full artifacts. |
| `validate` | Python: required keys present; lists never null; detonation heuristics (e.g. no `Ch.`-style primary trigger). |
| `repair_once` or `finalize` | On validation failure: one constrained “fix JSON” LLM call with errors; else build `WorkerResponse`. |

**Prompts**: Trim [`SKILL.md`](skills/consequence-cascade-implementation/SKILL.md) to contract + boundaries; keep per-node system snippets in `src/prompts/` or load slices — follow patterns in [`src/resolution_subgraph.py`](src/resolution_subgraph.py).

**New module (suggested path)**: `src/consequence_cascade_subgraph.py`.

---

## B. `balancing-realism-and-fantasy` → **sequential chain** first

Rationale: five dimensions share one prefetch; a **linear** chain is simpler than a graph unless you later parallelize dimensions.

1. **Prefetch (Python)** — MagicSystem, Faction, Location, Culture, optional POV Character, recent Chapters per skill. Optionally skip MagicSystem when a cheap draft scan finds no magic (skill already allows skipping).
2. **Pass 1 (LLM)** — small schema: `DraftSignals` (e.g. magic-like / violence-like signals, rough counts).
3. **Pass 2 (LLM)** — `FiveDimensionAudit` Pydantic: each dimension `status`, `flagged_passages[]`, dimension-specific fields matching skill §output. If integration tests show brittleness, split into **two** calls (dims 1–2 vs 3–5) with the same prefetch injected twice.
4. **Validate (Python)** — every dimension has `status`; each flagged passage has required strings; `magic_system_updates_recommended` present (may be `[]`); `kg_context_used` complete.
5. **Package** — `WorkerResponse` with `artifacts` as in skill.

**New module (suggested path)**: `src/consequence_realism_chain.py` (or `balancing_realism_chain.py`).

**Subgraph later**: optional LangGraph with parallel dimension nodes + merge only if cost/latency tradeoffs justify it.

---

## C. `ConsequenceSubagent` wiring

In [`src/agents/workers.py`](src/agents/workers.py):

- Add detection similar to `WritingSubagent` (`_is_pov_consistency_request`, etc.): e.g. `context["skill"]`, `operation`, or task substring for `consequence-cascade-implementation` vs `balancing-realism-and-fantasy`.
- `invoke` → `run_consequence_cascade_subgraph(self, state, config)` or `run_balancing_realism_chain(self, state, config)`; **fallback** `super().invoke` for unknown routes during rollout.

---

## D. Contract alignment (do early)

1. Unify **`knowledge_matrix_updates`** across skill, [`consequence_subagent.md`](src/prompts/consequence_subagent.md), and SSM batch payloads.
2. Replace **`from_node` / `to_node`** in cascade skill examples with **`from` / `to`**.
3. Resolve **scene-cycle** `analyze_consequences` artifact block in `consequence_subagent.md` vs actual orchestrator usage — either subgraph emits that shape when `context.operation == "analyze_consequences"` or remove obsolete contract per [`ORCHESTRATOR_SPEC.md`](ORCHESTRATOR_SPEC.md).

---

## E. Testing

- **Unit**: mock structured LLM outputs per node; assert prefetch query shapes, validation failures, and final `WorkerResponse` structure.
- **Integration** (`pytest -m integration`, optional): real LLM + `novelwriter_test_kg` fixture, mirroring [`test_plotting_subagent.py`](test_plotting_subagent.py) style.

---

## F. Implementation order

1. Shared prefetch helpers + SKILL / prompt field fixes.
2. Cascade subgraph + `ConsequenceSubagent` route + tests.
3. Realism chain + route + tests.
4. Add repair node only if metrics show need.

---

## G. Risks

| Risk | Mitigation |
|------|------------|
| Higher latency / cost vs one call | Use flash-tier model per small step; keep nodes minimal. |
| Schema drift | Shared Pydantic models in one module; assert in tests. |
| Brain omits `skill` | Conservative task/context heuristics + safe fallback to legacy agent path during migration. |

---

## References

- Internal chain pattern: [`src/character_integration_chain.py`](src/character_integration_chain.py)
- Subgraph + structured output pattern: [`src/resolution_subgraph.py`](src/resolution_subgraph.py), [`src/plotting_gardener_subgraph.py`](src/plotting_gardener_subgraph.py)
- Conversion guidance: [`skills/langgraph-subgraph-conversion/SKILL.md`](skills/langgraph-subgraph-conversion/SKILL.md), [`.cursor/rules/langgraph-orchestration-conversion.md`](.cursor/rules/langgraph-orchestration-conversion.md)
