# Instructions for an LLM: Creating Skills for the GRRM LangGraph Novel-Writing Agent

This document instructs an LLM (the **skill drafter**) how to create individual skill documents for the agent described in `grrm_agent_specs.md`. Because the spec contains a large amount of specialized background and many skills (24 across 7 groups), these instructions assume **incremental drafting** (one skill at a time, or small batches) and define what context must always be available to the drafter.

---

## 1. Clarifications and Assumptions


| Topic                    | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Deliverable format**   | **Claude SKILL.md.** Each skill is produced as a Claude skill: one directory per skill containing `SKILL.md` (and optionally `reference.md`, `examples.md`). See §5 for structure and naming.                                                                                                                                                                                                                                                                                                                                                               |
| **Length**               | No maximum length per skill. The drafter may include as much as the skill needs; skills can be edited later.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Batching**             | Draft **one skill at a time**. Optionally, when drafting a group, the drafter may receive the full group subsection from the spec plus the permanent context.                                                                                                                                                                                                                                                                                                                                                                                               |
| **Order**                | Draft in **group order** (1 → 7) and, within a group, in **dependency order** (e.g. Character Conception before Character Creation).                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Audience**             | Skill documents are consumed by (a) the **main agent** (or human) when deciding when to call a skill and what to pass, and/or (b) **implementers** building LangGraph nodes/tools.                                                                                                                                                                                                                                                                                                                                                                          |
| **World Bible**          | Skills never read or write the World Bible directly; they receive **curated excerpts** from the main agent and return outputs that the main agent uses to update the World Bible. This is non-negotiable in every skill.                                                                                                                                                                                                                                                                                                                                    |
| **Research Integration** | A **separate skill** in Group 1 (Planning). It is **not** invoked on every run of Worldbuilding. The main agent invokes Research Integration **only when** factual grounding is needed for a given domain (e.g. medieval warfare, political structures, geography). Its output is reference material that the main agent may then pass into Worldbuilding or other skills as needed. Draft it with Group 1; in the skill document, state clearly that it is invoked occasionally when using Worldbuilding (or other skills that require factual grounding). |


---

## 2. Permanent Context (Always Available to the Skill Drafter)

The following must **always** be in the skill drafter LLM’s context when producing or revising any skill. Without it, skills may contradict the system or each other.

### 2.1 Governing Rules (from the spec)

- All skills are **discrete, callable units** invoked **only by the main agent**.
- Skills **do not access the World Bible directly**. They receive **curated excerpts** from the main agent and return outputs to the main agent for World Bible updating.
- Skills **do not call other skills**. Only the main agent orchestrates skill invocation.
- **Output format for all writing skills:** Draft prose. Refinement happens only in the Self-Editing and Refinement pass.

### 2.2 World Bible: High-Level Structure

The drafter only needs to know **which modules exist** and **what they represent**, not every field. Use this summary; refer to `grrm_agent_specs.md` Section 3 for full schemas.


| Module                                  | Purpose                                                                                                    |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **1.1** Character Directory             | Per-character state: physical, social, location, beliefs, desires, fears, arc type/stage, POV count.       |
| **1.2** Character Knowledge Matrix      | Per character: what they KNOW / SUSPECT / BELIEVE (possibly false) / DO NOT KNOW, with chapter and source. |
| **1.3** Relationship Records            | Per pair (directional): valence, power, history, secrets, trajectory.                                      |
| **2.1** Absolute Timeline               | Dates, events, simultaneous events, travel, weather.                                                       |
| **2.2** POV Chapter Log                 | Per chapter: POV, location, scene summary, cliffhanger, connections, chapter delta.                        |
| **2.3** Plot Thread Registry            | Per thread: status, origin, characters, convergence window, dependencies, resolution.                      |
| **2.4** Pending Payoffs & Foreshadowing | Setups, type, planted chapter, payoff window, resolution status.                                           |
| **3.1–3.5** World State                 | Political/power map, geography, cultures/religion, history/legends, magic system state.                    |
| **4.x** Consequence Ledger              | Event→consequence chains, time-delayed consequence bombs, cascade chains.                                  |
| **5.x** Continuity Registry             | Physical continuity, logical continuity (information flow, cause-effect, time), contradiction log.         |


