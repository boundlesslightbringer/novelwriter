---
name: pov-consistency-maintenance
description: Audits a drafted scene for POV discipline violations — head-hopping, omniscient narration intrusions, knowledge violations, voice inconsistency against the character's voice profile, and external self-description errors. Queries the Story State KG directly for the POV character's voice profile and knowledge matrix. Returns a consistency report in artifacts. Does not rewrite. Always runs after scene-construction.
---

# POV Consistency Maintenance

## Identity

**Skill name:** `pov-consistency-maintenance`
**Purpose:** Verify that the scene draft produced by `scene-construction` holds POV discipline with complete consistency. Every violation is flagged with a specific text reference and a concrete correction note. The brain applies the quality gate to this report — a CLEAN report passes the scene; a VIOLATIONS FOUND report triggers re-delegation of `scene-construction` with the flags passed in context.

> **Sibling skills:** Audits output from `scene-construction`. The voice profile it checks against is stored in the Character node's `properties.voice_profile` sub-record, written by `character-voice-differentiation`.

---

## Core

Verify `scene-construction` output for: head-hopping, omniscient narration intrusions, knowledge violations (character acts on information they do not have), voice inconsistency against the voice profile, and external self-description errors. Return a consistency report in artifacts — flagged violations with specific text references and correction notes. Does not rewrite the scene.

---

## Input

### From brain context (`worker_request.context`)

1. **`draft_scene`** — The `draft_prose` string from `scene-construction` artifacts. Required.
2. **`pov_character_id`** — The `logical_id` of the POV character. Required.
3. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required.

### Fetched from Story State KG

The writing_subagent queries the Story State KG directly for the two reference standards this audit requires:

```
# POV character — full record including voice profile sub-record
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# POV character's knowledge matrix
query_kg_edges({from_node: pov_character_id, type: "KNOWS"},
               as_of_chapter=chapter_context)
# Fetch the KnowledgeItem nodes referenced by the KNOWS edges
```

**Critical:** Read the Character node and knowledge matrix **before** reading the draft. These are the reference standards; the audit compares the draft against them. Reading the draft first risks normalising violations because they appear within a coherent-seeming text.

---

## Output

All output is returned in `artifacts`. The consistency report is pure analysis — no KG persistence needed. The brain applies the quality gate: CLEAN passes the scene; VIOLATIONS FOUND triggers re-delegation.

### `artifacts` structure

```json
{
  "audit_header": {
    "pov_character_id": "char_<slug>",
    "scene_summary": "<one sentence>",
    "overall_status": "CLEAN | VIOLATIONS FOUND",
    "violation_count": 0,
    "violation_types_found": []
  },
  "violation_log": [
    {
      "violation_type": "Knowledge Violation | Head-Hopping | Omniscient Intrusion | External Self-Description | Voice Inconsistency",
      "offending_text": "<the specific sentence or phrase, quoted directly from the draft>",
      "description": "<precise description of what the violation is and why it is one>",
      "correction_note": "<specific, concrete suggestion for how to rewrite or replace the offending passage>"
    }
  ],
  "summary_pattern_note": null,
  "kg_context_used": {
    "character_node_found": true,
    "voice_profile_found": true,
    "knows_edges_found": 0
  }
}
```

`violation_log` is an empty array when `overall_status` is CLEAN. Violations are grouped by type in severity order: Knowledge Violations first (most damaging to narrative integrity), then Head-Hopping, then Omniscient Intrusions, then External Self-Description, then Voice Inconsistency.

`summary_pattern_note` is populated (non-null) when a pattern is visible across multiple violations — e.g. a systematic tendency to access other characters' inner states — to help `scene-construction` address the root cause rather than patching individual instances.

A CLEAN report is complete with only `audit_header` populated (no `violation_log` entries needed). A CLEAN report is a valid, complete output — it is not a failure to find violations.

---

## The Five Violation Categories

### Category 1 — Knowledge Violations (highest severity)

**Definition:** The POV character acts on, references, reacts to, or is affected by information that their knowledge matrix records them as not having. This includes information they `DOES NOT KNOW` and also information they `BELIEVES` falsely — if a character believes a false thing, the scene must render their belief in the false thing, not the true thing.

**What to check:** Every piece of information shaping the POV character's behaviour or narration. For each: what is the character's status for this information in their KNOWS edges?
- `KNOWS` — permitted.
- `SUSPECTS` — permitted with appropriate hedging; the character infers, guesses, reads between lines. They do not treat it as confirmed.
- `BELIEVES (possibly false)` — the scene must render the character acting on the *false* belief as though it were true. If the scene renders the true version instead, flag it.
- `DOES NOT KNOW` — the character cannot reference, respond to, or be affected by this information in any way.

