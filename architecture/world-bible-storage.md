# World Bible Storage Architecture

## Overview

This document defines the NoSQL storage schema for the World Bible, mapping each module from `grrm_agent_specs.md` to MongoDB collections with appropriate indexing strategies for efficient working-set queries.

---

## Storage Backend: MongoDB

**Rationale:**
- Document-oriented storage matches World Bible's semi-structured nature
- Rich query language supports working-set filtering
- Compound indexes enable fast exact lookups
- ACID transactions support state consistency during updates
- Schema versioning allows evolution

---

## Collection Schema Reference

### Module 1: Character State

#### Collection: `character_directory` (Module 1.1)

```javascript
{
  // Primary Key
  _id: ObjectId,
  character_id: "eddard_stark",  // Unique identifier (slug)
  
  // Identity
  full_name: "Eddard Stark",
  aliases: ["Ned", "Lord Stark"],
  
  // Physical & Social
  age: 35,
  age_reference_chapter: 1,  // Chapter when age was established
  physical_description: {
    height: "tall",
    build: "lean",
    hair: "dark brown, graying at temples",
    eyes: "gray",
    distinguishing_marks: ["scar on left forearm"]
  },
  social_class: "High Lord",
  current_role: "Hand of the King",
  current_title: "Lord of Winterfell",
  current_faction: "House Stark",
  
  // Location & State
  current_location: "King's Landing",
  location_since_chapter: 3,
  injuries: [],
  physical_state: "healthy",
  possessions_of_significance: ["Ice (greatsword)", "leather-bound book of lineage"],
  
  // Psychology
  current_beliefs: [
    "Robert is being manipulated by the Lannisters",
    "My duty is to protect the realm, not just my family"
  ],
  emotional_state: "troubled",
  emotional_state_chapter: 7,
  active_desires: [
    "Discover truth about Jon Arryn's death",
    "Protect my children from court politics"
  ],
  active_fears: [
    "Lannister treachery",
    "My honor will cost my family"
  ],
  
  // Arc
  arc_type: "Fall",  // Growth / Fall / Flat
  arc_stage: "pride_before_fall",
  
  // POV Tracking
  is_pov_character: true,
  pov_chapter_count: 7,
  last_pov_chapter: 7,
  
  // Metadata for working set queries
  last_appeared_chapter: 7,
  appears_in_chapters: [1, 2, 3, 5, 6, 7],
  
  // Versioning
  created_at: ISODate,
  updated_at: ISODate,
  version: 7  // Incremented on each update
}
```

**Indexes:**
```javascript
db.character_directory.createIndex({ "character_id": 1 }, { unique: true })
db.character_directory.createIndex({ "is_pov_character": 1, "last_pov_chapter": -1 })
db.character_directory.createIndex({ "last_appeared_chapter": -1 })
db.character_directory.createIndex({ "appears_in_chapters": 1 })
db.character_directory.createIndex({ "current_location": 1, "last_appeared_chapter": -1 })
```

---

#### Collection: `character_knowledge_matrix` (Module 1.2)

```javascript
{
  _id: ObjectId,
  
  // Composite Key Fields
  character_id: "eddard_stark",
  information_item_id: "lannister_incest",
  
  // Knowledge State
  status: "KNOWS",  // KNOWS / SUSPECTS / BELIEVES / DOES_NOT_KNOW
  acquired_at_chapter: 7,
  source: "Cersei's confession in godswood",
  
  // Dramatic positioning
  dramatic_irony_flag: false,  // True if reader knows more
  
  // Information metadata
  information_category: "secret",  // secret / event / identity / location
  confidence_level: "certain",  // certain / probable / possible / uncertain
  
  // Versioning
  created_at: ISODate,
  updated_at: ISODate,
  
  // Query optimization
  character_chapter_index: "eddard_stark#7"  // Compound for range queries
}
```

**Indexes:**
```javascript
db.character_knowledge_matrix.createIndex({ "character_id": 1, "status": 1 })
db.character_knowledge_matrix.createIndex({ "character_id": 1, "acquired_at_chapter": -1 })
db.character_knowledge_matrix.createIndex({ "information_item_id": 1, "status": 1 })
db.character_knowledge_matrix.createIndex({ "character_chapter_index": 1 })
db.character_knowledge_matrix.createIndex({ 
  "character_id": 1, 
  "information_category": 1, 
  "acquired_at_chapter": -1 
})
```

