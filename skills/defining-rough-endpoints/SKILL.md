---
name: defining-rough-endpoints
description: Establishes the story's compass — starting situation (with optional prologue), vague ending destination, 2–4 major milestones, and the core conflict question — from the validated seed. Because milestones naturally involve key characters who do not yet exist, this skill outputs character slot sketches alongside the compass; the brain then delegates to character_subagent for each slot before milestones are finalised. Invoked once (Pass 1) immediately after finding-a-seed, and again (Pass 2) after the brain returns character concepts. The planning_subagent writes to Story State Modules 2.3 and 2.4 via story_state_manager.
---

# Defining Rough Endpoints

## Identity

**Purpose:** Give the story a compass, not a map. Establish where the story begins (including whether a prologue is needed), where it vaguely ends, what major shape-moments lie between, and what single question the entire story is trying to answer. Because milestones naturally imply characters, and characters do not yet exist at this stage, this skill works in two passes via the brain: a first pass produces draft milestones with character slot sketches; the brain delegates to `character_subagent` for each slot; a second pass refines the milestones using the conceived characters' logic. The endpoint compass is a direction, not a plan.

---

## Core

Establish the story's compass: starting situation (with optional prologue specification), vague ending destination, 2–4 major milestones, and the core conflict question. Milestones naturally involve characters — this skill outputs character slot sketches to enable early Character Conception invocation by the brain, then incorporates the resulting character concepts to ensure milestones are grounded in character logic rather than abstract story structure. Endpoints are intentionally loose and will shift as the story grows. Do not plot individual scenes or chapters. Do not outline.

---

## Input

### From brain context (`worker_request.context`)

#### Pass 1 (required)

1. **`seed_document`** — The full seed document from the `finding-a-seed` artifacts of the prior delegation. Contains: seed statement, generation method, validation record, genre, subgenres, themes, thematic interdependencies, and questions.

2. **`research_output`** (optional) — Structured research notes from a prior `research-integration` delegation, if the brain judged that factual grounding was needed before the compass could be oriented.

3. **`thematic_constraints`** (optional) — Any additional thematic or tonal constraints not captured in the seed document.

#### Pass 2 (required to finalise milestones)

4. **`character_concepts`** — A list of character concept documents, one per character slot produced in Pass 1. These are returned by the brain after it has delegated each slot to `character_subagent` and collected the resulting concepts. Used to refine draft milestones so that milestone logic flows from character psychology, not structural convenience.

5. **`pass_1_output`** — The draft compass output from Pass 1, passed back by the brain so this skill can refine it without re-running the full Pass 1 logic.

### Fetched from Story State KG

None in the standard case. If the brain delegates this skill during a **Reassess** scenario (the Reassess Trigger has fired and the compass is being re-evaluated), the planning_subagent queries existing Story State records for context:

```
query_kg_nodes({type: "PlotThread"})      → existing thread seeds
query_kg_nodes({type: "Chapter"})          → how many chapters written
query_kg_nodes({type: "Character"})        → existing characters to preserve
```

These reassess queries use `as_of_chapter` equal to the last written chapter so the worker sees story state at the correct narrative position.

---

## Output

All output is returned in `artifacts`. The brain routes persistence to `story_state_manager`.

### Pass 1 artifacts

```json
{
  "pass": 1,
  "prologue_specification": {
    "warranted": true,
    "temporal_relationship": "<how far before Chapter 1>",
    "pov_or_register": "<whose perspective or what register>",
    "what_it_establishes": "<what the reader must carry into Ch. 1>",
    "what_it_withholds": "<what it implies but does not explain>",
    "relationship_to_milestones": "<whether it is itself a milestone or a precondition>"
  },
  "starting_situation": "<one paragraph>",
  "draft_ending_destination": "<1–2 sentences>",
  "draft_milestones": [
    {
      "milestone_id": "M1",
      "description": "<1–3 sentences>",
      "character_slots": ["slot_A", "slot_B"]
    }
  ],
  "character_slot_sketches": [
    {
      "slot_id": "slot_A",
      "narrative_role": "<what story function this character must serve>",
      "implied_contradiction": "<hypothesis from seed and compass>",
      "stakes": "<what they stand to lose or gain>",
      "world_context": "<relevant context from seed and compass>",
      "open_questions": ["<2–3 questions>"]
    }
  ],
  "draft_core_conflict_question": "<one sentence>",
  "compass_notes": "<what has been left open>"
}
```

