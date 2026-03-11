---
name: character-voice-differentiation
description: Defines a distinct narrative voice profile for each POV character — vocabulary range, sentence structure patterns, observational focus, internal thought patterns, and emotional processing style. Invoked after Character Creation is complete for a character who will serve as a POV. Outputs a voice profile document used by Scene Construction as a standing reference.
---

# Character Voice Differentiation

## Identity

**Purpose:** Produce a concrete, usable voice profile for a POV character that makes their chapters feel unmistakably distinct from every other POV — not through affectation or dialect tricks, but through authentic differences in how this specific person perceives, processes, and narrates the world.

---

## Core

Define a distinct narrative voice profile for each POV character. The profile covers: vocabulary range, sentence structure patterns, observational focus (what this character notices and in what order), internal thought patterns, and emotional processing style. The profile is derived entirely from the character's psychology — voice is the surface expression of interiority, not a stylistic overlay. Output the voice profile document; do not write scenes.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 1.1 (Character Directory)** for the specific character — full psychological record including core wound, core desire, core fear, self-deception, values under pressure, and response patterns.
2. *(Optional)* **Examples of existing POV voice profiles** for other characters, so the new profile can be differentiated from them explicitly.
3. *(Optional)* **Research material** from Research Integration if the character's cultural or social context (e.g. a character from a non-literate culture, a scholar, a soldier) affects vocabulary and cognitive patterns.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

A **voice profile document** per POV character, containing the following sections:

### 1. Vocabulary Range

- **Lexical register:** Formal / informal / mixed; latinate / germanic / dialect-influenced. Specific to this character's education, class, and cultural background — not a genre default.
- **Signature vocabulary categories:** What types of words does this character reach for when describing the world? (e.g. a soldier reaches for military metaphor and spatial language; a merchant thinks in exchange and value; a character from a rural clan frames experience through weather, season, and land.)
- **What they avoid:** Vocabulary categories this character would not use — words that belong to a register, faction, or worldview not theirs.

### 2. Sentence Structure Patterns

- **Default sentence length:** Short and declarative / long and subordinated / varied and controlled. Derived from whether this character's mind moves in quick assessments or extended deliberation.
- **Structural habits:** Patterns the character's narration tends to fall into — e.g. leading with observation before interpretation, or leading with interpretation before looking for evidence; tendency to qualify, or tendency to assert; tendency to double back, or tendency to commit.
- **Under stress:** How sentence structure changes when this character is in crisis, danger, or grief. (A character who normally deliberates may compress to fragments; a character who normally speaks in quick cuts may slow and overexplain when frightened.)

### 3. Observational Focus

This is the most important section for preventing head-hopping and generating genuine POV differentiation. What does this character notice first, habitually, automatically — and what do they systematically miss or ignore?

- **Primary lens:** What is the dominant filter through which this character reads any scene? (e.g. power dynamics, physical threat assessment, social status signals, emotional subtext, aesthetic beauty, practical utility, religious significance.)
- **Secondary lens:** A secondary filter that colours observations not captured by the primary lens.
- **Systematic blind spots:** What does this character fail to register, misread, or ignore, given who they are? These are as important as what they notice — they generate dramatic irony and Knowledge Matrix tension.
- **How they read other people:** What do they look at first in another person, and what does that tell them (accurately and inaccurately)?

### 4. Internal Thought Patterns

- **Deliberative style:** Does this character reason through problems step by step, or do they arrive at conclusions by instinct and rationalise afterward? Are they aware of the difference?
- **Self-monitoring:** Does this character examine their own motivations? Are they accurate when they do? Do they lie to themselves in narration?
- **Memory intrusion:** How and when does the past surface in this character's narration — frequently, in sensory flashes, in long deliberate recall, or almost not at all?
- **Relationship to time:** Does this character narrate in the present moment, or are they always orienting toward the past or future? This affects tense-feel even within a consistent past-tense narrative.

### 5. Emotional Processing Style

- **Speed of acknowledgment:** How quickly does this character consciously register an emotion? (Some characters feel grief in the scene; others feel it three chapters later when something small breaks them.)
- **Internal expression:** How does emotion surface in narration — named directly, displaced onto physical observation, expressed through action impulse, suppressed and noted by its absence?
- **What they cannot look at:** Every character has emotional territory they cannot directly narrate. What is it for this character? How does narration behave when it approaches that territory — deflection, acceleration, sudden flatness of affect?
- **Under extreme pressure:** How does emotional processing change when the character is at their limit?

### 6. Differentiation Notes

If other POV voice profiles have been provided:

- Explicitly note where this character's voice most risks sounding like another POV character.
- Provide 2–3 specific differentiation techniques to maintain separation in practice (e.g. "Where Character A reaches for military metaphor, Character B reaches for religious frame — check every abstract noun for which register it belongs to").

---

## Boundary

- **Does not** create the character. Character Creation must be complete before this skill is invoked.
- **Does not** write sample scenes or prose demonstrations. The voice profile is a reference document, not a sample chapter.
- **Does not** make plot decisions or place the character in specific scenes.
- **Does not** update the World Bible directly. Output is a voice profile document; the main agent writes it to Module 1.1 as a sub-record of the character's entry.
- **Does not** define character psychology beyond what is already in the character record — it translates existing psychology into narrative voice. If the character record is thin, this skill cannot compensate for it.

