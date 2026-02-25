---
name: research-integration
description: Gathers and synthesises reference knowledge to inform any other skill requiring grounding in a specific domain. Supports two domain types: (1) Real-world factual domains — historical, geographic, scientific, social, political; (2) Speculative and fictional domains — science fiction genre conventions, magic system precedents, mythological structures, speculative science extrapolation, and creative precedents from existing literature and film. Invoked occasionally by the main agent when a skill needs domain grounding; not called automatically before every run of Worldbuilding or any other skill. Does not make story decisions. Does not update the World Bible.
---

# Research Integration

## Identity

**Purpose:** Produce accurate, structured reference material on a specific domain — whether real-world historical/factual or speculative/fictional — so that worldbuilding, characters, and plot structures have the grounding needed to feel authentic. This skill serves other skills. It provides material; it does not decide how that material is used.

---

## Core

Gather and synthesise reference knowledge for a specified domain and return it as structured reference notes. Covers both real-world factual domains (medieval warfare, political structures, economic systems, geography, etc.) and speculative/fictional domains (science fiction conventions, magic system precedents, mythological structures, speculative science, creative precedents from existing works). Outputs reference material to the main agent only. Does not make story decisions. Does not update the World Bible. Draws on fictional precedents with strict anti-plagiarism discipline — structural patterns only, never specific creative content.

---

## Input

The main agent provides:

1. **Domain type** — declare which category applies:
   - `Real-world factual` — historical periods, geographic realities, political systems, military logistics, economic structures, social history, religious institutions, natural sciences, etc.
   - `Speculative / fictional` — science fiction genre conventions, magic system typologies, mythological structures, speculative science extrapolation (plausible futures, theoretical physics applied narratively, etc.), creative precedents from existing literature and film.
   - `Hybrid` — a real-world factual domain that has significant fictional treatment worth surveying alongside the factual record (e.g. "plague" has both a factual history and a rich genre precedent in fiction).

2. **Specific research question or domain** — what territory needs to be covered and why. The more specific, the more useful the output. Examples:
   - *Real-world:* "How did succession crises work in medieval European kingdoms — specifically legal mechanisms, factional behaviour, and the gap between official legitimacy and practical power?"
   - *Speculative:* "What are the structural patterns in how science fiction has handled first contact scenarios — what tensions and failure modes recur across the genre?"
   - *Hybrid:* "How have both historical pandemics and science fiction plague narratives handled the social disintegration of institutions — what patterns recur, what does fiction usually amplify or distort?"

3. **Story context** (brief) — 1–3 sentences describing the story situation that created the research need. This orients the research toward what is actually useful rather than what is encyclopedically complete.

4. *(Optional)* **Specificity constraints** — e.g. "specifically Byzantine political structures, not Western European"; "specifically soft SF treatments, not hard SF"; "specifically pre-Tolkien fantasy magic systems."

---

## Output

The output structure adapts to the domain type. All sections apply to both domain types unless marked otherwise.

### 1. Domain Summary

A brief overview of the researched domain: its internal logic, key tensions, what holds it together and what makes it fragile. For speculative/fictional domains, this is a survey of the genre or fictional territory — what the domain looks like across the body of works that have engaged it, what structural patterns dominate, and where those patterns generate conflict or creative pressure. 150–300 words.

### 2. Key Structural Facts / Patterns

The material most directly relevant to the story context, organised by sub-topic.

*For real-world factual domains:* mechanisms (how things actually worked), tensions (where the system generated conflict), edge cases and exceptions (where rules broke down), and the human cost (what living inside this system meant for ordinary participants).

*For speculative/fictional domains:* recurring structural patterns across significant works; the tensions those patterns generate; the variations and subversions that have proven creatively fertile; what the structural logic of the domain implies (e.g. faster-than-light travel implies specific things about empire, communication, and the experience of isolation that most FTL stories must engage or deliberately subvert).

### 3. Useful Specifics

Concrete, sensory, or anecdotal material with atmospheric and narrative texture — the kind of specific reality that, once known, changes how a writer imagines a scene.

*For real-world domains:* how people in this domain talked about their situation; what the daily work looked like; what moments of absurdity or unexpected humanity occurred within it.

