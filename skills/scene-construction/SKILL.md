---
name: scene-construction
description: Writes a single scene in draft prose. Applies the POV character's voice profile, executes scene parameters (goal, obstacle, choice, consequence), and embeds foreshadowing organically. Queries the Story State KG directly for all context it needs — character state, knowledge matrix, voice profile, pending payoffs, and relevant world state. Invoked after gardener-plotting-system has produced scene parameters. Outputs draft prose in artifacts.
---

# Scene Construction

## Identity

**Skill name:** `scene-construction`
**Purpose:** Write the scene. Everything upstream — character psychology, world state, scene parameters, voice profile, pacing guidance — is assembled by querying the Story State KG directly and from the brain's context dict. This skill executes the prose. It writes one complete scene in draft, entirely in the POV character's voice and perception. The output is raw discovery material — the first full pass — not the finished product.

> **Sibling skills:** Output is audited by `pov-consistency-maintenance`. Optional input from `pacing` (when psychological state has shifted significantly) governs prose rhythm.

---

## Core

Write a single scene in draft prose. One POV character, one goal, one obstacle, one choice, one consequence. Apply the POV character's voice profile throughout — every observation, interpretation, and thought is filtered through this character's perception, vocabulary, sentence rhythms, and observational focus. Embed foreshadowing naturally where consistent with the Pending Payoffs register. Produce draft prose only; do not self-audit for POV consistency. Do not write to the Story State KG.

---

## Input

### From brain context (`worker_request.context`)

1. **`scene_parameters`** — The full scene parameters from `gardener-plotting-system` artifacts. Contains: `pov_character_id`, `pov_character_name`, `arc_stage`, `dominant_emotional_state`, `scene_goal`, `obstacle`, `the_choice`, `projected_consequence_shape`, `character_logic_audit`, `active_thread_flags`, `active_consequence_flags`, `foreshadowing_opportunity`. Required.

2. **`chapter_context`** — Current chapter number. Used to scope all KG queries. Required.

3. **`pacing_guidance`** (optional) — Output from the `pacing` skill if it was invoked for this character's current psychological state. Contains: `scene_rhythm_register`, `sentence_density`, `interiority_level`, `dialogue_to_action_ratio`, `chapter_arc_alignment_note`, `tension_flags`. When provided, these parameters govern how the scene is written. When absent, pacing is inferred from the Character node's current emotional state.

4. **`conflict_layering_audit`** (optional) — Output from `conflict-layering` if a prior draft of this scene was returned as UNDERLOADED or CARRYING DEAD WEIGHT. The new draft addresses the audit's ranked suggestions.

5. **`pov_consistency_flags`** (optional) — Output from `pov-consistency-maintenance` if a prior draft was flagged for specific violations. The corrected draft addresses each flagged violation.

6. **`feedback`** (optional) — Correction directive from the brain if this is a re-delegation after a rejected artifact. The brain passes specific issues identified during the quality gate.

### Fetched from Story State KG

The writing_subagent queries the Story State KG directly to assemble all context the scene requires. The `pov_character_id` and `chapter_context` from brain context scope every query:

```
# POV character's full current state including voice profile
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# POV character's knowledge matrix — epistemic constraint on every sentence
query_kg_edges({from_node: pov_character_id, type: "KNOWS"},
               as_of_chapter=chapter_context)
# Fetch the KnowledgeItem nodes referenced by the KNOWS edges

# Pending payoffs — for organic foreshadowing
# (only if scene_parameters.foreshadowing_opportunity.present is true)
query_kg_nodes({type: "Payoff",
                "properties.resolution_status": "Pending"},
               as_of_chapter=chapter_context)

# Relevant world state for this scene's location and active characters
# Fetch the Location node for the scene's setting
query_kg_nodes({type: "Location",
                "properties.name": scene_location},
               as_of_chapter=chapter_context)
# Fetch relevant Culture or Faction nodes if the scene involves
# cultural or political context (infer from scene_parameters)
```

