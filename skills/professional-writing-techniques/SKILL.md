---
name: professional-writing-techniques
description: Applies specific advanced craft techniques to resolve local writing problems — single scenes or beats, not systemic tangles. Covers Skip and Return, Character Interview, Timeline Realignment, Consequence Trace-Back, Change POV, Freewrite the Tangle, and The Worse Choice Trick. Queries Story State KG for the excerpts relevant to the specific problem. Returns a technique application — a concrete path forward, a diagnostic, or a reframing — in artifacts. Invoked when a specific craft problem arises that does not require systemic tangle resolution.
---

# Professional Writing Techniques

## Identity

**Skill name:** `professional-writing-techniques`
**Purpose:** Apply a specific craft technique to a local writing problem — a single scene or beat that is stuck, flat, or unresolvable through normal scene-construction passes. This skill is tangle-focused for local problems. General prose quality improvement is `self-editing-and-refinement`'s domain. Systemic tangles that cannot be resolved in a single scene are escalated via the Reassess Trigger.

---

## Core

Apply specific advanced craft techniques to resolve writing problems. Covers: Skip and Return, Character Interview, Timeline Realignment, Consequence Trace-Back, Change POV, Freewrite the Tangle, The Worse Choice Trick. Return a concrete path forward, a diagnostic, or a reframing of the problem for the brain to act on. Does not write the scene — identifies the decision that unblocks `scene-construction`.

---

## Input

### From brain context (`worker_request.context`)

1. **`problem_description`** — A specific description of the local craft problem. Required. Should name: what has been attempted, what is not working, and what the stuck point is. Example: "The scene ends on Caradhen's choice but the choice feels arbitrary — both options feel equally available and I cannot find a reason to pick one over the other."

2. **`pov_character_id`** — The `logical_id` of the POV character involved. Required.

3. **`chapter_context`** — Current chapter number. Used to scope KG queries. Required.

4. **`stuck_draft`** (optional) — The partial or problematic draft prose, if the problem is in an existing draft rather than in planning. Passed when the brain has a scene that is written but is not working.

5. **`technique_hint`** (optional) — If the brain has a specific technique in mind (e.g. "try The Worse Choice Trick"), it can pass it here. The skill applies the hinted technique if it is appropriate for the problem type, or explains why a different technique is more suitable.

### Fetched from Story State KG

The writing_subagent queries the Story State KG for the records most relevant to the specific problem. The query scope is narrower than other writing skills — this skill targets only what is needed to diagnose and resolve the specific local issue:

```
# POV character — psychological record and current state
query_kg_nodes({logical_id: pov_character_id, type: "Character"},
               as_of_chapter=chapter_context)

# For choice-related problems: active consequence chains
# to understand what the choice is embedded in
query_kg_nodes({type: "CascadeChain"}, as_of_chapter=chapter_context)
# (filter to chains involving pov_character_id)

# For timeline or continuity problems: recent Chapter nodes
query_kg_nodes({type: "Chapter",
                "properties.chapter_number": {"$gte": chapter_context - 3}},
               as_of_chapter=chapter_context)

# For POV or voice problems: character voice profile
# (retrieved from Character node properties.voice_profile)
```

The writing_subagent should not run all of these queries by default — only the queries relevant to the specific problem type. A choice-arbitrariness problem requires the Character node and CascadeChain queries; a timeline problem requires the Chapter node query; a voice drift problem requires the Character node (for voice profile). Unnecessary KG queries waste tool calls.

If any relevant query returns no results, note the absence in `kg_context_used` and proceed with what is available.

---

## Output

All output is returned in `artifacts`. Technique application is pure analysis and path-forward — no KG persistence needed. The brain uses the output to decide the next delegation (usually re-delegating `scene-construction` with the path forward as context).

### `artifacts` structure

```json
{
  "technique_applied": "<name of the technique used>",
  "problem_diagnosis": {
    "problem_type": "<classified problem type>",
    "root_cause": "<specific diagnosis of why the scene/beat is not working>",
    "what_is_available": "<what material already exists that the path forward uses>"
  },
  "path_forward": {
    "primary_recommendation": "<specific, actionable: the decision or reframe that unblocks the scene>",
    "worked_application": "<the technique applied to this specific problem — not generic advice but the actual result of running this technique on this character, this scene, this choice>",
    "alternatives": ["<if applicable: one or two alternatives if primary is uncertain>"]
  },
  "scene_construction_context": "<a brief paragraph the brain can pass directly as `feedback` context in the re-delegation of scene-construction — written so scene-construction can act on it without needing to read this full report>",
  "kg_context_used": {
    "character_node_found": true,
    "cascade_chains_checked": false,
    "recent_chapters_checked": false
  }
}
```

`scene_construction_context` is the most important field for the brain's routing. It is written to be passed directly as the `feedback` key in the next `scene-construction` context dict — the brain does not need to synthesise or translate this output.

---

## The Seven Techniques

### Skip and Return

**When to apply:** The scene cannot find its ending; the beat that should close the scene remains elusive; writing forward is not producing a resolution.

