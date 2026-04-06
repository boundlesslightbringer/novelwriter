# Pacing Examples

## Example: Pacing Derivation

### Input Context

```json
{
  "pov_character_id": "char_caradhen",
  "chapter_context": 15,
  "last_scene_outcome": "Caradhen received word that Vara's assessment has reached Aldric and the contingency has been activated. He has one day to act.",
  "chapter_emotional_arc": "Opens in administrative normalcy. Moves through the arrival of the news, through the decision, to a close that is committed action."
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Module 1.1 excerpt (Caradhen of the Thornback):**
  Psychological/behavioral baseline:
    Habitual defense: encodes emotion in what he observes rather than naming it — displaces interior state onto external detail.
    Interiority: moderately high, but organised and purposeful.
    Cognitive style: sequential and tactical.
    Under pressure: goes still and very precise. Does not accelerate.
  Current state:
    Emotional state: The brittle calm of a decision already made but not yet enacted. His chest is tight. Awake since before the courier arrived.
    Active desire: To act before he thinks too carefully and stops himself.
    Active fear: That thinking will become an obstacle.
    Arc stage: Crisis approach.
    Physical state: Fatigued. Has not eaten.

### Output Artifacts

```json
{
  "pov_character_id": "char_caradhen",
  "character_psychology_summary": "Caradhen's habitual response to pressure is tactical stillness — he goes precise, not fast. Under acute pressure, his defense compresses further: sentences shorten, political observation disappears, and he begins counting things. His current state is at the outer edge of what this defense can hold.",
  "scene_rhythm_register": {
    "register": "Brittle",
    "justification": "Caradhen's psychology does not accelerate under pressure — it stills and compresses. Urgent would be wrong for this character even in a scene of genuine crisis. He is not genuinely in control — he is performing control over a decision that is costing him more than he is admitting. Brittle makes this character's specific crisis legible — the managed fracture of a man whose management system is working against him.",
    "internal_shift": {
      "present": true,
      "trigger_point": "The moment he issues the order to Sethric.",
      "destination_register": "Deliberate"
    }
  },
  "sentence_density": {
    "level": "Low",
    "justification": "His cognitive style under pressure is sequential and stripped of qualification; sentences should be short, declarative, and end on concrete nouns."
  },
  "interiority_level": {
    "level": "Compressed",
    "justification": "He is actively avoiding his own thoughts because he fears they will stop him from acting; interiority should be displaced entirely onto hyper-specific external observation."
  },
  "dialogue_to_action_ratio": {
    "ratio": "Action-heavy / Dialogue-sparse",
    "justification": "He is issuing orders, not discussing them; dialogue should be functional and one-sided."
  },
  "chapter_arc_alignment_note": "This scene sits at the climax of the chapter's arc. The brittle register holds the tension of the impending decision. The shift to 'Deliberate' after the order is given releases the acute tension into the committed action that closes the chapter.",
  "tension_flags": [
    {
      "type": "Overdrive risk",
      "description": "Risk of writing the crisis as 'Urgent' with fast, panicky prose, which violates his baseline of going still under pressure.",
      "instruction_for_scene_construction": "Keep the physical action slow and precise. The tension comes from the contrast between the massive consequence of the decision and the quiet, methodical way he executes it."
    },
    {
      "type": "Undercut risk",
      "description": "Risk of him explaining his decision to himself or Sethric.",
      "instruction_for_scene_construction": "Do not let him justify the choice in internal monologue or dialogue. The choice is made; the justification is what he is avoiding."
    }
  ],
  "kg_context_used": {
    "character_node_found": true
  }
}
```