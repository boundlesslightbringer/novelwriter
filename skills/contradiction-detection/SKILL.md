---
name: contradiction-detection
description: >
  Checks a proposed write operation against the existing World Bible state for
  contradictions before the WorldBibleManager commits it to the MongoDB knowledge
  graph. Invoked by the WorldBibleManager on every write — both node updates and
  edge updates. Returns CLEAR (write is safe to proceed) or BLOCKED (write
  contradicts established state) plus a structured contradiction record when
  blocked. Never queries MongoDB directly; operates solely on the payload and
  pre-fetched documents provided by the WorldBibleManager.
---

# Contradiction Detection

## Identity

**Skill name:** `contradiction-detection`
**Owner subagent:** WorldBibleManager
**Invocation point:** Before every write (node or edge) to the MongoDB knowledge
graph. This skill is a gate — the WorldBibleManager does not commit a write until
this skill returns CLEAR.

---

## Core

Check whether a proposed write to the World Bible conflicts with any established
record currently in the knowledge graph. Classify the contradiction by type if
one is found. Return a binary verdict (CLEAR / BLOCKED) and, when blocked, a
structured record ready for insertion into Module 5.3 (Contradiction Detection
Log). Do not suggest resolutions; that is the Reassess Trigger's job.

---

## The Performance Contract

The previous implementation failed because it attempted too broad a check in a
single pass. This skill enforces two hard constraints to keep every invocation
fast and bounded:

1. **Scoped context only.** The skill never sees more documents than the
   WorldBibleManager pre-fetched for this specific write. There is no full-graph
   scan.
2. **One contradiction type per check pass.** The skill runs up to four
   sequential, focused checks — stopping immediately at the first BLOCKED result.
   It does not run all four checks unconditionally.

---

## Input

The WorldBibleManager passes **all of the following** in a single structured
payload:

```
{
  "write_type": <string>,          // See Write Type Registry below
  "severity": "MINOR" | "MAJOR",  // Determined by WorldBibleManager before calling
  "target_module": <string>,       // e.g. "1.1", "2.1", "1.3"
  "proposed_payload": { ... },     // The full proposed write: fields + values
  "prefetched_docs": [ ... ]       // MongoDB documents pre-fetched by WorldBibleManager
                                   // Scope determined by severity tier (see below)
}
```

### What "pre-fetched docs" must contain

The WorldBibleManager determines which documents to fetch based on `severity`
and `write_type` using the **Module Scope Table** below. The skill checks only
what it is given. If a document was not fetched, the skill cannot check it — so
the WorldBibleManager is responsible for fetching the correct set.

---

## Severity Tiers and Module Scope

### How to classify severity

The WorldBibleManager classifies severity **before** calling the skill, using
this lookup. When in doubt, classify as MAJOR.

| Write Type | Severity | Modules to Pre-fetch |
|---|---|---|
| Update emotional / psychological state | MINOR | 1.1 only |
| Update arc stage | MINOR | 1.1 only |
| Add consequence record (no character state change) | MINOR | 4.1 only |
| Update plot thread status (Dormant ↔ Active; no resolution) | MINOR | 2.3 only |
| Add foreshadowing / pending payoff entry | MINOR | 2.4 only |
| Add relationship trajectory note (no power / valence change) | MINOR | 1.3 only |
| Update magic system state (minor: add unexplained phenomenon) | MINOR | 3.5 only |
| **Character location change** | **MAJOR** | 1.1, 2.1, 3.2, 5.1, 5.2 |
| **Character physical state change** (injury, death, appearance) | **MAJOR** | 1.1, 1.2, 1.3, 5.1 |
| **Character death or permanent removal** | **MAJOR** | 1.1, 1.2, 1.3, 2.3, 4.1, 5.1 |
| **Knowledge revelation** (character learns something significant) | **MAJOR** | 1.2, 5.2 |
| **Relationship power / valence change** | **MAJOR** | 1.3, 1.2, 5.1 |
| **New timeline event** | **MAJOR** | 2.1, 2.2, 5.2 |
| **World state change** (political, territorial, geographic) | **MAJOR** | 3.1, 3.2, 5.1 |
| **Magic system capability / limit change** | **MAJOR** | 3.5, 5.1 |
| **Consequence cascade** (major event with downstream effects) | **MAJOR** | 4.1, 4.2, 4.3, 1.1, 1.3 |
| **Plot thread resolution or creation** | **MAJOR** | 2.3, 2.4 |
| **Belief or current knowledge state update** (character now knows/suspects X) | **MAJOR** | 1.2, 5.2 |

---

## Check Sequence

Run checks in this order. **Stop and return BLOCKED at the first positive
result.** Do not run subsequent checks after a contradiction is found.

### For MINOR writes (1 check only)

