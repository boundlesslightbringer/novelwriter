# Character Conception Examples

## Example 1: Standard Mode

### Input Context

```json
{
  "narrative_role": "A regional warlord acting as an obstacle and potential reluctant ally.",
  "chapter_context": 5,
  "thematic_constraints": "Low fantasy, gritty realism, themes of survival vs. honor."
}
```

### Output Artifacts

```json
{
  "invocation_mode": "standard",
  "character_concept": {
    "assigned_narrative_role": "Regional warlord — obstacle and potential reluctant ally.",
    "generation_method": "Role-First: A warlord who has survived thirty years of shifting alliances must be someone who avoids commitment until absolutely necessary.",
    "core_contradiction": "Has kept his people alive for thirty years by never fighting a battle he could avoid / believes a man who will not fight for what is sacred deserves nothing he has.",
    "sketch": "Caradhen rules the Thornback passes not through martial brilliance, but through a meticulous economy of violence. He is a man who measures every word and every drop of blood spent. To the lowland lords, he is an untrustworthy opportunist. To his own people, he is the only reason they still have homes. Yet, beneath his calculated pragmatism lies a deeply buried grief for the sacred things he has compromised to ensure their survival. He watches the young, idealistic warriors with a mix of contempt and desperate, hidden envy.",
    "open_questions": [
      "What event taught him that commitment leads to catastrophe?",
      "What does he believe about himself that is completely untrue?",
      "Is there something for which he would break his own rule?",
      "How does he treat people who show the open courage he denies himself?",
      "What will the protagonist offer that breaks him open?"
    ]
  },
  "provisional_flag": {
    "present": false,
    "world_context_assumptions": [],
    "most_likely_to_change": "",
    "key_information_needed": ""
  },
  "kg_context_used": {
    "factions_found": 3,
    "existing_characters_found": 12,
    "active_threads_found": 4,
    "notes": "Checked existing warlords to ensure no overlap in narrative function."
  }
}
```

## Example 2: Early Invocation Mode

### Input Context

```json
{
  "character_slot_sketch": {
    "narrative_role": "The naive heir who inherits a broken kingdom.",
    "implied_contradiction": "Wants to be a good ruler / has no idea what 'good' actually costs.",
    "stakes": "If they fail, the kingdom falls to the encroaching empire.",
    "world_context": "A kingdom recently fractured by a sudden assassination, bordering a highly militarized empire.",
    "open_questions": ["Who is manipulating them?"]
  },
  "world_context_sketch": "The kingdom is weak, relying on old treaties that the empire no longer respects. The court is full of sycophants.",
  "thematic_constraints": "Coming of age, political disillusionment."
}
```

### Output Artifacts

```json
{
  "invocation_mode": "early_invocation",
  "character_concept": {
    "assigned_narrative_role": "The naive heir who inherits a broken kingdom.",
    "generation_method": "Archetype-Subversion: Instead of a reluctant heir, they are eager and over-prepared with theory, but completely lack practical cruelty.",
    "core_contradiction": "Desperately wants to apply the high ideals of their education / is surrounded by a reality that only responds to ruthless pragmatism.",
    "sketch": "Elara spent her youth in the high libraries, memorizing the treaties and philosophies of the Golden Age. When the assassination thrusts the crown upon her, she steps up with terrifying earnestness, believing that justice and law will shield the kingdom. She is not weak; she is dangerously principled. Her tragedy is not that she doesn't know how to rule, but that she knows how to rule a world that no longer exists. Every moral compromise she is forced to make chips away at the foundation of her sanity.",
    "open_questions": [
      "Which specific ideal will be the first she has to sacrifice?",
      "Who is the mentor she realizes lied to her about how the world works?",
      "When she finally uses cruelty, who is the victim?",
      "Does she break, or does she become the monster she hated?"
    ]
  },
  "provisional_flag": {
    "present": true,
    "world_context_assumptions": [
      "The existence of a 'Golden Age' philosophy in the kingdom's history.",
      "The specific nature of the treaties with the empire."
    ],
    "most_likely_to_change": "The specific historical precedents she relies on, once the Culture and Faction nodes are fully built.",
    "key_information_needed": "The actual history of the empire's aggression and the specific factions within her own court."
  },
  "kg_context_used": {
    "factions_found": 0,
    "existing_characters_found": 0,
    "active_threads_found": 0,
    "notes": "Early invocation mode: no KG queries performed."
  }
}
```