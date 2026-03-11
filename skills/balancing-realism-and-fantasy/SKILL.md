---
name: balancing-realism-and-fantasy
description: >
  Audits a completed chapter or flagged scene against the realism-fantasy calibration
  checklist — covering political realism, magic system consistency, violence framing,
  dark content justification, and tonal consistency. Returns a structured audit report
  with specific flags and recommended adjustments. The main agent invokes this skill when
  tone, magic use, or dark content has been flagged as a concern, or as a periodic audit
  after significant chapters. Does not rewrite; flags and recommends only.
---

# Skill: Balancing Realism and Fantasy

## Identity

**Skill name:** Balancing Realism and Fantasy  
**Group:** 5 – Consequence & Realism  
**Subagent:** Consequence Subagent  
**When to invoke:** Called by the main agent when any of the following is true:
- Tone in a completed chapter feels inconsistent with the established register.
- Magic is used in a way that may violate established system limits or inflate prevalence.
- A violent or dark scene has been drafted and needs calibration against justification criteria.
- The main agent has flagged a scene or chapter as a potential realism-fantasy balance concern.
- Periodic audit requested after a chapter of high consequence (major battle, large-scale magic, significant death).

This skill is an **audit tool**, not a writing tool. It is never invoked mid-scene.

---

## Core

Audit a completed chapter or flagged scene against five calibration dimensions:

1. **Political realism** — do power structures, faction behaviour, and human motivation follow plausible logic?
2. **Magic prevalence and consistency** — does magic use conform to established capabilities, limits, and costs?
3. **Violence framing** — is violence rendered with consequence and weight, not as spectacle?
4. **Dark content justification** — does darkness (cruelty, suffering, moral horror) serve the story, or is it gratuitous?
5. **Tonal consistency** — does the chapter's register match the novel's established tone?

Return a structured audit report with specific flagged passages and recommended adjustments. The main agent decides whether to act on the flags.

---

## Input

The main agent provides:

| Input | Description |
|---|---|
| **Chapter or scene draft** | The completed text to be audited. The main agent specifies whether this is a full chapter or a flagged scene excerpt. |
| **Module 3.5 excerpt** | Magic System State — confirmed capabilities, confirmed limits, confirmed costs, current prevalence, and recent magical events (with chapter references). |
| **Module 3.1–3.4 excerpt** | World State — political/power map, geography relevant to the scene, cultures/religion, history/legends as applicable to the content being audited. The main agent provides only the modules relevant to what the chapter contains; if no magic appears, Module 3.5 is not required. |
| **Tone reference (optional)** | A brief note from the main agent on the established tonal register, if not inferable from the World State excerpts — e.g., "the novel is operating in a low-fantasy, high-political-realism register." |

---

## Output

A structured **Balance Audit Report** with five sections — one per calibration dimension. Each section contains:
- **Status:** Pass / Flag / Concern (Pass = no issues; Flag = specific issue requiring attention; Concern = borderline, noted for awareness)
- **Flagged passages:** Specific text excerpts or line-level references where issues appear.
- **Description of the issue:** What specifically is miscalibrated and why.
- **Recommended adjustment:** A concrete editorial direction (not rewritten prose). The main agent decides whether to act.

If a dimension has no issues, the section is brief: Status = Pass, no further content.

The report closes with a **Priority Summary**: a ranked list of flags (high / medium / low priority) for the main agent's attention.

---

## Calibration Checklist: Five Dimensions

### Dimension 1: Political Realism

The political world of the story must behave according to plausible human logic — not genre convention and not authorial convenience.

Check for:
- **Faction behaviour:** Do political actors pursue their interests through means consistent with their established resources, alliances, and constraints? A lord with no army does not threaten war. A king with divided loyalties does not issue ultimatums he cannot enforce.
- **Information realism:** Do characters act on information they plausibly have? Do they fail to act on information they plausibly lack? Political actors should not have perfect knowledge of their enemies' intentions.
- **Consequence accountability:** Do political decisions carry realistic costs? Betrayals should create enemies. Public executions should produce fear and resentment, not just compliance. Marriages should create obligations, not just alliances.
- **Motivation plausibility:** Are characters pursuing power, safety, legacy, or survival through means proportionate to their situation? Flag characters who act against their established interests without sufficient explanation.
- **No genre shortcuts:** Flag any moment where a political outcome occurs because the plot requires it rather than because the characters' actions and the world's logic produced it.

