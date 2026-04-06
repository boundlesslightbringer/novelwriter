# Novel Writer — Orchestrator-Worker Design Specification

**Version:** 4.0 — FINAL IMPLEMENTATION REFERENCE
**Branch:** `feature/orchestrator-agent`
**Status:** Ready for implementation
**Supersedes:** v3.0

---

## Changelog from v3.0

| Section | Change |
|---|---|
| §8 | New: Skill Design Philosophy — quality checks as primary enforcement mechanism |
| §9.2 | `character-integration-with-plot` replaced by three-skill internal chain: `character-desire-network` → `character-knowledge-expansion` + `character-relationship-matrix` |
| §10 | New: Internal Chain Implementation — LangChain architecture for character integration |
| §11.1 | Bootstrap flow updated to reflect character integration chain |
| §12 | `CascadeChain (anticipatory)` row removed — anticipatory ledger seeding removed from integration pipeline entirely |
| §13 | Pointer 13.15 added for chain implementation; pointer 13.5 updated to reference new skill names |
| §16 | Skill file list updated for character subagent; chain implementation file added |
| Throughout | All references to `character-integration-with-plot` as a single skill replaced |

---

## 1. Purpose and Scope

This document is the authoritative implementation reference for the Novel Writer orchestrator-worker graph. It covers:

- Graph topology and message-passing model
- Shared state schema
- Brain node design (decision model, prompt architecture, quality gate)
- Skill design philosophy
- Worker tool access boundaries
- Per-skill input/output contracts and KG query patterns
- Internal chain implementation for character integration
- Cross-skill data flows
- Story State record lifecycle
- Implementation pointers — ordered by severity

---

## 2. System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                         Terminal (main.py)                      │
│   User input ──► graph.stream(turn_input)                       │
│   Printed output ◄── stream_mode=["messages","updates"]         │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │   LangGraph Graph    │
                  │  (compiled, with     │
                  │   MongoDBSaver)      │
                  └──────────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │   MongoDB            │
                  │  novelwriter_kg      │  ← Story State KG
                  │  novelwriter_chk     │  ← LangGraph checkpoints
                  └──────────────────────┘
```

---

## 3. Graph Topology

### 3.1 Node inventory

| Node | Type | KG access | Skills |
|---|---|---|---|
| `brain` | Orchestrator | None | — |
| `planning_subagent` | Worker | Read-only | finding-a-seed, defining-rough-endpoints, worldbuilding, research-integration |
| `character_subagent` | Worker | Read-only | character-conception, character-creation, character-voice-differentiation, character-desire-network → character-knowledge-expansion + character-relationship-matrix (internal chain) |
| `plotting_subagent` | Worker | Read-only | gardener-plotting-system, multiple-pov-structure, braided-narrative-technique, conflict-layering, plot-thread-tracking |
| `writing_subagent` | Worker | Read-only | scene-construction, pov-consistency-maintenance, pacing, layering-history-and-legend, professional-writing-techniques |
| `consequence_subagent` | Worker | Read-only | consequence-cascade-implementation, balancing-realism-and-fantasy |
| `story_state_manager` | Worker | Full (R+W) | All KG reads and writes |
| `resolution_subagent` | Worker | Write subset | contradiction-resolution (ANALYSE + IMPLEMENT) |
| `respond` | Terminal | None | — |

### 3.2 Full topology diagram

```
       START
         │
         ▼
      [brain] ◄──────────────────────────────────────────────────────┐
         │                                                            │
         │ route_from_brain()                                         │
         │                                                            │
         ├──► [planning_subagent] ────────────────────────────────────┤
         ├──► [character_subagent] ───────────────────────────────────┤
         ├──► [plotting_subagent] ────────────────────────────────────┤
         ├──► [writing_subagent] ─────────────────────────────────────┤
         ├──► [consequence_subagent] ─────────────────────────────────┤
         ├──► [story_state_manager] ──────────────────────────────────┤
         ├──► [resolution_subagent] ──────────────────────────────────┘
         │
         └──► [respond] ──► END
```

All conditional routing lives in `route_from_brain`. Every worker has one unconditional edge back to `brain`. Workers never chain to each other directly.

---

## 4. Shared State Schema

### 4.1 Field definitions

| Field | Type | Reducer | Reset per turn | Description |
|---|---|---|---|---|
| `messages` | `list[BaseMessage]` | `add_messages` | No | Full conversation history |
| `iteration_count` | `int` | Last write wins | Yes → 0 | Brain visits in current turn |
| `final_response` | `str \| None` | Last write wins | Yes → None | Set by brain on respond/clarify |
| `active_worker` | `str \| None` | Last write wins | Yes → None | Worker brain has delegated to |
| `worker_request` | `dict \| None` | Last write wins | Yes → None | `{task, context, reasoning}` |
| `latest_worker_result` | `dict \| None` | Last write wins | Yes → None | Most recent worker output |
| `worker_history` | `list[dict]` | `operator.add` | No | Full audit trail across session |

### 4.2 Why `latest_worker_result` resets per turn

Without this reset the brain on turn 2 would read a stale worker result from turn 1. The reset in `turn_input` ensures the brain's Layer 3 context block starts clean each user turn while `worker_history` (which uses `operator.add`) retains the full session audit trail.

---

## 5. Brain Node

### 5.1 BrainDecision schema

```python
class QualityVerdict(BaseModel):
    verdict : Literal["accept", "reject", "needs_clarification"]
    reason  : str   # internal only; never shown to user

class BrainDecision(BaseModel):
    reasoning          : str
    action             : Literal["delegate", "respond", "clarify"]
    worker             : Literal[<VALID_WORKERS>] | None
    task               : str | None
    context            : dict | None
    response           : str | None
    quality_assessment : QualityVerdict | None  # None for infrastructure workers
```

`quality_assessment` is populated when reviewing creative artifacts. It is always `None` after `story_state_manager` and `resolution_subagent` — those are infrastructure workers, not creative.

### 5.2 Three-layer prompt construction

```
Layer 1 — SystemMessage (brain.md, loaded once at startup, static)
  § Role and mandate
  § Operating rules (6 rules including persist-after-accept and contradiction handling)
  § Quality gate rules and reject budget
  § BrainDecision output field table
  § Worker registry (7 cards × ~55 tokens ≈ 385 tokens)
  ─────────────────────────────────────────
  Total Layer 1: ~985 tokens

Layer 2 — BaseMessages (full conversation history, all prior turns)

Layer 3 — HumanMessage (constructed per invocation; NOT persisted to messages)
  [Last worker result]
    Worker  : <name>
    Task    : <task string>
    Status  : <status>
    Summary : <summary>
    Artifacts: <json, string values truncated at 600 chars>
  [Recent worker history] — last 3 entries only
  ─────────────────────────────────────────
  Total Layer 3: ~300–600 tokens

Total per brain invocation (excluding message history): ~1,285–1,585 tokens
```

Layer 3 is injected as a `HumanMessage` that is not appended to `state["messages"]`. It is machine-facing context consumed by the structured LLM call but never visible to the user and never accumulates across turns.

### 5.3 Quality gate decision tree

```
latest_worker_result received
  │
  ├── worker == story_state_manager or resolution_subagent?
  │    └── YES → skip quality gate entirely; continue workflow
  │
  ├── status == "failed"?    → action="respond", surface failure to user
  ├── status == "need_input"?→ action="clarify", relay follow_up_questions
  │
  └── status == "success"
       ├── artifacts empty or missing expected keys?
       │    └── verdict="reject" → re-delegate same worker (see reject budget)
       ├── artifacts not addressing the task?
       │    └── verdict="needs_clarification" → action="clarify"
       └── artifacts well-formed and task-relevant?
            └── verdict="accept"
                 ├── structured records present? → delegate story_state_manager
                 └── no persist needed?          → action="respond"
