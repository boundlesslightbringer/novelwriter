# Layering History and Legend Examples

## Example: Integrating History into a Scene

### Input Context

```json
{
  "draft_scene": "Caradhen stood by the window, looking out over the valley. Sethric entered quietly. 'The envoy is waiting,' he said. Caradhen nodded, his eyes fixed on the distant ridge where the old stones caught the morning light.",
  "pov_character_id": "char_caradhen",
  "chapter_context": 7,
  "scene_location_id": "loc_thornback_keep"
}
```

### Output Artifacts

```json
{
  "revised_draft": "Caradhen stood by the window, looking out over the valley. His eyes fixed on the distant ridge where the old stones of the First Alliance wall caught the morning light—a monument to the last time the clans had trusted the lowlanders, and the slaughter that followed. Sethric entered quietly. 'The envoy is waiting,' he said. Caradhen nodded, still looking at the ruins.",
  "integration_log": [
    {
      "element_type": "Physical remnant",
      "source_node_id": "event_first_alliance_collapse",
      "where_integrated": "Added to his observation of the distant ridge, connecting the physical ruins to the historical betrayal.",
      "epistemic_basis": "KNOWS",
      "forced_plant_removed": false
    }
  ],
  "referenced_events_to_update": [
    {
      "event_logical_id": "event_first_alliance_collapse",
      "chapter_to_add": 7
    }
  ],
  "kg_context_used": {
    "historical_events_found": 1,
    "culture_nodes_found": 1,
    "knows_edges_found": 3,
    "location_node_found": true
  }
}
```