### Pass 2 artifacts (final compass)

```json
{
  "pass": 2,
  "prologue_specification": "...",
  "starting_situation": "...",
  "ending_destination": "<refined or confirmed>",
  "milestones": [
    {
      "milestone_id": "M1",
      "description": "<refined using character logic>",
      "character_references": ["<conceived character name/id>"]
    }
  ],
  "core_conflict_question": "<confirmed or revised>",
  "compass_notes": "...",
  "plot_thread_seeds": [
    {
      "node_type": "PlotThread",
      "properties": {
        "name": "<milestone as initial thread>",
        "status": "Active",
        "originating_chapter": 0
      }
    }
  ],
  "payoff_seeds": [
    {
      "node_type": "Payoff",
      "properties": {
        "type": "Foreshadowing",
        "description": "<milestone as early payoff seed>",
        "planted_in_chapter": 0,
        "resolution_status": "Pending"
      }
    }
  ]
}
```

The `plot_thread_seeds` and `payoff_seeds` arrays are structured as KG node records ready for `story_state_manager` to insert directly.

---

## Boundary

- **Does not** plot individual scenes, chapters, or sequences.
- **Does not** outline the story.
- **Does not** create character records — character slot sketches are inputs to `character_subagent` via the brain, not character records.
- **Does not** build the world beyond what is minimally implied by the compass. Worldbuilding is a separate skill.
- **Does not** lock the ending.
- **Does not** delegate to `character_subagent` directly — the brain manages that delegation between passes.
- **Does not** write to the Story State KG. Returns structured records in artifacts for persistence by `story_state_manager`.

---

## Invocation

The `planning_subagent` invokes this skill in two passes, each triggered by a separate brain delegation:

- **Pass 1:** Brain delegates immediately after `finding-a-seed` completes and its artifacts pass the quality gate. The brain includes the seed document in context.
- **Pass 2:** Brain delegates after it has collected character concept documents from `character_subagent` (one per slot produced in Pass 1) and includes them in context alongside the Pass 1 output.
- **Reassess scenario:** If the Reassess Trigger fires and the compass is judged unsound, the brain re-delegates both passes with the original seed, original constraints, and preservation constraints derived from already-written material.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | None in standard flow. In reassess scenario: PlotThread, Chapter, and Character nodes queried to establish preservation constraints |
| **Returns in artifacts** | Pass 1: draft compass + character slot sketches. Pass 2: final compass + `plot_thread_seeds` and `payoff_seeds` as KG-ready node records for `story_state_manager` to insert into Modules 2.3 and 2.4 |

---

## Dependencies

**Upstream:** Brain provides `seed_document` from prior `finding-a-seed` artifacts. Pass 2 additionally requires `character_concepts` collected by the brain from `character_subagent` delegations (one per slot).

**Downstream:** Pass 1 artifacts include character slot sketches; the brain uses these to delegate individual character conception tasks to `character_subagent`. Pass 2 artifacts include the final compass and KG-ready records; the brain routes these to `story_state_manager` for persistence, then delegates `worldbuilding` to `planning_subagent` using the final compass as context.

---

## Prologue Specification

When the seed or the story's structural needs suggest a prologue — a chapter that precedes the main narrative, operating at a different point in time, from a different perspective, or at a different narrative register — the prologue must be specified in the starting situation section.

A prologue is warranted when one or more of the following apply:
- The story's core tension is better *felt* before the main narrative begins than explained within it.
- A significant prior event (a death, a founding, an act of betrayal) needs to be rendered rather than referenced in backstory.
- A POV character or perspective that will not recur in the main narrative can establish something essential at the outset.
- The genre or tonal register of the story benefits from a threshold moment before Chapter 1.