```

### 5.4 Reject budget

The brain may reject and re-delegate to the same worker **at most 2 times** per task before escalating to the user. On the third failure, `action="respond"` surfaces the issue. This prevents silent correction loops consuming the iteration budget without user awareness.

### 5.5 Operating rules (encoded in brain.md)

1. **One decision per invocation.** One `BrainDecision` per brain visit.
2. **Apply quality gate before persisting.** Never route rejected or malformed artifacts to `story_state_manager`.
3. **Persist accepted records before continuing creative work.** Next creative delegation only after persistence confirms success.
4. **Handle contradictions immediately.** On `story_state_manager` returning `status: "blocked"`, delegate `resolution_subagent` with `mode: "ANALYSE"` before any other action.
5. **Clarify before delegating.** If intent is genuinely ambiguous, use `action: "clarify"` with one targeted question.
6. **Respect the iteration limit.** Default 15; on exhaustion use `action: "respond"` to summarise progress.

### 5.6 Worker registry cards in brain.md

Each worker gets one card. The `After` field is the most operationally important — it encodes what the brain does next based on the worker's output. Character subagent card must reflect the internal chain (one delegation produces all integration records):

```
**character_subagent**
Domain: Character lifecycle — conception, creation, voice differentiation,
  integration (desire network → knowledge expansion + relationship matrix).
Route when: A new character is needed; an existing character requires depth;
  a POV character needs a voice profile; characters need integrating into
  the relationship matrix and knowledge system.
Context keys:
  `skill` — one of "character-conception" | "character-creation" |
            "character-voice-differentiation" | "character-integration"
  `character_ids`     — list of logical_ids (for character-integration)
  `character_id`      — single logical_id (for voice differentiation)
  `character_concept` — for character-creation
  `chapter_context`   — always required
Returns: character concept; full character record (KG-ready); voice profile
  update; or combined knowledge matrix + relationship matrix records from
  the internal three-step chain.
Quality gate: character-integration must return both
  `knowledge_matrix_expansions` and `relationship_records` non-empty.
After: if artifacts contain character or integration records →
  route to story_state_manager.
```

---

## 6. Routing Function

```python
VALID_WORKERS: frozenset[str] = frozenset({
    "planning_subagent", "character_subagent", "plotting_subagent",
    "writing_subagent", "consequence_subagent",
    "story_state_manager", "resolution_subagent",
})

def route_from_brain(state: OrchestratorState) -> str:
    if state.get("final_response") is not None:
        return "respond"
    worker = state.get("active_worker")
    if worker and worker in VALID_WORKERS:
        return worker
    return "respond"   # safe fallback; graph never gets stuck
```

`VALID_WORKERS` is defined once in `src/state.py` and imported by both `src/brain.py` (to type `BrainDecision.worker` as a `Literal`) and `src/orchestrator.py` (for the routing guard). One definition, two consumers, no divergence.

---

## 7. Tool Access Matrix

Tools are passed to `create_agent` at construction time. A worker cannot call a tool absent from its list — enforced by LangGraph at the agent level, not by prompt instruction.

```
                         progressive  query   query   add     update  add     update  detect  init
                         _skill_      _kg_    _kg_    _kg_    _kg_    _kg_    _kg_    _kg_    _kg_
                         loader       nodes   edges   node    node    edge    edge    contr.  db
