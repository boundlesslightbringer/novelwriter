---
name: character-conception
description: Generates character concepts using role-first, archetype-subversion, historical inspiration, or "What If?" methods. Identifies the core contradiction that makes the character interesting. Operates in two modes: (1) Standard mode — invoked after Worldbuilding has been persisted; queries Story State KG for political/power map context. (2) Early invocation mode — invoked during the Defining Rough Endpoints two-pass process, before Worldbuilding has run; uses a character slot sketch and world context from the endpoint compass passed in brain context instead. Outputs a character concept document in artifacts in both modes.
---

# Character Conception

## Identity

**Skill name:** `character-conception`
**Purpose:** Generate a character concept — role, core contradiction, and a one-paragraph sketch — before full character construction begins. This is the idea-generation and filtering phase only. Operates in two modes depending on when in the project it is invoked.

---

## Core

Generate a character concept using one of four methods: role-first, archetype-subversion, historical inspiration, or "What If?". Identify the **core contradiction** — the internal tension that makes the character interesting and unpredictable rather than a function of their role. Return the concept in artifacts; do not build psychology, backstory, or plot placement.

---

## Input

### From brain context (`worker_request.context`)

The brain's context dict varies by invocation mode.

#### Standard mode context keys

1. **`narrative_role`** — What story function this character must serve. Required.
2. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required for standard mode.
3. **`thematic_constraints`** (optional) — Thematic or tonal constraints not already visible in Story State records.

#### Early invocation mode context keys

1. **`character_slot_sketch`** — The slot sketch produced by `defining-rough-endpoints` Pass 1. Contains: narrative role in the milestone, implied contradiction, stakes, world context from the endpoint compass, open questions. Required for early invocation mode.
2. **`world_context_sketch`** — A brief description of the political and social landscape implied by the endpoint compass and seed, substituting for the Story State political map which does not yet exist. Required for early invocation mode.
3. **`thematic_constraints`** (optional) — Genre, themes, and thematic interdependencies from the seed document.

### Fetched from Story State KG

#### Standard mode

The character_subagent queries the Story State KG directly to establish world context before generating a concept:

```
# Political and power map — primary world context
query_kg_nodes({type: "Faction"}, as_of_chapter=chapter_context)
query_kg_nodes({type: "Location"}, as_of_chapter=chapter_context)

# Existing characters — to avoid duplicating narrative function
query_kg_nodes({type: "Character"}, as_of_chapter=chapter_context)

# Active plot threads — to understand what narrative gaps exist
query_kg_nodes({type: "PlotThread",
                "properties.status": "Active"},
               as_of_chapter=chapter_context)
```

These queries replace the "World Bible excerpt — Module 3.1" that was previously relayed by the main agent. If any query returns no results, proceed with empty context and note the absence — do not halt.

#### Early invocation mode

No KG queries are made. The Story State KG contains no world data at this stage of the project. World context comes entirely from the `world_context_sketch` in brain context.

---

## Invocation Mode Detection

Determine which mode applies from the brain context:

- If `character_slot_sketch` is present in context → **Early invocation mode**
- If `chapter_context` and `narrative_role` are present (no slot sketch) → **Standard mode**

If neither pattern matches, return `need_input` with a follow-up question requesting the missing fields.

---

## Output

All output is returned in `artifacts`. The brain applies the quality gate and routes the concept document onward to `character-creation` via the next character_subagent delegation.

### `artifacts` structure

```json
{
  "invocation_mode": "standard | early_invocation",
  "character_concept": {
    "assigned_narrative_role": "<what story function this character fills>",
    "generation_method": "<which of the four methods and brief reasoning>",
    "core_contradiction": "<[Drive or value A] / [Drive or value B]>",
    "sketch": "<100–200 word prose paragraph>",
    "open_questions": ["<3–5 questions Character Creation must answer>"]
  },
  "provisional_flag": {
    "present": false,
    "world_context_assumptions": ["<list — early invocation mode only>"],
    "most_likely_to_change": "<which elements — early invocation mode only>",
    "key_information_needed": "<what world context would most change this concept>"
  },
  "kg_context_used": {
    "factions_found": 0,
    "existing_characters_found": 0,
    "active_threads_found": 0,
    "notes": "<any gaps or empty results noted here>"
  }
}
```

`provisional_flag.present` is `true` only in early invocation mode, where the concept was produced before Worldbuilding and may need revision once world records exist in the Story State KG. `kg_context_used` is populated in standard mode to confirm which Story State records informed the concept; left as zero counts in early invocation mode.

---

## Boundary

- **Does not** build psychological depth, core wound, fear/desire architecture, or arc type. That is `character-creation`.
- **Does not** place the character in the plot or assign them to specific events. That is `character-integration-with-plot`.
- **Does not** write scenes or prose involving this character.
- **Does not** generate multiple final candidates for the brain to choose between — returns one concept. If rejected, the brain re-delegates with revised constraints or feedback.
- **Does not** write to the Story State KG. Returns a concept document in artifacts only.
- **In early invocation mode:** does not attempt to fill in world detail that has not been established — works only from what the endpoint compass and seed actually provide, and flags assumptions explicitly in the provisional note.

---

## Invocation

The `character_subagent` invokes this skill when the brain delegates character conception. Two delegation patterns trigger this skill:

