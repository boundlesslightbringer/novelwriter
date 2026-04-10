---
name: character-creation
description: Builds the full character iceberg from a character concept — visible surface (physical, social) and the hidden 90% (core wound, fears, desires, arc type, contradictions, values, response patterns). Invoked by the character_subagent after character-conception has produced a validated concept. Queries Story State KG for world context if building against an established world. Returns a complete character record in artifacts structured for persistence via story_state_manager into Story State Modules 1.1, 1.2, and 1.3.
---

# Character Creation

## Identity

**Purpose:** Transform a character concept into a fully developed character using the iceberg principle. Build everything — ten times more than will appear on the page — so that what does appear is supported by a fully realised interior life. Return KG-ready records in artifacts for Story State Modules 1.1, 1.2 (initial entries), and 1.3 (initial entries).

---

## Core

Build the full character iceberg from an already-conceived character concept. The visible surface is physical description and social context. The hidden 90% is the psychological interior: core wound, fears, desires, arc type, contradictions, values under pressure, and response patterns across event categories. Return KG-ready node and edge records in artifacts. Do not place the character in the plot.

---

## Input

### From brain context (`worker_request.context`)

1. **`character_concept`** — The full concept document from `character-conception` artifacts of the prior delegation. Contains: assigned narrative role, generation method, core contradiction, sketch, open questions, provisional flag (if early invocation), `kg_context_used`. Required.

2. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required.

3. **`research_output`** (optional) — Structured research notes from a prior `research-integration` delegation, if the character's social role (e.g. a specific religious order, military rank, cultural practice) requires factual grounding for authenticity.

4. **`feedback`** (optional) — Correction directive from the brain if this is a re-delegation after a rejected artifact. The brain passes specific issues identified during the quality gate; this skill addresses them in the revised output.

### Fetched from Story State KG

The character_subagent queries the Story State KG to ground the character record in the established world:

```
# World context for social position and faction placement
query_kg_nodes({type: "Faction"}, as_of_chapter=chapter_context)
query_kg_nodes({type: "Culture"}, as_of_chapter=chapter_context)
query_kg_nodes({type: "Location"}, as_of_chapter=chapter_context)

# Existing characters — for pre-story relationship records (Module 1.3)
query_kg_nodes({type: "Character"}, as_of_chapter=chapter_context)

# Existing knowledge items — to initialise knowledge matrix sensibly
query_kg_nodes({type: "KnowledgeItem"}, as_of_chapter=chapter_context)
```

If the concept was produced in early invocation mode (world records do not yet exist), these queries will return empty results. Proceed with empty context — the `provisional_flag` in the concept document already notes this. Initial Module 1.2 and 1.3 entries will be minimal and flagged for expansion after Worldbuilding is persisted.

---

## Output

All output is returned in `artifacts` as KG-ready records, structured for direct insertion by `story_state_manager`. The brain applies the quality gate before routing to `story_state_manager`.

### `artifacts` structure