─────────────────────────────────────────────────────────────────────────────────────────────────
planning_subagent          ✓           ✓       ✓       ✗       ✗       ✗       ✗       ✗       ✗
character_subagent         ✓           ✓       ✓       ✗       ✗       ✗       ✗       ✗       ✗
plotting_subagent          ✓           ✓       ✓       ✗       ✗       ✗       ✗       ✗       ✗
writing_subagent           ✓           ✓       ✓       ✗       ✗       ✗       ✗       ✗       ✗
consequence_subagent       ✓           ✓       ✓       ✗       ✗       ✗       ✗       ✗       ✗
story_state_manager        ✗           ✓       ✓       ✓       ✓       ✓       ✓       ✓       ✓
resolution_subagent        ✗           ✓       ✓       ✓       ✓       ✓       ✓       ✗       ✗
brain                      ✗           ✗       ✗       ✗       ✗       ✗       ✗       ✗       ✗
respond                    ✗           ✗       ✗       ✗       ✗       ✗       ✗       ✗       ✗
```

Creative workers have `query_kg_nodes` and `query_kg_edges` — read-only — and self-fetch all KG context they need rather than receiving pre-fetched excerpts from the brain.

---

## 8. Skill Design Philosophy

### 8.1 The core principle

Every skill file enforces output quality through two mechanisms: a tightly specified output schema and a quality checks section. The relative weight of these two mechanisms differs by skill type.

**For most skills — quality checks as primary enforcement:**
The step-by-step instructions in a skill file are guidelines that orient the LLM's reasoning. The output schema defines precisely what must be produced. The quality checks section is what the LLM explicitly verifies against before returning output. For skills whose task is creative, analytical, or generative, the quality checks section is the primary enforcement mechanism — the instruction steps set direction, but the checks are what the LLM is held to. Instruction steps for these skills are kept to 3–5 key decision points, not exhaustive procedures.

**For audit skills — procedural detail is the point:**
Three skills are exceptions to this principle: `pov-consistency-maintenance`, `conflict-layering`, and `balancing-realism-and-fantasy`. These skills apply specific tests to specific material and return structured verdicts. For them, the step-by-step instructions define *which tests to apply and in what order*, and skipping a step produces a qualitatively different (worse) audit. These skills keep detailed procedural instructions.

### 8.2 Quality checks section requirements

Every skill's quality checks section must:
- Be structured as a checkable list (the LLM reads it as a self-verification pass before returning)
- Include at least one check that directly catches the most common failure mode for that skill
- Distinguish between "failure" items (if not met, return `need_input` or flag the issue) and "warning" items (note in artifacts but proceed)
- End with explicit confirmation that no KG writes occurred from this skill

### 8.3 Skill length targets

| Skill category | Instruction steps | Total length |
|---|---|---|
| Audit skills (pov-consistency, conflict-layering, realism audit) | Detailed (6–9 steps) | 1,500–2,000 words |
| Complex generative skills (character-creation, consequence-cascade) | Moderate (5–7 steps) | 1,000–1,500 words |
| Standard generative skills (most planning, plotting, writing skills) | Concise (3–5 steps) | 600–1,000 words |
| Analysis-only skills (desire-network, pacing, research-integration) | Minimal (3–4 steps) | 400–700 words |

### 8.4 What the output schema enforces that instructions cannot

The output schema (the `artifacts` JSON structure in each skill file) provides the LLM with structural constraints that are more reliable than procedural instructions:
- Required field presence is schema-enforced (the LLM knows the field must appear)
- Type constraints catch category errors (a string where a list is expected)
- The brain's quality gate checks key field presence, so an absent field causes a quality gate rejection and re-delegation

Invest in a precise output schema. Reduce reliance on instruction steps.

---

## 9. Per-Skill Interface Reference

### 9.1 Planning Subagent Skills

#### finding-a-seed

| Item | Detail |
|---|---|
| **KG reads** | None — invoked at project start; no Story State exists |
| **Key context keys** | `genre` (required), `themes` (required), `subgenres`, `thematic_interdependencies`, `negative_space` |
| **Artifacts out** | `seed_document` (seed, validation record, questions); `candidate_seeds_log`; echoed `genre`, `themes`, `subgenres` |
| **Brain routing after** | Persist seed document as initial PlotThread seeds → `story_state_manager`; then delegate `defining-rough-endpoints` Pass 1 |
| **Halt condition** | `genre` or `themes` absent → return `need_input` |

#### defining-rough-endpoints

| Item | Detail |
|---|---|
| **KG reads** | Pass 1: none (standard). Pass 1 reassess: PlotThread, Chapter, Character nodes. Pass 2: none |
| **Key context keys** | Pass 1: `seed_document`. Pass 2: `character_concepts` (list), `pass_1_output` |
| **Artifacts out** | Pass 1: draft compass + `character_slot_sketches`. Pass 2: final compass + `plot_thread_seeds` (KG-ready PlotThread nodes) + `payoff_seeds` (KG-ready Payoff nodes) |
| **Brain routing after** | Pass 1: delegate `character_subagent` once per slot sketch (early invocation mode). Pass 2: persist records → `story_state_manager`; then delegate `worldbuilding` |
| **Two-pass handoff** | Brain collects all Pass 1 slot sketches, delegates `character_subagent` for each, then delegates Pass 2 with full `character_concepts` list |

#### worldbuilding

| Item | Detail |
|---|---|
| **KG reads** | Initial: none. Targeted expansion: Faction, Location, Culture, MagicSystem, historical Event nodes at `as_of_chapter` |
| **Key context keys** | `endpoint_compass` (required), `research_output` (optional), `expansion_scope` (optional), `chapter_context` |
| **Artifacts out** | `political_power_map` (Faction nodes), `geography` (Location nodes), `cultures_customs_religion` (Culture nodes), `history_and_legends` (historical Event nodes), `magic_system` (MagicSystem node), `location_connections` (CONNECTED_TO edges) — all KG-ready |
| **Brain routing after** | Persist all records → `story_state_manager`; then begin character pipeline |

#### research-integration

| Item | Detail |
|---|---|
| **KG reads** | None |
| **Key context keys** | `domain_type` (required), `research_question` (required), `story_context` (required), `specificity_constraints` |
| **Artifacts out** | `domain_summary`, `key_structural_facts_or_patterns`, `useful_specifics`, `what_is_commonly_misrepresented`, `story_relevant_cautions`, `anti_plagiarism_note` (speculative domains), `further_questions` |
| **Brain routing after** | Pass `research_output` artifacts as context key in the delegation requiring the grounding. No persist needed |

---

### 9.2 Character Subagent Skills

#### character-conception

| Item | Detail |
|---|---|
| **KG reads** | Standard mode: Faction, Location, Character, active PlotThread nodes at `as_of_chapter`. Early invocation mode: none |
| **Mode detection** | `character_slot_sketch` in context → early invocation mode; `narrative_role` + `chapter_context` → standard mode |
| **Key context keys** | Standard: `narrative_role`, `chapter_context`. Early: `character_slot_sketch`, `world_context_sketch` |
| **Artifacts out** | `character_concept` (role, method, core contradiction, sketch, open questions); `provisional_flag` (early mode only, flags assumptions needing revision after worldbuilding); `kg_context_used` |
| **Brain routing after** | Pass `character_concept` as context to `character-creation`. In early invocation mode, also pass back to `planning_subagent` for `defining-rough-endpoints` Pass 2 once all slots are conceived |

#### character-creation

| Item | Detail |
|---|---|
| **KG reads** | Faction, Culture, Location nodes (world context); Character nodes (pre-story relationships); KnowledgeItem nodes. All at `as_of_chapter` |
| **Key context keys** | `character_concept` (required), `chapter_context` (required), `research_output` (optional), `feedback` (optional on re-delegation) |
| **Artifacts out** | `character_node` (full Character KG record including `core_wound`, `core_desire`, `core_fear`, `self_deception`, `response_patterns`, `arc_type`); `knowledge_matrix_edges` (KNOWS edges); `knowledge_items` (KnowledgeItem nodes); `relationship_edges` (RELATIONSHIP edges, pre-story only); `culture_edge` (BELONGS_TO_CULTURE edge) |
| **Brain routing after** | Persist all records → `story_state_manager`; then delegate `character-voice-differentiation` (if POV eligible); then `character-integration` after all characters in the cohort are created |
| **Logical ID convention** | `char_<firstname_lastname_slug>`, `ki_<description_slug>`, `rel_<a_slug>_<b_slug>` — consistent naming enforced by all skills |

#### character-voice-differentiation

| Item | Detail |
|---|---|
| **KG reads** | Character node (full record); BELONGS_TO_CULTURE edge + Culture node; all POV-eligible Character nodes (to retrieve existing `properties.voice_profile` records for differentiation notes) |
| **Key context keys** | `character_id` (required), `chapter_context` (required), `research_output` (optional) |
| **Artifacts out** | `character_id`; `voice_profile` (five-dimension object for merge into `properties.voice_profile` on Character node); `differentiation_notes`; `kg_context_used` |
| **Brain routing after** | Route as `update_kg_node` to `story_state_manager` — merges `voice_profile` into `properties.voice_profile` on Character node |
| **Key design decision** | Voice profile stored as `properties.voice_profile` sub-record of the Character node. `writing_subagent` retrieves both psychological record and voice profile in one `query_kg_nodes` call |

#### character integration — internal chain

The brain delegates character integration as a single task to `character_subagent`. The subagent runs an internal three-step LangChain chain and returns one combined `WorkerResponse`. The brain makes **one delegation** and receives **one result**. See §10 for the full chain implementation.

**Step 1 — character-desire-network:**

| Item | Detail |
|---|---|
| **KG reads** | Character nodes (all `character_ids`); Faction nodes; active PlotThread nodes |
| **Input** | Character nodes, Faction nodes, PlotThread nodes (assembled by `character_subagent` from KG before chain runs) |
| **Output** | `desire_network` document: list of character pairs each classified as `compatible`, `conflicting`, or `invisible`, with specific desire descriptions; `key_tensions`; `notes` |
| **Purpose** | Analytical scaffold consumed by both Step 2 and Step 3. Pure analysis — no KG records |
| **Cognitive task** | Single: map structural relationships between character desires |

**Step 2 — character-knowledge-expansion:**

| Item | Detail |
|---|---|
| **KG reads** | Existing KNOWS edges from KG (to avoid duplicating character-creation entries) |
| **Input** | Character nodes + existing KNOWS edges (from KG) + `desire_network` (from Step 1) |
| **Output** | `new_knowledge_items` (KnowledgeItem node records); `new_knows_edges` (KNOWS edge records with KNOWS/BELIEVES/SUSPECTS/DOES NOT KNOW status); `flags` |
| **Key constraint** | Cross-referencing rule: for every `KNOWS` edge created for Character A about B, a corresponding `DOES NOT KNOW` edge must be created for Character B about the same KnowledgeItem. This is checked in the quality checks section and verified by the brain's quality gate |
| **Cognitive task** | Single: derive information asymmetries from desire network and character psychology |

**Step 3 — character-relationship-matrix:**

| Item | Detail |
|---|---|
| **KG reads** | Existing RELATIONSHIP edges from KG (created by character-creation for pre-story relationships) |
| **Input** | Character nodes + existing RELATIONSHIP edges (from KG) + `desire_network` (from Step 1) |
| **Output** | `new_relationship_edges` (RELATIONSHIP edge records for pairs with no existing edge); `updated_relationship_edges` (update payloads for edges created by character-creation — adding trajectory, convergence_potential, power_dynamic detail); `flags` |
| **Key constraint** | Directionality: A→B and B→A are separate records. The asymmetry between them is the primary diagnostic signal. Every pair produces two records. Every record specifies power dynamic type and whether it is accurately perceived by both parties |
| **Cognitive task** | Single: build directional relationship matrix from desire network and character psychology |

**Combined artifacts returned to brain:**

```json
{
  "knowledge_matrix_expansions": {
    "new_knowledge_items": [...],
    "new_knows_edges": [...]
  },
  "relationship_records": {
    "new_relationship_edges": [...],
    "updated_relationship_edges": [...]
  },
  "integration_flags": [...]
}
```

`integration_flags` merges flags from Steps 2 and 3. The brain relays non-empty flags to the user.

**What was removed from the original skill:**
Anticipatory CascadeChain (consequence ledger seeding) was removed entirely. Anticipatory chains created before writing begins are speculative and are replaced by accurate records from `consequence-cascade-implementation` as actual events occur. Removing this task makes the three remaining tasks cleaner and produces only records that remain accurate over the course of the story.

---

### 9.3 Plotting Subagent Skills

#### gardener-plotting-system

| Item | Detail |
|---|---|
| **KG reads** | Character node (POV character, includes `properties.voice_profile`); KNOWS edges + KnowledgeItem nodes; INVOLVES edges + PlotThread nodes for POV character; CascadeChain nodes; optionally Payoff nodes with `resolution_status: "Pending"` |
| **Key context keys** | `pov_character_id` (required), `chapter_context` (required), `last_scene_outcome` (required), `pacing_guidance` (optional), `include_foreshadowing_check` (optional boolean) |
| **Artifacts out** | `scene_parameters` (goal, obstacle with internal/external/interpersonal components, the_choice, consequence shape, `character_logic_audit`); `active_thread_flags`; `active_consequence_flags`; `foreshadowing_opportunity`; `parameter_discrepancy_flag`; `kg_context_used` |
| **Brain routing after** | Pass `scene_parameters` + `simultaneous_events` (from prior `multiple-pov-structure` artifacts) as context to `writing_subagent (scene-construction)`. `active_thread_flags` and `active_consequence_flags` tell brain which records to update after scene is written |
| **Discrepancy handling** | If `parameter_discrepancy_flag` is non-null, brain resolves before delegating `scene-construction`. Do not silently forward a flagged parameter set |

#### multiple-pov-structure

| Item | Detail |
|---|---|
| **KG reads** | Chapter nodes (sort by `chapter_number` after retrieval — query does not guarantee order); non-historical Event nodes; POV-eligible Character nodes; active + dormant PlotThread nodes; CONNECTED_TO edges |
| **Key context keys** | `chapter_context` (required), `endpoint_compass` (optional), `active_thread_ids` (optional) |
| **Artifacts out** | `recommended_next_pov` (character_id + specific narrative reasoning); `simultaneous_events` (each with `pov_can_know`, `dramatic_irony_active`, `timeline_contradiction_risk`); `rotation_pressure_flags`; `cliffhanger_handling`; `pov_proliferation_check` |
| **Brain routing after** | Pass `recommended_next_pov.character_id` as `pov_character_id` AND pass `simultaneous_events` in context dict of the subsequent `gardener-plotting-system` delegation. Both fields must be forwarded — `simultaneous_events` is not automatic |
| **Sibling skill** | `single-pov-structure` is used instead when the user specifies the next POV. Same output structure, different entry point |

#### braided-narrative-technique

| Item | Detail |
|---|---|
| **KG reads** | Chapter nodes (sorted); PlotThread nodes (all statuses); INVOLVES edges; POV-eligible Character nodes; DEPENDS_ON edges |
| **Key context keys** | `chapter_context` (required), `analysis_range` (optional `{from_chapter, to_chapter}`), `endpoint_compass` (optional) |
| **Artifacts out** | `braid_map_summary`; `redundancy_flags` (each with `new_information_test`, `new_register_test`, `verdict`); `convergence_opportunities` (Planned / Discovered / Near-miss); `parallel_tension_assessment` (with `isolation_risk` flag); `recommendations` (immediate / near_term / monitor) |
| **Brain routing after** | `recommendations.immediate` items may trigger re-delegation of `writing_subagent (scene-construction)`, `plotting_subagent (multiple-pov-structure)`, or `plotting_subagent (gardener-plotting-system)`. No persist needed |
| **Invocation cadence** | Not mandatory at every chapter boundary. Invoked on specific braiding concerns or periodic health checks (~every 5–10 chapters) |

#### conflict-layering

| Item | Detail |
|---|---|
| **KG reads** | Character node (POV character); RELATIONSHIP edges from POV character to `other_character_ids` |
| **Key context keys** | `draft_scene` (required), `pov_character_id` (required), `chapter_context` (required), `scene_intended_function` (optional), `other_character_ids` (optional) |
| **Artifacts out** | `audit_header` with `momentum_verdict` (EARNING ITS PLACE / UNDERLOADED / CARRYING DEAD WEIGHT / SCENE PURPOSE QUESTION); `conflict_present`; `conflict_absent_or_underused` (only when absence causes a named, specific problem); `conflict_weight_assessment` (five levels); `suggestions` (ranked, only when verdict is not EARNING ITS PLACE); `scene_rhythm_note` |
| **Brain routing after** | EARNING ITS PLACE → no action required. Otherwise → re-delegate `writing_subagent (scene-construction)` with audit as `conflict_layering_audit` in context. No persist needed |
| **Audit skill** | Keeps detailed procedural instructions per §8.1. Absent levels are `"Absent — not applicable"` unless absence causes a specific named problem |

#### plot-thread-tracking

| Item | Detail |
|---|---|
| **KG reads** | PlotThread nodes (all); Payoff nodes (Pending + Overdue); DEPENDS_ON edges; INVOLVES edges; PAYS_OFF_IN edges. Convergence mode adds: CascadeChain nodes; Payoff nodes of type "Consequence bomb" |
| **Key context keys** | `chapter_context` (required), `convergence_mode` (boolean, default false), `endpoint_compass` (optional), `window_lookahead` (optional int, default 5) |
| **Artifacts out** | `thread_load_summary`; `active_thread_status`; `overdue_flags`; `pending_payoffs_status`; `convergence_bomb_sweep` (with `essential_bombs` detonation path assessments, `enriching_bombs` opportunity flags, `unclassified_bombs` reclassification recommendations, `registration_gaps`); `convergence_opportunities`; `thread_health_assessment`; `no_thread_abandonment_check`; `priority_summary` |
| **Brain routing after** | `registration_gaps` → route `update_kg_node` / `add_kg_node` writes to `story_state_manager` (add missing Payoff node registrations for Essential bombs). Reclassification recommendations → route `update_kg_node` to `story_state_manager`. No prose changes |
| **Convergence mode** | Brain sets `convergence_mode: true` at Convergence Checkpoint. Without it, `convergence_bomb_sweep.performed = false` |

---

### 9.4 Writing Subagent Skills

#### scene-construction

| Item | Detail |
|---|---|
| **KG reads** | Character node (POV character — includes `properties.voice_profile`); KNOWS edges + KnowledgeItem nodes (knowledge matrix); Payoff nodes `resolution_status: "Pending"` (if foreshadowing check); Location node for scene setting |
| **Key context keys** | `scene_parameters` (required, from gardener-plotting-system); `chapter_context` (required); `pacing_guidance` (optional); `conflict_layering_audit` (optional, on re-delegation); `pov_consistency_flags` (optional, on re-delegation); `feedback` (optional, on re-delegation) |
| **Artifacts out** | `draft_prose` (prose only — no markup, no headers, no annotations); `scene_metadata` (`pov_character_id`, `foreshadowing_embedded`, `foreshadowing_payoff_id`, `parameter_discrepancy_flag`, `approximate_word_count`); `kg_context_used` |
| **Brain routing after** | Always delegate `pov-consistency-maintenance` next. If `foreshadowing_embedded: true` and scene is later accepted, route Payoff node update to `story_state_manager`. If `parameter_discrepancy_flag` non-null, re-delegate `gardener-plotting-system` before accepting |
| **Voice profile access** | `properties.voice_profile` retrieved in same `query_kg_nodes` call as psychological record. If absent on a POV-eligible character, return `need_input` — character-voice-differentiation must run first |

#### pov-consistency-maintenance

| Item | Detail |
|---|---|
| **KG reads** | Character node (includes `properties.voice_profile`); KNOWS edges + KnowledgeItem nodes. **Both must be queried BEFORE the draft is read** — mandatory procedural ordering |
| **Key context keys** | `draft_scene` (required), `pov_character_id` (required), `chapter_context` (required) |
| **Artifacts out** | `audit_header` (`overall_status`: CLEAN or VIOLATIONS FOUND, `violation_count`, `violation_types_found`); `violation_log` (each entry: `violation_type`, `offending_text` quoted verbatim, `description`, `correction_note`); `summary_pattern_note` |
| **Brain routing after** | CLEAN → proceed (optionally `conflict-layering`, then `layering-history-and-legend`, then brain creates Chapter node). VIOLATIONS FOUND → re-delegate `scene-construction` with `violation_log` as `pov_consistency_flags` |
| **Audit skill** | Keeps detailed procedural instructions per §8.1. CLEAN is a complete, valid output — not a failure to find violations |
| **Five violation categories** | Knowledge Violation (highest severity), Head-Hopping, Omniscient Intrusion, External Self-Description, Voice Inconsistency — audited in this order, grouped in this order in output |

#### pacing

| Item | Detail |
|---|---|
| **KG reads** | Character node (POV character — full record including `emotional_state`, `arc_stage`, `injuries_physical_state`, `response_patterns`, `core_wound`, `self_deception`) |
| **Key context keys** | `pov_character_id` (required), `chapter_context` (required), `last_scene_outcome` (required), `chapter_emotional_arc` (required) |
| **Artifacts out** | `character_psychology_summary` (specific to this character — not generalisable); `scene_rhythm_register` (one of 8 registers + justification tracing the specific derivation + optional internal shift with trigger and destination register); `sentence_density`; `interiority_level`; `dialogue_to_action_ratio`; `chapter_arc_alignment_note`; `tension_flags` (character-specific named behavioural patterns, not generic advice) |
| **Brain routing after** | Pass full artifacts as `pacing_guidance` in subsequent `scene-construction` context dict |
| **Invocation trigger** | Only when POV character's psychological/emotional state has shifted significantly. Not on fixed schedule |

#### layering-history-and-legend

| Item | Detail |
|---|---|
| **KG reads** | KNOWS edges + KnowledgeItem nodes (knowledge matrix); BELONGS_TO_CULTURE edge + Culture node; historical Event nodes (`is_historical: true`); optionally Location node (if `scene_location_id` provided); other characters' Culture nodes for conflicting interpretations |
| **Key context keys** | `draft_scene` (required, POV-consistent draft from pov-consistency-maintenance CLEAN output), `pov_character_id` (required), `chapter_context` (required), `scene_location_id` (optional) |
| **Artifacts out** | `revised_draft` (complete revised prose — not a diff); `integration_log` (every candidate evaluated, including those rejected); `referenced_events_to_update` (list of `{event_logical_id, chapter_to_add}`) |
| **Brain routing after** | Route `referenced_events_to_update` as `update_kg_node` calls to `story_state_manager`. Revised draft replaces base draft as version of record going into Chapter node |
| **Invocation cadence** | Not every scene. Only when scene location, characters, or themes intersect with historical Event or Culture records in Story State |

#### professional-writing-techniques

| Item | Detail |
|---|---|
| **KG reads** | Character node (always); CascadeChain nodes (consequence trace-back problems only); recent Chapter nodes (timeline problems only). Query only what the specific problem type requires |
| **Key context keys** | `problem_description` (required), `pov_character_id` (required), `chapter_context` (required), `stuck_draft` (optional), `technique_hint` (optional) |
| **Artifacts out** | `technique_applied`; `problem_diagnosis` (type, root cause, available material); `path_forward` (primary recommendation + `worked_application` specific to this character and situation); `scene_construction_context` (pre-built paragraph for direct use as `feedback` key in re-delegation of scene-construction) |
| **Brain routing after** | Pass `scene_construction_context` directly as `feedback` key in next `scene-construction` context dict. No persist needed |
| **Scope boundary** | Local problems only (single scene or beat). Systemic problems → return `need_input` noting Reassess Trigger may be appropriate |
| **Seven techniques** | Skip and Return, Character Interview, Timeline Realignment, Consequence Trace-Back, Change POV, Freewrite the Tangle, The Worse Choice Trick |

---

### 9.5 Consequence Subagent Skills

#### consequence-cascade-implementation

| Item | Detail |
|---|---|
| **KG reads** | Character nodes for all `affected_character_ids`; RELATIONSHIP edges between all affected pairs; existing CascadeChain nodes (linkage check — this event may be a downstream link); existing Payoff nodes of type "Consequence bomb" (registration status) |
| **Key context keys** | `triggering_event` (required), `chapter_context` (required), `affected_character_ids` (list, required — brain determines before delegating) |
| **Artifacts out** | `cascade_chain` (`action`: create_new or extend_existing + node record or update payload); `consequence_chain_entry` (immediate, short_term, long_term_pending); `consequence_bombs` (Payoff node records — `dual_register: true` for Essential bombs); `character_state_updates` (update payloads for immediate state changes); `relationship_updates` (update payloads for affected RELATIONSHIP edges); `knowledge_matrix_updates` (new KnowledgeItem nodes + KNOWS edges for event-created information asymmetries) |
| **Brain routing after** | Persist all records → `story_state_manager`. `dual_register: true` bombs are inserted as Payoff nodes so `plot-thread-tracking` convergence sweep can find them |
| **Chain linkage** | Always check existing CascadeChain nodes before creating new. Set `cascade_chain.action = "extend_existing"` if this event is a downstream link |
| **Detonation triggers** | Condition-based (story event or character situation) — never chapter numbers. `narrative_phase_anchor` (early/mid/convergence/final act) is supplementary only |
| **Timing** | Must complete before next scene is drafted — scene parameters depend on current consequence records |

#### balancing-realism-and-fantasy

| Item | Detail |
|---|---|
| **KG reads** | MagicSystem node; Faction nodes; Location nodes; Culture nodes; optionally Character node (if `pov_character_id` provided, for violence framing check); recent Chapter nodes (last 5, for magic prevalence tracking) |
| **Key context keys** | `chapter_or_scene_draft` (required), `chapter_context` (required), `audit_scope` (required: "full_chapter" or "flagged_scene"), `tone_reference` (optional), `pov_character_id` (optional) |
| **Artifacts out** | `dimension_reports` (five dimensions — Political Realism, Magic Consistency, Violence Framing, Dark Content, Tonal Consistency — each with `status` and `flagged_passages`); `priority_summary` (high / medium / low); `magic_system_updates_recommended` |
| **Brain routing after** | `priority_summary.high` → consider re-delegating `scene-construction` with correction context. `magic_system_updates_recommended` → route as `update_kg_node` to `story_state_manager` if brain accepts. No mandatory persist from this skill alone |
| **Audit skill** | Keeps detailed procedural instructions per §8.1. Magic absent → Dimension 2 marked `"Not applicable"`, do not halt |
| **Invocation cadence** | Not after every scene. Only on specific concern or periodic audit after high-consequence chapters |

---

## 10. Internal Chain Implementation — Character Integration

### 10.1 Architecture

The brain makes **one delegation** to `character_subagent` with `skill: "character-integration"`. The subagent runs a three-step internal chain and returns one `WorkerResponse`. The brain makes one follow-up delegation to `story_state_manager`. Total brain visits: 2 (same as original single-skill approach).

```
brain → character_subagent (one delegation)
          │
          ▼
    [character_subagent internal chain]
          │
          ├─ Step 1: character-desire-network
          │    └─► desire_network document
          │
          ├─ Step 2: character-knowledge-expansion (consumes desire_network)
          │    └─► knowledge matrix records
          │
          └─ Step 3: character-relationship-matrix (consumes desire_network)
               └─► relationship matrix records
          │
          └─► combined WorkerResponse