*For speculative/fictional domains:* specific images, structural innovations, or narrative solutions from existing works that have proven particularly resonant or generative — described at the level of structural pattern and thematic effect, never reproduced as specific text, imagery, or plot. See Anti-Plagiarism Discipline below.

### 4. What Is Commonly Misrepresented

*For real-world domains:* 2–4 common fictional misrepresentations — anachronism, structural simplification, perspective bias, dramatic exaggeration.

*For speculative/fictional domains:* 2–4 patterns that the genre or canon handles poorly, that have calcified into defaults, or that represent easy choices the story should actively consider avoiding (e.g. "most FTL narratives treat faster-than-light communication as equivalent to FTL travel, producing political structures that are empirically implausible given the physics they claim to inhabit").

### 5. Story-Relevant Cautions

Flags where the domain — factual or fictional — creates specific implications for this story:
- Where accuracy or fidelity to genre conventions might create structural problems for the compass.
- Where the domain intersects with sensitive territory requiring careful handling.
- Where common defaults in this domain may conflict with the story's stated themes or negative space constraints.

### 6. Anti-Plagiarism Note *(speculative/fictional domains only)*

A brief statement of what was drawn on and how it was used: which works informed the structural patterns described, what was extracted (structural logic, consequence patterns, thematic tension structures), and explicit confirmation that no specific creative content — characters, dialogue, imagery, plot, prose style — was reproduced. See Anti-Plagiarism Discipline below.

### 7. Further Questions

3–5 questions the research raises for the main agent, worldbuilding, character work, or subsequent research passes.

---

## Anti-Plagiarism Discipline for Speculative/Fictional Domains

When drawing on existing works of fiction, film, mythology, or genre canon, this skill observes strict anti-plagiarism discipline. The purpose of consulting fictional precedents is to extract **structural intelligence** — not content.

**What may be extracted and used:**
- Structural patterns: the shape of a dilemma, the logic of a consequence chain, the architecture of an impossible choice
- Thematic tension structures: how a particular theme has been explored, what tensions it generates, where it tends to resolve and where it tends to break open
- Worldbuilding logic: the internal consistency rules a precedent work established for its domain (e.g. the specific cost structure of a magic system — not the magic itself, but the *logic* of cost and consequence)
- Failure modes: patterns that recur across works and tend to produce unsatisfying results, including why
- Subversions and innovations: structural approaches that departed from defaults in productive ways — described functionally, not as specific creative content

**What may never be extracted or reproduced:**
- Specific characters, character names, or character designs
- Specific plot events, sequences, or structures that are the creative property of the source work
- Specific dialogue, prose, or imagery
- Specific worldbuilding inventions that are the creative identity of a source work (e.g. the specific rules of a named magic system, the specific political structures of a named fictional world)
- The overall "feel" or aesthetic signature of a source work

**Application:** When describing a structural pattern derived from a fictional source, the description must be sufficiently generalised that it could apply to multiple works and cannot be reverse-engineered to reproduce the source. The Anti-Plagiarism Note in the output confirms this discipline was applied.

---

## Boundary

- **Does not** make story decisions — presents options, implications, and patterns; does not recommend which to use.
- **Does not** update the World Bible. Output goes to the main agent as reference material only.
- **Does not** write prose, draft scenes, or produce narrative content.
- **Does not** build characters, worldbuilding structures, or plot from the research.
- **Does not** conduct research on a domain the main agent has not specified.
- **Does not** replace Worldbuilding, Character Creation, or any other skill — it provides input material those skills can use if the main agent passes it to them.
- **Does not** reproduce specific creative content from fictional sources — structural patterns only.

---

## Invocation

The main agent invokes Research Integration **selectively** — not automatically before every Worldbuilding run or skill invocation. It is invoked when:

- A specific domain requires grounding before worldbuilding, character work, or plotting in that domain can proceed authentically.
- The story has reached a point where a specific mechanism (military, political, technological, magical, social) is about to become narratively central and the main agent lacks the structural detail needed to construct a plausible fictional equivalent.
- A plot event or character situation implies a domain structure that the story needs to get right — even if surface details are fictional.
- The main agent needs a survey of how a specific speculative problem has been handled in genre fiction before making worldbuilding choices.

