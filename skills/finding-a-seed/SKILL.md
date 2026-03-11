---
name: finding-a-seed
description: Generates and evaluates story seed ideas using four methods — Vivid Image, "What If?", Character-First, and Historical Inspiration — then validates and returns a single definitive seed plus a full log of all candidates considered. Requires at least one broad genre and at least one theme from the main agent (supplied by the human user). Supports multiple subgenres and standalone or interdependent thematic constraints. Invoked at the very start of a new project, before any worldbuilding or character work begins.
---

# Finding a Seed

## Identity

**Purpose:** Produce the generative starting point for the entire novel — one concrete, emotionally resonant image or moment, and the questions it makes inevitable. Everything else grows from this. The seed is not a plot summary, not a theme statement, not a premise. It is a vivid specific that compels forward movement.

---

## Core

Generate and evaluate seed ideas using four methods: Vivid Image, "What If?", Character-First, and Historical Inspiration. Operate within the genre and thematic constraints provided — which are required inputs, not optional. Select or synthesise the strongest candidate. Validate it against four criteria. Output the definitive seed, its questions, and a full Candidate Seeds Log so the main agent retains visibility into every seed considered and can reopen a strong alternative without re-invoking the skill.

---

## Input

The main agent provides (sourced from the human user):

### Required

1. **Broad genre** — exactly one top-level genre category. This is the story's genre home — the broadest category it inhabits. The seed must feel native to this genre. Examples: `Fantasy`, `Science Fiction`, `Historical Fiction`, `Horror`, `Literary Fiction`, `Thriller`, `Mythopoeic Fiction`.

2. **Primary theme(s)** — one or more thematic statements or questions the story is intended to explore. At least one is required. Themes may be stated as subjects ("legitimacy and the cost of inheritance"), as questions ("what does loyalty demand when the institution it serves has become corrupt?"), or as tensions ("the gap between what we make and what we become"). See Thematic Interdependencies below for how multiple themes relate to each other.

> **If either required input is absent, the skill must halt and return a request for the missing input. It does not proceed with assumed or inferred constraints.**

### Optional

3. **Subgenre(s)** — one or more subgenre qualifiers that narrow the broad genre. Multiple subgenres are allowed and encouraged; they stack. Subgenres shape tone, reader expectation, and what kind of seed will feel native to the work. Examples:
   - *Fantasy subgenres:* `Epic Fantasy`, `Dark Fantasy`, `Political Fantasy`, `Low Fantasy`, `Grimdark`, `Secondary World`, `Mythic Fantasy`
   - *Science Fiction subgenres:* `Space Opera`, `Hard SF`, `Biopunk`, `Climate Fiction`, `Generation Ship`, `First Contact`, `Cyberpunk`
   - *Cross-genre:* e.g. `Science Fantasy`, `Gothic Horror`, `Weird Fiction`

4. **Thematic interdependencies** — specifies how multiple themes relate. Three relationship types:
   - **Standalone:** Each theme is independently valid; a seed that addresses any one of them substantively passes. Multiple standalone themes give the skill more generative space.
   - **Interdependent:** Named themes must coexist in the seed and be in active tension with each other — the seed fails if it engages only one. Example: "Themes A and B are interdependent; the seed must hold both simultaneously."
   - **Primary + resonant:** One theme is load-bearing; others are welcome but not required. Example: "Theme A is primary; Theme B is a secondary resonance."
   
   If multiple themes are provided and no interdependency is specified, the skill treats them as standalone by default and notes this assumption in the output.

5. **Negative space constraints** — what the story should not be; territory to avoid; existing works the author does not want to echo.

---

## Output

### 1. Definitive Seed

- **The seed** — one concrete, specific image or moment, stated in 1–3 sentences. Vivid enough to generate scene. Contains latent emotional and narrative tension without explaining it.
- **Generation method** — which of the four methods produced it (or how methods were combined), and a brief account of the reasoning.
- **Validation record** — confirmation that the seed passes all four validation criteria (see Step 4), with a note on any criterion that required active consideration.
- **Genre and theme fit** — a brief statement of how the seed inhabits the stated genre and engages each required theme. For interdependent themes, explicitly state how both are held in tension within the seed.
- **Questions the seed raises** — 5–10 questions the seed makes inevitable. Not research questions, not plot questions — story questions that must eventually be answered but cannot yet be. At minimum: two character questions, two world/structural questions, one question not yet cleanly formulated.

