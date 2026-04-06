# Single POV Structure Examples

The following example demonstrates the expected input and output for the `single-pov-structure` skill.

## Example — Validating a User's POV Request

### Input Context (from Brain and Story State KG)

```yaml
Requested POV: Aldric (the king).
User's stated reason: "I want to show what Aldric is thinking after authorising the contingency — before Vara's report reaches him."

Module 2.2 excerpt (POV Chapter Log):
  Ch 12: Vara (Arrival at the passes)
  Ch 13: Aldric (Authorises the contingency in the capital)
  Ch 14: Caradhen (Meeting with Vara, ends on a tense question)

Module 2.1 excerpt (Absolute Timeline):
  Day 45: Vara's courier departs the passes for the capital.
  Day 46-47: Vara and Caradhen's meetings occur.
  Day 47 (Current): Aldric is in the capital. Courier is still en route (expected Day 52).
```

### Output shape (JSON `artifacts`)

```json
{
  "requested_assignment": {
    "requested_pov": "Aldric",
    "validation_status": "CLEAR",
    "validation_notes": "Aldric's last chapter was Ch. 13; the current chapter is 15. Aldric is in the capital, where he was last placed — no travel or location contradiction. His storyline (the contingency authorisation) has accumulated pressure; a chapter now is structurally well-timed. The assignment is consistent with the story state."
  },
  "intent_alignment": {
    "users_intent": "Show Aldric's internal state after authorising the contingency, before Vara's report arrives.",
    "story_state_confirmation": "This intent is achievable. Vara's courier departed the passes on Day 45; it is currently Day 47; the courier is not expected until Day 52. Aldric has not yet received any report. The chapter can show him in the aftermath of the authorisation, in the knowledge gap before the assessment lands.",
    "alignment_notes": "The 'contingency' (Ch. 13) was shown only as an authorisation — what Aldric actually instructed the third party to do has not been rendered. A chapter from his POV now is the natural moment to establish, in his own internal terms, what he has set in motion. This is the chapter's most load-bearing potential."
  },
  "simultaneous_events": [
    {
      "pov_character": "Caradhen / Vara",
      "event": "Meeting at the northern passes (Ch. 14, Day 46–47)",
      "plausible_knowledge": false,
      "knowledge_notes": "Aldric does not and cannot know the content of this meeting — no communication has reached him. The reader, however, knows it. This is active dramatic irony. If he refers to 'the envoy's mission' it should be from the general knowledge that she is there, not from any specific awareness of what is happening in the room.",
      "contradiction_risk": false
    },
    {
      "pov_character": "Vara",
      "event": "Courier dispatch (Day 45)",
      "plausible_knowledge": false,
      "knowledge_notes": "Aldric does not know the courier has departed — courier dispatch is not the kind of event that would have been communicated to him in advance.",
      "contradiction_risk": false
    }
  ],
  "rotation_pressure_flags": [
    {
      "character": "Vara",
      "pressure_level": "High",
      "notes": "Her assessment brief is building; she is at the passes. Skipping her for one chapter is sound, but her next chapter should likely follow Aldric's."
    },
    {
      "character": "Caradhen",
      "pressure_level": "Low",
      "notes": "His cliffhanger is best left unresolved for at least one more chapter. Aldric's chapter serves this well."
    }
  ],
  "cliffhanger_handling": {
    "previous_chapter_cliffhanger": true,
    "cutting_away": true,
    "handling_assessment": "The previous chapter (Ch. 14, Caradhen) ended on a cliffhanger — Vara asked a question Caradhen cannot easily answer. Cutting to Aldric is a motivated cut: the reader is left in Caradhen's suspended moment, while the chapter reveals what Aldric has authorised. When the reader returns to Caradhen (or to Vara), the dramatic irony will be compounded. The cut is purposeful."
  },
  "pov_proliferation_check": {
    "is_new_pov": false,
    "assessment": "Aldric is an established POV character (Ch. 5–6, Ch. 13). No proliferation concern."
  }
}
```