# Contradiction detection — examples

### Example 1 — MINOR write, CLEAR

**Input:**
```json
{
  "write_type": "Update emotional / psychological state",
  "severity": "MINOR",
  "target_module": "1.1",
  "proposed_payload": {
    "character": "Eddard Stark",
    "field": "emotional_state",
    "new_value": "Grief-stricken and politically isolated",
    "chapter": 7
  },
  "prefetched_docs": [
    {
      "module": "1.1",
      "character": "Eddard Stark",
      "emotional_state": "Suspicious and determined",
      "chapter_snapshot": 6
    }
  ]
}
```

**Reasoning:** MINOR write — run Check 4 (Logical) only. The field
`emotional_state` is not tracked in Module 5.1 as a physical continuity record.
No logical dependency check required for emotional state. No contradiction found.

**Output:**
```json
{
  "verdict": "CLEAR",
  "write_type": "Update emotional / psychological state",
  "severity": "MINOR",
  "checks_run": ["Logical"],
  "checks_skipped": ["Physical", "Knowledge", "Timeline"],
  "skip_reason": "Severity MINOR — single-module check only"
}
```

---

### Example 2 — MAJOR write, BLOCKED (Timeline)

**Input:**
```json
{
  "write_type": "Character location change",
  "severity": "MAJOR",
  "target_module": "1.1",
  "proposed_payload": {
    "character": "Jon Snow",
    "field": "location",
    "new_value": "King's Landing",
    "chapter": 9,
    "chapter_date": "Day 45"
  },
  "prefetched_docs": [
    {
      "module": "1.1",
      "character": "Jon Snow",
      "location": "Castle Black",
      "chapter_snapshot": 8,
      "chapter_date": "Day 43"
    },
    {
      "module": "3.2",
      "route": "Castle Black → King's Landing",
      "travel_time_horse": "18 days"
    },
    {
      "module": "5.1",
      "subject": "Jon Snow",
      "detail": "Black cloak of the Night's Watch",
      "established_chapter": 3
    },
    {
      "module": "5.2",
      "time_consistency_log": []
    }
  ]
}
```

**Reasoning:** MAJOR write. Run Check 1 (Physical) first — no physical field
being changed, CLEAR. Run Check 2 (Knowledge) — no knowledge field, CLEAR. Run
Check 3 (Timeline): last known location is Castle Black on Day 43. Proposed
location is King's Landing on Day 45. Travel time is 18 days. Days elapsed: 2.
2 < 18 → BLOCKED.

**Output:**
```json
{
  "verdict": "BLOCKED",
  "write_type": "Character location change",
  "severity": "MAJOR",
  "checks_run": ["Physical", "Knowledge", "Timeline"],
  "checks_skipped": ["Logical"],
  "skip_reason": "Halted at first contradiction",
  "contradiction_record": {
    "contradiction_id": "CONT-9-1711612800",
    "detected_at_chapter": 9,
    "nature": "Timeline",
    "conflicting_records": ["1.1:jon_snow_ch8", "3.2:castle_black_kings_landing"],
    "description": "Jon Snow's proposed location 'King's Landing' on Day 45 of Chapter 9 is impossible. His last recorded location is Castle Black on Day 43 (Chapter 8). The travel time from Castle Black to King's Landing by horse is 18 days (Module 3.2). Only 2 days have elapsed. The proposed write violates timeline continuity by 16 days.",
    "resolution_status": "Unresolved",
    "resolution_notes": ""
  }
}
```

---

### Example 3 — MAJOR write, BLOCKED (Knowledge)

**Input:**
```json
{
  "write_type": "Belief or current knowledge state update",
  "severity": "MAJOR",
  "target_module": "1.2",
  "proposed_payload": {
    "character": "Sansa Stark",
    "information_item": "Cersei Lannister plans to execute Eddard Stark",
    "status": "KNOWS",
    "chapter": 9,
    "source": "Overheard in the Red Keep corridors"
  },
  "prefetched_docs": [
    {
      "module": "1.2",
      "character": "Sansa Stark",
      "knowledge_entries": [
        {
          "information_item": "Cersei Lannister plans to execute Eddard Stark",
          "status": "DOES NOT KNOW",
          "acquired_at_chapter": null
        }
      ]
    },
    {
      "module": "5.2",
      "information_flow_log": []
    }
  ]
}
```

**Reasoning:** MAJOR write. Skip Check 1 (Physical — not relevant). Run Check 2
(Knowledge): the payload adds a KNOWS record for Sansa about Cersei's plan. The
Module 5.2 Information Flow Log has no entry showing this information was
transmitted to Sansa at Chapter 9. The payload claims "overheard in the Red Keep
corridors" — but no corresponding event in Module 2.1 or 5.2 establishes that
Sansa was present at such a conversation at Chapter 9. No transmission record
exists → BLOCKED.

**Output:**
```json
{
  "verdict": "BLOCKED",
  "write_type": "Belief or current knowledge state update",
  "severity": "MAJOR",
  "checks_run": ["Knowledge"],
  "checks_skipped": ["Physical", "Timeline", "Logical"],
  "skip_reason": "Halted at first contradiction",
  "contradiction_record": {
    "contradiction_id": "CONT-9-1711612900",
    "detected_at_chapter": 9,
    "nature": "Knowledge",
    "conflicting_records": ["1.2:sansa_stark", "5.2:information_flow_log"],
    "description": "Proposed write upgrades Sansa Stark's knowledge of 'Cersei Lannister plans to execute Eddard Stark' from DOES NOT KNOW to KNOWS at Chapter 9, citing 'overheard in the Red Keep corridors' as the source. Module 5.2 Information Flow Log contains no record of this information being transmitted to Sansa. No event in the pre-fetched documents establishes Sansa's presence at a relevant conversation at Chapter 9. The knowledge acquisition has no established transmission record.",
    "resolution_status": "Unresolved",
    "resolution_notes": ""
  }
}
```