A prologue is **not** warranted simply to provide exposition or worldbuilding context. If the material can be integrated into Chapter 1 or later chapters through the natural filter of a POV character, it should be.

---

## Character Slot Sketches and the Two-Pass Process

### The problem

Milestones are not abstract narrative events — they are moments in which specific people make choices, collide, or are broken by circumstances. A milestone without a character is a structural hypothesis, not a story event. But characters do not yet exist at the point this skill is first invoked.

### The solution

**Pass 1 — Draft milestones with character slots:**
Each draft milestone names the character *type* (role, implied contradiction, implied stakes) without creating a character record. This role description is output as a **character slot sketch** structured for early invocation of Character Conception by the brain.

**Brain delegation — Early Character Conception:**
The brain delegates to `character_subagent` for each slot, passing the slot sketch as the primary context. `character_subagent` operates in early invocation mode (see character-conception skill), using the world context implied by the endpoint compass in place of a fully populated Story State.

**Pass 2 — Refine milestones with conceived characters:**
The brain returns the character concept documents to this skill via `worker_request.context`. Draft milestones are refined: abstract role descriptions are replaced with characters whose specific psychology, core contradiction, and desires now drive the milestone logic.

> **Gardener principle:** Characters are not assigned to milestones — milestones are revised to fit the characters who have been conceived. If a conceived character's logic points away from a draft milestone, the character wins.

---

## Instructions

### Pass 1

#### Step 1 — Internalise the seed and constraints

Read the seed document from context. The compass must feel like a genuine extension of the seed — not a framework imposed on it. Hold the genre constraints: an Epic Fantasy compass looks and feels different from a Hard SF compass or a Historical Fiction compass.

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

#### Step 8 — Return Pass 1 artifacts

Return the full Pass 1 artifacts dict with `status: "success"`. The brain will delegate to `character_subagent` for each character slot before returning for Pass 2.

---

### Pass 2

#### Step 9 — Receive character concept documents

The brain provides `character_concepts` in context — one document per slot. Read each: role, core contradiction, one-paragraph sketch, open questions.

#### Step 10 — Revise milestones using character logic

For each draft milestone, ask: *Given who this character actually is — their core contradiction, desire, fear, and response patterns — does this milestone still make sense? Does the character's psychology support it, complicate it, or make it implausible?*

If the character's concept reveals that a draft milestone is implausible, revise the milestone to fit the character. If the character's concept reveals that the milestone is less interesting than a different milestone that follows naturally from who this character is, replace it.

The Gardener principle applies: the character wins over the plan.

#### Step 11 — Confirm or revise the core conflict question

Does the story's question still hold now that key characters have been conceived? Does a character's core contradiction sharpen or reframe it? Revise if necessary.

#### Step 12 — Build KG-ready persistence records

Construct `plot_thread_seeds` and `payoff_seeds` arrays from the finalised milestones, structured as KG node records ready for `story_state_manager` to insert.

#### Step 13 — Return Pass 2 artifacts

Return the complete final compass artifacts dict with `status: "success"`. The brain routes the KG-ready records to `story_state_manager` for persistence.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

### Pass 1 — before returning

- [ ] Prologue determination is explicit — warranted with specification, or absent with reason.
- [ ] Each draft milestone has at least one character slot sketch.
- [ ] Character slot sketches are structured for Character Conception early invocation — role, implied contradiction, stakes, world context, open questions.
- [ ] Milestones are 2–4; each is reachable in at least three different ways.
- [ ] Core conflict question is one sentence, genuinely open, about human stakes.
- [ ] Compass notes record what has been left open.

### Pass 2 — additionally

- [ ] Each milestone has been reviewed against its conceived character's logic.
- [ ] Any milestone the character concept makes implausible has been revised or replaced.
- [ ] Gardener principle honoured — characters revised milestones, not the other way around.
- [ ] `plot_thread_seeds` and `payoff_seeds` are structured as valid KG node records.
- [ ] No Story State KG writes from this skill — records in artifacts for story_state_manager.
- [ ] No scenes, chapters, or plot sequences produced.