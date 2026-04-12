Plan: Decompose Pass 2 into a linear LangGraph chain (shared state)
Goal
Replace the single LLM step inside run_pass_2 in src/planning_rough_endpoints_subgraph.py (one Pass2Output from pass2_llm) with a linear sequence of nodes on the same StateGraph(RoughEndpointsState)—no nested compiled subgraph, no new worker. External behavior stays the same: run_rough_endpoints_subgraph still returns pass_2_artifacts with pass: 2 and the same top-level keys.

This matches skills/langgraph-subgraph-conversion/SKILL.md: chain for fully linear flow; shared parent state (“direct nodes”) instead of an isolated nested subgraph.

Current baseline
RoughEndpointsState already includes pass_2_artifacts (planning_rough_endpoints_subgraph.py ~72–86).
run_pass_2 (~304–382) runs one structured call and writes the full pass_2_artifacts dict.
Graph: fetch_reassess_context → conditional → run_pass_2 → package_response (~428–445).
Target topology (linear)
fetch_reassess_context
pass2_refine_compass
pass2_plot_thread_seeds
pass2_payoff_seeds
pass2_assemble_artifacts
package_response
Pass 1: unchanged (run_pass_1 → package_response).
Pass 2: route_after_reassess sends run_pass == 2 to pass2_refine_compass, then the chain above, then package_response.
State extensions (RoughEndpointsState, all optional)
Field	Role
pass_2_compass
Refined narrative + milestones (no KG seeds): prologue, starting/ending, milestones, core_conflict_question, compass_notes (normalized dicts/lists).
pass_2_plot_thread_seeds
List of plot thread seed dicts from step 2.
pass_2_payoff_seeds
List of payoff seed dicts from step 3.
Final public payload remains in pass_2_artifacts (same keys as today).

Pydantic / LLM split
Introduce structured models (names illustrative):

Pass2CompassOutput — compass + milestones only (no plot_thread_seeds / payoff_seeds). Mirrors the non-seed slice of today’s Pass2Output.
Pass2SeedsOutput — both seed lists in one second call, or two models / two nodes: plot seeds only, then payoff seeds only, if prompts stay clearer.
Prompts

Node A: Same context as today’s Pass 2 payload (pass_1_output, character_concepts, reassess_context, skill excerpt). Instruct: refine compass only; no KG seeds.
Node B: Inputs: pass_2_compass (+ concepts as needed). Output: plot_thread_seeds.
Node C: Inputs: pass_2_compass + plot summaries / milestones. Output: payoff_seeds.
Each node: llm.with_structured_output(...) like Pass 1 / current Pass 2; early return {} if terminal_status or run_pass != 2.

Deterministic pass2_assemble_artifacts node
No LLM.
Merge pass_2_compass + seed lists into pass_2_artifacts with pass: 2.
Move milestone normalization and empty-seed fallbacks from current run_pass_2 (~322–368) here (or into small pure helpers used only by this node).
Optionally push a short entry onto warnings when fallbacks run.
This node is easy to unit test in isolation (recommended: _assemble_pass2_artifacts(...) helper).

Graph changes in _build_subgraph
Remove add_node("run_pass_2", run_pass_2) and the conditional edge target run_pass_2.
Add nodes: pass2_refine_compass, pass2_plot_thread_seeds, pass2_payoff_seeds, pass2_assemble_artifacts.
In route_after_reassess, when run_pass == 2, route to pass2_refine_compass.
Add linear edges through assemble → package_response.
Tests
tests/test_planning_subagent.py: test_defining_rough_endpoints_pass_2 must still pass (same artifact contract).
Add a unit test for assembly/normalization/fallbacks if extracted to a pure function (avoids LLM flakiness).
Tradeoffs
Cost/latency: up to three LLM calls vs one.
Reliability: smaller structured outputs per step usually improve consistency (main motivation).
Optional rollout
Env flag to switch old single-node vs chain—only if you want a quick revert; otherwise ship the chain only.

Files to touch
src/planning_rough_endpoints_subgraph.py — state, models, nodes, edges, assembly.
tests/test_planning_subagent.py (+ optional small test module for assembly).
Out of scope
Nested StateGraph as a separate compiled subgraph.
Changes to brain/bootstrap or worker routing.
ORCHESTRATOR_SPEC rewrites.
Implementation todos
state-models — Extend RoughEndpointsState; add Pass2CompassOutput + seed-focused Pydantic models; keep final pass_2_artifacts schema identical.
nodes-prompts — Implement the three LLM nodes with focused prompts and guards.
assemble — Implement pass2_assemble_artifacts + reuse/move normalization and fallbacks from current run_pass_2.
graph-wire — Rewire _build_subgraph conditional and edges as above.
tests — Regression on Pass 2; optional pure assembly unit test.