---

#### Collection: `relationship_records` (Module 1.3)

```javascript
{
  _id: ObjectId,
  
  // Directional relationship
  from_character: "eddard_stark",
  to_character: "cersei_lannister",
  
  // Relationship state
  emotional_valence: "contempt_with_fear",
  power_dynamic: {
    holder: "cersei_lannister",
    leverage: "control of throne, gold cloaks",
    shift_since_chapter: null
  },
  
  // History
  relationship_history: [
    {
      event: "First meeting at court",
      chapter: 1,
      impact: "neutral_suspicious"
    },
    {
      event: "Eddard threatens to expose incest",
      chapter: 7,
      impact: "deteriorated_severely"
    }
  ],
  
  // Secrets
  secrets_kept: {
    from_to: ["Jon Arryn's investigations"],
    to_from: ["Extent of Jaime relationship", "Plans for throne"]
  },
  
  // Current state
  most_recent_interaction: {
    chapter: 7,
    summary: "Confrontation in godswood",
    outcome: "threat_made_no_resolution"
  },
  trajectory: "Deteriorating",  // Stable / Deteriorating / Evolving / Volatile
  
  // Versioning
  last_updated_chapter: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.relationship_records.createIndex({ "from_character": 1, "to_character": 1 }, { unique: true })
db.relationship_records.createIndex({ "from_character": 1, "last_updated_chapter": -1 })
db.relationship_records.createIndex({ "to_character": 1, "last_updated_chapter": -1 })
db.relationship_records.createIndex({ "trajectory": 1, "last_updated_chapter": -1 })
```

---

### Module 2: Plot & Timeline State

#### Collection: `absolute_timeline` (Module 2.1)

```javascript
{
  _id: ObjectId,
  
  // Time reference
  day_number: 1,  // Relative day from story start
  absolute_date: "298 AC",  // In-world calendar
  
  // Events on this day
  events: [
    {
      event_id: "royal_arrival",
      description: "Royal party arrives at Winterfell",
      pov_chapters: [1],
      characters_involved: ["eddard_stark", "robert_baratheon"],
      location: "Winterfell"
    }
  ],
  
  // Simultaneous events (for multi-POV coordination)
  simultaneous_events: [
    {
      location: "King's Landing",
      event: "Small council meets without Ned",
      related_chapter: 1,  // Stark POV chapter where this is referenced
      pov_chapter_showing_it: null  // Filled when Lannister POV chapter written
    }
  ],
  
  // Travel records
  travel_records: [
    {
      character: "eddard_stark",
      from_location: "Winterfell",
      to_location: "King's Landing",
      departure_day: 3,
      arrival_day: 15,
      duration_days: 12
    }
  ],
  
  // Environment
  seasonal_state: "late_summer",
  weather_by_region: {
    "north": "cool, early autumn winds",
    "kings_landing": "hot, humid"
  },
  
  // Versioning
  chapter_snapshot: 1,  // This record represents state at end of chapter N
  created_at: ISODate
}
```

**Indexes:**
```javascript
db.absolute_timeline.createIndex({ "day_number": 1 }, { unique: true })
db.absolute_timeline.createIndex({ "chapter_snapshot": 1 }, { unique: true })
db.absolute_timeline.createIndex({ "events.pov_chapters": 1 })
db.absolute_timeline.createIndex({ "travel_records.character": 1, "travel_records.departure_day": 1 })
```

---

#### Collection: `pov_chapter_log` (Module 2.2)

