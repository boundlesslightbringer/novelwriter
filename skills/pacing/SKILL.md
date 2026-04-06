---
name: pacing
description: Calibrates narrative tension by deriving the appropriate prose rhythm register from the POV character's psychology intersected with their current emotional state. Queries the Story State KG directly for the character's full psychological and behavioural baseline and current state. Returns pacing guidance in artifacts for scene-construction to use as a governing parameter. Invoked when the POV character's psychological state has shifted significantly — not on a fixed schedule.
---

# Pacing

## Identity

**Skill name:** `pacing`
**Purpose:** Translate the POV character's interior life into concrete prose-rhythm guidance — in a way that keeps each character's voice distinct even across similar dramatic situations. Two characters in crisis are not in the same register simply because they are both in crisis. The register emerges from the intersection of who this character is and what is happening to them — not from the situation alone. This skill performs that derivation and returns the parameters `scene-construction` needs.

> **Sibling skill:** `scene-construction` consumes this skill's output as an optional input parameter. When pacing is invoked after a significant psychological state shift, its guidance governs how `scene-construction` renders the prose.

---

## Core

Calibrate narrative tension at scene and chapter level by first reading the POV character's specific psychological and behavioural traits, then modulating those traits against their current emotional state and the most recent scene outcome to derive the appropriate pacing register. Tension is a function of character psychology meeting situation — not situation alone. Return pacing guidance in artifacts for `scene-construction` to use as a parameter. Does not write prose. Does not make plot decisions.

---

## Input

### From brain context (`worker_request.context`)

1. **`pov_character_id`** — The `logical_id` of the POV character. Required.
2. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required.
3. **`last_scene_outcome`** — 2–5 sentence summary of what just happened: what the character attempted, what the obstacle was, what choice they made, what the immediate result was. The scene outcome is the acute input; the psychological baseline (from the Character node) is the persistent filter. Both are necessary. Required.
4. **`chapter_emotional_arc`** — What emotional shape the chapter as a whole is building toward. Pacing within the chapter should track and amplify this arc. Required.

### Fetched from Story State KG

The writing_subagent queries the Story State KG directly for the character record this skill requires:

```
# POV character — full record including psychological baseline and current state
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)
```

The Character node contains both the psychological/behavioural baseline (stable across chapters: `core_wound`, `self_deception`, `response_patterns`, `arc_type`) and the current state (updated each chapter: `emotional_state`, `active desires`, `active fears`, `arc_stage`, `injuries_physical_state`). Both sub-sets are required — the baseline is the primary driver of register derivation; the current state is what the baseline is being measured against.

If the Character node is not found, return `need_input` — the record must be persisted before pacing can be derived.

---

## Output

All output is returned in `artifacts`. Pacing guidance is passed directly by the brain as context in the `scene-construction` delegation. No KG persistence needed.

### `artifacts` structure

```json
{
  "pov_character_id": "char_<slug>",
  "character_psychology_summary": "<3–5 sentences: which traits directly determine how this character's prose moves under these conditions>",
  "scene_rhythm_register": {
    "register": "Urgent | Taut | Suspended | Brittle | Deliberate | Reflective | Numb | Dissociative",
    "justification": "<3–4 sentences tracing: specific psychological trait → how current pressure acts on that trait → the register>",
    "internal_shift": {
      "present": false,
      "trigger_point": null,
      "destination_register": null
    }
  },
  "sentence_density": {
    "level": "High | Medium | Low",
    "justification": "<one sentence anchored in character's cognitive style, not just register>"
  },
  "interiority_level": {
    "level": "Compressed | Balanced | Expanded | Disrupted",
    "justification": "<one sentence anchored in character's baseline interiority and how current state modifies it>"
  },
  "dialogue_to_action_ratio": {
    "ratio": "Dialogue-heavy | Balanced | Action-heavy / Dialogue-sparse | No dialogue",
    "justification": "<one sentence: scene social context + character's habitual communication pattern under this pressure>"
  },
  "chapter_arc_alignment_note": "<2–4 sentences connecting these parameters to the chapter's emotional arc>",
  "tension_flags": [
    {
      "type": "Undercut risk | Overdrive risk | Voice specificity risk",
      "description": "<specific behavioural pattern from the character's psychology that creates this risk>",
      "instruction_for_scene_construction": "<what scene-construction should do about it — specific, not generic>"
    }
  ],
  "kg_context_used": {
    "character_node_found": true
  }
}
```

`scene_rhythm_register.internal_shift.present` is `true` only when the chapter arc requires a register change within this specific scene. When `true`, `trigger_point` names the specific event or realisation that causes the shift, and `destination_register` names the register the scene moves to.

