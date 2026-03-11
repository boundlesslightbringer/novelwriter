---
name: braided-narrative-technique
description: Ensures POV storylines run parallel, intersect meaningfully at convergence points, and contain no redundant scenes (same event shown from two POVs with no new information added). Operates at the chapter-sequence level, not the individual scene level. Invoked when a storyline redundancy or convergence question arises. Outputs analysis only — does not rewrite.
---

# Braided Narrative Technique

## Identity

**Purpose:** Analyse the multi-POV narrative as a braided structure — examining whether the POV storylines are running with productive parallel tension, intersecting at genuinely meaningful convergence points, and carrying no redundant scenes where showing the same event from a second POV adds nothing the reader does not already have. Output is analysis and recommendations; the main agent decides what to act on.

> **Sibling skills:** This skill works alongside [multiple-pov-structure](../multiple-pov-structure/SKILL.md) (determines which POV narrates next) and [plot-thread-tracking](../plot-thread-tracking/SKILL.md) (tracks thread convergence windows). Use all three together for comprehensive multi-POV orchestration.

---

## Core

Ensure POV storylines run parallel, intersect meaningfully at planned and discovered convergence points, and contain no redundant scenes. Operates at chapter-sequence level, not individual scene level. Outputs braiding analysis — convergence opportunities, redundancy flags, suggested connection points. Does not rewrite. Does not make plot decisions.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 2.2 (POV Chapter Log):** The complete log of all chapters written — POV assignments, locations, scene summaries, cliffhanger status, inter-storyline connections, and chapter deltas. This is the primary material for braiding analysis.

2. **World Bible excerpt — Module 2.3 (Plot Thread Registry):** All active, dormant, and resolved threads — their characters, convergence windows, dependencies, and resolution status. Thread convergence windows inform where the braid should be pulling toward.

3. *(Optional)* **Endpoint compass** — the milestones from Defining Rough Endpoints. If the main agent wants to check whether the braid's current trajectory is moving toward the story's major structural moments, the compass provides that reference.

4. *(Optional)* **Chapter range for analysis** — if the main agent wants a focused analysis of a specific span of chapters (e.g. the last ten chapters, or chapters approaching a known convergence point) rather than the full narrative to date.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Braiding analysis** — a structured report containing:

### 1. Braid Map Summary

A concise representation of the current state of each POV storyline — where it is spatially, temporally, and narratively. This is not a retelling of the plot; it is a structural snapshot that makes the braid's shape visible:
- Which storylines are running in parallel without yet intersecting?
- Which storylines have already intersected, and what was the nature of that intersection?
- Which storylines are converging toward an imminent intersection?

### 2. Redundancy Flags

A flag for every scene or chapter where the same event is shown from two different POVs. For each flagged instance:
- **What event** is shown from multiple angles.
- **What the first POV rendering established** for the reader.
- **What the second POV rendering adds** — or fails to add. The critical distinction:
  - *New information:* The second POV reveals facts, interiority, or knowledge that the first POV could not access. This is not redundant — it is deliberate irony or revelation architecture.
  - *New emotional register:* The second POV shows the same event through a genuinely different psychological lens that transforms its meaning. This is not redundant — it is dramatic counterpoint.
  - *Neither:* The second POV restates what the reader already knows, from a perspective that adds no information and no meaningful reframing. This is redundant and should be flagged for removal or replacement.
- **Recommendation:** Cut the redundant rendering / replace it with a scene that advances the second POV character's storyline independently / restructure so the second POV arrives at the event through a genuinely different information state.

### 3. Convergence Opportunities

A list of convergence points — moments where POV storylines could meaningfully intersect — distinguishing:
- **Planned convergences:** Intersections that were anticipated in the thread registry or endpoint compass. Flag whether they are on track, approaching ahead of schedule, or at risk of being missed.
- **Discovered convergences:** Intersections that have emerged organically from the writing — not planned, but now legible in the braid. Flag these as opportunities: the main agent may choose to develop them, or to let them be present as structural resonance without explicit intersection.
- **Missed convergences:** Points where storylines were close enough to intersect meaningfully but did not. Flag whether the miss was deliberate (the near-miss is itself a structural choice, building toward a later intersection) or inadvertent.