### Dimension 2: Magic Prevalence and Consistency

Magic must remain internally consistent with the established system recorded in Module 3.5.

Check for:
- **Capability creep:** Does any magical act in this chapter exceed what Module 3.5 lists as "Confirmed capabilities"? If yes, flag — either the capability needs to be added to the record (escalation) or the act needs to be adjusted.
- **Limit violations:** Does any magical act contradict what Module 3.5 lists as "Confirmed limits"? This is a hard flag.
- **Cost evasion:** Is magic used without the recorded costs being paid or acknowledged? If the cost is injury, exhaustion, or sacrifice, the prose must show it.
- **Prevalence inflation:** Is magic appearing more frequently than the system's current prevalence level ("Rare / Increasing / Decreasing / Stable") would support? Multiple magical acts in a single chapter in a "Rare" system is a flag.
- **Unexplained phenomena:** If a new magical event occurs that cannot be explained by the current system, flag it as an "Unexplained phenomenon" for the main agent to decide whether it is intentional system expansion or a continuity error.
- **Reader disorientation:** Is magic used in a way that may confuse readers about what it can and cannot do, undermining the sense that the system has rules?

### Dimension 3: Violence Framing

Violence in the story is always consequential. It is never spectacle, never clean, and never cost-free.

Check for:
- **Weight and consequence:** Does each act of violence carry physical and psychological weight? A sword fight should leave exhaustion, injury, and psychological residue — not just a resolved situation.
- **Aftermath:** Is the aftermath of violence shown or acknowledged? A character who kills for the first time is not the same character afterward. A battle that kills hundreds should leave visible marks on the world.
- **Spectacle without cost:** Flag any action sequence that reads as exciting but consequence-free — where violence is rendered for dramatic pleasure without grounding in what it actually costs the characters.
- **Proportionality:** Is the level of violence depicted proportionate to what the scene requires to achieve its purpose? Gratuitous elaboration beyond narrative necessity is a flag.
- **POV character response:** Is the POV character's emotional and physiological response to violence consistent with their psychology (Module 1.1) and prior experience with violence? A hardened soldier and a merchant's daughter experience the same battle differently.

### Dimension 4: Dark Content Justification

Darkness — cruelty, suffering, moral horror, degradation — is present in the story because it illuminates something true about the human condition or the world, not because it shocks.

Check for:
- **Purposefulness:** Does each dark element (torture, atrocity, sexual violence, psychological cruelty, child death) serve a specific narrative, characterisation, or thematic purpose? Identify that purpose. If none can be identified, flag as potentially gratuitous.
- **Consequence integrity:** Dark events have consequences. A character who commits atrocity is changed by it. A world that contains systemic cruelty is shaped by it. Flag dark content that occurs without consequence — it reads as decoration.
- **Reader trust:** Is the darkness framed in a way that respects the reader? This means: not lingering for shock value, not aestheticising suffering, not presenting cruelty as entertaining spectacle. The question is not "is this dark?" but "is this dark in a way that asks something of the reader?"
- **Tonal register:** Is the darkness consistent with the established register of the novel, or does it represent a sudden escalation that breaks tonal contract with the reader?

### Dimension 5: Tonal Consistency

The novel has an established tone — a particular relationship between irony and earnestness, between horror and hope, between intimacy and scale. Single chapters should not rupture that register.

Check for:
- **Register breaks:** Does this chapter suddenly adopt a different emotional register from what the novel has established? (e.g., comic levity in a chapter following established tragedy; nihilistic bleakness in a story that has maintained moral stakes)
- **Voice consistency:** Does the prose register of this chapter match the prose register of surrounding chapters? Flagging here is about the authorial voice, not the POV character's voice (which should vary — that is POV Consistency Maintenance's domain).
- **Thematic consistency:** Does the chapter advance, complicate, or interrogate the novel's core themes — or does it contradict them without apparent purpose?
- **Hope and agency:** GRRM's fiction is dark but not nihilistic. Characters exercise agency that matters even when they fail. Check that this chapter does not reduce characters to purely passive victims of authorial will without any meaningful choice being present.

