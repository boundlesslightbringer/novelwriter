---
name: gardener-plotting-system
description: Drives scene-by-scene discovery by identifying the POV character's goal, the obstacle in the way, the choice they face, and the consequence that will open the next scene. Operates entirely from character logic — never from structural templates or pacing schedules. Queries the Story State KG directly for the POV character's current state, knowledge matrix, active plot threads, and consequence ledger. Returns scene parameters in artifacts. Invoked by the plotting_subagent at the start of every new scene, before writing_subagent is delegated.
---

# Gardener Plotting System

## Identity

**Purpose:** Determine what happens next in the story — not by consulting a plan, but by asking what the POV character would do next given who they are, what they know, what they want, and what just happened to them. The output is the set of parameters that `writing_subagent` needs to write the next scene.

---

## Core

Drive scene-by-scene discovery by identifying the current POV character's goal, the obstacle in the way, the choice they face, and the consequence that will open the next scene. Operates from character logic, not structural template. The scene that emerges must follow inevitably from who the character is — not from what the plot needs. Returns scene parameters in artifacts; does not write prose and does not determine pacing.

---

## Input

### From brain context (`worker_request.context`)

1. **`pov_character_id`** — The `logical_id` of the POV character for the next scene (e.g. `char_caradhen`). Required.
2. **`chapter_context`** — Current chapter number. Used to scope all KG queries. Required.
3. **`last_scene_outcome`** — A brief summary (2–5 sentences) of what happened in the previous scene: what the POV character attempted, what obstacle they encountered, what choice they made, and what the immediate result was. This is the direct causal input to the next scene's goal. Required.
4. **`pacing_guidance`** (optional) — If `pacing` skill has been invoked for this character's current psychological state, its guidance is passed here. Scene parameters should be consistent with any pacing register already determined.
5. **`include_foreshadowing_check`** (optional, boolean) — If `true`, the plotting_subagent also queries Pending Payoffs (Payoff nodes) and includes a foreshadowing opportunity note in artifacts.

### Fetched from Story State KG

The plotting_subagent queries the Story State KG directly to assemble all context this skill requires:

```
# POV character's current state — post-last-chapter snapshot
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# POV character's knowledge matrix
query_kg_edges({from_node: pov_character_id, type: "KNOWS"},
               as_of_chapter=chapter_context)

# Active and dormant plot threads involving this POV character
query_kg_edges({to_node: pov_character_id, type: "INVOLVES"},
               as_of_chapter=chapter_context)
# Then fetch the PlotThread nodes linked by the above edges

# Active consequence chains affecting this POV character
query_kg_edges({type: "INVOLVES", from_node: {$in: cascade_chain_ids}},
               as_of_chapter=chapter_context)
# (cascade_chain_ids derived from CascadeChain nodes involving pov_character_id)
query_kg_nodes({type: "CascadeChain"}, as_of_chapter=chapter_context)

# Pending payoffs — only if include_foreshadowing_check is true
query_kg_nodes({type: "Payoff",
                "properties.resolution_status": "Pending"},
               as_of_chapter=chapter_context)
```

If any query returns no results, proceed with empty context for that dimension and note the absence in artifacts — do not halt. An empty consequence ledger simply means no cascades are yet in play.

---

## Output

All output is returned in `artifacts`. Scene parameters are analysis output — they do not require KG persistence. The brain passes them directly as context in the subsequent `writing_subagent` delegation.

### `artifacts` structure

```json
{
  "scene_parameters": {
    "pov_character_id": "char_<slug>",
    "pov_character_name": "<full name>",
    "arc_stage": "<current arc stage from Character node>",
    "dominant_emotional_state": "<from Character node>",
    "scene_goal": "<what the POV character is trying to achieve — specific and character-grounded>",
    "obstacle": {
      "description": "<what prevents trivial achievement>",
      "components": {
        "external": "<world state or other characters' conflicting goals>",
        "interpersonal": "<another character's interference>",
        "internal": "<POV character's own psychology making this harder>"
      }
    },
    "the_choice": {
      "description": "<what decision the POV character faces>",
      "option_a": "<first option and its cost>",
      "option_b": "<second option and its cost>",
      "tests_core_contradiction": true
    },
    "projected_consequence_shape": "<the type of consequence that opens from this choice being made at all>",
    "character_logic_audit": "<2–4 sentences confirming every element follows from the POV character's psychology, knowledge, and last scene outcome>"
  },
  "active_thread_flags": [
    {
      "thread_id": "thread_<slug>",
      "thread_name": "<name>",
      "touched_how": "<advanced | complicated | at risk of being bypassed>"
    }
  ],
  "active_consequence_flags": [
    {
      "chain_id": "cc_<slug>",
      "current_position": "<which link in the chain>",
      "approaching_detonation": false,
      "note": "<how this scene relates to the chain>"
    }
  ],
  "foreshadowing_opportunity": {
    "present": false,
    "payoff_id": null,
    "payoff_description": null,
    "organic_integration_note": null
  },
  "kg_context_used": {
    "character_node_found": true,
    "knows_edges_found": 0,
    "active_threads_found": 0,
    "cascade_chains_found": 0,
    "pending_payoffs_checked": false
  },
  "parameter_discrepancy_flag": null
}
```

