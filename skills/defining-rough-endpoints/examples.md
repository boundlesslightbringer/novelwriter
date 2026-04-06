# Defining Rough Endpoints Examples

## Example: Two-Pass Compass Generation

### Input Context (Pass 1)

```json
{
  "seed_document": {
    "seed": "A woman kneels in a throne room before a court assembled to witness her execution. She is the last legitimate heir to the throne. The king who ordered her execution is her son.",
    "genre_theme_fit": "Political Fantasy / Dark Fantasy. Themes: Legitimacy and the cost of inheritance (interdependent with) the gap between what we make and what we become.",
    "questions": [
      "What did the mother do — or fail to do — that made this moment her son's only viable choice?",
      "What does the son believe about himself in this moment, and how much of it is true?"
    ]
  }
}
```

### Pass 1 Output Artifacts

```json
{
  "pass": 1,
  "prologue_specification": {
    "warranted": true,
    "temporal_relationship": "11 years before Chapter 1.",
    "pov_or_register": "Third person limited — the mother, before she became the Dowager, on the night she decided to make her son king rather than claim the throne herself.",
    "what_it_establishes": "The reader must enter Chapter 1 knowing that the mother had a choice, that she chose the son, and that she knew what it would cost. This cannot be established from within Chapter 1 without becoming exposition.",
    "what_it_withholds": "Whether she regrets it. Whether she was right.",
    "relationship_to_milestones": "The prologue event is a precondition — it is the choice that makes Milestone 1 possible."
  },
  "starting_situation": "The kingdom has been at peace for eleven years — the kind maintained through pressure rather than settlement. The king is young, effective, and aware that every faction supported him because he was the alternative to a worse option. His mother, under house arrest on charges that are technically true and politically necessary, is the instability that cannot remain as it is.",
  "draft_ending_destination": "The question of what legitimacy costs — and who pays it — will have been answered. Something will have been lost that cannot be recovered; the story ends in that loss's aftermath.",
  "draft_milestones": [
    {
      "milestone_id": "M1",
      "description": "The execution is carried out or not — the son makes the choice that determines who he is.",
      "character_slots": ["slot_king"]
    },
    {
      "milestone_id": "M2",
      "description": "A crisis in which the political machinery the mother built begins working against the son.",
      "character_slots": ["slot_king"]
    },
    {
      "milestone_id": "M3",
      "description": "A moment in which the mother's full account of what she did — and why — is rendered.",
      "character_slots": ["slot_mother"]
    }
  ],
  "character_slot_sketches": [
    {
      "slot_id": "slot_king",
      "narrative_role": "The person whose choice at Milestone 1 defines the story's central question.",
      "implied_contradiction": "Was made into something by someone who loved him / has become something that may have no use for love.",
      "stakes": "His legitimacy, his self-narrative, his capacity to be someone worth surviving as.",
      "world_context": "Young king, eleven years of regency shaped by his mother, now operating in personal rule; every faction's loyalty is contingent.",
      "open_questions": [
        "Does he believe the execution is necessary, or does he need to believe it?",
        "What would it mean for him to refuse — not politically, but psychologically?",
        "What does he think his mother actually wants from him in this moment?"
      ]
    },
    {
      "slot_id": "slot_mother",
      "narrative_role": "The person whose full account of her choices reframes the story's events.",
      "implied_contradiction": "Made the son king to protect him / or to extend herself / or both without being able to tell the difference.",
      "stakes": "What she is remembered as. Whether what she built survives her.",
      "world_context": "Former regent, now under arrest; the most politically intelligent person in the story, operating from a position of formal powerlessness.",
      "open_questions": [
        "What does she want in the final accounting — to be understood, to be forgiven, or something else entirely?",
        "When did she first know the execution was coming?",
        "What did she do in the years of the regency that she will not defend, even to herself?"
      ]
    }
  ],
  "draft_core_conflict_question": "Can a person survive becoming what someone who loved them made them, and still be someone worth surviving as?",
  "compass_notes": "The ending does not specify whether the son lives, dies, or is deposed. Milestone 1 is unsequenced — it may be the opening image, the midpoint, or the climax. The seed's questions about legitimacy as spiritual vs. political category remain open for Worldbuilding."
}
```

### Pass 2 Output Artifacts

```json
{
  "pass": 2,
  "prologue_specification": "Warranted. 11 years before Chapter 1. Third person limited — the mother, before she became the Dowager, on the night she decided to make her son king rather than claim the throne herself. Establishes she had a choice and chose the son. Withholds whether she regrets it.",
  "starting_situation": "The kingdom has been at peace for eleven years — the kind maintained through pressure rather than settlement. The king is young, effective, and aware that every faction supported him because he was the alternative to a worse option. His mother, under house arrest on charges that are technically true and politically necessary, is the instability that cannot remain as it is.",
  "ending_destination": "The question of what legitimacy costs — and who pays it — will have been answered. Something will have been lost that cannot be recovered; the story ends in that loss's aftermath.",
  "milestones": [
    {
      "milestone_id": "M1",
      "description": "The execution is carried out. The king's core contradiction — genuine belief in necessary ruthlessness / persistent inability to stop waiting for her to tell him he has done the right thing — means the milestone now has a specific internal texture that shapes how Scene Construction will approach it.",
      "character_references": ["char_king"]
    },
    {
      "milestone_id": "M2",
      "description": "A crisis in which the political machinery the mother built begins working against the son.",
      "character_references": ["char_king"]
    },
    {
      "milestone_id": "M3",
      "description": "The moment of accounting is now understood as a scene the mother stages deliberately, not one that happens to her. She is not passive in any situation she has time to prepare for.",
      "character_references": ["char_mother"]
    }
  ],
  "core_conflict_question": "Can a person survive becoming what someone who loved them made them, and still be someone worth surviving as?",
  "compass_notes": "The ending does not specify whether the son lives, dies, or is deposed. Milestone 1 is unsequenced — it may be the opening image, the midpoint, or the climax.",
  "plot_thread_seeds": [
    {
      "node_type": "PlotThread",
      "properties": {
        "name": "The Mother's Execution",
        "status": "Active",
        "originating_chapter": 1
      }
    },
    {
      "node_type": "PlotThread",
      "properties": {
        "name": "The Political Machinery Crisis",
        "status": "Active",
        "originating_chapter": 1
      }
    }
  ],
  "payoff_seeds": [
    {
      "node_type": "Payoff",
      "properties": {
        "type": "Foreshadowing",
        "description": "The mother's staged final accounting.",
        "planted_in_chapter": 1,
        "resolution_status": "Pending"
      }
    }
  ]
}
```