```javascript
{
  _id: ObjectId,
  
  // Primary key
  chapter_number: 7,
  
  // Basic info
  pov_character: "eddard_stark",
  location: "King's Landing",
  
  // Scene breakdown
  scenes: [
    {
      scene_number: 1,
      summary: "Eddard reviews Jon Arryn's notes",
      word_count: 450,
      archived_draft_ref: "ch7_scene1_v1.md"
    },
    {
      scene_number: 2,
      summary: "Confrontation with Cersei in godswood",
      word_count: 1200,
      archived_draft_ref: "ch7_scene2_v2.md"
    }
  ],
  
  // Chapter summary
  scene_summary: "Eddard discovers the truth and confronts Cersei, choosing mercy over immediate justice",
  
  // Cliffhanger
  cliffhanger: {
    present: true,
    description: "Cersei leaves with a threat; Eddard knows he has made an enemy of the queen"
  },
  
  // Connections
  connections: [
    {
      connected_pov: "cersei_lannister",
      connection_type: "same_event_different_angle",
      scene_reference: "godswood_confrontation"
    }
  ],
  
  // State changes this chapter
  chapter_delta: {
    characters_changed: ["eddard_stark", "cersei_lannister"],
    knowledge_revealed: ["lannister_incest"],
    relationships_changed: ["eddard_stark->cersei_lannister"],
    plot_threads_advanced: ["throne_succession", "jon_arryn_murder"],
    consequences_planted: ["cersei_retaliation_bomb"]
  },
  
  // Versioning
  status: "published",  // draft / published / revised
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.pov_chapter_log.createIndex({ "chapter_number": 1 }, { unique: true })
db.pov_chapter_log.createIndex({ "pov_character": 1, "chapter_number": -1 })
db.pov_chapter_log.createIndex({ "chapter_delta.characters_changed": 1 })
db.pov_chapter_log.createIndex({ "chapter_delta.plot_threads_advanced": 1 })
db.pov_chapter_log.createIndex({ "location": 1, "chapter_number": -1 })
```

---

#### Collection: `plot_thread_registry` (Module 2.3)

```javascript
{
  _id: ObjectId,
  
  // Identification
  thread_id: "throne_succession",
  thread_name: "Who will succeed Robert on the throne?",
  
  // Status
  status: "Active",  // Active / Dormant / Resolved / Abandoned
  
  // Timeline
  originating_chapter: 1,
  expected_convergence: {
    start_chapter: 20,
    end_chapter: 25,
    confidence: "rough_estimate"
  },
  actual_resolution_chapter: null,
  
  // Participants
  characters_involved: ["eddard_stark", "cersei_lannister", "joffrey_baratheon"],
  
  // Dependencies
  dependencies: {
    must_resolve_before: ["war_of_five_kings"],
    must_resolve_alongside: []
  },
  
  // Progress tracking
  thread_log: [
    {
      chapter: 1,
      event: "Jon Arryn's death raises succession questions",
      advancement: "established"
    },
    {
      chapter: 7,
      event: "Eddard confirms Joffrey is not Robert's son",
      advancement: "significant_progress"
    }
  ],
  
  // Resolution (when resolved)
  resolution_summary: null,
  
  // Versioning
  last_updated_chapter: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.plot_thread_registry.createIndex({ "thread_id": 1 }, { unique: true })
db.plot_thread_registry.createIndex({ "status": 1, "expected_convergence.start_chapter": 1 })
db.plot_thread_registry.createIndex({ "characters_involved": 1, "status": 1 })
db.plot_thread_registry.createIndex({ "last_updated_chapter": -1 })
db.plot_thread_registry.createIndex({ 
  "expected_convergence.start_chapter": 1,
  "expected_convergence.end_chapter": 1 
})
```

---

#### Collection: `pending_payoffs` (Module 2.4)

```javascript
{
  _id: ObjectId,
  
  // Setup identification
  setup_element_id: "cersei_adultery_revealed",
  setup_element: "Cersei's infidelity and incest revealed to reader",
  type: "Chekhov's gun",  // Chekhov's gun / Foreshadowing / Consequence bomb / Prophecy / Legend
  
  // Planting
  planted_in_chapter: 1,
  embedded_by: "Scene Construction",  // or "Foreshadowing Placement"
  
  // Payoff tracking
  expected_payoff_window: {
    start_chapter: 5,
    end_chapter: 10
  },
  resolution_status: "Pending",  // Pending / Paid off / Overdue
  payoff_chapter: null,
  
  // Dependencies
  must_payoff_before: ["robert_death"],
  related_setups: ["jon_arryn_investigation"],
  
  // Context for payoff
  payoff_context: {
    characters_who_know: ["eddard_stark"],
    characters_who_suspect: [],
    potential_reveal_methods: ["confrontation", "political_blackmail"]
  },
  
  // Versioning
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.pending_payoffs.createIndex({ "setup_element_id": 1 }, { unique: true })
db.pending_payoffs.createIndex({ "resolution_status": 1, "expected_payoff_window.end_chapter": 1 })
db.pending_payoffs.createIndex({ "planted_in_chapter": 1 })
db.pending_payoffs.createIndex({ 
  "resolution_status": "Pending",
  "expected_payoff_window.start_chapter": { $lte: "current_chapter" }
})
```

