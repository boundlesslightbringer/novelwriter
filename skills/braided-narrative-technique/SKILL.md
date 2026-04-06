---
name: braided-narrative-technique
description: Ensures POV storylines run parallel, intersect meaningfully at convergence points, and contain no redundant scenes (same event shown from two POVs with no new information added). Operates at the chapter-sequence level. Queries Story State KG directly for the POV chapter log and plot thread registry. Returns braiding analysis in artifacts — convergence opportunities, redundancy flags, parallel tension assessment, ranked recommendations. Invoked when a storyline redundancy or convergence question arises, or as a periodic structural health check.
---

# Braided Narrative Technique

## Identity

**Purpose:** Analyse the multi-POV narrative as a braided structure — examining whether the POV storylines are running with productive parallel tension, intersecting at genuinely meaningful convergence points, and containing no redundant scenes where showing the same event from a second POV adds nothing the reader does not already have. Output is analysis and recommendations; no rewrites.

> **Sibling skills:** Works alongside `multiple-pov-structure` (determines which POV narrates next) and `plot-thread-tracking` (tracks thread convergence windows). All three can be used together for comprehensive multi-POV orchestration.

---

## Core

Ensure POV storylines run parallel, intersect meaningfully at planned and discovered convergence points, and contain no redundant scenes. Operates at chapter-sequence level. Returns braiding analysis — convergence opportunities, redundancy flags, parallel tension assessment, ranked recommendations. Does not rewrite. Does not make plot decisions.

---

## Input

### From brain context (`worker_request.context`)

1. **`chapter_context`** — Current chapter number. Used to scope all KG queries. Required.
2. **`analysis_range`** (optional) — `{"from_chapter": N, "to_chapter": M}`. If provided, focuses the analysis on this span rather than the full narrative to date. Useful when the brain wants a targeted check rather than a full structural audit.
3. **`endpoint_compass`** (optional) — Milestones from `defining-rough-endpoints`. Passed by the brain when the story is approaching a milestone and the brain wants to assess whether the braid's trajectory is moving toward it.

### Fetched from Story State KG

The plotting_subagent queries the Story State KG directly:

```
# Full POV chapter log
query_kg_nodes({type: "Chapter"},
               as_of_chapter=chapter_context)

# Plot thread registry — all active, dormant, and resolved threads
query_kg_nodes({type: "PlotThread"},
               as_of_chapter=chapter_context)

# INVOLVES edges — which characters and events are in each thread
query_kg_edges({type: "INVOLVES"},
               as_of_chapter=chapter_context)

# All POV-eligible characters — for storyline mapping
query_kg_nodes({type: "Character",
                "properties.pov_eligible": true},
               as_of_chapter=chapter_context)

# DEPENDS_ON edges between threads — for dependency-aware convergence analysis
query_kg_edges({type: "DEPENDS_ON"},
               as_of_chapter=chapter_context)
```

Sort Chapter nodes by `properties.chapter_number` after retrieval. If `analysis_range` is provided, filter Chapter nodes to the specified span before analysis.

---

## Output

All output is returned in `artifacts`. Braiding analysis is pure analysis — no KG persistence needed. The brain uses the recommendations to decide follow-up delegations.

### `artifacts` structure

```json
{
  "braid_map_summary": {
    "pov_storylines": [
      {
        "character_id": "char_<slug>",
        "character_name": "<n>",
        "chapter_count": 0,
        "chapters": [0],
        "current_narrative_position": "<where this storyline stands at the analysis point>",
        "storyline_status": "Active | Dormant | Not yet introduced"
      }
    ],
    "intersection_points": [
      {
        "chapter_numbers": [0, 0],
        "characters_involved": ["char_<a>", "char_<b>"],
        "nature": "<direct interaction | same event different POVs | information crossover>"
      }
    ],
    "current_braid_shape": "<concise description — e.g. 'two-strand with Aldric running parallel'>"
  },
  "redundancy_flags": [
    {
      "chapters": [0, 0],
      "pov_characters": ["char_<a>", "char_<b>"],
      "shared_event": "<what event is shown from both POVs>",
      "new_information_test": "PASS | FAIL",
      "new_register_test": "PASS | FAIL",
      "verdict": "Not redundant | Redundant",
      "recommendation": "<cut second rendering | replace | restructure>"
    }
  ],
  "convergence_opportunities": [
    {
      "threads_involved": ["thread_<a>", "thread_<b>"],
      "characters_involved": ["char_<slug>"],
      "type": "Planned | Discovered | Near-miss",
      "imminence": "Imminent (1–3 chapters) | Developing | Distant",
      "narrative_meaning": "<what this convergence would mean for the story>",
      "status": "On track | At risk | Missed",
      "note": "<specific action recommended if at risk>"
    }
  ],
  "parallel_tension_assessment": [
    {
      "chapters_span": [0, 0],
      "storylines_running_parallel": ["char_<a>", "char_<b>"],
      "thematic_rhyme": true,
      "dramatic_irony_active": false,
      "isolation_risk": false,
      "assessment": "<what is working or needs attention in this parallel section>"
    }
  ],
  "recommendations": {
    "immediate": ["<issues that will compound if left unaddressed>"],
    "near_term": ["<convergence opportunities that will pass soon>"],
    "monitor": ["<tendencies not yet problems but worth watching>"]
  },
  "kg_context_used": {
    "chapter_nodes_found": 0,
    "pov_characters_found": 0,
    "plot_threads_found": 0
  }
}
```