### 4. Parallel Tension Assessment

An assessment of whether the parallel storylines — the sections of the braid where POV characters are not intersecting — are generating productive tension or coasting. A multi-POV narrative depends on the reader holding multiple storylines simultaneously; the storylines must be in productive dialogue even when they are not in direct contact. For each parallel section:
- Are the storylines thematically rhyming — exploring different facets of the same question from different positions?
- Are they in dramatic irony with each other — does the reader know something from one POV that creates dread or anticipation about what another POV character is walking into?
- Or are they running in isolation — neither rhyming nor in irony, merely coexisting? This is the weakest configuration and should be flagged.

### 5. Braiding Recommendations

Specific, actionable recommendations for the main agent, ranked by urgency:
- **Immediate:** Redundancies or structural gaps that, if left unaddressed, will compound and become harder to fix.
- **Near-term:** Convergence opportunities that will pass if not developed soon.
- **Monitor:** Issues that are not yet problems but should be watched.

---

## Boundary

- **Does not** operate at the individual scene level — it analyses chapter sequences, not the internal structure of individual scenes. Conflict Layering and Scene Construction handle scene-level concerns.
- **Does not** rewrite any scene or chapter. Flags, analyses, and recommends; the main agent decides what to act on.
- **Does not** make plot decisions. It surfaces convergence opportunities — the main agent decides whether to develop them.
- **Does not** determine POV assignment for upcoming chapters. That is Multiple POV Structure's domain.
- **Does not** audit individual POV voice consistency. That is POV Consistency Maintenance and POV Consistency Auditing's domain.
- **Does not** update the World Bible. Output is analysis returned to the main agent.

---

## Invocation

The main agent invokes Braided Narrative Technique:

- When a storyline redundancy question arises — the main agent suspects a scene is showing something the reader already knows from another POV.
- When a convergence question arises — storylines are approaching each other and the main agent wants to assess whether the intersection is structurally sound.
- Periodically as a structural health check — every five to ten chapters is a reasonable cadence for multi-POV narratives, or when the story has been written in a long linear stretch and the braiding has not been examined.
- When the story feels structurally slack — chapters passing without sufficient inter-storyline tension — and the main agent suspects the problem is in the braiding rather than in any individual scene.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 2.2 (POV Chapter Log), Module 2.3 (Plot Thread Registry). Optionally: endpoint compass. |
| **Main agent writes to** | Nothing — analysis is returned to the main agent; no World Bible update occurs from this skill's output. |

---

## Dependencies

**Upstream:** Module 2.2 and Module 2.3 must be current before this skill is invoked. **Plot Thread Tracking** output (if recently generated) may be passed alongside the Module 2.3 excerpt for richer convergence analysis.  
**Downstream:** Recommendations may trigger re-invocation of **Scene Construction** (to replace a redundant scene), **Multiple POV Structure** (to adjust upcoming POV assignments in response to braiding analysis), or **Gardener Plotting System** (to develop a discovered convergence opportunity).

---

## Instructions

### Step 1 — Build the braid map

From the POV Chapter Log, construct a structural picture of the braid. For each active POV character, list their chapters in sequence. Lay them against each other chronologically (using Module 2.1 for temporal orientation if needed). The result is the braid's current shape:
- Parallel sections (POVs running independently).
- Intersection points (chapters where POV characters are in the same location or directly interacting events).
- Gaps (periods where a POV is absent from the narrative).

This map is the analytical foundation for everything that follows. Make it explicit — even a simplified text representation (e.g. "Ch. 1–5: A and B parallel; Ch. 6: A intersects C; Ch. 7–10: B dormant; Ch. 11: B returns...") is more useful than a narrative description.

### Step 2 — Audit for redundancy

