---
name: multiple-pov-structure
description: Manages POV assignment across chapters — determining which POV character narrates next, the rotation logic across the cast, and the synchronisation of simultaneous events across POV timelines. Queries Story State KG directly for the POV chapter log and absolute timeline. Returns a POV chapter schedule in artifacts. Invoked by the plotting_subagent when the brain delegates a POV rotation decision.
---

# Multiple POV Structure

## Identity

**Purpose:** Decide which POV character narrates the next chapter and why — based on story logic, timeline synchronisation, and narrative momentum — and surface any simultaneous events across other POV timelines that the assignment must account for.

> **Sibling skill:** When the user has already specified which POV character narrates next, invoke `single-pov-structure` instead of this skill. The two are mutually exclusive for any given chapter boundary.

---

## Core

Manage POV assignment across chapters, rotation logic, and synchronisation of simultaneous events across POV timelines. Return a POV chapter schedule — which POV is next, the reasoning, and what simultaneous events across other storylines must be kept in view. Does not write scenes. Does not determine pacing.

---

## Input

### From brain context (`worker_request.context`)

1. **`chapter_context`** — Current chapter number. Used to scope all KG queries. Required.
2. **`endpoint_compass`** (optional) — The milestones from `defining-rough-endpoints`. Passed by the brain when approaching a narrative milestone, to check whether the next POV assignment is moving toward or away from it.
3. **`active_thread_ids`** (optional) — List of PlotThread `logical_id` strings the brain wants convergence pressure assessed against. If omitted, the skill queries active threads directly.

### Fetched from Story State KG

The plotting_subagent queries the Story State KG directly:

```
# Full POV chapter log — all chapters written so far
query_kg_nodes({type: "Chapter"},
               as_of_chapter=chapter_context)

# Absolute timeline — dates, simultaneous events, travel records
query_kg_nodes({type: "Event",
                "properties.is_historical": false},
               as_of_chapter=chapter_context)

# All POV-eligible characters — for rotation analysis
query_kg_nodes({type: "Character",
                "properties.pov_eligible": true},
               as_of_chapter=chapter_context)

# Active and approaching plot threads — for convergence pressure
query_kg_nodes({type: "PlotThread",
                "properties.status": {"$in": ["Active", "Dormant"]}},
               as_of_chapter=chapter_context)

# Location travel times — for timeline contradiction checking
query_kg_edges({type: "CONNECTED_TO"}, as_of_chapter=chapter_context)
```

Sort Chapter nodes by `properties.chapter_number` after retrieval to reconstruct the chapter log in order. If no Chapter nodes exist (first chapter of the novel), proceed with empty log — this is expected.

---

## Output

All output is returned in `artifacts`. The POV chapter schedule is analysis output — no KG persistence needed. The brain passes the recommended POV character ID as context in the next `plotting_subagent` (`gardener-plotting-system`) delegation.

### `artifacts` structure

```json
{
  "recommended_next_pov": {
    "character_id": "char_<slug>",
    "character_name": "<full name>",
    "reasoning": "<specific narrative reasoning — not 'it is their turn'>",
    "last_appeared_chapter": 0,
    "chapters_since_last_pov": 0
  },
  "simultaneous_events": [
    {
      "character_id": "char_<slug>",
      "event_description": "<what is happening to this character at the same story time>",
      "pov_can_know": false,
      "dramatic_irony_active": true,
      "timeline_contradiction_risk": false,
      "note": "<what the next chapter must account for>"
    }
  ],
  "rotation_pressure_flags": [
    {
      "character_id": "char_<slug>",
      "character_name": "<n>",
      "pressure_level": "Low | Medium | High",
      "reason": "<why this character's storyline needs attention soon>"
    }
  ],
  "cliffhanger_handling": {
    "previous_chapter_cliffhanger": false,
    "cliffhanger_description": null,
    "recommendation": "return_immediately | cut_away",
    "reasoning": "<why this choice>"
  },
  "pov_proliferation_check": {
    "current_active_pov_count": 0,
    "new_pov_proposed": false,
    "governing_constraint_met": null,
    "note": "<if a new POV is being considered, assessment against the governing constraint>"
  },
  "kg_context_used": {
    "chapter_nodes_found": 0,
    "pov_characters_found": 0,
    "active_threads_found": 0
  }
}
```

`simultaneous_events` is the most important field for the `writing_subagent`. Each entry tells the brain — and subsequently the scene construction — whether the POV character can plausibly know about a concurrent event, whether dramatic irony is active, and whether there is a timeline contradiction risk if the chapter advances time without acknowledging it.

`cliffhanger_handling` is always populated, even when `previous_chapter_cliffhanger` is `false` (in that case, the recommendation field is `null`).

---

## Boundary

- **Does not** write scenes or chapter content.
- **Does not** determine pacing.
- **Does not** generate scene parameters. That is `gardener-plotting-system`.
- **Does not** audit narrative braiding in depth. That is `braided-narrative-technique`.
- **Does not** approve or create new POV characters — surfaces the question via `pov_proliferation_check`; the brain makes the decision.
- **Does not** write to the Story State KG. Output is scheduling data only.