### 2.3 Skill List and Grouping

- **Group 1 – Planning:** Finding a Seed, Defining Rough Endpoints, Worldbuilding, Research Integration. *(Research Integration is a separate skill invoked occasionally when the main agent needs factual grounding for Worldbuilding or other skills; it is not called on every Worldbuilding run.)*  
- **Group 2 – Character:** Character Conception, Character Creation, Character Voice Differentiation, Character Integration with Plot  
- **Group 3 – Plotting & Structure:** Gardener Plotting System, Multiple POV Structure, Braided Narrative Technique, Conflict Layering, Plot Thread Tracking  
- **Group 4 – Writing Execution:** Scene Construction, POV Consistency Maintenance, Pacing, Layering History and Legend, Professional Writing Techniques  
- **Group 5 – Consequence & Realism:** Consequence Cascade Implementation, Balancing Realism and Fantasy  
- **Group 6 – Problem-Solving:** Resolving Obstacles and Untangling Tangles  
- **Group 7 – Refinement:** Self-Editing and Refinement, POV Consistency Auditing

### 2.4 Skill ↔ World Bible Interface (Summary)

The drafter must know, for the skill being written, what the skill **reads from** (via main-agent-provided excerpts) and what the main agent **writes to** the World Bible using that skill’s output. Use the **Appendix: Skill → World Bible Interface Reference** in `grrm_agent_specs.md` as the authoritative table; a short summary is below.

- **Reads nothing:** Finding a Seed, Research Integration (output goes to main agent only).  
- **Reads endpoints / compass:** Defining Rough Endpoints (writes initial 2.3, 2.4), Worldbuilding (writes 3.1–3.5).  
- **Reads world/character state:** Character Conception (no write), Character Creation (writes 1.1, 1.2 initial, 1.3 initial), Character Voice Differentiation (no write), Character Integration with Plot (writes 1.2, 1.3, 4.1 initial).  
- **Reads plot/timeline/consequence:** Gardener Plotting System, Multiple POV Structure, Braided Narrative Technique, Conflict Layering, Plot Thread Tracking (outputs to main agent only).  
- **Reads scene/chapter draft + character/world:** Scene Construction (main agent updates from output), POV Consistency Maintenance, Pacing, Layering History and Legend, Professional Writing Techniques (outputs only).  
- **Reads character/relationship/consequence:** Consequence Cascade Implementation (writes 4.x).  
- **Reads draft + world/magic:** Balancing Realism and Fantasy (audit only).  
- **Reads tangle + last stable state:** Resolving Obstacles and Untangling Tangles (path forward only).  
- **Refinement:** Self-Editing and Refinement (chapter draft only), POV Consistency Auditing (refined draft + voice profiles + 1.2).

When drafting a skill, the drafter must **explicitly state** in that skill document which modules the main agent should provide as excerpts (reads) and which modules the main agent updates from the skill output (writes).

### 2.5 Subagent Architecture (Skill-to-Subagent Mapping)

Skills are organized into **7 groups**, with each group assigned to a **session-persistent subagent**. When the brain (main agent) needs functionality from a skill group, it delegates to the corresponding subagent, which internally routes to the appropriate skill(s).

| Subagent Name | Skill Group | Skills Included | Responsibility |
|---------------|-------------|-----------------|----------------|
| **Planning Subagent** | Group 1 – Planning | Finding a Seed, Defining Rough Endpoints, Worldbuilding, Research Integration | Story foundation, world construction, initial story compass |
| **Character Subagent** | Group 2 – Character | Character Conception, Character Creation, Character Voice Differentiation, Character Integration with Plot | Full character lifecycle from concept to plot integration |
| **Plotting Subagent** | Group 3 – Plotting & Structure | Gardener Plotting System, Multiple POV Structure, Braided Narrative Technique, Conflict Layering, Plot Thread Tracking | Scene planning, POV management, structure, thread tracking |
| **Writing Subagent** | Group 4 – Writing Execution | Scene Construction, POV Consistency Maintenance, Pacing, Layering History and Legend, Professional Writing Techniques | Draft prose generation, quality audits, refinement |
| **Consequence Subagent** | Group 5 – Consequence & Realism | Consequence Cascade Implementation, Balancing Realism and Fantasy | Event impact analysis, realism/fantasy balance audits |
| **ProblemSolver Subagent** | Group 6 – Problem-Solving | Resolving Obstacles and Untangling Tangles | Diagnostic support, resolution path finding |
| **Refinement Subagent** | Group 7 – Refinement | Self-Editing and Refinement, POV Consistency Auditing | Final polish, comprehensive auditing |
| **WorldBibleManager** | Infrastructure | N/A (all modules) | ALL World Bible I/O operations |

