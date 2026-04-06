---
name: layering-history-and-legend
description: Weaves backstory, in-world songs, legends, ruins, artifacts, and conflicting historical accounts into a completed scene or chapter draft through the natural filter of the POV character's knowledge and cultural context. Queries Story State KG directly for history and legend records, culture records, and the POV character's knowledge matrix. Invoked after scene-construction and pov-consistency-maintenance have cleared the draft. Returns a revised draft in artifacts. Does not introduce new plot events or create new history not already in Story State.
---

# Layering History and Legend

## Identity

**Skill name:** `layering-history-and-legend`
**Purpose:** The past is not backstory — it is a living pressure on every scene. This skill integrates that pressure into prose that has already been written and cleared for POV consistency: the ruins visible from this window, the song one of these characters half-remembers, the contested legend the two cultures interpret differently, the artifact on the table whose significance the POV character partially understands. None of this is delivered as information. It enters the scene through the filter of what this specific character knows, misremembers, was taught, and believes — and it serves the scene's existing conflict, not a worldbuilding agenda.

> **Sibling skills:** Operates on output from `scene-construction` after it has passed `pov-consistency-maintenance`. History integration happens only after the scene's core prose is POV-consistent.

---

## Core

Weave backstory, in-world songs, legends, ruins, artifacts, and conflicting historical accounts into existing prose through the natural filter of the POV character's knowledge and cultural context. Operate on completed, POV-consistent scene or chapter drafts only. Do not introduce new plot events. Do not create new history not already in Story State. Return a revised draft in artifacts.

---

## Input

### From brain context (`worker_request.context`)

1. **`draft_scene`** — The POV-consistent scene or chapter draft from `pov-consistency-maintenance` CLEAN output. Required.
2. **`pov_character_id`** — The `logical_id` of the POV character. Required.
3. **`chapter_context`** — Current chapter number. Used to scope all KG queries. Required.
4. **`scene_location_id`** (optional) — The `logical_id` of the Location node for this scene's setting. When provided, the writing_subagent can query historical Event nodes whose `physical_remnants` involve this location.

### Fetched from Story State KG

The writing_subagent queries the Story State KG directly for all context this skill requires:

```
# POV character's knowledge matrix — epistemic constraint on history integration
query_kg_edges({from_node: pov_character_id, type: "KNOWS"},
               as_of_chapter=chapter_context)
# Fetch KnowledgeItem nodes referenced by the KNOWS edges

# POV character's culture — determines what history they know and how they interpret it
query_kg_edges({from_node: pov_character_id, type: "BELONGS_TO_CULTURE"},
               as_of_chapter=chapter_context)
# Fetch the Culture node(s) from the above edges

# Historical and legendary events — potential integration candidates
query_kg_nodes({type: "Event",
                "properties.is_historical": true},
               as_of_chapter=chapter_context)

# If scene_location_id is provided, also check the Location node
# for any historically significant features
query_kg_nodes({logical_id: scene_location_id, type: "Location"},
               as_of_chapter=chapter_context)

# Other cultures represented by non-POV characters in the scene
# (for conflicting interpretations — infer character IDs from scene context)
# Fetch their BELONGS_TO_CULTURE edges and Culture nodes
```

Review all historical Event nodes against the scene's location, characters, and active themes. Only retrieve the Culture nodes relevant to cultures represented in the scene — do not query all cultures in Story State.

If any query returns no results, note the absence in `kg_context_used` and proceed without that dimension. An empty historical Event set simply means no history has been recorded yet; do not halt.

---

## Output

All output is returned in `artifacts`. The revised draft is the primary output. The brain applies the quality gate. If the brain accepts the revised draft, it routes a `story_state_manager` update for any historical Event nodes whose `referenced_in_chapters` array should be updated.

### `artifacts` structure

```json
{
  "revised_draft": "<the complete revised prose — same scene, history integrated>",
  "integration_log": [
    {
      "element_type": "Physical remnant | Artifact | Legend | Song or saying | Conflicting account | Backstory",
      "source_node_id": "event_<slug> | culture_<slug>",
      "where_integrated": "<brief description of where in the scene and through what trigger>",
      "epistemic_basis": "KNOWS | BELIEVES (false) | Cultural background | No KG record — not integrated",
      "forced_plant_removed": false
    }
  ],
  "referenced_events_to_update": [
    {
      "event_logical_id": "event_<slug>",
      "chapter_to_add": 0
    }
  ],
  "kg_context_used": {
    "historical_events_found": 0,
    "culture_nodes_found": 0,
    "knows_edges_found": 0,
    "location_node_found": false
  }
}
```

`revised_draft` contains the complete scene prose with integrations woven in. It is not a diff or annotation — it is the full revised text ready to proceed.

`integration_log` records every candidate element that was evaluated: those integrated and those rejected (with `epistemic_basis: "No KG record — not integrated"` or with `forced_plant_removed: true` where a plant was rejected after evaluation). This allows the brain's quality gate to verify that integrations are grounded in actual Story State records and are epistemic-consistent.

