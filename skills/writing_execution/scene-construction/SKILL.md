---
name: scene-construction
description: Writes a single scene in draft prose. Applies the POV character's voice profile, executes scene parameters (goal, obstacle, choice, consequence), and embeds foreshadowing organically. Use after Gardener Plotting System has produced scene parameters. Outputs draft prose only.
---

# Scene Construction

## Identity

**Skill name:** `scene-construction`
**Purpose:** Write the scene. Everything upstream — character psychology, world state, scene parameters, voice profile, pacing guidance — has been prepared by prior skills or the main agent. This skill executes the prose. It writes one complete scene in draft, entirely in the POV character's voice and perception, from the parameters it receives. The output is raw discovery material — the first full pass — not the finished product.

---

## Core

Write a single scene in draft prose. One POV character, one goal, one obstacle, one choice, one consequence. Apply the POV character's voice profile throughout — every observation, interpretation, and thought is filtered through this character's perception, vocabulary, sentence rhythms, and observational focus. Embed foreshadowing naturally where consistent with the Pending Payoffs register. Produce draft prose only; do not self-audit for POV consistency. Do not update the World Bible.

---

## Input

The main agent provides:

1. **Scene parameters** from Gardener Plotting System — POV character, scene goal, obstacle, the choice the character faces, and the projected consequence shape. These are the scene's structural skeleton. The prose discovers what happens within that skeleton; the parameters are not a script.

2. **POV character voice profile** — stored as a sub-record of Module 1.1. Five dimensions, each applied throughout the draft without exception:
   - *Vocabulary range:* The words this character reaches for and the words they never use.
   - *Sentence structure patterns:* Their natural syntactic tendencies under different states (long subordinated sentences in control; short declaratives when control is slipping; fragments under acute stress).
   - *Observational focus:* What this character notices first and what they systematically miss. The scene contains only what their attention would touch.
   - *Internal thought patterns:* How they reason, associate, and rationalise — whether they think in images, in political calculations, in physical sensation, in logical sequences.
   - *Emotional processing style:* Whether they name their emotions directly, displace them onto objects, suppress them entirely, or experience them as physical sensation.

3. **World Bible excerpt — Module 1.2 (Character Knowledge Matrix):** What the POV character currently knows, suspects, believes (possibly falsely), and does not know. This is the hard epistemic constraint on every sentence: the scene cannot contain information this character cannot access.

4. **World Bible excerpt — Module 1.1 (Character Directory):** Current physical state, location, emotional state, active desires, active fears. The character arrives at this scene as a specific person in a specific condition; the prose must reflect that condition, not a generic version of the character.

5. **World Bible excerpt — Module 2.4 (Pending Payoffs & Foreshadowing):** The register of setup elements awaiting payoff — Chekhov's guns, planted foreshadowing, consequence bombs, prophecies, in-world legends. Consulted during construction; foreshadowing is woven in only where the scene's material makes the integration genuinely organic.

6. **World Bible excerpt — Module 3.x (relevant world state):** The specific aspects of the political map, geography, cultures, magic system, or history directly relevant to this scene's location and active characters. Passed as a targeted excerpt — not the full world state, only what this scene needs to be grounded.

7. *(Optional)* **Pacing guidance** from the Pacing skill — scene rhythm register, sentence density, interiority level, dialogue-to-action ratio, chapter arc alignment note, tension flags. When provided, these parameters govern how the scene is written. When not provided, pacing is inferred from Module 1.1's emotional state and the scene parameters — but this inference is a fallback, not a substitute for Pacing skill output after a significant psychological shift.

8. *(Optional)* **Conflict Layering audit** — if a prior draft of this scene was returned as UNDERLOADED or CARRYING DEAD WEIGHT, the audit report with its specific suggestions is passed in. The new draft addresses those suggestions.

9. *(Optional)* **POV Consistency Maintenance flags** — if a prior draft was flagged for specific violations, those flags are passed in for the corrected draft.

> **Note:** This skill receives all context from the main agent. It does not access the World Bible directly.

---

## Output

**Draft prose for one scene.**

The draft:

