---
name: character-integration-with-plot
description: Maps the desire→action→consequence loop for each character; builds the full relationship matrix with directional records; defines response patterns across event categories. Invoked after Character Creation is complete for all relevant characters. Outputs integration data for World Bible Modules 1.2, 1.3, and initial Consequence Ledger entries (Module 4.1).
---

# Character Integration with Plot

## Identity

**Purpose:** Integrate completed characters into the story's living system by formalising the desire→action→consequence loops that will drive plot from character, building the full directional relationship matrix between characters, and seeding the Consequence Ledger with anticipated consequence structures. This is the last character-building skill before writing begins.

---

## Core

Map the desire → action → consequence loop for each character; build the full relationship matrix with detailed directional records; define each character's response patterns to categories of events. Output integration data for World Bible Modules 1.2, 1.3, and initial entries in Consequence Ledger Module 4.1. Do not write scenes or plot events.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 1.1 (Character Directory):** Complete character records for all characters being integrated — psychology, core desire, fear, self-deception, values under pressure, response patterns, arc type.
2. **World Bible excerpt — Module 1.2 (Character Knowledge Matrix):** Current state of what each character knows, suspects, believes, and does not know — including initial entries from Character Creation.
3. **World Bible excerpt — Module 1.3 (Relationship Records):** Pre-existing relationship records as established by Character Creation.
4. **World Bible excerpt — Module 3.1 (Political/Power Map):** Current world state — faction alignments, power structures, active tensions — so that relationship trajectories and desire loops can be grounded in the political reality the characters inhabit.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

Integration data for the following World Bible modules, returned to the main agent for writing:

### For Module 1.2 — Character Knowledge Matrix (expansion)

For each character, add to the initial entries from Character Creation:

- **KNOWS:** Any inter-character knowledge that can be established at integration time — what Character A knows about Character B that Character B does not know they know; intelligence, secrets, assessments held by each character about the others.
- **SUSPECTS:** Suspicions each character holds about others at story start — derived from their psychology, their position in the power map, and the relationship history.
- **BELIEVES (possibly false):** Formally register all known false beliefs each character holds about the other characters at story start. These are the seeds of dramatic irony and future knowledge violations.
- **DOES NOT KNOW:** For each character, register what they definitively do not know at story start that is known to the reader or to other characters (information asymmetry at story opening).

> The purpose of populating these at integration time is to lock the Knowledge Matrix state before writing begins, so that Scene Construction and POV Consistency Maintenance have a reliable baseline.

### For Module 1.3 — Relationship Records (full build)

For each character pair where a significant relationship exists (directional — A→B and B→A as separate records), expand the initial records with:

- **Valence:** Positive / Negative / Complex / Unknown (from each direction separately — A may trust B; B may be using A).
- **Power dynamic:** Who holds power in this relationship, and what kind (coercive / social / informational / emotional / economic). Power may be asymmetric and may not be correctly perceived by either party.
- **History:** The relationship's substantive backstory — key events, turning points, what each character believes the relationship is based on (which may differ between them).
- **Secrets:** What each character is concealing from the other. What neither knows about the other. What one knows that the other does not suspect they know.
- **Trajectory:** Where this relationship is heading given the current psychological states, knowledge states, and political context. Trajectory is a hypothesis — the Gardener principle means character logic overrides planned trajectory.
- **Convergence potential:** Whether and approximately when these characters are likely to come into direct contact or conflict in the story.

### For Module 4.1 — Consequence Ledger (initial entries)

For each character's central desire loop, create an initial consequence entry that captures the anticipated consequence structure of the desire playing out:

- **Triggering driver:** This character's core desire, as the engine of action.
- **Anticipated action pattern:** The category of actions this desire will produce (e.g. "will seek to consolidate control of information channels"; "will refuse alliances that require subordinating judgment to another's authority"; "will protect specific person at cost to faction").
- **Anticipated immediate consequences:** What the first round of consequences from this desire-pattern is likely to produce for this character and for adjacent characters.
- **Affected characters:** Who else is structurally affected by this character's desire-driven action pattern.
- **Time-delayed consequence potential:** Whether this desire loop contains the structure of a future consequence bomb — an action taken early that will produce a catastrophic consequence only after several chapters.

> These are hypothetical entries, not locked outcomes. The Gardener principle applies. The main agent updates Module 4.1 as actual story events produce real consequences; these initial entries are anticipatory scaffolding.

---

## Boundary

- **Requires** Character Creation to be complete for all characters being integrated. Cannot run on concept documents or partial records.
- **Does not** write scenes, plot events, or prose.
- **Does not** produce a scene outline or chapter plan. Output is structured relationship and consequence data, not a plot.
- **Does not** determine pacing or chapter sequence. Those are Group 3 skill domains.
- **Does not** update the World Bible directly. The main agent writes Modules 1.2, 1.3, and 4.1 from this skill's output.
- **Does not** generate new character concepts or extend existing character psychology beyond what is in the character records. If the character records are incomplete, this skill returns the output it can and flags what is missing.

---

## Invocation

The main agent invokes Character Integration with Plot:

- After Character Creation is complete for all characters who will be present in the story's opening arc (not necessarily all characters in the novel — characters who appear later can be integrated when they are introduced).
- Before writing of the opening chapters begins.
- When a new significant character is added mid-story and must be integrated with existing characters.

This skill is invoked once per character cohort (or new character addition), not on a recurring basis.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 1.1 (Character Directory), Module 1.2 (Knowledge Matrix, current state), Module 1.3 (Relationship Records, initial entries), Module 3.1 (Political/Power Map) |
| **Main agent writes to** | Module 1.2 (expanded Knowledge Matrix), Module 1.3 (full Relationship Records), Module 4.1 (initial Consequence Ledger entries) |