### 2. Candidate Seeds Log

A record of every seed candidate generated before the definitive seed was selected. The main agent uses this log to review the reasoning trail and, if needed, reopen a strong alternative without re-invoking the skill. For each candidate:

- **Seed statement** — the candidate in 1–3 sentences.
- **Method** — which generation method produced it.
- **Strengths** — what was genuinely working; why it was a real contender.
- **Failure point** — the specific reason it was not selected: which validation criterion it failed, which genre/theme requirement it did not satisfy, or why the definitive seed was stronger. "Felt generic" is not a failure point — name the specific deficit.
- **Status** — one of:
  - `Rejected` — does not meet the bar for a viable alternative
  - `Merged` — elements of this candidate were incorporated into the definitive seed
  - `Held as alternative` — strong enough to serve as a fallback if the definitive seed is later judged insufficient; the main agent may reopen it without re-invoking the skill

> The log must contain at least one entry per generation method applied. A method that genuinely cannot produce a viable candidate for the given constraints should be logged with a brief explanation of why, rather than silently omitted.

---

## Boundary

- **Does not** begin writing prose, scenes, or chapters.
- **Does not** build the world, political landscape, magic system, or geography.
- **Does not** create characters, even sketchy ones.
- **Does not** define plot, structure, or endpoints.
- **Does not** proceed without at least one broad genre and at least one primary theme — halts and requests missing inputs instead.
- **Does not** produce a shortlist for the main agent to choose between — outputs one definitive seed with a log. If the definitive seed is rejected and no `Held as alternative` candidate suffices, the main agent re-invokes the skill, optionally with revised constraints.
- **Does not** update the World Bible. No World Bible exists at the point this skill is invoked.

---

## Invocation

The main agent invokes Finding a Seed:

- At the start of every new novel project, before any other skill is invoked. Genre, subgenre(s), and theme(s) must be sourced from the human user before invocation.
- If the Reassess Trigger fires and the main agent determines the story's generative core was never fully sound. In this case, the skill is re-invoked with the original constraints plus any elements from already-written material that must be preserved as additional constraints.

Not invoked mid-project under normal circumstances.

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** | Nothing — no World Bible exists at invocation |
| **Main agent writes to** | Nothing — output is passed to Defining Rough Endpoints; no World Bible update occurs |

---

## Dependencies

**Upstream:** None. This is the first skill invoked in any project. Requires genre and theme inputs from the main agent (sourced from the human user).  
**Downstream:** Validated seed document (including genre, subgenres, themes, thematic interdependencies, and questions) is passed to **Defining Rough Endpoints**.

---

## Instructions

### Step 1 — Parse and validate the constraints

Before generating anything, check the inputs:

- Is at least one broad genre present? If not, **halt and request it**.
- Is at least one primary theme present? If not, **halt and request it**.
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

> **For speculative genres (Fantasy, Science Fiction, Mythopoeic Fiction, etc.):** "Historical Inspiration" may draw on fictional precedents — existing works of literature, film, mythology, or genre canon — in addition to or instead of real historical events. The extraction rule is identical: take the *structural pattern* (the shape of the dilemma, the logic of the impossible choice, the consequence structure of the situation), not the characters, plot, setting, imagery, or any specific creative content from the source work. The Research Integration skill provides deeper support when fictional precedents need to be surveyed systematically.

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

### Step 7 — Assemble and return the full output

Return the complete output — definitive seed with validation record, genre/theme fit statement, questions, and Candidate Seeds Log — to the main agent. Do not proceed to worldbuilding or character work. Do not update the World Bible.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] At least one broad genre and at least one theme were provided — if not, output halted and inputs requested.
- [ ] Interdependent themes (if marked) are held in genuine tension within the definitive seed.
- [ ] Candidate Seeds Log contains at least one entry per method applied.
- [ ] At least one candidate is marked `Held as alternative` where the material supports it.
- [ ] Failure points in the log are specific, not generic.
- [ ] Definitive seed passes all four validation criteria; record confirms each.
- [ ] Questions are genuinely open — not answerable now; minimum counts met.
- [ ] No worldbuilding, character creation, or prose produced.
- [ ] No World Bible writes specified.
