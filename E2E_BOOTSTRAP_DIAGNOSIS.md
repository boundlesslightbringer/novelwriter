# E2E bootstrap failure — diagnosis

This document records why the full-stack end-to-end bootstrap test (`test_e2e_full_stack.py`, handoff §5.3) can fail with **no `PlotThread` nodes** in Mongo after turn 1, and what that implies about the system.

## What happens in the failing run

From observed run patterns, bootstrap stops very early:

1. **`planning_subagent`** runs `finding-a-seed` and returns **success** artifacts (e.g. `seed_document`, `candidate_seeds_log`, genre/themes).
2. The **brain** delegates to **`story_state_manager`** to persist.
3. **Persistence fails** (or persists nothing that satisfies downstream bootstrap), then the brain routes back to planning with a **retry** task.
4. That retry often returns **`need_input`** (e.g. missing seed constraints), and the turn **terminates** with a user-facing `final_response`.
5. As a result, **no `PlotThread`** (and therefore no downstream bootstrap node types from defining-rough-endpoints Pass 2, worldbuilding, character pipeline) exist in Mongo.

The E2E test therefore fails at the first structural assertion: `PlotThread` count > 0.

## Why this fails (root causes)

There are **two coupled issues**:

### 1. Brain-to-persistence payload contract is inconsistent

`story_state_manager` (via `story_state_manager_subgraph`) expects **write-ready** records: `nodes_to_add`, `edges_to_add`, `nodes_to_update`, `edges_to_update` (and related batch keys), with valid `logical_id` values where required.

The brain often sends **incomplete or malformed** persistence context after a creative worker result. Even when creative artifacts are present in `latest_worker_result`, they are **not consistently transformed** into valid write payloads before the persistence subgraph runs. That leads to validation failures inside the persistence path (e.g. missing write lists, empty `logical_id`, or LLM-generated `nodes_to_add` that do not match tool expectations).

### 2. Bootstrap routing is not robustly state-driven

After a persistence failure, the brain can re-route in a way that **drops required context** and regresses to a fresh “seed generation” request that then fails with **`need_input`**.

In other words, bootstrap progression (`seed → defining-rough-endpoints → worldbuilding → character pipeline`, per spec §11.1) is **not enforced as a deterministic state machine** at the code level; it remains **too sensitive to LLM routing** after errors. Recovery after failed persist is not constrained enough to keep bootstrap progressing.

## Why incremental fixes may not fully resolve it

Targeted hardening (injectable workers/checkpointer for tests, bridging artifacts into `story_state_manager` context, normalizing or synthesizing `logical_id` for some paths) addresses **edges** of the flow.

They do not, by themselves, fix the **core**: the brain can still issue a persistence delegation that is **semantically wrong for the current step**, and post-failure recovery can still **stall or mis-route** bootstrap.

## Bottom line

The E2E test is **correctly exposing** that the system may **not reliably complete Phase 6 bootstrap end-to-end** with a single user prompt (handoff §5.3 string).

The primary defect is in **brain orchestration and the persist handoff contract** (brain → `story_state_manager`), not in Mongo isolation, not in the checkpointer choice for tests, and not in the E2E harness shape itself.

## Suggested direction for a durable fix

- Make **bootstrap phase transitions** explicit in code (or a thin state machine) so the brain cannot skip from “persist seed” to “retry finding-a-seed” without carrying `seed_document` / `chapter_context` / write lists.
- Centralize **artifact → `nodes_to_add` / `edges_to_add`** mapping for known bootstrap steps (at minimum: seed as initial `PlotThread` records per spec) so `story_state_manager` always receives a valid payload when the brain intends persistence.
- After **`story_state_manager` `failed`**, prefer **re-delegating persistence with repaired context** derived from `latest_worker_result.artifacts` rather than re-running planning from scratch without that context.

---

*Related: handoff `HANDOFF_DOCUMENT.md` §5.3–5.4, spec `ORCHESTRATOR_SPEC.md` §11.1–11.2, E2E plan `.cursor/plans/e2e_integration_test_architecture_c70a76d1.plan.md`.*
