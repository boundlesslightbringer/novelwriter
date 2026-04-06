# Character Creation Examples

## Example: Full Character Construction

### Input Context

```json
{
  "character_concept": {
    "assigned_narrative_role": "Regional warlord — obstacle and potential reluctant ally.",
    "generation_method": "Role-First",
    "core_contradiction": "Has kept his people alive for thirty years by never fighting a battle he could avoid / believes a man who will not fight for what is sacred deserves nothing he has.",
    "sketch": "Caradhen rules the Thornback passes not through martial brilliance, but through a meticulous economy of violence...",
    "open_questions": [
      "What event taught him that commitment leads to catastrophe?",
      "What does he believe about himself that is completely untrue?",
      "Is there something for which he would break his own rule?",
      "How does he treat people who show the open courage he denies himself?",
      "What will the protagonist offer that breaks him open?"
    ]
  },
  "chapter_context": 1
}
```

### Output Artifacts

```json
{
  "character_node": {
    "logical_id": "char_caradhen_thornback",
    "node_type": "Character",
    "chapter": 1,
    "properties": {
      "full_name": "Caradhen of the Thornback",
      "aliases": ["The Fox of the Passes"],
      "age": 52,
      "gender": "Male",
      "physical_description": "Lean, weathered, with eyes that never stop moving. People notice his unassuming posture; they miss the tension in his hands.",
      "faction": "Thornback Clans",
      "rank": "Clan-Lord",
      "occupation": "Warlord",
      "public_vs_private_reputation": "Reputation: untrustworthy opportunist. Reality: tactical survivor who has never broken a promise he actually made.",
      "location": "The Thornback Passes",
      "surface_beliefs": ["Survival is the only victory.", "Alliances are just delayed betrayals."],
      "core_wound": "At age twenty-two, led his father's warband into an alliance battle on the western plains. The alliance collapsed. Half his warband died in an afternoon. He concluded: other people's causes are pits without bottoms.",
      "core_desire": "To hand something intact to the next generation — passes, people, customs — without having lost them in someone else's war.",
      "core_fear": "That the thing he is protecting has already been hollowed out — that the people he is preserving no longer remember what they are for.",
      "self_deception": "Believes he is protecting his people. Is also protecting himself from the grief of the plains, which he has never allowed to fully arrive.",
      "values_under_pressure": [
        "Will sacrifice honor for survival, but will not sacrifice his people for honor."
      ],
      "contradictions": [
        "Despises idealism, yet secretly respects those who hold to it even when it costs them."
      ],
      "response_patterns": {
        "betrayal": "Goes quiet. Stops trusting for reasons. Never explicitly confronts; simply removes access.",
        "loss": "Absorbs. Continues. Privately catastrophic; publicly unchanged. The grief has nowhere to go.",
        "sudden_power": "Suspicious. Looks immediately for the hidden cost or the trap.",
        "helplessness": "Calculates the exact minimum required to survive until the situation changes.",
        "unwanted_intimacy": "Deflects with political pragmatism or cold logic.",
        "being_correctly_seen": "Hostile. Withdraws immediately.",
        "unexpected_kindness_from_enemy": "Assumes it is a tactic and plans a counter-move."
      },
      "arc_type": "Revelation",
      "arc_stage": "Established. The audience and the protagonist will read him as political; the arc is the progressive stripping of that reading.",
      "pov_eligible": true,
      "pov_chapter_count": 0,
      "last_pov_chapter": null,
      "injuries_physical_state": [],
      "emotional_state": "Guarded, weary, perpetually calculating."
    }
  },
  "knowledge_matrix_edges": [
    {
      "logical_id": "knows_char_caradhen_thornback_ki_plains_massacre",
      "edge_type": "KNOWS",
      "from_node": "char_caradhen_thornback",
      "to_node": "ki_plains_massacre",
      "chapter": 1,
      "properties": {
        "status": "KNOWS",
        "acquired_at_chapter": 0,
        "source": "Lived experience",
        "dramatic_irony_flag": false
      }
    }
  ],
  "knowledge_items": [
    {
      "logical_id": "ki_plains_massacre",
      "node_type": "KnowledgeItem",
      "chapter": 1,
      "properties": {
        "description": "The alliance on the western plains collapsed thirty years ago, leading to the slaughter of half the Thornback warband."
      }
    }
  ],
  "relationship_edges": [
    {
      "logical_id": "rel_char_caradhen_thornback_char_vara",
      "edge_type": "RELATIONSHIP",
      "from_node": "char_caradhen_thornback",
      "to_node": "char_vara",
      "chapter": 1,
      "properties": {
        "emotional_valence": "distrust",
        "power_dynamic": "Caradhen holds the terrain; Vara holds the political legitimacy.",
        "history": "None prior to her arrival as envoy.",
        "secrets_kept": ["The true extent of his remaining forces.", "His underlying grief."],
        "trajectory": "Volatile",
        "convergence_potential": "Direct contact imminent.",
        "most_recent_interaction": null
      }
    }
  ],
  "culture_edge": {
    "logical_id": "culture_char_caradhen_thornback",
    "edge_type": "BELONGS_TO_CULTURE",
    "from_node": "char_caradhen_thornback",
    "to_node": "culture_thornback_clans",
    "chapter": 1,
    "properties": {
      "role": "Clan-Lord and protector."
    }
  },
  "arc_type_note": "Revelation fits best because his fundamental nature is already set by his past; the story's pressure will force him to reveal what he has hidden behind his pragmatism.",
  "provisional_expansion_flag": false,
  "provisional_expansion_notes": ""
}
```