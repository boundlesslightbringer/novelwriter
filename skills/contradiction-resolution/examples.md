# Contradiction resolution — examples

### Example 1 — Mode 1 output for a Timeline contradiction

**Input (abridged):**
```json
{
  "mode": "ANALYSE",
  "contradiction_record": {
    "contradiction_id": "CONT-9-1711612800",
    "nature": "Timeline",
    "description": "Jon Snow's proposed location 'King's Landing' on Day 45 of Chapter 9 is impossible. Last recorded at Castle Black on Day 43. Travel time is 18 days. Only 2 days have elapsed."
  },
  "blocked_write": {
    "write_type": "Character location change",
    "proposed_payload": { "character": "Jon Snow", "location": "King's Landing", "chapter": 9 }
  }
}
```

**Output:**
```json
{
  "mode": "ANALYSE",
  "contradiction_id": "CONT-9-1711612800",
  "briefing": "The story tried to place Jon Snow at King's Landing in Chapter 9. However, Jon was last seen at Castle Black just two days before that chapter, and the ride between those two locations takes at least eighteen days. The geography doesn't allow for it. Either Jon's arrival at King's Landing needs to happen in a later chapter, his departure from Castle Black needs to be moved back in the timeline, or there needs to be a story reason for him to travel faster than normal.",
  "resolution_options": [
    {
      "option_id": "A",
      "label": "Move Jon's arrival to a later chapter",
      "description": "Shift the Chapter 9 location event forward to Chapter 12 or later, when eighteen days of travel have elapsed. No other records need to change.",
      "affected_modules": ["1.1", "2.1"],
      "complexity": "Low"
    },
    {
      "option_id": "B",
      "label": "Move Jon's departure from Castle Black earlier",
      "description": "Insert a new timeline event in which Jon departs Castle Black before Day 27, giving him enough travel time to reach King's Landing by Day 45. Earlier chapters may need a note that Jon left sooner than previously recorded.",
      "affected_modules": ["2.1", "5.2"],
      "complexity": "Medium"
    },
    {
      "option_id": "C",
      "label": "Introduce a faster travel method",
      "description": "Add a world-state event in which Jon travels by ship along the coast, which the geography records allow at 4 days. Add a new entry to Module 2.1 and a travel record to Module 3.2.",
      "affected_modules": ["2.1", "3.2", "5.2"],
      "complexity": "Medium"
    },
    {
      "option_id": "D",
      "label": "Accept as intentional ambiguity",
      "description": "Mark the timeline discrepancy as a deliberate narrative gap — perhaps the timeline is being told through an unreliable chronicle. The contradiction is logged as accepted and the write proceeds.",
      "affected_modules": [],
      "complexity": "Low"
    }
  ],
  "recommended_option": "A",
  "recommendation_rationale": "Moving the arrival date is the least invasive change and requires no rewrites to earlier chapters."
}
```

---

### Example 2 — Mode 2 input after user chooses Option A

```json
{
  "mode": "IMPLEMENT",
  "contradiction_id": "CONT-9-1711612800",
  "contradiction_record": { "...": "..." },
  "blocked_write": {
    "write_type": "Character location change",
    "proposed_payload": { "character": "Jon Snow", "location": "King's Landing", "chapter": 9 }
  },
  "user_decision": {
    "chosen_option_id": "A",
    "custom_instructions": "",
    "accepted_as_intentional": false
  }
}
```

**Mode 2 derives these writes:**
1. Update Module 1.1 — Jon Snow's location event: move chapter reference from 9 to 12.
2. Update Module 2.1 — Absolute Timeline: move Jon's King's Landing arrival event from Day 45 / Chapter 9 to Day 61 / Chapter 12.
3. Update Module 5.3 — close the contradiction record.

**Output:**
```json
{
  "mode": "IMPLEMENT",
  "status": "RESOLVED",
  "contradiction_id": "CONT-9-1711612800",
  "resolution_type": "Resolved",
  "writes_executed": [
    { "operation": "update", "collection": "module_1_1", "filter": { "character": "Jon Snow" }, "outcome": "success" },
    { "operation": "update", "collection": "module_2_1", "filter": { "event": "Jon Snow arrives King's Landing" }, "outcome": "success" },
    { "operation": "update", "collection": "module_5_3", "filter": { "contradiction_id": "CONT-9-1711612800" }, "outcome": "success" }
  ],
  "module_5_3_updated": true,
  "re_issue_signal": {
    "action": "RE_ISSUE_BLOCKED_WRITE",
    "originating_write_type": "Character location change",
    "note": "Resolution complete. The originating subagent must re-issue the blocked write with the updated chapter reference (Chapter 12). The WorldBibleManager will re-run contradiction detection on the re-issued write."
  }
}
```