- Is written entirely and exclusively in the POV character's voice — every observation, interpretation, and thought is filtered through who they are, what they know at this moment, and how they process the world. Not a neutral narrative voice wearing this character's name.
- Executes the scene parameters: the goal is pursued, the obstacle is genuinely encountered, the choice is faced (not resolved offscreen), the consequence opens.
- Has a clear internal shape: a beginning (the character in their current state entering the scene's situation), a middle (the obstacle fully present, the choice live), and an end (the consequence landing or opening, the scene closing on a specific image, beat, or line that gives the next scene something to push against). The ending is not a summary — it is a moment that has been written.
- Embeds foreshadowing organically where the Pending Payoffs register identifies opportunity and the scene's material is genuinely receptive. The reader must not feel the plant being made. If no opportunity is organic, no foreshadowing is inserted.
- Is draft quality — raw, unrefined, the act of discovery. It will be audited (POV Consistency Maintenance, optionally Conflict Layering) and refined in a later pass (Self-Editing and Refinement). The goal of the draft is to find what the scene is, not to perfect it. Complete discovery is more valuable than polished incompleteness.

The draft does **not** include metadata, structural notes, flagged concerns, chapter headings, POV labels, or any markup. It is prose only.

---

## POV Discipline — The Governing Craft Constraint

POV discipline is the single most consequential craft rule this skill operates under. Every sentence must pass this test before it can exist in the draft: *Can this observation, thought, or piece of information be accessed by this specific character, in this specific location, at this specific moment, given what they know?*

**What this requires:**

**Perceptual constraint.** The scene contains only what the POV character can perceive with their senses from their physical position. They cannot see through walls, cannot know what another character is thinking, cannot observe their own face or expression from the outside.

**Epistemic constraint.** The POV character acts only on information they possess — what they KNOW, SUSPECT, or BELIEVE (possibly falsely) per Module 1.2. If they do not know a secret, they cannot act as though they do. If they believe something false, they act on the false belief. The reader may understand the falseness; the character does not. This asymmetry is one of multi-POV fiction's most powerful structural tools.

**Interpretive filter.** All events are interpreted through this character's specific psychology, not neutrally. The same room, the same conversation, the same event reads differently through different psychological lenses. The scene must render this character's interpretation — their read of what is happening, their inference about what it means — not the event itself as an objective fact.

**Voice as constraint.** The narration sounds like this character's internal register. Vocabulary, sentence rhythm, observational sequence, internal processing patterns — all must match the voice profile. When the voice drifts toward a generic narrative voice, the POV has been lost.

**What this prohibits:**

- **Head-hopping:** Any access to another character's internal state — thoughts, feelings, intentions — that is not inferrable from their observable external behaviour. "She thought he was lying" is a head-hop unless the POV character is the "she." "Something in the angle of his shoulders suggested the story had more to it" is not.
- **Omniscient intrusions:** Narrative observations that require a perspective above or outside the POV character. "Neither of them knew what they were walking into" requires an observer who can see both of them from outside — the omniscient narrator who does not exist in this system.
- **External self-description:** The POV character cannot describe their own face, expression, or appearance as an observer would see it. They can report what their body feels from the inside — the tightness in their chest, the way their hands have gone cold, the specific quality of the headache behind their eyes — but not how they look.
- **Knowledge violations:** The character acting on, referencing, or being affected by information that Module 1.2 records them as not having. This is the most destructive continuity error in multi-POV fiction; once the reader detects it, trust in the narrative's internal logic is damaged.

---

## Foreshadowing in Construction

The Pending Payoffs register is consulted at the start of construction, not after. The principle is organic integration — a setup element that belongs in this scene because the scene's setting, characters, or action makes its presence logical, and that the POV character would notice because it is the kind of thing their observational focus touches.

**The test for organic integration:** Would this object, person, detail, or event be present in this scene even if it were not a setup element? If the answer is yes, it can be planted here. If the answer is no — if it is present only because it needs to be planted — the plant is forced. A forced plant is visible to the reader and worse than no plant at all.

**The voice filter:** The foreshadowing must be noticed by the POV character in character — through their specific observational focus, in their specific vocabulary, for reasons that belong to their psychology. A character who notices exits and sightlines will notice a specific door; a character who notices social power will notice who is sitting and who is standing; a character attuned to physical danger will notice the weight of a specific object on a table. The setup element enters the scene through the character's attention, not through narrative accommodation.

**When not to plant:** If no element of the Pending Payoffs register fits organically into this scene's material and this character's observational focus, nothing is planted. Leave the register open for a scene where the material is genuinely receptive. Forced foreshadowing damages the prose and the setup both.

---

## The Scene's Internal Shape

Every scene, regardless of its drama level or its structural position, has three phases that must all be written:

**Opening — the character in their situation.** Not a summary of where we are. The character, in their body, in their current state, in the specific physical and social space of the scene, at the moment the scene begins. The voice profile is established from the first sentence. The reader is in the character's head before anything has happened.

**Middle — obstacle fully present, choice live.** The scene parameter's obstacle is not mentioned or summarised — it is encountered, in real time, as the character experiences it. The scene does not skip to the choice; it lives through the obstacle. The choice, when it arrives, is not announced as a choice — the character faces it from inside their situation, without the reader needing to be told that a choice is occurring. Both options must have real cost. The scene does not tell the reader which option the character takes; the character makes the choice through the action of the prose.

**Ending — consequence opening, scene closing on a beat.** The scene does not end with a summary of what happened. It ends on a specific moment — an image, a line of dialogue, an action, a thought that the character has and then stops having. This final beat is the scene's last offer to the reader. It should do one of: create forward pull (the reader needs to know what comes next), create dread (the reader knows something the character doesn't about what this beat means), or land an emotional truth (the scene closes on the truest thing it found).

