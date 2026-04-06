---
name: single-pov-structure
description: Called when the human user has specified that the next chapter should be narrated by a particular POV character. Validates the requested assignment against timeline synchronisation and structural concerns, then produces the same scheduling output as Multiple POV Structure — simultaneous events to account for, rotation pressure flags, cliffhanger handling, and POV proliferation check — so that Scene Construction can proceed with full structural awareness. Does not override the user's stated preference; surfaces concerns for the main agent to relay if the assignment is structurally problematic.
---

# Single POV Structure

## Identity

**Purpose:** When the human user specifies which POV character narrates the next chapter, this skill takes that assignment as given, validates it against the current story state, and produces the same structural scaffolding output as Multiple POV Structure — timeline synchronisation, simultaneous events, rotation pressure flags, cliffhanger handling — so that the main agent and Scene Construction have full awareness of what the chosen assignment entails. If the assignment creates structural problems, those problems are surfaced clearly; they are not silently corrected.

---

## Core

Accept a user-specified POV character for the next chapter. Validate the assignment against the current timeline, POV Chapter Log, and active story state. Produce the same scheduling output as Multiple POV Structure: simultaneous events to account for, rotation pressure on other storylines, cliffhanger handling, and POV proliferation check. Surface any structural concerns about the assignment without overriding it. Output scheduling data only; does not write scenes or determine pacing.

---

## Relationship to Multiple POV Structure

This skill is a sibling of Multiple POV Structure. The distinction is in the entry point:

- **Multiple POV Structure:** The main agent asks "whose POV should come next?" and the skill determines the best assignment using rotation logic and narrative priority.
- **Single POV Structure:** The human user has already answered "whose POV comes next" and the skill validates that answer, surfaces any concerns, and produces the structural output needed to proceed.

The **output structure is identical** in both skills. The difference is that Multiple POV Structure generates and justifies its own recommendation, while Single POV Structure receives the recommendation as a given and builds around it.

Where Multiple POV Structure would produce a "Recommended next POV" section with full rotation reasoning, Single POV Structure produces a "Requested assignment" section with a validation assessment. All other output sections — simultaneous events, rotation pressure flags, cliffhanger handling, POV proliferation check — are identical in structure and purpose.

---

## Input

The main agent provides:

1. **Requested POV character** — the specific character the human user has specified for the next chapter. Passed in by the main agent verbatim; not modified or reinterpreted.

2. **World Bible excerpt — Module 2.2 (POV Chapter Log):** The full log of chapters written so far — POV assignments, locations, scene summaries, cliffhanger status, connections to other storylines, and chapter deltas.

3. **World Bible excerpt — Module 2.1 (Absolute Timeline):** Current timeline state — dates, simultaneous events, travel records, seasonal/weather state. Essential for synchronising the chosen POV's chapter with events occurring elsewhere.

4. *(Optional)* **Reason from the human user** — if the human user has stated why they want this particular POV next (e.g. "I want to check in on Aldric before Vara's assessment arrives" or "I want to show what Sethric is doing during the negotiation"), this is passed in as context. It helps the skill assess whether the assignment achieves the user's stated intent and whether there are structural considerations the user may not have anticipated.

5. *(Optional)* **Current endpoint compass** — milestones from Defining Rough Endpoints, if the main agent wants to check whether the assignment is moving toward or away from a structural milestone.

6. *(Optional)* **World Bible excerpt — Module 2.3 (Plot Thread Registry):** Active thread statuses and convergence windows — useful for assessing whether the requested assignment will advance, stall, or bypass an active thread.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**POV chapter schedule** — a structured document containing:

### 1. Requested Assignment

- **Requested POV:** The character specified by the human user.
- **Validation status:** One of:
  - `CLEAR` — the assignment is consistent with the current story state; no structural concerns.
  - `ADVISORY` — the assignment is viable but carries one or more structural considerations the main agent should be aware of (e.g. the chosen POV has been absent for many chapters and re-entry will require careful anchoring; or the assignment bypasses an imminent cliffhanger resolution in a way that may feel arbitrary rather than purposeful).
  - `CONCERN` — the assignment creates a specific structural problem the main agent should relay to the human user before proceeding (e.g. it would require the chapter to be set at a time before events already narrated in another POV, creating a timeline contradiction; or the chosen character has not yet been established as a POV and no POV profile exists for them).
- **Validation notes:** The specific reasoning behind the validation status. If `CLEAR`, brief. If `ADVISORY` or `CONCERN`, specific and actionable — what is the issue, what does it affect, and what would resolve it.

