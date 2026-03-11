---
name: pov-consistency-maintenance
description: Audits scene drafts for POV discipline violations — head-hopping, omniscient intrusions, knowledge violations, voice inconsistency, external self-description. Use after Scene Construction. Outputs consistency report with flagged violations and correction notes. Does not rewrite.
---

# POV Consistency Maintenance

## Identity

**Skill name:** `pov-consistency-maintenance`
**Purpose:** Verify that the scene draft produced by Scene Construction holds POV discipline with complete consistency — no access to other characters' inner states, no omniscient perspective intrusions, no actions taken on knowledge the POV character does not have, no drift from the established voice profile, and no description of the POV character's own face or expression from outside. Every violation is flagged with a specific location in the text and a concrete correction note. The main agent decides whether to accept the scene or re-invoke Scene Construction.

> **Sibling skills:** This skill audits output from [scene-construction](../scene-construction/SKILL.md). The voice profile it checks against is produced by [character-voice-differentiation](../../character/character-voice-differentiation/SKILL.md).

---

## Core

Verify Scene Construction output for: head-hopping, omniscient narration intrusions, knowledge violations (character acts on information they do not have), voice inconsistency against the voice profile, and external self-description errors. Output a consistency report — flagged violations with specific line references and correction notes. Does not rewrite the scene. Main agent decides whether to re-invoke Scene Construction with corrections.

---

## Input

The main agent provides:

1. **Draft scene from Scene Construction** — the complete draft prose to be audited.

2. **POV character voice profile** — the sub-record of Module 1.1. Five dimensions: vocabulary range, sentence structure patterns, observational focus, internal thought patterns, emotional processing style. The voice profile is the reference standard for voice inconsistency checks.

3. **World Bible excerpt — Module 1.2 (Character Knowledge Matrix):** What the POV character currently knows, suspects, believes (possibly falsely), and does not know. This is the reference standard for knowledge violation checks.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Consistency report** — a structured audit document:

### 1. Audit Header

- POV character audited.
- Scene summary (one sentence — orientation only).
- Overall status: `CLEAN` (no violations found) or `VIOLATIONS FOUND` (N violations of M types).

A `CLEAN` report is a complete and valid output. The main agent accepts the scene and proceeds.

### 2. Violation Log

Present only when status is `VIOLATIONS FOUND`. One entry per violation. Each entry contains:

- **Violation type** — one of the five categories (see below).
- **Location** — a specific text reference: the offending sentence or phrase, quoted directly. Do not refer to line numbers (they may not be stable); quote the text.
- **What the violation is** — a precise description of the problem. "This sentence accesses Vara's interior state" is not precise enough. "This sentence states that Vara 'was concealing her relief' — Caradhen cannot know what Vara is concealing; this is access to her interior state" is precise.
- **Correction note** — a specific, concrete suggestion for how Scene Construction should rewrite or replace the offending passage to eliminate the violation while preserving the scene's intent. The correction note is not optional. Every flagged violation must have one.

Violations are grouped by type, in severity order: Knowledge Violations first (most damaging to narrative integrity), then Head-Hopping, then Omniscient Intrusions, then External Self-Description, then Voice Inconsistency.

### 3. Summary Note *(optional, present only when violations are found)*

If a pattern is visible across multiple violations — e.g. a systematic drift in the voice profile under a particular kind of scene content, or a recurring tendency toward a specific intrusion type — note it briefly. This helps Scene Construction address the root cause rather than patching individual instances.

---

## The Five Violation Categories

### Category 1 — Knowledge Violations

**Definition:** The POV character acts on, references, reacts to, or is affected by information that Module 1.2 records them as not having. This includes information they DO NOT KNOW and also information they BELIEVE falsely — if a character believes a false thing, the scene must render their belief in the false thing, not the true thing.

**What to check:** Every piece of information in the scene that shapes the POV character's behaviour. For each: does Module 1.2 record this character as knowing, suspecting, believing, or not knowing it? If a character responds to something as though they know it, and Module 1.2 says they do not know it, that is a knowledge violation.

