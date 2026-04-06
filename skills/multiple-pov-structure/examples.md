# Multiple POV Structure Examples

## Example: POV Chapter Schedule

### Input Context

```json
{
  "chapter_context": 15
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Module 2.2 excerpt (last 6 chapters):**
  Ch. 12 — POV: Vara (the envoy). Location: The Thornback passes. Summary: Vara conducts her first formal assessment meeting with Caradhen. He does not commit; she notes the pattern. Cliffhanger: No. Delta: Vara has begun compiling her assessment brief.
  Ch. 13 — POV: Aldric (the king). Location: The capital. Summary: Aldric receives a report that the envoy's mission is delayed; he is told Caradhen is "considering." His response is visible frustration, controlled. Cliffhanger: No. Delta: Aldric has privately authorised a contingency.
  Ch. 14 — POV: Caradhen. Location: The Thornback passes. Summary: Caradhen hosts Vara's second meeting. She shifts her approach — stops asking about the passes, starts asking about his people. He does not know what to do with this. Cliffhanger: Yes — chapter ends the moment Vara asks a question that Caradhen cannot answer without revealing something he has not decided to reveal.

**Module 2.1 excerpt:**
  Current story date: Day 47 of the king's third year.
  Simultaneous events: While Ch. 14 was occurring at the passes (Day 46–47), Aldric's contingency authorisation produced a specific instruction to a third party (Day 46). That instruction has not yet been shown from any POV.
  Travel records: Vara's courier departed the passes on Day 45 toward the capital — arrival expected Day 52.

### Output Artifacts

```json
{
  "recommended_next_pov": {
    "character_id": "char_vara",
    "character_name": "Vara",
    "reasoning": "Caradhen's chapter (Ch. 14) ended on a cliffhanger — Vara's unanswered question is hanging in the scene. Cutting away is the correct call here: the reader knows Vara asked something Caradhen cannot easily answer; dwelling in his perspective will dissipate the tension rather than build it. Vara's POV is the right cut because: (1) the reader does not yet know what Vara is actually assessing; (2) Vara's assessment brief is the mechanism through which Aldric's contingency becomes relevant; (3) her courier has already departed, which means her chapter has a natural structural question: what exactly did she send?",
    "last_appeared_chapter": 12,
    "chapters_since_last_pov": 2
  },
  "simultaneous_events": [
    {
      "character_id": "char_aldric",
      "event_description": "Aldric's contingency instruction (Day 46) was issued while Caradhen's chapter was occurring.",
      "pov_can_know": false,
      "dramatic_irony_active": true,
      "timeline_contradiction_risk": false,
      "note": "Vara does not know about it — she is at the passes, the instruction was issued at the capital, and no communication has reached her. The next chapter must not give Vara knowledge of this event. It is running in Vara's chapter's temporal background: the reader knows it exists; Vara does not. This is active dramatic irony and should be preserved."
    },
    {
      "character_id": "char_vara",
      "event_description": "Vara's courier departed Day 45. The next chapter is set on Day 47–48. The courier is en route but has not arrived.",
      "pov_can_know": true,
      "dramatic_irony_active": false,
      "timeline_contradiction_risk": false,
      "note": "No information has been delivered yet. This is consistent and requires no intervention."
    }
  ],
  "rotation_pressure_flags": [
    {
      "character_id": "char_vara",
      "character_name": "Vara",
      "pressure_level": "High",
      "reason": "Her storyline has direct momentum; the assessment brief is the next structural beat."
    },
    {
      "character_id": "char_aldric",
      "character_name": "Aldric",
      "pressure_level": "High",
      "reason": "His contingency instruction has been issued but not shown from his perspective. His storyline is accumulating unrevealed consequence. He needs a chapter within the next 2–3 to show what he has actually authorised and why."
    },
    {
      "character_id": "char_caradhen",
      "character_name": "Caradhen",
      "pressure_level": "Low",
      "reason": "His cliffhanger is best left unresolved for at least one chapter. His pressure will build in his absence."
    },
    {
      "character_id": "char_sethric",
      "character_name": "Sethric",
      "pressure_level": "Low",
      "reason": "Dormant thread; no pressure."
    }
  ],
  "cliffhanger_handling": {
    "previous_chapter_cliffhanger": true,
    "cliffhanger_description": "Chapter ends the moment Vara asks a question that Caradhen cannot answer without revealing something he has not decided to reveal.",
    "recommendation": "cut_away",
    "reasoning": "Dwelling in his perspective will dissipate the tension rather than build it. The reader knows Vara asked something Caradhen cannot easily answer."
  },
  "pov_proliferation_check": {
    "current_active_pov_count": 3,
    "new_pov_proposed": false,
    "governing_constraint_met": null,
    "note": "Current rotation period is manageable — each character appears roughly every 2–3 chapters. No structural pressure."
  },
  "kg_context_used": {
    "chapter_nodes_found": 14,
    "pov_characters_found": 3,
    "active_threads_found": 2
  }
}
```