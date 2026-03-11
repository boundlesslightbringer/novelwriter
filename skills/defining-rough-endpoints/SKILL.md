---
name: defining-rough-endpoints
description: Establishes the story's compass — starting situation (with optional prologue), vague ending destination, 2–4 major milestones, and the core conflict question — from the validated seed. Because milestones naturally involve key characters who do not yet exist, this skill outputs character slot sketches alongside the compass; the main agent then invokes Character Conception in early mode for each slot before milestones are finalised. Invoked once, immediately after Finding a Seed. Main agent writes to World Bible Modules 2.3 and 2.4.
---

# Defining Rough Endpoints

## Identity

**Purpose:** Give the story a compass, not a map. Establish where the story begins (including whether a prologue is needed), where it vaguely ends, what major shape-moments lie between, and what single question the entire story is trying to answer. Because milestones naturally imply characters, and characters do not yet exist at this stage, this skill works in two passes via the main agent: a first pass produces draft milestones with character slot sketches; the main agent invokes Character Conception for each slot; a second pass refines the milestones using the conceived characters' logic. The endpoint compass is a direction, not a plan.

---

## Core

Establish the story's compass: starting situation (with optional prologue specification), vague ending destination, 2–4 major milestones, and the core conflict question. Milestones naturally involve characters — this skill outputs character slot sketches to enable early Character Conception invocation, then incorporates the resulting character concepts to ensure milestones are grounded in character logic rather than abstract story structure. Endpoints are intentionally loose and will shift as the story grows. Do not plot individual scenes or chapters. Do not outline.

---

## Input

### Pass 1 (required)

1. **Validated seed document** from Finding a Seed — seed, generation method, validation record, genre/subgenres, themes, thematic interdependencies, and questions.
2. *(Optional)* **Thematic or tonal constraints** carried forward.
3. *(Optional)* **Research material** from Research Integration, if the seed's context requires factual grounding before the compass can be oriented.

### Pass 2 (required to finalise milestones)

4. **Character concept documents** — one per character slot, returned by Character Conception after the main agent invokes it for each slot produced in Pass 1. These concepts are used to refine draft milestones so that milestone logic flows from character psychology, not structural convenience.

> The main agent manages the handoff between passes. This skill does not invoke Character Conception directly.

---

## Output

### Pass 1 Output

1. **Prologue specification** *(if applicable)* — see below.
2. **Starting situation** — one paragraph.
3. **Draft ending destination** — 1–2 sentences.
4. **Draft milestones** — 2–4 milestone sketches, each flagged with which character slots they require.
5. **Character slot sketches** — one per implied character, structured for Character Conception early invocation (see below).
6. **Draft core conflict question** — one sentence.
7. **Compass notes** — what has been left open.

### Pass 2 Output (final compass)

The same structure as Pass 1, with milestones refined using the character concept documents received from Character Conception. The final compass replaces the draft. Character slot sketches are superseded by references to the conceived characters by name/role.

> The main agent uses the final compass to initialise World Bible Modules 2.3 and 2.4.

---

## Prologue Specification

When the seed or the story's structural needs suggest a prologue — a chapter that precedes the main narrative, operating at a different point in time, from a different perspective, or at a different narrative register — the prologue must be specified in the starting situation section.

A prologue is warranted when one or more of the following apply:
- The story's core tension is better *felt* before the main narrative begins than explained within it.
- A significant prior event (a death, a founding, an act of betrayal) needs to be rendered rather than referenced in backstory.
- A POV character or perspective that will not recur in the main narrative can establish something essential at the outset.
- The genre or tonal register of the story benefits from a threshold moment before Chapter 1.

A prologue is **not** warranted simply to provide exposition or worldbuilding context. If the material can be integrated into Chapter 1 or later chapters through the natural filter of a POV character, it should be.

**Prologue specification includes:**

- **Temporal relationship** to Chapter 1: how far before the main narrative? (Days, years, generations?)
- **POV or narrative register**: whose perspective, or — if omniscient or anonymous — what register?
- **What it establishes**: what the reader must carry into Chapter 1 that cannot be as effectively established in Chapter 1 itself.
- **What it withholds**: what the prologue implies but does not explain — the hook that pulls the reader into the main narrative.
- **Relationship to milestones**: whether the prologue event is itself a milestone, or is a precondition that makes a later milestone legible.

If no prologue is needed, this section is marked **absent** and the starting situation proceeds directly to the Chapter 1 configuration.

---

## Character Slot Sketches and the Two-Pass Process

### The problem