**Application:** Leave the scene at its current point. Establish where the story's next stable beat is (the next scene that the writer can clearly see). Write forward to that stable beat, then return. Often the ending of the stuck scene becomes visible in retrospect — it was concealed by the pressure of trying to write directly into it.

**Worked application:** Identify the next scene that is clearly visible given the character's trajectory. State it specifically. Frame the skip as "proceed to [next stable beat], then return to this scene with the knowledge of what that beat requires from this one."

### Character Interview

**When to apply:** The character's choice feels arbitrary; both options feel equally available; the character seems to be making decisions that contradict their psychology; the writer cannot find the character's genuine motivation.

**Application:** Step outside the narrative frame. Ask the character directly, in their own voice: *What do you want here? What are you afraid of? What would you never admit to yourself?* The answers emerge from the character's `core_wound`, `self_deception`, and `response_patterns` in the Character node. The interview is internal — it is not a scene, it is a diagnostic to find the real choice.

**Worked application:** Draw the character's core contradiction from the Character node. Frame the specific scene situation against that contradiction. State what each side of the contradiction pulls the character toward in this scene — this is the genuine choice that the arbitrary-feeling choice is masking.

### Timeline Realignment

**When to apply:** The scene's events seem to be happening at the wrong time; a consequence is arriving too early or too late; the character is in a situation that does not make sense given what just happened.

**Application:** Reconstruct the timeline from the most recent Chapter nodes. Identify where the temporal sequence has drifted from the causal sequence. The fix is usually adjusting the scene's position in the timeline, not the scene's content.

**Worked application:** Using the Chapter nodes retrieved from Story State, reconstruct the timeline of the last 3–5 chapters. Identify the specific temporal or causal discontinuity. State the adjustment needed.

### Consequence Trace-Back

**When to apply:** The scene does not feel earned; the character arrives at this choice or situation without a clear causal path from prior events; the scene feels imposed rather than discovered.

**Application:** Trace backward from the stuck scene to the last clearly established cause. The gap between the established cause and the current scene's situation is the missing material. Fill the gap — not necessarily with new scenes, but by understanding what intermediate consequence was not tracked.

**Worked application:** Using the CascadeChain nodes, trace the consequence chain backward from the stuck situation. Identify the missing link — the consequence that would have produced the character's current state from the last established event. State what that missing link is and whether it needs to be written as a scene or simply established as an off-page event in the narration.

### Change POV

**When to apply:** The scene cannot be written from this POV character's perspective; the information the scene needs to convey is not available to this character; the scene keeps trying to access knowledge the POV character does not have.

**Application:** Identify which other POV-eligible character (per `pov_eligible: true` in Character nodes) could narrate this scene or moment and would have natural access to what the scene needs to establish. Assess whether a POV switch is appropriate given the multi-POV structure or whether the scene should be approached differently.

**Worked application:** Query POV-eligible characters. Identify which character has access to what the scene requires. Assess against the multi-POV structure and the POV proliferation constraint. If a POV switch is appropriate, state which character and why. If it is not appropriate, identify what this POV character *can* see that serves the scene's purpose.

### Freewrite the Tangle

**When to apply:** The problem cannot be diagnosed; the scene resists all analytical approaches; the writer has reached the limit of thinking about it.

**Application:** Set the analytical frame aside. Write the scene freely, without trying to make it work — without applying voice profile, without constraining to scene parameters, without worrying about POV consistency. The act of writing without constraint often produces the image or moment that the constrained approach was blocking.

**Worked application:** This technique cannot be pre-worked — it is by definition outside the analytical frame. What this skill provides is the instruction to the writer: *Stop analysing. Write the scene wrong, quickly, without constraints. Look at what comes out.* The output of this technique is not a scene — it is a diagnostic image or moment that identifies what the scene actually needs.

In the context of this system: return a clear instruction to the brain to set aside the current scene parameters and re-delegate `scene-construction` with a note permitting the skill to write without optimising for POV consistency or conflict layering — to write to discover, not to produce a final draft.

### The Worse Choice Trick

**When to apply:** The character's choice feels too safe; both options are acceptable; the scene lacks genuine stakes; the choice does not feel like it costs anything real.

**Application:** For each option in the choice, ask: *What is the worst version of this outcome — not the most dramatic, but the most true to what this character would most want to avoid?* The worse choice is not the more painful choice; it is the choice that most directly implicates the character's core contradiction and forces them to reveal who they actually are under pressure.

**Worked application:** Using the Character node's `core_contradiction`, `core_fear`, and `values_under_pressure`, identify what each choice option would cost this specific character at the deepest level. State what the worse choice is — the one that most directly tests the character's core contradiction. Frame the scene around that cost rather than around the abstract options.

---

## Problem Type Classification

Use this table to select the most appropriate technique given the problem description:

