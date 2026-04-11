# Novel Writer — Development Handoff Document

**Prepared for:** Fresh Claude instance in Cursor
**Project:** novelwriter — a LangGraph orchestrator-worker agent for Gardener-style novel writing
**Handoff point:** Phases 1–5b complete and verified; Phase 6 remains

---

## 1. What This Project Is

A terminal REPL application that uses a compiled LangGraph state machine to assist
with writing novels using the Gardener approach (character-driven, discovery-based
plotting). The system has one brain node (orchestrator) and seven worker subagents,
each responsible for a group of creative skills. Workers read from a MongoDB knowledge
graph (Story State KG) but only one worker (`story_state_manager`) writes to it.

The authoritative design reference is `ORCHESTRATOR_SPEC.md` (version 4.0 in the spec header). When code and prompt
examples disagree with the spec, the spec wins. Only ask the user for guidance if the
spec itself leaves two materially different implementations open.

---

## 2. Completed and Verified Work

### Phase 1 — Scaffold ✓
Graph compiles. `main.py` runs. MongoDBSaver checkpointer connects. Thread ID persists
across runs.

### Phase 2 — Brain node ✓
Brain produces `BrainDecision` via `with_structured_output`. Quality gate runs.
Reject budget (max 2 re-delegations per task) enforced via `rejection_count` in state.
Iteration limit (15) triggers fallback response. `gemini-3.1-pro-preview` used for
brain; `gemini-3-flash-preview` is unreliable for the nested `QualityVerdict` schema.

### Phase 3 — story_state_manager ✓
KG reads and writes work. `detect_kg_contradiction` gates every write.
Batch write pattern (iterating list fields) implemented in `story_state_manager.md`.
Dual register pattern (Essential consequence bombs inserted as both CascadeChain and
Payoff nodes) implemented.

### Phase 4 — Character integration chain ✓
Three-step internal chain (`character-desire-network` → `character-knowledge-expansion`
+ `character-relationship-matrix`) runs inside `character_subagent` as a single brain
delegation. KG queries run before chain steps, not inside them. KNOWS/DOES NOT KNOW
cross-referencing verified — fix was applied to ensure the rule covers BELIEVES and
SUSPECTS edges, not only KNOWS edges. Test passed with 10 KNOWS edges and 2 directional
RELATIONSHIP edges.

### Phase 5a — Planning and plotting workers ✓ (plotting verified last)
`planning_subagent` passes with correct `seed_document` artifact structure including
populated `validation_record`. `plotting_subagent` passes `test_plotting_subagent.py`
with non-null `obstacle`, `the_choice`, `character_logic_audit`, and non-zero KG
context counts.

### Phase 5b — Writing and consequence workers ✓
`writing_subagent` and `consequence_subagent` use internal chains/subgraphs where
appropriate, the same Mongo-field and artifact guardrails as earlier workers, and
passing integration coverage. Section 4 below is a **reference record** of what
Phase 5b required; it is not open work.

---

## 3. Historical failure modes and guardrails

Most of the issues below **showed up when very long skills were presented as one
monolithic system prompt** (or one enormous skill load per turn), which overloaded
the model and made it skip tool calls or hollow out nested JSON. A lot of that work
has moved into **internal subgraphs and sequential chains**, so each LLM step sees
a smaller, focused instruction set. **Integration tests have not reproduced these
failure modes since those refactors.**

Keep §3 as **guardrails**, not as an active bug list: preserve the Mongo field
discipline (`logical_id`, `from`/`to`, `as_of_chapter`) everywhere, and when you
add or revert to **large monolithic** skill-in-prompt paths, re-apply the patterns
below before expecting stable structured output.

### Bug A — Null nested fields
**Symptom:** Required nested fields (`validation_record`, `obstacle`, `the_choice`,
`character_logic_audit`, etc.) return as `null` even though the reasoning appears
in prose elsewhere in the artifacts.
**Root cause (historical):** Artifact schema examples and instructions did not
treat nested objects as mandatory; worst under monolithic prompts.
**Fix pattern:** In the worker's `.md` prompt file, show every required nested field
fully populated in the artifact schema example and add: `"<field_name>" is required
and must never be null.`

