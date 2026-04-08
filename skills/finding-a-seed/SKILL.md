---
name: finding-a-seed
description: Generates and evaluates story seed ideas using four methods — Vivid Image, "What If?", Character-First, and Historical Inspiration — then validates and returns a single definitive seed plus a full log of all candidates considered. Requires at least one broad genre and at least one theme from the brain (originally sourced from the user). Supports multiple subgenres and standalone or interdependent thematic constraints. Invoked at the very start of a new project, before any worldbuilding or character work begins.
---

# Finding a Seed

## Identity

**Purpose:** Produce the generative starting point for the entire novel — one concrete, emotionally resonant image or moment, and the questions it makes inevitable. Everything else grows from this. The seed is not a plot summary, not a theme statement, not a premise. It is a vivid specific that compels forward movement.

---

## Core

Generate and evaluate seed ideas using four methods: Vivid Image, "What If?", Character-First, and Historical Inspiration. Operate within the genre and thematic constraints provided — which are required inputs, not optional. Select or synthesise the strongest candidate. Validate it against four criteria. Return the definitive seed, its questions, and a full Candidate Seeds Log in the artifacts dict so the brain retains visibility into every seed considered and can reopen a strong alternative without re-invoking this skill.

---

## Input

### From brain context (`worker_request.context`)

The brain passes the following fields, originally sourced from the user:

#### Required

1. **`genre`** — Exactly one top-level genre category. The seed must feel native to this genre. Examples: `Fantasy`, `Science Fiction`, `Historical Fiction`, `Horror`, `Literary Fiction`, `Thriller`, `Mythopoeic Fiction`.

2. **`themes`** — One or more thematic statements or questions. At least one is required. May be stated as subjects, questions, or tensions.

> **If either required field is absent, this skill must halt and return a `need_input` status with a `follow_up_questions` entry requesting the missing field. Do not proceed with assumed or inferred constraints.**

#### Optional

3. **`subgenres`** — One or more subgenre qualifiers. Multiple allowed and encouraged; they stack.

4. **`thematic_interdependencies`** — Specifies how multiple themes relate: `"standalone"`, `"interdependent"`, or `"primary_plus_resonant"`. If multiple themes are provided and no interdependency is specified, treat as standalone and note this assumption in output.

5. **`negative_space`** — Territory to avoid; existing works the story should not echo.

### Fetched from Story State KG

None. This skill is invoked at the start of a new project. The Story State KG contains no prior story records at this point. No queries are needed.

---

## Output

All output is returned in `artifacts`. The brain applies the quality gate before deciding whether to route the seed document to `story_state_manager` for persistence.

### `artifacts` structure

```json
{
  "seed_document": {
    "seed": "<1–3 sentence seed statement>",
    "generation_method": "<which method(s) produced it and brief reasoning>",
    "validation_record": {
      "concreteness": "PASS — <one sentence explaining why>",
      "generative_tension": "PASS — <one sentence explaining why>",
      "emotional_necessity": "PASS — <one sentence explaining why>",
      "open_architecture": "PASS — <one sentence explaining why>"
    },
    "genre_theme_fit": "<brief statement of genre inhabitation and theme engagement>",
    "questions": ["<5–10 questions the seed makes inevitable>"]
  },
  "candidate_seeds_log": [
    {
      "seed_statement": "<1–3 sentences>",
      "method": "<generation method>",
      "strengths": "<what was genuinely working>",
      "failure_point": "<specific reason not selected>",
      "status": "Rejected | Merged | Held as alternative"
    }
  ],
  "genre": "<the genre passed in>",
  "subgenres": ["<list>"],
  "themes": ["<list>"],
  "thematic_interdependencies": "<standalone | interdependent | primary_plus_resonant>"
}
```

**CRITICAL: The four validation criteria (`concreteness`, `generative_tension`, `emotional_necessity`, `open_architecture`) MUST be nested INSIDE the `validation_record` object. Do not flatten them into the `seed_document` root.**

The `genre`, `subgenres`, `themes`, and `thematic_interdependencies` fields are echoed in artifacts so that downstream skills (Defining Rough Endpoints, Worldbuilding) receive them from the brain's context dict without requiring a KG read.

---

## Boundary

- **Does not** begin writing prose, scenes, or chapters.
- **Does not** build the world, political landscape, magic system, or geography.
- **Does not** create characters, even sketchy ones.
- **Does not** define plot, structure, or endpoints.
- **Does not** proceed without at least one broad genre and at least one primary theme — returns `need_input` status with a question requesting missing fields.
- **Does not** produce a shortlist for the brain to choose between — returns one definitive seed with a log. If the definitive seed is rejected by the brain and no `Held as alternative` candidate suffices, the brain re-delegates with revised constraints.
- **Does not** write to the Story State KG. All output is in artifacts.

---

## Invocation

The `planning_subagent` invokes this skill when the brain delegates a seed generation task, typically at the start of a new novel project. The brain passes genre and themes in `worker_request.context`.

This skill is not invoked mid-project under normal circumstances. If the Reassess Trigger fires and the brain determines the story's generative core was never fully sound, the brain re-delegates this skill with the original constraints plus any preservation constraints derived from already-written material (passed in context).

---

## Story State Interface

| Direction | Details |
|---|---|
| **Queries from Story State KG** | None — no KG queries needed; invoked at project start before any story state exists |
| **Returns in artifacts** | `seed_document` and `candidate_seeds_log` — returned to brain; brain decides whether to route to `story_state_manager` for persistence as initial `PlotThread` seeds in Module 2.3 |

