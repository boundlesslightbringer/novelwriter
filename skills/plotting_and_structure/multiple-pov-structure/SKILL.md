---
name: multiple-pov-structure
description: Manages POV assignment across chapters — determining which POV character narrates next, the rotation logic across the cast, and the synchronisation of simultaneous events across POV timelines. Invoked by the main agent when a POV rotation decision is needed. Outputs scheduling data only; does not write scenes or determine pacing.
---

# Multiple POV Structure

## Identity

**Purpose:** Decide which POV character narrates the next chapter and why — based on story logic, timeline synchronisation, and narrative momentum — and surface any simultaneous events across other POV timelines that the assignment must account for. The decision must serve the story, not a mechanical rotation schedule.

---

## Core

Manage POV assignment across chapters, rotation logic, and synchronisation of simultaneous events across POV timelines. Output a POV chapter schedule — which POV is next, the reasoning, and what simultaneous events across other storylines must be kept in view. Does not write scenes. Does not determine pacing.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 2.2 (POV Chapter Log):** The full log of chapters written so far — POV assignments, locations, scene summaries, cliffhanger status, connections to other storylines, and chapter deltas. This is the primary record for rotation analysis.

2. **World Bible excerpt — Module 2.1 (Absolute Timeline):** Current timeline state — dates and day counts, simultaneous events, travel records, and seasonal/weather state per region. Essential for synchronising events happening at the same time across different POV locations.

3. *(Optional)* **Current endpoint compass** — the milestones from Defining Rough Endpoints, if the main agent wants to check whether the next POV assignment is moving toward or away from a narrative milestone. Useful when the story is approaching a convergence point.

4. *(Optional)* **World Bible excerpt — Module 2.3 (Plot Thread Registry):** Active thread statuses, including convergence windows. Useful when a thread is approaching its payoff window and a specific POV is needed to deliver it.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**POV chapter schedule** — a structured document containing:

1. **Recommended next POV** — which character narrates the next chapter, stated definitively.

2. **Reasoning** — the specific logic that produces this recommendation, drawn from the POV Chapter Log, the timeline, and any active thread pressures. The reasoning must be narrative, not mechanical: not "it is Character B's turn in the rotation" but "Character B's storyline has reached the moment where the next event must be shown from their perspective because [specific reason]."

3. **Simultaneous events to account for** — a list of events occurring at the same time in other POV timelines during the chapter being planned. For each:
   - Which POV character is it happening to?
   - What is the event?
   - Does the next chapter need to acknowledge it (because the POV character could plausibly know about it), or is it occurring out of reach of their knowledge?
   - Is there a risk of timeline contradiction if the next chapter advances time without accounting for this event?

4. **Rotation pressure flags** — characters whose storylines are accumulating pressure that will require a POV chapter soon. Not a schedule — a flag. Helps the main agent anticipate upcoming rotation decisions.

5. **Cliffhanger handling** — if the previous chapter ended on a cliffhanger (as logged in Module 2.2), a recommendation on whether to resolve it immediately (return to the same POV next) or delay it (cut away to another POV, building tension before returning). This is a narrative judgment, not a rule.

6. **POV proliferation check** — a flag if the story is approaching the point where a new POV might be proposed. Reminds the main agent of the governing constraint: a new POV character is only warranted if it provides a genuinely unique perspective — geographic, factional, psychological — unavailable from any existing POV. This check does not approve or reject new POVs; it surfaces the question for the main agent.

---

## Boundary

- **Does not** write scenes or chapter content of any kind.
- **Does not** determine pacing. Pacing is a separate skill.
- **Does not** generate scene parameters. That is Gardener Plotting System's domain; this skill tells the main agent whose scene to generate next.
- **Does not** audit narrative braiding or thread-level convergence in depth. Braided Narrative Technique handles that analysis. This skill flags convergence pressure but does not analyse it.
- **Does not** approve or create new POV characters. It surfaces the question of POV proliferation; the main agent makes the decision.
- **Does not** update the World Bible. Output is scheduling data returned to the main agent.

---

## Invocation

The main agent invokes Multiple POV Structure:

- Whenever a POV rotation decision is needed — typically at every chapter boundary, before Gardener Plotting System is invoked for the next chapter.
- When the story's structure feels unclear about whose perspective should carry the next significant event.
- When a simultaneous-events synchronisation question arises: two things are happening at the same time in different locations, and it is unclear in what order they should be rendered.

**Standard chapter-boundary invocation sequence:**  
`[Previous chapter complete] → Multiple POV Structure → Gardener Plotting System (for the assigned POV) → Scene Construction`

> **Sibling skill:** When the human user has already specified which POV character narrates the next chapter, invoke **Single POV Structure** instead of this skill. Single POV Structure accepts the user's assignment as given, validates it, and produces the same scheduling output. Multiple POV Structure and Single POV Structure are mutually exclusive for any given chapter boundary.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 2.2 (POV Chapter Log), Module 2.1 (Absolute Timeline). Optionally: Module 2.3 (Plot Thread Registry), endpoint compass. |
| **Main agent writes to** | Nothing — scheduling data is returned to the main agent; no World Bible update occurs from this skill's output. |

---

## Dependencies

