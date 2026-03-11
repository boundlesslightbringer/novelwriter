---
name: gardener-plotting-system
description: Drives scene-by-scene discovery by identifying the POV character's goal, the obstacle in the way, the choice they face, and the consequence that will open the next scene. Operates entirely from character logic — never from structural templates or pacing schedules. Invoked by the main agent at the start of every new scene, before Scene Construction. Outputs scene parameters only.
---

# Gardener Plotting System

## Identity

**Purpose:** Determine what happens next in the story — not by consulting a plan, but by asking what the POV character would do next given who they are, what they know, what they want, and what just happened to them. The output is the set of parameters that Scene Construction needs to write the next scene.

---

## Core

Drive scene-by-scene discovery by identifying the current POV character's goal, the obstacle in the way, the choice they face, and the consequence that will open the next scene. Operates from character logic, not structural template. The scene that emerges must follow inevitably from who the character is — not from what the plot needs. Outputs scene parameters only; does not write prose and does not determine pacing.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 1.1 (Character Directory):** Current state of the POV character — emotional state, active desires, active fears, location, physical state, arc stage. Must be the post-last-chapter state, not an earlier snapshot.

2. **World Bible excerpt — Module 1.2 (Character Knowledge Matrix):** What the POV character currently knows, suspects, believes (possibly falsely), and does not know. This is the epistemic ground the scene must operate within — the POV character can only act on what they know.

3. **World Bible excerpt — Module 2.3 (Plot Thread Registry):** Active and dormant threads involving this POV character, with their current status and expected convergence windows.

4. **World Bible excerpt — Module 4.1 (Consequence Ledger — Event→Consequence Chains):** Active consequences affecting this POV character — immediate consequences already in play, short-term consequences imminent, and any consequence bombs that may be approaching detonation.

5. **Most recent scene outcome** — a brief summary (2–5 sentences) of what happened in the previous scene: what the POV character attempted, what obstacle they encountered, what choice they made, and what the immediate result was. This is the direct causal input to the next scene's goal.

6. *(Optional)* **Pacing guidance** — if the Pacing skill has been invoked for this character's current psychological state, its recommended scene rhythm, interiority level, and sentence density are passed in here. Scene parameters should be consistent with the pacing guidance.

7. *(Optional)* **World Bible excerpt — Module 2.4 (Pending Payoffs):** If the main agent wants to check whether the next scene is a natural opportunity to pay off a planted setup or activate a consequence bomb, the Pending Payoffs register is passed in.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Scene parameters** — a structured document passed directly to Scene Construction:

1. **POV character** — confirmed, with current arc stage and dominant emotional state.

2. **Scene goal** — what the POV character is trying to achieve in this scene. Must be derived from their active desires and the outcome of the last scene. Specific and character-grounded — not "advance toward the endpoint," but the concrete, immediate thing this specific person wants right now.

3. **Obstacle** — what stands between the POV character and their scene goal. The obstacle must be genuine — it must actually prevent the goal from being achieved trivially. It must arise from: the world state (external), other characters (interpersonal), the POV character's own psychology (internal), or — at its most powerful — a combination of all three. Internal obstacles derived from the character's core wound, self-deception, or values under pressure are especially encouraged; they are the engine of character-driven plot.

4. **The choice** — what decision the POV character faces as a result of the obstacle. Every scene ends with a choice. The choice must be genuine — both options carry real cost; there is no obviously correct answer. The choice should, wherever possible, test the character's core contradiction: one option aligns with their stated values; the other aligns with their actual behaviour under pressure. A choice with no cost is not a choice — it is a formality.

5. **Projected consequence** — what the outcome of the choice is likely to produce, regardless of which option the POV character takes. This is not a locked plot event — it is the consequence shape: the type of consequence that follows from this choice being made at all. The consequence opens the next scene; it does not close this one.

6. **Character logic audit** — a brief statement (2–4 sentences) confirming that the scene parameters follow from the POV character's psychology as established in Module 1.1. This is the key test: *Would this specific character, in this specific situation, with this specific knowledge state, be pursuing this goal, facing this obstacle, and making this choice?* If the answer is no — if the scene is being driven by what the plot needs rather than what the character would do — the parameters must be revised before passing to Scene Construction.