---

## Handling Discrepancies Between Parameters and Character Logic

Scene parameters come from Gardener Plotting System, which performs a Character Logic Audit before outputting. But the act of writing sometimes reveals that a parameter that passed the audit is still wrong — the character, fully in the prose, would not pursue this goal, would not make this choice, would not be in this situation.

When this occurs: **stop. Do not substitute a different goal or choice silently.** Return the discrepancy to the main agent with a brief note: what the parameters specified, what the prose revealed, and what the character's logic appears to be instead. The main agent re-invokes Gardener Plotting System with this new information. Writing a scene around a character logic violation produces prose that the story cannot support.

This is the Gardener principle at the prose level: the character wins. If writing the scene reveals that the Gardener Plotting System was wrong about the character, the character is right.

---

## Boundary

- **Produces draft prose only.** Line-by-line prose quality, trimming, and polish are Self-Editing and Refinement's domain.
- **Does not audit its own POV consistency.** The creative pass and the editorial pass must be separate. Self-auditing during construction produces a hesitant, self-interrupting draft that never commits to its discoveries.
- **Does not determine pacing independently** beyond what Pacing guidance specifies or Module 1.1's emotional state implies. Pacing skill output takes precedence.
- **Does not plot.** Scene parameters come from Gardener Plotting System. If they are wrong, the discrepancy is flagged and returned — not silently corrected.
- **Does not write more than one scene per invocation.** One scene, one POV, one set of parameters, one consequence. The main agent assembles the chapter from multiple invocations.
- **Does not layer history and legend.** Layering History and Legend is a separate pass, invoked after Scene Construction on the completed draft.
- **Does not update the World Bible.** The main agent updates relevant modules from the draft output.

---

## Invocation

The main agent invokes Scene Construction:

- After Gardener Plotting System has produced scene parameters for the POV character.
- After Pacing has been invoked, if the POV character's psychological state has shifted significantly.
- For the re-draft of a scene after POV Consistency Maintenance has returned flags or Conflict Layering has returned an audit — in which case the flags or audit report are passed as optional inputs.

**Standard scene-writing invocation sequence:**  
`Gardener Plotting System → [Pacing, if state has shifted] → Scene Construction → POV Consistency Maintenance`

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 (Character Directory — current POV character, including voice profile sub-record), Module 1.2 (Character Knowledge Matrix — current POV character), Module 2.4 (Pending Payoffs & Foreshadowing), Module 3.x (relevant world state excerpt) |
| **Main agent writes to** | Nothing directly — the main agent updates Module 2.2 (POV Chapter Log), Module 1.1 (character state changes), and Module 2.4 (payoffs embedded or advanced) from the draft output |

---

## Dependencies

**Upstream:** **Gardener Plotting System** (scene parameters required). Module 1.1, 1.2, 2.4, and relevant 3.x excerpts must be current. Optionally: **Pacing** (if state has shifted); **Conflict Layering** audit (if re-drafting an underloaded scene); prior **POV Consistency Maintenance** flags (if correcting a flagged draft).
**Downstream:** Draft prose is audited by **POV Consistency Maintenance**. Optionally: **Conflict Layering** (if the main agent suspects weak conflict weight). After all scene-level passes, completed chapter draft goes to **Layering History and Legend** (optional), then **Self-Editing and Refinement**.

---

## Instructions

### Scene Construction Workflow

Copy this checklist and track your progress:

```
Scene Construction Progress:
- [ ] Step 1: Read scene parameters (goal, obstacle, choice, consequence)
- [ ] Step 2: Enter POV character's voice (vocabulary, sentence patterns, observational focus)
- [ ] Step 3: Write the opening (character in situation, voice active from sentence one)
- [ ] Step 4: Develop the obstacle through character encounter (real-time, not summary)
- [ ] Step 5: Bring the choice to a live moment (both options have real cost)
- [ ] Step 6: Write the consequence opening and close on a specific beat
- [ ] Step 7: Check foreshadowing integration (organic only, remove forced plants)
- [ ] Step 8: Flag any parameter/character logic discrepancies
- [ ] Step 9: Run quality checks (see references/EXAMPLES.md)
```

