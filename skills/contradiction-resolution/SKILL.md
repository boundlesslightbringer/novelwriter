---
name: contradiction-resolution
description: >
  Analyses a blocked World Bible write, explains the contradiction to the
  orchestrator in plain language, proposes resolution options, and — once the
  orchestrator delivers a user-finalized decision — implements that decision
  directly into the MongoDB knowledge graph. Operates in two sequential modes:
  ANALYSE (explain + propose) and IMPLEMENT (execute the agreed fix). Never
  invoked by any subagent directly; always called by the orchestrator.
---

# Contradiction Resolution

## Identity

**Skill name:** `contradiction-resolution`
**Owner subagent:** Resolution Subagent (dedicated)
**Invoked by:** Orchestrator only — never by another subagent, never by the
WorldBibleManager directly.
**Never invokes:** Other skills. Never calls the WorldBibleManager directly.
The orchestrator re-triggers the WorldBibleManager after resolution is complete.

---

## Core

Receive a contradiction record from the orchestrator, translate it into
plain-language prose the orchestrator can relay to the user, and produce
concrete resolution options. After the user finalises a choice (via discussion
with the orchestrator), receive the decision and implement it as a set of
targeted writes to the MongoDB knowledge graph. Update Module 5.3 to close the
contradiction record. Signal the orchestrator that resolution is complete and
that the originating subagent must re-issue the blocked write.

---

## Two-Mode Operation

This skill operates in two distinct, sequential modes per contradiction event.
The orchestrator calls the skill twice — once per mode.

```
Mode 1 — ANALYSE
  Input:  contradiction record (from WorldBibleManager's BLOCKED output)
  Output: plain-language contradiction briefing + resolution options

          ↓ orchestrator surfaces to user; user discusses and finalises ↓

Mode 2 — IMPLEMENT
  Input:  the original contradiction record + the user-finalised resolution decision
  Output: MongoDB write operations (executed by this skill) + closed Module 5.3 entry
          + re-issue signal to orchestrator
```

The orchestrator is responsible for:
- Storing the contradiction record between Mode 1 and Mode 2 calls.
- Carrying the user's finalised decision into the Mode 2 input.
- Notifying the originating subagent to re-issue the blocked write after
  receiving the re-issue signal.

---

## MODE 1 — ANALYSE

### Input

```json
{
  "mode": "ANALYSE",
  "contradiction_record": {
    "contradiction_id": "<CONT-{chapter}-{timestamp}>",
    "detected_at_chapter": <int>,
    "nature": "Physical | Knowledge | Timeline | Logical",
    "conflicting_records": ["<module_id:doc_id>", "<module_id:doc_id>"],
    "description": "<plain-language description from contradiction-detection skill>",
    "resolution_status": "Unresolved",
    "resolution_notes": ""
  },
  "blocked_write": {
    "write_type": "<write_type>",
    "proposed_payload": { ... }
  },
  "prefetched_docs": [ ... ]
}
```

The orchestrator passes the same `prefetched_docs` that the WorldBibleManager
originally supplied to the contradiction-detection skill. This is the Resolution
Subagent's only view of the current World Bible state — it does not query
MongoDB in Mode 1.

### Output

```json
{
  "mode": "ANALYSE",
  "contradiction_id": "<from input>",
  "briefing": "<See Briefing Format below>",
  "resolution_options": [
    {
      "option_id": "A",
      "label": "<Short descriptive label, e.g. 'Adjust the timeline'>",
      "description": "<What this option changes and what it leaves intact>",
      "affected_modules": ["2.1", "5.2"],
      "complexity": "Low | Medium | High"
    }
  ],
  "recommended_option": "A",
  "recommendation_rationale": "<One sentence: why this option best preserves story logic>"
}
```

### Briefing Format

The `briefing` field must be prose the orchestrator can relay verbatim to the
user. Write it in plain language — no module IDs, no JSON field names. Structure
it as follows:

