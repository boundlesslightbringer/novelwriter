# Character Integration Split — Architecture Note

## Why the original skill was split

`character-integration-with-plot` asked a single LLM invocation to:

1. Map structural desire relationships across N characters
2. Derive inter-character knowledge states with cross-referenced KNOWS/DOES NOT KNOW symmetry
3. Build full directional relationship records with asymmetric emotional content
4. Seed anticipatory consequence ledger entries

These are four cognitively distinct tasks. Running them simultaneously degrades cross-referencing
fidelity — the model produces complete-looking output where the KNOWS/DOES NOT KNOW symmetry
breaks quietly, relationship asymmetry becomes inconsistent, and priority reasoning is shallow.

## What replaced it

Three narrow skills in a sequential chain:

  character-desire-network
    ↓ (desire_network document)
  character-knowledge-expansion
    ↓ (knowledge matrix KG records)
  character-relationship-matrix
    ↓ (relationship matrix KG records)

Each skill has a single cognitive task and a tightly typed output.

Task 4 (consequence ledger seeding) was removed entirely. Anticipatory CascadeChain nodes
created before writing begins are speculative and are replaced by accurate records from
consequence-cascade-implementation as actual events occur. The gain from removing it:
the three remaining tasks are cleaner, and the consequence subagent produces better records
from real events anyway.

## Implementation: internal chain within character_subagent

The three skills are NOT separate brain delegations. They run as a LangChain
RunnableSequence (pipe chain) inside character_subagent:

  desire_network_step | knowledge_expansion_step | relationship_matrix_step

Each step:
  - Receives the KG query results and the prior step's output
  - Produces a narrowly typed intermediate or final output
  - Passes its output to the next step via the chain's input dict

The brain makes ONE delegation to character_subagent with task:
"Run full character integration for characters: [ids]"

character_subagent runs the internal chain and returns ONE WorkerResponse with combined
KG-ready records in artifacts.

The brain routes the combined artifacts to story_state_manager in ONE follow-up delegation.

## Brain delegation sequence (before and after)

BEFORE (1 delegation, 1 massive skill):
  brain → character_subagent (character-integration-with-plot)
  brain → story_state_manager

AFTER (1 delegation, 3 internal chain steps):
  brain → character_subagent (runs desire_network | knowledge_expansion | relationship_matrix)
  brain → story_state_manager

Same number of brain visits. Better output. No iteration budget cost.

## Internal chain input/output types

Step 1 — character-desire-network:
  Input:  {character_nodes: [...], relationship_edges_initial: [...],
           faction_nodes: [...], plot_thread_nodes: [...]}
  Output: {desire_network: {compatible_pairs: [...], conflicting_pairs: [...],
           invisible_pairs: [...], notes: "..."}}

Step 2 — character-knowledge-expansion:
  Input:  {character_nodes: [...], existing_knows_edges: [...],
           desire_network: <from step 1>}
  Output: {new_knowledge_items: [...], new_knows_edges: [...],
           integration_flags: [...]}

Step 3 — character-relationship-matrix:
  Input:  {character_nodes: [...], existing_relationship_edges: [...],
           desire_network: <from step 1>}
  Output: {new_relationship_edges: [...], updated_relationship_edges: [...],
           integration_flags: [...]}

Final combined artifacts:
  {knowledge_matrix_expansions: <from step 2>,
   relationship_records: <from step 3>,
   integration_flags: <merged from steps 2 and 3>}

## LangChain implementation sketch

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

desire_network_chain = (
    RunnablePassthrough()
    | desire_network_prompt
    | llm.with_structured_output(DesireNetwork)
)

knowledge_expansion_chain = (
    RunnablePassthrough()
    | knowledge_expansion_prompt
    | llm.with_structured_output(KnowledgeExpansionOutput)
)

relationship_matrix_chain = (
    RunnablePassthrough()
    | relationship_matrix_prompt
    | llm.with_structured_output(RelationshipMatrixOutput)
)

def run_integration_chain(kg_context: dict) -> dict:
    desire_network = desire_network_chain.invoke(kg_context)

    knowledge_output = knowledge_expansion_chain.invoke({
        **kg_context,
        "desire_network": desire_network
    })

    relationship_output = relationship_matrix_chain.invoke({
        **kg_context,
        "desire_network": desire_network
    })

    return {
        "knowledge_matrix_expansions": knowledge_output,
        "relationship_records": relationship_output,
        "integration_flags": knowledge_output.flags + relationship_output.flags
    }
```

Steps 2 and 3 both depend on step 1 but not on each other — they could run
in parallel with asyncio if latency becomes a concern.

## Pydantic schemas for structured chain outputs

```python
class DesireNetworkPair(BaseModel):
    character_a: str
    character_b: str
    relationship_type: str  # "compatible" | "conflicting" | "invisible"
    description: str

class DesireNetwork(BaseModel):
    pairs: list[DesireNetworkPair]
    notes: str

class KnowledgeExpansionOutput(BaseModel):
    new_knowledge_items: list[dict]
    new_knows_edges: list[dict]
    flags: list[dict]

class RelationshipMatrixOutput(BaseModel):
    new_relationship_edges: list[dict]
    updated_relationship_edges: list[dict]
    flags: list[dict]
```

These structured outputs are passed between chain steps as typed objects,
not as freeform text. The LLM at each step knows exactly what it is producing
and what it will receive.
