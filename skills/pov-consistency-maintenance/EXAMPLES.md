# POV Consistency Maintenance Examples

## Example: Consistency Audit

### Input Context

```json
{
  "draft_scene": "...Caradhen watched Vara pour the wine. He knew she was nervous — her hands moved too carefully, the way hands move when their owner is trying not to show that they are shaking. Vara thought the meeting was going well. She had been surprised when he agreed to the follow-up. He watched her and thought about his sons, about which of them would be standing in this room someday in his place. He felt his face harden. Neither of them understood what Aldric's contingency would mean for this conversation...",
  "pov_character_id": "char_caradhen",
  "chapter_context": 14
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Module 1.2 (Caradhen):**
  KNOWS: Vara has made a proposal; she is an envoy of the protagonist.
  SUSPECTS: She has more authority than her opening position suggests.
  DOES NOT KNOW: Vara's internal assessment of how the meeting is going.
  DOES NOT KNOW: Aldric's contingency has been activated.

**Voice profile (Caradhen):**
  Observational focus: power geometry, exits, what people do with their hands.
  Emotional processing: encodes emotion in what he notices; does not name it.
  Sentence structure: long and deliberate in control; compresses under pressure.

### Output Artifacts

```json
{
  "audit_header": {
    "pov_character_id": "char_caradhen",
    "scene_summary": "Follow-up meeting with Vara, solar.",
    "overall_status": "VIOLATIONS FOUND",
    "violation_count": 4,
    "violation_types_found": [
      "Knowledge Violation",
      "Head-Hopping",
      "Omniscient Intrusion",
      "External Self-Description"
    ]
  },
  "violation_log": [
    {
      "violation_type": "Knowledge Violation",
      "offending_text": "Neither of them understood what Aldric's contingency would mean for this conversation...",
      "description": "This sentence states that Caradhen does not understand what Aldric's contingency means — but Module 1.2 records Caradhen as DOES NOT KNOW that Aldric's contingency has been activated at all. He cannot not-understand the implications of something he has no knowledge of.",
      "correction_note": "Remove this sentence entirely."
    },
    {
      "violation_type": "Head-Hopping",
      "offending_text": "Vara thought the meeting was going well. She had been surprised when he agreed to the follow-up.",
      "description": "This directly states Vara's interior thought and emotional state (surprise) — Caradhen cannot access the content of Vara's thinking.",
      "correction_note": "Replace with Caradhen's observable evidence and inference (e.g., how she sits, the pace of her speech)."
    },
    {
      "violation_type": "Omniscient Intrusion",
      "offending_text": "Neither of them understood what Aldric's contingency would mean for this conversation...",
      "description": "In addition to the knowledge violation, this is an omniscient intrusion. It requires a perspective outside both characters to state what 'neither of them' understands about a future consequence.",
      "correction_note": "Remove this sentence entirely."
    },
    {
      "violation_type": "External Self-Description",
      "offending_text": "He felt his face harden.",
      "description": "Caradhen cannot observe his own face. While 'felt' attempts to internalize it, 'harden' is an external visual description of an expression.",
      "correction_note": "Replace with internal physical sensation (e.g., tension in the jaw, setting his teeth)."
    }
  ],
  "summary_pattern_note": "There is a tendency in this draft to slip into omniscient/authorial voice to explain the stakes or other characters' states, rather than staying strictly within Caradhen's limited observational lens.",
  "kg_context_used": {
    "character_node_found": true,
    "voice_profile_found": true,
    "knows_edges_found": 4
  }
}
```