```json
{
  "character_node": {
    "logical_id": "char_<slug>",
    "node_type": "Character",
    "chapter": 0,
    "properties": {
      "full_name": "<including titles and aliases>",
      "aliases": ["<list>"],
      "age": 0,
      "gender": "<string>",
      "physical_description": "<what is immediately observable; what is habitually overlooked>",
      "faction": "<faction name>",
      "rank": "<title or role>",
      "occupation": "<string>",
      "public_vs_private_reputation": "<how they are seen vs. who they are>",
      "location": "<starting location>",
      "surface_beliefs": ["<what the character says they believe>"],
      "core_wound": "<specific event and the conclusion the character drew from it>",
      "core_desire": "<what they want above all other things>",
      "core_fear": "<what threatens to reopen the wound>",
      "self_deception": "<what they believe about themselves that is false>",
      "values_under_pressure": ["<stated values vs. actual behaviour under real cost>"],
      "contradictions": ["<specific behavioural contradictions, not trait labels>"],
      "response_patterns": {
        "betrayal": "<how they respond>",
        "loss": "<how they respond>",
        "sudden_power": "<how they respond>",
        "helplessness": "<how they respond>",
        "unwanted_intimacy": "<how they respond>",
        "being_correctly_seen": "<how they respond>",
        "unexpected_kindness_from_enemy": "<how they respond>"
      },
      "arc_type": "Transformation | Revelation | Corruption | Disintegration | Steadfastness",
      "arc_stage": "<where in the arc they begin>",
      "pov_eligible": true,
      "pov_chapter_count": 0,
      "last_pov_chapter": null,
      "injuries_physical_state": [],
      "emotional_state": "<dominant emotional state at story start>"
    }
  },
  "knowledge_matrix_edges": [
    {
      "logical_id": "knows_<char_slug>_<item_slug>",
      "edge_type": "KNOWS",
      "from": "char_<slug>",
      "to": "ki_<slug>",
      "chapter": 0,
      "properties": {
        "status": "KNOWS | BELIEVES | SUSPECTS | DOES NOT KNOW",
        "acquired_at_chapter": 0,
        "source": "<how they came to know this>",
        "dramatic_irony_flag": false
      }
    }
  ],
  "knowledge_items": [
    {
      "logical_id": "ki_<slug>",
      "node_type": "KnowledgeItem",
      "chapter": 0,
      "properties": {
        "description": "<the specific fact, secret, or belief>"
      }
    }
  ],
  "relationship_edges": [
    {
      "logical_id": "rel_<char_a_slug>_<char_b_slug>",
      "edge_type": "RELATIONSHIP",
      "from": "char_<slug>",
      "to": "char_<other_slug>",
      "chapter": 0,
      "properties": {
        "emotional_valence": "<love | hate | fear | debt | respect | contempt | loyalty | distrust | etc.>",
        "power_dynamic": "<who holds leverage and why>",
        "history": "<formative events and turning points>",
        "secrets_kept": ["<what this character conceals from the other>"],
        "trajectory": "Stable | Deteriorating | Evolving | Volatile",
        "convergence_potential": "<whether and when direct contact is likely>",
        "most_recent_interaction": null
      }
    }
  ],
  "culture_edge": {
    "logical_id": "culture_<char_slug>",
    "edge_type": "BELONGS_TO_CULTURE",
    "from": "char_<slug>",
    "to": "culture_<slug>",
    "chapter": 0,
    "properties": {
      "role": "<their role within this culture>"
    }
  },
  "arc_type_note": "<reasoning for the assigned arc type — hypothesis, not locked outcome>",
  "provisional_expansion_flag": false,
  "provisional_expansion_notes": "<present only if early invocation; notes which fields need expansion after Worldbuilding>"
}
```

**Logical ID convention:**
- Character: `char_<firstname_lastname_slug>` e.g. `char_jon_snow`
- KnowledgeItem: `ki_<brief_description_slug>` e.g. `ki_cersei_execution_plan`
- KNOWS edge: `knows_<char_slug>_<item_slug>`
- RELATIONSHIP edge: `rel_<char_a_slug>_<char_b_slug>`

`relationship_edges` covers only **pre-story relationships** established in the concept document or visible in existing Character nodes. Active-story relationship entries are added by `character-integration-with-plot`. `knowledge_matrix_edges` covers only background facts and established false beliefs at story start.

---

## Boundary

- **Does not** generate a character concept. `character-conception` must run first.
- **Does not** place the character in plot events, assign them to scenes, or define their role in specific story beats. That is `character-integration-with-plot`.
- **Does not** write prose featuring this character.
- **Does not** define narrative voice or POV register. That is `character-voice-differentiation`.
- **Does not** write to the Story State KG. Returns KG-ready records in artifacts for `story_state_manager` to insert.

---

## Invocation

The `character_subagent` invokes this skill when the brain delegates full character construction, immediately after `character-conception` artifacts have passed the quality gate and the concept document is available in context.

This skill is always invoked after `character-conception`. It is never invoked without a concept document.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Faction, Culture, Location nodes (world context for social position); Character nodes (for pre-story relationship records); KnowledgeItem nodes (to initialise knowledge matrix sensibly). All queried with `as_of_chapter`. Empty results are expected and handled at project start |
| **Returns in artifacts** | KG-ready Character node record; KnowledgeItem node records; KNOWS edge records (Module 1.2 initial entries); RELATIONSHIP edge records (Module 1.3 initial entries); BELONGS_TO_CULTURE edge record. Brain routes to `story_state_manager` for persistence |

---

## Dependencies

**Upstream:** Brain provides `character_concept` from prior `character-conception` artifacts. Brain provides `chapter_context` for KG query scoping.

**Downstream:** Persisted Character node enables `character-voice-differentiation` (reads Character node properties via KG query) and `character-integration-with-plot` (reads full character records and relationship records).

---

## Instructions

### Step 1 — Answer the open questions from the concept

The concept document includes 3–5 open questions. Answer each one before building the character record. These answers are the foundation of the iceberg. Push toward specificity and toward answers that complicate the character rather than resolve them.

