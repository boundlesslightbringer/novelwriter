# Consequence Cascade Implementation Examples

## Example: Creating a New Cascade Chain

### Output Artifacts

```json
{
  "triggering_event_summary": "Caradhen definitively refuses the alliance proposal and expels Vara from the Thornback passes. (Chapter 12)",
  "cascade_chain": {
    "action": "create_new",
    "existing_chain_id": null,
    "node": {
      "logical_id": "cc_caradhen_refuses_alliance",
      "node_type": "CascadeChain",
      "chapter": 12,
      "properties": {
        "sequence": [
          "Caradhen refuses the alliance and expels Vara.",
          "Vara must return to Aldric with a failure, forcing her to spin the narrative to survive.",
          "Aldric implements his contingency plan to seize the passes by force.",
          "Sethric is forced to choose between his loyalty to Caradhen and the survival of the clan against impossible odds."
        ],
        "current_position": "Caradhen refuses the alliance and expels Vara.",
        "remaining_links": [
          "Vara must return to Aldric with a failure, forcing her to spin the narrative to survive.",
          "Aldric implements his contingency plan to seize the passes by force.",
          "Sethric is forced to choose between his loyalty to Caradhen and the survival of the clan against impossible odds."
        ]
      }
    },
    "update_existing": null
  },
  "consequence_chain_entry": {
    "node_type": "CascadeChain",
    "event_consequences": {
      "immediate": [
        {
          "affected_entity": "char_vara",
          "description": "Vara is physically escorted out of the territory, losing all access to her diplomatic network in the passes.",
          "chapter_reference": 12
        }
      ],
      "short_term": [
        {
          "affected_entity": "char_aldric",
          "description": "Aldric will receive word of the failure and begin mobilizing the border garrisons.",
          "projected_chapters": "13-15"
        }
      ],
      "long_term_pending": [
        {
          "affected_entity": "char_sethric",
          "description": "Sethric will face a crisis of loyalty when the lowland army arrives.",
          "bomb_id": "bomb_sethric_loyalty_crisis"
        }
      ]
    }
  },
  "consequence_bombs": [
    {
      "logical_id": "bomb_sethric_loyalty_crisis",
      "node_type": "Payoff",
      "chapter": 12,
      "properties": {
        "type": "Consequence bomb",
        "description": "Sethric must decide whether to support Caradhen's doomed defense or betray him to save the clan.",
        "planted_in_chapter": 12,
        "detonation_trigger": "When Aldric's army breaches the first gate of the passes and defeat becomes mathematically certain.",
        "narrative_phase_anchor": "convergence",
        "resolution_status": "Pending",
        "priority_tier": "Essential",
        "dual_register": true
      }
    }
  ],
  "character_state_updates": [
    {
      "logical_id": "char_vara",
      "updated_properties": {
        "emotional_state": "Humiliated, desperate, calculating her survival strategy.",
        "active_fears": ["Being executed by Aldric for failure"],
        "injuries_physical_state": []
      },
      "chapter": 12
    }
  ],
  "relationship_updates": [
    {
      "logical_id": "rel_char_vara_char_caradhen",
      "updated_properties": {
        "emotional_valence": "Cold fury and professional respect.",
        "trajectory": "Volatile",
        "most_recent_interaction": "Ch 12: Caradhen formally expelled her from the hall."
      },
      "chapter": 12
    }
  ],
  "knowledge_matrix_updates": [
    {
      "character_id": "char_vara",
      "new_knows_edges": [
        {
          "logical_id": "knows_char_vara_ki_caradhen_inflexible",
          "edge_type": "KNOWS",
          "from_node": "char_vara",
          "to_node": "ki_caradhen_inflexible",
          "chapter": 12,
          "properties": {
            "status": "KNOWS",
            "acquired_at_chapter": 12,
            "source": "Direct experience of his refusal",
            "dramatic_irony_flag": false
          }
        }
      ],
      "new_knowledge_items": [
        {
          "logical_id": "ki_caradhen_inflexible",
          "node_type": "KnowledgeItem",
          "chapter": 12,
          "properties": {
            "description": "Caradhen will not compromise the neutrality of the passes under any diplomatic pressure."
          }
        }
      ]
    }
  ],
  "kg_context_used": {
    "character_nodes_found": 3,
    "relationship_edges_found": 2,
    "existing_cascade_chains_found": 1,
    "chain_action": "create_new"
  }
}
```