**Inference overreach:** There is a spectrum between valid inference and knowledge violation. Reasonable inference from available data is not a violation; inference that requires access to unavailable data is. The POV character's established perceptiveness (from `voice_profile.observational_focus`) sets the upper bound on how sharp their inferences can be.

### Category 2 — Head-Hopping

**Definition:** The prose accesses the internal state — thoughts, feelings, intentions, motivations — of any character who is not the POV character, and this access is not inferrable from observable external behaviour.

**The inference threshold:** The most judgment-intensive category. Some interiority is inferrable from behaviour and a skilled POV narrator can render that inference without head-hopping. The test is: *Could the POV character reasonably form this inference from what they can observe? Is this inference consistent with the POV character's established perceptiveness from their voice profile?*

**What is not head-hopping:**
- "Something in the angle of his shoulders suggested he was not as calm as he appeared." (Observable behaviour; plausible inference.)
- "She smiled, and the smile did not reach her eyes." (Observable behaviour rendered through POV perception.)
- "He thought she looked like someone who had already decided." (The POV character's interpretation, not a report of another's actual interior state.)

**What is head-hopping:**
- "Vara was relieved." (States her interior state directly.)
- "He did not know that she had already decided." (Requires an outside observer to know both facts simultaneously.)
- "She was thinking about the assessment brief." (States the content of her thoughts directly.)

### Category 3 — Omniscient Narration Intrusions

**Definition:** A narrative observation or statement requiring a perspective positioned above or outside the POV character.

**Common forms:**
- Statements about what neither character knows: "Neither of them realised what was beginning."
- Statements of narrative futurity: "This would be the last time they met."
- Statements about simultaneous events elsewhere: "While Caradhen waited, in the capital Aldric was signing the order."
- Narrative commentary positioning the reader outside POV perception: "What Caradhen did not understand was..."

**What is not an intrusion:** The POV character can anticipate, dread, speculate, and wonder. "He did not think they would meet again" is not an intrusion — it is the character's belief, rendered as their belief. "He did not know they would never meet again" is an intrusion — it implies an external observer who knows the future.

### Category 4 — External Self-Description

**Definition:** The POV character describes their own face, expression, or physical appearance from the outside — as another character or external observer would see them.

**What this prohibits:**
- "His face darkened."
- "She felt her expression harden."
- "He looked pale."

**What is permitted:** The POV character experiences their own body from the inside — physical sensation, proprioception, autonomic response:
- "Something tightened in his jaw." (Muscular tension — proprioceptive.)
- "She felt the blood leave her face." (Physical sensation — not visual.)
- "His hands had gone very still." (He can observe his own hands.)
- "The headache arrived behind his left eye." (Internal physical experience.)

**Correction approach:** Replace external self-observation with the equivalent internal physical sensation. In almost all cases, the internal experience is more vivid and more immediate than the external description it replaces.

### Category 5 — Voice Inconsistency

**Definition:** Prose that has drifted from the POV character's established voice profile — vocabulary outside their range, sentence structures contradicting their established patterns, observational targets outside their established focus, or emotional processing contradicting their established style.

**How to assess:** Compare the flagged passage against the five dimensions of `properties.voice_profile`:
- *Vocabulary:* Is the word choice consistent with the character's established register?
- *Sentence structure:* Does the syntax match their established pattern for this emotional register? (A character whose profile specifies compression under stress should not be producing long subordinated sentences in an Urgent-register scene.)
- *Observational focus:* Is the character noticing things outside their established attention patterns?
- *Internal thought patterns:* Is the character reasoning in their established mode?
- *Emotional processing:* Is the character handling emotion in their established way?

**Important calibration:** Voice under extreme stress is legitimately different from baseline voice — the voice profile specifies the stressed-voice variant. Distinguish between voice inconsistency (the voice does not match the profile) and voice drift under stress (the voice is changing in ways not specified in the profile). Only flag the former as a violation; the latter warrants a `summary_pattern_note`.

---

## Boundary

- **Does not rewrite the scene.** Flags violations and provides correction notes; `scene-construction` executes the rewrite.
- **Does not audit for prose quality, rhythm, or craft beyond POV discipline.** That is `self-editing-and-refinement`'s domain.
- **Does not audit for conflict weight.** That is `conflict-layering`'s domain.
- **Does not audit continuity across chapters.** Audits a single scene. Full chapter-level POV audit is `pov-consistency-auditing`'s domain (Group 7, currently shelved).
- **Does not make plot decisions.** Correction notes specify how to fix the epistemic framing — not whether the information should be known.
- **Does not write to the Story State KG.**

---

## Invocation

The `writing_subagent` invokes this skill after every `scene-construction` invocation, before the scene is accepted. This skill always runs after `scene-construction`.

- A CLEAN report means the scene passes; the brain accepts the draft and proceeds to the next step.
- A VIOLATIONS FOUND report means the brain re-delegates `scene-construction` with the violation log passed in context as `pov_consistency_flags`. The corrected draft is then re-submitted to this skill.

