---
name: plot-thread-tracking
description: Maintains and reports on the registry of active, dormant, and resolved plot threads. Flags threads approaching overdue payoff windows. Identifies convergence opportunities. In convergence mode, performs a dedicated sweep of all Armed consequence bombs against their detonation triggers. Queries Story State KG directly for PlotThread nodes, Payoff nodes, and (in convergence mode) CascadeChain nodes. Returns a thread status report in artifacts. Invoked at chapter boundaries, at convergence checkpoints, and when the brain needs a structural health check.
---

# Plot Thread Tracking

## Identity

**Purpose:** Give the brain a clear picture of the story's full thread load at any point — what is active, what is dormant, what is approaching resolution, what is overdue, and what threads are moving toward each other in ways that could be developed or must be managed. No thread is dropped; all setups have payoffs; this skill is the mechanism that ensures both.

---

## Core

Query and report on the registry of active, dormant, and resolved threads. Flag threads approaching overdue payoff windows. Identify convergence opportunities. In convergence mode, perform the bomb sweep. Return a thread status report. Does not resolve threads. Does not write scenes.

---

## Input

### From brain context (`worker_request.context`)

1. **`chapter_context`** — Current chapter number. Used to scope all KG queries and assess which threads are within, approaching, or past their convergence windows. Required.
2. **`convergence_mode`** (boolean, default `false`) — If `true`, the plotting_subagent also queries CascadeChain nodes to perform the convergence-phase bomb sweep (Section 4a of the original skill). The brain sets this when invoking the Convergence Checkpoint.
3. **`endpoint_compass`** (optional) — Milestones from `defining-rough-endpoints`. Passed by the brain when approaching a milestone, to assess whether threads required by that milestone are sufficiently developed.
4. **`window_lookahead`** (optional, integer, default `5`) — Number of chapters ahead to consider when flagging threads as "approaching window." Adjustable for longer or shorter look-ahead horizons.

### Fetched from Story State KG

The plotting_subagent queries the Story State KG directly:

```
# Complete plot thread registry — all statuses
query_kg_nodes({type: "PlotThread"},
               as_of_chapter=chapter_context)

# Pending payoffs and foreshadowing — all unresolved setups
query_kg_nodes({type: "Payoff",
                "properties.resolution_status": {"$in": ["Pending", "Overdue"]}},
               as_of_chapter=chapter_context)

# DEPENDS_ON edges — thread dependencies
query_kg_edges({type: "DEPENDS_ON"},
               as_of_chapter=chapter_context)

# INVOLVES edges — characters and events per thread
query_kg_edges({type: "INVOLVES"},
               as_of_chapter=chapter_context)

# PAYS_OFF_IN edges — payoffs that have been resolved
query_kg_edges({type: "PAYS_OFF_IN"},
               as_of_chapter=chapter_context)

# Convergence mode only:
query_kg_nodes({type: "CascadeChain"},
               as_of_chapter=chapter_context)
# Also fetch armed Payoff nodes of type "Consequence bomb":
query_kg_nodes({type: "Payoff",
                "properties.type": "Consequence bomb",
                "properties.resolution_status": "Pending"},
               as_of_chapter=chapter_context)
```

---

## Output

All output is returned in `artifacts`. Thread status report is pure analysis — no KG persistence needed. However, the brain may use the report to update thread status fields (e.g. reclassifying Unclassified consequence bombs) via `story_state_manager` if the report recommends it.

### `artifacts` structure