| Problem type | Primary technique | Secondary technique |
|---|---|---|
| Choice feels arbitrary, both options equally available | Character Interview | The Worse Choice Trick |
| Scene cannot find its ending | Skip and Return | Freewrite the Tangle |
| Scene feels unearned, disconnected from prior events | Consequence Trace-Back | Timeline Realignment |
| Sequence feels temporally or causally wrong | Timeline Realignment | Consequence Trace-Back |
| Scene keeps trying to access information the POV doesn't have | Change POV | Character Interview |
| Character keeps making implausible decisions | Character Interview | Consequence Trace-Back |
| Everything analytical has failed | Freewrite the Tangle | — |
| Stakes are present but nothing feels at risk | The Worse Choice Trick | Character Interview |

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Boundary

- **Local problems only.** If the problem is systemic — non-converging plotlines, a character logic problem spanning multiple chapters, a choice that breaks the established plot — this is a systemic tangle. Return `need_input` with a note that the problem may require the Reassess Trigger rather than a local technique.
- **Does not write scenes.** Returns a path forward — the decision or reframe that unblocks `scene-construction`.
- **Does not update the Story State KG.** Output is analysis and path forward only.
- **Does not handle general prose quality improvement.** That is `self-editing-and-refinement`'s domain.

---

## Invocation

The `writing_subagent` invokes this skill when the brain delegates a local craft problem resolution:

- When a specific craft problem arises in a single scene or beat that does not require systemic tangle resolution.
- Typically invoked after `scene-construction` has been re-delegated multiple times on a scene and the quality gate keeps rejecting the output, suggesting the problem is in the scene parameters or character logic rather than in execution.
- When the brain's quality gate notes a `parameter_discrepancy_flag` that suggests a deeper character logic issue requiring diagnosis rather than a simple re-delegation.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | Character node (POV character — full psychological record and voice profile); optionally CascadeChain nodes (for consequence trace-back); optionally recent Chapter nodes (for timeline realignment). Query scope is narrowed to what is relevant to the specific problem type |
| **Returns in artifacts** | Technique application — diagnosis, path forward, worked application, `scene_construction_context` for direct use as `feedback` in next `scene-construction` delegation. No KG persistence needed |

---

## Dependencies

**Upstream:** Brain provides `problem_description`, `pov_character_id`, `chapter_context`, and optionally `stuck_draft` and `technique_hint`. Character node must be in Story State KG.

**Downstream:** `scene_construction_context` in artifacts is passed by the brain as the `feedback` key in the subsequent `scene-construction` context dict. The brain re-delegates `scene-construction` with this context alongside the original scene parameters.

---

## Instructions

### Step 1 — Query the Story State KG

Determine from `problem_description` which problem type this is. Run only the KG queries relevant to that problem type — do not run all available queries. Populate `kg_context_used`.

### Step 2 — Classify the problem

Use the problem type classification table to identify the primary technique. If `technique_hint` is provided in context, verify whether it is appropriate for the problem type. If not, explain briefly and apply the more appropriate technique.

Classify the problem type explicitly in `problem_diagnosis.problem_type`.

### Step 3 — Diagnose the root cause

Using the Character node and any other KG records retrieved, diagnose specifically why the scene or beat is not working. Avoid vague diagnoses ("the choice is unclear") — aim for specific root causes ("the choice feels arbitrary because both options require the character to act against their `core_contradiction` in the same way — there is no option that aligns with their stated values, so neither option is characteristically theirs").

State what available material already exists in the scene parameters, Character node, or Story State that the path forward will use.

### Step 4 — Apply the technique to the specific problem

Apply the selected technique to this specific character, in this specific situation, with this specific problem. The output must be the result of actually running the technique — not a description of how the technique works in general.

For Character Interview: draw from `core_wound`, `core_contradiction`, `self_deception`, `response_patterns`.
For Consequence Trace-Back: use CascadeChain nodes and Chapter node sequence.
For Timeline Realignment: use Chapter node chapter numbers and dates.
For The Worse Choice Trick: use `core_contradiction`, `core_fear`, `values_under_pressure`.

### Step 5 — Write the scene_construction_context

Write a single paragraph that the brain can pass directly as `feedback` in the next `scene-construction` delegation. This paragraph should:
- Name the specific issue in one sentence
- Give the specific instruction that resolves it
- Reference the character's psychology specifically (not generically)

This field is for `scene-construction` to read, not for the brain. Write it in the second person addressed to the scene writer, not to the orchestrator.

### Step 6 — Assemble and return artifacts

Return the complete artifacts dict with `status: "success"`. If the problem appears systemic rather than local, set `status: "need_input"` and explain in `summary` that the Reassess Trigger may be more appropriate.

---

## Quality Checks

Before returning output, verify:

- [ ] Character node was found in KG; `character_node_found: true`.
- [ ] Only queries relevant to the specific problem type were run — not all available queries.
- [ ] Problem type is explicitly classified in `problem_diagnosis.problem_type`.
- [ ] `problem_diagnosis.root_cause` is specific — not "the choice is unclear" but names the exact psychological or structural mechanism.
- [ ] `path_forward.worked_application` is the result of running the technique on this specific problem — not generic technique description.
- [ ] `scene_construction_context` is written for `scene-construction` to act on directly.
- [ ] Problem is local (single scene or beat) — systemic problems return `need_input`.
- [ ] No scenes written. No Story State KG writes from this skill.