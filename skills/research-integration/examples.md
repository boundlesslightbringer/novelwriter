# Research Integration Examples

The following examples demonstrate the expected input and output for the `research-integration` skill.

## Example A — Real-world factual domain

**Input shape:**
```
Domain type: Real-world factual
Question: How did succession crises actually work in medieval European kingdoms — specifically legal mechanisms, factional behaviour in the aftermath of delegitimising events?
Story context: A king has executed his mother, the previous heir. The court is divided between those who supported the execution and those now uncertain what it means for their position.
```

**Output shape (Prose Summary):**
```
Domain summary: Succession in medieval European kingdoms was not primarily a legal question — it was a question of who could enforce a claim. The law provided frameworks for legitimacy, but legitimacy without military and factional support was theoretical...

Key structural facts:
  The role of legitimacy claims: [notes]
  Factional behaviour after delegitimising events: [notes — specifically: most powerful actors waited to determine who was winning before committing; the window of ambiguity was dangerous for the ruler]
  Specific vulnerability of kings who destroyed their own succession line: [notes]

What fiction usually gets wrong:
  1. Presents succession disputes as primarily about legal right; in practice legal claims were secondary to who had swords and money.
  2. Presents factions as having clear sides early; in practice most powerful actors waited.
  [continues]

Story-relevant cautions:
  1. Accurate treatment implies the son's position is less secure after the execution than before — the execution may have solved one legitimacy problem while creating a larger one.
  [continues]
```

**Output shape (JSON `artifacts`):**
```json
{
  "domain_type": "real_world_factual",
  "research_question": "How did succession crises actually work in medieval European kingdoms — specifically legal mechanisms, factional behaviour in the aftermath of delegitimising events?",
  "domain_summary": "Succession in medieval European kingdoms was rarely a pure legal question; it was fundamentally a question of who could enforce a claim. While the law provided frameworks for legitimacy, legitimacy without military, financial, and factional support was largely theoretical. When a delegitimising event occurred—such as a ruler executing a close family member or heir—the immediate aftermath was characterized by extreme ambiguity. Factions did not typically form instantly around ideological lines; instead, the most powerful actors delayed committing their forces or wealth until they could determine which side was likely to win. This window of ambiguity was the most dangerous period for the ruler, as the perceived loss of legitimacy invited opportunistic challenges from rivals who might otherwise have remained loyal.",
  "key_structural_facts_or_patterns": {
    "the_role_of_legitimacy_claims": "Legitimacy was a tool for coalition-building rather than an absolute rule. A strong legal claim made it cheaper to buy support, but a weak claim backed by overwhelming force usually prevailed.",
    "factional_behaviour_after_delegitimising_events": "Most powerful actors waited to determine who was winning before committing. The window of ambiguity was highly dangerous for the ruler, as fence-sitting was the optimal survival strategy for the nobility.",
    "vulnerability_of_kings_who_destroyed_their_own_succession_line": "Executing a primary heir or family member often alienated the specific noble networks that had tied their fortunes to that heir, forcing the king to rely on narrower, more mercenary support bases."
  },
  "useful_specifics": "In several historical instances, the execution of a royal family member led to immediate capital flight—nobles quietly moving wealth or retreating to fortified estates rather than openly rebelling, creating a 'hollow court' where the king's commands were acknowledged but not executed.",
  "what_is_commonly_misrepresented": [
    "Fiction often presents succession disputes as primarily about legal right; in practice, legal claims were secondary to who had swords and money.",
    "Fiction presents factions as having clear, ideologically committed sides early on; in practice, most powerful actors waited to see who would win."
  ],
  "story_relevant_cautions": [
    "Accurate treatment implies the son's position is less secure after the execution than before—the execution may have solved one legitimacy problem while creating a much larger vulnerability.",
    "The court's division shouldn't be loud arguments in the throne room, but quiet absences, delayed tax payments, and unanswered summons."
  ],
  "further_questions": [
    "Which specific noble families had their fortunes tied to the executed mother?",
    "Who controls the treasury right now, and are they releasing funds to the king?",
    "Is there a secondary heir who suddenly looks like a safer bet to the fence-sitting nobles?"
  ]
}
```

---

## Example B — Speculative/fictional domain

**Input shape:**
```
Domain type: Speculative / fictional
Question: What are the structural patterns in how science fiction has handled the social and political consequences of faster-than-light travel — specifically how FTL shapes the plausibility of interstellar empires, communication lag, and individual experience of distance?
Story context: Building a generation ship / slower-than-light story and need to understand what structural choices FTL SF has made — and why — in order to make deliberate choices about the slower-than-light alternative.
```