`tension_flags` must be character-specific — naming the exact behavioural pattern from the Character node's psychology that creates the risk. Generic warnings ("keep the voice distinctive") are not valid flags.

---

## Register Reference Table

| Register | Prose character | Derived when the character's psychology... |
|---|---|---|
| **Urgent** | Very short sentences. Fragments. Active verbs. Minimal subordination. Sensory input arrives faster than it can be processed. | ...cannot maintain its habitual processing mode under the present pressure. Defences overwhelmed. |
| **Taut** | Short-to-medium sentences. Controlled subordination. High alertness — the control is real and costs something. | ...is under sustained threat and actively holding itself together. |
| **Suspended** | Precise but very slow sentences. Hyper-detailed, almost over-attentive. Time stretches. | ...is waiting for something it cannot prevent or hasten. Hyperawareness without outlet. |
| **Brittle** | Surface controlled. Underneath something is wrong — in odd word choices, in what the character notices. Performing composure while fracturing. | ...habitually manages its presentation but the thing being managed exceeds the management system. |
| **Deliberate** | Medium sentences with controlled variation. Interiority purposeful and organised. Emotion present but subordinated to function. | ...is genuinely in control — exercising it authentically, not performing it. |
| **Reflective** | Long, subordinated sentences. Interiority expands and wanders. Scene time slows. | ...has space or is forced into space. No immediate threat demands reaction. |
| **Numb** | Very flat. Short sentences that catalogue rather than experience. Minimal interiority. | ...has been under sustained pressure long enough that processing capacity has run out. |
| **Dissociative** | Syntactically fractured, or paradoxically and eerily calm in the face of horror. | ...has experienced something that has broken its interpretive capacity. |

**The derivation principle:** Identify which register this character's psychology channels their current state into. The situation sets the pressure; the character's psychology determines what shape that pressure takes in prose.

---

## Boundary

- **Does not write prose.** Returns guidance parameters; `scene-construction` writes the scene.
- **Does not make plot decisions.** Scene events come from `gardener-plotting-system`.
- **Does not operate on a fixed schedule.** The brain delegates this skill only when the POV character's psychological or emotional state has shifted significantly since the last scene.
- **Does not determine scene content.** Does not prescribe what the character does, says, or decides — only the prose rhythm in which those things are rendered.
- **Does not write to the Story State KG.**

---

## Invocation

The `writing_subagent` invokes this skill when the brain delegates pacing calibration:

- When the POV character's psychological or emotional state has shifted significantly since the last scene — a major loss, a revelation that reframes their situation, a choice with immediate psychological consequences, acute physical crisis.
- Not at act breaks, not automatically before every scene, not when the character's state is continuous with the previous scene.

**Standard invocation sequence when state shift is detected (brain-level):**
`plotting_subagent (gardener-plotting-system)` → `writing_subagent (pacing)` → `writing_subagent (scene-construction)`

Pacing guidance is passed by the brain as `pacing_guidance` in the `scene-construction` context dict. If no pacing guidance is provided, `scene-construction` infers rhythm from the Character node's `emotional_state` field — but this inference is a fallback, not a substitute for a full pacing analysis after a significant shift.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node (POV character — full psychological baseline and current state including `emotional_state`, `arc_stage`, `injuries_physical_state`, `response_patterns`, `core_wound`, `self_deception`) queried with `as_of_chapter` |
| **Returns in artifacts** | Pacing guidance document — passed by brain as `pacing_guidance` context key in `scene-construction` delegation. No KG persistence needed |

---

## Dependencies

**Upstream:** Character node must be current in Story State KG (updated after previous scene). Brain provides `pov_character_id`, `chapter_context`, `last_scene_outcome`, and `chapter_emotional_arc`.

**Downstream:** Pacing guidance in artifacts is consumed as an input parameter by `scene-construction`.

---

## Pacing Analysis Workflow

```
- [ ] Step 1: Query Story State KG — fetch Character node
- [ ] Step 2: Extract psychological/behavioural baseline (how they process pressure)
- [ ] Step 3: Read current state as pressure on the baseline
- [ ] Step 4: Derive the register from the intersection
- [ ] Step 5: Assess for register shift within the scene
- [ ] Step 6: Determine sentence density
- [ ] Step 7: Determine interiority level
- [ ] Step 8: Determine dialogue-to-action ratio
- [ ] Step 9: Write chapter arc alignment note
- [ ] Step 10: Write tension flags (character-specific warnings)
- [ ] Step 11: Assemble and return artifacts
```

### Step 1 — Query the Story State KG

Fetch the Character node at `as_of_chapter = chapter_context`. If not found, return `need_input`. Populate `kg_context_used`.

### Step 2 — Extract the character's psychological and behavioural baseline

