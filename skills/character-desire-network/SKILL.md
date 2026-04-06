---
name: character-desire-network
description: >
  Step 1 of 3 in the character integration chain. Maps the structural
  relationships between all characters' core desires — which desires are
  compatible (characters can use each other), conflicting (one's success
  requires the other's failure), or invisible (not yet in contact but will
  collide when they converge). Produces a desire network document consumed
  by character-knowledge-expansion and character-relationship-matrix. Pure
  analysis — no KG writes.
---

# Character Desire Network

## Identity

**Position in chain:** Step 1 of 3. Runs first. Its output is the analytical
scaffold that steps 2 and 3 both consume.

**Single task:** Map the structural relationships between all characters'
core desires. Determine how each character's pursuit of what they want
affects every other character's ability to get what they want.

---

## Input

From KG context assembled by `character_subagent` before the chain runs:

| Key | Description |
|---|---|
| `character_nodes` | Full Character node records for all characters being integrated — `core_desire`, `core_fear`, `core_wound`, `self_deception`, `response_patterns` required |
| `faction_nodes` | Current Faction nodes — power structures that shape what characters can realistically pursue |
| `active_plot_thread_nodes` | Active PlotThread nodes — convergence windows that indicate when invisible pairs will collide |

---

## Output

A `desire_network` document. Not a KG record — an analytical intermediate
passed to steps 2 and 3 via the chain's input dict.

```json
{
  "desire_network": {
    "pairs": [
      {
        "character_a_id": "char_<slug>",
        "character_b_id": "char_<slug>",
        "relationship_type": "compatible | conflicting | invisible",
        "description": "<specific: what A wants, what B wants, why this creates compatibility/conflict/invisibility>",
        "convergence_note": "<when will invisible pairs collide; what will make latent conflict active>"
      }
    ],
    "key_tensions": "<1–2 sentences identifying the most load-bearing structural conflicts in the cast>",
    "notes": "<anything that doesn't fit the pair structure — e.g. a three-way desire entanglement>"
  }
}
```

Every character pair must be covered. For N characters, that is N*(N-1)/2 pairs.
A pair with no relationship of interest is still noted as `"compatible"` with
a brief description — do not omit pairs.

---

## The three pair types

**Compatible:** The two characters want different things and can use each other
to get them. Their desires do not collide. One may exploit the other, but the
exploitation is not structurally guaranteed to become conflict.

**Conflicting:** One character's success at pursuing their core desire structurally
requires the other to fail, or they are competing for a scarce resource (power,
a specific person's loyalty, a piece of information, control of a location).
This conflict may be known to both, known to one, or unknown to either.

**Invisible:** The two characters' desires do not currently interact — they are
in different locations, different factions, different information worlds. But
their trajectory, given active plot threads and the political map, will bring
them into contact. When they converge, will it be compatible or conflicting?
State your assessment.

---

## Key constraint

Derive every pair description from the specific `core_desire` fields of the
Character nodes. Do not describe generic relationship types — name what each
character actually wants and why that specific want creates this specific
structural relationship with this specific other character.

**Weak:** "Caradhen and Vara are in conflict because they are on opposite sides."
**Strong:** "Caradhen's desire to preserve the passes intact without commitment
conflicts with Vara's desire to return to Aldric with a concrete agreement —
she cannot succeed without him committing, and commitment is precisely what
his thirty-year survival pattern prohibits."

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality checks

- [ ] Every character pair is covered — no pairs omitted.
- [ ] Every description names the specific core desires involved, not generic relationship labels.
- [ ] `invisible` pairs include a convergence assessment — not just "they haven't met yet."
- [ ] `key_tensions` identifies the most load-bearing conflicts for downstream skills to prioritise.
- [ ] No KG records produced. No KNOWS edges. No RELATIONSHIP edges. Output is the desire network document only.