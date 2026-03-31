---
name: worldbuilding
description: Builds the physical, political, cultural, religious, and magical architecture of the story world using the iceberg principle — ten times more is constructed than will be shown on the page. Invoked once, after Defining Rough Endpoints, before the character pipeline begins. Main agent writes output to World Bible Modules 3.1–3.5.
---

# Worldbuilding

## Identity

**Purpose:** Construct the world the story inhabits. Not to fill it with exposition, but to make the author confident in every detail a POV character will notice, filter, and misunderstand. The iceberg principle governs everything: what appears on the page is the visible tip; the depth beneath it is what makes the surface feel real.

---

## Core

Build geography, political landscape, cultures, religion, and magic system using the iceberg principle — construct ten times more than will be shown. Output is structured world data for World Bible Modules 3.1–3.5. The world must feel like a consequence of itself: geography shapes politics, politics shapes culture, culture shapes religion, religion shapes the magic system's relationship to society.

---

## Input

### Required

1. **Endpoint compass document** from Defining Rough Endpoints — starting situation, draft ending destination, draft milestones, core conflict question, compass notes. The world must feel like the natural habitat of this compass; it should not be a generic setting applied to an abstract story.

### Optional

2. **Research Integration output** — factual reference material passed by the main agent when domains require grounding (e.g. medieval political structures, siege warfare, disease, trade economics, religious institutions). Research Integration is a separate skill invoked by the main agent only when needed; this skill does not call it.

---

## Output

Structured world data across five domains, formatted for main agent use in initialising World Bible Modules 3.1–3.5. Each domain is delivered as a structured record ready for World Bible insertion. The iceberg principle applies to every domain: the record should contain full depth, not only what will appear on the page.

### Domain 1 — Political & Power Map (→ Module 3.1)

For each significant territory or power centre:

- **Name** — official and colloquial
- **Current controller** — character or faction, with basis of power (military, religious, hereditary, economic)
- **Allegiances** — current alliances, stability rating, and what holds each alliance together
- **Active enmities** — ongoing conflicts, cause, and current phase
- **Military assets** — scale, location, command structure, loyalty (to institution vs. individual)
- **Economic assets** — key resources, trade routes, dependencies, vulnerabilities
- **Internal tensions** — factions within, grievances, succession risks, ideological fractures
- **What this power does not know** — blind spots, intelligence failures, wilful ignorance

### Domain 2 — Geography (→ Module 3.2)

For each significant location:

- **Name** — official and colloquial
- **Physical description** — as it would appear to a POV character passing through it (sensory, specific, not encyclopaedic)
- **Climate and seasonal norms**
- **Adjacent locations and routes** — with travel times by foot, horse, and ship where applicable
- **What the geography makes difficult** — not just what it enables; the constraints geography places on movement, agriculture, communication, and warfare
- **What the geography means culturally** — how the people who live here have been shaped by it, what they take for granted about the physical world that people elsewhere do not

### Domain 3 — Cultures, Customs & Religion (→ Module 3.3)

For each culture or religious institution:

- **Core values** — what they honour, and the specific forms that honouring takes (rituals, language, hierarchy)
- **Core fears** — what they dread or despise, and what they do to manage or suppress that fear
- **Key customs** — birth, death, marriage, conflict; the specific forms these rituals take and what they reveal about what the culture believes
- **Class structure** — how hierarchy is organised, how it is enforced, what mobility exists and under what conditions
- **Gender dynamics** — roles, constraints, exceptions, and what the culture's official position conceals
- **Religious beliefs** — theology, afterlife, the relationship between the sacred and the political, what the religion's institutions actually do versus what they claim to do
- **Political power** — where religious and cultural institutions have leverage, and where they do not
- **Internal contradictions** — what the culture believes about itself that is not true, and what it refuses to acknowledge

### Domain 4 — History & Legends (→ Module 3.4)

For each significant historical or legendary event:

- **Event name** — how it is commonly known, and whether that name encodes a particular interpretation
- **True account** — what actually happened (as known to the author; this may differ from anything any character believes)
- **Believed account** — what the majority of characters in this world generally take to be true
- **Factional interpretations** — how different cultures, factions, or classes remember it differently, and what those differences reveal about each faction's interests
- **Physical remnants** — ruins, artifacts, locations, or practices that survive from this event and are encountered in the present
- **Story significance** — why this history matters to the current narrative; what it makes possible, what it forecloses

### Domain 5 — Magic System State (→ Module 3.5)

- **Nature of magic** — what it is, ontologically (force, gift, knowledge, relationship, cost, transformation)
- **Current prevalence** — rare / increasing / decreasing / stable; whether this is in flux and why
- **Confirmed capabilities** — what magic can do, with specificity; the capabilities that will appear in the story
- **Confirmed limits** — what magic cannot do; limits that are known, and limits that are suspected but unconfirmed
- **Confirmed costs** — what using magic requires or takes from a practitioner (physical, psychological, social, temporal)
- **Known practitioners** — who can use it, how they come to that ability, how society views them (as threat, resource, sacred, marginal, criminal)
- **Institutional relationship** — how the political and religious power structures have responded to magic; whether they control, suppress, weaponise, or ignore it
- **Unexplained phenomena** — magical events or properties that remain unaccounted for within the world's own understanding; the iceberg below the iceberg

---

## Iceberg Principle

For each domain, the output must contain substantially more than will appear in the story. The visible surface — what a POV character notices and what the prose renders — should feel inevitable, not arbitrary. Inevitability comes from the depth beneath it.

**Test:** For any world detail that will appear on the page, three questions must be answerable from the record: *Why is it this way? What would change it? Who benefits from it remaining as it is?* If the record cannot answer those three questions, the iceberg is not deep enough.