### Bug B — `status: "completed"` instead of `status: "success"`
**Symptom:** Test assertion `status == "success"` fails.
**Root cause:** LLM paraphrases valid status values.
**Fix:** Already applied in `src/agents/base.py` `_build_runtime_prompt` — adds
explicit constraint: `status MUST be exactly one of: 'success', 'need_input',
'blocked', 'failed'.`
**Action:** Verify the fix is present. Do not reapply if already there.

### Bug C — KG queries returning nothing (`character_node_found: false`)
**Symptom:** All `kg_context_used` counts are 0 despite correct KG fixture setup.
**Root cause (historical):** Prompts or context used names like `pov_character_id`
where Mongo expects `logical_id` on Character nodes.
**Fix pattern:** In the worker's `.md` Story State Access section, add explicit
query examples showing `logical_id` as the correct filter field:
```
query_kg_nodes(
    query={"logical_id": "<pov_character_id value>", "type": "Character"},
    as_of_chapter=<chapter_context value>
)
```
**Action:** Verify this fix remains in `plotting_subagent.md`, `writing_subagent.md`,
and `consequence_subagent.md` when editing those prompts.

### Bug D — `function_call` warning drops tool calls
**Symptom:** `Warning: there are non-text parts in the response: ['function_call'],
returning concatenated text result from text parts.`
**Root cause:** Gemini occasionally emits a function call and text in the same
response; SDK discards the function call silently. More likely when the model
mixes long reasoning with tools in one turn.
**Fix:** Set `max_iterations=10` explicitly in the `create_agent` call inside
`BaseWorkerSubagent._build_agent`. Also instruct workers in their `.md` prompts
to call all KG queries before loading the skill file, not interleaved with reasoning
(less critical when the heavy work sits in subgraph nodes with smaller prompts).
**Action:** Verify `max_iterations=10` is present in `_build_agent` when changing
agent setup. Preserve execution-order guidance on any worker that still loads large
skills in a single outer agent.

### Bug E — `from_node`/`to_node` vs `from`/`to` in edge queries
**Symptom:** Edge queries return 0 results even with correct `logical_id` filter.
**Root cause (historical):** Prompt examples used `from_node`/`to_node` while
`query_kg_edges` filters on `from` and `to`.
**Fix:** Applied in `plotting_subagent.md`, `writing_subagent.md`, and
`consequence_subagent.md` — all edge query examples must use `from` and `to`,
not `from_node` and `to_node`. Preserve when editing.

---

## 4. Phase 5b — Writing and Consequence Workers (complete — reference)

The checklist below documents what Phase 5b required. **All items are implemented.**
Use it when auditing or editing prompts, not as a pre-requisite gate.

### 4.1 Prompt hardening (implemented)

**`writing_subagent.md` — the following was required (all done):**

1. Bug C fix — add `logical_id` query examples with correct field names
2. Bug E fix — use `from`/`to` in all edge query examples
3. Bug D fix — add execution order instruction (all KG queries before skill load)
4. Bug A fix — for `scene-construction`, mark these fields as required non-null:
   - `draft_prose` — "Must be non-empty prose text. No JSON, no markdown headers,
     no structural annotations."
   - `scene_metadata.parameter_discrepancy_flag` — "null or a specific description"
   - `scene_metadata.foreshadowing_embedded` — "boolean, never null"
   - `kg_context_used` — "all fields required; zero counts are valid but the
     object must be present"
5. Bug A fix — for `pov-consistency-maintenance`, mark these fields as required:
   - `audit_header.overall_status` — "must be exactly 'CLEAN' or 'VIOLATIONS FOUND'"
   - `violation_log` — "required array; empty array is valid for CLEAN; never null"
   - Each violation entry must have all four fields: `violation_type`,
     `offending_text`, `description`, `correction_note`
6. Add this instruction to the `pov-consistency-maintenance` section:
   "Query the Character node and knowledge matrix BEFORE reading the draft.
   This ordering is mandatory."
7. Add the voice profile co-location note: "The voice profile is stored as
   `properties.voice_profile` inside the Character node. Retrieve it in the
   same `query_kg_nodes` call as the psychological record. If absent, return
   `need_input`."

**`consequence_subagent.md` — the following was required (all done):**

