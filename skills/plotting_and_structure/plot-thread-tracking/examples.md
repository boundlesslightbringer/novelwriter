## Example

### Input shape

```
Current chapter: 14
Module 2.3 excerpt:
  Thread 004 — The Alliance Approach: Active. Origin: Ch. 1. Characters: Vara, Caradhen, Aldric (indirect). Expected convergence: Ch. 18–22. Status: Developing — Vara's assessment is being compiled; Caradhen has not committed; Aldric's contingency is active.
  Thread 007 — Sethric's Unspoken Judgment: Dormant. Origin: Ch. 9 (Caradhen chapter, Sethric background presence). Characters: Sethric, Caradhen. No convergence window established.
  Thread 012 — Aldric's Contingency: Active. Origin: Ch. 13. Characters: Aldric, unnamed third party, Caradhen (future). No convergence window established.
  Thread 002 — The Dowager's Trial: Resolved. Ch. 3. Resolution: The formal charges were filed.
  Thread 001 — The Regency's Legacy: Active. Origin: Ch. 1. Characters: Aldric, the Dowager (absent). Expected convergence: Ch. 25–30. Status: Background pressure; not yet directly developed.

Module 2.4 excerpt:
  Payoff 001: The Dowager's letter (Chekhov's gun). Planted: Ch. 4. Window: Ch. 15–20. Status: Pending.
  Payoff 002: Vara's assessment brief (Consequence bomb). Planted: Ch. 10. Window: Ch. 18–22 (when it reaches Aldric). Status: Pending.
  Payoff 003: Caradhen's thirty-year survival pattern (Foreshadowing). Planted: Ch. 7. Window: Open — will resolve when Caradhen is forced to commit. Status: Pending.
```

### Output shape

```
Thread Load Summary:
  Total: 5 | Active: 3 | Dormant: 1 | Resolved: 1 | Abandoned: 0
  Overdue: 0 | Approaching window (within ~5 chapters): 2 (Thread 004, Payoff 001)

Active Thread Status:
  T004 — The Alliance Approach: ON TRACK. Vara's assessment building (Ch. 10–14). Aldric's contingency active (Ch. 13). Expected convergence Ch. 18–22 — 4–8 chapters away. At current development pace, resolution is plausible within window.
  T012 — Aldric's Contingency: AT RISK (no window established). This thread was opened in Ch. 13 but has no established convergence window. It is causally linked to T004 (Aldric's response to Vara's assessment), but the link is not formalised. Recommend: establish convergence window as Ch. 18–22 (same as T004) and mark as a dependency.
  T001 — The Regency's Legacy: ON TRACK (long horizon). Window Ch. 25–30. Currently operating as background pressure. No action needed yet.

Dormant Thread Status:
  T007 — Sethric's Unspoken Judgment: DORMANT. No convergence window. This thread has been flagged in prior analyses as having activation potential. It is not overdue (no window was established) but the story state (Caradhen's psychological development in Ch. 7–14) is building toward conditions that would make activation organic. Recommend: establish a convergence window now before the activation moment passes organically without being tracked.

Overdue Flags: None.

Pending Payoffs Status:
  P001 — The Dowager's Letter: APPROACHING WINDOW. Planted Ch. 4; window Ch. 15–20; current chapter 14. This is the most urgent pending payoff. A Chekhov's gun planted ten chapters ago is approaching its window; if it is not paid off within the next 6 chapters, it will become overdue. The current story state (Vara's presence at the passes; Aldric's contingency) suggests the letter may connect to one of these active threads — has it been incorporated into Thread 004 or Thread 012? If not, it is running independent of the story's active momentum and will be harder to pay off.
  P002 — Vara's Assessment Brief: ON TRACK. This is a consequence bomb that will detonate when it reaches Aldric (expected Ch. 18–22, same as T004 convergence window). Currently building. No action needed.
  P003 — Caradhen's Survival Pattern: PENDING (open window). This foreshadowing element has no specific window — it resolves when Caradhen is forced to commit. This is structurally sound for its type, but the main agent should confirm that the story's trajectory will eventually create that forcing condition. If the endpoint compass does not contain a moment that forces Caradhen's commitment, this payoff has no guaranteed resolution path.

Convergence Opportunities:
  T004 + T012 + P002: These three are structurally linked and converging in the same chapter window (Ch. 18–22). When Vara's assessment (P002) reaches Aldric, his contingency (T012) activates in response — this is the braid's first major three-POV convergence point. This convergence is planned and on track. Recommend: ensure Aldric receives a POV chapter before the assessment arrives (so the reader knows what the contingency is before it activates).
  
  T007 + T004 (discovered): Sethric's dormant thread and the Alliance Approach are not linked in the registry, but the narrative logic of the passes chapters suggests that if Caradhen is forced to make a decision about the alliance, Sethric's unspoken judgment will become relevant — Sethric is the person whose opinion Caradhen cannot admit matters. This is a discovered convergence opportunity. It is not in the registry's dependency fields. Recommend: consider adding T007 as a dependency or related thread to T004 and establishing a convergence window.

Thread Health Assessment: HEALTHY with two flags.
  Flag 1: T012 needs a convergence window established. Currently operating without structural anchoring.
  Flag 2: P001 (the Dowager's letter) is approaching its window and appears disconnected from active threads. If it is not integrated with T004 or T012, it will need a chapter of its own to be paid off — which may interrupt the braid at a structurally sensitive moment.

No-Thread-Abandonment Check: PASS. All threads are accounted for. No abandoned threads without rationale.
```
