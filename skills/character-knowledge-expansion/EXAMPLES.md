# Character Knowledge Expansion Examples

## Example: Knowledge Expansion Output

### Output Artifacts

```json
{
  "new_knowledge_items": [
    {
      "logical_id": "ki_vara_assessment_brief",
      "node_type": "KnowledgeItem",
      "chapter": 1,
      "properties": {
        "description": "Vara is carrying an assessment brief to evaluate whether Caradhen is an asset or an obstacle to be removed."
      }
    },
    {
      "logical_id": "ki_sethric_forgiveness",
      "node_type": "KnowledgeItem",
      "chapter": 1,
      "properties": {
        "description": "Sethric has not forgiven Caradhen for the plains battle disaster."
      }
    }
  ],
  "new_knows_edges": [
    {
      "logical_id": "knows_char_vara_ki_vara_assessment_brief",
      "edge_type": "KNOWS",
      "from_node": "char_vara",
      "to_node": "ki_vara_assessment_brief",
      "chapter": 1,
      "properties": {
        "status": "KNOWS",
        "acquired_at_chapter": 0,
        "source": "Her own mission orders",
        "dramatic_irony_flag": false
      }
    },
    {
      "logical_id": "knows_char_caradhen_ki_vara_assessment_brief",
      "edge_type": "KNOWS",
      "from_node": "char_caradhen",
      "to_node": "ki_vara_assessment_brief",
      "chapter": 1,
      "properties": {
        "status": "DOES NOT KNOW",
        "acquired_at_chapter": 0,
        "source": "Information asymmetry",
        "dramatic_irony_flag": true
      }
    },
    {
      "logical_id": "knows_char_caradhen_ki_sethric_forgiveness",
      "edge_type": "KNOWS",
      "from_node": "char_caradhen",
      "to_node": "ki_sethric_forgiveness",
      "chapter": 1,
      "properties": {
        "status": "BELIEVES",
        "acquired_at_chapter": 0,
        "source": "Self-deception to avoid grief",
        "dramatic_irony_flag": true
      }
    },
    {
      "logical_id": "knows_char_sethric_ki_sethric_forgiveness",
      "edge_type": "KNOWS",
      "from_node": "char_sethric",
      "to_node": "ki_sethric_forgiveness",
      "chapter": 1,
      "properties": {
        "status": "KNOWS",
        "acquired_at_chapter": 0,
        "source": "His own internal emotional state",
        "dramatic_irony_flag": false
      }
    }
  ],
  "flags": []
}
```