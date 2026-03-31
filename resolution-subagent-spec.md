# Resolution Subagent: Specification

## Placement in the Agent Architecture

The Resolution Subagent is an infrastructure subagent, alongside the
WorldBibleManager. It is not part of any skill group (Groups 1–5). It has no
writing, plotting, or character responsibilities. Its sole responsibility is
contradiction resolution: receiving a blocked write from the orchestrator,
analysing it, presenting it to the user, and implementing the user's finalised
decision into the MongoDB knowledge graph.

Updated subagent table for `grrm_agent_specs.md` Section 1:

| Subagent | Group | Skills | Purpose |
|---|---|---|---|
| Planning Subagent | Group 1 – Planning | Finding a Seed, Defining Rough Endpoints, Worldbuilding, Research Integration | Story foundation and world construction |
| Character Subagent | Group 2 – Character | Character Conception, Character Creation, Character Voice Differentiation, Character Integration with Plot | Full character lifecycle |
| Plotting Subagent | Group 3 – Plotting & Structure | Gardener Plotting System, Multiple POV Structure, Braided Narrative Technique, Conflict Layering, Plot Thread Tracking | Scene planning and structural management |
| Writing Subagent | Group 4 – Writing Execution | Scene Construction, POV Consistency Maintenance, Pacing, Layering History and Legend, Professional Writing Techniques | Draft prose generation and quality |
| Consequence Subagent | Group 5 – Consequence & Realism | Consequence Cascade Implementation, Balancing Realism and Fantasy | Event impact and realism audits |
| ~~ProblemSolver Subagent~~ | ~~Group 6 – Problem-Solving~~ | ~~Resolving Obstacles and Untangling Tangles~~ | ~~Shelved for first draft~~ |
| ~~Refinement Subagent~~ | ~~Group 7 – Refinement~~ | ~~Self-Editing and Refinement, POV Consistency Auditing~~ | ~~Shelved for first draft~~ |
| **WorldBibleManager** | Infrastructure | `contradiction-detection` skill | ALL World Bible I/O operations; contradiction detection gate |
| **Resolution Subagent** | Infrastructure | `contradiction-resolution` skill | ALL contradiction resolution; sole subagent with direct MongoDB write access outside of normal World Bible writes |

---

## Governing Rules

* The Resolution Subagent is invoked **only by the orchestrator**. No other
  subagent calls it directly.
* It receives **all context from the orchestrator**. It does not pull context
  from other subagents and does not hold session state of its own.
* It has **direct MongoDB write access** in Mode 2 (IMPLEMENT). This is the
  only subagent outside the WorldBibleManager with this access, and it is
  scoped strictly to the modules named in the resolution option's
  `affected_modules` list plus Module 5.3.
* It **does not make story decisions**. All resolution choices belong to the
  user. The subagent analyses, proposes options, and implements — it does not
  choose.
* It **does not call other skills**. The `contradiction-resolution` skill is
  its only skill, and it executes it internally.
* The **Reassess Trigger (Condition B)** is retired. The Resolution Subagent
  is its full replacement for all contradiction-related escalation. Unresolvable
  or deferred contradictions are owned by the user via the orchestrator, not by
  an automated trigger.

---

## Skill

The Resolution Subagent holds one skill: `contradiction-resolution`.

Full skill specification: `skills/contradiction-resolution/SKILL.md`.

Summary of that skill's two modes:

**Mode 1 — ANALYSE**
Receives: contradiction record + blocked write + pre-fetched World Bible
documents (passed by the orchestrator from the WorldBibleManager's BLOCKED
output).
Produces: a plain-language briefing for the user + 2–4 resolution options +
a recommended option with rationale.
MongoDB access: none. Operates solely on documents passed in the input.

**Mode 2 — IMPLEMENT**
Receives: contradiction record + blocked write + user-finalised decision
(packaged by the orchestrator after user discussion).
Produces: targeted MongoDB writes implementing the resolution + Module 5.3
closure + a RE_ISSUE_BLOCKED_WRITE signal to the orchestrator.
MongoDB access: scoped to `affected_modules` from the chosen resolution option,
plus Module 5.3.

---

## Full Lifecycle of a Contradiction Event

