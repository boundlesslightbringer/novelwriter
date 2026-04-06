---
name: consequence-cascade-implementation
description: Projects, structures, and records the full consequence cascade of a major story event. For every significant event — a death, a betrayal, a battle, a revelation, a broken oath — traces immediate, short-term, and long-term consequences across all affected characters and relationships, and identifies time-delayed consequence bombs. Queries Story State KG directly for all affected character records, relationship records, and existing consequence chains. Returns structured consequence records in artifacts for persistence via story_state_manager. Invoked immediately after a major event is written, before the next scene is drafted.
---

# Consequence Cascade Implementation

## Identity

**Skill name:** `consequence-cascade-implementation`
**Group:** 5 — Consequence & Realism
**Subagent:** consequence_subagent
**When to invoke:** Called by the `consequence_subagent` when the brain delegates consequence analysis immediately after a major event is written — a death, a decisive battle, a betrayal, a secret revealed, a power shift, a broken vow, or any action that materially changes one or more characters' situations. Must be completed before the next scene is drafted, so the consequence records are available to `gardener-plotting-system` and `scene-construction`.

---

## Core

For each major triggering event, project and record the full consequence cascade: immediate consequences, short-term consequences, and long-term consequences (consequence bombs). All consequences are traced across every affected character and every affected relationship pair. Each consequence bomb is assigned a condition-based detonation trigger, a narrative phase anchor, and a priority tier (Essential, Enriching, or Unclassified). Essential bombs are returned for dual registration — both in Module 4.2 records and as Payoff nodes so `plot-thread-tracking` can surface them during convergence sweeps. Return structured consequence records in artifacts for persistence by `story_state_manager`.

---

## Input

### From brain context (`worker_request.context`)

1. **`triggering_event`** — Plain-language description of what happened: the act, the outcome, and the chapter reference where it occurred. Required.
2. **`chapter_context`** — The chapter number where the event occurred. Used to scope all KG queries and to set `valid_from` on new records. Required.
3. **`affected_character_ids`** — List of `logical_id` strings for all characters directly or indirectly affected. Required. The brain determines this list before delegating — a character is affected if they witnessed the event, are named in the consequence, held a relationship with a character who was killed or transformed, or will plausibly act on new information the event creates.

### Fetched from Story State KG

The consequence_subagent queries the Story State KG directly for all records required to trace consequences:

```
# Full psychological records for all affected characters
query_kg_nodes({type: "Character",
                logical_id: {$in: affected_character_ids}},
               as_of_chapter=chapter_context)

# Directional relationship records for all affected character pairs
query_kg_edges({type: "RELATIONSHIP",
                from_node: {$in: affected_character_ids}},
               as_of_chapter=chapter_context)

# Existing consequence chains — to check whether this event
# is a downstream link in an existing chain or a new chain root
query_kg_nodes({type: "CascadeChain"},
               as_of_chapter=chapter_context)

# Existing consequence bombs — to check priority and registration
query_kg_nodes({type: "Payoff",
                "properties.type": "Consequence bomb",
                "properties.resolution_status": "Pending"},
               as_of_chapter=chapter_context)
```

If any character ID in `affected_character_ids` is not found in the KG, note the absence in `kg_context_used` and proceed with the characters that are available — do not halt.

---

## Output

All output is returned in `artifacts` as KG-ready records for `story_state_manager` to persist. The brain applies the quality gate before routing to `story_state_manager`.

### `artifacts` structure