---

### Module 3: World State

#### Collection: `political_power_map` (Module 3.1)

```javascript
{
  _id: ObjectId,
  
  // Territory
  territory_id: "westerlands",
  territory_name: "The Westerlands",
  
  // Current control
  current_controller: "House Lannister",
  controller_leader: "tywin_lannister",
  held_since_chapter: 1,
  
  // Political relationships
  allegiances: [
    {
      ally: "House Baratheon (crown)",
      stability: "shaky",  // strong / stable / shaky / collapsing
      nature: "marriage_alliance",
      since_chapter: 1
    }
  ],
  active_enmities: [
    {
      enemy: "House Stark",
      cause: "Ned's investigation threatens Lannisters",
      current_phase: "cold_war",
      chapter_reference: 7
    }
  ],
  
  // Assets
  military_assets: {
    army_size: "large",
    location: "dispersed",
    commander: "tywin_lannister",
    loyalty: "high"
  },
  economic_assets: {
    gold_reserves: "vast",
    key_resources: ["gold_mines", "trade_routes"],
    food_stores: "adequate"
  },
  
  // Conflicts
  ongoing_conflicts: [
    {
      conflict_id: "throne_politics",
      belligerents: ["House Lannister", "House Stark"],
      phase: "political_maneuvering",
      chapter_reference: 7
    }
  ],
  
  // Versioning (per-chapter snapshots)
  chapter_snapshot: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.political_power_map.createIndex({ "territory_id": 1, "chapter_snapshot": -1 }, { unique: true })
db.political_power_map.createIndex({ "current_controller": 1, "chapter_snapshot": -1 })
db.political_power_map.createIndex({ "allegiances.ally": 1, "chapter_snapshot": -1 })
db.political_power_map.createIndex({ "chapter_snapshot": -1 })
```

---

#### Collection: `geography` (Module 3.2)

```javascript
{
  _id: ObjectId,
  
  // Identity
  location_id: "kings_landing",
  location_name: "King's Landing",
  colloquial_names: ["The Capital", "The Crown City"],
  
  // Description
  physical_description: "Built on three hills, surrounded by walls, overlooking Blackwater Bay",
  
  // Climate
  climate: {
    seasonal_norms: "hot, humid summers; mild, wet winters",
    current_weather: "hot, humid"
  },
  
  // Connections
  connections: [
    {
      location_id: "winterfell",
      route_type: "road",
      distance_days_by_foot: 60,
      distance_days_by_horse: 30,
      distance_days_by_ship: 14
    },
    {
      location_id: "casterly_rock",
      route_type: "road",
      distance_days_by_horse: 20
    }
  ],
  
  // Versioning (static with versioned updates)
  established_in_chapter: 1,
  last_modified_chapter: 1,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.geography.createIndex({ "location_id": 1 }, { unique: true })
db.geography.createIndex({ "connections.location_id": 1 })
```

---

#### Collection: `cultures_customs_religion` (Module 3.3)

```javascript
{
  _id: ObjectId,
  
  // Identity
  culture_id: "nothern_customs",
  culture_name: "Northern Customs",
  region: "The North",
  
  // Values & Fears
  core_values: ["honor", "duty", "stoicism", "ancestral_memory"],
  core_fears: ["forgetting", "dishonor", "southern_corruption"],
  
  // Social structure
  customs: {
    birth: ["name_day celebrations"],
    death: ["burial in crypts", "remembrance feasts"],
    marriage: ["wedding in godswood", "guest right"],
    hospitality: "guest_right_sacred"
  },
  class_structure: {
    hierarchy: ["High Lords", "Bannermen", "Smallfolk"],
    enforcement: "traditional_oaths"
  },
  gender_dynamics: {
    roles: "egalitarian_by_westeros_standards",
    constraints: "women_can_inherit_if_no_sons",
    exceptions: ["Lady of Bear Island"]
  },
  
  // Religion
  religious_beliefs: {
    primary_faith: "Old Gods",
    theology: "nameless_gods_of_forest",
    afterlife: "become_part_of_weirwoods",
    magic_relationship: "accepted_as_part_of_world"
  },
  
  // Political influence
  political_power: {
    reach: "limited_to_north",
    influence: "declining_under_southern_pressure"
  },
  
  // Versioning
  established_in_chapter: 1,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.cultures_customs_religion.createIndex({ "culture_id": 1 }, { unique: true })
db.cultures_customs_religion.createIndex({ "region": 1 })
```

