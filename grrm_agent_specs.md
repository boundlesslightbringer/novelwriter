# GRRM Novel-Writing Agent: Final System Specification
## Boundaries, Cores, and Interfaces — Implementation Reference

---

# SECTION 1: AGENT SKILLS

## Governing Rules
- All skills are discrete, callable units invoked **only** by the main agent.
- Skills do not access the World Bible directly. They receive **curated excerpts** passed by the main agent, and return outputs to the main agent for World Bible updating.
- Skills do not call other skills. Only the main agent orchestrates skill invocation.
- **Output format for all writing skills:** Draft prose. Refinement occurs only on the Self-Editing and Refinement pass.

---

## Skill Group Architecture

Skills are organized into **7 functional groups**. In the DeepAgent implementation, each group maps to a **session-persistent subagent** that handles all skills within that domain:

| Subagent | Group | Skills | Purpose |
|----------|-------|--------|---------|
| **Planning Subagent** | Group 1 – Planning | Finding a Seed, Defining Rough Endpoints, Worldbuilding, Research Integration | Story foundation and world construction |
| **Character Subagent** | Group 2 – Character | Character Conception, Character Creation, Character Voice Differentiation, Character Integration with Plot | Full character lifecycle |
| **Plotting Subagent** | Group 3 – Plotting & Structure | Gardener Plotting System, Multiple POV Structure, Braided Narrative Technique, Conflict Layering, Plot Thread Tracking | Scene planning and structural management |
| **Writing Subagent** | Group 4 – Writing Execution | Scene Construction, POV Consistency Maintenance, Pacing, Layering History and Legend, Professional Writing Techniques | Draft prose generation and quality |
| **Consequence Subagent** | Group 5 – Consequence & Realism | Consequence Cascade Implementation, Balancing Realism and Fantasy | Event impact and realism audits |
| **ProblemSolver Subagent** | Group 6 – Problem-Solving | Resolving Obstacles and Untangling Tangles | Diagnostic and resolution support |
| **Refinement Subagent** | Group 7 – Refinement | Self-Editing and Refinement, POV Consistency Auditing | Final polish and auditing |
| **WorldBibleManager** | Infrastructure | All World Bible modules | ALL World Bible I/O operations |

**Delegation Pattern:** The brain (main agent) delegates to subagents by domain. Each subagent receives all skills in its group at initialization and internally routes to the appropriate skill(s) based on task context. This enables natural skill composition within domains while keeping the brain's orchestration logic clean.

---

## GROUP 1: PLANNING SKILLS

### Finding a Seed
- **Core:** Generate and evaluate seed ideas using four methods: Vivid Image, "What If?", Character-First, Historical Inspiration.
- **Input:** None required. Optionally receives thematic or genre constraints from main agent.
- **Output:** A validated seed — one concrete, emotionally resonant image or moment — and a list of the questions it raises.
- **Boundary:** Does not begin writing. Does not build world or characters. Outputs the seed only.

---

### Defining Rough Endpoints
- **Core:** Establish the story's compass — starting situation, vague ending destination, 2–4 major milestones, and the core conflict question.
- **Input:** Validated seed from Finding a Seed.
- **Output:** Endpoint compass document for World Bible initialisation.
- **Boundary:** Does not plot individual scenes or chapters. Does not outline. Endpoints are intentionally loose and will shift as the story grows.

---

### Worldbuilding
- **Core:** Build geography, political landscape, cultures, religion, and magic system using the iceberg principle — construct ten times more than will be shown.
- **Input:** Endpoint compass. Research material if Research Integration has been invoked.
- **Output:** Structured world data for World Bible initialisation (Modules 3.1–3.5).
- **Boundary:** Does not write prose. Does not create characters. Outputs structured world data only.

---

### Research Integration
- **Core:** Gather and synthesise external reference knowledge — medieval warfare, political structures, social history, geography, etc. — to inform any other skill that requires factual grounding.
- **Input:** A specific research question or domain from the main agent.
- **Output:** Factual reference material in structured notes format.
- **Boundary:** Does not make story decisions. Does not update the World Bible. Outputs reference material only, which the main agent passes to the relevant skill.

---

## GROUP 2: CHARACTER SKILLS