Research Integration is **not** invoked:
- Automatically before Worldbuilding.
- For domains where the story's fictional divergence from reality is so complete that factual grounding would be misleading.
- For questions that Worldbuilding or Character Creation can resolve from internal story logic alone.
- For speculative domains where the goal is creative originality rather than informed departure from precedent — in those cases, the main agent should proceed without this skill.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** | Nothing — no World Bible access |
| **Main agent writes to** | Nothing — output is reference material for the main agent only; no World Bible update occurs |

---

## Dependencies

**Upstream:** None. Research Integration can be invoked at any stage of the project.  
**Downstream:** Output is passed by the main agent as optional input to whichever skill required the grounding — most commonly **Worldbuilding**, but also potentially **Defining Rough Endpoints**, **Character Conception**, **Character Creation**, **Scene Construction**, or **Layering History and Legend**.

---

## Instructions

### Step 1 — Identify the domain type and scope

Confirm the domain type (real-world factual / speculative-fictional / hybrid). Define the scope:
- What specific aspect of the domain is being asked about?
- What level of depth is needed?
- What would make this research maximally useful to the skill that will consume it?

If the question is too broad, focus on the sub-domain most directly relevant to the story context and note the scope limitation.

### Step 2 — For real-world factual domains: identify what fiction commonly gets wrong

Before generating material, name 2–4 common fictional misrepresentations of this domain. This calibrates the output to add genuine value rather than confirming assumptions the story would have made anyway.

Common categories of fictional error:
- **Anachronism** — projecting modern values, technologies, or social structures backward
- **Structural simplification** — treating as a single clean mechanism what was actually contested and unstable
- **Perspective bias** — presenting the dominant-class view as the whole view
- **Dramatic exaggeration** — amplifying conflict at the expense of the administrative texture that makes conflict meaningful

### Step 3 — For speculative/fictional domains: survey the structural landscape

Before generating material, map the domain's genre territory:
- What structural patterns dominate this domain across significant works?
- Which patterns have been so frequently used they have become defaults?
- Where have the most interesting departures from those defaults occurred, and why were they productive?
- What tensions does the domain inherently generate, regardless of specific treatment?

This mapping positions the research to serve the story's stated genre and themes rather than producing a generic genre survey.

### Step 4 — Produce the domain summary

150–300 words. For real-world domains: what the system was for, who controlled it, where the friction points were, what it felt like from the inside. For speculative domains: what the structural landscape looks like, what patterns dominate, and where the most generative creative territory lies.

### Step 5 — Extract key structural facts / patterns relevant to the story context

With the story context in mind, select and organise the most narratively load-bearing material. Prioritise mechanisms that generate conflict naturally, exceptions and edge cases, and the human cost of the system.

For speculative domains, apply anti-plagiarism discipline throughout: extract structural logic and consequence patterns, not specific creative content.

### Step 6 — Compile useful specifics

Concrete material with atmospheric texture. For speculative domains, describe structural innovations in terms of their function and effect — not as descriptions of specific scenes, characters, or imagery from the source works.

### Step 7 — Write story-relevant cautions

Flag where the domain creates specific structural implications for this story, where accuracy requires careful handling, or where defaults in the domain conflict with the story's stated themes.

### Step 8 — Write the anti-plagiarism note (speculative/fictional domains)

Confirm: which bodies of work informed the structural patterns described; what was extracted (structural logic only); explicit confirmation that no specific creative content was reproduced.

### Step 9 — Generate further questions

3–5 questions the research raises for the main agent, for worldbuilding, for character work, or for a deeper research pass if needed.

### Step 10 — Return the structured reference notes

Return all sections to the main agent. Do not pass to any other skill. Do not update the World Bible. Do not recommend story decisions.

---

## Examples

For worked examples of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Domain type was declared and the output structure matches it.
- [ ] Research is specifically relevant to the question and story context — not a generic survey.
- [ ] For real-world domains: "What fiction commonly gets wrong" is present and substantive.
- [ ] For speculative/fictional domains: genre landscape is mapped before specifics; anti-plagiarism note is present and specific.
- [ ] For hybrid domains: factual and fictional portions are clearly distinguished.
- [ ] Anti-plagiarism discipline was applied throughout speculative/fictional sections — structural patterns only, no specific creative content reproduced.
- [ ] Story-relevant cautions are specific to this story context.
- [ ] No story decisions made — implications presented, not recommendations.
- [ ] No World Bible writes specified.
- [ ] No prose or narrative content produced.
