---
name: research-integration
description: Gathers and synthesises reference knowledge to inform any other skill requiring grounding in a specific domain. Supports two domain types: (1) Real-world factual domains — historical, geographic, scientific, social, political; (2) Speculative and fictional domains — science fiction genre conventions, magic system precedents, mythological structures, speculative science extrapolation, and creative precedents from existing literature and film. Invoked selectively by the brain when a skill needs domain grounding; not called automatically before every Worldbuilding or other skill delegation. Does not make story decisions. Does not write to Story State KG.
---

# Research Integration

## Identity

**Purpose:** Produce accurate, structured reference material on a specific domain — whether real-world historical/factual or speculative/fictional — so that worldbuilding, characters, and plot structures have the grounding needed to feel authentic. This skill serves other skills. It provides material; it does not decide how that material is used.

---

## Core

Gather and synthesise reference knowledge for a specified domain and return it as structured reference notes in artifacts. Covers both real-world factual domains (medieval warfare, political structures, economic systems, geography, etc.) and speculative/fictional domains (science fiction conventions, magic system precedents, mythological structures, speculative science, creative precedents from existing works). Does not make story decisions. Does not write to Story State KG. Draws on fictional precedents with strict anti-plagiarism discipline — structural patterns only, never specific creative content.

---

## Input

### From brain context (`worker_request.context`)

1. **`domain_type`** — One of: `"real_world_factual"`, `"speculative_fictional"`, `"hybrid"`.

2. **`research_question`** — The specific territory to cover and why. The more specific, the more useful the output. Examples:
   - *Real-world:* `"How did succession crises work in medieval European kingdoms — specifically legal mechanisms, factional behaviour, and the gap between official legitimacy and practical power?"`
   - *Speculative:* `"What are the structural patterns in how science fiction has handled first contact scenarios?"`
   - *Hybrid:* `"How have both historical pandemics and science fiction plague narratives handled social disintegration of institutions?"`

3. **`story_context`** — 1–3 sentences describing the story situation that created the research need. Orients the research toward what is useful rather than what is encyclopedically complete.

4. **`specificity_constraints`** (optional) — e.g., `"specifically Byzantine political structures, not Western European"`.

### Fetched from Story State KG

None. This skill performs external research and synthesis. It does not query the Story State KG.

---

## Output

All output is returned in `artifacts`. The brain passes this output as `research_output` in the context dict of the subsequent skill delegation that requires the grounding.

### `artifacts` structure

```json
{
  "domain_type": "<real_world_factual | speculative_fictional | hybrid>",
  "research_question": "<echoed from input>",
  "domain_summary": "<150–300 word overview>",
  "key_structural_facts_or_patterns": {
    "<sub_topic_1>": "<notes>",
    "<sub_topic_2>": "<notes>"
  },
  "useful_specifics": "<concrete, sensory, or anecdotal material with narrative texture>",
  "what_is_commonly_misrepresented": ["<2–4 common fictional misrepresentations>"],
  "story_relevant_cautions": ["<flags where the domain creates implications for this story>"],
  "anti_plagiarism_note": "<speculative/fictional domains only — what was drawn on and how>",
  "further_questions": ["<3–5 questions the research raises>"]
}
```

---

## Boundary

- **Does not** make story decisions — presents options, implications, and patterns; does not recommend which to use.
- **Does not** write to Story State KG. Output is reference material in artifacts only.
- **Does not** write prose, draft scenes, or produce narrative content.
- **Does not** build characters, worldbuilding structures, or plot from the research.
- **Does not** conduct research on a domain the brain has not specified.
- **Does not** replace Worldbuilding, Character Creation, or any other skill — provides input material those skills use when the brain passes it in context.
- **Does not** reproduce specific creative content from fictional sources — structural patterns only.

---

## Invocation

The `planning_subagent` invokes this skill **selectively** — the brain delegates it only when a specific domain requires grounding before another skill can proceed authentically. It is not called automatically before every Worldbuilding delegation.

The brain delegates Research Integration when:
- A specific domain requires grounding before worldbuilding or character work in that domain can proceed.
- A plot event or character situation implies a domain structure the story needs to get right.
- A survey of how a specific speculative problem has been handled in genre fiction is needed before making worldbuilding choices.

Research Integration is **not** delegated when:
- The story's fictional divergence from reality is so complete that factual grounding would be misleading.
- Worldbuilding or Character Creation can resolve the question from internal story logic alone.
- Creative originality is the goal rather than informed departure from precedent.

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | None — performs external research only |
| **Returns in artifacts** | Structured reference notes; brain passes these as `research_output` in the context dict of the skill delegation that requires the grounding (typically `worldbuilding` or `character-conception`) |

