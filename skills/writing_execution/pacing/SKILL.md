---
name: pacing
description: Calibrates narrative tension by deriving the appropriate prose rhythm register from character psychology intersected with current emotional state. Use when the POV character's psychological state has shifted significantly. Outputs pacing guidance for Scene Construction.
---

# Pacing

## Identity

**Skill name:** `pacing`
**Purpose:** Translate the POV character's interior life into concrete prose-rhythm guidance — but in a way that keeps each character's voice distinct even across similar dramatic situations. Two characters in crisis are not in the same register simply because they are both in crisis. A character who intellectualises under pressure will be in Deliberate when another character in the same scene would be Urgent. A character whose baseline is emotional suppression will be Brittle where a less defended character would be Dissociative. The register emerges from the intersection of who this character is and what is happening to them — not from the situation alone. This skill performs that derivation and outputs the parameters Scene Construction needs.

---

## Core

Calibrate narrative tension at scene and chapter level by first reading the POV character's specific psychological and behavioral traits, then modulating those traits against their current emotional state and the most recent scene outcome to derive the appropriate pacing register. Tension is a function of character psychology meeting situation — not situation alone. Output pacing guidance — recommended scene rhythm register, sentence density, interiority level, and dialogue-to-action ratio — for Scene Construction to use as a parameter. Does not write prose. Does not make plot decisions.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 1.1 (Character Directory):** Two distinct sub-records are both required:

   - **Psychological and behavioral traits (baseline):** The character's habitual processing style when not under unusual stress — how they think, what they do with emotion, what their default defenses are, how they respond to uncertainty, what breaks through and what doesn't. This is the primary driver of register derivation. The critical question is: *given who this character is, how do they metabolise this kind of pressure?*
   - **Current state:** Emotional state, active desires, active fears, arc stage, physical state (injury, exhaustion, constraint). This is what the baseline is being measured against. The gap between baseline and current state is where the register lives.

2. **Most recent scene outcome:** A brief summary (2–5 sentences) of what just happened — what the character attempted, what the obstacle was, what choice they made, what the immediate result was. The scene outcome is the acute input; the psychological baseline is the persistent filter through which that input is processed. Both are necessary.

3. **Current chapter's emotional arc:** What emotional shape the chapter as a whole is building toward. Pacing within the chapter should track and amplify this arc — the register assigned to this scene must be consistent with where the chapter is going, not just where it is now.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Pacing guidance** — a structured document passed to Scene Construction as an input parameter:

### 1. Character Psychology Summary

Before stating the register, establish the derivation's foundation in 3–5 sentences: what are this character's key behavioral and psychological traits relevant to the current situation? What is their habitual response pattern under this type of pressure? What do they do with the specific emotion the scene is generating? This is not a full character summary — it is a targeted extraction of the traits that directly determine how this character's prose will move under these conditions.

This section makes the register assignment legible and reproducible. Scene Construction can trace the register back to specific character traits, which prevents generic rendering.

### 2. Scene Rhythm Register

The overall tempo of the next scene. Derived from the Character Psychology Summary intersected with the current state — not read directly from the situation.

**The derivation principle:** Identify which register this character's psychology channels their current state into. A character who responds to threat by going very still and very precise is not Urgent — they are Taut or Deliberate even under acute danger. A character whose default is analytical detachment may be Deliberate in a moment that would push another character to Reflective. A character who performs composure over genuine fracture is Brittle, not Deliberate. The situation sets the pressure; the character's psychology determines what shape that pressure takes in prose.

**The register set:**