```
1.  A subagent (Planning, Character, Plotting, Writing, or Consequence)
    produces an output that requires a World Bible write.

2.  The main agent passes that write to the WorldBibleManager.

3.  WorldBibleManager classifies the write severity (MINOR / MAJOR),
    pre-fetches the relevant MongoDB documents, and calls the
    contradiction-detection skill.

4.  contradiction-detection returns either:
      CLEAR  → WorldBibleManager commits the write. Story proceeds.
      BLOCKED → WorldBibleManager returns the contradiction record
                and the pre-fetched documents to the orchestrator.
                The blocked write is discarded.

5.  Orchestrator receives the BLOCKED verdict.

6.  Orchestrator decides one of two paths:

      Path A — Route to Resolution Subagent first:
        Orchestrator calls contradiction-resolution in Mode 1 (ANALYSE).
        Resolution Subagent returns a plain-language briefing and
        resolution options.
        Orchestrator presents the briefing and options to the user.

      Path B — Surface directly to user:
        Orchestrator translates the contradiction record's description
        field into natural language and presents it to the user directly,
        without calling Mode 1.
        Orchestrator uses Path B when the contradiction is simple enough
        to explain without analytical support, or when the user has
        expressed a preference to always be consulted directly.

7.  User and orchestrator discuss the contradiction. Orchestrator
    facilitates until the user arrives at a finalised decision.
    The user may: choose a presented option, propose a custom resolution,
    or defer the contradiction to a future session.

8a. User finalises a resolution:
        Orchestrator packages the decision into the user_decision object.
        Orchestrator calls contradiction-resolution in Mode 2 (IMPLEMENT).
        Resolution Subagent executes the targeted MongoDB writes.
        Resolution Subagent updates Module 5.3 to Resolved or
        Accepted as intentional ambiguity.
        Resolution Subagent returns RE_ISSUE_BLOCKED_WRITE signal.
        Orchestrator notifies the originating subagent to re-issue
        the blocked write.
        WorldBibleManager runs contradiction-detection again on the
        re-issued write. If CLEAR, the write is committed. Story resumes.

8b. User defers the contradiction:
        Orchestrator updates Module 5.3 directly:
          resolution_status → "Deferred"
          resolution_notes  → summary of deferral reason
        Orchestrator logs the contradiction_id in the session-level
        pending list.
        Story generation pauses for the affected thread.
        At the start of the next session, the orchestrator surfaces
        all deferred contradictions from the pending list before
        any writing resumes.

8c. Mode 2 write fails (RESOLUTION_FAILED):
        No partial writes have been committed.
        Resolution Subagent returns the error details.
        Orchestrator surfaces the failure to the user and determines
        the next step (retry, custom resolution, or deferral).
```

---

## Orchestrator Responsibilities in the Contradiction Lifecycle

The orchestrator owns the following decisions and actions. None of these are
delegated to the Resolution Subagent.

| Responsibility | Notes |
|---|---|
| Receive BLOCKED verdict from WorldBibleManager | Includes the contradiction record and pre-fetched docs |
| Choose Path A or Path B | Based on contradiction complexity and user preferences |
| Call Mode 1 (if Path A) | Passes contradiction record + blocked write + pre-fetched docs |
| Relay briefing to user | Verbatim from Mode 1 output; in natural language |
| Present resolution options to user | May present Mode 1 options or invite free discussion |
| Facilitate discussion until decision is finalised | The orchestrator does not finalise the decision — the user does |
| Package user decision into `user_decision` object | Translates discussion outcome into structured input for Mode 2 |
| Call Mode 2 with finalised decision | Passes contradiction record + blocked write + user_decision |
| Notify originating subagent to re-issue blocked write | On RE_ISSUE_BLOCKED_WRITE signal from Mode 2 |
| Handle RESOLUTION_FAILED | Surface error to user; determine retry, custom resolution, or deferral |
| Update Module 5.3 on deferral | Sets resolution_status to "Deferred"; adds to session pending list |
| Surface deferred contradictions at session start | Before any writing resumes in the next session |
| Store contradiction record between Mode 1 and Mode 2 | The subagent has no state; the orchestrator holds it |

---

## Initialisation

The Resolution Subagent is **session-persistent**, like all other subagents. It
is initialised at the start of every writing session alongside the
WorldBibleManager and the five skill-group subagents.

At initialisation, the Resolution Subagent receives:

* The full `contradiction-resolution` skill document.
* The World Bible module structure summary (module IDs and one-line purposes —
  not full schemas). This is needed for Mode 1 option generation, where the
  subagent must correctly identify `affected_modules` per resolution option.
