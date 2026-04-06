# Scene Construction Examples

The following example demonstrates the expected input and output for the `scene-construction` skill.

## Example — Scene Draft Generation

### Input Context (from Brain and Story State KG)

```yaml
Scene parameters (from Gardener Plotting System):
  POV: Caradhen of the Thornback
  Goal: Conclude the envoy's follow-up meeting before Vara can move the
        conversation toward the question she has been building toward.
  Obstacle: Vara shifts the conversation without warning — she stops asking
        about trade routes and asks, with apparent casualness, which of
        Caradhen's sons he expects to outlive him. The question is not about
        his sons. Internal obstacle: Caradhen's survival pattern is to
        non-commit and exit. The question has trapped him where exiting
        would itself be a signal.
  Choice: Answer the question — which means engaging on terms Vara has set
        and revealing something about succession and loyalty — or refuse it,
        which means making visible that the question was not casual.
  Consequence shape: Whichever option he takes, Vara has what she came for:
        a data point about how Caradhen manages the question of legacy.

Character State & Voice Profile (from KG):
  Emotional state: controlled surface / something older and colder moving beneath.
  Observational focus: power geometry of rooms, exits, sightlines, what people are doing with their hands.
  Processing style: encodes emotion in what he notices, never names it directly.
  Voice: long deliberate sentences in control, compresses toward declaratives under pressure.

Knowledge Matrix (from KG):
  Caradhen DOES NOT KNOW Vara's full assessment brief.
  SUSPECTS she has more authority than her opening position suggests.
  KNOWS the question about his sons is not casual.

Pending Payoffs (from KG):
  Payoff 003 — Caradhen's thirty-year survival pattern (Foreshadowing).
  Window: open. Status: Pending.
  [The scene is a natural opportunity to advance this element — his survival pattern is being directly tested by Vara's question.]

Pacing guidance:
  TAUT. Compressed interiority. High sentence density. Dialogue-sparse relative to action.
  Voice flag: protect observational precision — he notices what she is doing with her hands.
```

### Output shape (JSON `artifacts`)

```json
{
  "draft_prose": "The solar had one door and three windows, and Vara had seated herself where she could see all of them.\n\nCaradhen had noticed this when she arrived. He had not remarked on it.\n\nThey had been discussing the northern pass for twenty minutes — road conditions, the weight limits of supply carts, the particular problem of the second switchback in early spring. Vara listened the way she always listened: with her full attention and no notes. He was explaining the drainage issue on the third terrace when she said, with the specific quality of casualness that was not casual at all:\n\n\"Which of your sons do you expect to outlive you?\"\n\nThe window above her right shoulder showed a strip of grey sky. He looked at it for a moment.\n\nNot long. But a moment.\n\nShe did not fill the silence. She never filled silences; that was one of the things he had catalogued about her in the past four days. She placed silences and waited to see what grew in them.\n\nHe had three sons. He had thoughts about each of them that he had not organised into anything he would call expectations. The question assumed he thought about his own death in terms of succession. He thought about his own death in terms of who would know, when it happened, that it had happened, and how quickly.\n\n\"Davin manages the eastern passes,\" he said. \"He has the patience for it.\"\n\nHe watched her right hand.\n\nHer right hand did not move.\n\n\"That isn't what I asked,\" she said, pleasantly.\n\n\"No,\" he said. \"It isn't.\"\n\nHe looked back at the strip of grey sky. Somewhere in the account she was building — the assessment brief he did not know existed but whose shape he had begun to understand — there was now a data point. He had answered by not answering, and she had noted what he had chosen instead.\n\nThe drainage issue on the third terrace, he thought, remained unresolved.",
  "scene_metadata": {
    "pov_character_id": "char_caradhen",
    "chapter_context": 4,
    "approximate_word_count": 342,
    "foreshadowing_embedded": true,
    "foreshadowing_payoff_id": "payoff_003",
    "parameter_discrepancy_flag": null
  },
  "kg_context_used": {
    "character_node_found": true,
    "voice_profile_found": true,
    "knows_edges_found": 3,
    "pending_payoffs_checked": true,
    "location_node_found": true
  }
}
```