1. Bug C fix — add `logical_id` query examples
2. Bug E fix — use `from`/`to` in edge query examples
3. Bug D fix — execution order instruction
4. Bug A fix — mark these as required non-null:
   - `cascade_chain` — with `action` field ("create_new" or "extend_existing")
   - `consequence_bombs` — "required array; empty array is valid; never null"
   - Each bomb must have `detonation_trigger` as a condition string, never a
     chapter number. Add: "detonation_trigger must describe a story condition
     or character situation. Never use a chapter number."
   - `character_state_updates` — "required array; empty array is valid; never null"
   - `relationship_updates` — "required array; empty array is valid; never null"
   - `knowledge_matrix_updates` — "required array; empty array is valid; never null"

### 4.2 Test fixture requirements for `test_writing_and_consequence.py` (reference)

**Character node must include full `voice_profile`:**
```python
"voice_profile": {
    "vocabulary_range": {
        "lexical_register": "informal, direct",
        "signature_vocabulary_categories": ["spatial", "threat assessment"],
        "avoids": ["courtly register", "abstract nouns"]
    },
    "sentence_structure_patterns": {
        "default_sentence_length": "short and declarative",
        "structural_habits": "observation before interpretation",
        "under_stress": "fragments, no subordination"
    },
    "observational_focus": {
        "primary_lens": "exits and physical threats",
        "secondary_lens": "who holds leverage in the room",
        "systematic_blind_spots": "emotional need in others",
        "how_they_read_people": "hands and feet before faces"
    },
    "internal_thought_patterns": {
        "deliberative_style": "instinct-first, rationalises after",
        "self_monitoring": "minimal",
        "memory_intrusion": "sensory triggers only",
        "relationship_to_time": "present-focused"
    },
    "emotional_processing_style": {
        "speed_of_acknowledgment": "slow",
        "internal_expression": "displaced onto physical observation",
        "what_they_cannot_look_at": "own complicity in past failures",
        "under_extreme_pressure": "affect flattens, catalogues externally"
    }
}
```

**`pov-consistency-maintenance` test must use a hardcoded draft, not output from
`scene-construction`.** The test for the audit skill must be independent. Embed
at least one deliberate violation in the hardcoded draft — a clear head-hop or
knowledge violation — so `VIOLATIONS FOUND` is the expected result and the
`violation_log` structure can be verified.

Example hardcoded draft with deliberate head-hop:
```python
DRAFT_WITH_VIOLATION = (
    "Elara pressed herself against the cold stone wall. "
    "The guards were two corridors away — she could hear their boots. "
    "She needed the eastern passage. "
    "Kael, waiting outside, felt a surge of anxiety as he wondered "
    "if she had been caught. "
    "She moved toward the drain cover and pulled it open."
)
```

**`consequence-cascade-implementation` requires two Character nodes and one
RELATIONSHIP edge** between them so the consequence can propagate across a
relationship. The test should assert:
- `cascade_chain.action` is `"create_new"` or `"extend_existing"` (not null)
- `consequence_bombs` is a non-empty list
- At least one bomb's `detonation_trigger` is a string containing words, not
  a chapter number (assert `not detonation_trigger.startswith("Ch.")` and
  `not any(char.isdigit() for char in detonation_trigger[:3])`)
- `character_state_updates` is a list (empty is acceptable)

### 4.3 Phase 5b test gate (passed)