---

#### Collection: `history_legends` (Module 3.4)

```javascript
{
  _id: ObjectId,
  
  // Identity
  event_id: "long_night",
  event_name: "The Long Night",
  common_names: ["The Long Night", "The Darkness", "The White Walkers' Invasion"],
  
  // Accounts
  true_account: "White Walkers invaded from the far north; humans allied with Children...",
  believed_account: "A great darkness that lasted a generation; heroes defeated it",
  
  // Factional interpretations
  factional_interpretations: {
    "northerners": "literal_truth_about_white_walkers",
    "southerners": "legendary_exaggeration",
    "maesters": "natural_phenomenon_exaggerated"
  },
  
  // Physical remnants
  physical_remnants: [
    {
      type: "Wall",
      location: "the_wall",
      description: "300-foot ice wall built after the Long Night"
    }
  ],
  
  // Story significance
  story_significance: "Historical precedent for supernatural threat; explains Wall's existence",
  
  // References
  referenced_in_chapters: [3, 12, 24],
  
  // Versioning
  established_in_chapter: 3,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.history_legends.createIndex({ "event_id": 1 }, { unique: true })
db.history_legends.createIndex({ "referenced_in_chapters": 1 })
db.history_legends.createIndex({ "physical_remnants.location": 1 })
```

---

#### Collection: `magic_system_state` (Module 3.5)

```javascript
{
  _id: ObjectId,
  
  // Current prevalence
  current_prevalence: "Increasing",  // Rare / Increasing / Decreasing / Stable
  prevalence_tracking_chapter: 15,
  
  // Capabilities
  confirmed_capabilities: [
    {
      capability: "Resurrection (limited)",
      chapter_reference: 10,
      practitioner: "thoros_of_myr",
      limitations: "only_recent_deaths"
    }
  ],
  
  // Limits
  confirmed_limits: [
    {
      limit: "Cannot resurrect the long-dead",
      chapter_reference: 10,
      evidence: "Thoros failed on three-day-old corpse"
    }
  ],
  
  // Costs
  confirmed_costs: [
    {
      cost: "Resurrection erases memory/personality",
      chapter_reference: 15,
      practitioner: "beric_dondarrion"
    }
  ],
  
  // Practitioners
  known_practitioners: [
    {
      character_id: "melisandre",
      abilities: ["shadow_birthing", "glamour", "prophecy"],
      social_status: "feared_respected"
    }
  ],
  
  // Unexplained phenomena
  unexplained_phenomena: [
    {
      phenomenon: "Direwolf birth coincidence",
      chapter_reference: 1,
      status: "unexplained_inworld"
    }
  ],
  
  // Recent events
  recent_magical_events: [1, 5, 10, 15],
  
  // Versioning (per-chapter snapshot)
  chapter_snapshot: 15,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.magic_system_state.createIndex({ "chapter_snapshot": -1 }, { unique: true })
db.magic_system_state.createIndex({ "confirmed_capabilities.chapter_reference": 1 })
db.magic_system_state.createIndex({ "known_practitioners.character_id": 1 })
```

---

### Module 4: Consequence Ledger

#### Collection: `consequence_chains` (Module 4.1)

