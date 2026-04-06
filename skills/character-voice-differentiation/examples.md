# Character Voice Differentiation Examples

## Example: Voice Profile Construction

### Input Context

```json
{
  "character_id": "char_caradhen",
  "chapter_context": 1
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Character:** Caradhen of the Thornback
**Module 1.1 excerpt:** [Full psychological record including — Core wound: led warband into alliance disaster at twenty-two; concluded other people's causes are pits without bottoms. Core desire: hand something intact to the next generation. Core fear: that what he is preserving has already been hollowed out. Self-deception: believes he is protecting his people; is also protecting himself from grief he has never allowed to arrive. Deliberative style: reasons carefully and completely before deciding; almost never changes a decision once made. Response to being correctly seen: goes still; leaves the conversation on a pretext. Values under pressure: preserves people over principle in almost all cases; has one exception he has never had to name aloud.]

### Output Artifacts

```json
{
  "character_id": "char_caradhen",
  "voice_profile": {
    "vocabulary_range": {
      "lexical_register": "Predominantly informal but precise; he has more education than he displays. Uses technical vocabulary for terrain, weather, livestock, and political arrangement — the vocabulary of someone who has had to manage real things in the physical world. No religious abstraction; no courtly register. When he reaches for an abstraction he tends to anchor it immediately to something physical.",
      "signature_vocabulary_categories": [
        "terrain and geography",
        "seasonal change",
        "practical labour",
        "the weight and maintenance of things"
      ],
      "avoids": [
        "Ideological vocabulary of any faction",
        "Anything that sounds like it belongs to someone else's cause"
      ]
    },
    "sentence_structure_patterns": {
      "default_sentence_length": "Medium-length, declarative, tending to end on a concrete noun or specific observation rather than a judgment. He reaches conclusions but usually buries them.",
      "structural_habits": "Observes, then draws inference, rarely states the inference — leaves it available to the reader. Rarely uses rhetorical questions. Almost never qualifies.",
      "under_stress": "Sentences compress. Observations without inference. Acts on information without processing it narratively. The gap between event and internal response widens — something happens, and three sentences of external description occur before the interior catches up."
    },
    "observational_focus": {
      "primary_lens": "Physical capability and intent. In any group, he clocks who is dangerous and in what specific way before registering anything else. In any space, he notes exits, sight lines, and the position of people relative to one another.",
      "secondary_lens": "Who in the room is lying to whom, including themselves.",
      "systematic_blind_spots": "Emotional need in others — not because he is unkind, but because his primary lenses are calibrated for threat and deception, not for distress that doesn't present as a problem to solve. People in grief who are not actively dangerous read to him as stable.",
      "how_they_read_people": "He looks at hands and feet before faces. Faces are performed; hands and feet are harder to control."
    },
    "internal_thought_patterns": {
      "deliberative_style": "Full, systematic, arrives at conclusions that he commits to. Rationalisation is almost never present — he genuinely thinks before he acts.",
      "self_monitoring": "Minimal. Does not examine his own motivations in narration. The gap between his stated reasons and his actual reasons is not visible to him and is therefore not narrated — the reader must infer it from what he systematically fails to notice about himself.",
      "memory_intrusion": "Rare, and almost always triggered by sensory specifics — a particular quality of light, the sound of a specific kind of wind in the passes, the smell of horses in cold weather. When memory intrudes it is brief and not followed by reflection. He notes it and continues.",
      "relationship_to_time": "Present-focused, with a heavy orientation toward maintaining the status quo for the future."
    },
    "emotional_processing_style": {
      "speed_of_acknowledgment": "Slow. Events land in the narration as events. The emotional weight arrives later, if at all — sometimes displaced onto an apparently unrelated observation about the physical world.",
      "internal_expression": "Almost never named directly. Emotion surfaces as impulse toward physical action, or as a sudden unusual precision in observation — he describes something in greater detail than necessary when he is trying not to feel something.",
      "what_they_cannot_look_at": "The question of whether the thing he is protecting is still worth protecting — whether his people are still the people his father's people were. Narration approaches this and turns. It will register as a non-sequitur change of subject.",
      "under_extreme_pressure": "Affect flattens. Observation becomes exhaustive and valueless — he describes what is in front of him with the thoroughness of someone trying to stay present by cataloguing."
    },
    "differentiation_notes": []
  },
  "kg_context_used": {
    "character_node_found": true,
    "culture_found": true,
    "existing_pov_profiles_found": 0
  }
}
```