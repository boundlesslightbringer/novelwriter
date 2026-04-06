# Plot Thread Tracking Examples

## Example: Convergence Checkpoint Analysis

### Input Context

```json
{
  "chapter_context": 14,
  "convergence_mode": true
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Module 2.3 excerpt:**
  Thread 004 — The Alliance Approach: Active. Origin: Ch. 1. Characters: Vara, Caradhen, Aldric (indirect). Expected convergence: Ch. 18–22. Status: Developing — Vara's assessment is being compiled; Caradhen has not committed; Aldric's contingency is active.
  Thread 007 — Sethric's Unspoken Judgment: Dormant. Origin: Ch. 9 (Caradhen chapter, Sethric background presence). Characters: Sethric, Caradhen. No convergence window established.
  Thread 012 — Aldric's Contingency: Active. Origin: Ch. 13. Characters: Aldric, unnamed third party, Caradhen (future). No convergence window established.
  Thread 002 — The Dowager's Trial: Resolved. Ch. 3. Resolution: The formal charges were filed.
  Thread 001 — The Regency's Legacy: Active. Origin: Ch. 1. Characters: Aldric, the Dowager (absent). Expected convergence: Ch. 25–30. Status: Background pressure; not yet directly developed.

**Module 2.4 excerpt:**
  Payoff 001: The Dowager's letter (Chekhov's gun). Planted: Ch. 4. Window: Ch. 15–20. Status: Pending.
  Payoff 002: Vara's assessment brief (Consequence bomb). Planted: Ch. 10. Detonation trigger: When the assessment brief reaches Aldric directly. Narrative phase anchor: Convergence. Priority tier: Essential. Status: Pending.
  Payoff 003: Caradhen's thirty-year survival pattern (Foreshadowing). Planted: Ch. 7. Window: Open — will resolve when Caradhen is forced to commit. Status: Pending.
  Payoff 004: Aldric's unspoken liability (Consequence bomb). Planted: Ch. 13. Detonation trigger: When Aldric's contingency is activated and the unnamed third party moves against him. Narrative phase anchor: Final act. Priority tier: Unclassified. Status: Pending.

**Module 4.2 excerpt (consequence bombs — convergence mode):**
  Bomb 4.2-001: Vara's assessment brief reaching Aldric. Priority: Essential. Status: Armed.
    Detonation trigger: When the brief reaches Aldric directly (same as Payoff 002 above).
    Module 2.4 registration: Yes (Payoff 002).
  Bomb 4.2-002: Aldric's unspoken liability. Priority: Unclassified. Status: Armed.
    Detonation trigger: When Aldric's contingency activates and the third party moves against him.
    Module 2.4 registration: Yes (Payoff 004).
  Bomb 4.2-003: Caradhen's exposure — what Sethric knows. Priority: Unclassified. Status: Armed.
    Planted: Ch. 9. Detonation trigger: When Caradhen is forced to publicly commit to a faction.
    Module 2.4 registration: No.

### Output Artifacts

```json
{
  "thread_load_summary": {
    "total": 5,
    "active": 3,
    "dormant": 1,
    "resolved": 1,
    "abandoned": 0,
    "overdue": 0,
    "approaching_window": 2
  },
  "active_thread_status": [
    {
      "thread_id": "thread_004",
      "thread_name": "The Alliance Approach",
      "characters_involved": ["char_vara", "char_caradhen", "char_aldric"],
      "current_status_within_thread": "Vara's assessment building (Ch. 10–14). Aldric's contingency active (Ch. 13).",
      "expected_convergence_window": "Ch. 18–22",
      "track_status": "On track",
      "dependencies": [],
      "note": "At current development pace, resolution is plausible within window."
    },
    {
      "thread_id": "thread_012",
      "thread_name": "Aldric's Contingency",
      "characters_involved": ["char_aldric", "char_caradhen"],
      "current_status_within_thread": "Opened in Ch. 13 but has no established convergence window.",
      "expected_convergence_window": "None",
      "track_status": "At risk",
      "dependencies": ["thread_004"],
      "note": "Recommend establishing convergence window as Ch. 18–22 (same as T004) and marking as a dependency."
    },
    {
      "thread_id": "thread_001",
      "thread_name": "The Regency's Legacy",
      "characters_involved": ["char_aldric", "char_dowager"],
      "current_status_within_thread": "Currently operating as background pressure.",
      "expected_convergence_window": "Ch. 25–30",
      "track_status": "On track",
      "dependencies": [],
      "note": "Long horizon. No action needed yet."
    }
  ],
  "overdue_flags": [],
  "pending_payoffs_status": [
    {
      "payoff_id": "payoff_001",
      "description": "The Dowager's letter",
      "type": "Chekhov's gun",
      "planted_chapter": 4,
      "expected_window_or_trigger": "Ch. 15–20",
      "resolution_status": "Pending",
      "priority_tier": "N/A",
      "note": "APPROACHING WINDOW. If not integrated with T004 or T012, it will need a chapter of its own — which may interrupt the braid at a structurally sensitive moment."
    },
    {
      "payoff_id": "payoff_002",
      "description": "Vara's assessment brief",
      "type": "Consequence bomb",
      "planted_chapter": 10,
      "expected_window_or_trigger": "When the assessment brief reaches Aldric directly",
      "resolution_status": "Pending",
      "priority_tier": "Essential",
      "note": "Detonation path visible — aligns with T004 convergence window. No action needed."
    },
    {
      "payoff_id": "payoff_003",
      "description": "Caradhen's thirty-year survival pattern",
      "type": "Foreshadowing",
      "planted_chapter": 7,
      "expected_window_or_trigger": "When Caradhen is forced to commit",
      "resolution_status": "Pending",
      "priority_tier": "N/A",
      "note": "Main agent should confirm that the story's trajectory will eventually create that forcing condition."
    },
    {
      "payoff_id": "payoff_004",
      "description": "Aldric's unspoken liability",
      "type": "Consequence bomb",
      "planted_chapter": 13,
      "expected_window_or_trigger": "When Aldric's contingency is activated and the third party moves against him",
      "resolution_status": "Pending",
      "priority_tier": "Unclassified",
      "note": "See bomb sweep for reclassification recommendation."
    }
  ],
  "convergence_bomb_sweep": {
    "performed": true,
    "essential_bombs": [
      {
        "chain_id": "cc_vara_assessment",
        "description": "Vara's assessment brief reaching Aldric",
        "detonation_trigger": "When the brief reaches Aldric directly",
        "narrative_phase_anchor": "convergence",
        "module_2_4_registered": true,
        "detonation_path_assessment": "On track — path visible",
        "note": "Aligns directly with T004's convergence window."
      }
    ],
    "enriching_bombs": [],
    "unclassified_bombs": [
      {
        "chain_id": "cc_aldric_liability",
        "description": "Aldric's unspoken liability",
        "reclassification_recommendation": "Enriching",
        "reasoning": "Adds earned weight to his arc's resolution, but the story's core conflict closes without it. Recommend reclassifying to Enriching; monitor for opportunity in T012's resolution window."
      },
      {
        "chain_id": "cc_caradhen_exposure",
        "description": "Caradhen's exposure — what Sethric knows",
        "reclassification_recommendation": "Essential",
        "reasoning": "Sethric's knowledge is the only thing that can force Caradhen's commitment publicly. Without it detonating, Caradhen's arc has no externally forced resolution."
      }
    ],
    "registration_gaps": [
      {
        "chain_id": "cc_caradhen_exposure",
        "issue": "Essential bomb not registered in Payoff nodes (Module 2.4)"
      }
    ]
  },
  "convergence_opportunities": [
    {
      "threads_involved": ["thread_004", "thread_012"],
      "narrative_meaning": "When Vara's assessment reaches Aldric, his contingency activates in response — this is the braid's first major three-POV convergence point.",
      "type": "Planned",
      "imminence": "Developing",
      "note": "Ensure Aldric receives a POV chapter before the assessment arrives."
    },
    {
      "threads_involved": ["thread_007", "thread_004"],
      "narrative_meaning": "When Caradhen is forced toward a public commitment (T004's convergence), Sethric becomes the detonation mechanism for both T007 and Bomb 4.2-003 simultaneously.",
      "type": "Discovered",
      "imminence": "Developing",
      "note": "Add Bomb 4.2-003 as a dependency of T007; link T007 to T004 in the registry; establish a convergence window for T007 aligned with T004's Ch. 18–22 window."
    }
  ],
  "thread_health_assessment": {
    "verdict": "Healthy",
    "detail": "Healthy with three flags requiring attention."
  },
  "no_thread_abandonment_check": {
    "pass": true,
    "abandoned_without_rationale": []
  },
  "priority_summary": {
    "high": [
      "Bomb 4.2-003 — Essential, no Module 2.4 registration, reclassification required immediately.",
      "P001 — Chekhov's gun approaching window, not integrated with active threads."
    ],
    "medium": [
      "T012 — no convergence window established.",
      "T007 — dormant, activation moment approaching organically without a tracking window."
    ],
    "low": [
      "Bomb 4.2-002 — Enriching, no detonation path urgency; monitor at next convergence check."
    ]
  },
  "kg_context_used": {
    "plot_thread_nodes_found": 5,
    "payoff_nodes_found": 4,
    "cascade_chain_nodes_found": 3
  }
}
```