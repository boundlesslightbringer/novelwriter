# Worldbuilding Examples

The following example demonstrates the expected output for the `worldbuilding` skill.

## Example — Minimal Worldbuilding Output

**Output shape (JSON `artifacts`):**
```json
{
  "political_power_map": [
    {
      "node_type": "Faction",
      "properties": {
        "name": "The Iron Syndicate",
        "core_values": ["Industrial efficiency", "Meritocratic advancement", "Resource monopoly"],
        "military_assets": "A highly disciplined, mechanized infantry equipped with steam-powered artillery.",
        "economic_assets": "Total control over the continent's largest coal and iron mines; a monopoly on rail transport."
      },
      "iceberg_notes": {
        "current_controller": "High Director Vane",
        "allegiances": "Uneasy trade agreement with the River Lords; open hostility with the Highland Tribes.",
        "active_enmities": "Currently in a cold war with the Highland Tribes over border mining rights.",
        "internal_tensions": "The merchant class is growing wealthy and demands political representation, threatening the military-first hierarchy.",
        "what_this_power_does_not_know": "The deep-mine operations have recently breached an ancient, dormant magical fault line."
      }
    }
  ],
  "geography": [
    {
      "node_type": "Location",
      "properties": {
        "name": "The Ash Wastes (Colloquially: The Grey)",
        "description": "A vast, arid expanse of volcanic ash and jagged basalt formations, constantly swept by dry, biting winds.",
        "climate": "Arid and cold, with extreme temperature drops at night.",
        "seasonal_weather_state": "Currently experiencing the 'Long Dust', a season of continuous low-visibility ash storms."
      },
      "iceberg_notes": {
        "adjacent_locations": "Borders the Iron Syndicate's industrial heartland to the south and the Highland Peaks to the north. Travel across takes three weeks on foot.",
        "what_the_geography_makes_difficult": "Agriculture is impossible. Wheeled transport sinks in the deep ash, forcing reliance on specialized skiffs or beasts of burden.",
        "cultural_meaning": "Viewed by outsiders as a wasteland, but revered by the nomadic tribes as the 'Bones of the Earth', a place of spiritual testing."
      }
    },
    {
      "node_type": "Location",
      "properties": {
        "name": "Syndicate Prime",
        "description": "A sprawling, smog-choked metropolis of steel towers and perpetual industry.",
        "climate": "Temperate, though heavily polluted.",
        "seasonal_weather_state": "Smog inversion layer currently trapping heat and exhaust."
      },
      "iceberg_notes": {
        "adjacent_locations": "Sits at the mouth of the Black River, connecting to the Ash Wastes via rail.",
        "what_the_geography_makes_difficult": "The city has outgrown its natural water supply and relies entirely on vulnerable aqueducts.",
        "cultural_meaning": "The symbol of human triumph over nature for its citizens; a monument to hubris for its enemies."
      }
    }
  ],
  "cultures_customs_religion": [
    {
      "node_type": "Culture",
      "properties": {
        "name": "The Ash Nomads",
        "core_values": ["Endurance", "Communal survival", "Oral tradition"],
        "core_fears": ["Stagnation", "Being forgotten by the ancestors", "The deep earth opening"],
        "key_customs": ["Leaving bone-carved markers at temporary camps", "Silent mourning rituals"],
        "class_structure": "Egalitarian within tribes, led by the eldest memory-keeper rather than the strongest warrior.",
        "gender_dynamics": "Strictly functional; roles are assigned by physical capability and tribal need rather than gender.",
        "religious_beliefs": "Animistic reverence for the 'Sleeping Gods' beneath the ash, who must not be disturbed by deep mining.",
        "political_power": "Minimal institutional power, but absolute control over safe passage through the Wastes.",
        "languages_dialects": ["Ash-cant (a sign-and-click language for use in storms)", "Trade Common"]
      },
      "iceberg_notes": {
        "internal_contradictions": "They believe they are the pure, original inhabitants of the land, but their oldest oral traditions contain descriptions of arriving from the stars."
      }
    }
  ],
  "history_and_legends": [
    {
      "node_type": "Event",
      "properties": {
        "name": "The Sundering",
        "summary": "A cataclysmic event that created the Ash Wastes and destroyed the previous dominant civilization.",
        "is_historical": true,
        "true_account": "An industrial accident involving the over-extraction of magical ambient energy, which caused a localized reality collapse.",
        "believed_account": "A divine punishment brought down upon the ancients for their arrogance.",
        "factional_interpretations": {
          "The Iron Syndicate": "A natural volcanic event that cleared the way for superior civilization.",
          "The Ash Nomads": "The day the Sleeping Gods turned over in their slumber due to the noise of cities."
        },
        "physical_remnants": ["Glassed craters in the deep Wastes", "Unexplained zones of zero gravity"],
        "story_significance": "The Iron Syndicate is currently repeating the exact mining practices that caused the Sundering.",
        "referenced_in_chapters": []
      }
    }
  ],
  "magic_system": {
    "node_type": "MagicSystem",
    "properties": {
      "prevalence": "Rare",
      "confirmed_capabilities": ["Kinetic energy transfer", "Temporary localized gravity negation", "Heat absorption"],
      "confirmed_limits": ["Cannot create energy from nothing; must draw from a physical source (usually the user's own body heat or surrounding fires).", "Requires physical contact or line of sight within ten meters."],
      "confirmed_costs": ["Severe physical exhaustion", "Hypothermia (if drawing from own body heat)", "Long-term cellular degradation (the 'Ash-sickness')"],
      "unexplained_phenomena": ["Spontaneous ignition of coal seams without a practitioner present", "Whispers heard by practitioners when drawing too much power"],
      "recent_magical_events": []
    },
    "iceberg_notes": {
      "nature_of_magic": "It is not a mystical force, but the leaked, ambient radiation of the 'Sleeping Gods' (ancient, buried terraforming engines).",
      "known_practitioners": "Called 'Siphons'. They are heavily regulated and often conscripted by the Syndicate as living batteries.",
      "institutional_relationship": "The Syndicate publicly denounces magic as primitive superstition while secretly weaponizing Siphons in their military."
    }
  },
  "location_connections": [
    {
      "edge_type": "CONNECTED_TO",
      "from_node": "Syndicate Prime",
      "to_node": "The Ash Wastes (Colloquially: The Grey)",
      "properties": {
        "distance": "Approximately 400 miles of gradually degrading terrain.",
        "travel_times": {
          "foot": "Three weeks (highly dangerous)",
          "horse": "Impossible due to lack of forage",
          "rail": "Four days to the edge of the Wastes"
        }
      }
    }
  ]
}
```