**Subcategories:**
- *Direct knowledge violation:* The character is stated to know, understand, or be aware of something they DO NOT KNOW.
- *Inference overreach:* The character draws an inference that would only be available to someone with information they lack. There is a spectrum here — reasonable inference from available data is not a violation; inference that requires access to unavailable data is.
- *False belief not honoured:* Module 1.2 records a BELIEVE (possibly false) status, but the scene renders the character acting on the true version of events rather than their false belief.

**Correction approach:** In most cases, the correction is to replace the statement of knowledge with a statement of inference, suspicion, or the character acting on their false belief as though it were true. The scene's surface can often be preserved; only the epistemic framing needs to change.

### Category 2 — Head-Hopping

**Definition:** The prose accesses the internal state — thoughts, feelings, intentions, motivations — of any character who is not the POV character, and this access is not inferrable from observable external behaviour.

**The inference threshold:** This is the most judgment-intensive of the five categories. Some interiority is inferrable from behaviour, and a skilled POV narrator can render that inference without head-hopping. The test is: *Could the POV character reasonably form this inference from what they can observe?* If the POV character is perceptive, they will form more inferences; if they are naive or distracted, fewer. The inferences must be consistent with this character's established perceptiveness and interpretive style.

**What is not head-hopping:**
- "Something in the angle of his shoulders suggested he was not as calm as he appeared." (Observable behaviour; plausible inference from an observant POV character.)
- "She smiled, and the smile did not reach her eyes." (Observable behaviour rendered through POV perception.)
- "He thought she looked like someone who had already decided." (A specific inference from external behaviour; the POV character's interpretation, not a report of Vara's actual interior state.)