---

## Dependencies

**Upstream:** **Character Creation** — all characters being integrated must have complete Module 1.1 records.  
**Downstream:** Output populates Module 1.3 (Relationship Records), which is read by **Gardener Plotting System**, **Conflict Layering**, and **Consequence Cascade Implementation**. Module 4.1 initial entries are the foundation for **Consequence Cascade Implementation**. Module 1.2 expansion is read by **POV Consistency Maintenance** and **POV Consistency Auditing**.

---

## Instructions

Follow these steps when executing this skill.

### Step 1 — Map the desire network

Before building relationships, map each character's core desire against the others'. Identify:

- Which characters' desires are structurally compatible — they want different things and can use each other.
- Which characters' desires are structurally in conflict — they want the same scarce resource, or one's success requires the other's failure.
- Which characters' desires are mutually invisible — they are not yet in conflict but will be when they converge.

This network is the foundation of all relationship trajectories and the engine from which plot will grow.

### Step 2 — Build the Knowledge Matrix expansion (Module 1.2)

For each character, work through the four knowledge states at story opening:

**KNOWS:** Focus on inter-character knowledge. What does this character know about others in the cast that creates advantage, obligation, or vulnerability? Cross-reference: if A knows something about B, ensure B's DOES NOT KNOW register reflects this.

**SUSPECTS:** Derive suspicions from psychology and position. A character whose primary observational lens is threat-assessment will have active suspicions even without direct evidence. A character whose blind spot is emotional need may fail to suspect betrayal from someone they perceive as distressed rather than calculating. Do not invent suspicions without grounding them in the character's specific psychology and available information.

**BELIEVES (possibly false):** Systematically register all false beliefs at story start. False beliefs about other characters are the seeds of: (a) dramatic irony (the reader knows; the character does not), (b) knowledge violations that POV Consistency Maintenance must catch, and (c) eventual revelation scenes. Register them now.

**DOES NOT KNOW:** Complete the matrix — for every significant fact that is known to at least one other character, specify who does not know it. Information asymmetry at story opening is a primary source of dramatic tension.

### Step 3 — Build directional relationship records (Module 1.3)

Build each significant relationship as two records: A→B and B→A. The asymmetry between these records is often the most dramatically interesting element.

For each record:

**Valence:** Be precise. "Complex" is not sufficient — specify what the complexity consists of (e.g. "genuine affection that coexists with active exploitation; A does not know both are present simultaneously in B's experience of the relationship").

**Power dynamic:** Who holds leverage, what kind, and whether either party is accurately assessing the power distribution. Misperceived power dynamics are a major source of dramatic complication — a character who believes they hold power and does not will make different decisions than one who knows the true structure.

**History:** Identify the 1–3 specific moments in the relationship's history that most define its current state. Not a complete history — the load-bearing moments.

**Secrets:** Be explicit about what each character is concealing and whether the other suspects concealment. "B is concealing X from A; A does not suspect X exists" is different from "B is concealing X from A; A suspects something but has no specific suspicion about X."

**Trajectory:** State the direction this relationship is heading if both characters continue acting from their current psychology and knowledge state. Mark it as a hypothesis. If the trajectory leads to a specific type of scene (confrontation, revelation, betrayal, alliance), note it without specifying the chapter.

**Convergence potential:** When will these characters be in the same scene? Does the story require them to be, or will their plotlines run parallel for some time?

### Step 4 — Seed the Consequence Ledger (Module 4.1)

For each character's central desire loop, create an anticipatory entry. The purpose is not to pre-plot events but to formalise the consequence *structure* that will emerge from this character's desires acting in this world.

For each entry, answer: *If this character pursues this desire in this world, given these relationships and this political context, what is the shape of the consequence that eventually comes back to them?* 

Specifically:
- What are they likely to do that will have consequences they cannot foresee?
- Who will be affected, and how?
- Is there a specific action that, if taken early, creates a consequence bomb — a delayed catastrophic consequence — that should be tracked from the start?

These entries are the main agent's early warning system. As actual events are written, Consequence Cascade Implementation will build on this foundation.

### Step 5 — Flag gaps and inconsistencies

Review the integration output before returning it. Flag:

- Any character pair where relationship records are asymmetric in a way that seems unintentional (vs. the intentional asymmetry of directionality).
- Any knowledge state that appears inconsistent — e.g. a character who KNOWS something that no one in their position could plausibly know.
- Any desire loop where the consequence structure cannot be anticipated because a key character's psychology is insufficiently developed in their Module 1.1 record.

Return flags to the main agent alongside the integration data.

### Step 6 — Return integration data to main agent

Return all three modules' data (1.2 expansion, 1.3 full records, 4.1 initial entries) and any flags to the main agent. The main agent writes the World Bible.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Knowledge Matrix is cross-referenced — if A KNOWS X about B, B's DOES NOT KNOW register reflects this.
- [ ] BELIEVES entries include all false beliefs established in character records, not just obvious ones.
- [ ] Relationship records are directional — A→B and B→A are separate entries with potentially asymmetric content.
- [ ] Power dynamics specify the type of power and whether it is accurately perceived.
- [ ] Consequence Ledger initial entries are anticipatory structures, not locked plot events.
- [ ] Character Creation is confirmed complete for all characters before integration proceeds.
- [ ] Gaps and inconsistencies are flagged and returned with the data, not silently corrected.
- [ ] No World Bible writes specified in the skill — all output returned to main agent.
- [ ] No prose scenes written. No chapter plan produced.
