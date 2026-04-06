---
name: balancing-realism-and-fantasy
description: Audits a completed chapter or flagged scene against the realism-fantasy calibration checklist — covering political realism, magic system consistency, violence framing, dark content justification, and tonal consistency. Queries Story State KG directly for the magic system state and relevant world state records. Returns a structured audit report in artifacts with specific flags and recommended adjustments. Does not rewrite. Invoked when tone, magic use, or dark content has been flagged as a concern, or as a periodic audit after significant chapters.
---

# Balancing Realism and Fantasy

## Identity

**Skill name:** `balancing-realism-and-fantasy`
**Group:** 5 — Consequence & Realism
**Subagent:** consequence_subagent
**When to invoke:** Called by the `consequence_subagent` when the brain delegates a realism audit after any of the following:
- Tone in a completed chapter feels inconsistent with the established register.
- Magic is used in a way that may violate established system limits or inflate prevalence.
- A violent or dark scene has been drafted and needs calibration against justification criteria.
- The brain has flagged a scene or chapter as a potential realism-fantasy balance concern.
- Periodic audit requested after a chapter of high consequence (major battle, large-scale magic, significant death).

This skill is an **audit tool**, not a writing tool. It is never invoked mid-scene.

---

## Core

Audit a completed chapter or flagged scene against five calibration dimensions: political realism, magic prevalence and consistency, violence framing, dark content justification, and tonal consistency. Return a structured audit report with specific flagged passages and recommended adjustments. The brain applies the quality gate and decides whether to re-delegate `scene-construction` or accept the chapter.

---

## Input

### From brain context (`worker_request.context`)