`character_logic_audit` is the most operationally important field. The brain's quality gate checks this first — if the audit reveals that any scene parameter is being driven by plot convenience rather than character psychology, the brain rejects the artifacts and re-delegates with feedback.

`parameter_discrepancy_flag` is populated (non-null, with a description) only when the character's full psychology — as retrieved from the Character node — reveals that a requested scene parameter is implausible. When this flag is set, the brain must resolve it before delegating to `writing_subagent`. It does not halt the skill; it flags the conflict for the brain to decide.

`foreshadowing_opportunity.present` is `false` by default and only evaluated when `include_foreshadowing_check` is `true` in context.

---

## Boundary

- **Does not** write prose. Scene parameters are structural, not narrative.
- **Does not** determine pacing. Pacing is a separate skill; if invoked, its guidance is received as input.
- **Does not** plan multiple scenes in advance. One scene at a time.
- **Does not** assign POV characters to upcoming chapters. That is `multiple-pov-structure`.
- **Does not** audit narrative braiding or thread convergence. That is `braided-narrative-technique` and `plot-thread-tracking`.
- **Does not** write to the Story State KG. Scene parameters are passed directly to `writing_subagent` via the brain's context dict.
- **Does not** override character logic. If the character would not plausibly pursue the goal, face the obstacle, or make the choice, the `parameter_discrepancy_flag` is set and the brain resolves it.

---

## Invocation

The `plotting_subagent` invokes this skill when the brain delegates scene parameter generation:

- At the start of every new scene, before `writing_subagent` is delegated.
- After the Story State KG has been updated from the previous scene's output — so Module 1.1 (Character node), Module 1.2 (KNOWS edges), and the Consequence Ledger reflect the current post-scene state.

**Standard scene-start delegation sequence (brain-level):**
`plotting_subagent (gardener-plotting-system)` → `[plotting_subagent (pacing) if state has shifted]` → `writing_subagent (scene-construction)` → `writing_subagent (pov-consistency-maintenance)`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node (POV character, `as_of_chapter`); KNOWS edges from POV character; INVOLVES edges and PlotThread nodes for POV character; CascadeChain nodes; optionally Payoff nodes with `resolution_status: "Pending"` |
| **Returns in artifacts** | Scene parameters (no KG persistence needed); `active_thread_flags` and `active_consequence_flags` (brain uses these to know which Story State records to update after `writing_subagent` completes); optional `foreshadowing_opportunity` |

---

## Dependencies

**Upstream:** Character node and knowledge matrix must be current in Story State KG. Brain provides `pov_character_id`, `chapter_context`, and `last_scene_outcome`. Optionally: pacing guidance from prior `pacing` skill invocation.

**Downstream:** Scene parameters in artifacts are passed by the brain as context in the `writing_subagent` delegation. `active_thread_flags` and `active_consequence_flags` are used by the brain after the scene is written to know which Story State records need updating via `story_state_manager`.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Review what is returned and populate `kg_context_used` counts.

Pay particular attention to:
- The Character node's `emotional_state`, `active desires`, `active fears`, `arc_stage`, and `physical_state` — these must be the post-last-chapter state, not an earlier snapshot. If the chapter_context is stale (the KG has not been updated since the last scene), the parameters will be built on outdated state. The brain is responsible for ensuring the KG is current before delegating this skill, but note any mismatch detected.
- The Character node's `response_patterns` — these govern the obstacle and choice derivation.

### Step 2 — Read the last scene outcome from context

