---
name: plot-thread-tracking
description: Maintains and reports on the registry of active, dormant, and resolved plot threads. Flags threads approaching overdue payoff windows. Identifies convergence opportunities across threads. Invoked at chapter boundaries, at convergence checkpoints, and when the main agent needs a structural health check on the story's thread load. Outputs a thread status report only — does not resolve threads or write scenes.
---

# Plot Thread Tracking

## Identity

**Purpose:** Give the main agent a clear picture of the story's full thread load at any point — what is active, what is dormant, what is approaching resolution, what is overdue, and what threads are moving toward each other in ways that could be developed or that must be managed. No thread is dropped; all setups have payoffs; this skill is the mechanism that ensures both.

---

## Core

Maintain and report on the registry of active, dormant, and resolved threads. Flag threads approaching overdue payoff windows. Identify convergence opportunities. Output a thread status report — current state of all threads, overdue flags, convergence opportunities. Does not resolve threads. Does not write scenes.

---

## Input

The main agent provides:

1. **World Bible excerpt — Module 2.3 (Plot Thread Registry):** The complete thread registry — all active, dormant, resolved, and abandoned threads, with their status, origin chapter, characters involved, expected convergence windows, dependencies, and resolution summaries.

2. **World Bible excerpt — Module 2.4 (Pending Payoffs & Foreshadowing):** All setup elements — Chekhov's guns, foreshadowing, consequence bombs, prophecies, in-world legends — with their planted chapter, expected payoff window, and resolution status.

3. *(Optional)* **Current chapter number** — so the skill can assess which threads and payoffs are approaching, within, or past their expected windows.

4. *(Optional)* **Endpoint compass** — the milestones from Defining Rough Endpoints. If the main agent is approaching a narrative milestone, thread status is assessed against whether the threads required by that milestone are sufficiently developed to support it.

> **Note:** This skill receives excerpts from the main agent. It does not access the World Bible directly.

---

## Output

**Thread status report** — a structured document containing:

### 1. Thread Load Summary

A quick-scan overview of the current thread registry:
- Total threads: [N]
- Active: [N]
- Dormant: [N]
- Resolved: [N]
- Abandoned: [N]
- Overdue (past expected convergence window): [N]
- Approaching window (within estimated 3–5 chapters): [N]

This summary gives the main agent an immediate sense of whether the story is carrying too many threads, too few, or a healthy load.

### 2. Active Thread Status

For each active thread, a one-line status report:
- Thread ID and name
- Characters involved
- Current status within the thread (what has happened so far in this thread; where it currently sits)
- Expected convergence window
- Whether the thread is **on track**, **at risk** (approaching its window without sufficient development), or **overdue** (past its window without resolution)
- Dependencies: what other threads must resolve before or alongside this one

### 3. Overdue Flags

A detailed entry for every thread or pending payoff that is past its expected window without resolution:
- Thread or payoff name and ID
- Expected window (chapter range)
- Current chapter (how far past the window)
- Why the overdue status matters: what narrative consequence does failing to resolve this thread have? (A thread that has been planted prominently and not paid off creates a structural debt that compounds. A setup element — especially a Chekhov's gun — that has been shown to the reader and not paid off damages trust in the narrative's internal logic.)
- Recommended action: resolve in next available chapter / revise the window estimate if the story's pacing has shifted / flag as intentional open-ending and mark accordingly in the registry.

### 4. Pending Payoffs Status