**Standard mode:** The brain delegates after Worldbuilding has been persisted to the Story State KG, whenever a new character is needed — new roles, new major figures, elevation of a minor character.

**Early invocation mode:** The brain delegates during the `defining-rough-endpoints` two-pass process — after Pass 1 has produced character slot sketches and before Pass 2 can be completed. The brain delegates one character_subagent invocation per slot sketch, passing the slot sketch and world context sketch in context. The resulting concept documents are passed back to `planning_subagent` for the `defining-rough-endpoints` Pass 2 delegation.

In both modes, this skill is always invoked **before** `character-creation`. It is never skipped.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Standard mode: Faction, Location, Character, and active PlotThread nodes queried with `as_of_chapter` to establish world context and existing cast. Early invocation mode: no queries — Story State KG contains no records at this project stage |
| **Returns in artifacts** | Character concept document; brain passes this as `character_concept` in the context dict of the subsequent `character-creation` delegation |

---

## Dependencies

**Upstream (standard mode):** Worldbuilding records must be persisted in Story State KG — character_subagent queries them directly. Brain provides `narrative_role` and `chapter_context`.

**Upstream (early invocation mode):** Brain provides `character_slot_sketch` and `world_context_sketch` from `defining-rough-endpoints` Pass 1 artifacts. No Story State KG records required.

**Downstream:** Concept document in artifacts is passed by the brain as `character_concept` in context to the next `character-creation` delegation. In early invocation mode, the concept is also passed back to `planning_subagent` for `defining-rough-endpoints` Pass 2.

---

## Instructions

### Step 1 — Identify the invocation mode

Check brain context for `character_slot_sketch`. If present: early invocation mode. Otherwise: standard mode.

In standard mode, query the Story State KG as specified. Note any empty results — a new project may have no existing characters, which is expected.

In early invocation mode, read the slot sketch carefully. Note what the endpoint compass and seed have established about the world. Note what has *not* been established — these are the assumptions to flag in the provisional note.

### Step 2 — Review the narrative requirement

Read the brain context's narrative role (standard mode) or the slot sketch's narrative role (early invocation mode). Identify what gap in the story's power map, faction structure, or POV landscape this character must fill. Do not invent a character who duplicates an existing character's narrative function — check the existing Character nodes returned by the KG query.

In early invocation mode, the "power map" is the world sketch from the compass and seed — thinner, but workable. Focus on the milestone's specific needs and the story's thematic logic.

### Step 3 — Select a generation method

Choose the method most suited to the narrative requirement and existing cast:

- **Role-First:** Begin with the story function, then ask what kind of *person* — not archetype — would hold that role and have survived in it. Work inward from the role to the human.
- **Archetype-Subversion:** Identify the most expected version of this character. List expected attributes. Invert or complicate three of them in ways that are internally coherent — the result must feel earned, not contrarian.
- **Historical Inspiration:** Draw on a real historical figure (or, for speculative genres, a fictional precedent) whose situation rhymes with the story's needs. Extract the structural pattern without copying biography. Synthesise with the world's specific context.
- **"What If?":** Pose a specific character question and follow the logic of who that person would have to be.

### Step 4 — Find the core contradiction

The core contradiction is not a quirk or a flaw. It is a genuine internal conflict between two things the character cannot reconcile. Test: *If this character is pushed to the limit, which side wins? And what does it cost them?* If that question cannot be answered, the contradiction is not yet real.

In early invocation mode, the slot sketch provides an *implied* contradiction — a hypothesis. This may be confirmed, refined, or replaced. Treat it as a starting hypothesis, not a locked specification.

State the contradiction as: **[Drive or value A] / [Drive or value B]** — one line.

### Step 5 — Write the one-paragraph sketch

100–200 words. Convey this character's presence and the shape of their contradiction without explaining either directly. Use concrete detail, not abstraction. Prose only — no bullet points, no trait lists.

### Step 6 — Generate open questions

3–5 questions the concept raises that `character-creation` must answer. Probe: the origin of the contradiction, what the character wants on the surface vs. what they actually need, where loyalty breaks or self-deception is most dangerous, how the contradiction might evolve across a long arc.

### Step 7 — Write the provisional flag (early invocation mode only)

Identify:
- Which elements of the concept rest on world-context assumptions not yet established by Worldbuilding.
- Which assumptions are most likely to change once world records exist in the Story State KG.
- What specific world-context information would most change the concept if it turned out differently than assumed.

### Step 8 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. In standard mode, populate `kg_context_used` with the counts of records found. In early invocation mode, set counts to zero and ensure `provisional_flag.present = true`.

---

## Example

For worked examples of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Invocation mode was correctly identified from the context.
- [ ] In standard mode: KG queries were made; `kg_context_used` is populated.
- [ ] Core contradiction is a genuine internal conflict, not a quirk or tragic flaw label.
- [ ] Sketch is prose — no bullet points, no trait lists.
- [ ] Character does not duplicate an existing character's narrative function (checked against KG Character nodes in standard mode).
- [ ] No psychological depth, backstory, or arc specification added.
- [ ] Open questions are genuinely open — they probe, they do not answer.
- [ ] In early invocation mode: provisional flag is present, specific, and actionable; no world-context details were invented beyond what the compass and seed actually establish.
- [ ] No Story State KG writes from this skill.