1. **`chapter_or_scene_draft`** — The completed text to be audited. Required.
2. **`chapter_context`** — The chapter number being audited. Used to scope all KG queries. Required.
3. **`audit_scope`** — `"full_chapter"` or `"flagged_scene"`. When `"flagged_scene"`, the brain also passes `scene_description` identifying which scene within a chapter is the concern. Required.
4. **`tone_reference`** (optional) — A brief note from the brain on the established tonal register if not inferable from Story State records (e.g. `"low fantasy, high political realism, earned darkness"`). When absent, the skill infers register from the world state records retrieved from KG.
5. **`pov_character_id`** (optional) — The `logical_id` of the POV character for the scene, if the audit requires character-level psychological checks (e.g. assessing whether the POV character's response to violence is consistent with their psychology).

### Fetched from Story State KG

The consequence_subagent queries the Story State KG directly for all world state and character records needed to calibrate the audit:

```
# Magic system state — required for Dimension 2 audit
query_kg_nodes({type: "MagicSystem"},
               as_of_chapter=chapter_context)

# Political and power map — required for Dimension 1 audit
query_kg_nodes({type: "Faction"},
               as_of_chapter=chapter_context)
query_kg_nodes({type: "Location"},
               as_of_chapter=chapter_context)

# Cultures — for tonal register inference (Dimension 5)
query_kg_nodes({type: "Culture"},
               as_of_chapter=chapter_context)

# POV character psychological record — for Dimension 3 (violence framing)
# Only if pov_character_id is provided in context
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# Recent magical events — from Chapter nodes, to assess prevalence
# (magic events are referenced in Chapter node properties or
# MagicSystem node's recent_magical_events field)
query_kg_nodes({type: "Chapter",
                "properties.chapter_number": {"$gte": chapter_context - 5}},
               as_of_chapter=chapter_context)
```

If the MagicSystem node is not found (no magic exists in this story), mark Dimension 2 as `"Not applicable"` and proceed. If no Faction or Location nodes are found, note the absence and assess Dimension 1 from what the draft itself establishes.

---

## Output

All output is returned in `artifacts`. The audit report is pure analysis — no KG persistence needed. However, if the audit identifies a new magic capability or unexplained phenomenon in the draft, the brain may route a `story_state_manager` update to add it to the MagicSystem node's records.

### `artifacts` structure

```json
{
  "audit_header": {
    "chapter_context": 0,
    "audit_scope": "full_chapter | flagged_scene",
    "pov_character_audited": "char_<slug> | null"
  },
  "dimension_reports": {
    "political_realism": {
      "status": "Pass | Flag | Concern",
      "flagged_passages": [
        {
          "text_reference": "<offending sentence or passage, quoted>",
          "issue_description": "<what specifically is miscalibrated and why>",
          "recommended_adjustment": "<concrete editorial direction — not rewritten prose>"
        }
      ]
    },
    "magic_prevalence_and_consistency": {
      "status": "Pass | Flag | Concern | Not applicable",
      "magic_acts_in_chapter": 0,
      "current_prevalence_level": "Rare | Increasing | Decreasing | Stable | Not applicable",
      "flagged_passages": []
    },
    "violence_framing": {
      "status": "Pass | Flag | Concern",
      "flagged_passages": []
    },
    "dark_content_justification": {
      "status": "Pass | Flag | Concern",
      "flagged_passages": []
    },
    "tonal_consistency": {
      "status": "Pass | Flag | Concern",
      "flagged_passages": []
    }
  },
  "priority_summary": {
    "high": ["<flag descriptions requiring immediate attention>"],
    "medium": ["<concerns worth addressing before the next draft pass>"],
    "low": ["<minor notes>"]
  },
  "magic_system_updates_recommended": [
    {
      "update_type": "add_confirmed_capability | add_confirmed_limit | add_unexplained_phenomenon",
      "description": "<what should be added to the MagicSystem node>",
      "justification": "<why this update is warranted — the magic act in the draft that warrants it>"
    }
  ],
  "kg_context_used": {
    "magic_system_found": true,
    "faction_nodes_found": 0,
    "culture_nodes_found": 0,
    "pov_character_found": false
  }
}
```

`flagged_passages` entries contain: quoted text reference, issue description, and recommended adjustment. The recommended adjustment is an editorial direction — not rewritten prose. Each dimension has its own `flagged_passages` array, which is empty when `status` is `"Pass"`.

`magic_system_updates_recommended` is populated when the audit identifies a magic act in the draft that represents either a new confirmed capability, a new confirmed limit, or a new unexplained phenomenon. These are recommendations to the brain, not automatic writes. The brain decides whether to route them to `story_state_manager` as `update_kg_node` calls on the MagicSystem node.

`priority_summary` ranks all flags across all five dimensions in one consolidated view for the brain's quality gate.

---

## The Five Calibration Dimensions

### Dimension 1 — Political Realism

The political world must behave according to plausible human logic — not genre convention and not authorial convenience.

Check for:
- **Faction behaviour:** Do political actors pursue their interests through means consistent with their established resources, alliances, and constraints from the Faction and Location nodes? A lord with no army does not threaten war. A king with divided loyalties does not issue ultimatums he cannot enforce.
- **Information realism:** Do characters act on information they plausibly have? Do they fail to act on information they plausibly lack?
- **Consequence accountability:** Do political decisions carry realistic costs?
- **Motivation plausibility:** Are characters pursuing power, safety, legacy, or survival through means proportionate to their situation?
- **No genre shortcuts:** Flag any moment where a political outcome occurs because the plot requires it rather than because the characters' actions and the world's logic produced it.

### Dimension 2 — Magic Prevalence and Consistency

Magic must remain internally consistent with the MagicSystem node retrieved from Story State KG.

Check for:
- **Capability creep:** Does any magical act exceed what `confirmed_capabilities` lists? If yes, flag — either the capability needs to be added (intentional expansion) or the act needs to be adjusted.
- **Limit violations:** Does any magical act contradict `confirmed_limits`? Hard flag.
- **Cost evasion:** Is magic used without the `confirmed_costs` being paid or acknowledged?
- **Prevalence inflation:** Is magic appearing more frequently than the `prevalence` level supports? Count magic acts in the chapter against the prevalence level and recent magical events from the last 5 Chapter nodes.
- **Unexplained phenomena:** If a new magical event cannot be explained by the current system, flag it as a new unexplained phenomenon — add to `magic_system_updates_recommended`.

If no MagicSystem node exists, mark `status: "Not applicable"`.

### Dimension 3 — Violence Framing

Violence is always consequential. It is never spectacle, never clean, and never cost-free.

Check for:
- **Weight and consequence:** Does each act of violence carry physical and psychological weight?
- **Aftermath:** Is the aftermath of violence shown or acknowledged?
- **Spectacle without cost:** Flag any action sequence that reads as exciting but consequence-free.
- **Proportionality:** Is the level of violence depicted proportionate to what the scene requires?
- **POV character response:** If `pov_character_id` is provided, is the POV character's response to violence consistent with their psychology from the Character node (`response_patterns`, `arc_stage`, experience with violence)?

### Dimension 4 — Dark Content Justification

Darkness — cruelty, suffering, moral horror, degradation — is present because it illuminates something true, not because it shocks.

Check for:
- **Purposefulness:** Does each dark element serve a specific narrative, characterisation, or thematic purpose? Identify that purpose. If none can be identified, flag as potentially gratuitous.
- **Consequence integrity:** Dark events have consequences. Flag dark content that occurs without consequence.
- **Reader trust:** Is the darkness framed in a way that respects the reader — not lingering for shock value, not aestheticising suffering?
- **Tonal register:** Is the darkness consistent with the established register of the novel?

### Dimension 5 — Tonal Consistency

The novel has an established tone — a particular relationship between irony and earnestness, between horror and hope. Single chapters should not rupture that register.

Check for:
- **Register breaks:** Does this chapter suddenly adopt a different emotional register from what the novel has established?
- **Voice consistency:** Does the prose register of this chapter match the prose register of surrounding chapters (authorial voice, not POV character voice)?
- **Thematic consistency:** Does the chapter advance, complicate, or interrogate the novel's core themes — or contradict them without apparent purpose?
- **Hope and agency:** GRRM's fiction is dark but not nihilistic. Characters exercise agency that matters even when they fail. Check that this chapter does not reduce characters to purely passive victims of authorial will without any meaningful choice being present.

---

## Boundary

- **Does not rewrite prose.** Flags and recommends only. All rewriting decisions rest with the brain and are executed via `scene-construction`.
- **Does not write to the Story State KG directly.** Returns `magic_system_updates_recommended` for the brain to route to `story_state_manager` if accepted.
- **Does not invoke other skills.** Does not call `scene-construction` or any other skill to implement its recommendations.
- **Does not audit POV consistency or voice.** That is `pov-consistency-maintenance`'s domain.
- **Does not audit plot thread status or consequence completeness.** That is `plot-thread-tracking` and `consequence-cascade-implementation`'s domain.
- **Does not operate mid-scene.** Audits completed drafts only.

---

## Invocation

The `consequence_subagent` invokes this skill when the brain delegates a realism-fantasy calibration audit. This skill is not invoked after every scene — only when the brain has identified a specific concern or requests a periodic audit after a high-consequence chapter.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | MagicSystem node (required for Dimension 2); Faction and Location nodes (Dimension 1); Culture nodes (Dimension 5 tonal inference); Character node for POV character (Dimension 3, optional); recent Chapter nodes for magic prevalence tracking. All queried with `as_of_chapter` |
| **Returns in artifacts** | Structured audit report across five dimensions; consolidated priority summary; `magic_system_updates_recommended` list for brain to route to `story_state_manager` if accepted. No direct KG writes from this skill |

---

## Dependencies

**Upstream:** Completed chapter or scene draft required in context. MagicSystem, Faction, Location, and Culture nodes must be current in Story State KG. Brain provides `chapter_or_scene_draft`, `chapter_context`, and `audit_scope`.

**Downstream:** `priority_summary.high` items guide the brain's decision to re-delegate `scene-construction` with correction context or to accept and proceed. `magic_system_updates_recommended` items, if accepted by the brain, are routed to `story_state_manager` as `update_kg_node` calls on the MagicSystem node.

---

## Instructions

### Step 1 — Query the Story State KG

Run all relevant queries at `as_of_chapter = chapter_context`. Run only the queries relevant to the draft's content — if no magic appears in the draft, skip the MagicSystem query. Populate `kg_context_used`.

### Step 2 — Read the draft with the records in view

Read the chapter or scene draft. Simultaneously hold the Faction nodes, MagicSystem node, and other retrieved records in view. Form an initial impression of where the draft feels miscalibrated before applying the formal checklist.

### Step 3 — Audit Dimension 1 (Political Realism)

Using Faction and Location nodes as the reference standard, check each political act and decision in the draft against the established resources, alliances, and constraints. Flag any political outcome that occurs because the plot requires it rather than because the world's logic produced it.

### Step 4 — Audit Dimension 2 (Magic Consistency)

If the MagicSystem node was found and magic appears in the draft:
- Count magic acts in the chapter.
- Compare each act against `confirmed_capabilities`, `confirmed_limits`, and `confirmed_costs`.
- Assess prevalence against the `prevalence` level and the last 5 chapters' magical events.
- For any magic act not explainable by the current system, add to `magic_system_updates_recommended`.

If no MagicSystem node exists or no magic appears, mark `status: "Not applicable"`.

### Step 5 — Audit Dimension 3 (Violence Framing)

Identify all acts of violence in the draft. For each, assess weight, aftermath, and — if `pov_character_id` provided — the POV character's response against their `response_patterns` from the Character node. Flag spectacle-without-cost or consequence-free violence.

### Step 6 — Audit Dimension 4 (Dark Content)

Identify all dark content in the draft. For each element, state what narrative, characterisation, or thematic purpose it serves. If no purpose can be identified, flag as potentially gratuitous. Check that all dark events carry consequences within the chapter or have a recorded consequence pending in the consequence ledger.

### Step 7 — Audit Dimension 5 (Tonal Consistency)

Assess the chapter's overall register against the tone reference (from context or inferred from Culture nodes and world state). Check that the chapter maintains the novel's established relationship between darkness and agency.

### Step 8 — Compile and rank flags

Across all five dimensions, identify all flags and concerns. Rank in `priority_summary`:
- **High:** Hard continuity errors (magic limit violations, impossible political acts given established resources), significant tonal ruptures.
- **Medium:** Dark content over-elaboration, spectacle-without-cost violence, borderline prevalence inflation.
- **Low:** Minor tonal notes, concerns that read as intentional choices rather than errors.

### Step 9 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. Ensure `magic_system_updates_recommended` is present (even if empty array).

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] MagicSystem node was queried if magic appears in the draft; `status: "Not applicable"` if no magic system exists.
- [ ] Every flagged passage contains: quoted text reference, issue description, recommended adjustment.
- [ ] Recommended adjustments are editorial directions — no prose rewrites.
- [ ] `priority_summary` consolidates all flags across all five dimensions.
- [ ] `magic_system_updates_recommended` is present (even if empty array).
- [ ] Dimension 5 tonal assessment addresses the hope-and-agency check explicitly.
- [ ] Dimensions with no issues have `status: "Pass"` and empty `flagged_passages` array.
- [ ] No prose rewritten. No scenes written.
- [ ] No Story State KG writes from this skill — updates in `magic_system_updates_recommended` are routed by the brain.