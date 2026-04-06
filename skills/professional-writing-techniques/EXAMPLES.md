# Professional Writing Techniques Examples

## Example: Technique Application

### Input Context

```json
{
  "problem_description": "The scene ends on Caradhen's choice but the choice feels arbitrary — both options feel equally available and I cannot find a reason to pick one over the other. He can either request a private meeting with Vara or let her initiate.",
  "pov_character_id": "char_caradhen",
  "chapter_context": 14,
  "technique_hint": "Character Interview"
}
```

### Output Artifacts

```json
{
  "technique_applied": "Character Interview",
  "problem_diagnosis": {
    "problem_type": "Choice arbitrariness",
    "root_cause": "The choice is being framed as a tactical decision (who initiates the meeting), which makes both options equally valid tactically. The genuine choice is not tactical; it is psychological.",
    "what_is_available": "Caradhen's core contradiction (belief in survival via non-commitment vs. respect for those who fight for what is sacred) and his active fear (being correctly read by Vara)."
  },
  "path_forward": {
    "primary_recommendation": "Reframe the choice. The decision is not about who initiates the meeting; it is about whether Caradhen is willing to risk being seen in order to gather information.",
    "worked_application": "Internal Interview: 'What do you want here?' -> 'I want to know if she sees through me.' 'What are you afraid of?' -> 'That she already has.' 'What would you never admit?' -> 'That I want her to see through me, because I am tired of the performance.' The choice is therefore: (A) Request the meeting, risking exposure but gaining clarity, or (B) Wait, maintaining the shield but enduring the uncertainty. Because his core wound drives him to avoid commitment (and thus exposure), he will choose (B) — he will wait. The tension comes from how much it costs him to wait.",
    "alternatives": [
      "If the plot requires him to request the meeting (Option A), he must do it by rationalizing it as a purely tactical necessity, actively deceiving himself about his underlying desire to be seen."
    ]
  },
  "scene_construction_context": "The choice at the end of the scene is not tactical; it is psychological. Caradhen must choose between risking exposure (requesting the meeting) and enduring uncertainty (waiting). Because his primary defense is non-commitment, he will choose to wait. The scene's tension should not come from him weighing the tactical pros and cons, but from the internal cost of maintaining his silence when he desperately wants to know what Vara sees.",
  "kg_context_used": {
    "character_node_found": true,
    "cascade_chains_checked": true,
    "recent_chapters_checked": false
  }
}
```