A redundancy flag's verdict is `"Not redundant"` when either `new_information_test` or `new_register_test` passes — both must fail for a redundancy verdict.

---

## Boundary

- **Does not** operate at the individual scene level — analyses chapter sequences only.
- **Does not** rewrite any scene or chapter.
- **Does not** make plot decisions — surfaces convergence opportunities; the brain decides whether to develop them.
- **Does not** determine POV assignment for upcoming chapters. That is `multiple-pov-structure`.
- **Does not** audit individual POV voice consistency. That is `pov-consistency-maintenance`.
- **Does not** write to the Story State KG. Output is analysis returned to the brain.

---

## Invocation

The `plotting_subagent` invokes this skill when the brain delegates a braiding analysis:

- When a storyline redundancy question arises — the brain suspects a scene shows something the reader already knows from another POV.
- When a convergence question arises — storylines are approaching each other and the brain wants to assess whether the intersection is structurally sound.
- Periodically as a structural health check, roughly every 5–10 chapters in a multi-POV narrative, or when the story has been written in a long linear stretch.
- When the story feels structurally slack and the brain suspects the problem is in the braiding rather than in any individual scene.

This skill is not invoked at every chapter boundary — only when there is a specific braiding concern or a periodic check is due.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Chapter nodes (full chapter log, sorted); PlotThread nodes (all statuses); INVOLVES edges (characters and events per thread); POV-eligible Character nodes; DEPENDS_ON edges (thread dependencies). All queried with `as_of_chapter` |
| **Returns in artifacts** | Full braiding analysis — braid map, redundancy flags, convergence opportunities, parallel tension assessment, ranked recommendations. No KG persistence needed |

---

## Dependencies

**Upstream:** Chapter nodes, PlotThread nodes, and INVOLVES edges must be current in Story State KG. Brain provides `chapter_context`.

**Downstream:** `recommendations.immediate` items may trigger follow-up brain delegations to `writing_subagent` (to replace a redundant scene), `multiple-pov-structure` (to adjust upcoming POV assignments), or `plotting_subagent (gardener-plotting-system)` (to develop a discovered convergence opportunity).

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Sort Chapter nodes by `properties.chapter_number`. If `analysis_range` is provided, filter to that span. Populate `kg_context_used`.

### Step 2 — Build the braid map

From the Chapter nodes and POV-eligible Character nodes, construct a structural picture of the braid. For each POV character, list their chapters in sequence. Lay them against each other chronologically. Identify:
- Parallel sections (POVs running independently)
- Intersection points (chapters where POV characters are in the same location or directly interacting)
- Gaps (periods where a POV is absent)

This map is the analytical foundation for everything that follows. Populate `braid_map_summary`. The `current_braid_shape` field should be a concise text description — even a simple notation ("Ch. 1–5: A and B parallel; Ch. 6: A intersects C; Ch. 7–10: B dormant...") is more useful than a narrative description.

### Step 3 — Audit for redundancy

For every chapter in the log, check: does this chapter render an event that has already been rendered by another POV? If yes, apply both tests:

**New information test:** Does the second POV have access to facts, actions, or knowledge that the first POV could not see? If yes and the information is narratively material — PASS. Not redundant.

**New register test:** Does the second POV experience the event through a psychological lens so different that the *meaning* of the event is transformed? If yes and the transformation is genuinely illuminating — PASS. Not redundant.

**If both tests fail:** REDUNDANT. Populate `redundancy_flags` with a recommendation.

### Step 4 — Map convergence points

From PlotThread nodes and their INVOLVES edges, extract convergence windows — where threads are expected to resolve, and which POV characters are involved. Cross-reference with the braid map. Flag:
- **Planned convergences on track:** Thread convergence windows the braid is approaching at the expected pace.
- **Planned convergences at risk:** Windows the current braid trajectory will miss.
- **Discovered convergences:** Places where organic narrative development has brought storylines into proximity not in the thread registry — Gardener moments.
- **Near-misses to assess:** Places where storylines came close but did not intersect. Was this deliberate?

### Step 5 — Assess parallel tension

For each parallel section of the braid — chapters where POV characters run independently — assess the quality of inter-storyline tension. Ask:

**Thematic rhyme:** Are parallel storylines exploring the same question from different positions? (Strong — the braid working as intended.)

**Dramatic irony:** Does the reader know something from one POV that creates dread or anticipation about what another POV character is walking into? (Strongest form of parallel tension.)

**Isolation:** Are parallel storylines running with no thematic rhyme and no dramatic irony? (Weakest configuration — flag as `isolation_risk: true`.)

### Step 6 — Rank and assemble recommendations

Organise by urgency:
- **Immediate:** Confirmed redundancies; convergences about to be missed; long isolation sections.
- **Near-term:** Discovered convergence opportunities approaching; planned convergences needing attention within a few chapters.
- **Monitor:** Structural tendencies not yet problems.

### Step 7 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Braid map is present and explicit before analysis begins.
- [ ] Every dual-POV rendering has been tested against both the new information test and the new register test; verdicts are explicit in each flag.
- [ ] Convergence opportunities distinguish planned, discovered, and near-miss types.
- [ ] Parallel tension assessment covers every significant parallel section found.
- [ ] Recommendations are ranked into immediate / near-term / monitor.
- [ ] `isolation_risk: true` is set for genuinely isolated parallel sections, not used as a default.
- [ ] No rewrites produced. No plot decisions made. No POV assignments specified.
- [ ] No Story State KG writes from this skill.