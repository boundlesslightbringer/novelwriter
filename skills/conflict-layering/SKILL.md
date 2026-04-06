---
name: conflict-layering
description: Audits a drafted scene or chapter for conflict weight — not conflict count. A scene with a single conflict passes if that conflict carries enough momentum to justify the scene's existence. A scene with many conflicts fails if none of them land with real force. Queries Story State KG directly for the POV character's current psychological state and relevant relationship records. Returns a conflict audit report in artifacts. Does not rewrite.
---

# Conflict Layering

## Identity

**Purpose:** Diagnose whether the conflict in a drafted scene is doing real work — creating momentum, revealing character, or advancing the story's stakes. The question is never "how many conflict levels are present?" It is always "is the conflict that is present earning the scene's place in the narrative?"

---

## Core

Audit a drafted scene or chapter for the weight and effectiveness of its conflict, not for the number of conflict levels it contains. Assess whether what is present is pulling its narrative weight — generating momentum, revealing character under pressure, or advancing stakes. Identify what is genuinely absent or underused only when its absence is causing a specific, diagnosable weakness. Flag when conflict is present in name but not in force. Return a conflict audit report in artifacts. Does not rewrite the scene.

---

## The Central Principle

A story's conflict landscape is not a checklist. The five conflict levels — internal, interpersonal, societal, factional, existential — are a diagnostic vocabulary, not a quota. A scene that uses every level superficially is worse than a scene that uses one level at full depth. The corollary: forcing conflict into a scene that does not need it produces a mechanical narrative.

**The question is not: does this scene have five kinds of conflict?**
**The question is: does this scene have enough conflict weight to earn its place?**

---

## Input

### From brain context (`worker_request.context`)

1. **`draft_scene`** — The prose draft to be audited (from `scene-construction` artifacts). Required.
2. **`pov_character_id`** — The `logical_id` of the POV character for the scene. Required.
3. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required.
4. **`scene_intended_function`** (optional) — A brief note from the brain on what role this scene plays in the narrative (e.g. "quiet scene to establish character in a lull," "emotional turning point of the chapter," "transitional scene"). When provided, the audit calibrates its weight assessment to the intended function.
5. **`other_character_ids`** (optional) — List of `logical_id` strings for non-POV characters who appear in the scene. The plotting_subagent fetches their relationship records if provided.

### Fetched from Story State KG

The plotting_subagent queries the Story State KG directly:

```
# POV character's current psychological state
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# Relationship records for characters in the scene (directional)
# For each character_id in other_character_ids:
query_kg_edges({from_node: pov_character_id,
                to_node: character_id,
                type: "RELATIONSHIP"},
               as_of_chapter=chapter_context)
```

If `other_character_ids` is not provided in context, skip the relationship queries — conflict assessment will focus on the internal and observational dimensions. Note the absence in `kg_context_used`.

---

## Output

All output is returned in `artifacts`. Conflict audit is pure analysis — no KG persistence needed. If the brain's quality gate accepts the audit (momentum verdict is not EARNING ITS PLACE), the brain decides whether to re-delegate `scene-construction` with the audit as additional context.

### `artifacts` structure

```json
{
  "audit_header": {
    "pov_character_id": "char_<slug>",
    "scene_summary": "<one sentence>",
    "intended_function": "<from context or inferred>",
    "momentum_verdict": "EARNING ITS PLACE | UNDERLOADED | CARRYING DEAD WEIGHT | SCENE PURPOSE QUESTION"
  },
  "conflict_present": {
    "summary": "<what is working and why it is landing at depth>",
    "primary_conflict_level": "Internal | Interpersonal | Societal | Factional | Existential",
    "operating_depth": "Surface (declared) | Depth (felt as real pressure)"
  },
  "conflict_absent_or_underused": [
    {
      "level": "Internal | Interpersonal | Societal | Factional | Existential",
      "status": "Absent — available | Absent — not applicable",
      "why_it_matters": "<specific problem caused by this absence — not 'this level should be present'>",
      "available_material": "<what already exists in scene or character record that could carry this>"
    }
  ],
  "conflict_weight_assessment": {
    "internal": {
      "status": "Active | Latent | Weak | Absent — available | Absent — not applicable",
      "note": "<one or two sentences>"
    },
    "interpersonal": {
      "status": "Active | Latent | Weak | Absent — available | Absent — not applicable",
      "note": "<one or two sentences>"
    },
    "societal": {
      "status": "Active | Latent | Weak | Absent — available | Absent — not applicable",
      "note": "<one or two sentences>"
    },
    "factional": {
      "status": "Active | Latent | Weak | Absent — available | Absent — not applicable",
      "note": "<one or two sentences>"
    },
    "existential": {
      "status": "Active | Latent | Weak | Absent — available | Absent — not applicable",
      "note": "<one or two sentences>"
    }
  },
  "suggestions": [
    {
      "rank": 1,
      "specific_addition": "<what to add or change>",
      "derived_from": "<the character's specific psychology or the scene's existing material>",
      "predicted_effect": "<specific effect on conflict weight>"
    }
  ],
  "scene_rhythm_note": null,
  "summary_pattern_note": null,
  "kg_context_used": {
    "pov_character_found": true,
    "relationship_records_found": 0
  }
}
```

