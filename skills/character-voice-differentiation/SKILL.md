---
name: character-voice-differentiation
description: Defines a distinct narrative voice profile for each POV character — vocabulary range, sentence structure patterns, observational focus, internal thought patterns, and emotional processing style. Invoked after character-creation has been persisted for a character who will serve as a POV. Queries Story State KG for the character's full psychological record and existing voice profiles. Returns a voice profile document in artifacts for persistence into the Character node in Story State.
---

# Character Voice Differentiation

## Identity

**Purpose:** Produce a concrete, usable voice profile for a POV character that makes their chapters feel unmistakably distinct from every other POV — not through affectation or dialect tricks, but through authentic differences in how this specific person perceives, processes, and narrates the world.

---

## Core

Define a distinct narrative voice profile for each POV character. The profile covers: vocabulary range, sentence structure patterns, observational focus (what this character notices and in what order), internal thought patterns, and emotional processing style. The profile is derived entirely from the character's psychology — voice is the surface expression of interiority, not a stylistic overlay. Return the voice profile in artifacts; do not write scenes.

---

## Input

### From brain context (`worker_request.context`)

1. **`character_id`** — The `logical_id` of the Character node to build a voice profile for (e.g. `char_caradhen`). Required.
2. **`chapter_context`** — Current chapter number for KG query scoping. Required.
3. **`research_output`** (optional) — Research notes from a prior `research-integration` delegation, if the character's cultural or social context (e.g. non-literate culture, scholarly background, military formation) affects vocabulary and cognitive patterns.

### Fetched from Story State KG

The character_subagent queries the Story State KG directly to assemble all inputs this skill requires:

```
# Full psychological record for the target character
query_kg_nodes({logical_id: character_id, type: "Character"},
               as_of_chapter=chapter_context)

# Culture the character belongs to — affects vocabulary and cognitive style
query_kg_edges({from_node: character_id, type: "BELONGS_TO_CULTURE"},
               as_of_chapter=chapter_context)
# Then fetch the Culture node(s) returned by the above edge query

# All existing POV character voice profiles — for differentiation
# (POV-eligible characters who already have a voice_profile property)
query_kg_nodes({type: "Character",
                "properties.pov_eligible": true},
               as_of_chapter=chapter_context)
```

The existing voice profiles are retrieved from the `properties` of other POV-eligible Character nodes (stored as `properties.voice_profile` after prior invocations of this skill). If no other profiles exist yet, proceed without differentiation notes — this is the first POV voice profile for this project.

---

## Output

All output is returned in `artifacts`. The brain routes the voice profile to `story_state_manager`, which updates the Character node by merging `voice_profile` into `properties` as a sub-record.

### `artifacts` structure

```json
{
  "character_id": "char_<slug>",
  "voice_profile": {
    "vocabulary_range": {
      "lexical_register": "<formal | informal | mixed; latinate | germanic | dialect>",
      "signature_vocabulary_categories": ["<type of words this character reaches for>"],
      "avoids": ["<vocabulary categories this character would not use>"]
    },
    "sentence_structure_patterns": {
      "default_sentence_length": "<short and declarative | long and subordinated | varied and controlled>",
      "structural_habits": "<patterns the character's narration tends to fall into>",
      "under_stress": "<how sentence structure changes in crisis, danger, or grief>"
    },
    "observational_focus": {
      "primary_lens": "<dominant filter through which this character reads any scene>",
      "secondary_lens": "<secondary filter>",
      "systematic_blind_spots": "<what this character fails to register or systematically misreads>",
      "how_they_read_people": "<what they look at first in another person>"
    },
    "internal_thought_patterns": {
      "deliberative_style": "<step-by-step | instinct-first | mixed>",
      "self_monitoring": "<do they examine their own motivations; are they accurate when they do>",
      "memory_intrusion": "<how and when the past surfaces in narration>",
      "relationship_to_time": "<present-focused | past-oriented | future-oriented>"
    },
    "emotional_processing_style": {
      "speed_of_acknowledgment": "<how quickly this character consciously registers emotion>",
      "internal_expression": "<how emotion surfaces in narration>",
      "what_they_cannot_look_at": "<emotional territory they cannot directly narrate>",
      "under_extreme_pressure": "<how emotional processing changes at their limit>"
    },
    "differentiation_notes": [
      {
        "risk_pairing": "<this character> / <other POV character>",
        "drift_risk": "<where their voices most risk sounding alike>",
        "techniques": ["<2–3 specific differentiation techniques>"]
      }
    ]
  },
  "kg_context_used": {
    "character_node_found": true,
    "culture_found": true,
    "existing_pov_profiles_found": 0
  }
}
```

`differentiation_notes` is populated for each existing POV character whose voice overlaps most with this one. If no other POV profiles exist, this array is empty.

The `voice_profile` object is structured to be stored as `properties.voice_profile` on the Character node via an `update_kg_node` call by `story_state_manager`. This keeps the voice profile co-located with the psychological record it is derived from, and allows `writing_subagent` to retrieve both in a single `query_kg_nodes` call.

---

## Boundary

