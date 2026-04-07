---
name: character-knowledge-expansion
description: >
  Step 2 of 3 in the character integration chain. Uses the desire network
  from step 1 to derive inter-character knowledge states — who knows what
  about whom, who believes what falsely, who suspects what, and who is
  definitively ignorant of what. Produces KnowledgeItem nodes and KNOWS
  edges for the Story State KG. The cross-referencing rule — if A KNOWS X
  about B, then B must have a DOES NOT KNOW entry for the same item — is
  the primary quality gate for this step.
---

# Character Knowledge Expansion

## Identity

**Position in chain:** Step 2 of 3. Runs after `character-desire-network`.

**Single task:** Derive the information asymmetries at story opening. Who
holds what knowledge about whom, and what does that asymmetry mean for
dramatic irony and future revelation?

---

## Input

From the chain's accumulated context:

| Key | Description |
|---|---|
| `character_nodes` | Full Character node records — `core_wound`, `self_deception`, `surface_beliefs`, `faction`, `location` |
| `existing_knows_edges` | KNOWS edges already created by `character-creation` (background facts and established false beliefs) — do not duplicate these |
| `desire_network` | Output of step 1 — especially `conflicting` pairs, which generate the most interesting knowledge asymmetries |

---

## Output

KG-ready records to be included in the chain's combined `knowledge_matrix_expansions`
artifacts field.

```json
{
  "new_knowledge_items": [
    {
      "logical_id": "ki_<description_slug>",
      "node_type": "KnowledgeItem",
      "chapter": 0,
      "properties": {
        "description": "<the specific fact, secret, or event>"
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
        "source": "<how they came to know, believe, or suspect this>",
        "dramatic_irony_flag": false
      }
    }
  ],
  "flags": [
    {
      "type": "knowledge_plausibility | missing_cross_reference",
      "description": "<specific issue>",
      "affected_characters": ["char_<slug>"]
    }
  ]
}
```

---

## The four knowledge states to populate

Work through these four states systematically, in order, for each character:

**KNOWS (inter-character):** What does this character know about another character
that creates advantage, obligation, or vulnerability? Focus on knowledge that is
not obvious from their faction membership or public role — the non-trivial things
one character knows about another that the other does not realise they know.

**BELIEVES (possibly false):** What does this character falsely believe about
another character at story start? These are the seeds of future revelation scenes.
Derive false beliefs from `self_deception` fields in the Character nodes — a
character who self-deceives in a particular way tends to project that deception
onto how they read others. Also register false beliefs from `surface_beliefs` that
contradict what other Character nodes establish as true.

**SUSPECTS:** What does this character actively suspect about another, without
confirmation? Derive from the desire network — characters in `conflicting` pairs
are more likely to carry active suspicions about each other's motives. Also
derive from `response_patterns.betrayal` — a character who responds to betrayal
by going quiet and withdrawing access rather than confronting may be carrying
ongoing suspicions already.

**DOES NOT KNOW:** For every `KNOWS`, `BELIEVES`, or `SUSPECTS` edge you create for Character A about
Character B, you must create a corresponding `DOES NOT KNOW` edge for Character B
about the same `KnowledgeItem`. This is the cross-referencing rule. Do not create
a `KNOWS`, `BELIEVES`, or `SUSPECTS` edge without its mirror `DOES NOT KNOW` edge.

---

## The cross-referencing rule

This is the most common point of failure in the original skill. State it plainly:
The cross-referencing rule applies to ALL knowledge states (`KNOWS`, `BELIEVES`, and `SUSPECTS`).

If you create a `KNOWS` edge:
  `char_caradhen → ki_vara_is_evaluating_him [KNOWS]`

You must also create:
  `char_vara → ki_vara_is_evaluating_him [DOES NOT KNOW]`
  (She does not know that Caradhen has identified what she is doing.)

If you create a `BELIEVES` or `SUSPECTS` edge:
  `char_alice → ki_bob_is_selfish_mercenary [BELIEVES]`

You must also create:
  `char_bob → ki_bob_is_selfish_mercenary [DOES NOT KNOW]`
  (Bob does not know that Alice falsely believes this about him.)

Check every edge you produce. Find the corresponding character. Create
their `DOES NOT KNOW` entry. Set `dramatic_irony_flag: true` on the edge
when the reader will know what the character does not.

---

## What not to include

- Background facts the character knows about their own history — those were created
  by `character-creation`. Check `existing_knows_edges` before creating any edge
  and do not duplicate.
- Information that will be acquired during the story — this step covers story-start
  knowledge states only.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality checks

- [ ] Every `KNOWS`, `BELIEVES`, and `SUSPECTS` edge has a corresponding `DOES NOT KNOW` edge for the other character. The cross-referencing rule applies to ALL knowledge states.
- [ ] `BELIEVES` entries include false beliefs derived from `self_deception` — not just
      obvious misunderstandings.
- [ ] `SUSPECTS` entries are derived from character psychology or the desire network —
      not invented.
- [ ] No duplicate entries vs. `existing_knows_edges`.
- [ ] `dramatic_irony_flag: true` is set on edges where the reader is in a different
      knowledge state than the character.
- [ ] `flags` array is present — empty array is valid; do not omit.