```javascript
{
  _id: ObjectId,
  
  // Triggering event
  event_id: "ned_confronts_cersei",
  triggering_event: "Eddard confronts Cersei about incest",
  chapter_reference: 7,
  
  // Consequence phases
  consequences: {
    immediate: [
      {
        consequence: "Cersei becomes active enemy of Ned",
        chapter_played_out: 7,
        affected_characters: ["eddard_stark", "cersei_lannister"]
      }
    ],
    short_term: [
      {
        consequence: "Cersei accelerates plan to neutralize Ned",
        chapter_window: { start: 8, end: 10 },
        affected_characters: ["cersei_lannister"],
        status: "in_progress"
      }
    ],
    long_term: [
      {
        consequence: "Lannister-Stark conflict becomes open war",
        chapter_window: { start: 20, end: 25 },
        affected_characters: ["all_major_houses"],
        status: "projected",
        cascade_chain_id: "war_of_five_kings"
      }
    ]
  },
  
  // Affected characters
  affected_characters: ["eddard_stark", "cersei_lannister", "children_of_ned", "children_of_cersei"],
  
  // Cascade linking
  cascade_chain_id: "lannister_stark_conflict",
  
  // Versioning
  last_updated_chapter: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.consequence_chains.createIndex({ "event_id": 1 }, { unique: true })
db.consequence_chains.createIndex({ "chapter_reference": -1 })
db.consequence_chains.createIndex({ "consequences.short_term.chapter_window.start": 1 })
db.consequence_chains.createIndex({ "affected_characters": 1 })
db.consequence_chains.createIndex({ "cascade_chain_id": 1 })
```

---

#### Collection: `consequence_bombs` (Module 4.2)

```javascript
{
  _id: ObjectId,
  
  // Planted event
  bomb_id: "cersei_retaliation",
  planted_event: "Cersei swears revenge after Ned's confrontation",
  chapter_planted: 7,
  
  // Future consequence
  nature_of_future_consequence: "Cersei arranges for Ned's arrest/trial",
  
  // Detonation tracking
  estimated_detonation_window: {
    start_chapter: 8,
    end_chapter: 12
  },
  status: "Armed",  // Armed / Detonated / Defused
  detonation_chapter: null,
  
  // Trigger conditions
  trigger_conditions: [
    "Ned acts against Cersei's interests",
    "Cersei gains advantage"
  ],
  
  // Versioning
  last_checked_chapter: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.consequence_bombs.createIndex({ "bomb_id": 1 }, { unique: true })
db.consequence_bombs.createIndex({ "status": 1, "estimated_detonation_window.start": 1 })
db.consequence_bombs.createIndex({ "chapter_planted": 1 })
db.consequence_bombs.createIndex({ 
  "status": "Armed",
  "estimated_detonation_window.end": { $lte: "current_chapter" }
})
```

---

#### Collection: `cascade_chains` (Module 4.3)

```javascript
{
  _id: ObjectId,
  
  // Chain identity
  chain_id: "lannister_stark_conflict",
  chain_name: "Lannister-Stark Conflict Cascade",
  
  // Sequence
  chain_sequence: [
    { step: 1, event: "Jon Arryn's death investigation", chapter: 1 },
    { step: 2, event: "Ned discovers incest", chapter: 7 },
    { step: 3, event: "Ned confronts Cersei", chapter: 7 },
    { step: 4, event: "TBD - Ned's arrest", chapter: null },
    { step: 5, event: "TBD - War of Five Kings", chapter: null }
  ],
  
  // Progress
  current_position: 3,
  remaining_links: [
    { step: 4, event: "Ned's arrest", projected_chapter: "8-12" },
    { step: 5, event: "War of Five Kings", projected_chapter: "20-25" }
  ],
  
  // Participants
  characters_involved: ["eddard_stark", "cersei_lannister", "tywin_lannister", "robert_baratheon"],
  
  // Versioning
  last_updated_chapter: 7,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.cascade_chains.createIndex({ "chain_id": 1 }, { unique: true })
db.cascade_chains.createIndex({ "characters_involved": 1 })
db.cascade_chains.createIndex({ "last_updated_chapter": -1 })
```

---

### Module 5: Continuity Registry

#### Collection: `physical_continuity` (Module 5.1)

```javascript
{
  _id: ObjectId,
  
  // Subject
  subject_type: "character",  // character / object / location
  subject_id: "eddard_stark",
  
  // Physical detail
  detail_category: "possession",
  detail: "owns greatsword Ice",
  
  // Tracking
  established_in_chapter: 1,
  last_referenced_in_chapter: 7,
  
  // References
  all_references: [1, 3, 7],
  
  // Versioning
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.physical_continuity.createIndex({ "subject_id": 1, "detail_category": 1 })
db.physical_continuity.createIndex({ "established_in_chapter": 1 })
db.physical_continuity.createIndex({ "last_referenced_in_chapter": -1 })
```