- **Does not** create the character. `character-creation` must be persisted before this skill is invoked.
- **Does not** write sample scenes or prose demonstrations. The voice profile is a reference document, not a sample chapter.
- **Does not** make plot decisions or place the character in specific scenes.
- **Does not** define character psychology beyond what is already in the persisted Character node — it translates existing psychology into narrative voice. If the Character node is thin, this skill cannot compensate.
- **Does not** write to the Story State KG. Returns the voice profile in artifacts for `story_state_manager` to merge into the Character node.

---

## Invocation

The `character_subagent` invokes this skill when the brain delegates voice profile construction:

- After `character-creation` artifacts have been persisted to the Story State KG for a character who will serve as a POV (i.e. `pov_eligible: true` in their Character node).
- Before that character's first POV chapter is written by `writing_subagent`.
- When the brain suspects voice drift has occurred across many chapters and re-delegates to re-anchor the profile.

This skill is not invoked for non-POV characters.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node (full psychological record, `as_of_chapter`); BELONGS_TO_CULTURE edge and the Culture node it links to; all POV-eligible Character nodes (to retrieve existing voice profiles from `properties.voice_profile` for differentiation) |
| **Returns in artifacts** | `voice_profile` object structured for merge into the Character node's `properties` via `story_state_manager`; brain routes the update as `update_kg_node` call to persist the sub-record |

---

## Dependencies

**Upstream:** Character node must be persisted in Story State KG — character_subagent queries it directly. Brain provides `character_id` and `chapter_context`.

**Downstream:** Voice profile is stored in the Character node and retrieved by `writing_subagent` via `query_kg_nodes` when constructing scenes, and by `writing_subagent` when running `pov-consistency-maintenance` audits.

---

## Instructions

### Step 1 — Query the Story State KG

Fetch the Character node, its Culture association, and existing POV voice profiles using the specified queries. If the Character node is not found, return `need_input` with a follow-up question — the node must be persisted before this skill can run.

### Step 2 — Read the full psychological record before touching voice

Before considering vocabulary or syntax, read the full Character node properties: core wound, desire, fear, self-deception, values under pressure, response patterns, arc type. Voice is not a stylistic choice — it is the psychological record expressed as narration. Do not proceed to voice construction until the interiority is fully understood.

### Step 3 — Derive vocabulary from psychology and social position

A character who grew up in a mercantile family in a port city has a different vocabulary pool than a character raised in a highland clan. Derive the lexical register from the Culture node's `core_values`, `class_structure`, and `languages_dialects` fields, and from the Character node's `occupation`, `faction`, and `rank`. Do not impose a register that feels characterful but is not grounded in the character's actual formation.

### Step 4 — Derive sentence structure from cognitive style

The character's deliberative style (from `response_patterns` and psychological record) determines sentence structure. A character who reasons step-by-step tends toward longer, more qualified sentences. A character who moves by instinct and acts first tends toward shorter, more declarative sentences. Map the character's default cognitive rhythm onto a sentence structure pattern, then specify how that pattern changes under stress.

### Step 5 — Define the observational lens precisely

This is the section most likely to be done lazily and to produce the most damage if it is. "She notices power dynamics" is not sufficient. Specify:
- The first thing they clock in a new person (status? threat? emotional state? physical capability? wealth marker?)
- The first thing they clock in a new physical space (exits? people? objects of value? signs of decay?)
- What they almost never notice, or systematically misread, because their primary lens blocks it.

The blind spots produce dramatic irony. They are the POV filter working as it should.

### Step 6 — Map internal thought and memory patterns

Specify whether this character's internal narration includes:
- Explicit self-analysis (they examine their own motivations in narration)
- Implicit self-analysis (they narrate around their motivations; the reader infers)
- Active self-deception in narration (they tell themselves a story that is demonstrably wrong)

Memory: specify the conditions under which past events surface (sensory triggers? structural parallels? certain persons or places?), or whether the past almost never intrudes.

### Step 7 — Specify emotional processing for the character's key emotional territory

Every character has emotional material they cannot look at directly. Identify what it is for this character (derived from the core wound and self-deception in their Character node). Specify how narration *behaves* when it approaches that territory — acceleration, deflection to external observation, sudden flatness, intrusion of physical sensation without interpretation. This is what makes emotional scenes feel distinct per POV.

### Step 8 — Write differentiation notes for overlapping POV profiles

Review the existing POV voice profiles retrieved from other Character nodes. For each character whose voice overlaps most with this one, identify:
- Where the overlap risk is highest (similar registers, similar observational foci)
- Two or three specific differentiation techniques

If no other POV profiles exist, skip this step.

### Step 9 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. Populate `kg_context_used` with query results. The voice profile is structured for direct merge into the Character node's `properties` by `story_state_manager`.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Character node was found in KG before proceeding; `kg_context_used.character_node_found = true`.
- [ ] Every element of the voice profile is derived from the Character node's psychological record — nothing imposed from outside.
- [ ] Observational blind spots are specified, not just observational strengths.
- [ ] Emotional processing covers what the character cannot look at, not just how they feel.
- [ ] `under_stress` sentence pattern differs meaningfully from the default pattern.
- [ ] No prose samples or demonstration scenes written.
- [ ] Differentiation notes present for each overlapping POV character found in KG (or array empty with reason if none found).
- [ ] The profile is specific to this character — no element could be lifted and applied to a generic character type.
- [ ] No Story State KG writes from this skill — voice profile returned in artifacts for story_state_manager.