---
name: consequence-cascade-implementation
description: >
  Projects, structures, and records the full consequence cascade of a major story event.
  For every significant event — a death, a betrayal, a battle, a revelation, a broken oath —
  this skill traces immediate, short-term, and long-term consequences across all affected
  characters and relationships, and identifies any time-delayed consequence bombs to be
  planted in the ledger. Each bomb is assigned a condition-based detonation trigger, a
  narrative phase anchor, and a priority tier (Essential / Enriching / Unclassified) so the
  main agent knows which bombs must fire before the story ends and which enrich it if they do.
  Essential bombs are registered in both Module 4.2 and Module 2.4 so Plot Thread Tracking
  can surface them during convergence. The main agent invokes this skill immediately after a
  major event occurs in the draft, before writing the next scene.
---

# Skill: Consequence Cascade Implementation

## Identity

**Skill name:** Consequence Cascade Implementation  
**Group:** 5 – Consequence & Realism  
**Subagent:** Consequence Subagent  
**When to invoke:** Called by the main agent immediately after a major event is written — a death, a decisive battle, a betrayal, a secret revealed, a power shift, a broken vow, or any action that materially changes one or more characters' situations. Must be run before the next scene is drafted, so the consequence record is available to Gardener Plotting System and Scene Construction.

---

## Core

For each major triggering event, project and record the full consequence cascade:

1. **Immediate consequences** — what changes in the very next scene or within the same chapter.
2. **Short-term consequences** — what unfolds across the next several chapters.
3. **Long-term consequences** — what is set in motion but will not resolve until much later (consequence bombs).

All consequences are traced across every affected character and every affected relationship pair. Each consequence bomb is assigned a **condition-based detonation trigger** (the story event or character situation that causes it to fire, not a chapter number), a **narrative phase anchor** (the structural phase in which detonation is expected — early, mid, convergence, or final act), and a **priority tier** (Essential, Enriching, or Unclassified) that tells the main agent whether the bomb must detonate before the story ends.

Essential bombs are registered in both Module 4.2 (Consequence Ledger) and Module 2.4 (Pending Payoffs & Foreshadowing), making them visible to Plot Thread Tracking during convergence-phase sweeps. Enriching bombs are registered in Module 4.2 only.

The output is a structured consequence record that the main agent uses to update World Bible Modules 4 and, for Essential bombs, Module 2.4.

---

## Input

The main agent provides:

| Input | Description |
|---|---|
| **Triggering event description** | Plain-language description of what happened — the act itself, the outcome, and the chapter reference where it occurred. |
| **Module 1.1 excerpt** | Character Directory entries for all characters directly or indirectly affected by the event — current psychological state, desires, fears, arc type, arc stage. |
| **Module 1.3 excerpt** | Relationship Records for all affected character pairs (directional) — valence, power balance, history, active secrets. |
| **Module 4.1 excerpt** | Existing Event → Consequence Chains — so this skill can identify if the new event is a downstream consequence of an existing chain (enabling cascade linkage) or a new chain root. |

The main agent must determine which characters are "affected" before invoking this skill. A character is affected if: they witnessed the event, they are directly named in the consequence, they held a relationship with a character who was killed or transformed, or they are likely to act on new information the event creates.

---

## Output

A structured consequence cascade record, ready for the main agent to write into World Bible Module 4. The record has three parts:

### Part 1: Event → Consequence Chain (Module 4.1 entry)

```
Triggering event: [description + chapter reference]

Immediate consequences (already played out or plays out in current/next scene):
  - [Character A]: [what changes for them immediately]
  - [Character B]: [what changes for them immediately]
  - [Relationship pair A↔B]: [how this relationship shifts immediately]

Short-term consequences (projected for next N chapters):
  - [Character A]: [what is now in motion for them]
  - [Character B]: [what is now in motion for them]
  - [Political/world state]: [if applicable]

Long-term consequences (flagged as pending — to be written later):
  - [Character A]: [what this eventually leads to]
  - [World-level]: [if applicable]

Affected characters: [list]
Cascade chain ID: [new chain ID, or reference to existing chain if this is a downstream link]
```

### Part 2: Time-Delayed Consequence Bombs (Module 4.2 entries; Essential bombs also to Module 2.4)