1. **What was being attempted** — one sentence describing the blocked write in
   story terms (e.g. "The story tried to record that Jon Snow arrives at King's
   Landing in Chapter 9.").
2. **What the contradiction is** — one or two sentences describing the conflict
   in story terms (e.g. "However, Jon was last seen at Castle Black just two
   days earlier, and the journey between those two locations takes at least
   eighteen days on horseback. The timeline doesn't hold.").
3. **What needs to be resolved** — one sentence framing the decision the user
   needs to make (e.g. "Either Jon's arrival needs to be pushed to a later
   chapter, or his departure from Castle Black needs to be moved earlier.").

Do not mention internal system mechanics, module numbers, or database operations
in the briefing. The user is a novelist, not a developer.

### How Many Resolution Options to Produce

- Always produce at least 2 options.
- Produce at most 4 options.
- Prefer fewer, more meaningful options over many overlapping ones.
- Always include one option that accepts the contradiction as intentional
  (authorial choice / deliberate ambiguity) if the nature of the contradiction
  makes that narratively plausible — label it "Accept as intentional ambiguity."
- Always designate one option as `recommended_option`.

### Generating Resolution Options by Contradiction Type

Use the following heuristics to derive options. The goal is narrative
coherence, not mechanical completeness.

**Physical contradiction**
- Option: Correct the physical detail in the established record (retcon the
  earlier description).
- Option: Introduce an in-story cause for the change (injury, disguise, curse,
  time passage) — add a cause event to the timeline.
- Option: Accept as intentional ambiguity (unreliable narrator, character
  misremembered).

**Knowledge contradiction**
- Option: Insert a missing information-transfer event into Module 5.2 that
  establishes how the character came to know this.
- Option: Downgrade the character's knowledge status (KNOWS → SUSPECTS or
  BELIEVES) so it is compatible with the existing record.
- Option: Retcon the earlier knowledge-state record if the earlier chapter
  established it in error.

**Timeline contradiction**
- Option: Shift the proposed event's date forward to respect travel time.
- Option: Shift the character's departure date earlier (if narratively
  compatible) so travel time is satisfied.
- Option: Introduce a faster travel method (ship, raven relay, magic) as a
  new world-state event.
- Option: Accept as intentional error (another character's false account,
  unreliable chronicle).

**Logical contradiction**
- Option: Insert the missing cause event into Module 4.1 or 5.2.
- Option: Revise the consequence record to reference a different, established
  cause.
- Option: Remove the consequence record entirely if the triggering event cannot
  be established.

---

## MODE 2 — IMPLEMENT

### Input

```json
{
  "mode": "IMPLEMENT",
  "contradiction_id": "<from Mode 1>",
  "contradiction_record": { ... },
  "blocked_write": {
    "write_type": "<write_type>",
    "proposed_payload": { ... }
  },
  "user_decision": {
    "chosen_option_id": "A | B | C | D | custom",
    "custom_instructions": "<optional free-text from user if chosen_option_id is 'custom'>",
    "accepted_as_intentional": true | false
  }
}
```

If `accepted_as_intentional` is `true`, skip all MongoDB writes and go directly
to the Module 5.3 closure step.

### Implementation Steps (execute in order)

**Step 1 — Derive the write operations.**

Translate the user's decision into a minimal, concrete set of MongoDB write
operations. Each operation must specify:

```json
{
  "operation": "update | insert | delete",
  "collection": "<module collection name>",
  "filter": { "<field>": "<value>" },
  "update_or_document": { ... }
}
```

Derive operations only from the chosen resolution option's `affected_modules`
and the user's instructions. Do not touch modules not involved in the
resolution.

**Step 2 — Execute the writes.**

Execute each derived write operation against MongoDB in the order listed. If any
write fails, halt and return a `RESOLUTION_FAILED` signal to the orchestrator
with the error details — do not partially commit.

**Step 3 — Close the Module 5.3 record.**

Update the contradiction record in Module 5.3 as follows:

```json
{
  "resolution_status": "Resolved | Accepted as intentional ambiguity",
  "resolution_notes": "<One sentence summarising what was changed and which option was chosen.>"
}
```

**Step 4 — Emit the re-issue signal.**

Return the output below. This is the orchestrator's cue to notify the
originating subagent to re-issue the blocked write.

### Output (success)

```json
{
  "mode": "IMPLEMENT",
  "status": "RESOLVED",
  "contradiction_id": "<from input>",
  "resolution_type": "Resolved | Accepted as intentional ambiguity",
  "writes_executed": [
    {
      "operation": "update | insert | delete",
      "collection": "<collection>",
      "filter": { ... },
      "outcome": "success"
    }
  ],
  "module_5_3_updated": true,
  "re_issue_signal": {
    "action": "RE_ISSUE_BLOCKED_WRITE",
    "originating_write_type": "<write_type from blocked_write>",
    "note": "Resolution complete. The originating subagent must re-issue the blocked write. The WorldBibleManager will re-run contradiction detection on the re-issued write."
  }
}
```

### Output (failure)

```json
{
  "mode": "IMPLEMENT",
  "status": "RESOLUTION_FAILED",
  "contradiction_id": "<from input>",
  "failed_at_step": <int>,
  "error_details": "<description of what failed>",
  "writes_executed_before_failure": [ ... ],
  "note": "No partial writes committed. Orchestrator must surface this failure to the user."
}
```

---

## Orchestrator's Full Responsibility Map

| Step | Owner |
|---|---|
| Receive BLOCKED verdict from WorldBibleManager | Orchestrator |
| Decide: route to Resolution Subagent or surface directly to user | Orchestrator |
| Call this skill in Mode 1 (ANALYSE) | Orchestrator |
| Relay the `briefing` to the user in natural language | Orchestrator |
| Present `resolution_options` to user (if desired) or invite free discussion | Orchestrator |
| Facilitate discussion with user until a decision is finalised | Orchestrator |
| Package finalised decision into `user_decision` object | Orchestrator |
| Call this skill in Mode 2 (IMPLEMENT) with the decision | Orchestrator |
| On RESOLVED: notify originating subagent to re-issue the blocked write | Orchestrator |
| On RESOLUTION_FAILED: surface error to user and determine next step | Orchestrator |
| Store contradiction record between Mode 1 and Mode 2 calls | Orchestrator |

---

## When the Orchestrator Routes Directly to the User (Skipping Mode 1)

The orchestrator may bypass Mode 1 entirely and surface the contradiction
directly to the user in natural language when:

- The contradiction is simple enough that the orchestrator can translate the
  `description` field from the contradiction record without analytical support.
- The user has previously expressed a preference to always be consulted directly
  on contradictions.

In this case, the orchestrator still calls Mode 2 after the user finalises a
decision. Mode 2 does not require Mode 1 to have run.

---

## Escalation: When Resolution Cannot Be Determined

If the user cannot or does not wish to resolve a contradiction in the current
session:

1. The orchestrator marks the contradiction record in Module 5.3 with
   `resolution_status: "Deferred"` and a note.
2. The blocked write remains discarded. The originating subagent does not
   re-issue.
3. Story generation **pauses** for the affected thread until the deferred
   contradiction is resolved in a future session.
4. The orchestrator logs the deferred contradiction in a **session-level
   pending list** so it surfaces automatically at the start of the next session.

There is no automatic fallback. All unresolved contradictions are user-owned.

---

## World Bible Interface

| Direction | Modules |
|---|---|
| Reads (Mode 1, via prefetched_docs only) | Subset of: 1.1, 1.2, 1.3, 2.1, 2.3, 2.4, 3.2, 4.1, 5.1, 5.2 — only what the orchestrator passes |
| Reads (Mode 2, via MongoDB direct access) | Only the specific documents targeted by the resolution writes |
| Writes (Mode 2) | Any module required by the resolution — derived from `affected_modules` in the chosen option |
| Always writes (Mode 2) | Module 5.3 (Contradiction Detection Log) — to close the record |

---

## Dependencies

**Upstream:** Orchestrator passes the contradiction record (originally produced
by the `contradiction-detection` skill via WorldBibleManager).

**Downstream:** On RESOLVED, orchestrator notifies the originating subagent
(Planning, Character, Plotting, Writing, or Consequence) to re-issue the blocked
write. WorldBibleManager then runs contradiction detection again on the re-issued
write.

---

## Boundary

This skill does **not**:

- Query MongoDB in Mode 1. It works only from the pre-fetched documents supplied
  in the input.
- Automatically determine whether to involve the user. That decision belongs to
  the orchestrator.
- Re-issue the blocked write itself. It signals the orchestrator; the
  orchestrator notifies the originating subagent.
- Fire the Reassess Trigger. The Reassess Trigger is retired. All unresolvable
  contradictions are escalated to the user via the orchestrator.
- Write to Module 5.3 in Mode 1. The 5.3 record is only updated in Mode 2 once
  the resolution is committed.
- Make story decisions. Resolution options are presented as choices; the user
  (via the orchestrator) decides.
- Partially commit writes. Either all resolution writes succeed or none are
  committed.

---

## Examples

Full worked examples (ANALYSE and IMPLEMENT): see [examples.md](examples.md).