The `last_scene_outcome` in brain context is the direct causal input to the next scene's goal. A scene goal that ignores this outcome is a structural break in the story's cause-and-consequence chain.

### Step 3 — Derive the scene goal from character logic

The scene goal is not what the plot needs to happen. It is what this specific character, in their current state, with their current knowledge, would be attempting to do next.

Ask: *Given what just happened and who this character is, what is the first thing they would do? What would they want? What would they move toward or away from?*

The scene goal must be:
- **Specific and concrete** — not "survive" or "find a way forward," but the specific action or outcome this character is pursuing.
- **Character-grounded** — derivable from `active desires`, `emotional_state`, and core psychology in the Character node.
- **Achievable in a single scene** — scene-level, not chapter-level or arc-level.

### Step 4 — Identify the obstacle

The most powerful obstacles are layered: external circumstances + interpersonal resistance + internal psychological resistance. Populate all three `components` in the obstacle object. An obstacle with only an external component is thin — the internal component, derived from the character's `core_wound`, `self_deception`, or `values_under_pressure`, is where story lives.

The best obstacle is one that could only be in *this* character's way — arising specifically from who they are and the specific situation they are in.

### Step 5 — Construct the choice

The choice must be genuine: both options carry real cost, neither is safe, and — where possible — it tests the core contradiction from the Character node. One option aligns with the character's stated values or self-image; the other aligns with how they actually behave when pressure is real.

The scene does not specify which option the character takes — that is discovered in `scene-construction`, through the act of writing. Gardener Plotting System plots the fork in the road; writing reveals which path the character walks.

Set `tests_core_contradiction: true` if at least one of the options directly implicates the character's core contradiction. If neither option does, examine whether the choice is specific enough.

### Step 6 — Project the consequence shape

The consequence is not the result of the choice — it is the consequence *shape*: the type of thing that follows from this choice being made at all, regardless of which option is selected.

Check the CascadeChain nodes: are any active consequence chains about to advance because of this scene? Are any consequence bombs approaching detonation (`remaining_links` is short)? If so, populate `active_consequence_flags.approaching_detonation = true`.

### Step 7 — Perform the character logic audit

Before assembling output, run the audit:

*Is every element of these scene parameters — the goal, the obstacle, the choice, the consequence — derivable from who this character is, what they know at this moment, and what just happened to them?*

Specifically test:
- Could a different character in the same situation have a completely different scene goal? (If yes: good — this goal is specific to this character.)
- Is the obstacle something only this character would find obstructing in this specific way? (If no: make it more specific.)
- Does the choice test something real about this character's psychology? (If no: the choice is a structural placeholder — find the real version.)

If any element fails this test, either revise it or set `parameter_discrepancy_flag` with a description of the conflict.

### Step 8 — Flag active threads and consequences

Scan INVOLVES edges and PlotThread nodes. List which threads are touched by this scene — not resolved, but advanced, complicated, or at minimum present. List active CascadeChains in play. These flags tell the brain which Story State records to update after `writing_subagent` completes.

### Step 9 — Foreshadowing check (if requested)

If `include_foreshadowing_check` is `true`, scan Payoff nodes with `resolution_status: "Pending"`. Ask: is this scene a natural moment — given where the character is, what they are doing, and who else might be present — to pay off a setup, bring a Chekhov's gun into focus, or plant a new element? If yes, populate `foreshadowing_opportunity`. Do not force it — organic integration only.

### Step 10 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. If `parameter_discrepancy_flag` is set, include it in `summary` so the brain's quality gate is immediately aware.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Scene goal is derived from the POV character's current KG state and the last scene outcome — not from structural need.
- [ ] Obstacle has an internal component derived from the character's psychological record — not only external.
- [ ] Choice carries genuine cost on both sides; `tests_core_contradiction` is honest.
- [ ] Projected consequence shape opens the next scene — it does not resolve this one.
- [ ] `character_logic_audit` is 2–4 sentences of specific reasoning, not a generic "yes this is consistent."
- [ ] `active_thread_flags` and `active_consequence_flags` are present (even if empty arrays).
- [ ] `kg_context_used` is populated with actual counts from KG queries.
- [ ] `parameter_discrepancy_flag` is `null` or describes a specific conflict.
- [ ] No prose written. No pacing determined. No future scenes planned.
- [ ] No Story State KG writes from this skill.