```json
{
  "triggering_event_summary": "<description + chapter reference>",
  "cascade_chain": {
    "action": "create_new | extend_existing",
    "existing_chain_id": null,
    "node": {
      "logical_id": "cc_<event_slug>",
      "node_type": "CascadeChain",
      "chapter": 0,
      "properties": {
        "sequence": [
          "<triggering event>",
          "<immediate consequence>",
          "<short-term consequence>",
          "<long-term consequence>"
        ],
        "current_position": "<triggering event>",
        "remaining_links": [
          "<short-term consequence>",
          "<long-term consequence>"
        ]
      }
    },
    "update_existing": null
  },
  "consequence_chain_entry": {
    "node_type": "CascadeChain",
    "event_consequences": {
      "immediate": [
        {
          "affected_entity": "char_<slug> | relationship | world_state",
          "description": "<specific, concrete change>",
          "chapter_reference": 0
        }
      ],
      "short_term": [
        {
          "affected_entity": "char_<slug> | relationship | world_state",
          "description": "<what is now in motion>",
          "projected_chapters": "<rough chapter range>"
        }
      ],
      "long_term_pending": [
        {
          "affected_entity": "char_<slug> | relationship | world_state",
          "description": "<what this eventually leads to>",
          "bomb_id": "bomb_<slug>"
        }
      ]
    }
  },
  "consequence_bombs": [
    {
      "logical_id": "bomb_<slug>",
      "node_type": "Payoff",
      "chapter": 0,
      "properties": {
        "type": "Consequence bomb",
        "description": "<nature of the future consequence>",
        "planted_in_chapter": 0,
        "detonation_trigger": "<story condition or character situation that fires this — NOT a chapter number>",
        "narrative_phase_anchor": "early | mid | convergence | final act",
        "resolution_status": "Pending",
        "priority_tier": "Essential | Enriching | Unclassified",
        "dual_register": false
      }
    }
  ],
  "character_state_updates": [
    {
      "logical_id": "char_<slug>",
      "updated_properties": {
        "emotional_state": "<updated>",
        "active_fears": ["<updated>"],
        "injuries_physical_state": ["<if applicable>"]
      },
      "chapter": 0
    }
  ],
  "relationship_updates": [
    {
      "logical_id": "rel_<a_slug>_<b_slug>",
      "updated_properties": {
        "emotional_valence": "<updated>",
        "trajectory": "Stable | Deteriorating | Evolving | Volatile",
        "most_recent_interaction": "<chapter reference + brief summary>"
      },
      "chapter": 0
    }
  ],
  "knowledge_matrix_updates": [
    {
      "character_id": "char_<slug>",
      "new_knows_edges": [
        {
          "logical_id": "knows_<char_slug>_<item_slug>",
          "edge_type": "KNOWS",
          "from_node": "char_<slug>",
          "to_node": "ki_<slug>",
          "chapter": 0,
          "properties": {
            "status": "KNOWS | BELIEVES | SUSPECTS | DOES NOT KNOW",
            "acquired_at_chapter": 0,
            "source": "<how they came to know this from the event>",
            "dramatic_irony_flag": false
          }
        }
      ],
      "new_knowledge_items": [
        {
          "logical_id": "ki_<slug>",
          "node_type": "KnowledgeItem",
          "chapter": 0,
          "properties": {
            "description": "<the new fact, secret, or revelation created by this event>"
          }
        }
      ]
    }
  ],
  "kg_context_used": {
    "character_nodes_found": 0,
    "relationship_edges_found": 0,
    "existing_cascade_chains_found": 0,
    "chain_action": "create_new | extend_existing"
  }
}
```

**`cascade_chain.action`** is `"extend_existing"` when this event is a downstream link in an existing CascadeChain node (the event was listed as a `remaining_links` entry). In that case, `existing_chain_id` is populated and `update_existing` contains the updated `current_position` and `remaining_links` to patch the existing node. When `"create_new"`, the `node` field contains a new CascadeChain node record.

**`consequence_bombs`** are structured as Payoff node records ready for `story_state_manager` to insert. `dual_register: true` flags Essential bombs — `story_state_manager` inserts these as Payoff nodes in the KG, making them visible to `plot-thread-tracking`'s convergence sweep. Enriching and Unclassified bombs are also inserted as Payoff nodes (for completeness) but with `priority_tier` set accordingly.

**`character_state_updates`** and **`relationship_updates`** are `update_kg_node` and `update_kg_edge` payloads — the consequence may immediately change a character's emotional state, a relationship's trajectory, or a relationship's most recent interaction record.

**`knowledge_matrix_updates`** tracks new information that characters gain (or do not gain) from the event — new KnowledgeItem nodes and KNOWS edges for each affected character, reflecting what they witnessed or learned.