The Character node's `properties.voice_profile` sub-record (stored by `character-voice-differentiation`) contains the full voice profile. Both the psychological record and voice profile are retrieved in the single Character node query — no separate query needed.

If any query returns no results, proceed with empty context for that dimension and note the absence in `artifacts.kg_context_used` — do not halt. An empty Location node result simply means the setting has not been formalised in Story State yet; proceed with what the scene parameters establish.

---

## Output

All output is returned in `artifacts`. The draft prose is the primary output. The brain applies the quality gate before deciding whether to persist a Chapter node to `story_state_manager` or re-delegate for corrections.

### `artifacts` structure

```json
{
  "draft_prose": "<complete scene prose — no markup, no structural notes>",
  "scene_metadata": {
    "pov_character_id": "char_<slug>",
    "chapter_context": 0,
    "approximate_word_count": 0,
    "foreshadowing_embedded": false,
    "foreshadowing_payoff_id": null,
    "parameter_discrepancy_flag": null
  },
  "kg_context_used": {
    "character_node_found": true,
    "voice_profile_found": true,
    "knows_edges_found": 0,
    "pending_payoffs_checked": false,
    "location_node_found": false
  }
}
```

`draft_prose` contains only the scene text — no headers, no metadata, no POV labels, no structural annotations.

`parameter_discrepancy_flag` is set (non-null, with a description) when the act of writing reveals that a scene parameter is inconsistent with the character's full psychology as retrieved from the Character node. When this flag is set, the brain must resolve it before accepting the draft — it takes priority over the quality gate's other checks.

`foreshadowing_embedded` is `true` only if a pending payoff was organically integrated into the prose. `foreshadowing_payoff_id` identifies which Payoff node was advanced, so the brain can update it via `story_state_manager`.

---

## Examples

For worked examples of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## POV Discipline — The Governing Craft Constraint

POV discipline is the single most consequential craft rule. Every sentence must pass this test before it exists in the draft: *Can this observation, thought, or piece of information be accessed by this specific character, in this specific location, at this specific moment, given what they know?*

**What this requires:**

**Perceptual constraint.** The scene contains only what the POV character can perceive with their senses from their physical position. They cannot see through walls, cannot know what another character is thinking, cannot observe their own face or expression from the outside.

**Epistemic constraint.** The POV character acts only on information in their KNOWS edges. Status `KNOWS` or `SUSPECTS` or `BELIEVES` (possibly falsely) per the knowledge matrix — and if they BELIEVE something false, they act on the false belief. The reader may understand the falseness; the character does not.

**Voice constraint.** The narration sounds like this character's internal register as defined in `properties.voice_profile`. Vocabulary, sentence rhythm, observational sequence, internal processing patterns — all match the voice profile. When the voice drifts toward a generic narrative voice, the POV has been lost.

**What this prohibits:**
- **Head-hopping:** Any access to another character's internal state not inferrable from observable external behaviour.
- **Omniscient intrusions:** Narrative observations requiring a perspective above or outside the POV character.
- **External self-description:** The POV character describing their own face or appearance as an observer would see it.
- **Knowledge violations:** The character acting on information recorded as `DOES NOT KNOW` in their knowledge matrix.

---

## Foreshadowing in Construction

The `foreshadowing_opportunity` field in `scene_parameters` indicates whether a pending payoff is a candidate for organic integration. The Payoff nodes queried from Story State KG provide the full register.

**The test for organic integration:** Would this object, person, detail, or event be present in this scene even if it were not a setup element? If yes — and the POV character would notice it given their observational focus from `voice_profile` — it can be planted. If it is present only because it needs to be planted, the plant is forced.

**When not to plant:** If no pending payoff fits organically into this scene's material and this character's observational focus, nothing is planted. Set `foreshadowing_embedded: false`. Leave the register open for a scene where the material is genuinely receptive. Forced foreshadowing damages the prose and the setup both.

---