**Output shape (Prose Summary):**
```
Domain summary: FTL in science fiction is rarely just a transportation mechanism — it is a political enabling technology. The structural pattern across the genre is that FTL travel tends to be used to make interstellar empire plausible (you cannot have a coherent empire across light-years without near-instantaneous communication and travel). The interesting tension is between the scale FTL enables and the human-scale stories that require intimacy and consequence...

Key structural patterns:
  Empire and communication: Works that grant FTL travel almost always grant FTL communication; the few that separate the two (faster travel than communication, or vice versa) generate distinct political structures — specifically: polities that can move armies faster than they can send orders create fundamentally different command structures than those with instant communication.
  The cost structure of FTL: The most generatively interesting SF treatments attach specific costs to FTL — not just fuel or technology, but cognitive, psychological, or biological costs that create character and social pressure. The absence of cost tends to produce empire stories that feel politically thin.
  Slower-than-light as a structural choice: Works that deliberately choose STL over FTL tend to generate stories about: (a) the experience of irreversible commitment (you cannot go back); (b) the divergence of cultures over generations; (c) the psychology of people who will never see the destination. These are structurally very different pressures than FTL generates and tend to produce more intimate, consequence-heavy narratives.

What the genre commonly handles poorly:
  1. FTL communication treated as equivalent to FTL travel — the political structures this implies are rarely examined rigorously.
  2. STL generation ship stories often focus on the middle generation (those born on the ship who will never see origin or destination) but less often on the political structure question: who holds authority in a closed system with no external enforcement?

Story-relevant cautions:
  1. If the story uses STL, the absence of rescue, reinforcement, or external authority is a structural feature, not a detail — it changes what kinds of conflict are possible.

Anti-plagiarism note: Structural patterns described above are generalised across a body of SF works. No specific characters, imagery, dialogue, plots, or named worldbuilding inventions from any specific work were reproduced. The pattern descriptions are functional — they describe logical implications, not creative content.

Further questions:
  1. What is the political structure of the origin civilization that sent the ship — and does the story care about that civilization's fate?
  2. What happens to authority when the original mission parameters become impossible or obsolete?
  [continues]
```

**Output shape (JSON `artifacts`):**
```json
{
  "domain_type": "speculative_fictional",
  "research_question": "What are the structural patterns in how science fiction has handled the social and political consequences of faster-than-light travel — specifically how FTL shapes the plausibility of interstellar empires, communication lag, and individual experience of distance?",
  "domain_summary": "FTL in science fiction is rarely just a transportation mechanism—it is a political enabling technology. The structural pattern across the genre is that FTL travel tends to be used to make interstellar empire plausible, as you cannot maintain a coherent, centralized empire across light-years without near-instantaneous communication and travel. The interesting tension in the genre lies between the massive scale FTL enables and the human-scale stories that require intimacy and consequence. When FTL is removed (such as in slower-than-light or generation ship narratives), the political and social structures must fundamentally change to account for isolation, irreversible commitment, and the breakdown of external authority.",
  "key_structural_facts_or_patterns": {
    "empire_and_communication": "Works that grant FTL travel almost always grant FTL communication. The few that separate the two (e.g., faster travel than communication, or vice versa) generate distinct political structures. Polities that can move armies faster than they can send orders create fundamentally different, highly decentralized command structures.",
    "the_cost_structure_of_ftl": "The most generatively interesting SF treatments attach specific costs to FTL—not just fuel, but cognitive, psychological, or biological costs that create character pressure. The absence of cost tends to produce empire stories that feel politically thin.",
    "slower_than_light_as_a_structural_choice": "Works that deliberately choose STL over FTL tend to generate stories about the experience of irreversible commitment, the divergence of cultures over generations, and the psychology of people who will never see the destination."
  },
  "useful_specifics": "A recurring structural innovation in STL stories is the 'mutiny of the middle generation'—the political crisis that occurs when the generation born on the ship, who never chose the mission and will never see its completion, realizes they are merely maintenance workers for their ancestors' dreams.",
  "what_is_commonly_misrepresented": [
    "FTL communication is often treated as functionally identical to FTL travel, and the massive political implications of instantaneous information transfer are rarely examined rigorously.",
    "STL generation ship stories often focus on the psychological angst of the middle generation but gloss over the hard political structure question: who holds the monopoly on violence in a closed system with no external enforcement?"
  ],
  "story_relevant_cautions": [
    "If the story uses STL, the absolute absence of rescue, reinforcement, or external authority is a structural feature, not a background detail. It fundamentally changes what kinds of conflict are possible and how they must be resolved."
  ],
  "anti_plagiarism_note": "Structural patterns described above are generalised across a broad body of SF works (including generation ship and space opera subgenres). No specific characters, imagery, dialogue, plots, or named worldbuilding inventions from any specific work were reproduced. The pattern descriptions are purely functional, describing logical implications rather than creative content.",
  "further_questions": [
    "What is the political structure of the origin civilization that sent the ship, and does the story actually care about that civilization's fate?",
    "What happens to the ship's internal authority when the original mission parameters become impossible or demonstrably obsolete?",
    "How is the history of the origin world taught to the middle generation, and who controls that curriculum?"
  ]
}
```

---

## Example C — Hybrid domain

**Input shape:**
```
Domain type: Hybrid
Question: How have both historical pandemics and science fiction / fantasy plague narratives handled the disintegration of social institutions — what structural patterns recur, what does fiction amplify or distort relative to historical reality?
Story context: A fantasy world experiencing a magical plague whose mechanism is unknown; interested in how social trust, religious authority, and governance actually collapse (or don't) under pandemic pressure.
```

**Output shape:** Sections structured to cover both the historical factual record and the fictional precedent landscape in parallel, with explicit comparison of where they diverge and what each offers. Anti-plagiarism note applies to the fictional portion.