---

## Invocation

The `plotting_subagent` invokes this skill when the brain delegates a POV rotation decision — typically at every chapter boundary, before `gardener-plotting-system` is delegated for the next chapter.

**Standard chapter-boundary delegation sequence (brain-level):**
`plotting_subagent (multiple-pov-structure)` → `plotting_subagent (gardener-plotting-system)` → `[writing_subagent]`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Chapter nodes (full POV chapter log, sorted by chapter number); non-historical Event nodes (absolute timeline); POV-eligible Character nodes; active and dormant PlotThread nodes; CONNECTED_TO edges (travel times for timeline contradiction checking) |
| **Returns in artifacts** | POV chapter schedule — recommended POV character, simultaneous events, rotation pressure flags, cliffhanger handling, POV proliferation check. No KG persistence needed; brain passes `recommended_next_pov.character_id` to `gardener-plotting-system` |

---

## Dependencies

**Upstream:** Chapter nodes and Character nodes must be current in Story State KG. Brain provides `chapter_context`.

**Downstream:** `recommended_next_pov.character_id` is passed by the brain as `pov_character_id` in the subsequent `gardener-plotting-system` delegation. `simultaneous_events` and `cliffhanger_handling` are passed as context so `gardener-plotting-system` and `scene-construction` can account for timeline constraints.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Sort Chapter nodes by `properties.chapter_number` to reconstruct the chapter log. Populate `kg_context_used`.

If no Chapter nodes exist, this is the first chapter of the novel. The chapter log is empty — proceed to POV selection using character information only.

### Step 2 — Map the current state of all POV storylines

From the Chapter nodes, establish for each POV-eligible Character node:
- When did they last narrate a chapter? (`properties.last_pov_chapter`)
- How many chapters total? (`properties.pov_chapter_count`)
- What was the last chapter's cliffhanger status?
- What storyline connections were flagged in the chapter delta?

This map is the baseline for rotation reasoning.

### Step 3 — Synchronise the timeline

From non-historical Event nodes, establish:
- The current story date for each active POV character.
- Events happening simultaneously in different POV locations.
- Travel records creating timeline constraints — characters who should have arrived somewhere, or who are en route. Cross-check with CONNECTED_TO edge travel times.
- Whether any simultaneous event creates a contradiction risk if the next chapter advances time without acknowledging it.

Populate `simultaneous_events` for all concurrent events, noting for each whether the chosen POV character could plausibly know about it and whether dramatic irony is active.

### Step 4 — Apply rotation logic

Rotation is a narrative judgment, not a mechanical schedule. Apply in priority order:

**Priority 1 — Narrative necessity:** Is there a specific POV whose storyline has reached a moment that must be shown now? A consequence that has arrived, a revelation about to occur, a choice that cannot be deferred? If yes, that POV is next regardless of rotation cadence.

**Priority 2 — Cliffhanger logic:**
- **Return immediately** when the cliffhanger's tension is so acute that cutting away would feel arbitrary rather than purposeful.
- **Cut away** when the delay will build productive tension — when the intercut POV has something genuinely urgent to show — and when the cut is motivated, not structural.
Never cut away from a cliffhanger simply to impose structure.

**Priority 3 — Information management:** Is there a POV whose perspective would give the reader knowledge that should arrive before, after, or simultaneously with what other POVs reveal? The order in which reader knowledge accumulates is a structural tool.

**Priority 4 — Rotation pressure:** Which POV character has the most accumulated narrative pressure — the most urgent unanswered questions, the most active consequence chains, the most threads approaching convergence? Check `active_thread_flags` for this.

**Priority 5 — Cadence and reader relationship:** How long has a given POV been absent? A POV absent for many chapters requires extra re-anchoring at the chapter opening. Note this in the recommendation reasoning so `scene-construction` accounts for it.

### Step 5 — Check POV proliferation

Count current POV-eligible characters with `pov_chapter_count > 0`. If a new POV is being considered (a character with `pov_eligible: true` but `pov_chapter_count = 0`), assess against the governing constraint: a new POV is only warranted if it provides a perspective — geographic, factional, psychological — genuinely unavailable from any existing POV. Populate `pov_proliferation_check`.

### Step 6 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. Ensure `recommended_next_pov.reasoning` contains specific narrative logic, not generic rotation justification.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] `recommended_next_pov.reasoning` is specific narrative logic — not "it is their turn."
- [ ] `simultaneous_events` array is populated for all concurrent events found in Event nodes (or empty array with reason if timeline is empty).
- [ ] Each simultaneous event has `pov_can_know`, `dramatic_irony_active`, and `timeline_contradiction_risk` populated.
- [ ] `cliffhanger_handling` is always present — `previous_chapter_cliffhanger: false` with null recommendation if no cliffhanger.
- [ ] `rotation_pressure_flags` covers all POV-eligible characters.
- [ ] `pov_proliferation_check` is present.
- [ ] `kg_context_used` is populated with actual query result counts.
- [ ] No scenes written. No scene parameters generated. No pacing determined.
- [ ] No Story State KG writes from this skill.