**Key Principle:** Each subagent receives ALL skills in its group at initialization. The subagent internally determines which skill(s) to apply based on the task context. This provides:
- Natural skill composition within domains
- Reduced subagent spawning overhead
- Better context retention across related operations

### 2.6 Domain Glossary (Minimal)

These terms appear in the spec and should be used consistently in skill documents. Include only the definitions needed for the skill at hand; do not duplicate the full spec.

- **Iceberg principle:** Build far more world/character detail than will be shown on the page; the visible surface implies the rest.  
- **Endpoint compass:** Starting situation, vague ending, 2–4 major milestones, core conflict question — loose, not a scene outline.  
- **Desire → action → consequence:** Character desire drives action; action produces consequences; consequences are tracked and honoured.  
- **Scene Purpose Test:** Every scene must advance plot and/or reveal character; otherwise it is cut.  
- **POV discipline:** One POV per chapter; no head-hopping; no omniscient narrator; all content filtered through that character’s perception and knowledge.  
- **Knowledge Matrix:** What each character knows, suspects, believes, or does not know — used to avoid knowledge violations.  
- **Voice profile:** Vocabulary range, sentence structure, observational focus, internal thought patterns, emotional processing (per POV character).  
- **Consequence ledger / cascade:** Recorded immediate, short-term, and long-term consequences of events; includes time-delayed “consequence bombs.”  
- **Tangle:** A story problem — e.g. character in impossible situation, non-converging plotlines, choice that breaks plot, unknown scene ending.  
- **Reassess Trigger:** Fired after N failed tangle-resolution attempts or when the World Bible contradiction system flags an unresolvable conflict; halts writing and triggers full reassessment.

---

## 3. Per-Skill Context (What to Give When Drafting One Skill)

When drafting a **single** skill, provide the drafter with:

1. **Permanent context** (Section 2 above).
2. **The full subsection for that skill** from `grrm_agent_specs.md` Section 1 (Core, Input, Output, Boundary, and Invocation if present).
3. **The corresponding row(s)** from the Appendix (Skill → World Bible Interface Reference) for that skill.
4. **Upstream skills** (if any): names and a one-line description of the output they produce that this skill consumes (e.g. “Character Conception produces a character concept: role, core contradiction, one-paragraph sketch”). This avoids the drafter inventing inputs that don’t exist.
5. **Downstream skills** (if any): names only, so the drafter can state “Output is used by X” where relevant.

Optionally, for **group-level** drafting (e.g. “draft all of Group 2”): provide the full Section 1 subsection for the entire group plus the Appendix rows for that group, and ask the drafter to produce one skill document per skill in dependency order, re-using the same permanent context.

---

## 4. What Each Skill Document Must Contain

Every skill document produced by the drafter must include the following. Adapt section titles to the target format (e.g. Claude SKILL.md vs. LangGraph tool spec).


| Section                   | Required content                                                                                                                                                                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Identity**              | Skill name (exactly as in the spec) and a short description (what it does and when the main agent should invoke it).                                                                                                                                    |
| **Core**                  | The single responsibility of the skill, in 1–3 sentences, matching the spec’s “Core.”                                                                                                                                                                   |
| **Input**                 | What the skill receives: (a) from the main agent (e.g. optional thematic constraints, validated seed, World Bible excerpts), and (b) which World Bible modules the main agent must supply as excerpts. List exact module IDs (e.g. 1.1, 2.3, 2.4).      |
| **Output**                | The artifact the skill returns (e.g. validated seed + questions, endpoint compass, structured world data, draft prose, audit report, pacing guidance). No World Bible writes inside the skill; the main agent updates the World Bible from this output. |
| **Boundary**              | What this skill **does not** do. Use the spec’s “Boundary” and add one or two “Does not …” lines to avoid overlap with neighbouring skills (e.g. “Does not write prose”; “Does not update the World Bible”).                                            |
| **Invocation**            | When the main agent should call this skill. Use the spec’s “Invocation” if present; otherwise derive from Section 2 “Skill Invocation Reference” in the spec.                                                                                           |
| **World Bible interface** | “Reads from: Module X, Y (as excerpts). Main agent writes to: Module Z (using this skill’s output).” For read-only or output-only skills, say so explicitly.                                                                                            |
| **Dependencies**          | Upstream: which skills’ outputs this skill expects. Downstream: which skills use this skill’s output (by name).                                                                                                                                         |