For each entry in Module 2.4:
- Setup element and type (Chekhov's gun / Foreshadowing / Consequence bomb / Prophecy / In-world legend)
- Planted chapter
- Expected payoff window
- Current resolution status: Pending / Paid off / Overdue
- If overdue: same treatment as Thread Overdue Flags above.

### 5. Convergence Opportunities

A list of threads and payoffs that are approaching each other — whose convergence would be structurally productive:
- Which threads are involved
- What the convergence would mean narratively (what happens when these threads intersect)
- Whether the convergence is planned (in the thread registry's convergence window or the endpoint compass's milestones) or discovered (emerging from the current story state without prior planning)
- Whether the convergence is imminent (within the next 2–3 chapters) or developing (building toward a later intersection)

For discovered convergences: flag explicitly that this is a Gardener moment — an organic intersection the story has grown toward. The main agent decides whether to develop it.

### 6. Thread Health Assessment

An overall assessment of the story's thread load:

- **Carrying too many threads:** If the active thread count is high relative to the number of chapters remaining until major milestones, some threads may need to be resolved, converged, or deliberately marked as open-endings before the story reaches its structural climax. A novel that is still opening new threads in its final third will not be able to close them satisfactorily.
- **Carrying too few threads:** If the active thread count is low and the story is still in its early or middle section, it may be operating too linearly — following a single thread without the complexity and interconnection that makes a multi-POV narrative feel like a living world. This is a structural observation, not a prescription to add complexity for its own sake.
- **Thread dependencies at risk:** If Thread B cannot resolve before Thread A, and Thread A is overdue, this is a cascade risk. Flag it.

### 7. No-Thread-Abandonment Check

A specific audit against the governing constraint: *no planted story thread is dropped without resolution or deliberate, tracked open-ending.*

For each thread marked `Abandoned` in the registry:
- Was the abandonment deliberate and tracked? (Is there a resolution note explaining the decision?)
- Or is the thread simply absent — no longer being developed, no resolution noted, no intentional open-ending recorded? If so, flag it as a structural gap requiring attention.

---

## Boundary

- **Does not** resolve threads — it reports on their status. The main agent (informed by Gardener Plotting System and Scene Construction) resolves threads through the act of writing.
- **Does not** write scenes or scene parameters.
- **Does not** audit braiding or POV structure at the sequence level. Braided Narrative Technique handles that.
- **Does not** decide which threads to develop or how. It reports status and flags urgency; the main agent decides.
- **Does not** update the World Bible. The thread status report is returned to the main agent; any changes to the Thread Registry (new threads, resolved threads, revised windows) are written by the main agent.

---

## Invocation

The main agent invokes Plot Thread Tracking:

- At every chapter boundary, as part of the standard chapter-completion sequence, to check whether any threads or payoffs require attention before the next chapter begins.
- When the main agent invokes the Convergence Checkpoint (from the system prompt's Block 4) — checking whether the major conflicts are beginning to move toward resolution and whether POV arcs are converging toward the rough endpoint.
- When the story feels structurally complex and the main agent has lost confidence in its thread load — a health check.
- When approaching a narrative milestone from the endpoint compass — to confirm that the threads and payoffs required to make the milestone land are sufficiently developed.

**Standard chapter-boundary sequence:**  
`[Chapter complete] → Plot Thread Tracking → [Main agent updates Module 2.3 and 2.4 if needed] → Multiple POV Structure → Gardener Plotting System`

---

## World Bible Interface

| Direction | Modules |
|-----------|---------|
| **Reads from** (as excerpts provided by main agent) | Module 2.3 (Plot Thread Registry), Module 2.4 (Pending Payoffs & Foreshadowing). Optionally: current chapter number, endpoint compass. |
| **Main agent writes to** | Nothing — status report is returned to the main agent; any World Bible updates to Module 2.3 or 2.4 are made by the main agent based on the report. |

---

## Dependencies

**Upstream:** Module 2.3 and Module 2.4 must be current before invocation. Both modules are updated by the main agent after each chapter using the Chapter Delta from Module 2.2.  
**Downstream:** Thread status report informs the main agent's decisions about upcoming chapter content, POV assignment (Multiple POV Structure), and scene parameters (Gardener Plotting System). Braided Narrative Technique uses Module 2.3 for convergence analysis; Plot Thread Tracking's report may be passed alongside Module 2.3 as supplementary context.

---

## Instructions

### Step 1 — Establish the current chapter position

If the current chapter number was provided, use it as the baseline for all window assessments. If not, derive the approximate current position from the Chapter Log's most recent entry.

### Step 2 — Triage the thread registry

Read the full Module 2.3. Categorise every thread:
- Active threads: still developing, not yet resolved.
- Dormant threads: introduced and left without resolution; not currently developing.
- Resolved threads: completed, with resolution summary.
- Abandoned threads: not resolved and no longer developing, with or without a tracked rationale.

Apply the no-thread-abandonment check immediately: any thread that is not Active, Dormant, or Resolved must have an abandonment rationale. If it does not, flag it.

### Step 3 — Assess active threads against their convergence windows

For each active thread:
- What is the expected convergence window?
- Is the thread on track to reach that window given its current development?
- Has the window passed? If so, it is overdue.
- Is the window within the next 3–5 chapters? If so, flag as approaching.

A thread is "at risk" when it is within its window but has not reached the development stage required to make resolution plausible. This is different from overdue — at risk threads still have time, but not much, and the main agent should begin planning how to bring them to resolution.

### Step 4 — Assess pending payoffs

For each entry in Module 2.4:
- What is the setup element and when was it planted?
- What is the expected payoff window?
- Has the window passed? Is it approaching?
- Is the setup element still in play — is the reader likely to remember it? (A Chekhov's gun planted in Chapter 2 but not paid off by Chapter 20 may need a brief re-activation before its payoff to ensure the reader still holds it.)

The no-thread-abandonment constraint applies here too: a setup element that is never paid off is a structural failure. The audit must surface all pending items that have no clear path to resolution.

### Step 5 — Identify convergence opportunities

Survey the active thread registry and pending payoffs. Look for:
- Thread pairs or groups whose characters, locations, or expected convergence windows overlap. Are there threads that would naturally resolve together — where the resolution of one creates the conditions for the resolution of another?
- Setup elements (Module 2.4) that are connected to active threads and whose payoff would coincide with a thread's convergence.
- Threads approaching milestones from the endpoint compass — threads that are moving toward the story's major structural moments.

For each convergence opportunity, state: which threads are involved, what the convergence would mean narratively, whether it is planned or discovered, and how imminent it is.

### Step 6 — Assess thread load health

Count active threads. Consider:
- How many chapters have been written? How many remain (estimated, based on the endpoint compass)?
- Is the active thread count consistent with the story's current structural position? (Early chapters can carry more open threads; later chapters must begin closing them.)
- Are there dependency chains at risk — threads that must resolve in a specific order, where the first link in the chain is overdue?

### Step 7 — Assemble and return the report

Compile the full report in the output structure defined above. Return it to the main agent. Do not update the World Bible directly.

---

## Example

For a worked example of input and output, see [examples.md](examples.md).

---

## Quality Checks

Before returning output, verify:

- [ ] Thread Load Summary is present with all counts.
- [ ] Every active thread has an on-track / at-risk / overdue assessment.
- [ ] Every overdue thread or payoff has a detailed flag with recommended action.
- [ ] Every pending payoff in Module 2.4 has a status assessment.
- [ ] Convergence opportunities distinguish planned from discovered.
- [ ] Thread health assessment is present.
- [ ] No-thread-abandonment check is present and explicit.
- [ ] No threads resolved. No scenes written. No World Bible writes specified.
