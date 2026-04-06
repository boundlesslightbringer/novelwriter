---
name: character-relationship-matrix
description: >
  Step 3 of 3 in the character integration chain. Uses the desire network
  from step 1 to build the full directional relationship matrix — one record
  per character pair per direction, with emotional valence, power dynamic,
  history, secrets, and trajectory. Expands and corrects the initial
  relationship edges created by character-creation. Produces RELATIONSHIP
  edge records for the Story State KG.
---

# Character Relationship Matrix

## Identity

**Position in chain:** Step 3 of 3. Runs after `character-desire-network`.
Runs in parallel with `character-knowledge-expansion` (neither depends on
the other's output).

**Single task:** Build the full directional relationship records. The key word
is *directional* — A→B and B→A are separate records that may be radically
asymmetric. The asymmetry between the two directions is often the most
dramatically useful thing about a relationship.

---

## Input

From the chain's accumulated context:

| Key | Description |
|---|---|
| `character_nodes` | Full Character node records — `core_wound`, `core_fear`, `self_deception`, `values_under_pressure`, `response_patterns` |
| `existing_relationship_edges` | RELATIONSHIP edges already created by `character-creation` (pre-story relationships with initial properties) — expand and correct these where warranted |
| `desire_network` | Output of step 1 — the structural classification of each pair (compatible / conflicting / invisible) and the specific desire descriptions |

---

## Output

KG-ready records to be included in the chain's combined `relationship_records`
artifacts field.

```json
{
  "new_relationship_edges": [
    {
      "logical_id": "rel_<char_a_slug>_<char_b_slug>",
      "edge_type": "RELATIONSHIP",
      "from_node": "char_<slug>",
      "to_node": "char_<other_slug>",
      "chapter": 0,
      "properties": {
        "emotional_valence": "<the dominant emotion from A's perspective toward B>",
        "power_dynamic": "<who holds leverage, what kind, whether accurately perceived by both>",
        "history": "<1–3 load-bearing moments that define the current state>",
        "secrets_kept": ["<what A is concealing from B>"],
        "trajectory": "Stable | Deteriorating | Evolving | Volatile",
        "convergence_potential": "<whether and approximately when direct contact or conflict>",
        "most_recent_interaction": null
      }
    }
  ],
  "updated_relationship_edges": [
    {
      "logical_id": "rel_<existing_edge_slug>",
      "updated_properties": {
        "power_dynamic": "<corrected or expanded>",
        "trajectory": "<now determinable from desire network>",
        "convergence_potential": "<now determinable>"
      },
      "chapter": 0
    }
  ],
  "flags": [
    {
      "type": "asymmetry_risk | power_misperception | trajectory_gap",
      "description": "<specific issue>",
      "affected_characters": ["char_<slug>"]
    }
  ]
}
```

---

## Building each record

For each character pair, build two records: A→B and B→A. Do not merge them
into one record. Do not make them symmetric by default.

Work through these four fields carefully for each direction:

**Emotional valence.** Name the specific dominant emotion from this character's
perspective, not a generic label. "Respect that contains an unacknowledged
fear of being seen through" is a valence. "Respect" alone is not. Derive from
the character's `core_fear` and `response_patterns.being_correctly_seen` —
how does this character feel toward someone who might accurately assess them?

**Power dynamic.** Answer three questions: (1) Who holds leverage in this
relationship, and what kind — coercive, informational, emotional, economic,
social? (2) Is the leverage accurately perceived by both parties? Misperceived
power dynamics are a primary source of dramatic complication — a character who
believes they hold power and does not will make different decisions. (3) Could
the power balance shift, and under what conditions?

**Secrets kept.** What is A concealing from B that would materially affect B's
behaviour if known? Do not list trivial concealments — only secrets that carry
real narrative weight. Cross-reference with `self_deception` fields: a character
who self-deceives about X is likely to conceal the same X from others.

**Trajectory.** Given both characters' current psychology, knowledge states,
and the political context from the desire network — where is this relationship
heading if nothing intervenes? Mark as a hypothesis. If the trajectory points
toward a specific type of confrontation or revelation, name it without
specifying a chapter.

---

## Handling existing relationship edges

`character-creation` created initial RELATIONSHIP edges for pre-story relationships.
These have some fields populated (valence, history) but others left empty
(trajectory, convergence_potential, power_dynamic details).

For each existing edge:
- If the desire network clarifies the trajectory or power dynamic, add it to
  `updated_relationship_edges`.
- If the initial valence or history was set correctly, do not touch it.
- If the desire network reveals that the initial valence is wrong or incomplete,
  flag it in `flags` rather than silently correcting it — let the brain decide
  whether to update.

New character pairs with no existing edge go into `new_relationship_edges`.

---

## The asymmetry principle

The most important thing this skill produces is the asymmetry between A→B and B→A.
Before returning output, check each pair and ask: *are these two records actually
different from each other, or did I just reverse the names?*

Real asymmetry examples:
- A trusts B; B is using A.
- A holds formal power; B holds the specific power of being A's witness to something
  A cannot afford to have witnessed.
- A believes the relationship is a genuine alliance; B knows it is a temporary
  accommodation.

If two records look like mirrors of each other with reversed names, at least one
of them is wrong.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality checks

- [ ] Every character pair has two records: A→B and B→A.
- [ ] The two records for each pair are genuinely asymmetric — not just reversed.
- [ ] Power dynamic specifies the *type* of leverage and whether it is accurately
      perceived by both parties.
- [ ] `emotional_valence` is specific — not a generic label.
- [ ] `secrets_kept` are narratively material — not trivial.
- [ ] Trajectory is stated as a hypothesis. Specific type of confrontation or
      revelation named if determinable.
- [ ] Existing edges are expanded in `updated_relationship_edges`, not duplicated
      in `new_relationship_edges`.
- [ ] `flags` is present — empty array is valid; do not omit.
- [ ] No KNOWS edges produced here. No KnowledgeItem nodes. Output is RELATIONSHIP
      edges only.