---

#### Collection: `logical_continuity` (Module 5.2)

```javascript
{
  _id: ObjectId,
  
  // Information flow
  information_item_id: "lannister_incest",
  transmitted_from: "cersei_lannister",
  transmitted_to: "eddard_stark",
  chapter_reference: 7,
  method: "Spoken",  // Spoken / Written / Overheard / Inferred
  
  // Context
  transmission_scene: "godswood_confrontation",
  
  // Versioning
  created_at: ISODate
}
```

**Indexes:**
```javascript
db.logical_continuity.createIndex({ "information_item_id": 1, "chapter_reference": -1 })
db.logical_continuity.createIndex({ "transmitted_from": 1, "chapter_reference": -1 })
db.logical_continuity.createIndex({ "transmitted_to": 1, "chapter_reference": -1 })
```

---

#### Collection: `contradiction_log` (Module 5.3)

```javascript
{
  _id: ObjectId,
  
  // Contradiction identification
  contradiction_id: "CON-001",
  detected_at_chapter: 12,
  
  // Nature
  nature: "Knowledge",  // Physical / Logical / Knowledge / Timeline
  description: "Character acts on information they shouldn't have yet",
  
  // Conflicting records
  conflicting_records: [
    { record_type: "character_knowledge", record_id: "ObjectId(...)" },
    { record_type: "scene_content", record_id: "ch12_scene3" }
  ],
  
  // Resolution
  resolution_status: "Unresolved",  // Unresolved / Resolved / Accepted
  resolution_notes: null,
  resolved_at_chapter: null,
  
  // Versioning
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
```javascript
db.contradiction_log.createIndex({ "contradiction_id": 1 }, { unique: true })
db.contradiction_log.createIndex({ "resolution_status": 1, "detected_at_chapter": -1 })
db.contradiction_log.createIndex({ "nature": 1 })
```

---

## Summary of Collections

| Module | Collection | Documents | Primary Query Pattern |
|--------|-----------|-----------|----------------------|
| 1.1 | `character_directory` | Per character | Exact lookup by ID, filtered by appearance |
| 1.2 | `character_knowledge_matrix` | Per character per info | Filter by character + chapter range |
| 1.3 | `relationship_records` | Per pair | Filter by character + recency |
| 2.1 | `absolute_timeline` | Per day/chapter | Time range queries |
| 2.2 | `pov_chapter_log` | Per chapter | Exact chapter lookup |
| 2.3 | `plot_thread_registry` | Per thread | Status + convergence window |
| 2.4 | `pending_payoffs` | Per setup | Status + payoff window |
| 3.1 | `political_power_map` | Per territory per chapter | Chapter snapshot |
| 3.2 | `geography` | Per location | Exact lookup |
| 3.3 | `cultures_customs_religion` | Per culture | Region lookup |
| 3.4 | `history_legends` | Per event | Reference lookup |
| 3.5 | `magic_system_state` | Per chapter | Chapter snapshot |
| 4.1 | `consequence_chains` | Per event | Affected character lookup |
| 4.2 | `consequence_bombs` | Per bomb | Status + detonation window |
| 4.3 | `cascade_chains` | Per chain | Character involvement |
| 5.1 | `physical_continuity` | Per detail | Subject lookup |
| 5.2 | `logical_continuity` | Per transmission | Information flow lookup |
| 5.3 | `contradiction_log` | Per contradiction | Status lookup |

**Total: 17 collections**

---

## Schema Evolution

All collections include `version` or chapter-based versioning fields to support schema evolution:

1. Add new fields as optional
2. Use `updated_at` timestamps to identify records needing migration
3. Maintain backward compatibility in queries
4. Version schema changes in application layer

---

## Backup and Archival

- **Hot data:** Last 3 chapters (frequent queries)
- **Warm data:** Chapters 4-20 (occasional queries)
- **Cold data:** Archive to S3/Azure Blob after chapter 20
- **Snapshot schedule:** After each chapter completion
