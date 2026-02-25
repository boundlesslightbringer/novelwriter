---
name: layering-history-and-legend
description: Weaves backstory, in-world songs, legends, ruins, artifacts, and conflicting historical accounts into a completed scene or chapter draft through the natural filter of the POV character's knowledge and cultural context. Invoked after Scene Construction and POV Consistency Maintenance have cleared the draft. Outputs a revised draft with history and legend integrated. Does not introduce new plot events or create new history not already in the World Bible.
---

# Layering History and Legend

## Identity

**Skill name:** `layering-history-and-legend`
**Purpose:** The past is not backstory — it is a living pressure on every scene. This skill integrates that pressure into prose that has already been written and cleared for POV consistency: the ruins that are visible from this window, the song one of these characters half-remembers, the contested legend that the two cultures in the room interpret differently, the artifact on the table whose significance the POV character partially understands. None of this is delivered as information. It enters the scene through the filter of what this specific character knows, misremembers, was taught, and believes — and it serves the scene's existing conflict, not a worldbuilding agenda.

---

## Core

Weave backstory, in-world songs, legends, ruins, artifacts, and conflicting historical accounts into existing prose through the natural filter of the POV character's knowledge and cultural context. Operate on completed, POV-consistent scene or chapter drafts only. Do not introduce new plot events. Do not create new history not already in the World Bible. Output a revised draft with history and legend integrated.

---

## Input

The main agent provides:

1. **Completed scene or chapter draft** — a draft that has already passed POV Consistency Maintenance (and Conflict Layering, if that was invoked). The draft is the base material; the skill adds to it without removing or altering its existing events, choices, or consequences.

2. **World Bible excerpt — Module 3.4 (History & Legends):** The relevant records — specifically those whose physical remnants, believed accounts, or factional interpretations intersect with this scene's location, characters, or active themes. The main agent passes only the records relevant to this scene, not the full Module 3.4. Key fields per record: event name, true account (if known), believed account (what characters generally believe), factional interpretations (how different cultures or factions remember it differently), physical remnants (ruins, artifacts, locations), and story significance.

3. **World Bible excerpt — Module 3.3 (Cultures, Customs & Religion):** The relevant cultural records — specifically the cultures represented by characters in the scene, including their core values, customs, religious beliefs, and relationship to history and legend. The POV character's cultural lens shapes which histories they know, how they interpret them, and what weight they give to legend versus documented account.

