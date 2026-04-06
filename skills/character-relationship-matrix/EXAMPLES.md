# Character Relationship Matrix Examples

## Example: Full Directional Relationship Records

### Output Artifacts

```json
{
  "new_relationship_edges": [
    {
      "logical_id": "rel_char_caradhen_char_sethric",
      "edge_type": "RELATIONSHIP",
      "from_node": "char_caradhen",
      "to_node": "char_sethric",
      "chapter": 1,
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
      "chapter": 1,
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
  "updated_relationship_edges": [],
  "flags": []
}
```