## The Scene's Internal Shape

Every scene has three phases that must all be written:

**Opening — the character in their situation.** The character, in their body, in their current state, in the specific physical and social space of the scene, at the moment the scene begins. Voice profile active from the first sentence.

**Middle — obstacle fully present, choice live.** The obstacle is encountered in real time, not summarised. Both options of the choice carry real cost. The character makes the choice through the action of the prose — it is not announced.

**Ending — consequence opening, scene closing on a beat.** The scene ends on a specific moment — an image, a line of dialogue, an action, a thought. Not a summary. This final beat creates forward pull, dread, or an emotional truth.

---

## Handling Parameter Discrepancies

When the act of writing reveals that a scene parameter is inconsistent with the character's psychology as retrieved from the Character node: **stop. Do not substitute a different goal or choice silently.** Set `parameter_discrepancy_flag` with a description of the conflict. The brain re-delegates to `gardener-plotting-system` with this information. Writing a scene around a character logic violation produces prose the story cannot support.

---

## Boundary

- **Produces draft prose only.** Line-by-line polish is `self-editing-and-refinement`'s domain.
- **Does not audit its own POV consistency.** The creative pass and the editorial pass must be separate.
- **Does not determine pacing independently** beyond what pacing guidance specifies or the Character node's emotional state implies.
- **Does not plot.** Scene parameters come from `gardener-plotting-system`. If wrong, the discrepancy is flagged — not silently corrected.
- **Does not write more than one scene per invocation.**
- **Does not layer history and legend.** That is a separate pass after this draft is POV-consistent.
- **Does not write to the Story State KG.** The brain routes Chapter node creation and any Payoff node updates to `story_state_manager`.

---

## Invocation

The `writing_subagent` invokes this skill when the brain delegates scene writing:

- After `gardener-plotting-system` has produced scene parameters passing the brain's quality gate.
- After `pacing` has been invoked, if the POV character's psychological state has shifted significantly.
- For re-drafts after `pov-consistency-maintenance` flags violations, or after `conflict-layering` returns a non-passing verdict — in which case those outputs are passed in context.

**Standard scene-writing delegation sequence (brain-level):**
`plotting_subagent (gardener-plotting-system)` → `[plotting_subagent (pacing) if state shifted]` → `writing_subagent (scene-construction)` → `writing_subagent (pov-consistency-maintenance)`

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node including `voice_profile` sub-record (POV character, `as_of_chapter`); KNOWS edges and KnowledgeItem nodes (knowledge matrix); Payoff nodes with `resolution_status: "Pending"` (if foreshadowing check requested); Location node for scene setting; optionally Culture or Faction nodes for world context |
| **Returns in artifacts** | Draft prose; `scene_metadata` including `foreshadowing_embedded` and `parameter_discrepancy_flag`. Brain routes Chapter node creation to `story_state_manager`; if `foreshadowing_embedded: true`, brain routes Payoff node update (advancing toward payoff) to `story_state_manager` |

---

## Dependencies

**Upstream:** `gardener-plotting-system` scene parameters required in context. Character node with voice profile must be persisted in Story State KG. Brain provides `scene_parameters`, `chapter_context`, and optional pacing/audit inputs.

**Downstream:** Draft prose is audited by `writing_subagent (pov-consistency-maintenance)`. Optionally: `writing_subagent (conflict-layering)` if the brain suspects weak conflict weight. After all scene-level passes, completed chapter draft proceeds to `writing_subagent (layering-history-and-legend)` (optional), then the brain creates the Chapter node via `story_state_manager`.

---

## Instructions

### Step 1 — Query the Story State KG

Run all specified queries at `as_of_chapter = chapter_context`. Populate `kg_context_used`. If the Character node is not found or `properties.voice_profile` is absent, return `need_input` — the character record must be persisted before scene construction can proceed.

### Step 2 — Read the scene parameters and establish the structural skeleton

