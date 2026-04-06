# Balancing Realism and Fantasy Examples

## Example: Flagged Scene Audit

### Input Context

```json
{
  "chapter_or_scene_draft": "The lord slammed his fist on the table. 'I will march ten thousand men on the capital tomorrow if the king does not yield!' he roared. Outside, his three remaining guards shivered in the rain. Later, the court mage waved his hand, and the entire castle was instantly repaired from the siege damage, without breaking a sweat. The king, seeing this, laughed heartily, completely forgetting the massacre of his family the day before.",
  "chapter_context": 12,
  "audit_scope": "flagged_scene",
  "scene_description": "The confrontation in the ruined hall.",
  "tone_reference": "low fantasy, high political realism, earned darkness"
}
```

### Output Artifacts

```json
{
  "audit_header": {
    "chapter_context": 12,
    "audit_scope": "flagged_scene",
    "pov_character_audited": null
  },
  "dimension_reports": {
    "political_realism": {
      "status": "Flag",
      "flagged_passages": [
        {
          "text_reference": "'I will march ten thousand men on the capital tomorrow if the king does not yield!' he roared. Outside, his three remaining guards shivered in the rain.",
          "issue_description": "The lord threatens a massive army while only having three guards. This violates political realism as his threat carries no weight and contradicts his established resources.",
          "recommended_adjustment": "Adjust the lord's threat to match his actual desperate situation, perhaps threatening to reveal a secret or leverage a minor alliance instead of an impossible army."
        }
      ]
    },
    "magic_prevalence_and_consistency": {
      "status": "Concern",
      "magic_acts_in_chapter": 1,
      "current_prevalence_level": "Rare",
      "flagged_passages": [
        {
          "text_reference": "the court mage waved his hand, and the entire castle was instantly repaired from the siege damage, without breaking a sweat.",
          "issue_description": "The magic act exceeds established limits (instant massive repair) and evades the confirmed costs (no physical toll or sweat).",
          "recommended_adjustment": "Scale back the magic to a minor, costly act, or remove it entirely if the repair is not structurally necessary."
        }
      ]
    },
    "violence_framing": {
      "status": "Pass",
      "flagged_passages": []
    },
    "dark_content_justification": {
      "status": "Pass",
      "flagged_passages": []
    },
    "tonal_consistency": {
      "status": "Flag",
      "flagged_passages": [
        {
          "text_reference": "The king, seeing this, laughed heartily, completely forgetting the massacre of his family the day before.",
          "issue_description": "The king's hearty laughter immediately following the massacre of his family ruptures the established 'earned darkness' tone and violates basic psychological realism.",
          "recommended_adjustment": "Ensure the king's reaction reflects the weight of the recent massacre, maintaining the somber tone."
        }
      ]
    }
  },
  "priority_summary": {
    "high": [
      "Magic limit violation: instant castle repair with no cost.",
      "Tonal rupture: king laughing heartily after family massacre."
    ],
    "medium": [
      "Political realism: lord threatening an army he doesn't have."
    ],
    "low": []
  },
  "magic_system_updates_recommended": [
    {
      "update_type": "add_unexplained_phenomenon",
      "description": "Instant architectural restoration magic.",
      "justification": "The court mage repaired the castle instantly. If this is kept, it represents a massive new capability that needs explanation and integration into the system limits."
    }
  ],
  "kg_context_used": {
    "magic_system_found": true,
    "faction_nodes_found": 2,
    "culture_nodes_found": 1,
    "pov_character_found": false
  }
}
```