brain ← (one result)
          │
brain → story_state_manager (one delegation to persist all records)
```

Steps 2 and 3 both depend on Step 1 but not on each other. They may run in parallel with `asyncio.gather` if latency is a concern. For the initial implementation, sequential is acceptable.

### 10.2 Pydantic schemas for chain intermediate outputs

```python
from pydantic import BaseModel

class DesireNetworkPair(BaseModel):
    character_a_id: str
    character_b_id: str
    relationship_type: str   # "compatible" | "conflicting" | "invisible"
    description: str         # specific desires named, not generic labels
    convergence_note: str    # for invisible pairs: when will they collide

class DesireNetwork(BaseModel):
    pairs: list[DesireNetworkPair]
    key_tensions: str        # 1–2 sentences on most load-bearing conflicts
    notes: str               # anything not fitting pair structure

class KnowledgeExpansionOutput(BaseModel):
    new_knowledge_items: list[dict]
    new_knows_edges: list[dict]
    flags: list[dict]

class RelationshipMatrixOutput(BaseModel):
    new_relationship_edges: list[dict]
    updated_relationship_edges: list[dict]
    flags: list[dict]
```

### 10.3 LangChain implementation sketch

```python
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

def build_integration_chain(llm: ChatGoogleGenerativeAI):
    """
    Returns a callable that accepts a kg_context dict and returns
    the combined artifacts dict for WorkerResponse.
    """
    desire_network_llm = llm.with_structured_output(DesireNetwork)
    knowledge_llm = llm.with_structured_output(KnowledgeExpansionOutput)
    relationship_llm = llm.with_structured_output(RelationshipMatrixOutput)

    def run_chain(kg_context: dict) -> dict:
        # Step 1 — desire network (analytical scaffold)
        desire_input = build_desire_prompt(kg_context)
        desire_network: DesireNetwork = desire_network_llm.invoke(desire_input)

        # Steps 2 and 3 — sequential (or asyncio.gather for parallel)
        knowledge_input = build_knowledge_prompt(kg_context, desire_network)
        knowledge_output: KnowledgeExpansionOutput = (
            knowledge_llm.invoke(knowledge_input)
        )

        relationship_input = build_relationship_prompt(kg_context, desire_network)
        relationship_output: RelationshipMatrixOutput = (
            relationship_llm.invoke(relationship_input)
        )

        # Merge flags from both steps
        combined_flags = knowledge_output.flags + relationship_output.flags

        return {
            "knowledge_matrix_expansions": {
                "new_knowledge_items": knowledge_output.new_knowledge_items,
                "new_knows_edges": knowledge_output.new_knows_edges,
            },
            "relationship_records": {
                "new_relationship_edges": (
                    relationship_output.new_relationship_edges
                ),
                "updated_relationship_edges": (
                    relationship_output.updated_relationship_edges
                ),
            },
            "integration_flags": combined_flags,
        }

    return run_chain