* The current session's deferred contradiction list from the orchestrator, if
  any deferred contradictions exist from prior sessions. The subagent does not
  act on these at initialisation — it holds them in case the orchestrator routes
  one for resolution during the session.

The Resolution Subagent does **not** receive:

* World Bible content (it receives this per-call via `prefetched_docs` in Mode 1
  and via direct MongoDB access in Mode 2).
* Any skill documents from Groups 1–5 (it has no writing, plotting, or character
  responsibilities).
* The full system prompt (it operates from its own skill document and the
  governing rules in this spec).

---

## MongoDB Access Scope

The Resolution Subagent has direct MongoDB write access in Mode 2 only. This
access is strictly scoped:

* **Writes:** Only to the modules listed in the chosen resolution option's
  `affected_modules` field, plus Module 5.3.
* **Reads:** Only the specific documents required to execute the resolution
  writes. No full-collection scans.
* **In Mode 1:** No MongoDB access at all. The subagent works from
  `prefetched_docs` only.

This scoping is enforced by the Resolution Subagent itself, not by external
access control. The subagent must not query or write any module not named in
`affected_modules` or 5.3, even if it believes additional changes would be
beneficial. Additional changes are the user's decision in the next resolution
cycle.

---

## What This Subagent Does Not Do

* Does not make story decisions. Resolution options are proposals; the user
  decides.
* Does not invoke other subagents. It signals the orchestrator; the orchestrator
  notifies the originating subagent.
* Does not call other skills. The `contradiction-resolution` skill is its only
  skill.
* Does not hold state between sessions. The orchestrator owns the pending
  deferred contradiction list.
* Does not fire the Reassess Trigger. The Reassess Trigger (Condition B) is
  retired. Unresolvable contradictions are escalated to the user.
* Does not partially commit writes. In Mode 2, either all writes succeed or none
  are committed and RESOLUTION_FAILED is returned.
* Does not proactively scan the World Bible for contradictions. It only acts on
  contradictions surfaced by the WorldBibleManager's `contradiction-detection`
  skill and passed by the orchestrator.
* Does not modify the blocked write. The blocked write is discarded at Step 4
  and re-issued by the originating subagent after resolution. The Resolution
  Subagent does not alter, queue, or re-execute it.

---

## Interaction with the Reassess Trigger

The Reassess Trigger's Condition B ("World Bible Contradiction Detection system
flags a contradiction that cannot be resolved without rewriting established
chapters") is **retired in full**. It is replaced by the Resolution Subagent
lifecycle defined above.

Condition A of the Reassess Trigger ("main agent cannot find a path forward
after N consecutive attempts") remains unchanged. It is unrelated to
contradiction detection and is not affected by this subagent.

The updated Reassess Trigger definition for `grrm_agent_specs.md` Section 2,
Block 6:

> **Reassess Trigger**
>
> The Reassess Trigger fires when the following condition is met:
>
> * **Condition A:** The main agent cannot find a path forward after N
>   consecutive attempts to continue the story. *(N = implementation-defined
>   threshold.)* The agent halts, documents the tangle, and waits for human
>   input.
>
> *(Condition B — World Bible contradiction detection — is retired. All
> contradiction resolution is handled by the Resolution Subagent and
> orchestrator. See Resolution Subagent Specification.)*
>
> When the trigger fires:
> 1. Halt all writing.
> 2. Document the specific tangle, including the last stable chapter state
>    and the character logic that led to the impasse.
> 3. Perform a full World Bible consistency review.
> 4. Re-evaluate character logic from the last stable chapter state.
> 5. If the endpoint is no longer reachable or no longer valid: re-invoke
>    Defining Rough Endpoints with the current world state as input.
> 6. Only resume writing once a clear path forward exists (either discovered
>    through re-evaluation or provided by human input).

---

## Skill → World Bible Interface Reference (Resolution Subagent rows)

These rows should be added to the Appendix table in `grrm_agent_specs.md`:

| Skill | Reads from World Bible | Writes to World Bible |
|---|---|---|
| `contradiction-resolution` (Mode 1 — ANALYSE) | Pre-fetched excerpts passed by orchestrator: subset of 1.1, 1.2, 1.3, 2.1, 2.3, 2.4, 3.2, 4.1, 5.1, 5.2 | Nothing |
| `contradiction-resolution` (Mode 2 — IMPLEMENT) | Only documents targeted by resolution writes (direct MongoDB read) | Modules named in `affected_modules` of the chosen option; always Module 5.3 |
