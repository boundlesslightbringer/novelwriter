---
name: character-integration-with-plot
description: Maps the desire→action→consequence loop for each character; builds the full directional relationship matrix with detailed records; defines response patterns to categories of events. Invoked after character-creation has been persisted for all relevant characters. Queries Story State KG directly for all character records, existing knowledge matrix entries, relationship records, and the political map. Returns expanded knowledge matrix edges, full relationship edges, and initial consequence ledger entries in artifacts for persistence via story_state_manager.
---

# Character Integration with Plot

## Identity

**Purpose:** Integrate completed characters into the story's living system by formalising the desire→action→consequence loops that will drive plot from character, building the full directional relationship matrix between characters, and seeding the Consequence Ledger with anticipated consequence structures. This is the last character-building skill before writing begins.

---

## Core

Map the desire → action → consequence loop for each character; build the full relationship matrix with detailed directional records; define each character's response patterns to categories of events. Return expanded knowledge matrix edges, full relationship edge records, and initial Consequence Ledger entries in artifacts. Do not write scenes or plot events.

---

## Input

### From brain context (`worker_request.context`)

1. **`character_ids`** — List of `logical_id` strings for all characters to integrate. Required. Example: `["char_caradhen", "char_vara", "char_sethric"]`.
2. **`chapter_context`** — Current chapter number for KG query scoping. Required.

### Fetched from Story State KG

The character_subagent queries the Story State KG to retrieve all records this skill requires, replacing the previously relayed excerpts from Modules 1.1, 1.2, 1.3, and 3.1:

```
# Full psychological records for all characters being integrated
query_kg_nodes({type: "Character",
                logical_id: {$in: character_ids}},
               as_of_chapter=chapter_context)

# Current knowledge matrix entries for all characters
query_kg_edges({type: "KNOWS",
                from_node: {$in: character_ids}},
               as_of_chapter=chapter_context)

# Existing relationship edges (initial entries from character-creation)
query_kg_edges({type: "RELATIONSHIP",
                from_node: {$in: character_ids}},
               as_of_chapter=chapter_context)

# Political and power map — for grounding desire loops
# and relationship trajectories in the political reality
query_kg_nodes({type: "Faction"}, as_of_chapter=chapter_context)
query_kg_nodes({type: "PlotThread",
                "properties.status": "Active"},
               as_of_chapter=chapter_context)

# All existing consequence ledger entries — to check for linkage
query_kg_nodes({type: "CascadeChain"}, as_of_chapter=chapter_context)
```

The MongoDB `$in` operator syntax is used here for clarity; the actual query form depends on what `query_kg_nodes` and `query_kg_edges` support. If batch querying is not available, run one query per character ID and merge results.

---

## Output

All output is returned in `artifacts` as KG-ready records for `story_state_manager` to persist. The brain applies the quality gate before routing to `story_state_manager`.

### `artifacts` structure

```json
{
  "knowledge_matrix_expansions": {
    "new_knowledge_items": [
      {
        "logical_id": "ki_<slug>",
        "node_type": "KnowledgeItem",
        "chapter": 0,
        "properties": {
          "description": "<specific fact, secret, or event>"
        }
      }
    ],
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
          "source": "<how they came to know, suspect, or believe this>",
          "dramatic_irony_flag": false
        }
      }
    ]
  },
  "relationship_records": {
    "new_relationship_edges": [
      {
        "logical_id": "rel_<char_a_slug>_<char_b_slug>",
        "edge_type": "RELATIONSHIP",
        "from_node": "char_<slug>",
        "to_node": "char_<other_slug>",
        "chapter": 0,
        "properties": {
          "emotional_valence": "<current dominant emotion from A's perspective>",
          "power_dynamic": "<who holds leverage, what kind, whether accurately perceived>",
          "history": "<1–3 load-bearing moments>",
          "secrets_kept": ["<what A is concealing from B>"],
          "trajectory": "Stable | Deteriorating | Evolving | Volatile",
          "convergence_potential": "<whether and approximately when direct contact/conflict>",
          "most_recent_interaction": null
        }
      }
    ],
    "updated_relationship_edges": [
      {
        "logical_id": "rel_<existing_edge_slug>",
        "updated_properties": {
          "power_dynamic": "<corrected after full integration analysis>",
          "trajectory": "<updated trajectory>",
          "convergence_potential": "<now determinable>"
        },
        "chapter": 0
      }
    ]
  },
  "consequence_ledger_seeds": {
    "cascade_chain_nodes": [
      {
        "logical_id": "cc_<char_slug>_desire_loop",
        "node_type": "CascadeChain",
        "chapter": 0,
        "properties": {
          "sequence": [
            "<desire driver>",
            "<anticipated action pattern>",
            "<anticipated immediate consequence>",
            "<time-delayed consequence if applicable>"
          ],
          "current_position": "<desire driver>",
          "remaining_links": ["<anticipated action>", "<consequence>"]
        }
      }
    ]
  },
  "integration_flags": [
    {
      "type": "asymmetric_relationship_risk | knowledge_plausibility | desire_loop_gap",
      "description": "<specific flag>",
      "affected_characters": ["char_<slug>"]
    }
  ]
}
```