**Upstream:** Module 2.2 and Module 2.1 must be updated after the previous chapter before this skill is invoked. Optionally: **Plot Thread Tracking** output (if a recent thread status report is available, the main agent may pass convergence window data alongside the Module 2.3 excerpt).  
**Downstream:** The recommended next POV is passed to **Gardener Plotting System**, which generates scene parameters for that character. Braided Narrative Technique uses Module 2.2 for deeper convergence analysis when needed.

---

## Instructions

### Step 1 — Map the current state of all POV storylines

Read the full POV Chapter Log (Module 2.2). For each active POV character, establish:
- When did they last narrate a chapter?
- Where did their storyline end — what was their chapter's last state?
- Was there a cliffhanger? If so, is it pending resolution?
- What connections were flagged to other POV storylines in their chapter delta?
- How many chapters have they narrated in total, and what is the rough cadence of their appearances?

This map is the baseline for rotation reasoning.

### Step 2 — Synchronise the timeline

Read the Absolute Timeline (Module 2.1). Establish:
- What is the current story date for each active POV character?
- Are any events happening simultaneously in different POV locations?
- Are any travel records creating timeline constraints — characters who should have arrived somewhere, or who are en route?
- Is there a risk of timeline contradiction if the next chapter advances time without accounting for a simultaneous event?

Timeline synchronisation is non-negotiable. If two POV characters are experiencing events at the same time in different locations, the order in which those events are rendered on the page matters — both for reader knowledge management and for dramatic irony — but neither can simply not happen.

### Step 3 — Apply rotation logic

Rotation in a multi-POV story is not a mechanical schedule. It is a narrative judgment. Apply the following in order of priority:

**Priority 1 — Narrative necessity:** Is there a specific POV whose storyline has reached a moment that must be shown now? A consequence that has arrived, a revelation that is about to occur, a choice that cannot be deferred? If yes, that POV is next regardless of rotation cadence.

**Priority 2 — Cliffhanger logic:** Did the previous chapter end on a cliffhanger? The decision to return immediately or cut away is a narrative choice:
- **Return immediately** when the cliffhanger's tension is so acute that cutting away would feel arbitrary rather than purposeful, or when the reader needs resolution to be able to hold what comes next.
- **Cut away** when the delay will build productive tension — when the reader's suspense about the cliffhanger makes the intervening chapter more charged — and when the intercut POV has something genuinely urgent of its own to show.
Never cut away from a cliffhanger simply to impose structure. The cut must be motivated.

**Priority 3 — Information management:** Is there a POV character whose perspective would give the reader knowledge that should arrive before, after, or simultaneously with what other POVs reveal? The order in which reader knowledge accumulates is a structural tool. Use it deliberately.

**Priority 4 — Rotation pressure:** Which POV character has the most accumulated narrative pressure — the most urgent unanswered questions, the most active consequence chains, the most threads approaching convergence? This is not a tiebreaker of last resort; it is the default when no higher priority applies.

**Priority 5 — Cadence and reader relationship:** How long has it been since the reader was in a given POV character's head? If a POV has been absent for many chapters, re-establishing it requires some re-anchoring — the reader needs to re-enter the character's voice and situation. This is a cost that must be weighed against the narrative benefit of returning to that POV now.

### Step 4 — Identify simultaneous events

For every event logged in Module 2.1 as occurring simultaneously with events in the chosen POV's upcoming chapter:

- Determine whether the chosen POV character could plausibly know about it (are they in the same location? have they received word?).
- If they could know: the scene parameters for the next chapter must account for this knowledge.
- If they could not know: the event is running in parallel, off-page. Flag it for the main agent so that the subsequent POV chapter (when it arrives) can render it from the correct temporal position.
- If the simultaneous event creates a potential timeline contradiction with the chosen chapter: flag it for the main agent to resolve before writing begins.

### Step 5 — Flag rotation pressures

Survey the full cast of active POV characters. For each, note whether their storyline pressure is:
- **Low** — their last chapter ended at a relative pause; they can wait.
- **Medium** — their storyline has accumulated some pressure; they should appear within the next few chapters.
- **High** — their storyline has reached a point where delay will create structural problems: consequences will arrive off-page, threads will lapse past their convergence window, or reader relationship to the character will weaken from absence.

Return these flags to the main agent. Do not assign chapter numbers — just flag the pressure level and the reason.

### Step 6 — POV proliferation check

Count the current number of active POV characters. If:
- A new POV is being considered, confirm the governing constraint: a new POV is only warranted if it provides a perspective — geographic, factional, psychological — genuinely unavailable from any existing POV. Surface this question for the main agent without ruling on it.
- The current POV count is high enough that the rotation period for each POV character is becoming long (readers are spending many chapters away from any given character), flag this as a structural pressure. It does not require action immediately, but it should be tracked.

### Step 7 — Assemble and return the POV chapter schedule

Return the complete scheduling document to the main agent. The main agent passes the recommended POV to Gardener Plotting System for scene parameter generation.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Recommended POV is stated definitively with specific narrative reasoning — not "it's their turn."
- [ ] Simultaneous events are mapped and cross-referenced against what the chosen POV character can plausibly know.
- [ ] Cliffhanger handling is explicit and reasoned — not defaulted.
- [ ] Rotation pressure flags are present for all active POV characters.
- [ ] POV proliferation check is present.
- [ ] No scenes written, no scene parameters generated, no pacing determined.
- [ ] No World Bible writes specified.