4. **World Bible excerpt — Module 1.2 (Character Knowledge Matrix):** What the POV character currently knows, suspects, believes, and does not know. This is the epistemic constraint on history integration: the POV character can only know, misremember, or wonder about historical and legendary material that is consistent with their knowledge state. They cannot reveal, reference, or be affected by historical facts that Module 1.2 records them as not having.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Revised draft** — the complete scene or chapter draft with history and legend integrated. The output is prose, not an annotation of changes. The revised draft is ready to proceed to the next step (Self-Editing and Refinement, or POV Consistency Auditing if this is the chapter's final pass).

The integration is:
- **Organic** — history and legend enter through the scene's existing material: what the POV character notices in the environment, what a piece of dialogue triggers in their memory, what a physical object makes them think of, what they were taught versus what the other character in the scene was taught.
- **Filtered** — all historical content passes through the POV character's specific knowledge state (Module 1.2), their cultural lens (Module 3.3), and their voice profile. The narration never becomes a neutral history lecture.
- **Functional** — integrated history serves the scene's existing conflict, character dynamics, or stakes. It does not pause the scene for worldbuilding. If a legend is referenced, it is because it resonates with what the characters are experiencing or deepens the reader's understanding of the scene's underlying tension.
- **Iceberg-consistent** — the amount of history visible on the page is the tip. The integration should create the sense that a much larger historical reality exists beneath the surface of the scene. Do not deliver all available historical content; deliver what the scene absorbs naturally.

---

## What May Be Integrated

### Ruins, locations, and physical remnants

Physical remnants of history that exist in the scene's location — a wall built by a culture that no longer exists, a room that was once something else, a skyline that is missing what it used to have. These enter through the POV character's perception of the physical space: they notice the remnant, and their noticing carries their knowledge or ignorance of what it means.

Not every scene has a historically significant physical setting. This category applies only when the scene is set in a location with a Module 3.4 physical remnant record.

### Artifacts and objects

Objects with historical, cultural, or legendary significance that are present in the scene. Weapons, tools, garments, documents, ritual objects, gifts. They enter through the POV character's perception of the object and whatever knowledge or association they have with it.

The POV character's relationship to an object's history is filtered by their culture (Module 3.3) and their knowledge state (Module 1.2). A character may know an artifact's significance and treat it with appropriate weight; a character from a different culture may not recognise it at all; a character may misidentify it and carry an incorrect interpretation. All three are valid integrations. The false identification must be consistent with Module 1.2's BELIEVE (possibly false) records or with reasonable ignorance given the character's cultural background.

### Legends and oral traditions

Stories that exist in the world — in-world myths, founding legends, cautionary tales, stories about specific places or objects or bloodlines. They enter through the scene's active material when the scene's events rhyme with a legend's structure, when one character references a legend the other interprets differently, or when a physical setting has a legendary resonance.

The power of in-world legends is that different characters know different versions. Two characters from different cultures or factions in the same scene may reference the same event with entirely different interpretations — and neither may know the true account (if Module 3.4 records one). This tension between interpretations, rendered within a scene, is one of the richest forms of history integration.

### In-world songs, sayings, and oral literature

Brief fragments — a line from a song, a proverb, a saying — that one of the scene's characters might reach for in this moment. These must be consistent with the POV character's cultural background (Module 3.3) and must serve the scene's current emotional or thematic content. A character who is about to do something that violates their culture's core values may hear a fragment of their culture's oral tradition rising in their mind unbidden — not because the plot needs it, but because that is how cultural formation actually works under pressure.

Songs and sayings are fragments only. This skill does not write complete in-world songs or poems unless they are already recorded in Module 3.4. If a song exists in Module 3.4, a line or phrase may be cited; never reproduced in full unless the scene requires the full text and the cultural context makes the recitation in-scene plausible.

### Conflicting historical accounts

When two characters in a scene come from different cultures or factions, they may carry incompatible versions of the same historical event — because Module 3.4 records multiple factional interpretations. This is the most structurally powerful form of history integration: the conflict between interpretations mirrors or amplifies the scene's existing interpersonal conflict. It does not need to be made explicit — the POV character noticing that the other character's reference to a historical event carries a different meaning than the meaning they were taught is sufficient.

### Backstory

Character-specific backstory — specific formative events, remembered experiences, the texture of the past that has produced the person now in the scene. Backstory enters through specific memory triggers in the scene's present material: a smell, a sound, a word, a gesture by another character that resonates with something in the POV character's personal past. Backstory is always specific and always brief; a memory intrusion should be a sentence or two, not a scene-within-a-scene. The past is a pressure on the present; it is not the present.

---

## What May Not Be Integrated

- **New historical events not recorded in Module 3.4.** This skill works only with established World Bible content. If relevant history is absent from Module 3.4, the main agent must first update the World Bible; the skill cannot create history.
- **New plot events.** The revised draft may not contain events — actions, revelations, choices, consequences — that were not in the base draft. Integration adds texture and depth to existing material; it does not advance the plot.
- **Exposition blocks.** History is never delivered as an information dump, regardless of how it is framed. A character's internal monologue summarising a historical event for the reader's benefit is exposition; it must not appear. History enters through observation, fragment, association, and implication — not through summary.
- **Corrected false beliefs.** If Module 1.2 records the POV character as believing something historically false (a BELIEVE status), the integration must honour that false belief. The character does not receive accurate historical information through the act of integration. The skill does not resolve the character's historical ignorance; it works within it.
- **Voice violations.** All integrated material passes through the POV character's established voice profile. If a historical reference would require a vocabulary or sentence structure inconsistent with the voice profile, it must be adapted or excluded.

---

## The Filter — How History Enters Prose

Every integrated element must pass through the same filter:

**Filter test:** *Would this specific POV character, in this specific moment, given what they know and what they are experiencing, notice, remember, reference, or be affected by this historical element — and if so, how?*

The filter has three components:

1. **Situational trigger:** What in the scene's current material — the physical setting, the conversation, another character's behaviour, the POV character's own action — activates the historical element? There must be a specific trigger. History does not arise from nowhere; it is called up by something present.

2. **Epistemic consistency:** Does the POV character have access to this historical knowledge? Module 1.2 and Module 3.3 (their cultural background) define the boundaries. They know what people from their background typically know; they do not know what their background did not teach them; they believe what their background taught them, even if it is false.

3. **Processing register:** How does this character experience historical memory? Some characters carry history analytically — they note the evidence and make inferences. Some carry it emotionally — the past surfaces as feeling before it surfaces as fact. Some carry it as cultural habit — proverbs and formulas that arise without full conscious recall. The voice profile specifies this; the integration must match it.

---

## Boundary

- **Operates on completed, POV-consistent scene or chapter drafts only.** Does not run on drafts that have not passed POV Consistency Maintenance.
- **Does not introduce new plot events.** The scene's structure — its goal, obstacle, choice, consequence — is fixed before this skill is invoked. Integration adds to the prose's texture and depth; it does not change what happens.
- **Does not create new history.** All historical and legendary content must already exist in Module 3.4. If the main agent wants to integrate history that is not yet in the World Bible, Module 3.4 must be updated first.
- **Does not write complete in-world songs, poems, or extended oral texts** unless these already exist in Module 3.4 and the scene warrants full citation.
- **Does not update the World Bible.** Output is a revised draft returned to the main agent. The main agent notes any new chapter references in Module 3.4's "Referenced in chapters" field.
- **Does not correct false historical beliefs.** The POV character's epistemic state is honoured as-is.

---

## Invocation

The main agent invokes Layering History and Legend:

- After a scene or chapter draft has passed POV Consistency Maintenance (and Conflict Layering, if that was invoked).
- Not after every scene — only when the scene's location, characters, or active themes intersect with relevant Module 3.4 material. Many scenes do not require this pass.
- Not before Scene Construction or POV Consistency Maintenance. History integration happens after the scene's core prose is sound.
- At the chapter level when the main agent judges that the completed chapter would benefit from a unified history integration pass rather than scene-by-scene passes.

**Standard post-scene-construction sequence when applicable:**  
`Scene Construction → POV Consistency Maintenance → [Conflict Layering if needed] → Layering History and Legend → Self-Editing and Refinement`

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Reads from** (as excerpts provided by main agent) | Module 3.4 (History & Legends — relevant records), Module 3.3 (Cultures, Customs & Religion — cultures represented in the scene), Module 1.2 (Character Knowledge Matrix — POV character) |
| **Main agent writes to** | Nothing — revised draft is returned to the main agent; the main agent may update Module 3.4's "Referenced in chapters" field to note where historical records have been cited in the prose |

---

## Dependencies

**Upstream:** Scene or chapter draft must have passed **POV Consistency Maintenance**. Module 3.4, 3.3, and 1.2 must be current.
**Downstream:** Revised draft proceeds to **Self-Editing and Refinement** (and ultimately **POV Consistency Auditing** at the chapter level). The revised draft replaces the base draft as the version of record.

---

## Instructions

### Step 1 — Read the base draft with the historical record in view

Read the scene or chapter draft. Simultaneously, read the relevant Module 3.4 records and the relevant Module 3.3 cultural records.

Do not begin integrating immediately. First, map the intersections: where in the draft's existing material does history already press on the scene, even implicitly? Where is the setting physically located within historical space? Which characters carry which cultural backgrounds? What is the scene's active conflict — and which historical events or legends resonate structurally with that conflict?

Make a mental map of integration opportunities before writing a word.

### Step 2 — Apply the filter to each candidate element

For each historical element that intersects with the scene, apply the three-component filter:

*Situational trigger:* What in the scene's present material would activate this element? If there is no specific trigger — no moment where the physical setting, the conversation, or the character's action would naturally call this history up — do not integrate it here. Leave it for a scene where the trigger is organic.

*Epistemic consistency:* Does the POV character have access to this knowledge given Module 1.2 and their Module 3.3 cultural background? If they do not know this history, they cannot reference it directly — but they may notice the physical remnant without knowing what it is, or they may misidentify the artifact according to their own culture's interpretation.

*Processing register:* How would this character experience this historical element — analytically, emotionally, as cultural habit? The integration must match their voice profile.

Rank the candidate elements: which integrations are organic (the scene would be richer for them, and the trigger is clear and natural), which are marginal (plausible but not compelling), and which are forced (no organic trigger)? Integrate only the organic ones. The iceberg principle applies: most of the history stays beneath the surface.

### Step 3 — Integrate physical remnants and setting

If the scene's location has historical significance recorded in Module 3.4, integrate this through the POV character's perception of the physical space. The character notices something — a feature of the room or landscape — and their noticing carries whatever knowledge or ignorance they have about it.

A character who knows the history: notices the feature, understands its significance, perhaps has a complex relationship with what it represents for their culture or faction.

A character who does not know the history: notices the feature as a feature, perhaps finds it strange or striking, does not understand what it is. The reader, holding Module 3.4, may understand what the character does not. This is one form of the history's iceberg — the reader sees more than the character.

Keep setting-based history brief. One or two sentences. A detail in the world, noticed, not explained.

### Step 4 — Integrate artifacts and objects

If an object with Module 3.4 significance is present in the scene, integrate its history through the POV character's relationship to the object: what they know about it, what they believe about it (which may be false), what it makes them think.

If two characters in the scene have different cultural relationships to the object — if Module 3.3 records different cultural interpretations — render the POV character's relationship and, if possible, let the asymmetry surface in the scene's existing interaction without resolving it. Two people in the same room with the same object, carrying incompatible understandings of what it means, is stronger than any exposition about the object's history.

### Step 5 — Integrate legend, oral tradition, and conflicting interpretations

If the scene's active conflict or character dynamics rhyme with a Module 3.4 legend, and if the POV character's cultural background gives them access to some version of it, integrate through association or reference — not through summary.

The character does not think, "This reminds me of the legend of X, which says Y." They experience the resonance more obliquely: "Something in the way this was going reminded him of a story he'd been told as a child, though the story ended worse." Or another character references the legend from their factional interpretation, and the POV character registers that the reference means something different in their own tradition.

Conflicting interpretations are most effective when rendered without resolution — the reader understands that there are two versions, the characters do not acknowledge it because to them it is simply what happened, and the tension between the interpretations adds to the scene's existing interpersonal conflict without requiring explanation.

### Step 6 — Integrate backstory through specific memory

If a moment in the scene's present material — a sensory detail, a word, a gesture — provides a genuine trigger for a relevant character backstory element, integrate a brief, specific memory intrusion.

Brief means: one or two sentences. Specific means: a particular image or moment from the past, not a summary of a period or a relationship. The past arrives as a flash and recedes; it does not become the scene's dominant material.

The memory must serve the scene's current content — it deepens the character's response to the present moment; it does not replace the present moment with a past one.

### Step 7 — Review the integrated draft for organic quality

Read the complete revised draft. For each integrated element, ask:

- Does the integration feel like the character's natural perception and memory, or does it feel like a planted worldbuilding note?
- Did the history stop the scene — did the reader have to pause the scene's forward movement to receive historical information?
- Is the integrated element consistent with Module 1.2's knowledge state and Module 3.3's cultural record?
- Did any integration create a new plot event that was not in the base draft?

Remove or rewrite any integration that fails these tests. An unintegrated element is better than a forced one.

### Step 8 — Return the revised draft

Return the complete revised draft to the main agent. The prose is the output — no annotation of what was changed, no structural notes. If any Module 3.4 records were cited for the first time in this draft, note this briefly so the main agent can update the "Referenced in chapters" field.

---

## Example

### Input shape

```
Base draft excerpt (Caradhen POV, meeting with Vara in the old solar of the
Thornback hall):

  The solar had one door and three windows, and Vara had seated herself where
  she could see all of them.
  [... scene continues ...]
  He watched her right hand. Her right hand did not move.
  "That isn't what I asked," she said, pleasantly.
  "No," he said. "It isn't."

Module 3.4 excerpt (relevant records):
  Event: The Thornback Compact.
  Believed account: A truce signed in this hall, in the solar now used for
    private meetings, that ended thirty years of border war between Caradhen's
    ancestors and the kingdom to the south.
  Factional interpretation — Thornback clans: The Compact was the last act
    of a great lord who understood that survival requires knowing when to stop
    fighting.
  Factional interpretation — kingdom historians: The Compact was a surrender
    dressed as diplomacy; the Thornback clansmen were exhausted and had no
    choice.
  Physical remnants: The table in the solar is the original treaty table.
    The document itself is gone; only the table remains.

Module 3.3 excerpt (Thornback culture):
  Core values: Survival; the preservation of the passes; loyalty to kin over
    loyalty to cause.
  Relationship to history: History is preserved as oral tradition and
    practical lesson, not written record. The Thornback do not write their own
    history; it is carried in memory and in objects.

Module 1.2 (Caradhen):
  KNOWS: This is the treaty table. His father told him the story.
  BELIEVES (possibly false): The Compact was a great act of strategic wisdom.
  DOES NOT KNOW: Kingdom historians interpret the Compact as a surrender.
```

### Output shape (revised excerpt)

```
The solar had one door and three windows, and Vara had seated herself where
she could see all of them.

He had not offered her any other chair. There were three in the room. She
had chosen the one that faced the door. He filed this.

The table between them was old — older than the hall as it currently stood,
older than his father's father. The grain of the wood had the specific
smoothness of a surface that had been touched ten thousand times by hands that
knew what it was. His father had told him: this is where the Compact was
signed. He had been seven. He had put his hand flat on the table to see if
he could feel it.

He still thought about that sometimes — the seven-year-old's idea that
history was something you could put your hand on.

[... scene continues unchanged ...]

He watched her right hand. Her right hand did not move.

"That isn't what I asked," she said, pleasantly.

"No," he said. "It isn't."

He looked at the table. His ancestor had sat at this table and understood,
his father said, when to stop fighting. He was not sure, anymore, that
"stop fighting" and "surrender" were as different as the story had insisted.
```

---

## Quality Checks

Before returning the revised draft, verify:

- [ ] Every integrated element has a specific situational trigger — it is not inserted, it is called up by something in the scene.
- [ ] Every integrated element passed the epistemic consistency check against Module 1.2 — the POV character only knows what Module 1.2 and their cultural background give them access to.
- [ ] False historical beliefs (BELIEVE status in Module 1.2) are honoured — the character carries their false version, not the true account.
- [ ] No exposition blocks — history enters as observation, fragment, association, or implication; never as summary delivered for the reader's benefit.
- [ ] No new plot events introduced — the scene's structure (goal, obstacle, choice, consequence) is unchanged.
- [ ] All integrated material passes through the POV character's voice profile — vocabulary, rhythm, processing register all consistent.
- [ ] Integration is selective — not all available Module 3.4 material is used; only what the scene organically absorbs.
- [ ] The scene's forward movement is not stopped by any integrated element.
- [ ] No new history created outside Module 3.4 records.
- [ ] No World Bible writes specified.