`suggestions` is only populated when `momentum_verdict` is not `EARNING ITS PLACE`. Suggestions are ranked by impact-to-disruption ratio. Each suggestion uses only existing scene material and character psychology — no new plot events.

`scene_rhythm_note` is populated (non-null) only when conflict weight is appropriate but sequencing within the scene is creating a structural problem (front-loaded conflict, late-arriving tension, etc.).

`summary_pattern_note` is populated when a pattern is visible across multiple violations — e.g. a systematic tendency toward declared rather than dramatised conflict — to help `scene-construction` address the root cause rather than patching individual instances.

---

## The Central Test

Before assigning the momentum verdict, apply the Scene Purpose Test to conflict weight specifically. A scene passes if its conflict is producing at least one of:
- Plot advancement (things change in the story's state), **and/or**
- Character revelation (something about the POV character under pressure the reader did not fully have before), **and/or**
- Stake building (increasing the reader's sense of what matters and what is at risk)

A scene fails when: events occur but nothing changes; the character is present but untested; conflict is declared but not felt.

---

## Conflict Level Reference

| Level | Active when | Weak when | Not applicable when |
|---|---|---|---|
| **Internal** | The character's psychology is under genuine pressure — self-deception straining, core contradiction surfacing | Declared in narration without being dramatised | The scene is a deliberate, structurally justified pause where the character is not being tested |
| **Interpersonal** | Two characters have incompatible aims, asymmetric knowledge, or unresolved relational material shaping the interaction | Characters exchange information without relational subtext doing work | Only the POV character is present, or all present characters are genuinely aligned |
| **Societal** | The social order is making a demand on the character that conflicts with who they are | Social context present as scenery but not as pressure | Scene occurs outside any social structure relevant to its material |
| **Factional** | A faction's interests or obligations are actively shaping what the character can do | Faction exists in the world but is not registering in the scene | Scene is genuinely private — no factional forces present or relevant |
| **Existential** | Scene touches one of the story's largest questions through this character's specific lived experience | Gestured at in narration without the character actually confronting anything | Scene is not at a structural moment that warrants this level — most scenes are not |

---

## Boundary

- **Does not** prescribe a minimum or maximum number of conflict levels per scene.
- **Does not** flag absent levels as deficiencies unless their absence is causing a specific, diagnosable problem.
- **Does not** rewrite the scene. Suggests only; `scene-construction` executes if the brain re-delegates.
- **Does not** operate on scenes before they are drafted.
- **Does not** audit POV voice consistency, knowledge violations, or prose quality. Those are `pov-consistency-maintenance` and `self-editing-and-refinement` domains.
- **Does not** write to the Story State KG.
- **Does not** mandate revision. A verdict of EARNING ITS PLACE means the scene passes.

---

## Invocation

The `plotting_subagent` invokes this skill when the brain delegates a conflict audit:

- When the story feels too linear, too predictable, or structurally flat for a specific scene or chapter.
- After `scene-construction`, as an optional quality check on scenes the brain suspects are underloaded.
- When a scene involves a significant character interaction or turning point and the brain wants to verify conflict weight.
- When a scene feels inert despite containing the right events.

This skill is **not** a mandatory post-construction step for every scene. It is invoked when there is a specific concern. Routine scenes that are clearly doing their work do not require this audit.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node (POV character, `as_of_chapter`); RELATIONSHIP edges from POV character to other characters in the scene |
| **Returns in artifacts** | Conflict audit report — momentum verdict, conflict present/absent analysis, five-level assessment, suggestions (if verdict is not EARNING ITS PLACE), optional rhythm and pattern notes. No KG persistence needed |

---

## Dependencies

**Upstream:** A drafted scene from `writing_subagent (scene-construction)` is required in context. POV Character node and relevant RELATIONSHIP edges must be current in Story State KG.

**Downstream:** If `momentum_verdict` is not EARNING ITS PLACE, the brain may re-delegate `writing_subagent (scene-construction)` with the audit report included in context as `conflict_layering_audit`. The brain is not required to act on the audit — EARNING ITS PLACE requires no follow-up.

---

## Instructions

### Step 1 — Query the Story State KG

Fetch the POV Character node and, if `other_character_ids` is provided, the relevant RELATIONSHIP edges. Populate `kg_context_used`. If the Character node is not found, return `need_input`.

### Step 2 — Establish the scene's intended function

Read `scene_intended_function` from context. If not provided, infer from the scene's position in the narrative (if determinable from Chapter nodes) and the scene parameters that generated it. Hold this context throughout — a transitional scene has a different conflict requirement than a pivot scene where long-building tension finally breaks.

### Step 3 — Read the draft for what is present and landing

Read the scene draft. Track:
- What conflict is present — at which level, in what form?
- Is it landing — felt as pressure, shaping choices and perceptions — or declared without being dramatised?
- Where in the scene does conflict have the most force? Where does it thin or disappear?
- Is conflict arising from who the character is and what the situation demands — or does it feel installed?

### Step 4 — Assess momentum and assign the verdict

Apply the Scene Purpose Test. Ask: **Is this scene generating enough narrative momentum — enough forward pull, enough revelation, enough escalation of stakes — to justify its existence?**

Assign one of four verdicts:
- `EARNING ITS PLACE` — Conflict present is generating sufficient momentum for the scene's function.
- `UNDERLOADED` — Contains conflict but it is not landing with enough force.
- `CARRYING DEAD WEIGHT` — Contains conflict but it is mechanical or manufactured — present because a conflict should be present, not arising naturally.
- `SCENE PURPOSE QUESTION` — So little conflict weight that the Scene Purpose Test may not be passing. Reserve for scenes that genuinely cannot justify their existence — not a default for quiet scenes.

### Step 5 — If verdict is not EARNING ITS PLACE: diagnose the specific weakness

Identify precisely what is causing the shortfall. Find the specific material already available — in the character's psychology from the Character node, in the relationship records from RELATIONSHIP edges, in the scene's existing events — that could carry the missing weight. Populate `conflict_absent_or_underused` with specific, named diagnoses.

### Step 6 — Map the five levels as diagnostic vocabulary

For each level, note its current status and whether that status is appropriate for this scene's function. Keep this section brief — it is a map of the terrain, not the core analysis. The depth goes in Step 5.

Absent levels are `"Absent — not applicable"` when the scene's material does not call for them. Only `"Absent — available"` when their absence is causing the specific weakness diagnosed in Step 5.

### Step 7 — Write suggestions (only if verdict is not EARNING ITS PLACE)

Write targeted suggestions ranked by impact-to-disruption ratio:
- Each suggestion addresses the specific weakness from Step 5.
- Each uses existing scene material and character psychology — no new plot events.
- Each states the specific addition and its predicted effect.

If verdict is EARNING ITS PLACE, suggestions may be included as optional observations but are not required.

### Step 8 — Add rhythm and pattern notes if warranted

If conflict sequencing within the scene is creating a structural problem despite appropriate weight, populate `scene_rhythm_note`. If a systematic pattern is visible across the draft, populate `summary_pattern_note`.

### Step 9 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`.

---

## Example

For worked examples of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] `momentum_verdict` is one of the four valid values.
- [ ] `conflict_present` names what is working before diagnosing weakness — audit does not lead with deficiency.
- [ ] Every entry in `conflict_absent_or_underused` names the specific weakness and explains *why it matters here*, not "this level is missing."
- [ ] Every suggestion (if present) uses only existing material — no new plot events introduced.
- [ ] Suggestions are ranked.
- [ ] Absent levels are `"Absent — not applicable"` unless their absence is causing a named problem.
- [ ] If `momentum_verdict == "EARNING ITS PLACE"`: audit affirms this clearly without excessive caveats.
- [ ] No prose rewritten. No plot decisions made.
- [ ] No Story State KG writes from this skill.