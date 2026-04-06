# Character Desire Network Examples

## Example: N=3 Cast Network

*Note: Real runs scale with cast size, covering all N×(N−1)/2 pairs. This example uses a 3-character cast to demonstrate the complete pair structure.*

### Output Artifacts

```json
{
  "desire_network": {
    "pairs": [
      {
        "character_a_id": "char_caradhen",
        "character_b_id": "char_vara",
        "relationship_type": "conflicting",
        "description": "Caradhen's desire to preserve the passes intact without commitment conflicts with Vara's desire to return to Aldric with a concrete agreement — she cannot succeed without him committing, and commitment is precisely what his thirty-year survival pattern prohibits.",
        "convergence_note": ""
      },
      {
        "character_a_id": "char_caradhen",
        "character_b_id": "char_aldric",
        "relationship_type": "invisible",
        "description": "Caradhen wants to avoid the lowland wars entirely. Aldric wants to secure the northern border against the empire, which requires controlling the passes. Their desires are fundamentally incompatible, but they are currently operating in different spheres.",
        "convergence_note": "They will collide when Vara's assessment reaches Aldric (Thread 004, Ch. 18-22). Aldric's resulting contingency plan will force Caradhen to make the choice he has avoided for thirty years."
      },
      {
        "character_a_id": "char_vara",
        "character_b_id": "char_aldric",
        "relationship_type": "compatible",
        "description": "Vara wants to prove her diplomatic competence and secure her position at court. Aldric wants the passes secured. Vara can use Aldric's authority to pressure Caradhen, while Aldric uses Vara as his instrument. Their desires align, though Aldric may exploit her without her full knowledge.",
        "convergence_note": ""
      }
    ],
    "key_tensions": "The central structural conflict is between Caradhen's need for non-commitment and Aldric's need for absolute control of the passes, with Vara caught as the active agent trying to force a resolution.",
    "notes": "Vara believes she is negotiating a treaty, but Aldric's true desire may be a pretext for annexation if Caradhen refuses. This creates a three-way entanglement where Vara's success might inadvertently destroy Caradhen's people."
  }
}
```