Run only the check that corresponds to the single target module:

- **Module 1.x write** → Run Check 1 (Physical) if touching physical fields,
  or Check 4 (Logical) if touching knowledge/relationship fields.
- **Module 2.x write** → Run Check 3 (Timeline).
- **Module 3.x write** → Run Check 1 (Physical) for world-state physical facts.
- **Module 4.x write** → Run Check 4 (Logical) — verify the triggering event
  exists.

### For MAJOR writes (up to 4 checks, halt at first BLOCK)

Run checks in the order below, using only the pre-fetched documents relevant to
each check type:

---

### Check 1 — Physical Contradiction

**What it catches:** A proposed write changes an established physical fact
(character appearance, object description, geographic feature) without an
in-story cause present in the payload or pre-fetched documents.

**Documents needed:** Module 5.1 (Physical Continuity), Module 1.1 (Character
Directory) if character-related, Module 3.2 (Geography) if location-related.

**Rules:**
- If the proposed payload changes any field tracked in Module 5.1 for the same
  subject, check whether the current value in 5.1 matches the payload's new
  value.
- If they differ: is there a cause for the change present in the payload (e.g.
  an injury record, a disguise, a chapter reference explaining the change)?
- If no cause is present → **BLOCKED, type: PHYSICAL**.
- If the subject does not yet exist in Module 5.1 → **CLEAR** (new record, no
  conflict).

---

### Check 2 — Knowledge Contradiction

**What it catches:** A proposed write has a character act on, possess, or
transmit information that their Knowledge Matrix (Module 1.2) does not record
them as having at the current chapter.

**Documents needed:** Module 1.2 (Character Knowledge Matrix) for all characters
named in the payload.

**Rules:**
- If the proposed payload attributes an action, decision, or statement to a
  character that requires knowledge of fact X: check whether that character's
  1.2 record shows KNOWS or SUSPECTS X as of the current chapter.
- If the character's status for X is DOES NOT KNOW or is absent from 1.2 →
  **BLOCKED, type: KNOWLEDGE**.
- If the proposed payload *adds* a new knowledge record for a character: check
  whether a corresponding information-transmission event exists in Module 5.2
  (Information Flow Log) that would explain how they came to know it.
- If no transmission event exists and the knowledge wasn't established by direct
  experience (i.e., the character was not present at the event per Module 2.1)
  → **BLOCKED, type: KNOWLEDGE**.

---

### Check 3 — Timeline Contradiction

**What it catches:** A proposed write places a character at a location they
could not have reached given travel times, or records an event before its
established cause, or violates the Time Consistency Log.

**Documents needed:** Module 2.1 (Absolute Timeline), Module 3.2 (Geography —
distance/travel records), Module 5.2 (Time Consistency Log).

**Rules:**
- If the payload records a character's location at a given date: retrieve their
  last known location and the date from Module 1.1 / Module 2.1. Look up the
  travel time between the two locations in Module 3.2.
- If `(proposed date − last known date) < travel time between locations` →
  **BLOCKED, type: TIMELINE**.
- If the payload records a new event: check Module 2.1 for any event listed as
  a prerequisite or cause. If the cause event has a later date than the proposed
  event → **BLOCKED, type: TIMELINE**.
- If the payload introduces a new entry into Module 5.2 (Time Consistency Log):
  check that the proposed sequence does not contradict existing entries in that
  log → **BLOCKED if inconsistent, type: TIMELINE**.

---

### Check 4 — Logical Contradiction

**What it catches:** A proposed write records a consequence whose triggering
cause has no established record, or records an information-transfer event that
conflicts with existing information-flow records in Module 5.2.

**Documents needed:** Module 4.1 (Event → Consequence Chains), Module 5.2
(Information Flow Log, Cause-Effect Chain Integrity).

**Rules:**
- If the payload adds a new consequence record to Module 4.x: verify that the
  `triggering_event` referenced in the payload exists in Module 4.1 with a
  chapter reference. If no such event exists → **BLOCKED, type: LOGICAL**.
- If the payload adds an entry to Module 5.2 (Information Flow Log): verify
  that the `transmitted_from` character could have possessed this information
  at the stated chapter (cross-reference with their Module 1.2 record). If they
  do not have it → **BLOCKED, type: LOGICAL**.
- If the payload updates a world-state cause-effect chain (Module 5.2): verify
  that adding this entry does not create a circular dependency (effect precedes
  its own cause in the chain) → **BLOCKED if circular, type: LOGICAL**.

---

## Output

Always return one of the two structures below.

### CLEAR

```json
{
  "verdict": "CLEAR",
  "write_type": "<write_type from input>",
  "severity": "<MINOR | MAJOR>",
  "checks_run": ["Physical", "Knowledge"],
  "checks_skipped": ["Timeline", "Logical"],
  "skip_reason": "Severity MINOR — single-module check only"
}
```