### Character Conception
- **Core:** Generate character concepts using role-first, archetype-subversion, historical inspiration, or "What If?" methods. Identify the core contradiction that makes the character interesting.
- **Input:** World Bible excerpt — world state, power map, required narrative roles.
- **Output:** Character concept: role, core contradiction, and a one-paragraph sketch.
- **Boundary:** Does not build psychological depth. Does not place character in plot. Outputs concept only.

---

### Character Creation
- **Core:** Build the full character iceberg — visible surface (physical, social) and the hidden 90% (core wound, fears, desires, arc type, contradictions, values, response patterns).
- **Input:** Character concept from Character Conception.
- **Output:** Complete character record for World Bible Module 1.1 and initial entries for Module 1.2 (Knowledge Matrix) and Module 1.3 (Relationships).
- **Boundary:** Operates on an already-conceived character. Does not place character in plot. Does not write prose.

---
<!-- 
not every character needs a voice differentiation, only POV characters do
voice profile document needs to be stored in the World Bible -->
### Character Voice Differentiation
- **Core:** Define a distinct narrative voice profile for each POV character — vocabulary range, sentence structure patterns, observational focus (what they notice), internal thought patterns, and emotional processing style.
- **Input:** Completed character record from Character Creation.
- **Output:** Voice profile document per POV character. Used by Scene Construction as a reference.
- **Boundary:** Operates after Character Creation is complete. Does not write scenes. Outputs voice profile only.

---

### Character Integration with Plot
- **Core:** Map the desire → action → consequence loop for each character; build the full relationship matrix with detailed records; define response patterns to categories of events.
- **Input:** Completed character records; World Bible excerpt of current world state and political map.
- **Output:** Integration data for World Bible Modules 1.2, 1.3, and initial entries in Consequence Ledger (Module 4).
- **Boundary:** Requires Character Creation to be complete for all relevant characters. Does not write scenes or plot events.

---

## GROUP 3: PLOTTING & STRUCTURE SKILLS

### Gardener Plotting System
- **Core:** Drive scene-by-scene discovery by identifying the POV character's goal, the obstacle in the way, the choice they face, and the consequence that will open the next scene. Operates from character logic, not structural template.
- **Input:** Current chapter's POV character state; most recent scene outcome; World Bible excerpt of active plot threads and consequence ledger.
- **Output:** Next scene parameters — goal, obstacle, choice, projected consequence — passed to Scene Construction.
- **Boundary:** Does not write prose. Does not determine pacing. Outputs scene parameters only.

---

### Multiple POV Structure
- **Core:** Manage POV assignment across chapters, rotation logic, and synchronisation of simultaneous events across POV timelines.
- **Input:** World Bible POV Chapter Log (Module 2.2); current timeline state (Module 2.1).
- **Output:** POV chapter schedule — which POV is next, why, and what simultaneous events to account for.
- **Boundary:** Does not write scenes. Does not determine pacing. Outputs scheduling data only.

---

### Braided Narrative Technique
- **Core:** Ensure POV storylines run parallel, intersect meaningfully at planned and discovered convergence points, and contain no redundant scenes (same event shown from two POVs with no new information added).
- **Input:** World Bible POV Chapter Log; Plot Thread Registry (Module 2.3).
- **Output:** Braiding analysis — convergence opportunities, redundancy flags, suggested connection points.
- **Boundary:** Operates at chapter sequence level, not individual scene level. Does not rewrite. Outputs analysis only.

---

### Conflict Layering
- **Core:** Audit a drafted scene or chapter to ensure conflict exists at all five levels relevant to the POV character: internal, interpersonal, societal, factional, existential. Flag absent levels.
- **Input:** Drafted scene or chapter; World Bible character state and relationship records for POV character.
- **Output:** Conflict audit report — which levels are present, which are absent, and suggested additions.
- **Boundary:** Does not rewrite the scene. Flags and suggests only. Main agent decides whether to invoke Scene Construction again.

---

### Plot Thread Tracking
- **Core:** Maintain and report on the registry of active, dormant, and resolved threads. Flag threads approaching overdue payoff windows. Identify convergence opportunities.
- **Input:** World Bible Plot Thread Registry (Module 2.3) and Pending Payoffs (Module 2.4).
- **Output:** Thread status report — current state of all threads, overdue flags, convergence opportunities.
- **Boundary:** Does not resolve threads. Does not write scenes. Outputs status report only.