| Register | Prose character | Derived when the character's psychology... |
|---|---|---|
| **Urgent** | Very short sentences. Fragments. Active verbs. Minimal subordination. Sensory input arrives faster than it can be processed. Thought is interrupted by event. | ...cannot maintain its habitual processing mode under the present pressure. The character's defenses or organizing systems have been overwhelmed and the prose reflects raw, unfiltered reaction. |
| **Taut** | Short-to-medium sentences. Controlled subordination. High alertness, but the control is real — it costs something. Interiority is compressed into flashes. Dialogue clipped. | ...is under sustained threat and is actively holding itself together. The control is not performance; it is genuine effort. The seams of that effort may show. |
| **Suspended** | Sentences are precise but very slow — hyper-detailed, almost over-attentive. Time seems to stretch. The character is intensely present but not yet in motion. | ...is waiting for something to happen that it cannot prevent or hasten. Hyperawareness without outlet. The body is still; the mind catalogues everything. |
| **Brittle** | Surface sentences are controlled and functional, occasionally too even. But underneath — in the interiority, in odd word choices, in what the character notices — something is wrong. The prose is performing composure while the character fractures. | ...habitually manages its presentation and is doing so now, but the thing being managed is larger than the management system can handle. The gap between surface and interior is the scene's engine. |
| **Deliberate** | Medium sentences with controlled variation. Interiority is purposeful and organised. The character is thinking in full clauses. Emotion is present but subordinated to function. | ...is genuinely in control of its processing — not performing control, but exercising it authentically. The character is capable of strategic thought, careful attention, and sequenced action. |
| **Reflective** | Long, subordinated sentences. Interiority expands and wanders. Scene time slows. Attention moves freely across memory, perception, and association with no urgent pressure to return. | ...has space or is forced into space. No immediate threat demands reaction; the character turns inward, or is held still by circumstance and turns inward involuntarily. |
| **Numb** | Very flat. Short sentences that catalogue rather than experience. Minimal interiority. External events are registered without emotional processing — not because the character is controlling the processing, but because the processing capacity has run out. | ...has been under sustained or catastrophic pressure long enough that it has simply stopped responding at full amplitude. Not dissociation — not fractured — just emptied. The character is still functional but running on residue. |
| **Dissociative** | Syntactically fractured, or paradoxically and eerily calm in the face of horror. The interpretive layer has partially failed — narration may describe things with inappropriate precision or inappropriate detachment, or may skip in ways that don't follow cause and effect. | ...has experienced something that has broken its interpretive capacity. The character is present but not fully processing. What the prose describes and what the character appears to feel are not aligned in the way they should be. |

State the register. Write the justification in 3–4 sentences, tracing it explicitly from the Character Psychology Summary through the current state to the register assignment. The justification is the most important part of this section — it is what makes the guidance character-specific rather than situational.

**On register mixing and transition:** A single scene may begin in one register and end in another. If the chapter arc requires a shift within the scene, name the trigger point: what event or realisation should cause the transition, and which register does the scene move to. Not every scene has an internal shift; most don't. But when the chapter arc demands one, name it.

### 3. Sentence Density

How much information and sensation should be packed per sentence — derived from the register and from this character's specific cognitive style (does this character's mind move in dense associative bursts, or in precise sequential steps?):

- **High density:** Multiple observations, implications, or sensations in a single clause. The character's mind is moving fast and selecting hard, or their habitual style is associative and layered. Common in Urgent, Taut, and some Deliberate characters who think in compressed analytical chains.
- **Medium density:** One clear primary observation or action per sentence, with room for one qualifying thought. Standard for Deliberate and some Reflective passages.
- **Low density:** Sentences breathe. A single image can hold a sentence. Space between sentences is part of the rhythm. Common in Reflective, Numb, and Dissociative registers, and in Suspended moments where time is stretching.

State the density and anchor it in the character's cognitive style — not just the register. Two characters in Taut register may have different sentence densities because their habitual cognitive style differs.

### 4. Interiority Level

How much of the scene's page-space is given to the POV character's internal processing — thoughts, interpretations, memory intrusions, emotional registering — versus external event, action, and dialogue.

Derive this from two intersecting factors: the character's baseline interiority level (are they habitually internal or habitually external?), and how the current state is modulating that baseline.

- **Compressed:** Interior processing is minimal — flashes, not sustained thought. Even a highly interior character may be compressed if their current state has disabled their processing or if they are deliberately suppressing it.
- **Balanced:** Interior processing is present and legible but does not dominate.
- **Expanded:** Interior processing is the scene's primary material. Common in Reflective, and in any character whose baseline is highly interior and whose current state has given them space or forced stillness.
- **Disrupted:** Interior processing is present but unreliable — fragmented, looping, or disconnected from the external events that should be triggering it. Common in Dissociative register.

State the interiority level and anchor it specifically in this character's baseline interiority pattern and how the current state is modifying it.

### 5. Dialogue-to-Action Ratio

For scenes that contain dialogue:

- **Dialogue-heavy:** Characters speak; action beats are minimal. Appropriate when the scene's conflict is interpersonal and stakes live in what is and isn't said. The character processes primarily through language.
- **Balanced:** Dialogue and action alternate. Dialogue advances; action punctuates and grounds.
- **Action-heavy / dialogue-sparse:** Characters say little. Physical action, sensation, and interior narration carry the scene. Appropriate when the character is alone, or when the character's current state has suppressed their verbal processing, or when the situation demands physical response over speech.
- **No dialogue:** The scene contains no exchange. Specify if this applies.

Consider whether this character habitually processes through speech or through action and observation. Some characters think by talking; others go silent when under pressure. The ratio should reflect both the scene's social context and this character's habitual communication pattern under stress.

### 6. Chapter Arc Alignment Note