### BLOCKED

```json
{
  "verdict": "BLOCKED",
  "write_type": "<write_type from input>",
  "severity": "<MINOR | MAJOR>",
  "checks_run": ["Physical"],
  "checks_skipped": ["Knowledge", "Timeline", "Logical"],
  "skip_reason": "Halted at first contradiction",
  "contradiction_record": {
    "contradiction_id": "<generate: CONT-{chapter}-{timestamp}>",
    "detected_at_chapter": <int>,
    "nature": "Physical | Knowledge | Timeline | Logical",
    "conflicting_records": ["<module_id:document_id_1>", "<module_id:document_id_2>"],
    "description": "<Plain-language description of the specific conflict. Name the fields, values, and documents involved. Be concrete — do not use vague language like 'possible inconsistency'.>",
    "resolution_status": "Unresolved",
    "resolution_notes": ""
  }
}
```

**The `contradiction_record` object is structured for direct insertion into
Module 5.3 (Contradiction Detection Log).** The WorldBibleManager inserts it
verbatim — this skill does not write to MongoDB.

---

## WorldBibleManager Responsibilities (What This Skill Does NOT Do)

This boundary is strict. The skill fails silently if these responsibilities are
violated.

| Responsibility | Owner |
|---|---|
| Classify write severity (MINOR / MAJOR) | WorldBibleManager |
| Determine which modules to pre-fetch using the Module Scope Table | WorldBibleManager |
| Execute the pre-fetch from MongoDB | WorldBibleManager |
| Pass the complete input payload to this skill | WorldBibleManager |
| Commit the write if verdict is CLEAR | WorldBibleManager |
| Insert `contradiction_record` into Module 5.3 if verdict is BLOCKED | WorldBibleManager |
| Return BLOCKED verdict + contradiction record to the orchestrator | WorldBibleManager |
| Decide whether to route to Resolution Subagent or surface to user | **Orchestrator** |
| Facilitate user discussion and finalise resolution decision | **Orchestrator** |
| Implement the finalised resolution into MongoDB | **Resolution Subagent** (`contradiction-resolution` skill) |
| Query MongoDB directly | **Prohibited** — this skill never touches MongoDB |
| Run more than one check after a BLOCKED result | **Prohibited** — halt immediately |

---

## Invocation

Called by the WorldBibleManager **before every write** — both node writes and
edge writes — to the MongoDB knowledge graph. The WorldBibleManager must
complete the severity classification and module pre-fetch before calling this
skill. This skill must complete and return before the WorldBibleManager proceeds
with the write or the Reassess Trigger.

**This skill is never called by the main agent directly.** It is internal to
the WorldBibleManager's write pipeline.

---

## World Bible Interface

| Direction | Modules |
|---|---|
| Reads (via pre-fetched excerpts only) | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.5, 4.1, 4.2, 4.3, 5.1, 5.2 — only the subset provided in `prefetched_docs` |
| Writes | **Nothing.** This skill never writes to the World Bible. |
| Main agent writes from output | Module 5.3 (Contradiction Detection Log) — WorldBibleManager inserts the `contradiction_record` on a BLOCKED result. |

---

## Dependencies

**Upstream:** WorldBibleManager (provides all input; this skill has no upstream
skill dependency).

**Downstream:** If CLEAR → WorldBibleManager commits the write. If BLOCKED →
WorldBibleManager returns the contradiction record to the orchestrator. The
orchestrator decides whether to route to the Resolution Subagent
(`contradiction-resolution` skill) or surface the contradiction directly to the
user in natural language. The Reassess Trigger (Condition B) is retired — all
contradiction resolution is handled by the orchestrator and Resolution Subagent.

---

## Examples

Full worked examples (CLEAR, BLOCKED timeline, BLOCKED knowledge): see [examples.md](examples.md).

---

## Boundary

This skill does **not**:

- Query MongoDB. It operates solely on the payload and pre-fetched documents passed by the WorldBibleManager.
- Suggest or implement resolutions to detected contradictions. Resolution is handled by the Reassess Trigger.
- Run more than one check after a BLOCKED result is produced.
- Run all four checks unconditionally. Checks halt at the first BLOCKED result; MINOR writes run one check only.
- Perform a full-graph scan. It checks only the modules in `prefetched_docs`.
- Write to Module 5.3 or any other module. The WorldBibleManager inserts the `contradiction_record` from the output.
- Fire the Reassess Trigger directly. The Reassess Trigger is retired. The
  WorldBibleManager returns a BLOCKED verdict to the orchestrator, which owns
  the resolution routing decision.
- Handle write failures unrelated to contradiction (e.g. network errors, schema validation). Those are WorldBibleManager concerns.