**What is head-hopping:**
- "Vara was relieved." (States her interior state directly — no inference mechanism.)
- "He did not know that she had already decided." (Requires an outside observer to know both that he doesn't know and that she has decided.)
- "She was thinking about the assessment brief." (States the content of her thoughts directly.)

**Correction approach:** Replace the direct interior-state access with the POV character's observation of external behaviour and their inference from it. Preserve the intended meaning — the reader still understands what Vara is feeling — but route it through the POV character's perception and interpretive apparatus.

### Category 3 — Omniscient Narration Intrusions

**Definition:** A narrative observation or statement that requires a perspective positioned above or outside the POV character — a god's-eye view that neither character nor reader can occupy from within this POV.

**Common forms:**
- Statements about what neither character knows: "Neither of them realised what was beginning." (Who is the observer who knows what neither of them realises?)
- Statements about the future from a position of narrative knowledge: "This would be the last time they met." (The POV character cannot know this; neither can any in-scene observer.)
- Statements about what is happening elsewhere simultaneously: "While Caradhen waited, in the capital Aldric was signing the order." (The POV character cannot perceive this.)
- Narrative commentary that positions the reader outside the POV's perception: "What Caradhen did not understand was..." (The POV character cannot report what they do not understand from outside their own ignorance.)

**What is not an omniscient intrusion:** The POV character can anticipate, dread, speculate, and wonder. "He did not think they would meet again" is not an omniscient intrusion — it is the character's belief, rendered as their belief. "He did not know they would never meet again" is an intrusion — it implies an external observer who knows the future.

**Correction approach:** Reroute the observation through the POV character's perception, belief, or inference. What the character can experience — dread, intuition, premonition — can carry the same emotional content without requiring an external observer.

### Category 4 — External Self-Description

**Definition:** The POV character describes their own face, expression, or physical appearance from the outside — as another character or an external observer would see them.

**What this prohibits:**
- "His face darkened." (Caradhen cannot see his own face.)
- "She felt her expression harden." (She can feel muscular tension; she cannot see her expression.)
- "He looked pale." (He cannot observe his own pallor.)

**What is permitted:** The POV character experiences their own body from the inside. Physical sensation, proprioception, and autonomic response are all available.
- "Something tightened in his jaw." (Muscular tension — proprioceptive, not visual.)
- "She felt the blood leave her face." (Physical sensation — not visual self-observation.)
- "His hands had gone very still." (He can observe his own hands.)
- "The headache arrived behind his left eye." (Internal physical experience.)

**Correction approach:** Replace the external self-observation with the equivalent internal physical sensation. In almost all cases, the internal experience is more vivid and more immediate than the external description it replaces.

### Category 5 — Voice Inconsistency

**Definition:** Prose that has drifted from the POV character's established voice profile — vocabulary that does not match their range, sentence structures that contradict their established patterns, observational targets that fall outside their established focus, or emotional processing that contradicts their established style.

**How to assess:** Compare the flagged passage to the voice profile's five dimensions:
- *Vocabulary:* Is the word choice consistent with this character's established range? Does it reach for words this character would not use?
- *Sentence structure:* Does the syntax match their established patterns for this emotional register? (A character whose voice profile specifies compression under stress should not be producing long subordinated sentences in an Urgent-register scene.)
- *Observational focus:* Is the character noticing things that fall outside their established attention patterns? (A character who notices power geometry noticing decoration instead is a voice drift unless it is deliberate and motivated.)
- *Internal thought patterns:* Is the character reasoning in their established mode — image-based, logical, associative — or in a generic mode?
- *Emotional processing:* Is the character handling their emotion in their established way, or has the narration slipped into a generic emotional register?

**Important calibration:** Voice under extreme stress is legitimately different from baseline voice. The voice profile should specify how the voice changes under pressure; a character whose baseline is long and deliberate may have short declaratives as their stressed mode. Distinguish between voice inconsistency (the voice doesn't match the profile) and voice drift under stress (the voice is changing in ways not specified in the profile). Only flag the former as a violation; the latter may warrant a note in the Summary section.

**Correction approach:** Rewrite the flagged passage to restore the voice profile parameters for this character in this emotional register. The scene's content can often be preserved; the rendering must change.

---

## Boundary

- **Does not rewrite the scene.** Flags violations and provides correction notes; Scene Construction executes the rewrite.
- **Does not audit for prose quality, rhythm, or craft beyond POV discipline.** Sentence trimming, rhythm improvement, and line-level polish are Self-Editing and Refinement's domain.
- **Does not audit for conflict weight.** That is Conflict Layering's domain.
- **Does not audit continuity across chapters.** This skill audits a single scene. Full chapter-level POV consistency audit (across all scenes in a chapter) is POV Consistency Auditing's domain (Group 7).
- **Does not make plot decisions.** If a knowledge violation is found, the correction note specifies how to fix the epistemic framing — not whether the information should be known or how the character should react.
- **Does not update the World Bible.** Output is an audit report returned to the main agent.

---

## Invocation

The main agent invokes POV Consistency Maintenance:

- After every Scene Construction invocation, before the scene is accepted. This skill always runs after Scene Construction.
- A `CLEAN` report means the scene passes; the main agent accepts the draft and proceeds to the next step (Conflict Layering if flagged, Layering History and Legend if applicable, or the next scene in the chapter).
- A `VIOLATIONS FOUND` report means the main agent re-invokes Scene Construction with the correction notes as additional input. The corrected draft is then re-submitted to POV Consistency Maintenance.

**Standard post-scene-construction sequence:**  
`Scene Construction → POV Consistency Maintenance → [if VIOLATIONS FOUND: back to Scene Construction] → [if CLEAN: next step]`

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 (Character Directory — POV character voice profile sub-record), Module 1.2 (Character Knowledge Matrix — current POV character) |
| **Main agent writes to** | Nothing — consistency report is returned to the main agent; no World Bible update occurs |

---

## Dependencies

**Upstream:** **Scene Construction** (draft scene required). Module 1.1 voice profile and Module 1.2 must be current.
**Downstream:** A `CLEAN` report clears the scene for the next step. A `VIOLATIONS FOUND` report triggers re-invocation of **Scene Construction** with correction notes. After all scenes in a chapter are clean, the completed chapter draft proceeds to **Layering History and Legend** (optional), then **Self-Editing and Refinement**, then **POV Consistency Auditing** (chapter-level).

---

## Instructions

### POV Consistency Audit Workflow

Copy this checklist and track your progress:

```
POV Consistency Audit Progress:
- [ ] Step 1: Read voice profile and knowledge matrix (before draft)
- [ ] Step 2: Read draft for knowledge violations (epistemic check)
- [ ] Step 3: Read draft for head-hopping (inference threshold check)
- [ ] Step 4: Read draft for omniscient intrusions
- [ ] Step 5: Read draft for external self-description
- [ ] Step 6: Read draft for voice inconsistency
- [ ] Step 7: Assemble and return consistency report
```

---

### Step 1 — Read the voice profile and knowledge matrix before reading the draft

Do not read the draft first. Read the voice profile (Module 1.1 sub-record) and the knowledge matrix (Module 1.2) first. These are the reference standards; the audit compares the draft against them. Reading the draft before establishing the reference standards risks normalising violations because they appear within a coherent-seeming draft.

Identify from the voice profile:
- The character's vocabulary range and any specific markers (words they reach for, words they do not use)
- Sentence structure patterns per emotional register
- What they notice and what they miss
- How they process emotion internally
- Their stressed-voice variant (how the profile changes under pressure)

Identify from the knowledge matrix:
- Everything flagged DOES NOT KNOW — these are the hard prohibition on the POV character's access to information
- Everything flagged BELIEVES (possibly false) — the character acts on their false belief; the scene must honour this
- Everything flagged SUSPECTS — the character may infer toward these but cannot treat them as known

### Step 2 — Read the draft for knowledge violations

Read the scene draft with Module 1.2 active as a reference. For every piece of information that shapes the POV character's behaviour or narration:

Ask: *Is this information within the character's epistemic access?*
- If KNOWS: permitted. The character can reference, act on, and respond to this freely.
- If SUSPECTS: permitted with appropriate hedging. The character infers, guesses, reads between lines. They do not treat it as confirmed.
- If BELIEVES (possibly false): the scene must render the character acting on the false belief as though it were true. If the scene renders the true version instead, flag it.
- If DOES NOT KNOW: the character cannot reference, respond to, or be affected by this information in any way. Any passage where they appear to be affected by it is a knowledge violation.

Flag every violation. Be specific in the quotation and precise in the description.

### Step 3 — Read the draft for head-hopping

Read the draft again, now attending specifically to every passage that concerns a character other than the POV character. For each:

Apply the inference threshold: *Can the POV character reasonably infer this about the other character from what they can observe? Is this inference consistent with the POV character's established perceptiveness and interpretive style?*

If the passage directly states the other character's interior state without routing through inference or observable behaviour: flag it.
If the passage makes an inference that is plausible given the POV character's observational capacity: not a violation.
If the inference would require information the POV character does not have access to: knowledge violation, not head-hopping — record it in Category 1.

### Step 4 — Read the draft for omniscient intrusions

Read the draft again, now attending to statements that require an external or above-the-action perspective. Flag any:
- Statements about what neither character knows
- Statements that position the reader outside the POV's perception ("What Caradhen did not realise was...")
- Statements of narrative futurity that require an outside observer to know the future
- Statements about events happening elsewhere simultaneously and outside the POV character's perception

Distinguish these from the POV character's internal speculation about the future (permitted) or their intuition about something they cannot verify (permitted with appropriate epistemic hedging).

### Step 5 — Read the draft for external self-description

Read the draft again, attending specifically to passages about the POV character's own physical appearance. Flag any passage where the character observes their own face, expression, or overall appearance as though from outside.

Check: does the passage route through internal physical sensation and proprioception (permitted) or through external visual observation (prohibited)?

### Step 6 — Read the draft for voice inconsistency

Read the draft again, now holding the voice profile as the active reference. For each paragraph, check the five dimensions:
- Does the vocabulary match the established range for this character in this emotional register?
- Does the sentence structure match the established pattern for this character under this level of stress?
- Are the observational targets within the established focus?
- Is the internal processing mode consistent with how this character thinks?
- Is the emotional processing consistent with this character's established style?

Flag passages where the answer is no. Apply the calibration distinction: is this a genuine inconsistency with the profile, or is it a legitimate stressed-voice variant that the profile accounts for? Only flag the former.

If a passage shows voice drift that is not a clear violation but is a tendency worth noting (e.g. a sustained middle section where the character's specific vocabulary markers are absent), include it in the Summary Note rather than the Violation Log.

### Step 7 — Assemble and return the consistency report

Group violations by category in severity order. For each violation, write:
- The type
- The offending text, quoted
- The precise description of the violation
- A specific, concrete correction note

If no violations were found: return a `CLEAN` report with the audit header only. No further content is needed.

If a pattern note is warranted: add the Summary Note after the Violation Log.

Return the complete report to the main agent.

---

## Example

See [references/EXAMPLES.md](references/EXAMPLES.md) for input/output examples and quality checklist.