---

## Dependencies

**Upstream:** Brain provides `research_question`, `domain_type`, and `story_context` from `worker_request.context`. No prior skill outputs required.

**Downstream:** `research_output` in artifacts is passed by the brain as context in the subsequent delegation that requires the grounding — most commonly `worldbuilding`, but also potentially `defining-rough-endpoints`, `character-conception`, `character-creation`, `scene-construction`, or `layering-history-and-legend` delegations.

---

## Anti-Plagiarism Discipline for Speculative/Fictional Domains

When drawing on existing works of fiction, film, mythology, or genre canon, this skill observes strict anti-plagiarism discipline. The purpose of consulting fictional precedents is to extract **structural intelligence** — not content.

**What may be extracted and used:**
- Structural patterns: the shape of a dilemma, the logic of a consequence chain, the architecture of an impossible choice
- Thematic tension structures: how a particular theme has been explored, what tensions it generates
- Worldbuilding logic: the internal consistency rules a precedent work established for its domain
- Failure modes: patterns that recur across works and tend to produce unsatisfying results
- Subversions and innovations: structural approaches that departed from defaults productively

**What may never be extracted or reproduced:**
- Specific characters, character names, or character designs
- Specific plot events, sequences, or structures that are the creative property of the source work
- Specific dialogue, prose, or imagery
- Specific worldbuilding inventions that are the creative identity of a source work
- The overall "feel" or aesthetic signature of a source work

---

## Instructions

### Step 1 — Identify the domain type and scope

Confirm the domain type from context. Define the scope: what specific aspect of the domain is being asked about, and what level of depth is needed? If the question is too broad, focus on the sub-domain most directly relevant to the story context and note the scope limitation.

### Step 2 — For real-world factual domains: identify what fiction commonly gets wrong

Before generating material, name 2–4 common fictional misrepresentations of this domain. This calibrates the output to add genuine value rather than confirming assumptions the story would have made anyway.

Common categories of fictional error:
- **Anachronism** — projecting modern values, technologies, or social structures backward
- **Structural simplification** — treating as a single clean mechanism what was actually contested and unstable
- **Perspective bias** — presenting the dominant-class view as the whole view
- **Dramatic exaggeration** — amplifying conflict at the expense of administrative texture

### Step 3 — For speculative/fictional domains: survey the structural landscape

Before generating material, map the domain's genre territory: what structural patterns dominate, which have become defaults, where the most interesting departures occurred, and what tensions the domain inherently generates regardless of specific treatment.

### Step 4 — Produce the domain summary

150–300 words. For real-world domains: what the system was for, who controlled it, where the friction points were. For speculative domains: what the structural landscape looks like and where the most generative creative territory lies.

### Step 5 — Extract key structural facts / patterns

With the story context in mind, select and organise the most narratively load-bearing material. Prioritise mechanisms that generate conflict naturally, exceptions and edge cases, and the human cost of the system.

For speculative domains, apply anti-plagiarism discipline throughout.

### Step 6 — Compile useful specifics

Concrete material with atmospheric texture. For speculative domains, describe structural innovations in terms of their function and effect — not as descriptions of specific scenes, characters, or imagery from source works.

### Step 7 — Write story-relevant cautions

Flag where the domain creates specific structural implications for this story, where accuracy requires careful handling, or where defaults in the domain conflict with the story's stated themes.

### Step 8 — Write the anti-plagiarism note (speculative/fictional domains)

Confirm: which bodies of work informed the structural patterns described; what was extracted (structural logic only); explicit confirmation that no specific creative content was reproduced.

### Step 9 — Generate further questions

3–5 questions the research raises for the brain, for worldbuilding, for character work, or for a deeper research pass if needed.

### Step 10 — Return artifacts

Return all sections in artifacts. Set `status: "success"`. No Story State KG writes.

---

## Examples

For worked examples of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Domain type was declared and the output structure matches it.
- [ ] Research is specifically relevant to the question and story context.
- [ ] For real-world domains: commonly misrepresented items are present and substantive.
- [ ] For speculative/fictional domains: genre landscape is mapped; anti-plagiarism note is present and specific.
- [ ] For hybrid domains: factual and fictional portions are clearly distinguished.
- [ ] Anti-plagiarism discipline applied throughout speculative/fictional sections.
- [ ] Story-relevant cautions are specific to this story context.
- [ ] No story decisions made — implications presented, not recommendations.
- [ ] No Story State KG writes from this skill.
- [ ] No prose or narrative content produced.