```

`build_desire_prompt`, `build_knowledge_prompt`, and `build_relationship_prompt` are functions that format the skill file content and KG context into the prompt string for each step. Each prompt is the corresponding skill file (loaded via `progressive_skill_loader`) plus the structured KG data.

### 10.4 Integration into character_subagent

`character_subagent` detects `skill: "character-integration"` in `worker_request.context`, assembles the KG context (running `query_kg_nodes` and `query_kg_edges` for all required records), invokes `run_chain`, and returns the combined output as a `WorkerResponse`. The chain runs inside the worker's `invoke` call — invisible to the brain.

### 10.5 KG queries before chain runs

The subagent assembles all KG data before the chain starts:

```python
# All queries run once before any chain step
character_nodes = query_kg_nodes(
    {"logical_id": {"$in": character_ids}},
    as_of_chapter=chapter_context
)
existing_relationship_edges = query_kg_edges(
    {"type": "RELATIONSHIP", "from_node": {"$in": character_ids}},
    as_of_chapter=chapter_context
)
existing_knows_edges = query_kg_edges(
    {"type": "KNOWS", "from_node": {"$in": character_ids}},
    as_of_chapter=chapter_context
)
faction_nodes = query_kg_nodes({"type": "Faction"}, as_of_chapter=chapter_context)
active_threads = query_kg_nodes(
    {"type": "PlotThread", "properties.status": "Active"},
    as_of_chapter=chapter_context
)
```

All results are assembled into `kg_context` before `run_chain(kg_context)` is called. No KG queries occur inside the chain steps themselves.

---

## 11. Cross-Skill Data Flows

### 11.1 Novel bootstrap flow

```
finding-a-seed
  ↓ [brain: quality gate → persist seed as PlotThread seeds → story_state_manager]