A brief note (2–4 sentences) connecting these pacing parameters to the chapter's emotional arc. If the chapter builds toward a specific emotional climax or transition, note where this scene sits within that arc and whether the pacing should be climbing, plateauing, or descending. If there is a register shift within the scene, note its trigger here.

### 7. Tension Flags

Specific warnings for Scene Construction about rhythm problems that are predictable given this character's psychology and current state. These must be character-specific — derived from the behavioral and psychological traits in the Character Psychology Summary, not from generic writing warnings.

The three flag types to check:

- **Undercut risk:** Does this character habitually deflect, intellectualise, perform composure, or suppress emotion in ways that could flatten the scene's tension below what the situation warrants? If yes, flag the specific habit and how Scene Construction should handle it — push against it, render it as characterisation (the suppression itself is the scene's tension), or both.
- **Overdrive risk:** Does this character's baseline processing style risk producing prose that is too slow or too internal given the external urgency? Or conversely, does their habitual compression risk producing prose that is too flat to register the scene's emotional weight? Flag the specific risk.
- **Voice specificity risk:** Under the pressure of this state, what specific voice markers are most at risk of going generic? Name 1–2 concrete markers that must be preserved. Not "keep the voice distinctive" — name the specific things: the cognitive tic, the observational habit, the characteristic way of encoding a specific emotion, the syntactic pattern that belongs to this character alone.

---

## Boundary

- **Does not write prose.** Pacing outputs guidance parameters; Scene Construction writes the scene.
- **Does not make plot decisions.** The scene's events come from Gardener Plotting System. Pacing shapes how those events are rendered, not what they are.
- **Does not operate on a fixed schedule.** The main agent invokes Pacing when the POV character's psychological or emotional state has shifted significantly. A shift is significant when the character's baseline processing mode has changed — not every chapter, not every scene.
- **Does not determine scene content.** It does not prescribe what the character does, says, or decides — only the prose rhythm in which those things are rendered.
- **Does not update the World Bible.** Output is pacing guidance returned to the main agent and passed to Scene Construction.

---

## Invocation

The main agent invokes Pacing:

- When the POV character's psychological or emotional state has shifted significantly since the last scene — a major loss, a revelation that reframes their situation, a choice with immediate psychological consequences, acute physical crisis, or any event that moves the character into a substantially different interior register.
- Not on a fixed schedule. Not at act breaks. Not automatically before every scene.
- Not when the character's state is continuous with the previous scene and the pacing established by the last Scene Construction invocation remains appropriate.

**Standard invocation sequence when state shift is detected:**
`Gardener Plotting System → [Pacing, if state has shifted] → Scene Construction`

Pacing guidance is passed directly to Scene Construction as an input parameter. If no Pacing guidance is provided, Scene Construction infers rhythm from Module 1.1's emotional state field — but this inference is a fallback, not a substitute for a full Pacing analysis after a significant shift.

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 (Character Directory — current POV character: psychological/behavioral traits baseline, emotional state, desires, fears, arc stage, physical state, voice profile) |
| **Main agent writes to** | Nothing — pacing guidance is returned to the main agent and passed to Scene Construction; no World Bible update occurs |

---

## Dependencies

**Upstream:** Module 1.1 must be current (updated after the previous scene) before Pacing is invoked. Gardener Plotting System has already determined the scene parameters. The most recent scene outcome is summarised by the main agent from the previous draft.
**Downstream:** Pacing guidance is consumed as an input parameter by **Scene Construction**.

---

## Instructions

### Pacing Analysis Workflow

Copy this checklist and track your progress:

```
Pacing Analysis Progress:
- [ ] Step 1: Extract psychological/behavioral baseline (how they process pressure)
- [ ] Step 2: Read current state as pressure on the baseline
- [ ] Step 3: Derive the register from the intersection
- [ ] Step 4: Assess for register shift within the scene
- [ ] Step 5: Determine sentence density
- [ ] Step 6: Determine interiority level
- [ ] Step 7: Determine dialogue-to-action ratio
- [ ] Step 8: Write chapter arc alignment note
- [ ] Step 9: Write tension flags (character-specific warnings)
- [ ] Step 10: Run quality checks (see references/EXAMPLES.md)
```

---

### Step 1 — Extract the character's psychological and behavioral baseline

Read Module 1.1 with the specific question: *How does this character process pressure of this type?*

Do not begin with the current state. Begin with the stable psychological traits — the patterns that are present across chapters, not only in crisis:

- What is their habitual emotional defense? Do they intellectualise, suppress, perform composure, deflect into action, dissociate, over-control?
- What is their baseline interiority level — are they a highly internal processor or do they live primarily in external perception and action?
- What breaks through their defenses, and what doesn't? What kind of pressure can they hold, and what kind overwhelms their system?
- What is their characteristic cognitive style — associative, sequential, analytical, imagistic, tactical?
- How do they communicate under pressure — do they go silent, become more verbal, become more precise, become more evasive?