7. **Active thread and consequence flags** — a list of which active plot threads and live consequences are touched by this scene. Not resolved — touched. These flags tell the main agent what World Bible records may need updating after Scene Construction returns the draft.

8. *(If Module 2.4 was provided)* **Foreshadowing opportunity note** — whether this scene is a natural moment to pay off a pending payoff, advance a Chekhov's gun toward readiness, or plant a new setup element. This is a flag for the main agent and for Scene Construction — not an instruction to force the foreshadowing.

---

## Boundary

- **Does not** write prose. Scene parameters are structural, not narrative.
- **Does not** determine pacing. Pacing is a separate skill invoked when the POV character's psychological state has shifted significantly; this skill receives pacing guidance as an optional input and respects it.
- **Does not** plan multiple scenes in advance. One scene at a time. The Gardener principle applies: the scene that emerges will produce a new scene outcome, and the next invocation of this skill will discover the scene after that.
- **Does not** assign POV characters to upcoming chapters. That is Multiple POV Structure's domain.
- **Does not** audit narrative braiding or thread convergence at the sequence level. That is Braided Narrative Technique and Plot Thread Tracking's domain.
- **Does not** update the World Bible. Output goes to the main agent and then to Scene Construction; the main agent updates the World Bible from the scene draft.
- **Does not** override character logic in the service of plot convenience. If the character would not plausibly pursue the goal, face the obstacle, or make the choice, the parameters must change. The Character Logic Audit is non-optional.

---

## Invocation

The main agent invokes Gardener Plotting System:

- At the start of every new scene, before Scene Construction is invoked.
- After the main agent has updated the World Bible from the previous scene's draft — so that Module 1.1, Module 1.2, and the Consequence Ledger reflect the current post-scene state before new parameters are generated.

**Standard scene-start invocation sequence:**  
`Gardener Plotting System → [Pacing if character state has shifted] → Scene Construction → POV Consistency Maintenance`

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 (Character Directory — current POV character), Module 1.2 (Knowledge Matrix — current POV character), Module 2.3 (Plot Thread Registry — active threads for this POV), Module 4.1 (Consequence Ledger — active consequences for this POV). Optionally: Module 2.4 (Pending Payoffs). |
| **Main agent writes to** | Nothing — scene parameters are passed to Scene Construction; the main agent updates the World Bible from the resulting scene draft, not from this skill's output. |

---

## Dependencies