---

## Detonation Trigger Design

Consequence bombs must use **condition-based detonation triggers**, not chapter numbers. The novel's length is unknown and its pacing may shift.

**Weak (chapter-anchored):** `"Estimated detonation: Ch. 22–25"`
**Strong (condition-anchored):** `"Detonates when Cavan is publicly forced to choose a side — the moment when silence is no longer possible"`

The condition should be specific enough to be recognisable when it arrives but robust enough to survive pacing changes. A `narrative_phase_anchor` label (early / mid / convergence / final act) may be added as a supplementary orientation point — but it is never the primary trigger specification.

---

## Priority Tier Assignment

Ask: *If the story ended without this bomb detonating, would the ending feel incomplete, or merely less rich?*

- **Essential:** The story's thematic or emotional resolution genuinely depends on this bomb firing. A reader tracking this thread would feel the ending was unfinished without it. These bombs must find a scene before the story closes.
- **Enriching:** The bomb adds resonance and depth if it fires. The story's main arc closes satisfactorily without it. Fire if opportunity permits.
- **Unclassified:** Consequences are clear but whether they are load-bearing for the ending cannot be determined at this point. Flag for reassessment at the convergence-phase sweep.

When in doubt between Essential and Enriching: Is this bomb connected to the story's core conflict question (from the endpoint compass)? If yes, lean Essential. If it deepens a subplot or enriches a secondary character arc, lean Enriching.

---

## Boundary

- **Does not write prose.** Produces structured KG-ready records, not scenes.
- **Does not determine how consequences will be dramatised.** That is `gardener-plotting-system` and `scene-construction`. This skill records what must happen; those skills determine how and in what scene.
- **Does not write to the Story State KG.** Returns structured records in artifacts; `story_state_manager` performs all writes.
- **Does not speculate beyond the provided character IDs.** Works only from the Character nodes and RELATIONSHIP edges retrieved for the `affected_character_ids` list. Does not invent affected characters not present in the KG records.
- **Does not resolve the consequences.** Maps what is now in motion. Resolution occurs in future chapters.
- **Does not use chapter numbers as primary detonation anchors.** Condition-based triggers only.
- **Does not make final determinations on priority tier when uncertain.** Unclassified is a valid tier; priority is revisited by `plot-thread-tracking` at convergence.

---

## Invocation

The `consequence_subagent` invokes this skill when the brain delegates consequence analysis — immediately after a major scene has been drafted and a major event has occurred in the story. The brain determines which characters are affected before delegating.

The brain must ensure the Story State KG has been updated with the scene's output (Chapter node created, character states updated from the scene) before delegating this skill, so the character records reflect the post-event state.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character nodes for all `affected_character_ids`; RELATIONSHIP edges between all affected pairs; existing CascadeChain nodes (to check for existing chain linkage); existing Payoff nodes of type "Consequence bomb" (to check registration status). All queried with `as_of_chapter` |
| **Returns in artifacts** | CascadeChain node (new or update payload for existing); Payoff nodes for all consequence bombs (including dual-register Essential bombs); character state update payloads; relationship update payloads; knowledge matrix update payloads (new KnowledgeItem nodes and KNOWS edges). Brain routes all to `story_state_manager` for persistence |

---

## Dependencies

**Upstream:** Major scene must be written and passed the quality gate. Character and relationship records for `affected_character_ids` must be current in Story State KG. Brain provides `triggering_event`, `chapter_context`, and `affected_character_ids`.

**Downstream:** Persisted CascadeChain and Payoff nodes are read by `plotting_subagent (plot-thread-tracking)` during convergence sweeps. Persisted Payoff nodes (consequence bombs) are read by `plotting_subagent (gardener-plotting-system)` when checking for approaching detonations. Updated character state records are read by all subsequent scene-level skills.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Populate `kg_context_used`. If any character ID in `affected_character_ids` is not found, note it and proceed with available records.

### Step 2 — Parse the triggering event