For every chapter in the log, check: does this chapter render an event that has already been rendered by another POV?

If yes, apply the test: what does the second rendering add?

**New information test:** Does the second POV have access to facts, actions, or knowledge that the first POV could not see? (The first POV was in the room; the second POV is in the room too but knows something the first does not.) If the answer is yes — and the new information is narratively material — this is not redundancy. It is information architecture.

**New register test:** Does the second POV experience the event through a psychological lens so different that the *meaning* of the event is transformed? (The first POV reads a conversation as a political negotiation; the second reads the same conversation as a moment of personal betrayal.) If the answer is yes — and the transformation is genuinely illuminating — this is not redundancy. It is dramatic counterpoint.

**If neither test passes:** Flag it. The second rendering is restating known information. Recommend cutting it or replacing it with a scene that advances the second POV's storyline independently.

### Step 3 — Map convergence points

From the Plot Thread Registry, extract convergence windows — where are threads expected to resolve, and which POV characters are involved?

Cross-reference with the braid map: where are POV storylines physically and temporally close enough to intersect? Flag:
- **Planned convergences on track:** Thread registry convergence windows that the braid map shows the narrative approaching at the expected pace.
- **Planned convergences at risk:** Convergence windows that the current braid trajectory will miss — either because a storyline is moving too slowly, or because the POV assignment has kept the relevant characters apart longer than the window allows.
- **Discovered convergences:** Places where the organic development of the narrative has brought storylines into proximity that was not in the thread registry. These are Gardener moments — the story has grown toward something the planning did not anticipate. Flag them as opportunities.
- **Near-misses to assess:** Places where storylines came close but did not intersect. Ask: was this a deliberate choice (the near-miss itself is meaningful — the reader sees how close they came, which builds toward the eventual real intersection)? Or was it inadvertent? Near-misses only work structurally if the reader is positioned to feel them.

### Step 4 — Assess parallel tension

For each parallel section of the braid — chapters where POV characters are running independently — assess the quality of the inter-storyline tension. Ask:

**Thematic rhyme:** Are the parallel storylines exploring the same question from different positions? Two characters in different locations, one learning the cost of loyalty and the other learning the cost of its absence, are in productive thematic dialogue even without physical intersection. This is the braid working as it should.

**Dramatic irony:** Does the reader know something from one POV that creates dread or anticipation about what another POV character is walking into? This is the most powerful form of parallel tension — the reader holds knowledge that the character does not, and that knowledge charges every subsequent scene with the other POV.

**Isolation:** Are the parallel storylines running independently with no thematic rhyme and no dramatic irony? This is the weakest configuration. The reader is moving between storylines without any structural reason to hold them together; they will feel like separate stories rather than a braided narrative. Flag these sections.

### Step 5 — Rank and write recommendations

Organise recommendations by urgency:

**Immediate:** Confirmed redundancies (failed both tests in Step 2); convergences that are about to be missed and cannot be recovered later; parallel sections that have been running in isolation for long enough that reader engagement with the absent POV will have weakened.

**Near-term:** Discovered convergence opportunities that are approaching and should be developed if the main agent chooses to take them; planned convergences that are on track but will require attention within the next few chapters.

**Monitor:** Structural tendencies — a POV that has been absent too long; a thread whose convergence window is still distant but whose trajectory is not building toward it; a parallel section that is not yet in isolation but is at risk.

### Step 6 — Return the braiding analysis

Return the complete analysis to the main agent. The main agent decides which recommendations to act on and in what order.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Braid map is present — the shape of the narrative is made explicit before analysis begins.
- [ ] Every dual-POV rendering has been tested against both the new information test and the new register test; verdicts are explicit.
- [ ] Convergence opportunities distinguish planned, discovered, and near-miss types.
- [ ] Parallel tension assessment covers every significant parallel section.
- [ ] Recommendations are ranked by urgency (immediate / near-term / monitor).
- [ ] No rewrites produced. No plot decisions made. No POV assignments specified.
- [ ] No World Bible writes specified.