> **If the validation status is CONCERN:** The main agent should relay the concern to the human user and request confirmation before invoking Scene Construction. The skill does not refuse to produce the rest of the output — it completes the scheduling document so that everything is ready if the user confirms — but it flags that confirmation is needed.

> **The skill does not override the user's preference.** Even in a CONCERN case, the full output is produced. The main agent decides how to handle the concern.

### 2. Intent Alignment Check *(if user's reason was provided)*

If the human user stated why they want this POV next, assess whether the assignment achieves that intent:
- Does the requested POV's current storyline position actually deliver what the user expects?
- Are there any story-state facts (e.g. the character is in a different location than the user may have assumed, or a relevant event has already occurred off-page in another chapter) that the user should know before proceeding?
- If the user's intent could be achieved equally well — or better — with a small modification to the assignment, note it as an option. Do not recommend abandoning the user's preference; offer the variant as information only.

### 3. Simultaneous Events to Account For

Identical in structure to Multiple POV Structure's output. For every event occurring at the same story-time as the chapter being planned, in other POV timelines:
- Which POV character is it happening to?
- What is the event?
- Can the requested POV character plausibly know about it? If yes, their chapter must account for this knowledge. If no, note the dramatic irony or timeline consideration.
- Is there a risk of contradiction if the chapter advances time without accounting for this event?

### 4. Rotation Pressure Flags

Identical in structure to Multiple POV Structure's output. For all active POV characters *other than the one being assigned*:
- Flag their current rotation pressure: Low / Medium / High.
- If assigning the requested POV means a high-pressure storyline is being passed over, note it explicitly — not as a reason to override the user's choice, but as a flag for the main agent to plan around. (A high-pressure storyline being skipped may need to be addressed in the chapter immediately after the user-requested one.)

### 5. Cliffhanger Handling

Identical in structure to Multiple POV Structure's output. If the previous chapter ended on a cliffhanger:
- Is the requested POV assignment cutting away from the cliffhanger or returning to it?
- If cutting away: is this motivated (the cut will build tension productively) or does it risk feeling arbitrary? Note the distinction.
- If returning: confirm that the requested POV is the same character who was at the cliffhanger, or — if it is a different character — note that the cliffhanger remains unresolved and will need to be addressed in a subsequent chapter.

### 6. POV Proliferation Check

Identical in structure to Multiple POV Structure's output. If the requested character is a new POV — one who has not previously narrated a chapter — flag this:
- Does this character meet the governing constraint for a new POV? (A new POV is only warranted if it provides a genuinely unique perspective — geographic, factional, psychological — unavailable from any existing POV.)
- If yes: confirm the constraint is met and note what unique perspective this new POV provides.
- If no, or if it is unclear: surface the question for the main agent to assess before proceeding.

---

## Boundary

- **Does not** override the human user's stated POV preference. The assignment is taken as given; concerns are surfaced, not enforced.
- **Does not** generate an alternative recommendation. If the user's assignment has problems, the skill surfaces them; it does not substitute a different assignment.
- **Does not** write scenes or scene parameters. That is Gardener Plotting System and Scene Construction's domain.
- **Does not** determine pacing. Pacing is a separate skill.
- **Does not** audit narrative braiding or thread convergence in depth. Braided Narrative Technique handles that.
- **Does not** update the World Bible. Output is scheduling data returned to the main agent.

---

## Invocation

The main agent invokes Single POV Structure:

- When the human user specifies which POV character should narrate the next chapter, in place of Multiple POV Structure.
- Single POV Structure and Multiple POV Structure are mutually exclusive for any given chapter boundary — one or the other is invoked, not both.

**Invocation sequence when user specifies a POV:**  
`[Human user specifies POV] → Single POV Structure → [Main agent relays any CONCERN to user if present, confirms] → Gardener Plotting System (for the assigned POV) → Scene Construction`

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 2.2 (POV Chapter Log), Module 2.1 (Absolute Timeline). Optionally: Module 2.3 (Plot Thread Registry), endpoint compass. |
| **Main agent writes to** | Nothing — scheduling data is returned to the main agent; no World Bible update occurs from this skill's output. |

---

## Dependencies

**Upstream:** Module 2.2 and Module 2.1 must be current before invocation. The human user's stated POV preference must be passed in by the main agent.  
**Downstream:** The confirmed POV assignment is passed to **Gardener Plotting System**, which generates scene parameters for that character. If a CONCERN is raised, the main agent relays it to the human user before proceeding.