---

## Step-by-Step Instructions

### Step 1: Read the Draft

Read the full chapter or scene draft provided. Do not annotate yet. Form an initial impression of:
- What the chapter is doing narratively.
- Where it feels miscalibrated (instinct pass only at this stage).

### Step 2: Audit Against Module 3.5 (if magic present)

If any magical act occurs in the draft:
- Compare each act against Module 3.5's Confirmed capabilities, Confirmed limits, and Confirmed costs.
- Note the prevalence level and count magical acts in the chapter.
- Record all findings for Dimension 2.

If no magic appears in the draft, mark Dimension 2 as Pass and proceed.

### Step 3: Audit Against Module 3.1–3.4 (political and world realism)

Using the World State excerpts provided:
- Check political acts and decisions against the power map and faction records.
- Check character motivations against their established desires and constraints.
- Check that information characters act on is information they plausibly have.
- Record findings for Dimension 1.

### Step 4: Audit Violence Framing (Dimension 3)

Identify all acts of violence in the draft. For each:
- Assess weight, aftermath, and POV character response against their Module 1.1 psychology (if the main agent provided that excerpt; if not, assess from what the prose itself establishes).
- Flag spectacle-without-cost or consequence-free violence.

### Step 5: Audit Dark Content (Dimension 4)

Identify all dark content in the draft. For each element:
- State what narrative, characterisation, or thematic purpose it serves.
- If no purpose can be identified, flag as potentially gratuitous.
- Check that all dark events carry consequences within the chapter or have a recorded consequence pending.

### Step 6: Audit Tonal Consistency (Dimension 5)

Assess the chapter's overall register against:
- The tone reference provided by the main agent (or inferred from the World State).
- Whether the chapter maintains the novel's established relationship between darkness and agency.

### Step 7: Assemble the Audit Report

For each dimension:
- Assign Status (Pass / Flag / Concern).
- For Flags and Concerns: provide the specific flagged passage or reference, the issue description, and the recommended adjustment.

Close with the Priority Summary ranking all flags.

---

## Boundary

This skill:
- **Does not rewrite prose.** It flags and recommends only. All rewriting decisions rest with the main agent and are executed via Scene Construction, Layering History and Legend, or Self-Editing and Refinement.
- **Does not update the World Bible directly.** It returns an audit report; the main agent decides what to act on and performs any World Bible updates (e.g., adding a new magic capability to Module 3.5 if the main agent decides the magical act was intentional expansion).
- **Does not invoke other skills.** It does not call Scene Construction or Self-Editing and Refinement to implement its recommendations.
- **Does not audit POV consistency or voice.** That is POV Consistency Maintenance (scene level) and POV Consistency Auditing (chapter level).
- **Does not audit plot thread status or consequence completeness.** That is Plot Thread Tracking and Consequence Cascade Implementation.
- **Does not operate mid-scene.** It audits completed drafts only.

---

## World Bible Interface

| Direction | Modules |
|---|---|
| **Main agent reads and provides as excerpts** | Module 3.5 (Magic System State — required if magic appears in the draft); Modules 3.1–3.4 (World State — relevant subsets only, as applicable to the chapter content) |
| **Main agent writes from this skill's output** | Nothing directly written from audit output. The main agent may choose to update Module 3.5 (e.g., to add a new confirmed capability or unexplained phenomenon) based on the audit's findings. All such writes are the main agent's decision. |

---

## Dependencies

**Upstream (what this skill consumes):**
- Scene Construction — this skill audits completed scene or chapter drafts produced by Scene Construction.
- Worldbuilding — the World State modules (3.1–3.5) this skill reads were initialised by Worldbuilding and have been maintained by the main agent since.

