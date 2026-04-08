# Finding a Seed Examples

## Example: Seed Generation Output

### Input Context

```json
{
  "genre": "Fantasy",
  "subgenres": ["Political Fantasy", "Dark Fantasy"],
  "themes": [
    "Legitimacy and the cost of inheritance",
    "The gap between what we make and what we become"
  ],
  "thematic_interdependencies": "interdependent",
  "negative_space": "No chosen-one framing. No dark lord. Not a quest structure."
}
```

### Output Artifacts

```json
{
  "seed_document": {
    "seed": "A woman kneels in a throne room before a court assembled to witness her execution. She is the last legitimate heir to the throne. The king who ordered her execution is her son.",
    "generation_method": "Character-First combined with 'What If?' — began with the impossible situation and asked what psychology could produce both figures without either being a monster.",
    "validation_record": {
      "concreteness": "PASS — specific room, specific moment, specific relationship; fully placeable.",
      "generative_tension": "PASS — raises more questions than it resolves; the history, the political necessity, and the human cost are all implied and none explained.",
      "emotional_necessity": "PASS — the mother/son structure makes the stake immediately and universally legible.",
      "open_architecture": "PASS — compatible with multiple narrative structures; no specific plot implied."
    },
    "genre_theme_fit": "Political Fantasy / Dark Fantasy: throne room, court, succession machinery are genre-native; darkness is human, not supernatural. Theme 1 (Legitimacy and inheritance): The execution is a legitimacy act. Theme 2 (What we make / what we become): The mother made the king; the king is executing the maker. Both themes are structurally inseparable in this seed — interdependency holds.",
    "questions": [
      "What did the mother do — or fail to do — that made this moment her son's only viable choice?",
      "What does the son believe about himself in this moment, and how much of it is true?",
      "Is there a version of this world in which legitimacy is not a death sentence?",
      "Who is watching this execution, and what do they owe each of them?",
      "What is the mother thinking about — not her death, but what specifically?",
      "What did she want for him? What did she actually give him?",
      "Is 'legitimate heir' a political category in this world or a spiritual one?",
      "What happens in the hour after the execution — to the court, to the son, to the body?",
      "Who in this room is lying about what they feel, and who is most dangerous because of it?",
      "Not yet cleanly formulated: something about whether love and the making of rulers can coexist — whether you can make a king without making something that will eventually have no use for you."
    ]
  },
  "candidate_seeds_log": [
    {
      "seed_statement": "A throne dragged to the centre of a great hall and set alight, the court watching in silence while the king who ordered it stands at the back in ordinary clothes.",
      "method": "Vivid Image",
      "strengths": "Visually strong; the ordinary clothes carry theme weight; politically resonant.",
      "failure_point": "Failed Open Architecture — implies an abdication or revolutionary moment with a narrow structural path. Insufficient generative tension for a novel.",
      "status": "Rejected"
    },
    {
      "seed_statement": "What if the only person who knows how to hold a fractured kingdom together is the person the new king had to destroy to take it?",
      "method": "What If?",
      "strengths": "Engages both interdependent themes; creates structural irony native to Political Fantasy.",
      "failure_point": "Failed Concreteness — exists as a structural premise, not an image; cannot be placed with a camera.",
      "status": "Rejected"
    },
    {
      "seed_statement": "Drew structural pattern from Eleanor of Aquitaine — a politically powerful woman who outlasts the system built to contain her, whose children become instruments of her containment.",
      "method": "Historical Inspiration",
      "strengths": "Rich structural pattern; engages inheritance theme directly; strong emotional architecture.",
      "failure_point": "Partial failure on Open Architecture — the Eleanor pattern implies a survival arc that narrows the story's options. Weaker than the definitive seed on Emotional Necessity (less concentrated).",
      "status": "Held as alternative"
    }
  ],
  "genre": "Fantasy",
  "subgenres": ["Political Fantasy", "Dark Fantasy"],
  "themes": [
    "Legitimacy and the cost of inheritance",
    "The gap between what we make and what we become"
  ],
  "thematic_interdependencies": "interdependent"
}
```