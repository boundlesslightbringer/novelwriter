# Gardener Plotting System Examples

## Example: Scene Parameters Generation

### Input Context

```json
{
  "pov_character_id": "char_caradhen",
  "chapter_context": 4,
  "include_foreshadowing_check": true
}
```

### Supplementary Narrative Context

*The following prose explains the reasoning behind the JSON output.*

**POV character:** Caradhen of the Thornback (Module 1.1 excerpt)
  Emotional state: Surface — controlled, deliberate. Beneath — something approaching dread, not yet named by him.
  Active desire: To conclude the envoy's visit without having committed to anything specific.
  Active fear: That Vara (the envoy) has read him more clearly than he has read her.
  Arc stage: Established — approaching first genuine test.
  Knowledge state (Module 1.2 excerpt): KNOWS Vara was sent because the protagonist cannot come personally. SUSPECTS she has more authority than her opening position. DOES NOT KNOW she is also carrying an assessment brief — she is evaluating whether he is an asset or an obstacle to be removed.

**Last scene outcome:** Caradhen hosted the envoy's first formal dinner. Vara made her opening proposal — an alliance of passage rights through the passes in exchange for trade protections. Caradhen responded with gracious non-commitment. She did not press. He went to bed unsure whether her restraint was patience or preparation.

**Active threads (Module 2.3 excerpt):** Thread 004 — The Alliance Approach (Active). Thread 007 — Sethric's Unspoken Judgment (Dormant — flagged for potential activation).

**Active consequences (Module 4.1 excerpt):** Caradhen's thirty-year non-commitment pattern has produced an anticipated consequence structure: if he is perceived as managing rather than negotiating, the protagonist's response may force the confrontation he has spent thirty years avoiding.

### Output Artifacts

```json
{
  "scene_parameters": {
    "pov_character_id": "char_caradhen",
    "pov_character_name": "Caradhen of the Thornback",
    "arc_stage": "Established",
    "dominant_emotional_state": "controlled surface / unacknowledged dread",
    "scene_goal": "To find out, without appearing to be asking, whether Vara knows more than she has shown — specifically whether her restraint at dinner was tactical patience or genuine uncertainty about his position.",
    "obstacle": {
      "description": "Vara's professional training makes her intent opaque, neutralizing Caradhen's usual methods of reading people.",
      "components": {
        "external": "Vara is good at this; she will not reveal her read of him if she has one.",
        "interpersonal": "To find out what she knows, Caradhen would have to reveal what he is concerned about, which would tell her something he does not want her to know.",
        "internal": "His primary cognitive tool (reading intent from physical behaviour) is blunted here: Vara's professional training means her physical tells are managed. He is in a situation where his most reliable instrument does not work, and he cannot acknowledge that without acknowledging uncertainty."
      }
    },
    "the_choice": {
      "description": "How to proceed with the envoy the morning after the dinner.",
      "option_a": "Request a private follow-up meeting on the pretext of reviewing the specific trade routes — which creates the opportunity to probe her but also signals that he is taking the proposal seriously enough to engage with it in detail, moving him closer to a position than he wants.",
      "option_b": "Do nothing, let another day pass, and observe whether she initiates — which preserves his neutrality but cedes the initiative to her and risks her reading his inaction as reluctance rather than assessment.",
      "tests_core_contradiction": true
    },
    "projected_consequence_shape": "Whichever option he chooses, Vara will update her assessment of him. The consequence that is opening is: the envoy's evaluation is no longer being made on neutral terms. Whatever Caradhen does next — including doing nothing — will be read as a signal. He is now inside her assessment, not outside it. That fact cannot be undone.",
    "character_logic_audit": "PASS. Caradhen's goal (probe without revealing) is derived directly from his observational lens (reads intent, reads power), his active fear (being correctly read), and his response pattern to unwanted intimacy (goes quiet, removes access on a pretext). The obstacle is specifically keyed to his established blind spot: Vara is not presenting as a physical threat or a social status signal, which are his primary lenses; she is presenting as a professional peer whose intent is genuinely opaque to him. The choice tests his core operating principle — his thirty-year survival strategy is non-commitment, but both options here involve some form of signal."
  },
  "active_thread_flags": [
    {
      "thread_id": "thread_004",
      "thread_name": "The Alliance Approach",
      "touched_how": "advancing"
    },
    {
      "thread_id": "thread_007",
      "thread_name": "Sethric's Unspoken Judgment",
      "touched_how": "not activated by this scene; flag for next POV rotation check"
    }
  ],
  "active_consequence_flags": [
    {
      "chain_id": "cc_caradhen_desire_loop",
      "current_position": "Anticipated consequence structure",
      "approaching_detonation": false,
      "note": "The anticipated consequence structure from Module 4.1 is now closer to activation — Vara's assessment brief means that Caradhen's management strategy, if she has identified it, may already be travelling back toward the protagonist."
    }
  ],
  "foreshadowing_opportunity": {
    "present": true,
    "payoff_id": "bomb_vara_assessment",
    "payoff_description": "Vara's assessment brief or the protagonist's contingency response.",
    "organic_integration_note": "If Module 2.4 includes any setup related to Vara's assessment brief or the protagonist's contingency response, this scene — specifically the private meeting option if Caradhen chooses it — is a natural moment for Vara to reveal, in her behaviour, that she is assessing more than she is negotiating."
  },
  "kg_context_used": {
    "character_node_found": true,
    "knows_edges_found": 3,
    "active_threads_found": 2,
    "cascade_chains_found": 1,
    "pending_payoffs_checked": true
  },
  "parameter_discrepancy_flag": null
}
```