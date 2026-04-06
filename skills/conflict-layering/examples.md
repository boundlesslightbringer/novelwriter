# Conflict Layering Examples

## Example 1: Scene Passing the Audit

### Input Context

```json
{
  "draft_scene": "Caradhen and Sethric ride out to inspect the northern pass. Sethric is quiet. Caradhen asks about the garrison readiness. Sethric gives precise, professional answers. Near the end of the ride, Caradhen says something about the envoy that is neutral on its face — that she is \"competent.\" Sethric says nothing. Caradhen notices the silence. The scene ends with them returning to the hall without having said anything that mattered.",
  "pov_character_id": "char_caradhen",
  "chapter_context": 3,
  "scene_intended_function": "Quiet scene — establish that something is wrong between Caradhen and Sethric before the story makes it explicit.",
  "other_character_ids": ["char_sethric"]
}
```

### Output Artifacts

```json
{
  "audit_header": {
    "pov_character_id": "char_caradhen",
    "scene_summary": "Caradhen and Sethric inspect the northern pass, ending in a loaded silence.",
    "intended_function": "Quiet scene — establish that something is wrong between Caradhen and Sethric before the story makes it explicit.",
    "momentum_verdict": "EARNING ITS PLACE"
  },
  "conflict_present": {
    "summary": "The scene is doing exactly what a quiet scene between these two characters should do. The conflict is entirely beneath the surface — it does not break through — and that is its structural point. Sethric's silence at the word 'competent' is doing the work of an entire confrontation. Caradhen notices it but does not name it. This is interpersonal conflict operating at depth without a single line of overt tension.",
    "primary_conflict_level": "Interpersonal",
    "operating_depth": "Depth"
  },
  "conflict_absent_or_underused": [],
  "conflict_weight_assessment": {
    "internal": {
      "status": "Latent",
      "note": "Present in what Caradhen does not let himself think. Appropriate for this scene's function."
    },
    "interpersonal": {
      "status": "Active",
      "note": "Sethric's silence is the scene's primary event. Functioning at full weight."
    },
    "societal": {
      "status": "Absent — not applicable",
      "note": "The scene is private and the social codes of the clan are not relevant to what the scene is doing."
    },
    "factional": {
      "status": "Absent — not applicable",
      "note": "The scene is not about the alliance; it is about these two men."
    },
    "existential": {
      "status": "Absent — not applicable",
      "note": "The scene is building toward the existential question, not yet touching it."
    }
  },
  "suggestions": [],
  "scene_rhythm_note": "The scene's silence at the end is the right landing point. One consideration: the moment Caradhen says 'competent' and Sethric goes quiet — if this is in the scene's final third, the reader may not have enough time to sit with it before the scene closes. If it is in the middle, the scene has room to breathe after the silence, which is better. Worth checking placement.",
  "summary_pattern_note": null,
  "kg_context_used": {
    "pov_character_found": true,
    "relationship_records_found": 1
  }
}
```

---

## Example 2: Scene Failing the Audit

### Input Context

```json
{
  "draft_scene": "Aldric meets with his council to discuss the envoy's mission. Three councillors offer opinions. Aldric listens, thanks them, and dismisses them. He is described as \"troubled by the political complexity.\" He decides to wait for Vara's report before acting.",
  "pov_character_id": "char_aldric",
  "chapter_context": 4,
  "scene_intended_function": "Show Aldric deliberating over the envoy's mission.",
  "other_character_ids": []
}
```

### Output Artifacts

```json
{
  "audit_header": {
    "pov_character_id": "char_aldric",
    "scene_summary": "Aldric hears from his council and decides to wait for Vara's report.",
    "intended_function": "Show Aldric deliberating over the envoy's mission.",
    "momentum_verdict": "UNDERLOADED"
  },
  "conflict_present": {
    "summary": "The scene contains the structural elements of a council scene but none of it lands as conflict. The councillors are delivering information; Aldric is receiving it. The scene is an information transfer dressed as a deliberation. 'Troubled by the political complexity' is declared conflict — the narration tells the reader that tension exists without creating its experience.",
    "primary_conflict_level": "Factional",
    "operating_depth": "Surface"
  },
  "conflict_absent_or_underused": [
    {
      "level": "Internal",
      "status": "Absent — available",
      "why_it_matters": "Aldric's core contradiction (belief in ruthlessness vs. need for validation) is entirely absent. A council scene is exactly where this contradiction should surface. Does he trust their read? Does the decision to 'wait' feel like strategy or relief?",
      "available_material": "Aldric's Module 1.1 record makes this internal conflict fully available."
    },
    {
      "level": "Interpersonal",
      "status": "Absent — available",
      "why_it_matters": "The council scene has three councillors but no characters. No councillor is pursuing anything or has a position that conflicts with Aldric's. A council in which all advisors are functionally identical is not a scene with interpersonal conflict.",
      "available_material": "If even one councillor has a stake in the outcome, that stake can carry the scene's interpersonal level."
    }
  ],
  "conflict_weight_assessment": {
    "internal": {
      "status": "Absent — available",
      "note": "Aldric's internal conflict is entirely absent despite being fully available."
    },
    "interpersonal": {
      "status": "Weak",
      "note": "Present in form (multiple characters in a room) but not in substance."
    },
    "societal": {
      "status": "Latent",
      "note": "The council itself is a societal structure; Aldric's authority within it is present as background. Not the primary weakness."
    },
    "factional": {
      "status": "Weak",
      "note": "The political situation is in the room but not under pressure."
    },
    "existential": {
      "status": "Absent — not applicable",
      "note": "Not applicable to this scene."
    }
  },
  "suggestions": [
    {
      "rank": 1,
      "specific_addition": "Give Aldric one moment of internal conflict around the decision to wait. He makes the decision, and then notices that it felt like a relief rather than a strategy.",
      "derived_from": "Aldric's self-deception.",
      "predicted_effect": "Transforms the decision from a non-event into a character revelation."
    },
    {
      "rank": 2,
      "specific_addition": "Give one councillor a position that costs Aldric something to dismiss. If Aldric dismisses a view that some part of him knows is correct, the scene has interpersonal weight.",
      "derived_from": "The existing council setting.",
      "predicted_effect": "Adds interpersonal tension and makes the deliberation meaningful."
    }
  ],
  "scene_rhythm_note": null,
  "summary_pattern_note": "A systematic tendency toward declared rather than dramatised conflict is visible here.",
  "kg_context_used": {
    "pov_character_found": true,
    "relationship_records_found": 0
  }
}
```