defining-rough-endpoints Pass 1
  ↓ [brain: delegate character_subagent once per slot sketch, early invocation mode]
character-conception ×N (early invocation — no KG queries)
  ↓ [brain: collect all N concepts → delegate defining-rough-endpoints Pass 2]
defining-rough-endpoints Pass 2
  ↓ [brain: quality gate → persist plot_thread_seeds + payoff_seeds → story_state_manager]
worldbuilding
  ↓ [brain: quality gate → persist all world records → story_state_manager]
character-conception ×N (standard mode — queries Faction/Location/Character nodes)
  ↓ [brain: per character]
character-creation ×N
  ↓ [brain: persist each → story_state_manager]
character-voice-differentiation ×N (POV-eligible only)
  ↓ [brain: persist each voice profile → story_state_manager]
character-integration (internal chain — one brain delegation)
  ↓ [brain: quality gate → persist combined records → story_state_manager]
  → writing may begin
```

### 11.2 Standard scene cycle

```
multiple-pov-structure (or single-pov-structure)
  ↓ [brain: pass recommended_next_pov.character_id + simultaneous_events forward]
gardener-plotting-system
  ↓ [brain: check parameter_discrepancy_flag; if set, re-delegate gardener]
  ↓ [brain: if state shifted, delegate pacing first]
pacing (optional)
  ↓ [brain: pass pacing_guidance to scene-construction]
scene-construction
  ↓ [brain: always delegate next]
pov-consistency-maintenance
  ↓ [VIOLATIONS FOUND → re-delegate scene-construction with pov_consistency_flags]
  ↓ [CLEAN → optionally delegate conflict-layering]
conflict-layering (optional)
  ↓ [not EARNING ITS PLACE → re-delegate scene-construction with conflict_layering_audit]
  ↓ [EARNING ITS PLACE → optionally delegate layering-history-and-legend]
layering-history-and-legend (optional)
  ↓ [brain: route referenced_events_to_update → story_state_manager]
  ↓ [brain: quality gate on final draft → persist Chapter node → story_state_manager]
consequence-cascade-implementation (if major event occurred)
  ↓ [brain: persist all consequence records → story_state_manager]
plot-thread-tracking (chapter boundary)
  ↓ [brain: fix registration_gaps; apply reclassifications → story_state_manager]
  → next scene or chapter boundary