```json
{
  "thread_load_summary": {
    "total": 0,
    "active": 0,
    "dormant": 0,
    "resolved": 0,
    "abandoned": 0,
    "overdue": 0,
    "approaching_window": 0
  },
  "active_thread_status": [
    {
      "thread_id": "thread_<slug>",
      "thread_name": "<n>",
      "characters_involved": ["char_<slug>"],
      "current_status_within_thread": "<where this thread currently sits narratively>",
      "expected_convergence_window": "<rough chapter range or condition>",
      "track_status": "On track | At risk | Overdue",
      "dependencies": ["thread_<slug>"],
      "note": "<anything specific the brain should know>"
    }
  ],
  "overdue_flags": [
    {
      "id": "thread_<slug> | payoff_<slug>",
      "name": "<n>",
      "type": "PlotThread | Payoff",
      "expected_window": "<when it was supposed to resolve>",
      "chapters_past_window": 0,
      "narrative_consequence": "<what structural debt accumulates from this being unresolved>",
      "recommended_action": "Resolve in next available chapter | Revise window estimate | Mark as intentional open-ending"
    }
  ],
  "pending_payoffs_status": [
    {
      "payoff_id": "payoff_<slug>",
      "description": "<setup element>",
      "type": "Chekhov's gun | Foreshadowing | Consequence bomb | Prophecy | In-world legend",
      "planted_chapter": 0,
      "expected_window_or_trigger": "<chapter range or condition-based trigger>",
      "resolution_status": "Pending | Overdue",
      "priority_tier": "Essential | Enriching | Unclassified | N/A",
      "note": "<any integration concern — e.g. Chekhov's gun needs re-activation>"
    }
  ],
  "convergence_bomb_sweep": {
    "performed": false,
    "essential_bombs": [
      {
        "chain_id": "cc_<slug>",
        "description": "<nature of the consequence>",
        "detonation_trigger": "<story condition that fires this>",
        "narrative_phase_anchor": "early | mid | convergence | final act",
        "module_2_4_registered": true,
        "detonation_path_assessment": "On track — path visible | AT RISK — no visible path",
        "note": "<specific action if AT RISK>"
      }
    ],
    "enriching_bombs": [
      {
        "chain_id": "cc_<slug>",
        "description": "<n>",
        "detonation_trigger": "<condition>",
        "opportunity_status": "Opportunity available | No current opportunity — monitor"
      }
    ],
    "unclassified_bombs": [
      {
        "chain_id": "cc_<slug>",
        "description": "<n>",
        "reclassification_recommendation": "Essential | Enriching | Retain as Unclassified",
        "reasoning": "<why this recommendation>"
      }
    ],
    "registration_gaps": [
      {
        "chain_id": "cc_<slug>",
        "issue": "Essential bomb not registered in Payoff nodes (Module 2.4)"
      }
    ]
  },
  "convergence_opportunities": [
    {
      "threads_involved": ["thread_<slug>"],
      "narrative_meaning": "<what happens when these threads intersect>",
      "type": "Planned | Discovered",
      "imminence": "Imminent (1–3 chapters) | Developing | Distant",
      "note": "<action recommended>"
    }
  ],
  "thread_health_assessment": {
    "verdict": "Healthy | Overloaded | Underloaded | Dependency cascade risk",
    "detail": "<specific concern if not Healthy>"
  },
  "no_thread_abandonment_check": {
    "pass": true,
    "abandoned_without_rationale": ["thread_<slug>"]
  },
  "priority_summary": {
    "high": ["<items requiring immediate brain action>"],
    "medium": ["<items requiring attention soon>"],
    "low": ["<items to monitor>"]
  },
  "kg_context_used": {
    "plot_thread_nodes_found": 0,
    "payoff_nodes_found": 0,
    "cascade_chain_nodes_found": 0
  }
}
```

`convergence_bomb_sweep` is always present in artifacts but `performed: false` when `convergence_mode` is not set. `registration_gaps` lists Essential consequence bombs that are present in CascadeChain nodes but not registered as Payoff nodes — the brain routes a `story_state_manager` write to fix these gaps if found.

`no_thread_abandonment_check.abandoned_without_rationale` lists thread IDs where status is `Abandoned` but no `abandonment_rationale` property is set in the PlotThread node — these are structural gaps requiring attention.

---

## Boundary

- **Does not** resolve threads — reports on their status.
- **Does not** write scenes or scene parameters.
- **Does not** audit braiding or POV structure at the sequence level. That is `braided-narrative-technique`.
- **Does not** decide which threads to develop or how — reports status and flags urgency; the brain decides.
- **Does not** write to the Story State KG directly. The brain may route follow-up writes to `story_state_manager` based on the report (e.g. to reclassify consequence bomb priority tiers, fix registration gaps, or update abandoned thread rationales).
- **Does not** reclassify consequence bomb priority tiers directly — recommends reclassification; the brain applies the update via `story_state_manager`.

---

## Invocation

The `plotting_subagent` invokes this skill when the brain delegates a thread tracking check:

- At chapter boundaries, as part of the standard chapter-completion sequence, to check whether any threads or payoffs require attention before the next chapter begins.
- When the brain invokes the Convergence Checkpoint — checking whether major conflicts are moving toward resolution. In this case, the brain sets `convergence_mode: true` so the bomb sweep is performed.
- When the story feels structurally complex and the brain has lost confidence in the thread load — a health check.
- When approaching a narrative milestone, to confirm threads and payoffs required for the milestone are sufficiently developed.

**Standard chapter-boundary delegation sequence (brain-level):**
`plotting_subagent (plot-thread-tracking)` → `[brain updates Story State via story_state_manager if needed]` → `plotting_subagent (multiple-pov-structure)` → `plotting_subagent (gardener-plotting-system)`

**Convergence-mode invocation:**
`plotting_subagent (plot-thread-tracking, convergence_mode=true)` → `[brain acts on bomb sweep flags before resuming forward writing]`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | PlotThread nodes (all statuses); Payoff nodes (Pending and Overdue); DEPENDS_ON edges; INVOLVES edges; PAYS_OFF_IN edges. In convergence mode: CascadeChain nodes; Payoff nodes of type "Consequence bomb" |
| **Returns in artifacts** | Thread status report — load summary, active thread status, overdue flags, pending payoffs status, convergence bomb sweep (convergence mode), convergence opportunities, thread health assessment, no-thread-abandonment check, priority summary. Brain routes follow-up writes to `story_state_manager` if registration gaps or reclassifications are needed |

