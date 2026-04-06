# Character Integration with Plot Examples

## Example: Full Integration Output

### Input Context

```json
{
  "character_ids": ["char_caradhen", "char_vara", "char_sethric"],
  "chapter_context": 5
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**Characters for integration:** Caradhen (warlord), Vara (protagonist's envoy), Sethric (Caradhen's second-in-command).

**Module 1.1 excerpts:** [full psychological records for all three]
**Module 1.2 initial entries:** [from Character Creation for each]
**Module 1.3 initial entries:** [Caradhen knows Sethric since childhood; Vara has no prior relationship with either]
**Module 3.1 excerpt:** [three-faction political map; Thornback passes as strategic neutral zone; protagonist's faction has recently seized lowland cities]

### Output Artifacts

```json
{
  "knowledge_matrix_expansions": {
    "new_knowledge_items": [
      {
        "logical_id": "ki_sethric_father_death_causal",
        "node_type": "KnowledgeItem",
        "chapter": 5,
        "properties": {
          "description": "Sethric's father died in the plains battle not by coincidence, but due to Caradhen's specific tactical decision."
        }
      },
      {
        "logical_id": "ki_vara_assessment_brief",
        "node_type": "KnowledgeItem",
        "chapter": 5,
        "properties": {
          "description": "Vara is not primarily a diplomat — she is carrying an assessment brief to evaluate whether Caradhen is an asset or an obstacle to be removed."
        }
      }
    ],
    "new_knows_edges": [
      {
        "logical_id": "knows_char_caradhen_ki_sethric_father_death_causal",
        "edge_type": "KNOWS",
        "from_node": "char_caradhen",
        "to_node": "ki_sethric_father_death_causal",
        "chapter": 5,
        "properties": {
          "status": "KNOWS",
          "acquired_at_chapter": 0,
          "source": "Lived experience / his own decision",
          "dramatic_irony_flag": false
        }
      },
      {
        "logical_id": "knows_char_sethric_ki_sethric_father_death_causal",
        "edge_type": "KNOWS",
        "from_node": "char_sethric",
        "to_node": "ki_sethric_father_death_causal",
        "chapter": 5,
        "properties": {
          "status": "KNOWS",
          "acquired_at_chapter": 0,
          "source": "Observation during the battle",
          "dramatic_irony_flag": false
        }
      },
      {
        "logical_id": "knows_char_caradhen_ki_vara_assessment_brief",
        "edge_type": "KNOWS",
        "from_node": "char_caradhen",
        "to_node": "ki_vara_assessment_brief",
        "chapter": 5,
        "properties": {
          "status": "DOES NOT KNOW",
          "acquired_at_chapter": 0,
          "source": "Information asymmetry",
          "dramatic_irony_flag": true
        }
      },
      {
        "logical_id": "knows_char_vara_ki_vara_assessment_brief",
        "edge_type": "KNOWS",
        "from_node": "char_vara",
        "to_node": "ki_vara_assessment_brief",
        "chapter": 5,
        "properties": {
          "status": "KNOWS",
          "acquired_at_chapter": 0,
          "source": "Her own mission orders",
          "dramatic_irony_flag": false
        }
      }
    ]
  },
  "relationship_records": {
    "new_relationship_edges": [
      {
        "logical_id": "rel_char_caradhen_char_sethric",
        "edge_type": "RELATIONSHIP",
        "from_node": "char_caradhen",
        "to_node": "char_sethric",
        "chapter": 5,
        "properties": {
          "emotional_valence": "Complex trust mixed with unacknowledged guilt.",
          "power_dynamic": "Caradhen holds formal power; Sethric holds informal moral authority that Caradhen would never acknowledge.",
          "history": "Grew up together; Sethric's father served Caradhen's father. The plains battle is the load-bearing moment — Sethric was there, survived, and has never mentioned it.",
          "secrets_kept": ["Caradhen conceals that he thinks about the plains battle often."],
          "trajectory": "Stable surface; pressure fault underneath. A moment of direct challenge to Caradhen's authority may surface the unspoken structure.",
          "convergence_potential": "Already in direct contact.",
          "most_recent_interaction": null
        }
      },
      {
        "logical_id": "rel_char_sethric_char_caradhen",
        "edge_type": "RELATIONSHIP",
        "from_node": "char_sethric",
        "to_node": "char_caradhen",
        "chapter": 5,
        "properties": {
          "emotional_valence": "Loyalty that coexists with a grief that has calcified into a judgment he has never delivered.",
          "power_dynamic": "Sethric holds no formal power; holds the specific power of a witness — he could break Caradhen's self-narrative at any moment by speaking.",
          "history": "Grew up together; the plains battle.",
          "secrets_kept": ["Sethric conceals that he has never stopped thinking about the plains battle."],
          "trajectory": "Stable surface; pressure fault underneath.",
          "convergence_potential": "Already in direct contact.",
          "most_recent_interaction": null
        }
      }
    ],
    "updated_relationship_edges": []
  },
  "consequence_ledger_seeds": {
    "cascade_chain_nodes": [
      {
        "logical_id": "cc_char_caradhen_desire_loop",
        "node_type": "CascadeChain",
        "chapter": 5,
        "properties": {
          "sequence": [
            "Preserve the passes and the people intact; avoid commitment that costs what he protects.",
            "Will offer apparent cooperation without actual commitment; will read every proposal for its commitment cost before anything else.",
            "The protagonist's envoy (Vara) will read his non-commitment as stalling or as receptivity, depending on how sophisticated her brief is.",
            "If Caradhen makes a promise to Vara that he does not intend to keep, the discovery that Caradhen was managing them rather than negotiating with them may produce a response that forces the very confrontation he has spent thirty years avoiding."
          ],
          "current_position": "Preserve the passes and the people intact; avoid commitment that costs what he protects.",
          "remaining_links": [
            "Will offer apparent cooperation without actual commitment; will read every proposal for its commitment cost before anything else.",
            "The protagonist's envoy (Vara) will read his non-commitment as stalling or as receptivity, depending on how sophisticated her brief is.",
            "If Caradhen makes a promise to Vara that he does not intend to keep, the discovery that Caradhen was managing them rather than negotiating with them may produce a response that forces the very confrontation he has spent thirty years avoiding."
          ]
        }
      }
    ]
  },
  "integration_flags": []
}
```