---

## Dependencies

**Upstream:** Brain provides `genre` and `themes` inputs from the user via `worker_request.context`. No prior skill outputs required.

**Downstream:** The `seed_document` in artifacts is passed by the brain to the `planning_subagent` in the next delegation (Defining Rough Endpoints). The brain includes the seed document in the context dict of that subsequent delegation.

---

## Instructions

### Step 1 — Parse and validate the constraints

Before generating anything, check the brain context:

- Is `genre` present? If not, **return `need_input` with a follow-up question requesting it**.
- Is at least one entry in `themes` present? If not, **return `need_input` with a follow-up question requesting it**.
- If multiple themes are present, is their interdependency relationship specified? If not, treat as standalone and note the assumption.
- Map any tensions between the constraints themselves (e.g. a theme of "quiet domestic grief" against a subgenre of "Grimdark" is generative tension, not a contradiction — name it; it may point toward the most interesting seeds).

### Step 2 — Generate using each applicable method

Work through all four methods. Generate at least one genuine candidate per method before selecting the strongest. Do not stop at the first workable idea.

**Vivid Image**
Begin with a single image — specific, concrete, visually completable. Not a situation or a premise: an *image*. Check it against the genre and themes: does it feel native to the genre? Does it carry the thematic weight? Test: *What happened before this? What happens next? Why does it matter?* If those three questions don't arise immediately, the image is not yet a seed.

**"What If?"**
Pose a structural question about a human situation — not a world mechanic. Specific enough to imply a character and a crisis. Must engage at least one required theme directly. For interdependent themes, the situation should hold both in tension.

**Character-First**
Begin with a person in a specific impossible situation. The impossibility must come from inside (psychology, values, what they cannot bring themselves to do) as much as from outside (circumstances). Check that the character's situation engages the required themes and feels at home in the stated genre.

**Historical Inspiration**
Identify a real historical situation, crisis, or person whose structural pattern rhymes with the story territory. Extract the structural pattern — not the biography, setting, or specific facts — and transpose it fully into the story's world. The historical source must not be recognisable in the output.

> **For speculative genres (Fantasy, Science Fiction, Mythopoeic Fiction, etc.):** "Historical Inspiration" may draw on fictional precedents — existing works of literature, film, mythology, or genre canon — in addition to or instead of real historical events. The extraction rule is identical: take the *structural pattern*, not the characters, plot, setting, imagery, or any specific creative content from the source work.

### Step 3 — Filter all candidates against genre and thematic requirements

Before applying the four validation criteria, check each candidate against the provided constraints:

- Does it inhabit the stated genre authentically, or does it feel imported from another genre?
- Does it engage the required themes? For standalone themes: does it engage at least one substantively? For interdependent themes: does it hold both in genuine tension within a single image or situation?
- Does it respect the negative space constraints?

A candidate that fails genre or theme fit is logged with that specific failure regardless of its other strengths.

### Step 4 — Validate the strongest compliant candidate

Select the strongest genre/theme-compliant candidate. Apply all four validation criteria. The seed must pass all four.

**Criterion 1 — Concreteness**
Can you see it? Can you place a camera? A seed that exists only as an idea, a theme, or a relationship dynamic is not yet a seed. It must be an image or a moment.

**Criterion 2 — Generative Tension**
Does it generate more questions than it answers? A seed that feels complete — that explains itself, resolves its own tension — is a premise, not a seed. It should feel like a lock that implies a key that implies a door that implies a room full of things to be discovered.

**Criterion 3 — Emotional Necessity**
Is there a human stake that makes the tension matter? Not plot stakes — emotional stakes. A reader who knew nothing else about this story should feel that something important is at risk.

**Criterion 4 — Open Architecture**
Does the seed resist premature closure? The best seeds make several entirely different novels possible. If the seed already implies a specific plot structure or predetermined ending, it is too closed.

### Step 5 — Compile the Candidate Seeds Log

Write a log entry for every candidate generated in Step 2. Be honest about strengths — a weak candidate may still have one strong element worth preserving. Be specific about failure points. Mark any candidate that passed genre/theme requirements and at least two validation criteria as `Held as alternative`.

### Step 6 — Generate questions for the definitive seed

Write 5–10 questions the definitive seed makes inevitable: at least two character questions, at least two world/structural questions, at least one not yet cleanly formulated. All must be genuinely open — not answerable now.

### Step 7 — Assemble and return artifacts

Return the complete artifacts dict — definitive seed with validation record, genre/theme fit statement, questions, echoed genre/themes/subgenres, and Candidate Seeds Log. Set `status: "success"`.

Do not proceed to worldbuilding or character work. No Story State KG writes occur from this skill.

---

## Example

For a worked example of input and output, see [EXAMPLES.md](EXAMPLES.md).

---

## Quality Checks

Before returning output, verify:

- [ ] At least one broad genre and at least one theme were provided — if not, returned `need_input` with a follow-up question.
- [ ] Interdependent themes (if marked) are held in genuine tension within the definitive seed.
- [ ] Candidate Seeds Log contains at least one entry per method applied.
- [ ] At least one candidate is marked `Held as alternative` where the material supports it.
- [ ] Failure points in the log are specific, not generic.
- [ ] Definitive seed passes all four validation criteria; validation record confirms each.
- [ ] Questions are genuinely open — not answerable now; minimum counts met.
- [ ] Genre, subgenres, themes, and thematic_interdependencies are echoed in artifacts.
- [ ] No worldbuilding, character creation, or prose produced.
- [ ] No Story State KG writes from this skill.