**Claude SKILL.md (required):** Each skill document must be a valid Claude skill. Include:

- **Metadata (YAML frontmatter):** `name` (skill-name-slug, lowercase, hyphens; see §5), `description` (brief, third-person, WHAT + WHEN; see Claude create-skill guidance).  
- **Instructions:** Step-by-step instructions for an agent (or human) executing this skill, using the domain glossary where needed.  
- **Examples:** At least one example of input → output (or “input shape → output shape”) where the spec allows it without spoiling the novel.  
- Optional: `reference.md` or `examples.md` in the same skill directory for progressive disclosure if the main SKILL.md would otherwise become very long.

---

## 5. Target Format: Claude SKILL.md

- **Format:** Claude skill per the “create-skill” skill: one directory per skill, with required `SKILL.md` (YAML frontmatter + markdown body). Optional: `reference.md`, `examples.md` in the same directory.  
- **Location:** One directory per skill, e.g. under `.Claude/skills/grrm-agent/` or a project path you choose (e.g. `skills/planning/finding-a-seed/`).  
- **Line limit:** None; include as much as the skill needs. Skills can be edited later.  
- **Naming:** Use a slug for the skill directory and for the `name` frontmatter field: lowercase letters, numbers, hyphens only (e.g. `finding-a-seed`, `character-creation`, `research-integration`, `resolving-obstacles-and-untangling-tangles`). Match the skill’s name in `grrm_agent_specs.md` Section 1.

---

## 6. Drafting Order and Batching

- **Order:** Draft skills in **group order** (1 → 7). Within each group, draft in **dependency order** (e.g. Character Conception → Character Creation → Character Voice Differentiation → Character Integration with Plot).  
- **Batching:** Prefer **one skill per drafting request**. If the context window allows, you may request “draft all skills in Group N” and provide the full Group N subsection plus the Appendix rows for that group; the drafter should still output **one document per skill** in order.  
- **Revisions:** When revising a skill, always provide **permanent context** again plus the current skill document and the spec subsection for that skill. Mention any specific boundary or interface conflict to fix.

---

## 7. Quality Checks for the Drafter

Before finalising a skill document, the drafter should verify:

- **No direct World Bible access** — the skill is described as receiving excerpts and returning an output; the main agent is responsible for writes.  
- **No skill-to-skill calls** — the skill does not invoke other skills.  
- **Boundary clarity** — at least 2–3 “Does not …” statements to avoid overlap with other skills.  
- **Input/output match** — inputs match upstream skill outputs and World Bible modules; output matches what downstream skills or the main agent expect.  
- **Glossary consistency** — domain terms (iceberg, POV discipline, consequence ledger, etc.) are used as in §2.6.  
- **Invocation** — when to call this skill is stated and consistent with the spec’s Skill Invocation Reference.

---

## 8. Reference to the Full Spec

The single source of truth is `**grrm_agent_specs.md`** in this project. It contains:

- **Section 1:** Full skill definitions (Core, Input, Output, Boundary, Invocation) for all 24 skills.  
- **Section 2:** System prompt (philosophy, immutable rules, decision frameworks, operational logic, skill invocation table).  
- **Section 3:** Complete World Bible schema (all modules and fields).  
- **Appendix:** Skill → World Bible Interface Reference (reads/writes per skill).

The skill drafter should **not** duplicate the full system prompt or full World Bible schema inside each skill. It should **reference** the spec and include only the minimal context (e.g. module IDs and one-line purpose) needed to execute or invoke that skill.

---

*End of instructions. Deliverable format is Claude SKILL.md (§5); §1 records all resolved assumptions.*