For each long-term consequence that is not yet written, one record:

```
Planted event: [what was set in motion + chapter reference]
Nature of future consequence: [what will eventually happen]
Detonation trigger: [the story condition or character situation that causes this to fire —
  e.g., "when Mira directly confronts Harren with the forged correspondence" or
  "when Cavan is forced to choose a side publicly"]
Narrative phase anchor: [early / mid / convergence / final act — loose structural estimate]
Priority tier: [Essential / Enriching / Unclassified]
  Essential = the story's thematic or emotional resolution requires this to detonate before the ending.
  Enriching = adds resonance and depth if it fires; the story closes satisfactorily without it.
  Unclassified = consequences are clear but story-level necessity is not yet determinable;
    revisit at the convergence-phase sweep.
Status: Armed
Dual-register: [Yes — write to Module 2.4 as well / No — Module 4.2 only]
  (Yes for Essential; No for Enriching and Unclassified)
```

**On writing Essential bombs to Module 2.4:** The main agent writes Essential Armed bombs as Pending Payoff entries in Module 2.4 with type "Consequence bomb" and the same detonation trigger and narrative phase anchor. This makes them visible to Plot Thread Tracking's convergence-phase sweep without any skill-to-skill dependency. The Module 4.2 record remains the authoritative consequence record; the Module 2.4 entry is the convergence-tracking hook.

### Part 3: Cascade Chain Record (Module 4.3 entry — new or updated)

If this event is a new chain root:
```
Chain ID: [new unique ID]
Chain sequence: [Event] → [Immediate consequence] → [Short-term consequence] → [Long-term consequence]
  Each link is described as a condition or story event, not a chapter number.
  e.g.: "Harren's accusation" → "Mira's isolation" → "Mira finds the correspondence"
    → "Harren is exposed and destroyed"
Current position: [Event / Immediate consequence]
Remaining links: [Short-term and long-term consequences not yet written, stated as conditions]
Characters involved: [all affected characters]
```

If this event is a downstream link in an existing chain, the skill returns updated `Remaining links` and `Current position` fields for the main agent to patch into the existing Module 4.3 record.

---

## Step-by-Step Instructions

### Step 1: Parse the Triggering Event

Read the triggering event description. Identify:
- What specifically changed in the world (a person died, power shifted, a secret was revealed, an alliance broke, etc.)
- Who was present and who will learn of it.
- What was irrevocably altered vs. what is temporarily disrupted.

Name the event concisely (e.g., "Assassination of Lord Varen at the Red Feast, Ch. 14").

### Step 2: Identify All Affected Characters

Using Module 1.1 and 1.3 excerpts, enumerate every character who:
- Was present at the event.
- Holds a recorded relationship with a character directly affected.
- Will learn of the event through information channels already established.
- Has an active desire, fear, or goal that this event directly advances, blocks, or transforms.

Do **not** speculate about characters with no recorded connection to the event. Affect only those in the Module 1.1 and 1.3 excerpts provided.

### Step 3: Trace Immediate Consequences (Character by Character)

For each affected character, apply the **desire → action → consequence** model:
- What did they want before this event?
- What has this event taken from them, given them, or forced them to confront?
- What is the first thing they will do or feel in the immediate aftermath?

For each affected relationship pair (from Module 1.3):
- Has the valence shifted (alliance → enmity, trust → suspicion)?
- Has a secret been exposed or a power balance altered?
- Record directional changes (Character A's view of Character B may change differently from B's view of A).

### Step 4: Project Short-Term Consequences

