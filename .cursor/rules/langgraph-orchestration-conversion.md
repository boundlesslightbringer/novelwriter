# LangGraph Orchestration Conversion Rule

## Trigger
When a file resembling an agent skill specification is present (e.g. SKILL.md, agent skill block, YAML spec), or when the user asks about orchestration modeling.

## Instruction

You must:

1. Parse the skill as an orchestration specification.
2. Determine whether it should be implemented as:
   - a sequential chain, or
   - a LangGraph subgraph

3. Choose the model that maximizes:
   - output correctness
   - failure containment
   - observability
   - debuggability

## Decision Criteria

### Prefer sequential chain only if:
- Execution is strictly linear
- No meaningful branching exists
- No validation gates affect control flow
- No retries or fallback paths exist
- No multi-source context aggregation
- Failure can safely terminate execution

### Prefer subgraph if ANY of the following are present:
- Conditional branching
- Multiple execution modes
- Optional steps
- Validation or audit gates
- Retry / fallback logic
- Multi-source context gathering
- Stateful intermediate reasoning
- Partial failure tolerance requirements

## Output Requirements

If **chain**:
- Provide step sequence
- Provide failure handling notes
- Explain why subgraph is unnecessary

If **subgraph**:
You MUST produce:

- State schema
- Node list (clear responsibilities)
- Edge definitions
- Conditional routing logic
- Subgraph boundary definition
- Whether to:
  - call subgraph inside a node, OR
  - add subgraph directly as a node
- Reliability rationale

## Reliability Rule (Critical)

If uncertain:
→ choose the model that minimizes silent failure and invalid intermediate propagation.

## Execution

Delegate to:
→ `subagent: langgraph-architect`

Pass the skill file content as input.