**Upstream:** World Bible must be updated after the previous scene before this skill is invoked. Optionally: **Pacing** (if invoked for this character's current psychological state, its guidance is passed in). **Multiple POV Structure** determines which POV character is next — this skill then generates parameters for that character.  
**Downstream:** Scene parameters are passed directly to **Scene Construction**. The `Active thread and consequence flags` in the output are used by the main agent to know which World Bible records to update after Scene Construction returns the draft.

---

## Instructions

### Step 1 — Establish the character's current state

Read Module 1.1 for the POV character. Identify:
- **Active desire:** What are they pursuing right now — not their deep core desire, but the specific immediate thing they want in the chapter that follows this scene?
- **Active fear:** What are they trying to avoid or suppress?
- **Emotional state:** What is the dominant emotional register they are operating from?
- **Arc stage:** Where are they in their arc? Has the arc advanced since the last scene?
- **Physical state:** Are they injured, exhausted, under physical constraint? Physical state shapes what is possible.

Then read Module 1.2 for the POV character. Map their knowledge state: what do they know, what do they falsely believe, and — crucially — what do they not know that the reader knows? This epistemic map is the constraint on the scene: the POV character cannot act on information they do not have.

### Step 2 — Read the last scene outcome

The last scene outcome is the direct causal input to the next scene's goal. Ask:
- What did the character try to do?
- What stopped them, or complicated what they achieved?
- What choice did they make?
- What is the immediate result that they are now living with?

The scene goal for the next scene must follow causally from this result. A scene goal that ignores the last scene outcome is a structural break in the story's chain of cause and consequence.

### Step 3 — Derive the scene goal from character logic

The scene goal is not what the plot needs to happen. It is what this specific character, in their current state, with their current knowledge, would be attempting to do next.

Ask: *Given what just happened and who this character is, what is the first thing they would do? What would they want? What would they move toward or away from?*

The scene goal must be:
- **Specific and concrete** — not "survive" or "find a way forward," but the specific action or outcome this character is pursuing.
- **Character-grounded** — derivable from their active desires, emotional state, and core psychology; not assigned by structural need.
- **Achievable in a single scene** — the goal is scene-level, not chapter-level or arc-level.

### Step 4 — Identify the obstacle

The obstacle must prevent the scene goal from being achieved trivially. The most powerful obstacles are layered: external circumstances + interpersonal resistance + internal psychological resistance. An obstacle that is only external (the door is locked) is thin. An obstacle that is also internal (the character could ask for help, but their self-deception tells them asking for help means admitting weakness) is where story actually lives.

Sources of obstacle:
- **External:** World state, physical environment, other characters' goals that conflict with this one.
- **Interpersonal:** Another character who is also pursuing something, and whose pursuit puts them in the way.
- **Internal:** The POV character's own core wound, self-deception, values under pressure, or response patterns. What part of who they are makes this harder than it should be?

The best obstacle is one that could only be in this character's way — not a generic plot obstacle, but one that arises specifically from who this character is and the specific situation they are in.

### Step 5 — Construct the choice

The choice is what the character faces when the obstacle stops them. It must be genuine:
- **Both options carry cost.** If one option is obviously correct, it is not a choice — it is a problem with an answer.
- **Neither option is safe.** The character cannot step around the choice; they must go through it.
- **The choice tests the core contradiction.** One option aligns with their stated values or their self-image; the other aligns with how they actually behave when pressure is real. The most revealing choices are ones where the character must decide, right now, which version of themselves they actually are.

The scene does not specify which option the character takes — that is discovered in Scene Construction, through the act of writing. The Gardener plots the fork in the road; the act of writing reveals which path the character actually walks.

### Step 6 — Project the consequence shape

The consequence is not the result of the choice — it is the consequence *shape*: the type of thing that follows from this choice being made at all, regardless of which option is selected.

Ask: *What kind of consequence does this choice produce? What has been set in motion that cannot be undone?* The consequence opens the next scene. It does not resolve this one. It is the story's momentum — the reason there is something to write next.

Check the Consequence Ledger: are any active consequence chains about to advance because of this scene? Are any consequence bombs approaching detonation? If so, note them in the active flags.

### Step 7 — Perform the character logic audit

Before assembling the output, run the audit:

*Is every element of these scene parameters — the goal, the obstacle, the choice, the consequence — derivable from who this character is, what they know, and what just happened to them?*

If the honest answer is no — if any element is driven by what the plot needs rather than what the character would do — stop and revise it. The audit is not a formality. It is the core operating principle of the Gardener approach: character logic drives plot, never the reverse.

Specifically test:
- Could a different character in the same situation have a completely different scene goal? (If yes: good. This goal is specific to this character.)
- Is the obstacle something only this character would find obstructing in this specific way? (If no: make it more specific to who they are.)
- Does the choice test something real about this character's psychology? (If no: the choice is a structural placeholder. Find the real version.)

### Step 8 — Flag active threads and consequences

List which Plot Thread Registry entries (Module 2.3) are touched by this scene — not resolved, but advanced, complicated, or at minimum present. List which active consequence chains from Module 4.1 are in play. These flags tell the main agent what World Bible records to examine after Scene Construction returns the draft.

### Step 9 — Add foreshadowing opportunity note (if Module 2.4 provided)

Scan the Pending Payoffs register. Is this scene a natural moment — given where the character is, what they are doing, and who else is present — to pay off a setup, bring a Chekhov's gun into focus, or plant a new element? If yes, note it. Do not force it. Scene Construction uses this as a flag, not a directive.

### Step 10 — Assemble and return scene parameters

Return the complete scene parameters document to the main agent. The main agent passes them to Scene Construction.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Scene goal is derived from the POV character's current state and the last scene outcome — not from structural need.
- [ ] Obstacle is specific to this character and this situation — not a generic plot obstacle.
- [ ] Choice carries genuine cost on both sides; at least one side tests the character's core contradiction.
- [ ] Projected consequence opens the next scene — it does not resolve this one.
- [ ] Character Logic Audit was performed and the result is explicit in the output.
- [ ] Active thread and consequence flags are present.
- [ ] No prose written. No pacing determined. No future scenes planned.
- [ ] No World Bible writes specified.