These were the acceptance criteria before closing Phase 5b; all were satisfied:
1. `draft_prose` is non-empty and contains no JSON, no markdown headers (`#`),
   no code blocks (` ``` `)
2. `pov-consistency-maintenance` returns `overall_status` of `CLEAN` or
   `VIOLATIONS FOUND` with a properly structured `violation_log`
3. `consequence-cascade-implementation` returns a valid `cascade_chain.action`
   and at least one consequence bomb with a condition-based `detonation_trigger`

---

## 5. Phase 6 — Resolution Subagent and End-to-End Verification (remaining)

### 5.1 Resolution subagent implementation

`resolution_subagent` operates in two sequential modes per contradiction event.
The brain calls it twice — once with `mode: "ANALYSE"` and once with
`mode: "IMPLEMENT"` after the user chooses a resolution option.

**Tool access** (verify against spec §7 tool matrix):
- Has: `query_kg_nodes`, `query_kg_edges`, `add_kg_node`, `update_kg_node`,
  `add_kg_edge`, `update_kg_edge`
- Does NOT have: `detect_kg_contradiction`, `init_kg_db`

**ANALYSE mode must produce:**
- `briefing` — plain language, no module IDs, no JSON field names, no system
  mechanics. Written for the user, not the developer.
- `resolution_options` — 2–4 options. Always include one "Accept as intentional
  ambiguity" option when narratively plausible. Always set `recommended_option`.
- Output structured as: `{mode, contradiction_id, briefing, resolution_options,
  recommended_option, recommendation_rationale}`

**IMPLEMENT mode must produce:**
- Execute targeted MongoDB writes for the chosen resolution option only
- Update Module 5.3 (Contradiction node) to close the record
- Emit `re_issue_signal` with `action: "RE_ISSUE_BLOCKED_WRITE"`
- Either all writes succeed or none are committed (no partial commits)

**`resolution_subagent.md` key requirement:** The `briefing` field must be
explicitly instructed as: "Prose the orchestrator can relay verbatim to the user.
No module IDs, no JSON field names, no database terminology."

### 5.2 Brain wiring audit before Phase 6 end-to-end run

Before running the bootstrap, audit `src/brain.py` and `src/prompts/brain.md`
for these five specific behaviours. If any are absent, fix them before the run:

1. **Contradiction routing:** When `story_state_manager` returns
   `status: "blocked"`, the brain's next action must be `delegate` to
   `resolution_subagent` with `mode: "ANALYSE"`. Verify the quality gate
   decision tree handles `"blocked"` status separately from `"failed"`.

2. **`simultaneous_events` forwarding:** The brain must forward
   `simultaneous_events` from `multiple-pov-structure` artifacts into the
   `gardener-plotting-system` context dict. This does not happen automatically.
   Verify `brain.md` registry card `After` field for `plotting_subagent` says:
   "Pass `recommended_next_pov.character_id` as `pov_character_id` AND
   `simultaneous_events` from artifacts into the `gardener-plotting-system`
   context dict."

3. **`story_state_manager` skip in quality gate:** The quality gate must skip
   for `story_state_manager` and `resolution_subagent`. Verify `brain.py`
   quality gate checks `if worker in {"story_state_manager", "resolution_subagent"}:
   skip_quality_gate`.

4. **Persist-before-continue:** After any creative worker returns accepted
   artifacts containing structured records, the brain must delegate to
   `story_state_manager` before the next creative task. Verify `brain.md`
   Operating Rule 3 is present and actionable, not just aspirational.

5. **`rejection_count` reset:** `rejection_count` is reset to 0 in `turn_input`
   in `main.py`. Verify this field is in the turn_input dict.

### 5.3 Phase 6 bootstrap test (§11.1)

Run a full bootstrap with this user input: `"genre: High Fantasy, themes:
legitimacy and the cost of inheritance"`. Do not intervene — let the brain
run autonomously until it produces a `respond` action.

**After bootstrap, query the KG and assert all of these node types exist:**
```python
expected_types = [
    "PlotThread",    # from defining-rough-endpoints Pass 2
    "Payoff",        # from defining-rough-endpoints Pass 2
    "Faction",       # from worldbuilding
    "Location",      # from worldbuilding
    "Culture",       # from worldbuilding
    "Event",         # from worldbuilding (historical events)
    "MagicSystem",   # from worldbuilding
    "Character",     # from character pipeline
]
for node_type in expected_types:
    count = db.nodes.count_documents({"type": node_type, "valid_to": None})
    assert count > 0, f"Missing {node_type} nodes after bootstrap"
```

**Also assert:** `worker_history` from the final state contains 8–12 entries
and no entry has `result.status == "failed"`.

### 5.4 Phase 6 first-scene test (§11.2)

After a successful bootstrap, continue the same session with: `"write the first
scene"`. Let the brain run through the scene cycle.

**After scene cycle, additionally assert:**
```python
# Chapter node created
chapter_count = db.nodes.count_documents({"type": "Chapter", "valid_to": None})
assert chapter_count > 0, "No Chapter nodes after first scene"

# draft_prose appears in worker_history for writing_subagent
writing_results = [
    e for e in worker_history
    if e.get("worker") == "writing_subagent"
]
assert any(
    e.get("result", {}).get("artifacts", {}).get("draft_prose")
    for e in writing_results
), "No draft_prose found in writing_subagent history"
```

---

## 6. Files to Attach to This Conversation

Attach all files in this list. Do not attach files marked "do not attach" — they
are already implemented and tested, and including them wastes context.

### Always attach
| File | Why |
|---|---|
| `ORCHESTRATOR_SPEC.md` | Authoritative design reference — consult §9.4, §9.5, §8.5, §13 heavily |
| `src/agents/base.py` | `BaseWorkerSubagent` structure, `_build_runtime_prompt`, `create_agent` call |
| `src/agents/workers.py` | All worker class definitions; verify tool lists match §7 |
| `src/brain.py` | Quality gate, routing, reject budget, iteration limit |
| `src/state.py` | Shared state schema — `OrchestratorState`, `BrainDecision`, `QualityVerdict` |
| `src/prompts/brain.md` | Worker registry cards; routing After fields |
| `src/world_bible_tools.py` | Tool implementations and actual field names (`from`/`to` not `from_node`/`to_node`) |
| `src/kg_models.py` | KG Pydantic schemas — verify artifact structures against these |

### Phase 5b files (implemented — attach only when editing)
| File | Why |
|---|---|
| `src/prompts/writing_subagent.md` | Reference when changing writing worker behaviour |
| `src/prompts/consequence_subagent.md` | Reference when changing consequence worker behaviour |
| `skills/scene-construction/SKILL.md` | Scene draft structure — do not weaken constraints |
| `skills/pov-consistency-maintenance/SKILL.md` | Audit skill — do not simplify instructions |
| `skills/consequence-cascade-implementation/SKILL.md` | Most structurally complex consequence skill |

### Phase 6 files
| File | Why |
|---|---|
| `src/prompts/resolution_subagent.md` | Implement from scratch against §14 |
| `src/orchestrator.py` | Verify graph wiring, node connections, checkpointer |
| `main.py` | Verify `turn_input` resets, `rejection_count`, stream handling |

### Reference tests (show pattern, do not modify)
| File | Why |
|---|---|
| `test_character_integration_chain.py` | Phase 4 test pattern — use as template |
| `test_plotting_subagent.py` | Phase 5a verified test — shows KG fixture pattern |

### Do not attach
- `src/prompts/planning_subagent.md` — implemented and passing
- `src/prompts/plotting_subagent.md` — implemented and passing
- `src/prompts/character_subagent.md` — implemented and passing
- `src/prompts/writing_subagent.md` — Phase 5b complete
- `src/prompts/consequence_subagent.md` — Phase 5b complete
- All character, planning, and plotting skill files — already implemented
- `skills/scene-construction/SKILL.md`, `skills/pov-consistency-maintenance/SKILL.md`,
  `skills/consequence-cascade-implementation/SKILL.md` — Phase 5b complete
- `src/character_integration_chain.py` — Phase 4 complete

---

## 7. Quick Reference — Field Name Gotchas

These are the naming mismatches that have caused test failures. Keep this list
visible while editing prompts.

| Correct field (in MongoDB) | Wrong field (LLM tends to use) |
|---|---|
| `logical_id` | `character_id`, `pov_character_id`, `node_id` |
| `from` | `from_node` |
| `to` | `to_node` |
| `status: "success"` | `status: "completed"`, `status: "done"` |
| `overall_status: "CLEAN"` | `overall_status: "clean"`, `overall_status: "pass"` |
| `overall_status: "VIOLATIONS FOUND"` | `overall_status: "violations_found"` |
| `properties.voice_profile` | `voice_profile` (top-level), `properties.voice` |

---

## 8. One Paragraph to Paste at the Top of Every Cursor Prompt

Include this verbatim at the start of every new Cursor prompt regardless of phase:

> The Story State KG uses MongoDB with a two-collection design (`nodes` and `edges`)
> with temporal versioning (`valid_from`, `valid_to`). Workers have read-only KG
> access via `query_kg_nodes` and `query_kg_edges`. Only `story_state_manager` writes
> to the KG. The correct filter field for character nodes is `logical_id`, not
> `pov_character_id` or `character_id`. Edge fields are `from` and `to`, not
> `from_node` and `to_node`. The `as_of_chapter` parameter must be passed in every
> KG query. All creative workers return KG-ready records in artifacts — they never
> call write tools directly.