Write the Character Psychology Summary from this. It should be specific enough that a different character's summary would be recognisably different.

### Step 2 — Read the current state as a pressure on the baseline

Now read the current emotional state, active desires, active fears, physical condition, and scene outcome. Ask not "what is this character feeling?" but "what is this pressure doing to this character's specific processing system?"

- Is the current state within the range the character's psychology can manage with its habitual defenses? Or is it at or beyond that range?
- What is the specific form the pressure takes for this character? Grief may manifest as analytical over-function in one character and as perceptual disruption in another.
- Is the physical state (injury, exhaustion) compressing or disrupting the character's cognitive capacity?
- What did the scene outcome do specifically to this character's psychology — not just "it was bad" but what function of theirs does it impair or activate?

### Step 3 — Derive the register from the intersection

Do not look at the register table and match the situation to the nearest row. Instead, ask:

*Given what I know about how this character processes pressure, what shape does the prose take when this character is in this state?*

Then find the register that matches that shape. The register is the conclusion of the derivation, not the starting point.

A character who goes to analytical over-function under grief → Deliberate, not Reflective.
A character who performs composure over genuine fracture → Brittle, not Deliberate.
A character who responds to acute threat by going very still and very precise → Suspended or Taut, not Urgent.
A character who has exhausted their processing capacity → Numb, even if the situation is objectively urgent.

Write the justification in 3–4 sentences, tracing the derivation explicitly: from the specific psychological trait, through the way the current pressure acts on that trait, to the register.

### Step 4 — Assess for register shift within the scene

Read the chapter arc. Does the scene need to move between registers? If yes: identify the trigger point (what event, realisation, or moment of choice causes the shift) and name the destination register. If no: note that the scene holds a single register throughout.

### Step 5 — Determine sentence density

Consider two things: the derived register (which has density implications) and this character's specific cognitive style. Assign density (High / Medium / Low) and explain the assignment in one sentence, anchored in the character's habitual cognitive pattern, not just the register.

### Step 6 — Determine interiority level

Consider the character's baseline interiority level and how the current state modifies it. A highly interior character who is actively suppressing interiority is Compressed, not Expanded — the suppression itself is characterisation. A low-interiority character whose current state has forced stillness may be Expanded, which is unusual for them and should be noted as such.

Assign the level (Compressed / Balanced / Expanded / Disrupted) and explain in one sentence.

### Step 7 — Determine dialogue-to-action ratio

Consider both the scene's social context (who is present, what the scene's interpersonal dynamics are) and this character's habitual communication pattern under this type of pressure. Assign and explain briefly.

### Step 8 — Write the chapter arc alignment note

2–4 sentences connecting these parameters to the chapter's arc. Note any anticipated register shift within the scene and its trigger.

### Step 9 — Write the tension flags

Review the Character Psychology Summary for patterns that are predictable risks in this specific scene. Write the flags as character-specific, actionable warnings. Each flag should name the specific behavioral pattern and specify what Scene Construction should do about it.

### Step 10 — Assemble and return pacing guidance

Compile all sections. Return the complete pacing guidance document to the main agent, who passes it to Scene Construction.

---

## Example

See [references/EXAMPLES.md](references/EXAMPLES.md) for input/output examples and quality checklist.

---

## Register Reference Table

| Register | Prose character | Derived when the character's psychology... |
|---|---|---|
| **Urgent** | Very short sentences. Fragments. Active verbs. Minimal subordination. | ...cannot maintain its habitual processing mode under the present pressure. Defenses overwhelmed. |
| **Taut** | Short-to-medium sentences. Controlled subordination. High alertness. | ...is under sustained threat and actively holding itself together. Control costs something. |
| **Suspended** | Precise but very slow sentences. Hyper-detailed, over-attentive. Time stretches. | ...is waiting for something it cannot prevent or hasten. Hyperawareness without outlet. |
| **Brittle** | Surface controlled, underneath something is wrong. Performing composure while fracturing. | ...habitually manages presentation but the thing being managed exceeds the system. |
| **Deliberate** | Medium sentences with controlled variation. Purposeful interiority. | ...is genuinely in control — exercising it authentically, not performing. |
| **Reflective** | Long, subordinated sentences. Interiority expands and wanders. Scene time slows. | ...has space or is forced into space. No immediate threat demands reaction. |
| **Numb** | Very flat. Short sentences that catalogue. Minimal interiority. | ...has been under sustained pressure long enough that processing capacity has run out. |
| **Dissociative** | Syntactically fractured, or eerily calm in face of horror. | ...has experienced something that has broken its interpretive capacity. |