**Note on scope:** This skill constructs the world's architecture, not its prose rendering. The Layering History and Legend skill integrates history, legends, and cultural texture into actual scenes; this skill provides the material that skill draws from.

---

## Boundary

- **Does not** write prose, scenes, or narrative description. Outputs structured data.
- **Does not** create character records. Character Conception reads Module 3.1 (political/power map) as its primary world context; this skill provides that input, but does not create characters.
- **Does not** plot scenes or assign events. Worldbuilding is background architecture, not plot.
- **Does not** update the World Bible directly. The main agent writes Modules 3.1–3.5 from this skill's output.
- **Does not** invoke Research Integration. The main agent decides when Research Integration is needed and passes its output to this skill as optional input.
- **Does not** produce an exhaustive encyclopaedia. The iceberg principle cuts both ways: depth of understanding, not length of record. If a detail has no bearing on any plausible story event, it does not belong in the output.

---

## Invocation

The main agent invokes Worldbuilding:

- **Once**, after Defining Rough Endpoints (Pass 1) has produced the endpoint compass, and before the character pipeline (Character Conception → Character Creation) begins. The compass orients the world; Character Conception reads Module 3.1 to conceive characters. This order is not optional.
- **Optionally**, for targeted expansion of a single domain — e.g. when a new region is introduced mid-story and needs a geography and culture record. In this case, the main agent passes the compass plus any relevant existing World Bible excerpts, and specifies which domain(s) to expand.
- **Reassess scenario:** If the Reassess Trigger fires and the world architecture is judged to be the source of the problem, this skill is re-invoked with the full original compass plus preservation constraints derived from already-written material.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (via main-agent-provided excerpts) | Endpoint compass (from Defining Rough Endpoints); optionally Research Integration output |
| **Main agent writes to** | Module 3.1 — Political & Power Map; Module 3.2 — Geography; Module 3.3 — Cultures, Customs & Religion; Module 3.4 — History & Legends; Module 3.5 — Magic System State |

---

## Dependencies

**Upstream:** Defining Rough Endpoints (required — endpoint compass document). Optionally: Research Integration (factual reference material for specific domains).  
**Downstream:** Module 3.1 is the primary world context for **Character Conception**. Modules 3.1–3.5 are subsequently read by **Scene Construction**, **Layering History and Legend**, **Balancing Realism and Fantasy**, and **Character Integration with Plot**.

---

## Instructions

### Step 1 — Internalise the compass

Read the endpoint compass fully before constructing anything. The world must feel like the natural habitat of this story — the political landscape, geography, and cultural tensions should make the starting situation legible and the milestones plausible. Ask: *What kind of world makes this story inevitable?*

### Step 2 — Establish geography first

Geography is the foundation. Political power is shaped by it. Culture is adapted to it. Magic systems interact with it. Build geography before politics or culture; let the physical reality constrain what can exist.

Work through each significant location the compass implies — where the story starts, where milestones are likely to occur, the broader region they sit within. Apply the iceberg: know more about each place than will be rendered.

### Step 3 — Build political and power structures from geography

Given the geography, ask: *Who controls what, and why?* Power follows from geography (control of routes, resources, defensible positions), from history (conquest, inheritance, religious sanction), and from current capacity (armies, wealth, legitimacy). Build each power centre as a consequence of the physical world and its own history.

Flag internal tensions: no power structure is stable. What is under pressure? Who wants what, and from whom?

### Step 4 — Develop cultures and religion as consequences of geography and politics

Culture is how people adapt to and make meaning from where they live and who rules them. Religion is how they explain what they cannot control. Build each culture and institution as a consequence of the geography and political landscape already established — not as a free-floating set of customs.

Flag the internal contradictions: what does this culture believe about itself that is not true?

### Step 5 — Layer history and legend

Every political and cultural reality has a history that made it. Identify the 2–4 historical events most relevant to the current story situation. For each, establish the true account (author-level knowledge) and the believed account (what characters generally accept). Identify factional disputes where relevant.

Physical remnants matter: the ruins, artifacts, and surviving practices that make the past present.

### Step 6 — Define the magic system

Build the magic system as a consequence of the world already established — its nature, distribution, costs, and institutional relationships must make sense given the geography, politics, culture, and history. A magic system that could be dropped into any world is not yet a worldbuilding output; it must be specific to *this* world.

Apply the iceberg: establish capabilities, limits, and costs with precision. Leave space for unexplained phenomena — the mysteries a POV character encounters that even the world's own scholars cannot account for.

### Step 7 — Apply the iceberg test

Before returning output, apply the three-question iceberg test to each significant world detail that will appear on the page: *Why is it this way? What would change it? Who benefits from it remaining as it is?* If the record cannot answer, deepen the relevant section.

### Step 8 — Assemble and return structured output

Return structured output per domain (3.1–3.5), formatted for main agent use. Do not write prose. Do not create characters. Do not plot events.

---

## Quality Checks

Before returning output, verify:

- [ ] Geography was established before politics and culture — the physical world shapes the social one.
- [ ] Each power structure has at least one internal tension flagged.
- [ ] Each culture has at least one internal contradiction flagged.
- [ ] History is present: at least 2–4 significant historical events with true account and believed account.
- [ ] Magic system is specific to this world — its nature and costs reflect the geography, culture, and history already built.
- [ ] Iceberg test applied: three questions answerable for all major world details.
- [ ] No prose written. No characters created. No plot events specified.
- [ ] No World Bible writes specified — output is structured data for the main agent to write.
- [ ] Output covers all five domains (3.1–3.5), or explicitly states which domains were out of scope and why.