Milestones are not abstract narrative events — they are moments in which specific people make choices, collide, or are broken by circumstances. A milestone without a character is a structural hypothesis, not a story event. But characters do not yet exist at the point Defining Rough Endpoints is first invoked: Worldbuilding has not run, Module 3.1 does not exist, and Character Conception normally reads Module 3.1 as its primary input.

### The solution

This skill resolves the problem through a two-pass loop via the main agent:

**Pass 1 — Draft milestones with character slots:**  
Each draft milestone names the character *type* (role, implied contradiction, implied stakes) without creating a character record. This role description is output as a **character slot sketch** structured for early invocation of Character Conception.

**Main agent loop — Early Character Conception:**  
The main agent invokes Character Conception for each slot, passing the slot sketch as the primary input instead of Module 3.1. Character Conception operates in **early invocation mode** (see that skill's documentation), using the world context implied by the endpoint compass in place of a fully populated Module 3.1.

**Pass 2 — Refine milestones with conceived characters:**  
The main agent returns the character concept documents to this skill. Draft milestones are refined: abstract role descriptions are replaced with characters whose specific psychology, core contradiction, and desires now drive the milestone logic. If a character concept reveals that a draft milestone is implausible or uninteresting given who the character actually is, the milestone is revised or discarded.

> **Gardener principle:** The two-pass process honours the Gardener approach. Characters are not assigned to milestones — milestones are revised to fit the characters who have been conceived. If a conceived character's logic points away from a draft milestone, the character wins.

### Character slot sketch structure

Each character slot sketch contains:

1. **Narrative role** — what story function this character must serve in the milestone context (e.g. "the person whose choice determines the milestone's outcome"; "the figure whose arrival triggers the turning point"; "the character who carries the consequence of this event forward").
2. **Implied contradiction** — based on the seed and compass, what internal tension does this character's role seem to require? This is a hypothesis, not a specification — Character Conception will find or replace it.
3. **Stakes** — what does this character stand to lose or gain in the milestone? What makes their presence in this moment consequential?
4. **World context available** — the relevant world sketch from the endpoint compass and seed (substitutes for Module 3.1 in early invocation mode).
5. **Open questions** — 2–3 questions about this character that the milestone cannot answer without knowing who they actually are.

---

## Full Output Structure

### Prologue specification *(if applicable)*
*As described above, or marked absent.*

### Starting situation
A one-paragraph description of where the main narrative opens: the world's state (sketch only — Worldbuilding will develop it), the central figure(s)' position within it, and the specific instability already present. Not a scene — a situation. The room before the argument, not the argument itself.

### Ending destination *(draft in Pass 1; may be refined in Pass 2)*
1–2 sentences. The type of ending — the territory, not the location. Specific enough to orient; vague enough to be discovered. Test: *If we arrived somewhere slightly different, would it still feel like the story found its ending?*

### Milestones *(draft in Pass 1; refined with character concepts in Pass 2)*
2–4 milestones. Each described in 1–3 sentences: what kind of event or turning point, which forces are in play, what changes. Each tested for looseness — it must be reachable in at least three different ways. Each linked to one or more character slots (Pass 1) or conceived characters (Pass 2). Milestones are hypotheses; the Gardener principle applies.

### Core conflict question *(draft in Pass 1; confirmed or revised in Pass 2)*
One sentence. Genuinely open. About human stakes. Irreducible — not compound. The story's question, not one character's.

### Compass notes
What the compass leaves open: what about the ending is intentionally unspecified; what the milestones do not determine; which seed questions remain entirely open by design.

---

## Boundary

- **Does not** plot individual scenes, chapters, or sequences.
- **Does not** outline the story.
- **Does not** create character records — that is Character Creation's domain. Character slot sketches are inputs to Character Conception, not character records.
- **Does not** build the world beyond what is minimally implied by the compass. Worldbuilding is a separate skill.
- **Does not** lock the ending.
- **Does not** invoke Character Conception directly — the main agent manages that invocation.
- **Does not** update the World Bible directly. The main agent initialises Modules 2.3 and 2.4 from the final compass.

---

## Invocation

The main agent invokes Defining Rough Endpoints:

- **Pass 1:** Once, immediately after Finding a Seed.
- **Pass 2:** After Character Conception has returned concept documents for all character slots from Pass 1. The main agent passes the concepts back into this skill to produce the final compass.
- **Reassess scenario:** If the Reassess Trigger fires and the compass itself is judged unsound, both passes are re-run with the original seed, original constraints, and a set of preservation constraints derived from already-written material.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** | Nothing (Pass 1 works from seed document; Pass 2 works from seed document + character concept documents) |
| **Main agent writes to** | Module 2.3 — Plot Thread Registry (milestones as initial thread seeds); Module 2.4 — Pending Payoffs & Foreshadowing (milestones as early payoff seeds) |

---

## Dependencies

**Upstream:** **Finding a Seed** (required — validated seed document). Optionally: **Research Integration** (factual grounding for specific domains).  
**Downstream (Pass 1):** Character slot sketches trigger **Character Conception** (early invocation mode) via the main agent.  
**Downstream (Pass 2 / final):** Final compass is the primary input for **Worldbuilding**. Milestones initialise Modules 2.3 and 2.4, subsequently read by **Gardener Plotting System**, **Plot Thread Tracking**, and **Braided Narrative Technique**.

---

## Instructions

### Pass 1

#### Step 1 — Internalise the seed and constraints

Read the seed, its questions, genre, and themes. The compass must feel like a genuine extension of the seed — not a framework imposed on it. Hold the genre constraints: an Epic Fantasy compass looks and feels different from a Hard SF compass or a Historical Fiction compass.

Ask: *What kind of story does this seed want to become? What would it mean for this seed to have found its story?*

#### Step 2 — Determine whether a prologue is warranted

Apply the prologue criteria. If a prologue is warranted, specify it before building the starting situation. Be rigorous: if the material can live in Chapter 1, it should.

#### Step 3 — Orient the starting situation

Describe the world configuration and the central figure(s)' position in it. One paragraph. Specific enough to feel grounded; loose enough that the opening chapter has not been determined. The instability already present must be legible — the reader should feel the argument coming before it starts.

#### Step 4 — Orient the draft ending destination

Specific enough to give direction; vague enough to be discovered. 1–2 sentences. Resist the urge to write more.

#### Step 5 — Identify draft milestones and extract character slots

For each draft milestone, ask: *Who is the person whose presence makes this moment real?* That question produces a character slot.

Write each milestone in 1–3 sentences. Immediately below it, write the character slot sketch. For each slot:
- State the narrative role in the milestone.
- State the implied contradiction (what the seed and compass seem to require of this person internally).
- State the stakes (what they stand to lose or gain here).
- Include the world context available from the compass and seed.
- Write 2–3 open questions about this character that the milestone cannot answer without knowing who they are.

Test each milestone: can it be reached in at least three different ways? If only one path to the milestone is conceivable, pull it back to the underlying necessity.

#### Step 6 — State the draft core conflict question

One sentence. Genuinely open. About human stakes. Irreducible. Test: is this the story's question, or one character's question?

#### Step 7 — Write compass notes

Explicitly record what has been left open. Prevent the compass from hardening into an outline.

#### Step 8 — Return Pass 1 output

Return the full Pass 1 output to the main agent. The main agent invokes Character Conception for each character slot before returning to this skill for Pass 2.

---

### Pass 2

#### Step 9 — Receive character concept documents

The main agent provides one character concept document per slot. Read each: role, core contradiction, one-paragraph sketch, open questions.

#### Step 10 — Revise milestones using character logic

For each draft milestone, ask: *Given who this character actually is — their core contradiction, desire, fear, and response patterns — does this milestone still make sense? Does the character's psychology support it, complicate it, or make it implausible?*

If the character's concept reveals that a draft milestone is implausible (the character would not be in this situation given who they are), revise the milestone to fit the character. If the character's concept reveals that the milestone is less interesting than a different milestone that follows naturally from who this character is, replace it.

The Gardener principle applies: the character wins over the plan.

#### Step 11 — Confirm or revise the core conflict question

Does the story's question still hold now that key characters have been conceived? Does a character's core contradiction sharpen or reframe it? Revise if necessary.

#### Step 12 — Return the final compass

Return the complete final compass (prologue specification if applicable, starting situation, ending destination, milestones with character references, core conflict question, compass notes) to the main agent. The main agent writes Modules 2.3 and 2.4.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning Pass 1 output, verify:

- [ ] Prologue determination is explicit — warranted with specification, or marked absent with reason.
- [ ] Each draft milestone has at least one character slot sketch.
- [ ] Character slot sketches are structured for Character Conception early invocation — role, implied contradiction, stakes, world context, open questions.
- [ ] Milestones are 2–4; each is reachable in at least three different ways.
- [ ] Core conflict question is one sentence, genuinely open, about human stakes.
- [ ] Compass notes record what has been left open.

Before returning Pass 2 (final) output, additionally verify:

- [ ] Each milestone has been reviewed against its conceived character's logic.
- [ ] Any milestone the character concept makes implausible has been revised or replaced.
- [ ] Gardener principle honoured — characters revised milestones, not the other way around.
- [ ] No World Bible writes specified in the skill.
- [ ] No scenes, chapters, or plot sequences produced.