**Downstream (what consumes this skill's output):**
- The main agent receives the audit report and decides whether to:
  - Re-invoke Scene Construction to address flagged passages.
  - Invoke Self-Editing and Refinement to address tonal or prose issues.
  - Update Module 3.5 if a magic act represents intentional system expansion.
  - Accept flagged items as intentional and proceed.

---

## Example

### Input shape

```
Chapter 17 draft provided (Saerina POV — the siege of Ashford, first major battle scene).

Module 3.5 excerpt:
  Magic System State — Prevalence: Rare.
  Confirmed capabilities: fire-starting at close range; compulsion of small animals; 
    detection of deception within 10 feet.
  Confirmed limits: cannot raise the dead; cannot affect weather.
  Confirmed costs: each use requires 24 hours of physical exhaustion; 
    cannot be used twice in one day.
  Recent magical events: Saerina used compulsion (Ch. 11); Vorn used fire-starting (Ch. 14).

Module 3.1 excerpt:
  Power map — Ashford garrison: 400 soldiers, no cavalry, low on provisions.
  Attacking force (House Drev): 1,100 soldiers, supply line intact, siege engines.
  Lord Ashford: no formal alliances; has sent no word to neighboring houses.

Tone reference: "Low fantasy, high political realism, earned darkness."
```

### Output shape (abbreviated)

```
BALANCE AUDIT REPORT — Chapter 17 (Saerina POV)

DIMENSION 1: Political Realism — FLAG
  Flagged passage: Paragraph 4 — Lord Ashford orders a cavalry charge.
  Issue: Module 3.1 confirms no cavalry in the Ashford garrison. 
    This act is impossible given established resources.
  Recommended adjustment: Replace with an infantry sortie, or establish 
    that Ashford has hidden cavalry reserves (requires World Bible update to 3.1).

DIMENSION 2: Magic Prevalence and Consistency — CONCERN
  Flagged passage: Paragraph 19 — Saerina uses compulsion, then 
    fire-starting in the same scene.
  Issue: Module 3.5 confirms magic cannot be used twice in one day. 
    Using two abilities in the same battle violates established cost.
  Recommended adjustment: Remove one magical act, or introduce the 
    cost explicitly (Saerina collapses after the second use and is 
    non-functional for the battle's remainder).

DIMENSION 3: Violence Framing — PASS
  Violence carries weight throughout; aftermath is shown; Saerina's 
  inexperience with battlefield death is rendered through physiological 
  response (shaking, tunnel vision). No spectacle-without-cost found.

DIMENSION 4: Dark Content Justification — FLAG
  Flagged passage: Paragraphs 31–34 — extended depiction of 
    prisoners being executed after surrender.
  Issue: The sequence runs four paragraphs. The narrative purpose 
    (establishing House Drev's brutality) is achieved by paragraph 32. 
    Paragraphs 33–34 continue without adding new information or 
    emotional meaning. Risk of gratuitousness by elaboration.
  Recommended adjustment: Cut to two paragraphs. The effect is 
    stronger with less.

DIMENSION 5: Tonal Consistency — PASS
  Chapter maintains the established low-fantasy register. 
  Saerina exercises meaningful agency (her choice at the gate 
  matters) despite the outcome being defeat. No register break found.

PRIORITY SUMMARY:
  High: Dimension 2 (magic cost violation — continuity error)
  High: Dimension 1 (cavalry — factual impossibility given World Bible)
  Medium: Dimension 4 (dark content over-elaboration)
```

---

## Glossary (Relevant Terms)

- **Iceberg principle:** Build far more world detail than appears on the page. The political realism and magic system coherence this skill audits are downstream of that principle — the world must be consistent whether or not the reader sees all of it.
- **Magic system state:** The versioned record in Module 3.5 of what magic has confirmed been shown to do, what it cannot do, and what it costs — the authoritative source for magic auditing.
- **Scene Purpose Test:** Every scene must advance plot or reveal character. This audit's "dark content justification" check is one application of this principle — darkness that serves neither purpose fails the test.
- **POV discipline:** This skill does not audit POV consistency (that is POV Consistency Maintenance's domain), but it does check that the POV character's response to violence and darkness is internally consistent with their psychology.