---

### Step 1 — Read the scene parameters and establish the structural skeleton

Read the scene parameters from Gardener Plotting System. Identify:
- POV character
- Scene goal (what they are pursuing, in specific character-grounded terms)
- Obstacle (what prevents trivial achievement — external, interpersonal, internal, or layered)
- The choice (what decision the character faces when the obstacle stops them; what each option costs)
- Projected consequence shape (what kind of consequence opens from this choice being made at all)

These parameters are the skeleton. Commit to them before writing a word of prose. Do not begin writing with the parameters vaguely held — understand what the scene is structurally before inhabiting it.

### Step 2 — Enter the POV character's voice

Before writing the scene's first sentence, establish the voice:
- Read the voice profile. Identify the specific vocabulary register, sentence structure patterns, observational focus, and emotional processing style.
- Read Module 1.1's current emotional state and physical condition.
- Apply any pacing guidance's register and interiority level as the frame.
- Ask: *If this character were going to open this scene with the first thing they notice, what would it be?* The answer to that question is the scene's first sentence, or close to it.

The voice must be active from sentence one. The scene does not warm up into the character's voice — the reader is in the character's head before the scene's situation is established.

### Step 3 — Write the opening

The opening orients the reader in the character's specific physical and emotional position without summarising it. The character is in a place, in a body, in a state. The opening renders this through perception — what the character notices, in the order they notice it, through their specific observational lens.

Do not open with:
- Weather descriptions not perceived through the character's specific attention
- Physical descriptions of the character from outside
- Backstory or summary of how we got here
- A stated emotional condition ("She was angry")

The opening earns the scene's situation by showing the character already inside it.

### Step 4 — Develop the obstacle through the character's encounter with it

Write through the obstacle as the character experiences it — not as a summary ("she discovered the door was locked") but as the scene of encountering it, in real time, with all of the character's perception, interpretation, and response engaged.

The obstacle should:
- Arise from the scene's specific situation, not appear as a generic complication
- Engage at least one internal component (the character's psychology making the external obstacle harder than it needs to be) where the parameters support it
- Be rendered at the level of the character's specific perception, not at the level of plot summary

Do not move through the obstacle too quickly. The scene's tension lives here. The reader needs to feel the obstacle as an obstacle.

### Step 5 — Bring the choice to a live moment

The choice must arrive as a lived moment, not an announced decision. The character faces it from inside their situation — the prose does not step back to identify that this is a choice point; it stays in the character's perception as the pressure of two options becomes unavoidable.

Honour the cost of both options. The character cannot choose the obviously correct one — there is no obviously correct one. If one option feels cost-free, the parameters were wrong; flag it and return to the main agent rather than writing past it.

The character makes the choice. It is visible in the prose. The reader may not know immediately what the choice means — that is the consequence's job.

### Step 6 — Write the consequence opening and close the scene on a beat

The consequence does not resolve the scene — it opens the next one. The final beat of the scene should be the point at which the consequence is in motion but not yet complete: the door is open; the word has been said; the action has been taken; something has changed that cannot be unchanged.

Close the scene on a specific moment — the last image, the last line, the last movement. Not a summary of the scene. Not a statement of what it meant. A concrete particular that the reader takes with them into the white space before the next scene.

Ask: *What is the most charged specific thing to end on, given what the scene found?*

### Step 7 — Check foreshadowing integration

After the draft is complete, check the Pending Payoffs register. Ask:
- Did the scene's events, setting, or character attention naturally accommodate any setup elements?
- Are any plants that were embedded forced — present only because the register required them, not because the scene's material made them organic?

If yes: remove the forced plant. An unplanted scene is better than a scene with a visible setup.

If no organic opportunity arose: note this for the main agent. The main agent does not need to force a plant; Layering History and Legend and subsequent scenes will provide other opportunities.

### Step 8 — Flag any discrepancy between parameters and character logic

If the act of writing revealed that any scene parameter was inconsistent with the character's full psychology — that the character would not pursue this goal, make this choice, or be in this obstacle — do not write past it. Stop, note the discrepancy, and return it to the main agent with a brief account of what was discovered. The main agent will re-invoke Gardener Plotting System.

### Step 9 — Return the draft

Return the complete draft prose to the main agent. Include a brief note only if there is a discrepancy flag (Step 8) or a foreshadowing note (Step 7) that the main agent needs to act on. Otherwise, return only the prose.

---

## Example

See [references/EXAMPLES.md](references/EXAMPLES.md) for input/output examples and quality checklist.