Read `triggering_event` from context. Identify:
- What specifically changed in the world (person died, power shifted, secret revealed, alliance broke, etc.)
- Who was present and who will learn of it
- What was irrevocably altered vs. what is temporarily disrupted

Name the event concisely for use in logical IDs (e.g. `harren_public_accusation_ch9`).

### Step 3 — Check for existing cascade chain linkage

Review the CascadeChain nodes retrieved from KG. Is this event already listed as a `remaining_links` entry in an existing chain? If yes, this event is a downstream link — update the existing chain rather than creating a new one. Set `cascade_chain.action = "extend_existing"`, populate `existing_chain_id`, and construct the `update_existing` payload updating `current_position` and removing this event from `remaining_links`.

If this event is genuinely new and not a downstream link of anything recorded, set `cascade_chain.action = "create_new"` and construct the new CascadeChain node.

### Step 4 — Trace immediate consequences

For each affected character, apply the desire → action → consequence model:
- What did they want before this event?
- What has this event taken from them, given them, or forced them to confront?
- What is the first thing they will do or feel in the immediate aftermath?

For each affected RELATIONSHIP edge (directional):
- Has the valence shifted?
- Has a secret been exposed or a power balance altered?
- What is the most recent interaction now?

Immediate consequences are those that play out in the current or next scene.

### Step 5 — Project short-term consequences

Extend the cascade across the next several chapters. For each character, ask:
- What action does the immediate consequence compel?
- What does that action collide with (other characters' plans, world state, active plot threads)?
- What new conflicts or opportunities does this create?

Short-term consequences must be concrete and plausible, not vague. "Aemond will seek revenge" is insufficient. "Aemond will move to consolidate control of the eastern garrison before the news reaches his brother's allies — creating a three-chapter window where Daemon must decide whether to strike first or negotiate" is a short-term consequence.

### Step 6 — Identify consequence bombs and assign priority

For each long-term consequence that will not be dramatised for many chapters:

**6a. Define the detonation trigger as a story condition, not a chapter number.** The condition must be specific enough to be recognisable when it arrives but robust enough to survive pacing changes.

**6b. Assign priority tier** using the Essential / Enriching / Unclassified framework. When uncertain, apply the core conflict question test.

**6c. Construct Payoff node records** for each bomb. Set `dual_register: true` for Essential bombs.

### Step 7 — Build character state and relationship update payloads

For each affected character whose `emotional_state`, `active_fears`, or `injuries_physical_state` has changed as an immediate consequence of the event, construct an `update_kg_node` payload.

For each affected RELATIONSHIP edge whose `emotional_valence`, `trajectory`, or `most_recent_interaction` has changed, construct an `update_kg_edge` payload.

### Step 8 — Build knowledge matrix updates

For each affected character, assess what they now know, suspect, or believe as a result of the event that they did not before. Construct new KnowledgeItem nodes and KNOWS edges for each new piece of information, with the appropriate status and `dramatic_irony_flag` where the reader knows more than the character.

### Step 9 — Assemble and return artifacts

Assemble the complete artifacts dict. Set `status: "success"`. Ensure consequence bombs with `dual_register: true` are clearly identifiable for `story_state_manager` to insert as both CascadeChain entries and Payoff nodes.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] `cascade_chain.action` is explicitly `"create_new"` or `"extend_existing"`.
- [ ] If `"extend_existing"`: `existing_chain_id` is populated and `update_existing` contains correct patch payload.
- [ ] All consequence bombs use condition-based detonation triggers — no chapter number estimates as primary triggers.
- [ ] Priority tier assignment is explicit for every bomb; Unclassified is used when genuinely uncertain, not as a default.
- [ ] `dual_register: true` is set only for Essential bombs.
- [ ] `character_state_updates` covers all characters whose immediate state has changed.
- [ ] `knowledge_matrix_updates` covers information asymmetries created by the event (who witnessed it, who will not learn of it).
- [ ] Short-term consequences are specific and concrete — not vague intentions.
- [ ] No prose written. No scenes determined.
- [ ] No Story State KG writes from this skill — all output in artifacts for story_state_manager.