---

## Invocation

The main agent invokes Character Voice Differentiation:

- After Character Creation is complete for any character who will serve as a POV.
- Before that character's first POV chapter is written by Scene Construction.
- When the main agent suspects voice drift has occurred across many chapters and wants to re-anchor the profile.

This skill is not invoked for non-POV characters.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 — Character Directory (full psychological record for the character) |
| **Main agent writes to** | Module 1.1 — Voice profile is stored as a sub-record of the character's Module 1.1 entry (e.g. `1.1.voice_profile`). Main agent writes from this skill's output. |

---

## Dependencies

**Upstream:** **Character Creation** — this skill requires a complete Module 1.1 character record. It cannot be run from a concept document alone.  
**Downstream:** Voice profile is stored in Module 1.1 and passed by the main agent to **Scene Construction** (as a standing reference for every POV chapter) and to **POV Consistency Maintenance** and **POV Consistency Auditing** (as the benchmark against which voice drift is measured).

---

## Instructions

Follow these steps when executing this skill.

### Step 1 — Read the full psychological record

Before touching vocabulary or syntax, read the complete Module 1.1 record for this character: core wound, desire, fear, self-deception, values under pressure, response patterns, arc type. Voice is not a stylistic choice — it is the psychological record expressed as narration. Do not proceed to voice construction until the interiority is fully understood.

### Step 2 — Derive vocabulary from psychology and social position

A character who grew up in a mercantile family in a port city has a different vocabulary pool than a character raised in a highland clan. A character with formal religious education reaches for different abstraction than a pragmatic soldier. Derive the lexical register from:

- Social class and education
- Cultural and regional origin
- Occupation and the cognitive demands of that occupation
- What the character reads, if they read at all
- What the character's circle of reference sounds like

Do not impose a register that feels characterful but is not grounded in the character's actual formation.

### Step 3 — Derive sentence structure from cognitive style

The character's deliberative style (Step 4 of this skill) determines sentence structure. A character who reasons step-by-step and checks their own assumptions tends toward longer, more qualified sentences. A character who moves by instinct and acts first tends toward shorter, more declarative sentences with rationalisation added after. A character who is internally fragmented may produce irregular syntax even when they believe they are being clear.

Map the character's default cognitive rhythm onto a sentence structure pattern. Then specify how that pattern changes under stress — crisis compresses some minds, expands others.

### Step 4 — Define the observational lens precisely

This is the section most likely to be done lazily and to produce the most damage if it is. "She notices power dynamics" is not sufficient. The question is: *What does she look at first when she enters a room, and what does that reveal and conceal?*

For each character, specify:
- The first thing they clock in a new person (status? threat? emotional state? physical capability? wealth marker?).
- The first thing they clock in a new physical space (exits? people? objects of value? signs of decay? sources of warmth or light?).
- What they almost never notice, or systematically misread, because their primary lens blocks it.

The blind spots produce dramatic irony. They are the POV filter working as it should — the reader sees what the character sees and infers what the character cannot.

### Step 5 — Map internal thought and memory patterns

Specify whether this character's internal narration includes:
- Explicit self-analysis (they examine their own motivations in narration).
- Implicit self-analysis (they narrate around their motivations; the reader infers what the character will not say).
- Active self-deception in narration (they tell themselves a story in narration that is demonstrably wrong — the reader is positioned to see through it).

Memory: specify the conditions under which past events surface. Sensory triggers? Structural parallels to the present? Certain persons or places? Or does the past almost never intrude because this character has learned not to look at it?

### Step 6 — Specify emotional processing for the character's key emotional territory

Every character has emotional material they cannot look at directly. Identify what it is for this character (derived from the core wound and self-deception). Then specify how narration *behaves* when it approaches that territory — acceleration, deflection to external observation, sudden flatness, intrusion of physical sensation without interpretation, or other pattern.

This is what makes emotional scenes feel distinct per POV. Two characters can witness the same death and have their narration behave completely differently in how it approaches and refuses to approach grief.

### Step 7 — Write differentiation notes if other profiles were provided

If other voice profiles were passed in, read them. Identify the one or two characters whose voice is most likely to blur with this one. Write explicit guidance: "The most common drift risk is between [Character A] and [Character B]. Watch for [specific element] — when narration does [X], check whether it belongs to A's cognitive pattern or B's."

### Step 8 — Return the voice profile document

Return the complete document to the main agent. The main agent writes it to Module 1.1 as a sub-record of this character's entry, and passes it to Scene Construction and POV Consistency skills when required.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Every element of the voice profile is derived from the Module 1.1 character record — nothing is imposed from outside.
- [ ] Observational blind spots are specified, not just observational strengths.
- [ ] Emotional processing covers what the character cannot look at, not just how they feel.
- [ ] No prose samples or demonstration scenes are written.
- [ ] World Bible write is correctly specified — main agent writes voice profile to Module 1.1 (not directly by the skill).
- [ ] Differentiation notes are provided if other voice profiles were supplied as input.
- [ ] The profile is specific to this character — no element could be lifted and applied to a generic character type.