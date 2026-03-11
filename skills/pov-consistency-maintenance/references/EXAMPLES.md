# POV Consistency Maintenance Examples

## Input/Output Example

### Input

```yaml
Draft scene excerpt (partial):
  "...Caradhen watched Vara pour the wine. He knew she was nervous — her hands
  moved too carefully, the way hands move when their owner is trying not to
  show that they are shaking. Vara thought the meeting was going well.
  She had been surprised when he agreed to the follow-up. He watched her
  and thought about his sons, about which of them would be standing in this
  room someday in his place. He felt his face harden. Neither of them
  understood what Aldric's contingency would mean for this conversation..."

Module 1.2 (Caradhen):
  KNOWS: Vara has made a proposal; she is an envoy of the protagonist.
  SUSPECTS: She has more authority than her opening position suggests.
  DOES NOT KNOW: Vara's internal assessment of how the meeting is going.
  DOES NOT KNOW: Aldric's contingency has been activated.

Voice profile (Caradhen):
  Observational focus: power geometry, exits, what people do with their hands.
  Emotional processing: encodes emotion in what he notices; does not name it.
  Sentence structure: long and deliberate in control; compresses under pressure.
```

### Output

```markdown
Audit header:
  POV: Caradhen of the Thornback.
  Scene: Follow-up meeting with Vara, solar.
  Status: VIOLATIONS FOUND — 4 violations of 3 types.

Violation Log:

[Category 1 — Knowledge Violation]
Text: "Neither of them understood what Aldric's contingency would mean for
      this conversation"
What: This sentence states that Caradhen does not understand what Aldric's
      contingency means — but Module 1.2 records Caradhen as DOES NOT KNOW
      that Aldric's contingency has been activated at all. He cannot not-
      understand the implications of something he has no knowledge of.
Correction: Remove this sentence entirely.

[Category 2 — Head-Hopping]
Text: "Vara thought the meeting was going well."
What: This directly states Vara's interior thought — Caradhen cannot access
      the content of Vara's thinking.
Correction: Replace with Caradhen's observable evidence and inference.

[Category 4 — External Self-Description]
Text: "He felt his face harden."
What: Caradhen cannot observe his own face.
Correction: Replace with internal physical sensation.
```

## Quality Checklist

Before returning the consistency report, verify:

- [ ] Reference standards (voice profile and knowledge matrix) were read before the draft.
- [ ] Every category was checked in a dedicated reading pass.
- [ ] Every violation entry has: type, quoted text, precise description, specific correction note.
- [ ] Violations are grouped by category in severity order.
- [ ] Inference threshold was applied for head-hopping.
- [ ] External self-description was distinguished from internal physical sensation.
- [ ] Voice inconsistency was distinguished from legitimate stressed-voice variants.
- [ ] A CLEAN report is complete with only the header.
- [ ] No prose rewritten. Correction notes only.
- [ ] No World Bible writes specified.