---

## Dependencies

**Upstream:** PlotThread nodes, Payoff nodes, and INVOLVES edges must be current in Story State KG. Brain provides `chapter_context` and `convergence_mode`.

**Downstream:** `priority_summary.high` items guide the brain's immediate follow-up. Registration gaps trigger `story_state_manager` writes. Reclassification recommendations are applied by the brain via `story_state_manager` update to the relevant CascadeChain nodes. Convergence opportunities may trigger `braided-narrative-technique` for deeper analysis.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. If `convergence_mode` is `true`, also run the CascadeChain and Consequence bomb queries. Populate `kg_context_used`.

### Step 2 — Triage the thread registry

Categorise every PlotThread node by status. Apply the no-thread-abandonment check immediately: any thread with status `Abandoned` and no `abandonment_rationale` property is a gap. Populate `no_thread_abandonment_check`.

### Step 3 — Assess active threads against their convergence windows

For each active PlotThread node:
- What is the `expected_convergence_window`? (May be a chapter range string or a condition.)
- Is the thread on track given its current development as inferred from INVOLVES edges and Chapter nodes?
- Has the window passed? (`chapter_context` > estimated window end) → overdue.
- Is the window within `window_lookahead` chapters? → approaching.

A thread is "at risk" when it is within its window but has not reached the development stage required to make resolution plausible. Flag these separately from overdue threads — they still have time, but not much.

### Step 4 — Assess pending payoffs

For each Payoff node with `resolution_status` Pending or Overdue:
- Has the `expected_window_or_trigger` been reached or passed?
- Is the setup element still in play — will the reader remember it? A Chekhov's gun planted many chapters ago may need re-activation before its payoff, noted in the `note` field.
- For Consequence bomb Payoffs: is the `detonation_trigger` condition approaching in the current narrative?

### Step 5 — Convergence-phase bomb sweep (convergence mode only)

If `convergence_mode` is `true`:

For each CascadeChain node, retrieve its consequence bomb character (Essential / Enriching / Unclassified from `properties.priority_tier`).

**Check registration gaps:** Is this Essential CascadeChain registered as a Payoff node of type "Consequence bomb"? If not, add to `registration_gaps`.

**Assess by tier:**
- **Essential:** Must detonate before the story ends. Is the `detonation_trigger` condition present in the current story trajectory? Flag as "On track — path visible" or "AT RISK — no visible detonation path before ending." AT RISK items go into `priority_summary.high`.
- **Enriching:** Should fire if opportunity permits. Flag any with a natural detonation opportunity in the current convergence window as "Opportunity available."
- **Unclassified:** Convergence is the moment to reclassify. Assess whether the story's current arc makes it clear whether the bomb is Essential or Enriching. Recommend reclassification.

### Step 6 — Identify convergence opportunities

Scan active PlotThread pairs for structural overlap in their INVOLVES edges (same characters, approaching timelines, complementary convergence windows) and DEPENDS_ON edges. Flag:
- Planned convergences (in thread convergence windows or endpoint compass milestones) — on track or at risk.
- Discovered convergences (organic intersections not in the registry) — flag as Gardener moments.

### Step 7 — Assess thread health

Count active threads against the story's structural position. Flag:
- **Overloaded:** Active thread count is high relative to the chapters remaining until major milestones; some threads may need resolution or deliberate open-ending before the structural climax.
- **Underloaded:** Too few active threads for the story's current phase.
- **Dependency cascade risk:** Thread B cannot resolve before Thread A, and Thread A is overdue. The cascade risk compounds.

### Step 8 — Assemble priority summary

Rank all flags:
- **High:** Registration gaps; Essential AT RISK bombs; threads that are significantly overdue with structural consequence.
- **Medium:** Approaching window threads needing attention; reclassification recommendations.
- **Low:** Monitor items, slow-developing tendencies.

### Step 9 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. Ensure `priority_summary` is populated even if all arrays are empty.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] `thread_load_summary` is present with all counts.
- [ ] Every active PlotThread has an on-track / at-risk / overdue assessment.
- [ ] Every overdue thread or payoff has a `narrative_consequence` — why this matters, not just that the window has passed.
- [ ] Every pending Payoff has a `resolution_status` assessment.
- [ ] `convergence_bomb_sweep.performed` matches `convergence_mode` setting.
- [ ] In convergence mode: every Essential bomb has a `detonation_path_assessment`; every Unclassified bomb has a `reclassification_recommendation`.
- [ ] `registration_gaps` is present (even if empty array) in convergence mode.
- [ ] Convergence opportunities distinguish Planned from Discovered.
- [ ] `thread_health_assessment` is present with a specific verdict.
- [ ] `no_thread_abandonment_check` is present; `abandoned_without_rationale` is populated or empty array.
- [ ] No threads resolved. No scenes written. No Story State KG writes from this skill.