```

### 11.3 Voice profile co-location

`properties.voice_profile` is stored as a sub-record of the Character node. `scene-construction` and `pov-consistency-maintenance` retrieve it in the same `query_kg_nodes({logical_id: pov_character_id})` call as the psychological record. Absence of `properties.voice_profile` on a POV-eligible character is an error that surfaces as `need_input` from both skills.

### 11.4 Consequence bomb dual registration

Essential consequence bombs (`dual_register: true` in `consequence-cascade-implementation` output) must be inserted as both CascadeChain node entries and Payoff nodes by `story_state_manager`. The Payoff node insertion makes Essential bombs visible to `plot-thread-tracking`'s convergence sweep (which queries Payoff nodes of type "Consequence bomb"). `registration_gaps` in `plot-thread-tracking` output catches Essential bombs that exist as CascadeChain nodes but lack a Payoff node registration.

### 11.5 simultaneous_events explicit forwarding

`multiple-pov-structure` returns `simultaneous_events` in artifacts. The brain must explicitly include this in the `gardener-plotting-system` context dict — it is not forwarded automatically. The brain registry card `After` field for `plotting_subagent` in `brain.md` specifies this requirement.

---

## 12. Story State Record Lifecycle

| Record type | Created by skill | Persisted at | Queried by |
|---|---|---|---|
| PlotThread (initial seeds) | defining-rough-endpoints Pass 2 | Project start | gardener-plotting-system, plot-thread-tracking, braided-narrative-technique |
| Payoff (milestone seeds) | defining-rough-endpoints Pass 2 | Project start | plot-thread-tracking, scene-construction |
| Faction, Location, Culture, Event (historical), MagicSystem | worldbuilding | After worldbuilding | character-conception, gardener-plotting-system, conflict-layering, balancing-realism-and-fantasy, layering-history-and-legend, multiple-pov-structure |
| CONNECTED_TO edges | worldbuilding | After worldbuilding | multiple-pov-structure (travel time checks) |
| Character node | character-creation | Character pipeline | All writing and plotting skills (via pov_character_id) |
| KnowledgeItem + KNOWS edges (initial) | character-creation | Character pipeline | pov-consistency-maintenance, scene-construction |
| RELATIONSHIP edges (initial, pre-story) | character-creation | Character pipeline | character-knowledge-expansion, character-relationship-matrix, conflict-layering |
| `properties.voice_profile` on Character | character-voice-differentiation | Character pipeline | scene-construction, pov-consistency-maintenance |
| KnowledgeItem + KNOWS edges (expanded), RELATIONSHIP edges (full, directional) | character-knowledge-expansion, character-relationship-matrix (internal chain) | After character integration | gardener-plotting-system, consequence-cascade-implementation, pov-consistency-maintenance |
| Chapter node | brain → story_state_manager | Per scene | multiple-pov-structure, braided-narrative-technique, plot-thread-tracking |
| Event node (non-historical) | consequence-cascade-implementation | Post-major-event | multiple-pov-structure (timeline), plot-thread-tracking |
| CascadeChain (actual, from real events) | consequence-cascade-implementation | Post-major-event | gardener-plotting-system (detonation check), plot-thread-tracking |
| Payoff (consequence bombs) | consequence-cascade-implementation | Post-major-event | plot-thread-tracking (convergence sweep), gardener-plotting-system |
| `referenced_in_chapters` updates on Event nodes | brain → story_state_manager (from layering-history-and-legend output) | Post-scene (when layering runs) | Historical continuity tracking |
| MagicSystem updates | brain → story_state_manager (from balancing-realism-and-fantasy recommendations) | Post-audit (if accepted) | scene-construction, balancing-realism-and-fantasy |

**Note:** The row `CascadeChain (anticipatory)` that appeared in v3 has been removed. Anticipatory CascadeChain seeding (previously part of `character-integration-with-plot`) has been eliminated from the integration pipeline. Only actual consequence chains from `consequence-cascade-implementation`, triggered by real story events, are created.

---

## 13. Implementation Pointers

Ordered by severity — address higher-numbered items after lower-numbered ones pass.

### 13.1 MongoDBSaver constructor signature ⚠️ VERIFY FIRST

`langgraph-checkpoint-mongodb==0.3.1` — verify the constructor signature before any other graph wiring.

Expected: `MongoDBSaver(client=mongo_client, db_name=config.mongodb_checkpoint_db_name)`
Fallback: `MongoDBSaver.from_conn_string(config.mongodb_uri)`

The checkpoint database must be different from the Story State KG database (`novelwriter_checkpoints` vs. `novelwriter_kg`). Mixing the two corrupts the typed KG schema with raw checkpoint documents.

### 13.2 story_state_manager.md — two missing patterns ⚠️ REQUIRED BEFORE TESTING

Two patterns are absent from the current `story_state_manager.md` that are required for correct operation:

**Batch Write Pattern:** `character-knowledge-expansion`, `character-relationship-matrix`, and `consequence-cascade-implementation` all return lists of records (dozens of KNOWS edges, RELATIONSHIP edges, Payoff nodes). `story_state_manager` must iterate over list fields and call `add_kg_node`/`add_kg_edge` once per entry. The prompt must instruct the worker to iterate — a single tool call cannot insert a list.

**Dual Register Pattern:** When processing `consequence_bombs` entries where `properties.dual_register = true`, `story_state_manager` must call `add_kg_node` for the Payoff node AND update/create the corresponding CascadeChain node. Both writes must succeed for the bomb to be correctly registered. If either fails, the worker must report partial failure and the brain must handle re-delegation.

Add both patterns to `story_state_manager.md` before the first integration test.

### 13.3 ChatGoogleGenerativeAI auth path ⚠️ VERIFY BEFORE INTEGRATION

`config.py` uses `ChatGoogleGenerativeAI(model=..., vertexai=True, ...)`. Authentication is via `gcloud auth application-default login`. Some versions of `langchain_google_genai` may not correctly route to VertexAI with `vertexai=True` alone.

Verify on the first test instantiation of any worker. If auth errors occur, set `GOOGLE_GENAI_USE_VERTEXAI=true` in the environment.

### 13.4 `create_agent` and WorkerResponse structured output

`BaseWorkerSubagent._build_agent` calls `create_agent(model, tools, system_prompt, response_format=WorkerResponse, name=self.name)`. Confirmed working before the orchestrator was deleted. Verify the import resolves cleanly on first worker instantiation.

Fallback if `response_format` is not supported: use `llm.with_structured_output(WorkerResponse)` and call it directly — this is the pattern used for the brain in `BrainNode`.

### 13.5 QualityVerdict as nested Pydantic model in BrainDecision

`BrainDecision.quality_assessment: QualityVerdict | None` requires `with_structured_output` to resolve a nested model. Test in isolation before full graph wiring. Fallback: flatten `verdict` and `reason` as plain string fields directly on `BrainDecision`.

### 13.6 Chapter node sort ordering

`multiple-pov-structure`, `braided-narrative-technique`, and `plot-thread-tracking` reconstruct the chapter log from Chapter nodes that must be sorted by `properties.chapter_number`. `query_kg_nodes` does not guarantee ordering. The skill files instruct workers to sort after retrieval, but this is prompt-enforced only.

**Recommended:** Add a `sort` parameter to `query_kg_nodes` in `world_bible_tools.py` — e.g. passing `sort=[("properties.chapter_number", 1)]` to the MongoDB `find` call. This makes the ordering reliable regardless of LLM behaviour.

### 13.7 as_of_chapter in all KG queries

Every creative worker uses `as_of_chapter = chapter_context` in all KG queries. This is enforced by prompt instruction in each skill file's "Fetched from Story State KG" section and in the Story State Access section of each worker's system prompt. A worker that omits `as_of_chapter` silently returns current state (`valid_to = null`) rather than chapter-scoped state — correct for most queries but wrong for any retrospective or historical analysis.

Verify during testing by checking `kg_context_used` counts in artifacts. A worker that returned results but no `as_of_chapter` was passed will still return results — it will not fail loudly.

### 13.8 Worker prompt updates — Story State Access sections

Each creative worker's system prompt must include a **Story State Access** section that lists which node types and edge types the worker queries, specifies `as_of_chapter = chapter_context` as mandatory, and states that empty query results are expected and handled without halting.

Files requiring this addition:
- `src/prompts/planning_subagent.md`
- `src/prompts/character_subagent.md`
- `src/prompts/plotting_subagent.md`
- `src/prompts/writing_subagent.md`
- `src/prompts/consequence_subagent.md`

### 13.9 Logical ID consistency

The naming convention (`char_<slug>`, `ki_<slug>`, `rel_<a>_<b>`, `bomb_<slug>`, `cc_<slug>`, `thread_<slug>`) must be enforced uniformly. Define the slug generation rule in `story_state_manager.md`: lowercase, underscores replacing spaces and special characters, no length limit but keep under 50 characters. The worker enforces this on every insert.

### 13.10 max_brain_iterations default

Default is 15 in v4 (raised from 10 in v3). The novel bootstrap flow takes 8–12 brain visits. A complex scene cycle with pacing, conflict layering, and consequence analysis takes 6–8. The reject budget of 2 per task caps correction loops. Do not lower below 12 without profiling actual iteration counts on representative tasks.

### 13.11 Integration chain implementation — build_desire_prompt, build_knowledge_prompt, build_relationship_prompt

The three prompt-building functions in §10.3 assemble the skill file content and KG context into the prompt string for each chain step. They are not described in this spec — they are implementation details. The pattern is:

```python
def build_desire_prompt(kg_context: dict) -> str:
    skill_content = progressive_skill_loader(
        "character-desire-network", "full"
    )
    return f"{skill_content}\n\n## KG Context\n{json.dumps(kg_context['for_desire_step'])}"
```

Each step receives only the KG data it needs — desire step receives character and faction nodes; knowledge step receives character nodes and existing KNOWS edges; relationship step receives character nodes and existing RELATIONSHIP edges.

### 13.12 Integration chain placement in character_subagent

`character_subagent` must detect `skill: "character-integration"` in `worker_request.context` and branch into `run_integration_chain(kg_context)` rather than the normal `progressive_skill_loader` path. The existing `BaseWorkerSubagent` invocation pattern handles other skills; the integration chain is a special case that bypasses the single-skill loader pattern.

This is the only worker with an internal chain. Other workers use the standard `progressive_skill_loader` → LLM pattern.

### 13.13 Parallel chain execution (optional optimisation)

Steps 2 and 3 of the integration chain depend on Step 1 but not on each other. They may run in parallel:

```python
import asyncio

