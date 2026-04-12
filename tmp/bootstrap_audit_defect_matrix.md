# Bootstrap forensic audit — defect matrix

Partial trace archive: `tmp/bootstrap_e2e_trace.jsonl` (captured before the full `test_e2e_bootstrap_then_first_scene` run was stopped). JSONL events: `brain_quality_gate_creative` (raw `artifacts`, `artifact_validation_errors`, `mapper_errors`, write counts) and `story_state_manager_complete` (SSM `records_updated` / `records_failed`).

**Classification:** **A** = malformed raw worker artifacts; **B** = mapper gap or bad handoff; **C** = SSM / tools / Mongo; **D** = brain orchestration (wrong next step, missing context, quality gate).

| Bootstrap step | Observed symptom | Class | Evidence (trace) | Root cause hypothesis | Minimal fix | Status |
|----------------|------------------|-------|-------------------|------------------------|-------------|--------|
| finding-a-seed | Extra `nodes_to_add` with invalid `StorySeed` / wrong shape (`id`, `type`, not `logical_id`/`node_type`) | A | Line 1: `mapper_errors` skipped record `type: StorySeed` | Planning LLM invented KG write lists and a non-schema node type despite skill contract | Prompt boundary in `src/prompts/planning_subagent.md` (no write lists in artifacts); mapper filters unknown `node_type` | Done (prompt + `ALLOWED_KG_NODE_TYPES` in `src/brain_persistence_mapper.py`) |
| finding-a-seed | First SSM batch would have failed before mapper fix | C | Prior run (pre-fix): `AddNodeArgs` rejected `StorySeed` | Same as row above | Mapper must not forward invalid types | Done |
| character (brain task drift) | `character-creation-suite`, `characters[]` instead of `character_node` + skill contract | A / D | Line 3: `characters` array; SSM persisted `node_1`, `node_2` | Brain task was broad (“develop main characters”); worker returned narrative bundle, not KG-ready `character-creation` artifacts | Tighten `src/prompts/brain.md` bootstrap routing; enforce `context.skill` + single `character-creation` invocation per slot | Open |
| character / relationships | Edges use `source`/`target`/`relation` not `from`/`to`/`edge_type` | A | Line 3: skipped edge records `relation: RIVAL` | LLM graph shape drift vs `PersistPayloadMapper` | Extend mapper `_normalize_edge_add` to accept `source`→`from`, `target`→`to`, map `relation`→`RELATIONSHIP` when unambiguous; and/or prompt `character-creation` / integration skills | Open (optional mapper alias) |
| plotting | `Scene` nodes, `HAS_POV` edges — not in `AddNodeArgs` / `AddEdgeArgs` | A | Line 5: mapper skipped `type: Scene`, generic graph edges | Plotting worker emitted app-level graph, not KG tool schema | Plotting prompt + mapper ignore or map only supported types | Open |
| planning / Pass 2+ | Seed scaffold masks missing real `PlotThread`/`Payoff` from Pass 2 | B / D | Plan doc + `brain_persistence_mapper` seed block | By design today: scaffold fills Mongo when Pass 2 output missing | Gate scaffold behind env once Pass 2 artifacts validated in trace | Future |
| consequence | Empty KG updates after accept path ambiguity | A / D | Trace tail: `quality_verdict: reject`, empty updates | Separate from bootstrap skills; worker returned null-heavy shell | Consequence subgraph / prompt (out of bootstrap audit scope) | Open |

## Tooling delivered

- **Trace:** set `NOVELWRITER_BOOTSTRAP_TRACE=/path/to/file.jsonl`. Logs brain quality-gate rows for creative workers and `story_state_manager_complete` rows from `src/orchestrator.py`.
- **Validators:** `src/bootstrap_artifact_audit.py` + tests in `tests/test_bootstrap_artifact_audit.py`.
- **Prompt:** `src/prompts/character_subagent.md` — structured `character_concept` example; `status: failed` for errors (not `error`).

## Re-running E2E without blocking the session

Full-stack E2E can run **many minutes** (large `max_brain_iterations`, multiple LLM workers). Options:

1. **Unit / integration only:** `uv run pytest tests/test_bootstrap_artifact_audit.py tests/test_brain_persistence_mapper.py tests/test_brain_node.py -q`
2. **Shorter traced smoke (local only):** temporarily lower `NovelWriterConfig(max_brain_iterations=...)` in a scratch script or forked test; expect bootstrap may not finish.
3. **Trace + E2E overnight:** `NOVELWRITER_BOOTSTRAP_TRACE=tmp/run.jsonl uv run pytest tests/test_e2e_full_stack.py -m e2e -k bootstrap --tb=short`

## Exit criteria (plan) — current state

| Criterion | State |
|-----------|--------|
| Valid raw artifacts each audited bootstrap step | Partially met in trace for `finding-a-seed`; character/plotting rows show drift when brain task is not skill-scoped |
| SSM valid payloads without scaffold hacks | Scaffold still present in mapper; documented as follow-up |
| E2E bootstrap + first scene | Not verified in the killed run; re-run when acceptable |