`referenced_events_to_update` is the list of historical Event nodes where `referenced_in_chapters` should be updated to include `chapter_context`. The brain routes these as `update_kg_node` calls to `story_state_manager`. If no historical events were referenced in the revised draft, this array is empty.

---

## What May Be Integrated

### Ruins, locations, and physical remnants

Physical remnants of history that exist in the scene's location — a wall built by a culture that no longer exists, a room that was once something else, a skyline missing what it used to have. Enter through the POV character's perception of the physical space. They notice the remnant, and their noticing carries whatever knowledge or ignorance they have about what it means.

Check: is the physical remnant listed in a historical Event node's `physical_remnants` array? If yes, and the scene is set at that location, it may be integrated. The character's `KNOWS`/`BELIEVES`/`DOES NOT KNOW` status for the associated historical event determines how they interpret it.

### Artifacts and objects

Objects with historical, cultural, or legendary significance present in the scene. Enter through the POV character's perception of the object and whatever knowledge or association they have with it. The character may know the artifact's significance, misidentify it, or not recognise it at all — all three are valid integrations, determined by the knowledge matrix.

### Legends and oral traditions

In-world myths, founding legends, cautionary tales, stories about specific places or bloodlines. Enter when the scene's events rhyme with a legend's structure, or when one character references a legend the other interprets differently.

The power of in-world legends is that different cultures know different versions. Two characters from different cultures may reference the same historical Event with entirely different interpretations (per `factional_interpretations` in the Event node). This tension — rendered without resolution — is one of the richest forms of history integration.

### In-world songs, sayings, and oral literature

Brief fragments — a line from a song, a proverb, a saying. Must be consistent with the POV character's Cultural background and serve the scene's current emotional or thematic content. Fragments only, not complete texts.

### Conflicting historical accounts

When two characters come from different cultures, they may carry incompatible versions of the same historical event. The POV character noticing that the other character's reference to a historical event carries a different meaning than their own tradition is sufficient — it does not need to be made explicit.

### Backstory

Character-specific formative memories triggered by something in the scene's present material. Always specific (a particular image or moment from the past, not a summary of a period) and always brief — one or two sentences. The past is a pressure on the present; it is not the present.

---

## What May Not Be Integrated

- **New historical events not recorded in Story State as historical Event nodes.** If relevant history is absent from Story State, return the draft unmodified and note the absence in `integration_log`. Do not invent history.
- **New plot events.** The scene's structure — goal, obstacle, choice, consequence — is fixed. Integration adds texture; it does not advance the plot.
- **Exposition blocks.** History is never delivered as an information dump. A character's internal monologue summarising a historical event for the reader's benefit is exposition. History enters through observation, fragment, association, and implication — not through summary.
- **Corrected false beliefs.** If the knowledge matrix records the POV character as believing something historically false (`BELIEVES` status), the integration honours that false belief. The character does not receive accurate historical information through the act of integration.
- **Voice violations.** All integrated material passes through the POV character's voice profile. If a historical reference would require a vocabulary or sentence structure inconsistent with the voice profile, it is adapted or excluded.

---

## The Filter — How History Enters Prose

Every integrated element must pass through the same filter:

**Filter test:** *Would this specific POV character, in this specific moment, given what they know and what they are experiencing, notice, remember, reference, or be affected by this historical element — and if so, how?*

The filter has three components:

1. **Situational trigger:** What in the scene's current material activates the historical element? There must be a specific trigger — history does not arise from nowhere.

2. **Epistemic consistency:** Does the POV character have access to this historical knowledge? Check the KNOWS edges and the Culture node's `religious_beliefs`, `key_customs`, and `core_values` — these establish what people of this background typically know.

3. **Processing register:** How does this character experience historical memory — analytically, emotionally, as cultural habit? The voice profile specifies this; the integration matches it.

---

## Boundary

- **Operates on completed, POV-consistent scene or chapter drafts only.** Does not run on drafts that have not passed `pov-consistency-maintenance`.
- **Does not introduce new plot events.** The scene's structure is fixed before this skill is invoked.
- **Does not create new historical Event nodes.** All history integrated must already exist in Story State. If needed history is absent, note it and proceed without it.
- **Does not write complete in-world songs, poems, or extended oral texts** unless these already exist in a historical Event node's fields.
- **Does not write to the Story State KG.** Returns `referenced_events_to_update` in artifacts; the brain routes updates to `story_state_manager`.
- **Does not correct false historical beliefs.** The POV character's epistemic state is honoured as-is.

---

## Invocation

The `writing_subagent` invokes this skill when the brain delegates history integration:

- After a scene or chapter draft has passed `pov-consistency-maintenance` (and `conflict-layering`, if that was invoked).
- Not after every scene — only when the scene's location, characters, or active themes intersect with relevant historical Event or Culture records in Story State. Many scenes do not require this pass.
- At the chapter level when the brain judges that the completed chapter would benefit from a unified history integration pass rather than scene-by-scene passes.