Read `scene_parameters` from context. Identify the goal, obstacle, choice, and consequence shape. Commit to them before writing a word of prose.

If any optional correction inputs are present (`pov_consistency_flags`, `conflict_layering_audit`, `feedback`), read them now. These correction directives shape the draft — each flagged issue from a prior pass must be addressed.

### Step 3 — Enter the POV character's voice

Before writing the scene's first sentence, establish the voice from `properties.voice_profile`:
- Lexical register and signature vocabulary categories
- Default sentence structure pattern and the stressed-voice variant
- Primary observational lens and systematic blind spots
- Internal thought pattern and emotional processing style

Apply any pacing guidance from context. The register, sentence density, interiority level, and dialogue-to-action ratio specified by `pacing` override defaults.

Ask: *If this character were going to open this scene with the first thing they notice, what would it be?* That is the scene's first sentence, or close to it.

### Step 4 — Write the opening

Orient the reader in the character's specific physical and emotional position without summarising it. The character is in a place, in a body, in a state. The opening renders this through perception — what the character notices, in the order they notice it, through their specific observational lens. Voice profile active from sentence one.

### Step 5 — Develop the obstacle through the character's encounter with it

Write through the obstacle as the character experiences it — not as a summary but in real time. The obstacle should:
- Arise from the scene's specific situation, not appear as a generic complication
- Engage at least one internal component from the character's `core_wound`, `self_deception`, or `values_under_pressure` where the parameters support it
- Be rendered at the level of the character's specific perception, not plot summary

### Step 6 — Bring the choice to a live moment

The choice must arrive as a lived moment, not an announced decision. The character faces it from inside their situation. Honour the cost of both options. The character makes the choice through the action of the prose — the reader sees it happen; the character does not narrate it as a decision.

### Step 7 — Write the consequence opening and close on a beat

The consequence does not resolve the scene — it opens the next one. Close on a specific moment: the last image, the last line, the last movement. Not a summary. Not a statement of what it meant. A concrete particular that the reader carries into the white space before the next scene.

### Step 8 — Check foreshadowing integration

After the draft is complete, review the `foreshadowing_opportunity` field in scene parameters and the Payoff nodes retrieved from Story State KG. Ask: did the scene's events, setting, or character attention naturally accommodate any pending payoff? If yes — and the integration was organic — set `foreshadowing_embedded: true` and `foreshadowing_payoff_id` to the relevant node's `logical_id`.

If any plant was forced, remove it. An unplanted scene is better than a scene with a visible setup.

### Step 9 — Check for parameter discrepancy

If the act of writing revealed that any scene parameter was inconsistent with the character's full psychology — as retrieved from the Character node — set `parameter_discrepancy_flag` with a brief account of the conflict. Return the draft with the flag set; the brain resolves it before accepting.

### Step 10 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. `draft_prose` contains only prose — no markup. `scene_metadata` contains all operational information the brain needs for follow-up routing.

---

## Quality Checks

Before returning output, verify:

- [ ] Character node and voice profile were found in KG; `kg_context_used` is populated.
- [ ] Every sentence passes the POV discipline test: perceptual, epistemic, and voice constraints.
- [ ] No head-hopping, no omniscient intrusions, no external self-description, no knowledge violations.
- [ ] Voice profile is active from the first sentence and sustained throughout.
- [ ] Scene has all three phases: opening, middle with obstacle and live choice, ending on a specific beat.
- [ ] If `pov_consistency_flags` were provided: each flagged violation is addressed.
- [ ] If `conflict_layering_audit` was provided: ranked suggestions are addressed.
- [ ] Foreshadowing, if embedded, passes the organic integration test; `foreshadowing_embedded` and `foreshadowing_payoff_id` are accurate.
- [ ] Pacing guidance, if provided, is respected throughout.
- [ ] `parameter_discrepancy_flag` is null or describes a specific conflict.
- [ ] `draft_prose` contains only prose — no metadata, headers, or structural annotations.
- [ ] No Story State KG writes from this skill.