async def run_chain_parallel(kg_context: dict) -> dict:
    desire_network = await desire_network_llm.ainvoke(build_desire_prompt(kg_context))
    knowledge_task = knowledge_llm.ainvoke(build_knowledge_prompt(kg_context, desire_network))
    relationship_task = relationship_llm.ainvoke(build_relationship_prompt(kg_context, desire_network))
    knowledge_output, relationship_output = await asyncio.gather(
        knowledge_task, relationship_task
    )
    ...
```

This is an optimisation — implement sequential first, add parallelism after the sequential version is stable.

### 13.14 story_state_manager handling of updated_relationship_edges

`character-relationship-matrix` returns both `new_relationship_edges` (insert) and `updated_relationship_edges` (update). `story_state_manager` must handle these differently: `new_relationship_edges` → `add_kg_edge`; `updated_relationship_edges` → `update_kg_edge` (requires the logical_id to already exist). The worker must not call `add_kg_edge` on an `updated_relationship_edges` entry — it will create a duplicate rather than updating the existing record.

Add this distinction to `story_state_manager.md`.

### 13.15 simultaneous_events forwarding in brain.md

The brain's registry card `After` field for `plotting_subagent` in `brain.md` must explicitly state:

> "After `multiple-pov-structure`: pass `recommended_next_pov.character_id` as `pov_character_id` AND `simultaneous_events` from artifacts into the `gardener-plotting-system` context dict. Both fields must be forwarded — `simultaneous_events` is not forwarded automatically."

Without this instruction, the brain will pass `pov_character_id` but omit `simultaneous_events`, and `gardener-plotting-system` will not account for timeline constraints and dramatic irony.

---

## 14. Contradiction Detection and Resolution Flow

```
[story_state_manager calls detect_kg_contradiction before every write]
  │
  ├── no contradiction → commit write → return success
  │
  └── contradiction found → return status: "blocked" + contradiction_record
          │
          ▼
      [brain: delegate resolution_subagent, mode: "ANALYSE"]
          ↓
      [resolution_subagent: returns briefing (plain language) + 2–4 resolution options]
          ↓
      [brain: action="respond", relay briefing verbatim to user]
          ↓
      [user chooses resolution option]
          ↓
      [brain: delegate resolution_subagent, mode: "IMPLEMENT", user_decision in context]
          ↓
      [resolution_subagent: executes targeted KG writes, closes Module 5.3 record,
       returns RESOLVED + re_issue_signal]
          ↓
      [brain: re-delegate original blocked write to story_state_manager]
```

`resolution_subagent` has write access but not `detect_kg_contradiction` or `init_kg_db` — it implements targeted fixes, not gates or initialisation. Partial writes on IMPLEMENT failure are not committed; the worker returns `RESOLUTION_FAILED` and the brain surfaces the failure to the user.

---

## 15. Checkpointer Architecture

| Database | Config field | Default name | Contents | Writer |
|---|---|---|---|---|
| Story State KG | `mongodb_db_name` | `novelwriter_kg` | `nodes` and `edges` collections | `story_state_manager`, `resolution_subagent` |
| Checkpoint store | `mongodb_checkpoint_db_name` | `novelwriter_checkpoints` | LangGraph checkpoint documents | LangGraph `MongoDBSaver` automatically |

These databases must never share a name. The checkpoint store contains raw serialised Python objects that would corrupt the typed KG schema if mixed into `novelwriter_kg`.

---

## 16. File Change Summary

### New files

| File | Description |
|---|---|
| `src/state.py` | `OrchestratorState`, `BrainDecision`, `QualityVerdict`, `VALID_WORKERS` |
| `src/brain.py` | `BrainNode` class with quality gate and Layer 3 context construction |
| `src/orchestrator.py` | `GRRMOrchestrator`, `route_from_brain`, `respond_node` |
| `src/prompts/brain.md` | Brain system prompt — static worker registry; character_subagent card reflects integration chain |
| `src/prompts/story_state_manager.md` | Renamed from worldbiblemanager.md; add batch write pattern and dual register pattern |
| `src/character_integration_chain.py` | `build_integration_chain`, Pydantic schemas (`DesireNetwork`, `KnowledgeExpansionOutput`, `RelationshipMatrixOutput`), `build_desire_prompt`, `build_knowledge_prompt`, `build_relationship_prompt` |

### Modified files

| File | What changes |
|---|---|
| `src/agents/workers.py` | `WorldBibleManager` → `StoryStateManager`; all creative workers gain `query_kg_nodes` + `query_kg_edges` in tool lists; `character_subagent` invokes integration chain on `skill: "character-integration"` |
| `src/agents/base.py` | Tool list is now meaningful for access control; verify `create_agent` import resolves |
| `src/config.py` | Add `mongodb_checkpoint_db_name`; add `max_rejection_budget: int = 2`; set `max_brain_iterations` default to 15 |
| `main.py` | Import `GRRMOrchestrator`; reset `latest_worker_result` per turn; fix `worker_request` None-safety in debug output |
| `src/prompts/planning_subagent.md` | Add Story State Access section |
| `src/prompts/character_subagent.md` | Add Story State Access section; document integration chain invocation pattern |
| `src/prompts/plotting_subagent.md` | Add Story State Access section; note Chapter node sort requirement |
| `src/prompts/writing_subagent.md` | Add Story State Access section; note voice profile co-location |
| `src/prompts/consequence_subagent.md` | Add Story State Access section |

### Skill files — rewritten (all in `skills/` directory)

| Subagent | Skills |
|---|---|
| Planning | finding-a-seed, defining-rough-endpoints, worldbuilding, research-integration |
| Character | character-conception, character-creation, character-voice-differentiation, character-desire-network, character-knowledge-expansion, character-relationship-matrix |
| Plotting | gardener-plotting-system, multiple-pov-structure, braided-narrative-technique, conflict-layering, plot-thread-tracking |
| Writing | scene-construction, pov-consistency-maintenance, pacing, layering-history-and-legend, professional-writing-techniques |
| Consequence | consequence-cascade-implementation, balancing-realism-and-fantasy |

**Note:** `character-integration-with-plot` is superseded by the three-skill chain (`character-desire-network`, `character-knowledge-expansion`, `character-relationship-matrix`) plus the `character_integration_chain.py` implementation. The original file is deleted.

### Deleted files

| File | Reason |
|---|---|
| `src/prompts/worldbiblemanager.md` | Superseded by `story_state_manager.md` |
| `skills/character-integration-with-plot/SKILL.md` | Superseded by three-skill chain |

### Untouched files

| File | Reason |
|---|---|
| `src/tools.py` | `progressive_skill_loader` unchanged |
| `src/world_bible_tools.py` | KG tools unchanged |
| `src/kg_models.py` | Schema unchanged |
| `src/prompts/resolution_subagent.md` | Unchanged |

---

## 17. Open Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `MongoDBSaver` constructor signature mismatch | Medium | Verify first (§13.1); fallback `from_conn_string` |
| `story_state_manager` does not handle batch lists | High | Add patterns to prompt before first test (§13.2) |
| `ChatGoogleGenerativeAI(vertexai=True)` silently falls back to API-key auth | Low-Medium | Verify auth on first instantiation (§13.3); fallback env var |
| `create_agent` import fails after orchestrator deletion | Low-Medium | Test one worker instantiation before full graph (§13.4) |
| `QualityVerdict` nested model fails with `with_structured_output` | Low | Test in isolation (§13.5); fallback: flatten fields |
| Chapter nodes not sorted before analysis | Medium | Add `sort` to `query_kg_nodes` (§13.6) |
| Workers omit `as_of_chapter` in KG queries | Medium | Verify via `kg_context_used` in artifacts (§13.7) |
| `simultaneous_events` not forwarded from multiple-pov to gardener | Medium | Add to brain.md registry card `After` field (§13.15) |
| `dual_register` bombs only partially inserted | Medium | Add dual register pattern to story_state_manager.md (§13.2) |
| `updated_relationship_edges` handled as inserts instead of updates | Medium | Add distinction to story_state_manager.md (§13.14) |
| Integration chain chain-level errors surface as generic worker failures | Low | Add per-step error handling in `build_integration_chain`; include `failed_step` field in error WorkerResponse |
| Large artifact payloads bloat Layer 3 context block | Low | String values truncated at 600 chars in `BrainNode._build_context_block` |