**`knowledge_matrix_expansions`** adds the inter-character knowledge that was not established at creation time: what Character A knows about Character B that Character B does not know they know; established false beliefs about other characters (BELIEVES entries); information asymmetries at story opening (DOES NOT KNOW entries).

**`relationship_records.new_relationship_edges`** contains the full directional records for character pairs. These are directional — A→B and B→A are separate edge records with potentially asymmetric content. `updated_relationship_edges` patches existing edges created by `character-creation` where integration analysis reveals corrections.

**`consequence_ledger_seeds`** creates anticipatory CascadeChain nodes — one per character's central desire loop — recording the consequence *structure* that will emerge from their desires acting in this world. These are hypothetical scaffolding; Consequence Cascade Implementation adds actual chains as events are written.

**`integration_flags`** returns any gaps or inconsistencies found during integration for the brain to surface to the user or act on.

---

## Boundary

- **Requires** `character-creation` to be persisted in Story State KG for all characters being integrated. Cannot run on concept documents or partial records.
- **Does not** write scenes, plot events, or prose.
- **Does not** produce a scene outline or chapter plan.
- **Does not** determine pacing or chapter sequence. Those are Group 3 skill domains.
- **Does not** write to the Story State KG. Returns KG-ready records in artifacts for `story_state_manager`.
- **Does not** generate new character concepts or extend existing character psychology beyond what is in the persisted Character nodes. If the records are incomplete, returns the output it can and flags what is missing in `integration_flags`.

---

## Invocation

The `character_subagent` invokes this skill when the brain delegates character integration:

- After `character-creation` has been persisted in the Story State KG for all characters who will be present in the story's opening arc.
- Before writing of the opening chapters begins.
- When a new significant character is added mid-story and must be integrated with existing characters. The brain passes the new character's ID alongside existing character IDs in `character_ids`.

This skill is invoked once per character cohort (or new character addition), not on a recurring basis.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character nodes (full psychological records for all `character_ids`); existing KNOWS edges (current knowledge matrix state); existing RELATIONSHIP edges (initial entries from character-creation); Faction and active PlotThread nodes (political context); CascadeChain nodes (existing consequence chains to check for linkage). All queried with `as_of_chapter` |
| **Returns in artifacts** | Expanded KnowledgeItem nodes and KNOWS edges (Module 1.2 expansion); new and updated RELATIONSHIP edges (Module 1.3 full records); anticipatory CascadeChain nodes (Module 4.3 initial entries); `integration_flags` for any gaps. Brain routes all to `story_state_manager` for persistence |

---

## Dependencies

**Upstream:** All Character nodes in `character_ids` must be persisted in Story State KG. Brain provides `character_ids` and `chapter_context`.

**Downstream:** Persisted Module 1.3 Relationship edges are read by `plotting_subagent` (`gardener-plotting-system`, `conflict-layering`) and `consequence_subagent` (`consequence-cascade-implementation`). Persisted Module 1.2 KNOWS edges are read by `writing_subagent` (`pov-consistency-maintenance`). Anticipatory CascadeChain nodes provide scaffolding for `consequence_subagent`.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries. If any Character node in `character_ids` is not found, add a flag to `integration_flags` and proceed with the characters that are available.

Review what is returned:
- Character nodes: the psychological foundations for all desire loops
- Existing KNOWS edges: what the knowledge matrix already contains
- Existing RELATIONSHIP edges: what `character-creation` established
- Faction and PlotThread nodes: the political and narrative context