**Standard post-scene-construction sequence:**
`writing_subagent (scene-construction)` → `writing_subagent (pov-consistency-maintenance)` → `[if VIOLATIONS FOUND: back to scene-construction]` → `[if CLEAN: next step]`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node including `voice_profile` sub-record (POV character, `as_of_chapter`); KNOWS edges and KnowledgeItem nodes (knowledge matrix for the POV character) |
| **Returns in artifacts** | Consistency report — overall status, violation log with correction notes, optional summary pattern note. No KG persistence needed |

---

## Dependencies

**Upstream:** `scene-construction` draft prose required in context. Character node with voice profile and KNOWS edges must be current in Story State KG.

**Downstream:** CLEAN report clears the scene for the next step (optionally `conflict-layering`, then `layering-history-and-legend`, then the brain creates a Chapter node via `story_state_manager`). VIOLATIONS FOUND report triggers re-delegation of `scene-construction` with the violation log in context.

---

## Instructions

### Audit Workflow

```
- [ ] Step 1: Query Story State KG — fetch Character node and knowledge matrix BEFORE reading draft
- [ ] Step 2: Read draft for Knowledge Violations (epistemic check)
- [ ] Step 3: Read draft for Head-Hopping (inference threshold check)
- [ ] Step 4: Read draft for Omniscient Intrusions
- [ ] Step 5: Read draft for External Self-Description
- [ ] Step 6: Read draft for Voice Inconsistency
- [ ] Step 7: Assemble and return consistency report
```

### Step 1 — Query the Story State KG

Query the Character node and KNOWS edges **before reading the draft**. Reading the reference standards first prevents the audit from normalising violations by reading them within a coherent-seeming context.

From the Character node, identify:
- `properties.voice_profile` — five dimensions; the reference standard for Category 5
- `properties.core_wound`, `self_deception`, and `response_patterns` — context for assessing inference plausibility

From the KNOWS edges and KnowledgeItem nodes, map:
- All items with status `DOES NOT KNOW` — hard prohibition on POV character access
- All items with status `BELIEVES` (possibly false) — character acts on the false version; the true version is a violation
- All items with status `SUSPECTS` — character may infer toward these but cannot treat them as confirmed

### Step 2 — Read the draft for knowledge violations

Read the scene draft with the knowledge matrix active as a reference. For every piece of information shaping the POV character's behaviour, check the character's status. Flag every violation with a quoted offending text and a precise description. Specify the character's actual status for the information in the correction note.

### Step 3 — Read the draft for head-hopping

Read the draft attending specifically to every passage concerning a non-POV character. For each, apply the inference threshold: *Could the POV character reasonably form this inference from observable behaviour, consistent with their established perceptiveness?* If the passage directly states another character's interior state without routing through inference or observable behaviour, flag it.

If the passage makes an inference that requires information the POV character does not have — cross-reference with the knowledge matrix — record it as a knowledge violation (Category 1), not head-hopping.

### Step 4 — Read the draft for omniscient intrusions

Attend to statements requiring an external or above-the-action perspective. Distinguish from the POV character's internal speculation about the future (permitted) or their intuition about something they cannot verify (permitted with appropriate epistemic hedging).

### Step 5 — Read the draft for external self-description

Attend specifically to passages about the POV character's own physical appearance. Check whether the passage routes through internal physical sensation and proprioception (permitted) or through external visual observation (prohibited).

### Step 6 — Read the draft for voice inconsistency

Hold the voice profile as the active reference. For each paragraph, check the five dimensions. Apply the calibration distinction: genuine inconsistency with the profile vs. legitimate stressed-voice variant that the profile accounts for. Only flag the former. If voice drift that is not a clear violation but is a tendency worth noting is found, include it in `summary_pattern_note`.

### Step 7 — Assemble and return the consistency report

Group violations by category in severity order. For each violation: quoted offending text, precise description, specific correction note.

If no violations: return a CLEAN report with `overall_status: "CLEAN"` and an empty `violation_log` array. No further content needed — CLEAN is a complete, valid output.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Character node and knowledge matrix were queried **before** the draft was read.
- [ ] `kg_context_used.voice_profile_found` is `true` before proceeding; if `false`, return `need_input`.
- [ ] Every violation entry has: type, quoted offending text (not a line number), precise description, specific correction note.
- [ ] Violations are grouped by category in severity order.
- [ ] Inference threshold was applied honestly for head-hopping — plausible inference is not a violation.
- [ ] External self-description is distinguished from internal physical sensation.
- [ ] Voice inconsistency is distinguished from legitimate stressed-voice variants.
- [ ] A CLEAN report has `overall_status: "CLEAN"` and `violation_log: []`. Nothing further required.
- [ ] No prose rewritten. Correction notes only.
- [ ] No Story State KG writes from this skill.