---

## Instructions

### Step 1 — Confirm the requested character's POV status

Is the requested character an existing POV character with a prior narrated chapter? If yes, proceed directly to Step 2. If no — this is a first-time POV for this character — apply the POV proliferation check immediately (Step 6) and flag it in the validation notes before continuing.

### Step 2 — Validate the assignment against the current story state

Read Module 2.2 to establish the requested character's current storyline position: where they last narrated, what state their storyline is in, how long they have been absent from narration.

Check for structural concerns in this priority order:

**Timeline integrity:** Would a chapter from this POV, set at the current story date, create a contradiction with events already established in the Chapter Log? (e.g. the requested character was established as being in Location A in Chapter 12; placing them in Location B in Chapter 15 requires travel time that has not been accounted for.) If yes: CONCERN.

**Knowledge state integrity:** Does the requested character's current knowledge state (Module 1.2, if passed in, or as implied by the Chapter Log) support the chapter the user appears to want? If the user's reason suggests they want to show this character learning something, check whether that information is something the character could plausibly have access to at this story-date. If there is a mismatch: ADVISORY.

**Re-entry cost:** How long has this POV been absent? A character absent for five or more chapters will require deliberate re-anchoring — the reader needs to re-enter their voice, location, and situation. This is not a reason to refuse the assignment; it is an ADVISORY note that Scene Construction should factor in extra re-anchoring at the chapter's opening.

**Cliffhanger bypass:** Does the assignment cut away from an unresolved cliffhanger? If so, is the cut motivated, or does it risk feeling arbitrary? Assess and note. This is typically ADVISORY rather than CONCERN unless the cliffhanger is severe enough that the cut would be actively confusing.

Assign validation status: CLEAR / ADVISORY / CONCERN.

### Step 3 — Intent alignment check (if user's reason was provided)

Read the user's stated reason for the assignment. Ask:
- Is the requested character's current storyline in a position to deliver what the user expects?
- Are there story-state facts the user may not have in mind that affect whether the chapter will achieve the intended effect?

If the user's intent is fully achievable with the requested assignment: note it briefly and move on.

If there is a gap between the user's intent and what the assignment will deliver, surface it clearly: "Based on the current story state, [requested character] is [current situation]. If the intent is [stated intent], [note the gap]. A possible approach: [option]." State it as information, not as a recommendation to change the assignment.

### Step 4 — Map simultaneous events

Read Module 2.1. For the story-date of the chapter being planned, identify all events occurring simultaneously in other POV timelines. For each:
- Can the requested POV character plausibly know about it?
- Is it creating active dramatic irony (the reader knows; the character does not)?
- Does it risk a timeline contradiction if the chapter advances time without acknowledging it?

### Step 5 — Flag rotation pressures

Survey the full cast of active POV characters other than the one being assigned. For each, note Low / Medium / High rotation pressure and the reason. If any high-pressure storyline is being passed over by this assignment, flag it explicitly for the main agent's planning.

### Step 6 — Cliffhanger handling

Assess the previous chapter's cliffhanger status (from Module 2.2). Apply the same logic as Multiple POV Structure: is the cut away motivated or arbitrary? State the assessment and, if advisory, note what makes a cut away work in this specific case (what the intercut chapter must contain to make the delay feel purposeful rather than evasive).

### Step 7 — POV proliferation check

If the requested character is a new POV: assess whether the governing constraint is met (genuinely unique perspective unavailable from existing POVs). State the assessment. If it is clearly met, confirm it. If it is unclear or unmet, surface the question for the main agent — this is not a refusal, it is a flag.

### Step 8 — Assemble and return the scheduling document

Return the complete scheduling document to the main agent. If validation status is CONCERN, the main agent should relay the concern to the human user before passing the assignment to Gardener Plotting System.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Validation status is explicit — CLEAR / ADVISORY / CONCERN — with specific reasoning.
- [ ] Intent alignment check is present if user's reason was provided.
- [ ] Simultaneous events are mapped; each is cross-referenced against what the requested POV can plausibly know.
- [ ] Rotation pressure flags are present for all active POV characters other than the assigned one.
- [ ] Cliffhanger handling is explicit and reasoned.
- [ ] POV proliferation check is present — either confirming an existing POV or assessing a new one against the governing constraint.
- [ ] The user's preference was not overridden — even in a CONCERN case, the full output is produced.
- [ ] No scenes written, no scene parameters generated, no pacing determined.
- [ ] No World Bible writes specified.