### Step 2 — Map the desire network

Before building relationships, map each character's core desire against the others':
- Which desires are structurally compatible — they want different things and can use each other?
- Which are in conflict — they want the same scarce resource, or one's success requires the other's failure?
- Which are mutually invisible — not yet in conflict but will be when they converge?

This network is the foundation of all relationship trajectories.

### Step 3 — Expand the knowledge matrix

For each character, work through the four knowledge states at story opening:

**KNOWS:** Focus on inter-character knowledge. What does this character know about others that creates advantage, obligation, or vulnerability? Cross-reference: if A knows something about B, ensure B gets a DOES NOT KNOW entry for the same KnowledgeItem.

**SUSPECTS:** Derive suspicions from psychology and position. A character whose primary lens is threat-assessment will have active suspicions even without direct evidence.

**BELIEVES (possibly false):** Systematically register all false beliefs at story start. False beliefs about other characters are seeds of dramatic irony, knowledge violations for `pov-consistency-maintenance` to catch, and eventual revelation scenes.

**DOES NOT KNOW:** For every significant fact known to at least one other character, specify who does not know it. Information asymmetry at story opening is a primary source of dramatic tension.

### Step 4 — Build full directional relationship records

Build each significant relationship as two edge records: A→B and B→A. The asymmetry between these records is often the most dramatically interesting element.

For each record:

**Valence:** Be precise. "Complex" is not sufficient — specify what the complexity consists of (e.g. "genuine affection that coexists with active exploitation; A does not know both are present simultaneously in B's experience of the relationship").

**Power dynamic:** Who holds leverage, what kind, and whether either party is accurately assessing the power distribution. Misperceived power dynamics are a major source of dramatic complication.

**History:** Identify the 1–3 specific moments in the relationship's history that most define its current state. Not a complete history — the load-bearing moments.

**Secrets:** Be explicit about what each character is concealing and whether the other suspects concealment.

**Trajectory:** State the direction this relationship is heading if both characters continue acting from their current psychology and knowledge state. Mark it as a hypothesis.

**Convergence potential:** When will these characters be in the same scene? Does the story require them to be, or will their plotlines run parallel for some time?

If existing RELATIONSHIP edges from `character-creation` need updating (trajectory can now be determined, power dynamic is more precisely understood), add them to `updated_relationship_edges`.

### Step 5 — Seed the Consequence Ledger

For each character's central desire loop, create an anticipatory CascadeChain node. The purpose is not to pre-plot events but to formalise the consequence *structure* that will emerge from this character's desires acting in this world.

For each node, answer: *If this character pursues this desire in this world, given these relationships and this political context, what is the shape of the consequence that eventually comes back to them?* Specifically:
- What are they likely to do that will have consequences they cannot foresee?
- Who will be affected, and how?
- Is there a specific action that, if taken early, creates a time-delayed catastrophic consequence?

### Step 6 — Flag gaps and inconsistencies

Review the integration output before assembling artifacts. Flag:
- Any character pair where relationship asymmetry seems unintentional.
- Any knowledge state that appears implausible given the character's position.
- Any desire loop where the consequence structure cannot be anticipated because a character's psychology is insufficiently developed in their Character node (possible if early invocation context was used).

Return flags in `integration_flags` alongside the data.

### Step 7 — Assemble and return artifacts

Assemble the full artifacts dict with all KG-ready records. Set `status: "success"`. If flags are present, note them in `summary` so the brain's quality gate is aware.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] All Character nodes in `character_ids` were found in KG; missing nodes are flagged.
- [ ] Knowledge matrix is cross-referenced — if A KNOWS X about B, B's DOES NOT KNOW entry exists.
- [ ] BELIEVES entries include all false beliefs from Character node records, not just obvious ones.
- [ ] Relationship edges are directional — A→B and B→A are separate with potentially asymmetric content.
- [ ] Power dynamics specify the type of power and whether it is accurately perceived by both parties.
- [ ] CascadeChain nodes are anticipatory structures, not locked plot events.
- [ ] `integration_flags` is present (even if empty array).
- [ ] No Story State KG writes from this skill — all output in artifacts for story_state_manager.
- [ ] No prose scenes written. No chapter plan produced.