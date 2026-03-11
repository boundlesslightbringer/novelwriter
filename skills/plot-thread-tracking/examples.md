## Example

### Input shape

```
Current chapter: 14
Invocation mode: Convergence checkpoint (Module 4.2 provided)

Module 2.3 excerpt:
  Thread 004 — The Alliance Approach: Active. Origin: Ch. 1. Characters: Vara, Caradhen, Aldric (indirect). Expected convergence: Ch. 18–22. Status: Developing — Vara's assessment is being compiled; Caradhen has not committed; Aldric's contingency is active.
  Thread 007 — Sethric's Unspoken Judgment: Dormant. Origin: Ch. 9 (Caradhen chapter, Sethric background presence). Characters: Sethric, Caradhen. No convergence window established.
  Thread 012 — Aldric's Contingency: Active. Origin: Ch. 13. Characters: Aldric, unnamed third party, Caradhen (future). No convergence window established.
  Thread 002 — The Dowager's Trial: Resolved. Ch. 3. Resolution: The formal charges were filed.
  Thread 001 — The Regency's Legacy: Active. Origin: Ch. 1. Characters: Aldric, the Dowager (absent). Expected convergence: Ch. 25–30. Status: Background pressure; not yet directly developed.

Module 2.4 excerpt:
  Payoff 001: The Dowager's letter (Chekhov's gun). Planted: Ch. 4. Window: Ch. 15–20. Status: Pending.
  Payoff 002: Vara's assessment brief (Consequence bomb). Planted: Ch. 10. Detonation trigger: When the assessment brief reaches Aldric directly. Narrative phase anchor: Convergence. Priority tier: Essential. Status: Pending.
  Payoff 003: Caradhen's thirty-year survival pattern (Foreshadowing). Planted: Ch. 7. Window: Open — will resolve when Caradhen is forced to commit. Status: Pending.
  Payoff 004: Aldric's unspoken liability (Consequence bomb). Planted: Ch. 13. Detonation trigger: When Aldric's contingency is activated and the unnamed third party moves against him. Narrative phase anchor: Final act. Priority tier: Unclassified. Status: Pending.

Module 4.2 excerpt (consequence bombs — convergence mode):
  Bomb 4.2-001: Vara's assessment brief reaching Aldric. Priority: Essential. Status: Armed.
    Detonation trigger: When the brief reaches Aldric directly (same as Payoff 002 above).
    Module 2.4 registration: Yes (Payoff 002).
  Bomb 4.2-002: Aldric's unspoken liability. Priority: Unclassified. Status: Armed.
    Detonation trigger: When Aldric's contingency activates and the third party moves against him.
    Module 2.4 registration: Yes (Payoff 004).
  Bomb 4.2-003: Caradhen's exposure — what Sethric knows. Priority: Unclassified. Status: Armed.
    Planted: Ch. 9. Detonation trigger: When Caradhen is forced to publicly commit to a faction.
    Module 2.4 registration: No.
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
  P002 — Vara's Assessment Brief: ON TRACK. Consequence bomb. Detonation trigger: when the brief reaches Aldric directly. Essential. Module 4.2 registration confirmed. Detonation path visible — aligns with T004 convergence window. No action needed; bomb is structurally anchored.
  P003 — Caradhen's Survival Pattern: PENDING (open window). This foreshadowing element has no specific window — it resolves when Caradhen is forced to commit. This is structurally sound for its type, but the main agent should confirm that the story's trajectory will eventually create that forcing condition. If the endpoint compass does not contain a moment that forces Caradhen's commitment, this payoff has no guaranteed resolution path.
  P004 — Aldric's Unspoken Liability: PENDING. Consequence bomb. Detonation trigger: when Aldric's contingency activates and the third party moves against him. Currently Unclassified priority. See bomb sweep below for reclassification recommendation.

Convergence-Phase Bomb Sweep (Module 4.2 provided — convergence mode active):

  Bomb 4.2-001 — Vara's Assessment Brief:
    Priority: Essential | Status: Armed | Module 2.4 registration: Confirmed (P002).
    Detonation path assessment: ON TRACK. The trigger (brief reaching Aldric) aligns directly with T004's convergence window. Detonation path is visible and structurally anchored. No action required.

  Bomb 4.2-002 — Aldric's Unspoken Liability:
    Priority: Unclassified | Status: Armed | Module 2.4 registration: Confirmed (P004).
    Reclassification recommendation: ENRICHING. Aldric's liability adds earned weight to his arc's resolution, but the story's core conflict (the alliance approach) closes without it. The detonation trigger (third party moving against Aldric after contingency activates) is a final-act condition — if the story's final act is structurally crowded, this bomb can be acknowledged in passing rather than given a full scene. Recommend: reclassify to Enriching; monitor for opportunity in T012's resolution window.

  Bomb 4.2-003 — Caradhen's Exposure (What Sethric Knows):
    Priority: Unclassified | Status: Armed | Module 2.4 registration: NOT FOUND — registration gap.
    Reclassification recommendation: ESSENTIAL. Sethric's knowledge of Caradhen is the only thing that can force Caradhen's commitment publicly. Without it detonating, Caradhen's arc has no externally forced resolution — it relies on Caradhen choosing to commit voluntarily, which his thirty-year survival pattern (P003) makes structurally implausible. This bomb and P003 are causally linked; the bomb is the forcing condition P003 has been waiting for.
    Action required (two items):
      1. Reclassify Bomb 4.2-003 to Essential in Module 4.2.
      2. Register in Module 2.4 as Pending Payoff (type: Consequence bomb) immediately.
    Note: This bomb is a discovered convergence with T007 — see Convergence Opportunities below.

Convergence Opportunities:
  T004 + T012 + P002: These three are structurally linked and converging in the same chapter window (Ch. 18–22). When Vara's assessment (P002) reaches Aldric, his contingency (T012) activates in response — this is the braid's first major three-POV convergence point. This convergence is planned and on track. Recommend: ensure Aldric receives a POV chapter before the assessment arrives (so the reader knows what the contingency is before it activates).
  
  T007 + T004 + Bomb 4.2-003 (DISCOVERED): Sethric's dormant thread, the Alliance Approach, and the newly identified Caradhen's Exposure bomb are not linked in the registry — but the narrative logic connects them directly. Sethric knows something about Caradhen that Caradhen cannot suppress. When Caradhen is forced toward a public commitment (T004's convergence), Sethric becomes the detonation mechanism for both T007 and Bomb 4.2-003 simultaneously. This is a Gardener moment: the story has grown three separate elements toward the same resolution point without prior planning. Recommend: add Bomb 4.2-003 as a dependency of T007; link T007 to T004 in the registry; establish a convergence window for T007 aligned with T004's Ch. 18–22 window.

Thread Health Assessment: HEALTHY with three flags.
  Flag 1 (High): Bomb 4.2-003 (Caradhen's Exposure) is Essential and not registered in Module 2.4. Registration gap must be corrected before next chapter.
  Flag 2 (Medium): T012 needs a convergence window established. Currently operating without structural anchoring.
  Flag 3 (Medium): P001 (the Dowager's letter) is approaching its window and appears disconnected from active threads. If it is not integrated with T004 or T012, it will need a chapter of its own — which may interrupt the braid at a structurally sensitive moment.

No-Thread-Abandonment Check: PASS. All threads are accounted for. No abandoned threads without rationale.

Priority Summary:
  HIGH: Bomb 4.2-003 — Essential, no Module 2.4 registration, reclassification required immediately.
  HIGH: P001 — Chekhov's gun approaching window, not integrated with active threads.
  MEDIUM: T012 — no convergence window established.
  MEDIUM: T007 — dormant, activation moment approaching organically without a tracking window.
  LOW: Bomb 4.2-002 — Enriching, no detonation path urgency; monitor at next convergence check.
```