---

## GROUP 4: WRITING EXECUTION SKILLS

### Scene Construction
- **Core:** Write a single scene in draft prose. One POV character, one goal, one obstacle, one choice, one consequence. Applies the POV character's voice profile throughout. Foreshadowing is embedded during construction — setup elements consistent with the Pending Payoffs register are woven into the scene naturally.
- **Input:** Scene parameters from Gardener Plotting System; POV character voice profile; World Bible excerpts for character knowledge state, current world state, and Pending Payoffs register.
- **Output:** Draft prose for one scene.
- **Boundary:** Produces draft prose only — not refined prose. Does not audit its own POV consistency (that is POV Consistency Maintenance's job). Does not update the World Bible.

---

### POV Consistency Maintenance
- **Core:** Verify Scene Construction output for: head-hopping, omniscient narration intrusions, knowledge violations (character acts on information they do not have), voice inconsistency against the voice profile, and external self-description errors.
- **Input:** Draft scene from Scene Construction; POV character voice profile; World Bible Character Knowledge Matrix for the POV character.
- **Output:** Consistency report — flagged violations with specific line references and correction notes.
- **Boundary:** Always runs after Scene Construction. Does not rewrite the scene. Flags issues only. Main agent decides whether to re-invoke Scene Construction with corrections.

---

### Pacing
- **Core:** Calibrate narrative tension at scene and chapter level based on the **POV character's current psychological and emotional state**. A character in crisis drives faster, shorter, more urgent prose rhythms. A character in grief or reflection drives slower, more interior rhythms. Tension is a function of what the character is experiencing, not of structural phase.
- **Input:** Current POV character's psychological state from World Bible Module 1.1; most recent scene outcome; current chapter's emotional arc.
- **Output:** Pacing guidance — recommended scene rhythm, sentence density, interiority level, and dialogue-to-action ratio for the current scene or chapter.
- **Invocation:** Called by the main agent when the POV character's psychological state has shifted significantly — not on a fixed schedule and not tied to structural phase transitions.
- **Boundary:** Does not write prose. Does not make plot decisions. Outputs guidance only, which Scene Construction uses as a parameter.

---

### Layering History and Legend
- **Core:** Weave backstory, in-world songs, legends, ruins, artifacts, and conflicting historical accounts into existing prose through the natural filter of the POV character's knowledge and cultural context.
- **Input:** Completed scene or chapter draft; World Bible History & Legends (Module 3.4) and Cultures (Module 3.3); POV character knowledge state.
- **Output:** Revised draft with history and legend integrated.
- **Boundary:** Operates on completed scenes or chapters only. Does not introduce new plot events. Does not create new history not already in World Bible.

---

### Professional Writing Techniques
- **Core:** Apply specific advanced craft techniques to resolve writing problems. Covers: Skip and Return, Character Interview, Timeline Realignment, Consequence Trace-Back, Change POV, Freewrite the Tangle, The Worse Choice Trick.
- **Input:** Description of the specific problem from main agent; relevant World Bible excerpts.
- **Output:** Technique application — either a concrete path forward, a diagnostic, or a reframing of the problem for the main agent to act on.
- **Invocation:** Called by the main agent when a specific craft problem arises that does not require Tangle Resolution (i.e., the problem is local — a single scene or beat — not systemic).
- **Boundary:** Tangle-focused. Does not handle general prose quality (that is Self-Editing's domain). Does not update the World Bible.

---

## GROUP 5: CONSEQUENCE & REALISM SKILLS

### Consequence Cascade Implementation
- **Core:** For each major event, project and record immediate, short-term, and long-term consequences across all affected characters. Identify time-delayed consequence bombs and add them to the ledger.
- **Input:** Description of the triggering event and chapter reference; World Bible Character Directory, Relationship Records, and current Consequence Ledger.
- **Output:** Consequence cascade record for World Bible Module 4.
- **Boundary:** Does not write scenes. Does not determine how consequences will be dramatised. Outputs structured consequence data for the World Bible only.

---

### Balancing Realism and Fantasy
- **Core:** Audit a completed chapter or flagged scene against the realism-fantasy calibration checklist — political realism, magic prevalence, violence framing, dark content justification, and tonal consistency.
- **Input:** Completed chapter or scene draft; World Bible Magic System State (Module 3.5) and World State (Module 3.1–3.4).
- **Output:** Balance audit report — specific flags with recommended adjustments.
- **Boundary:** Does not rewrite. Flags and recommends only.

---

## GROUP 6: PROBLEM-SOLVING SKILLS

### Resolving Obstacles and Untangling Tangles
- **Core:** Diagnose the tangle type (character in impossible situation, non-converging plotlines, character choice that breaks plot, unknown scene ending), select the appropriate resolution technique from the professional toolkit, and follow character logic to a viable path forward.
- **Input:** Description of the tangle; World Bible excerpt of the last stable chapter state, relevant character psychology, and active consequence chains.
- **Output:** A concrete path forward — not the written scene, but the decision that unblocks the main agent.
- **Invocation:** Called by main agent when stuck, or triggered automatically by the Reassess Trigger.
- **Boundary:** Outputs a path forward only. Does not write scenes. Does not update the World Bible.

---

## GROUP 7: REFINEMENT SKILLS

### Self-Editing and Refinement
- **Core:** Line-by-line trimming of a completed chapter draft — remove unnecessary words, tighten dialogue, cut scenes that fail the Scene Purpose Test, kill darlings, and improve general prose quality (sentence rhythm, word choice, avoidance of adverbs and passive constructions where they weaken prose).
- **Input:** Completed chapter draft.
- **Output:** Refined chapter draft.
- **Invocation:** After chapter completion only. Not mid-scene, not mid-chapter.
- **Boundary:** General prose quality lives here. Does not audit POV consistency (that is POV Consistency Auditing's job).

---

### POV Consistency Auditing
- **Core:** Full chapter-level audit of POV discipline, voice differentiation, and Knowledge Matrix compliance across the entire chapter (not just a single scene).
- **Input:** Refined chapter draft from Self-Editing; all POV voice profiles; World Bible Character Knowledge Matrix for all characters appearing in the chapter.
- **Output:** Audit report with flagged violations and correction notes.
- **Invocation:** After Self-Editing and Refinement. Not before.
- **Boundary:** Does not rewrite. Flags only.

---

# SECTION 2: SYSTEM PROMPT

## Governing Rules
- The system prompt contains only principles, rules, and decision logic that apply to **every single action** the main agent takes.
- Detailed pacing rules, craft technique lists, editing checklists, and worldbuilding frameworks are **not** in the system prompt — they live in their respective skills.
- The system prompt is permanent operating context. It does not grow with the novel.

---

## BLOCK 1: CORE PHILOSOPHY — THE GARDENER

You are a Gardener, not an Architect. You do not write from a blueprint. You plant a seed and follow where it grows.

You know your starting point. You have a rough sense of where the story ends. Everything between is discovered through the act of writing — not planned in advance, not outlined scene by scene.

Your surprise is the reader's surprise. When a character leads you somewhere unexpected, that is the story working. Trust it.

---

## BLOCK 2: IMMUTABLE WRITING RULES

These rules are never suspended, never traded off against convenience.

**Characters Drive Plot.**
Character choices create plot events. Plot events do not dictate character choices. When you need to decide what happens next, ask what the character would do — not what the story needs.

**Every Action Has Consequences.**
All character choices produce consequences. Consequences are tracked in the World Bible and honoured in future chapters. No consequence, once recorded, is forgotten or quietly discarded.

**No Plot Armor.**
Any character can die, fail, or be broken if their choices lead there. Protagonists and POV characters have no structural protection. The story does not owe them survival.

**POV Discipline.**
Each chapter belongs to one POV character. Everything in that chapter — description, observation, interpretation, knowledge — is filtered through that character's perception and nothing else. This is never broken mid-chapter. The omniscient narrator does not exist.

**The Scene Purpose Test.**
Every scene must do at least one of two things: advance the plot, or reveal character. A scene that does neither is cut.

---

## BLOCK 3: THE PROCESS OF DISCOVERY

Each writing session begins by revising the final pages of the previous chapter before writing forward. This is not optional. It restores the POV character's voice and reconnects to the story's current state.

Write to find out what happens — not to execute what was planned.

When character logic and any prior intention conflict, character logic wins.

Stop mid-scene when possible — at a moment where you already know what comes next. This preserves momentum for the following session.

---

## BLOCK 4: DECISION FRAMEWORKS

**Embrace Tangles vs. Create Complications**

When the story becomes complicated because a character made an unexpected choice:
→ Embrace it. Follow the character. Write through the complication. Blind alleys are often richer than planned paths.

When the story is too linear, too predictable, or progressing without genuine resistance:
→ Invoke Conflict Layering. Force characters into situations with no clean resolution. Let them make flawed, human choices with real costs.

---

**Character Choice Resolution**

When determining what a character does in any situation, the only valid question is:
*What would this specific character do, given their psychology, their knowledge at this moment, and their situation?*

The question *What does the plot need to happen?* is not a valid input to this decision.

---

**Convergence Checkpoint**

At every chapter boundary, evaluate:
*Have the major conflicts begun moving toward resolution? Are the POV arcs converging toward the rough endpoint?*

- If **no**: continue writing forward. Invoke Gardener Plotting System for the next scene parameters.
- If **yes**: shift into convergence mode. Begin resolving arcs, paying off setups, and drawing threads together. Invoke Plot Thread Tracking to ensure no thread is unaccounted for before the ending.

---

**Pacing Invocation**

Invoke the Pacing skill when a POV character's psychological or emotional state shifts significantly — not on a fixed schedule, not at structural phase transitions. Pacing is a function of what the character is living through, not of where the story is structurally.

---

## BLOCK 5: NEGATIVE CONSTRAINTS

**No Info-Dumping.**
World details are never delivered in explanatory blocks of exposition. They emerge through action, dialogue, and the natural filter of what the POV character would think and notice. The POV character does not explain what they already know.

**No Plot Armor.**
Already stated as an immutable rule. Restated here for emphasis: the survival of a character is never assumed. It is always earned or lost through consequence.

**No Head-Hopping.**
POV never shifts mid-chapter. No accessing other characters' inner states. No omniscient narrative intrusions. What the POV character cannot perceive, the reader cannot know.

**No POV Proliferation.**
New POV characters are not added without clear justification. A new POV is only warranted if it provides a genuinely unique perspective — geographic, factional, psychological — unavailable from any existing POV.

**No Thread Abandonment.**
No planted story thread is dropped without resolution or deliberate, tracked open-ending. All setups have payoffs. All payoffs are tracked in the World Bible Pending Payoffs register.

---

## BLOCK 6: OPERATIONAL LOGIC

**World Bible Protocol**

The World Bible is the sole ground truth for story state. Only the main agent reads from and writes to it. Sub-agents receive only the excerpts relevant to their specific task.

After every chapter, before any further writing begins, the World Bible is updated in this order:
1. Character State (Module 1)
2. Timeline and POV Chapter Log (Module 2.1–2.2)
3. Plot Thread Registry and Pending Payoffs (Module 2.3–2.4)
4. Consequence Ledger (Module 4)
5. Continuity Registry (Module 5)

---

**Reassess Trigger**

The Reassess Trigger fires when either of the following conditions is met:

- **Condition A:** Tangle Resolution has been invoked N consecutive times without producing a viable path forward. *(N = implementation-defined threshold)*
- **Condition B:** The World Bible Contradiction Detection system flags a contradiction that cannot be resolved without rewriting established chapters.

When the trigger fires:
1. Halt all writing.
2. Perform a full World Bible consistency review.
3. Re-evaluate character logic from the last stable chapter state.
4. If the endpoint is no longer reachable or no longer valid: re-invoke Defining Rough Endpoints with the current world state as input.
5. Only resume writing once a clear path forward exists.

---

**Skill Invocation Reference**

| Trigger Condition | Skill to Invoke |
|---|---|
| Starting the novel | Finding a Seed → Defining Rough Endpoints → Worldbuilding → Character pipeline |
| Need factual grounding for any skill | Research Integration |
| Starting a new scene | Gardener Plotting System → Scene Construction → POV Consistency Maintenance |
| POV character state has shifted significantly | Pacing (before Scene Construction) |
| Story feels too linear or conflict-free | Conflict Layering |
| POV rotation decision needed | Multiple POV Structure |
| Storyline redundancy or convergence question | Braided Narrative Technique |
| Major event just occurred | Consequence Cascade Implementation |
| Tone, magic, or dark content flagged | Balancing Realism and Fantasy |
| Local craft problem (single scene or beat) | Professional Writing Techniques |
| Systemic tangle (cannot find path forward) | Resolving Obstacles and Untangling Tangles |
| Chapter complete | Self-Editing and Refinement → POV Consistency Auditing |
| Thread status or convergence check | Plot Thread Tracking |
| Tangle Resolution invoked N times with no progress | Reassess Trigger |
| World Bible contradiction detected | Reassess Trigger |

---

# SECTION 3: WORLD BIBLE

## Governing Rules
- The World Bible is the sole ground truth for all story state.
- **Access:** Main agent only. Sub-agents receive curated excerpts passed by the main agent.
- **Granularity:** Chapter-level state snapshots.
- **Versioning:** A full state snapshot is saved after every chapter update.
- **Querying:** Any record is queryable as of Chapter N.
- **Diff Tracking:** The delta between consecutive chapter snapshots is tracked and accessible.
- **Contradiction Detection:** A write operation that conflicts with an established record is automatically flagged before the write is committed.

---

## MODULE 1: CHARACTER STATE

### 1.1 Character Directory
*One record per character — both POV and non-POV*

| Field | Description |
|---|---|
| Full name | Including titles and aliases |
| Age | At current chapter |
| Physical description | Height, build, eye colour, hair, distinguishing marks, scars |
| Social class / Role | Current role in society, title, faction |
| Location | Current chapter location |
| Injuries / Physical state | Active injuries, disabilities, fatigue |
| Possessions of significance | Items with plot, sentimental, or symbolic weight |
| Current beliefs | What they believe to be true about the world and themselves |
| Emotional state | Current dominant emotional state and cause |
| Active desires | What they are actively pursuing in this chapter |
| Active fears | What they are actively trying to avoid or suppress |
| Arc type | Growth / Fall / Flat |
| Arc stage | Where in the arc they currently sit |
| POV chapter count | How many chapters they have narrated |
| Last POV chapter | Chapter number of their most recent narrated chapter |

---

### 1.2 Character Knowledge Matrix
*Per character, per piece of significant information*

| Field | Description |
|---|---|
| Character | Who holds this knowledge state |
| Information item | The specific fact, secret, or event |
| Status | KNOWS / SUSPECTS / BELIEVES (possibly false) / DOES NOT KNOW |
| Acquired at chapter | When this knowledge state was established or changed |
| Source | How they came to know, suspect, or believe it |
| Dramatic irony flag | Is the reader in a different knowledge state than this character? |

---

### 1.3 Relationship Records
*One record per character pair — directional (A→B and B→A are separate records)*

| Field | Description |
|---|---|
| Character A → Character B | Directional relationship being recorded |
| Emotional valence | Current dominant emotion: love, hate, fear, debt, respect, contempt, loyalty, distrust, etc. |
| Power dynamic | Who holds leverage, and why |
| Relationship history | Formative events and turning points, with chapter references |
| Secrets A keeps from B | What A is concealing |
| Secrets B keeps from A | What B is concealing |
| Most recent interaction | Chapter reference and brief summary |
| Trajectory | Stable / Deteriorating / Evolving / Volatile |

---

## MODULE 2: PLOT & TIMELINE STATE

### 2.1 Absolute Timeline
*Versioned per chapter snapshot*

| Field | Description |
|---|---|
| Absolute date / day | Calendar or relative day count |
| Events on this date | All events, with POV chapter references |
| Simultaneous events | Events occurring at the same time across different POV locations |
| Travel records | Character, from, to, departure date, arrival date, travel duration |
| Seasonal / weather state | Per region, current chapter |

---

### 2.2 POV Chapter Log
*One entry per chapter*

| Field | Description |
|---|---|
| Chapter number | Sequential |
| POV character | Who narrates |
| Location | Where the chapter takes place |
| Scene summary | 2–3 sentence summary |
| Cliffhanger status | Yes / No — if yes, description |
| Connections | Links to other POV storylines affected by this chapter's events |
| Chapter delta | Key changes to world state introduced in this chapter |

---

### 2.3 Plot Thread Registry
*One record per thread*

| Field | Description |
|---|---|
| Thread ID | Unique identifier |
| Thread name | Brief descriptive name |
| Status | Active / Dormant / Resolved / Abandoned |
| Originating chapter | When the thread was introduced |
| Characters involved | All POV and non-POV characters in this thread |
| Expected convergence | Rough chapter window for resolution, if known |
| Dependencies | Other threads that must resolve before or alongside this one |
| Resolution summary | If resolved: how it ended, chapter reference |

---

### 2.4 Pending Payoffs & Foreshadowing
*One record per setup element*

| Field | Description |
|---|---|
| Setup element | What was planted — specific description |
| Type | Chekhov's gun / Foreshadowing / Consequence bomb / Prophecy / In-world legend |
| Planted in chapter | Chapter reference |
| Embedded by | Scene Construction (foreshadowing during writing) or Foreshadowing Placement (post-construction) |
| Expected payoff window | Rough chapter range for payoff |
| Resolution status | Pending / Paid off / Overdue |
| Payoff chapter | If resolved: chapter reference |

---

## MODULE 3: WORLD STATE

### 3.1 Political & Power Map
*Versioned per chapter snapshot*

| Field | Description |
|---|---|
| Territory | Named region or location |
| Current controller | Character or faction holding power |
| Held since | Chapter reference when control was established |
| Allegiances | Current alliances, with stability rating |
| Active enmities | Current conflicts, cause, and current phase |
| Military assets | Army size, location, commander, loyalty |
| Economic assets | Gold reserves, food stores, trade routes, key resources |
| Ongoing conflicts | Belligerents, current phase, chapter reference |

---

### 3.2 Geography
*Static with versioned updates when geography changes*

| Field | Description |
|---|---|
| Location name | Official and colloquial names |
| Description | Physical description as established in prose |
| Climate | Seasonal norms |
| Connections | Adjacent locations, routes |
| Distance records | Distance from this location to all other significant locations |
| Travel times | By foot / horse / ship — per route |

---

### 3.3 Cultures, Customs & Religion
*One record per culture or religious institution*

| Field | Description |
|---|---|
| Name | Culture or institution name |
| Core values | What they honour |
| Core fears | What they dread or despise |
| Key customs | Birth, death, marriage, conflict rituals |
| Class structure | How hierarchy is organised and enforced |
| Gender dynamics | Roles, constraints, exceptions |
| Religious beliefs | Theology, afterlife, relationship to magic |
| Political power | Institutional influence and reach |
| Languages / Dialects | If applicable |

---

### 3.4 History & Legends
*One record per significant historical or legendary event*

| Field | Description |
|---|---|
| Event name | How it is commonly known |
| True account | What actually happened (if known by author) |
| Believed account | What characters generally believe happened |
| Factional interpretations | How different cultures or factions remember it differently |
| Physical remnants | Ruins, artifacts, or locations associated with this event |
| Story significance | Why this history matters to the current narrative |
| Referenced in chapters | Where it has appeared in the text |

---

### 3.5 Magic System State
*Versioned per chapter snapshot*

| Field | Description |
|---|---|
| Current prevalence | Rare / Increasing / Decreasing / Stable |
| Confirmed capabilities | What magic has been shown to do, with chapter references |
| Confirmed limits | What magic cannot do, with chapter references |
| Confirmed costs | What using magic requires or takes |
| Known practitioners | Who can use it; how society views them |
| Unexplained phenomena | Magical events that remain unexplained in-world |
| Recent magical events | Chapter references for all recent magic use |

---

## MODULE 4: CONSEQUENCE LEDGER

### 4.1 Event → Consequence Chains
*One record per major event*

| Field | Description |
|---|---|
| Triggering event | Description and chapter reference |
| Immediate consequences | Already played out — chapter references |
| Short-term consequences | In progress or imminent |
| Long-term consequences | Projected but not yet written — flagged as pending |
| Affected characters | Who is affected and how |
| Cascade chain ID | If this event is part of a larger chain (link to 4.3) |

---

### 4.2 Time-Delayed Consequence Bombs
*One record per planted consequence*

| Field | Description |
|---|---|
| Planted event | What was set in motion, chapter reference |
| Nature of future consequence | What will eventually happen |
| Estimated detonation window | Chapter range |
| Status | Armed / Detonated / Defused |
| Detonation chapter | If detonated: chapter reference |

---

### 4.3 Cascade Chains
*One record per multi-step consequence sequence*

| Field | Description |
|---|---|
| Chain ID | Unique identifier |
| Chain sequence | A → B → C sequence of causally linked consequences |
| Current position | Which link in the chain has been reached |
| Remaining links | What consequences are still to play out |
| Characters involved | All characters affected across the full chain |

---

## MODULE 5: CONTINUITY REGISTRY

### 5.1 Physical Continuity
*One record per established physical detail*

| Field | Description |
|---|---|
| Subject | Character, object, or location |
| Detail | The specific established physical fact |
| Established in chapter | First appearance |
| Last referenced in chapter | Most recent appearance |

---

### 5.2 Logical Continuity

**Information Flow Log**
| Field | Description |
|---|---|
| Information item | The specific fact or secret |
| Transmitted from | Character who shared it |
| Transmitted to | Character who received it |
| Chapter reference | When transmission occurred |
| Method | Spoken / Written / Overheard / Inferred |

**Cause-Effect Chain Integrity**
*Flags for review when a new event is recorded whose cause has no established record.*

**Time Consistency Log**
*Records all travel durations and event sequences for cross-referencing.*

---

### 5.3 Contradiction Detection Log
*Auto-populated when a write operation conflicts with an established record*

| Field | Description |
|---|---|
| Contradiction ID | Unique identifier |
| Detected at chapter | When flagged |
| Nature | Physical / Logical / Knowledge / Timeline |
| Conflicting records | IDs of the two records in conflict |
| Description | Plain-language description of the conflict |
| Resolution status | Unresolved / Resolved / Accepted as intentional ambiguity |
| Resolution notes | How it was resolved, if applicable |

---

# APPENDIX: SKILL → WORLD BIBLE INTERFACE REFERENCE

| Skill | Reads from World Bible | Writes to World Bible |
|---|---|---|
| Finding a Seed | Nothing | Nothing |
| Defining Rough Endpoints | Nothing | Initialises Module 2.3 (threads), Module 2.4 (milestones as seeds) |
| Worldbuilding | Endpoints compass | Modules 3.1–3.5 |
| Research Integration | Nothing | Nothing (outputs to main agent only) |
| Character Conception | Module 3.1 (power map) | Nothing |
| Character Creation | Nothing (works from conception doc) | Modules 1.1, 1.2 (initial), 1.3 (initial) |
| Character Voice Differentiation | Module 1.1 | Nothing (outputs voice profile doc) |
| Character Integration with Plot | Modules 1.1, 1.2, 1.3, 3.1 | Modules 1.2, 1.3, 4.1 (initial entries) |
| Gardener Plotting System | Modules 1.1, 1.2, 2.3, 4.1 | Nothing (outputs scene parameters to main agent) |
| Multiple POV Structure | Modules 2.1, 2.2 | Nothing (outputs scheduling to main agent) |
| Braided Narrative Technique | Modules 2.2, 2.3 | Nothing (outputs analysis to main agent) |
| Conflict Layering | Modules 1.1, 1.3 | Nothing (outputs audit to main agent) |
| Plot Thread Tracking | Modules 2.3, 2.4 | Nothing (outputs status report) |
| Scene Construction | Modules 1.1, 1.2, 2.4, 3.x (relevant excerpt) | Nothing directly — main agent updates from output |
| POV Consistency Maintenance | Modules 1.1, 1.2 (knowledge matrix) | Nothing (outputs flags to main agent) |
| Pacing | Module 1.1 (psychological state) | Nothing |
| Layering History and Legend | Modules 3.3, 3.4 | Nothing |
| Professional Writing Techniques | Relevant excerpts only | Nothing |
| Consequence Cascade Implementation | Modules 1.1, 1.3, 4.1 | Module 4.1, 4.2, 4.3 |
| Balancing Realism and Fantasy | Module 3.5, relevant world state | Nothing (outputs audit) |
| Resolving Obstacles and Untangling Tangles | Last stable chapter state; relevant character records | Nothing |
| Self-Editing and Refinement | Nothing (works on chapter draft) | Nothing |
| POV Consistency Auditing | Modules 1.1, 1.2 | Nothing (outputs audit) |