Read the Character node with the specific question: *How does this character process pressure of this type?*

Focus on stable traits from the Character node: `core_wound`, `self_deception`, `response_patterns`, `arc_type`. Ask:
- What is their habitual emotional defence? (Intellectualise, suppress, perform composure, deflect into action, dissociate, over-control?)
- What is their baseline interiority level — highly internal processor or primarily external perceiver?
- What breaks through their defences, and what does not?
- What is their characteristic cognitive style — associative, sequential, analytical, imagistic, tactical?
- How do they communicate under pressure — go silent, become more verbal, become more precise, become more evasive?

Write the `character_psychology_summary` from this. It must be specific enough that a different character's summary would be recognisably different.

### Step 3 — Read the current state as a pressure on the baseline

Read `emotional_state`, `active fears`, `arc_stage`, and `injuries_physical_state` from the Character node. Read `last_scene_outcome` from context. Ask not "what is this character feeling?" but "what is this pressure doing to this character's specific processing system?"

- Is the current state within the range the character's psychology can manage with its habitual defences? Or at or beyond that range?
- What specific form does the pressure take for this character? Grief may manifest as analytical over-function in one character and perceptual disruption in another.
- Is the physical state compressing or disrupting the character's cognitive capacity?

### Step 4 — Derive the register from the intersection

Do not look at the register table and match the situation to the nearest row. Instead, ask: *Given what I know about how this character processes pressure, what shape does the prose take when this character is in this state?* Then find the register that matches that shape.

A character who goes to analytical over-function under grief → **Deliberate**, not Reflective.
A character who performs composure over genuine fracture → **Brittle**, not Deliberate.
A character who responds to acute threat by going very still and very precise → **Suspended** or **Taut**, not Urgent.
A character who has exhausted their processing capacity → **Numb**, even if the situation is objectively urgent.

Write the justification tracing the derivation explicitly: from the specific psychological trait, through the way the current pressure acts on that trait, to the register.

### Step 5 — Assess for register shift within the scene

Read `chapter_emotional_arc` from context. Does the scene need to move between registers? If yes, identify: the trigger point (what specific event or realisation causes the shift) and the destination register. Most scenes hold a single register; not every scene has an internal shift.

### Step 6 — Determine sentence density

Consider both the derived register and this character's specific cognitive style. Assign density (High / Medium / Low). Anchor the justification in the character's habitual cognitive pattern — not just the register. Two characters in Taut register may have different sentence densities because their habitual cognitive styles differ.

### Step 7 — Determine interiority level

Consider the character's baseline interiority level (from `response_patterns` and behavioural baseline) and how the current state modifies it. A highly interior character who is actively suppressing interiority is **Compressed** — the suppression itself is characterisation. Assign and justify in one sentence.

### Step 8 — Determine dialogue-to-action ratio

Consider the scene's social context (inferred from `scene_parameters` passed to the brain) and this character's habitual communication pattern under this type of pressure. Assign and justify briefly.

### Step 9 — Write the chapter arc alignment note

2–4 sentences connecting these parameters to the chapter's emotional arc. Note any anticipated register shift within the scene and its trigger. Note where this scene sits within the chapter's arc — climbing, plateauing, or descending.

### Step 10 — Write the tension flags

Review the `character_psychology_summary` for patterns that are predictable risks in this specific scene. Write character-specific, actionable flags. Each flag must name the specific behavioural pattern and specify what `scene-construction` should do about it:

- **Undercut risk:** Does this character habitually deflect, intellectualise, or suppress emotion in ways that could flatten the scene's tension? Name the specific habit and how to handle it.
- **Overdrive risk:** Does this character's baseline processing style risk producing prose too slow for the external urgency, or too flat to register emotional weight? Name the specific risk.
- **Voice specificity risk:** Under this pressure, which specific voice markers are most at risk of going generic? Name 1–2 concrete markers — not "keep the voice distinctive" but the specific cognitive tic, observational habit, or syntactic pattern that belongs to this character alone.

### Step 11 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Character node was found in KG; `kg_context_used.character_node_found = true`.
- [ ] `character_psychology_summary` is specific — could not apply to a different character.
- [ ] Register is derived from character psychology intersected with current state — not read directly from the situation.
- [ ] Register `justification` traces the derivation explicitly from a named trait through a named pressure to the register.
- [ ] All output sections are present: psychology summary, register + justification, sentence density, interiority level, dialogue ratio, chapter arc alignment, tension flags.
- [ ] Tension flags are character-specific — named behavioural patterns, not generic writing advice.
- [ ] Register assignment check: would a different character in the same situation land in a different register? (Should be yes.)
- [ ] No prose written. No plot decisions. No scene content specified.
- [ ] No Story State KG writes from this skill.