**Standard post-pov-consistency sequence when applicable:**
`writing_subagent (scene-construction)` → `writing_subagent (pov-consistency-maintenance)` → `[writing_subagent (conflict-layering) if needed]` → `writing_subagent (layering-history-and-legend)` → `[brain routes referenced_events_to_update to story_state_manager]`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | KNOWS edges and KnowledgeItem nodes (POV character knowledge matrix); BELONGS_TO_CULTURE edges and Culture nodes (POV character and other characters in scene); historical Event nodes (`is_historical: true`); optionally Location node for scene setting. All queried with `as_of_chapter` |
| **Returns in artifacts** | Revised draft with history integrated; `integration_log` documenting every candidate evaluated; `referenced_events_to_update` list. Brain routes Event node updates to `story_state_manager` |

---

## Dependencies

**Upstream:** Scene draft must have passed `pov-consistency-maintenance` — required in context. Historical Event, Culture, and KnowledgeItem nodes must be current in Story State KG.

**Downstream:** Revised draft proceeds to the brain for quality gate review. After acceptance, the brain routes `referenced_events_to_update` to `story_state_manager` as `update_kg_node` calls (adding `chapter_context` to `properties.referenced_in_chapters` for each). The revised draft replaces the base draft as the version of record going into the Chapter node.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Populate `kg_context_used`. Note which query types returned results.

### Step 2 — Read the base draft with the historical record in view

Read the scene draft. Simultaneously, review the historical Event nodes and Culture nodes retrieved. Map the intersections: where in the draft does history already press on the scene, even implicitly? Where is the setting physically located within historical space? What cultural backgrounds are represented? What is the scene's active conflict — and which historical events or legends resonate structurally with it?

Make a mental map of integration opportunities before writing a word.

### Step 3 — Apply the filter to each candidate element

For each historical element that intersects with the scene, apply all three filter components:
- **Situational trigger:** Is there a specific trigger in the scene's present material that activates this element?
- **Epistemic consistency:** What is the POV character's KNOWS status for this historical knowledge? If `DOES NOT KNOW`, they cannot reference it directly — but they may notice a physical remnant without knowing what it is.
- **Processing register:** How would this character experience this element, as specified in their voice profile?

Rank candidate elements: organic (trigger is clear, integration is natural), marginal (plausible but not compelling), forced (no organic trigger). Integrate only organic elements. The iceberg principle applies — most history stays beneath the surface.

### Step 4 — Integrate physical remnants and setting

Enter through the POV character's perception of the physical space. Keep setting-based history brief — one or two sentences. A detail in the world, noticed, not explained.

A character who knows the history: notices the feature, understands its significance.
A character who does not know the history: notices the feature as a feature, perhaps finds it strange. The reader may understand what the character does not — this is the iceberg working as it should.

### Step 5 — Integrate artifacts and objects

Enter through the POV character's relationship to the object: what they know about it (per knowledge matrix), what they believe about it (which may be false per `BELIEVES` status), what it makes them think. If two characters have different cultural relationships to the same object, render the asymmetry without resolving it.

### Step 6 — Integrate legends, oral tradition, and conflicting interpretations

Enter through association or reference — not through summary. The character does not think "This reminds me of the legend of X, which says Y." The resonance surfaces more obliquely. Conflicting interpretations are most effective when rendered without resolution.

### Step 7 — Integrate backstory through specific memory

A specific, sensory trigger in the scene's present material activates a brief, specific memory — one or two sentences. The past arrives as a flash and recedes. The memory must serve the scene's current content. It does not become the scene's dominant material.

### Step 8 — Review the integrated draft for organic quality

Read the complete revised draft. For each integrated element, verify:
- Does the integration feel like the character's natural perception and memory, or does it feel like a planted worldbuilding note?
- Did the history stop the scene — did the reader have to pause to receive information?
- Is the integrated element consistent with the knowledge matrix and Cultural background?
- Did any integration introduce a new plot event?

Remove or rewrite any integration that fails these tests. An unintegrated element is better than a forced one.

### Step 9 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. `revised_draft` is the full prose text. `integration_log` records every candidate evaluated. `referenced_events_to_update` lists historical Event nodes whose `referenced_in_chapters` should now include `chapter_context`.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Every integrated element has a specific situational trigger — it is not inserted, it is called up by something in the scene.
- [ ] Every integrated element passed the epistemic consistency check against the knowledge matrix.
- [ ] False historical beliefs (`BELIEVES` status) are honoured — the character carries their false version, not the true account.
- [ ] No exposition blocks — history enters as observation, fragment, association, or implication; never as summary.
- [ ] No new plot events introduced — the scene's structure is unchanged.
- [ ] All integrated material passes through the POV character's voice profile.
- [ ] Integration is selective — not all available historical Event records are used; only what the scene organically absorbs.
- [ ] The scene's forward movement is not stopped by any integrated element.
- [ ] No new history invented outside existing historical Event nodes.
- [ ] `referenced_events_to_update` is populated for every historical Event cited in the revised draft (or empty array if none).
- [ ] `integration_log` records every candidate evaluated, including those rejected.
- [ ] No Story State KG writes from this skill — updates routed via `referenced_events_to_update` to brain for `story_state_manager`.