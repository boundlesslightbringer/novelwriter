# Braided Narrative Technique Examples

## Example: Structural Health Check

### Input Context

```json
{
  "chapter_context": 14,
  "analysis_range": {
    "from_chapter": 1,
    "to_chapter": 14
  }
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Input shape:**
Module 2.2 excerpt (14 chapters):
  Ch. 1–4: Vara POV (capital, mission briefing, departure).
  Ch. 5–6: Aldric POV (capital, receiving reports of the Thornback situation).
  Ch. 7–9: Caradhen POV (passes, preparing for the envoy's arrival).
  Ch. 10–12: Vara POV (passes, first and second assessment meetings with Caradhen).
  Ch. 13: Aldric POV (capital, receives delayed report; authorises contingency).
  Ch. 14: Caradhen POV (passes, second meeting ends on cliffhanger).

Module 2.3 excerpt:
  Thread 004 — The Alliance Approach: Active. Convergence window: Ch. 18–22 (Vara's assessment reaches Aldric and produces a response that Caradhen must confront directly).
  Thread 007 — Sethric's Unspoken Judgment: Dormant. No convergence window established.
  Thread 012 — Aldric's Contingency: Active (new). No convergence window established yet.

### Output Artifacts

```json
{
  "braid_map_summary": {
    "pov_storylines": [
      {
        "character_id": "char_vara",
        "character_name": "Vara",
        "chapter_count": 7,
        "chapters": [1, 2, 3, 4, 10, 11, 12],
        "current_narrative_position": "Currently at the passes.",
        "storyline_status": "Active"
      },
      {
        "character_id": "char_aldric",
        "character_name": "Aldric",
        "chapter_count": 3,
        "chapters": [5, 6, 13],
        "current_narrative_position": "Capital. Gap of 7 chapters between appearances. Accumulating narrative pressure.",
        "storyline_status": "Active"
      },
      {
        "character_id": "char_caradhen",
        "character_name": "Caradhen",
        "chapter_count": 4,
        "chapters": [7, 8, 9, 14],
        "current_narrative_position": "At the passes. At cliffhanger.",
        "storyline_status": "Active"
      }
    ],
    "intersection_points": [
      {
        "chapter_numbers": [10, 11, 12, 14],
        "characters_involved": ["char_vara", "char_caradhen"],
        "nature": "direct interaction"
      }
    ],
    "current_braid_shape": "Two-strand braid (Vara/Caradhen interacting; Aldric running parallel). The braid has not yet brought all three POV timelines into meaningful contact."
  },
  "redundancy_flags": [
    {
      "chapters": [10, 11],
      "pov_characters": ["char_vara", "char_caradhen"],
      "shared_event": "The first assessment meeting.",
      "new_information_test": "PASS",
      "new_register_test": "PASS",
      "verdict": "Not redundant",
      "recommendation": "Monitor. If Ch. 15 shows Vara's version of the Ch. 14 cliffhanger moment, apply the tests again with the bar raised."
    }
  ],
  "convergence_opportunities": [
    {
      "threads_involved": ["thread_004"],
      "characters_involved": ["char_vara", "char_aldric", "char_caradhen"],
      "type": "Planned",
      "imminence": "Developing",
      "narrative_meaning": "Vara's assessment reaches Aldric and produces a response that Caradhen must confront directly.",
      "status": "On track",
      "note": "Vara's next chapter should show her composing/completing the assessment; Aldric needs a chapter before the courier arrives so the reader knows what he has authorised before Vara's assessment lands."
    },
    {
      "threads_involved": ["thread_007"],
      "characters_involved": ["char_caradhen", "char_sethric"],
      "type": "Discovered",
      "imminence": "Developing",
      "narrative_meaning": "Activation of Sethric's unspoken judgment.",
      "status": "On track",
      "note": "If Sethric appears in a Caradhen chapter within the next 3–5 chapters, the conditions for activating this thread will be present."
    }
  ],
  "parallel_tension_assessment": [
    {
      "chapters_span": [10, 14],
      "storylines_running_parallel": ["char_vara", "char_caradhen"],
      "thematic_rhyme": true,
      "dramatic_irony_active": true,
      "isolation_risk": false,
      "assessment": "High tension. The reader is inside both heads in alternating chapters; both are managing information; the dramatic irony (the reader knows Vara's assessment brief exists; Caradhen does not) is active and charged."
    },
    {
      "chapters_span": [5, 13],
      "storylines_running_parallel": ["char_aldric"],
      "thematic_rhyme": false,
      "dramatic_irony_active": true,
      "isolation_risk": true,
      "assessment": "Currently in isolation risk. Aldric has appeared in only 3 chapters across 14. His storyline is not yet in thematic rhyme with the passes storyline. The contingency authorisation (Ch. 13) creates the beginning of dramatic irony, but this irony will decay if Aldric's next chapter is delayed much further."
    }
  ],
  "recommendations": {
    "immediate": [
      "Aldric needs a chapter within the next 2 chapters. The contingency authorisation is the story's most significant live dramatic irony, and it is at risk of decaying."
    ],
    "near_term": [
      "Develop the Vara assessment -> Aldric reception sequence carefully. The dramatic irony architecture requires that the reader know Aldric's contingency before Vara's assessment lands."
    ],
    "monitor": [
      "Sethric/Thread 007 activation window. Caradhen's passes chapters are building toward a psychological state that makes the Sethric thread imminent. Watch for a natural entry point."
    ]
  },
  "kg_context_used": {
    "chapter_nodes_found": 14,
    "pov_characters_found": 3,
    "plot_threads_found": 3
  }
}
```