### Step 2 — Query the Story State KG

Run the specified queries with `as_of_chapter = chapter_context`. Review:
- Faction nodes: what social positions and power structures exist to place this character within
- Culture nodes: which culture does this character belong to; what does membership mean for them
- Character nodes: which existing characters have pre-story relationships with this one
- KnowledgeItem nodes: which existing knowledge items does this character have access to at story start

If early invocation mode is indicated by `provisional_flag.present = true` in the concept, these queries will return empty results. Note this and proceed.

### Step 3 — Build the core wound

The core wound is not a backstory event. It is a specific experience and the **conclusion** the character drew from it. That conclusion shapes every subsequent choice. The conclusion may be wrong — it often is. Record:

- What happened (specific; not categorical).
- What the character concluded about themselves, other people, or the world as a result.
- How that conclusion has been *useful* — core wounds persist because they protect something.

### Step 4 — Derive desire, fear, and self-deception from the wound

The core wound produces:
- **Core desire:** What the character is trying to get or become so that wound is never reopened.
- **Core fear:** What threatens to reopen it.
- **Self-deception:** What they must believe about themselves to pursue the desire without confronting the fear directly.

These three must be internally consistent and derived from the wound — not selected from a list of interesting traits.

### Step 5 — Build the visible surface

Physical description: what is immediately observable, and what is habitually overlooked or misread by others. Avoid a list of physical attributes; focus on what the character's body communicates and conceals.

Social position: what role they occupy, what reputation precedes them, and where reality diverges from reputation. Ground this in the Faction and Location nodes returned by the KG query.

### Step 6 — Define values under pressure and contradictions

Identify two or three moments of type — situations where this character would say one thing and do another, not out of hypocrisy but out of genuine conflict between their stated self and their actual psychology. State these as contradictions, not as hypocrisy. The character may not be aware of them.

### Step 7 — Map response patterns

For each of the seven event categories, specify how this specific character — not a type, not a role — would respond. These patterns will be used by `gardener-plotting-system` and `scene-construction` to ensure character-driven decisions remain consistent under extreme pressure.

### Step 8 — Assign arc type and starting stage

Select the arc type that best fits the character's setup and state where they begin. Be explicit that this is a hypothesis — the Gardener principle means character logic overrides arc planning. Record the reasoning so it can be revisited if the arc evolves.

### Step 9 — Build initial knowledge matrix entries

Construct KnowledgeItem nodes and KNOWS edges for:
- **KNOWS entries:** Background facts the character knows — their own history, the political situation as they understand it at story start.
- **BELIEVES (possibly false) entries:** The character's self-deception and any established false beliefs about the world as formal BELIEVES entries, so KG contradiction detection can flag violations later.

Leave SUSPECTS and DOES NOT KNOW entries blank at creation; these are populated as story events occur.

### Step 10 — Record pre-story relationship edges

For every significant pre-existing relationship — visible in existing Character nodes or established in the concept document — construct a RELATIONSHIP edge record. Include: other character logical_id, valence, power dynamic, history, secrets kept. Leave trajectory field minimal; `character-integration-with-plot` expands these.

Relationship edges are directional. If building two records (A→B and B→A), include both in `relationship_edges`.

### Step 11 — Assemble and return artifacts

Assemble the full artifacts dict with all KG-ready records. Set status to one of the allowed worker status values only: `success`, `need_input`, `blocked`, or `failed` (use `success` for complete outputs).

All required nested fields must be non-null. If a value is unknown, use an empty string `""` or empty array `[]`, not `null`.

If this was built in early invocation context (empty world records), set `provisional_expansion_flag = true` and note which fields need expansion once Worldbuilding records exist in the Story State KG.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Core wound is specific — an event and a conclusion — not a backstory category.
- [ ] Desire, fear, and self-deception are derived from the wound, not selected independently.
- [ ] Contradictions are behaviourally specific — not trait labels.
- [ ] Response patterns are character-specific — not generic.
- [ ] Arc type is stated as a hypothesis with justification.
- [ ] All seven response pattern categories are populated.
- [ ] `character_node.properties` contains all required fields — no nulls except `last_pov_chapter`.
- [ ] Knowledge matrix entries cover only background knowledge and established false beliefs — no story event knowledge.
- [ ] Relationship edges cover only pre-story relationships.
- [ ] All logical IDs follow the naming convention.
- [ ] No Story State KG writes from this skill — all output in artifacts for story_state_manager.
- [ ] No prose scenes written. No plot placement made.