Extend the cascade across the next several chapters. Ask for each character:
- What action does the immediate consequence compel?
- What does that action collide with (other characters' plans, world state, active plot threads)?
- What new conflicts or opportunities does this create?

Short-term consequences should be concrete and plausible, not vague. "Aemond will seek revenge" is insufficient. "Aemond will move to consolidate control of the eastern garrison before the news reaches his brother's allies — creating a three-chapter window where Daemon must decide whether to strike first or negotiate" is a short-term consequence.

### Step 5: Identify Consequence Bombs (Long-Term) and Assign Priority

Long-term consequences are those that will not be dramatised for many chapters but are set in motion by this event. They are planted now so they cannot be forgotten.

For each long-term consequence identified:

**5a. Define the detonation trigger as a story condition, not a chapter number.**
The novel's length is unknown. Chapter numbers make bombs fragile — the story may end before they arrive, or its pacing may shift so that the estimated chapter is wrong by ten chapters. Instead, state the trigger as a narrative condition: the event or character situation that *causes* the bomb to fire.

- Weak (chapter-anchored): *"Estimated detonation window: Ch. 22–25."*
- Strong (condition-anchored): *"Detonates when Cavan is publicly forced to choose a side — the moment when silence is no longer possible."*

The condition should be specific enough to be recognisable when it arrives but robust enough to survive pacing changes. If a rough narrative phase is useful as a secondary anchor, add it (early / mid / convergence / final act) — but it is supplementary, not primary.

**5b. Assign a priority tier.**

Ask: *If the story ended without this bomb detonating, would the ending feel incomplete, or merely less rich?*

- **Essential:** The story's thematic or emotional resolution genuinely depends on this bomb firing. A reader who has been tracking this thread would feel the ending was unfinished if it did not resolve. These bombs must find a scene before the story closes.
- **Enriching:** The bomb adds resonance, depth, or earned texture if it fires. The story's main arc closes satisfactorily without it. These bombs should fire if opportunity permits, but their absence is not a structural failure.
- **Unclassified:** The consequences are clear, but whether they are load-bearing for the ending cannot be determined at this point in the story. Mark as Unclassified and flag for reassessment at the convergence-phase sweep.

When in doubt between Essential and Enriching, ask: *Is this bomb connected to the story's core conflict question (from the endpoint compass)?* If yes, lean Essential. If it deepens a subplot or enriches a secondary character arc, lean Enriching.

**5c. Register Essential bombs in both Module 4.2 and Module 2.4.**
Essential Armed bombs must be written to Module 2.4 (Pending Payoffs & Foreshadowing) as entries with type "Consequence bomb." This makes them visible to Plot Thread Tracking's convergence-phase sweep. The main agent performs this dual write. Enriching and Unclassified bombs are registered in Module 4.2 only.

**5d. Flag each bomb in the cascade chain as a "Remaining link."**

Examples of consequence bomb types by priority:

| Type | Example | Likely tier |
|---|---|---|
| Withheld knowledge that surfaces under pressure | A character who witnessed a betrayal stays silent — but this will surface when they are cornered | Essential if the betrayal is the story's core conflict; Enriching if it is a subplot |
| Political ripple from a distant death | A death's consequences take many chapters to reach a far house | Often Enriching unless that house is central to the ending |
| Psychological wound manifesting under stress | A wound (physical, psychological) that does not manifest until a character is at their limit | Essential if this defines their arc resolution |
| Debt created by a forced choice | A character's decision will be held against them by whoever loses the conflict | Priority depends on whether the debt-calling is part of the climax |

### Step 6: Check for Cascade Chain Linkage

Before creating a new chain, check the Module 4.1 excerpt:
- Is this event already recorded as a "long-term consequence" or "short-term consequence" of a prior event?
- If so, this event is a downstream link in an existing chain. Update that chain's `Current position` and `Remaining links` rather than opening a new chain root.
- If this event is genuinely new (not downstream of anything recorded), open a new chain.

### Step 7: Assemble and Return the Consequence Record

Return the three-part output (Event → Consequence Chain, Time-Delayed Consequence Bombs, Cascade Chain record). The main agent writes these into World Bible Module 4.

---

## Boundary

This skill:
- **Does not write prose.** It produces structured data, not scenes.
- **Does not determine how consequences will be dramatised.** That is Gardener Plotting System's and Scene Construction's responsibility. This skill records what must happen; those skills determine how and in what scene.
- **Does not update the World Bible directly.** It returns structured records; the main agent performs all World Bible writes — including the dual-register write for Essential bombs.
- **Does not invoke other skills.** It does not call Gardener Plotting System, Scene Construction, Plot Thread Tracking, or Balancing Realism and Fantasy.
- **Does not speculate beyond the provided excerpts.** It works only from the character and relationship data the main agent supplies. It does not invent affected characters not present in the excerpts.
- **Does not resolve the consequences.** It maps what is now in motion. Resolution occurs in future chapters.
- **Does not use chapter numbers as primary detonation anchors.** Detonation triggers are always story conditions. A narrative phase label (early / mid / convergence / final act) may be added as a loose secondary anchor but never replaces the condition.
- **Does not make final determinations on priority tier when uncertain.** Unclassified is a valid tier. Priority is revisited by Plot Thread Tracking at convergence, not forced at planting time.

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Main agent reads and provides as excerpts** | Module 1.1 (Character Directory — all affected characters), Module 1.3 (Relationship Records — all affected pairs), Module 4.1 (existing Consequence Chains — to check for linkage) |
| **Main agent writes from this skill's output** | Module 4.1 (new or updated Event → Consequence Chain), Module 4.2 (all new Time-Delayed Consequence Bomb entries), Module 4.3 (new or updated Cascade Chain record), **Module 2.4 (Essential bombs only — registered as Pending Payoff entries with type "Consequence bomb" so Plot Thread Tracking can sweep them at convergence)** |

---

## Dependencies

**Upstream (what this skill consumes):**
- Scene Construction — this skill is invoked immediately after a major scene is drafted and a major event has occurred.
- Character Integration with Plot — the desire → action → consequence loops and relationship records it established are the foundation for consequence tracing here.

**Downstream (what consumes this skill's output):**
- The main agent updates Modules 4.1, 4.2, 4.3, and (for Essential bombs) Module 2.4 from this skill's output.
- Gardener Plotting System reads Module 4.1 when determining the next scene's parameters — the consequence record directly shapes what goals, obstacles, and choices are available.
- Scene Construction reads Module 4.1 (via Pending Payoffs) to embed foreshadowing.
- Plot Thread Tracking reads Module 2.4 during convergence-phase sweeps and will surface all Essential Armed bombs that have not yet detonated, flagging them for the main agent to schedule before the ending.
- Resolving Obstacles and Untangling Tangles reads active consequence chains when diagnosing a tangle.

---

## Example

### Input shape

```
Triggering event: Lord Harren's public accusation of Lady Mira before the assembled court — 
  claiming she passed troop movements to the river lords. Chapter 9.

Module 1.1 excerpts provided:
  - Lady Mira: desires restoration of her house's honor; fears public exposure of her 
    brother's debts; arc = fall and reinvention; currently in stage 2 of 4.
  - Lord Harren: desires full political dominance of the eastern council; fears his own 
    vulnerability if Mira can prove his accusation is fabricated; arc = antagonist.
  - Lord Cavan (Mira's ally): desires a quiet political life; fears being drawn into 
    open conflict; arc = bystander becoming participant.

Module 1.3 excerpts provided:
  - Harren → Mira: valence hostile; power advantage Harren; secret = Harren knows 
    about Mira's brother's debts; trajectory = escalating.
  - Mira → Cavan: valence allied; power roughly equal; secret = Cavan knows Mira 
    passed no information; trajectory = stable but fragile.
  - Cavan → Harren: valence neutral-fearful; power disadvantage Cavan.

Module 4.1: No existing chain involving Mira or Harren found.
```

### Output shape

**Part 1: Event → Consequence Chain**
```
Triggering event: Harren's public accusation of Mira, Ch. 9.

Immediate consequences:
  - Lady Mira: social standing suspended; allies will not speak for her publicly until 
    the accusation is answered; access to court resources restricted.
  - Lord Cavan: forced to choose silence (safety) or testimony (risk); either choice 
    is now costly where before it cost him nothing.
  - Harren → Mira: relationship moves from hostile-covert to hostile-public; Harren 
    has committed to destruction rather than leverage.
  - Mira → Cavan: Mira will need Cavan's testimony; Cavan now holds power over her 
    that he did not hold before.

Short-term consequences:
  - Mira must either find proof of fabrication or mount a counter-accusation — 
    compelling her to seek her brother's hidden correspondence (3–4 chapter arc).
  - Cavan must decide within one chapter whether to testify; delay will be read as 
    guilt-by-association by Harren's faction.
  - Harren's public commitment makes private negotiation with Mira impossible; 
    he must destroy her or be exposed as a fabricator — no middle path.

Long-term consequences (flagged as pending):
  - If Mira survives this: Harren becomes permanently vulnerable to her. 
    The power balance inverts.
  - Cavan's choice here defines his arc for the remainder of the novel.

Affected characters: Lady Mira, Lord Harren, Lord Cavan.
Cascade chain ID: CC-009 (new chain).
```

**Part 2: Consequence Bombs**
```
Bomb 4.2-A:
  Planted event: Harren's public overcommitment, Ch. 9.
  Nature: If Mira finds the forged correspondence, Harren is destroyed —
    not merely checked. The evidence will exist for multiple chapters before surfacing.
  Detonation trigger: When Mira directly confronts Harren with the forged correspondence
    in a public or semi-public setting where he cannot suppress it.
  Narrative phase anchor: Convergence phase.
  Priority tier: Essential — the story's central conflict (Harren's destruction or Mira's)
    cannot resolve without this bomb firing. If it does not detonate before the ending,
    the Mira/Harren arc has no resolution.
  Status: Armed.
  Dual-register: Yes — write to Module 2.4 as Pending Payoff (type: Consequence bomb).

Bomb 4.2-B:
  Planted event: Cavan's moment of forced choice, Ch. 9–10.
  Nature: Cavan's decision (silence or testimony) will be held against him
    by whoever loses this conflict — creating a debt that will be called in
    when Cavan least wants to pay it.
  Detonation trigger: When the losing party (Harren or Mira) has cause to act against
    Cavan and sufficient leverage to do so — i.e., after the Mira/Harren conflict resolves.
  Narrative phase anchor: Final act.
  Priority tier: Enriching — Cavan's debt adds earned weight to his arc's conclusion,
    but the main Mira/Harren story closes satisfactorily without it detonating.
    If the story's final act is structurally crowded, this bomb can be acknowledged
    in passing rather than dramatised as a full scene.
  Status: Armed.
  Dual-register: No — Module 4.2 only.
```

**Part 3: Cascade Chain**
```
Chain ID: CC-009
Sequence:
  Harren's public accusation (Ch. 9)
    → Mira's isolation and suspension of standing (immediate)
    → Cavan's forced choice: silence or testimony (next chapter)
    → Mira seeks her brother's hidden correspondence (multi-chapter search arc)
    → Mira confronts Harren with the forged correspondence [Bomb 4.2-A detonation trigger]
    → Harren is exposed and destroyed / power balance inverts
    → Cavan's debt is called in [Bomb 4.2-B detonation trigger]
Current position: Harren's public accusation (Ch. 9) — immediate consequences in play.
Remaining links: All links from "Cavan's forced choice" onward.
Characters involved: Lady Mira, Lord Harren, Lord Cavan.
```

---

## Glossary (Relevant Terms)

- **Desire → action → consequence:** The causal engine of all plot: character desire drives action; action produces consequences; consequences are tracked and honoured in future chapters. This skill maps the consequence leg of that loop.
- **Consequence ledger / cascade:** The recorded immediate, short-term, and long-term consequences of story events, including time-delayed "consequence bombs."
- **Consequence bomb:** A consequence set in motion now but detonating later — recorded at planting so it cannot be silently discarded. Detonation is defined by a story condition, not a chapter number.
- **Detonation trigger:** The story condition or character situation that causes a consequence bomb to fire — e.g., "when Mira confronts Harren with the forged correspondence." Condition-based triggers are robust to pacing changes; chapter-number anchors are not.
- **Narrative phase anchor:** A loose structural label (early / mid / convergence / final act) used as a secondary orientation point for a bomb's expected detonation. Supplementary to the detonation trigger, never a substitute for it.
- **Priority tier:** The classification of a consequence bomb's narrative necessity. Essential = must detonate before the story ends; Enriching = adds depth if it fires, not structurally required; Unclassified = revisit at convergence.
- **Dual-register:** The practice of writing Essential Armed bombs to both Module 4.2 (the authoritative consequence record) and Module 2.4 (Pending Payoffs), making them visible to Plot Thread Tracking's convergence-phase sweep.
- **Cascade chain:** A multi-step causal sequence: A causes B causes C causes D. This skill both opens new chains and extends existing ones.
