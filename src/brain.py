import json
import os
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import NovelWriterConfig
from src.state import BrainDecision, BrainDecisionFallback, OrchestratorState, QualityVerdict


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


class BrainNode:
    """The orchestrator brain that makes routing and quality decisions."""
    
    def __init__(self, config: NovelWriterConfig):
        self.config = config
        self.iteration_limit_response = "Iteration limit reached. Summarizing progress..."  
        llm_config = self.config.get_llm_config("brain")
        
        # Initialize the LLM
        
        self.llm = ChatGoogleGenerativeAI(
            model=llm_config.model_name,
            temperature=llm_config.temperature,
            top_p=llm_config.top_p,
            top_k=llm_config.top_k,
            vertexai=True
        )
        
        # Load the brain prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "brain.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def _build_context_block(self, state: OrchestratorState) -> str:
        """Construct the Layer 3 context block."""
        latest_result = state.get("latest_worker_result")
        history = state.get("worker_history", [])
        
        lines = []
        if latest_result:
            lines.append("[Last worker result]")
            lines.append(f"  Worker  : {latest_result.get('worker')}")
            lines.append(f"  Task    : {latest_result.get('task')}")
            
            result_data = latest_result.get("result", {})
            lines.append(f"  Status  : {result_data.get('status')}")
            lines.append(f"  Summary : {result_data.get('summary')}")
            
            artifacts = result_data.get("artifacts", {})
            # Truncate string values in artifacts to 600 chars
            truncated_artifacts = {}
            for k, v in artifacts.items():
                if isinstance(v, str) and len(v) > 600:
                    truncated_artifacts[k] = v[:600] + "... [truncated]"
                else:
                    truncated_artifacts[k] = v
            lines.append(f"  Artifacts: {json.dumps(truncated_artifacts)}")
        else:
            lines.append("[Last worker result]: None")
            
        lines.append("\n[Recent worker history]")
        if history:
            # Last 3 entries only
            recent = history[-3:]
            for entry in recent:
                worker = entry.get("worker")
                status = entry.get("result", {}).get("status")
                lines.append(f"  - {worker} -> {status}")
        else:
            lines.append("  None")
            
        return "\n".join(lines)

    def __call__(self, state: OrchestratorState, config: RunnableConfig | None = None) -> Dict[str, Any]:
        """Execute the brain node."""
        iteration_count = state.get("iteration_count", 0) 
        
        # 1. Iteration Limit Check
        if iteration_count >= self.config.max_brain_iterations:
            print(f"[DEBUG] Iteration limit hit at {iteration_count}", flush=True)
            return {
                "final_response": self.iteration_limit_response,
                "iteration_count": iteration_count + 1,
                "active_worker": None,
                "worker_request": None
            }
            
        # 2. Three-Layer Prompt Construction
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(state.get("messages", []))
        
        layer3_content = self._build_context_block(state)
        messages.append(HumanMessage(content=layer3_content))
        
        # 3. LLM Invocation with Fallback
        try:
            decision: BrainDecision = self.llm.with_structured_output(BrainDecision).invoke(messages)
        except Exception as e:
            print(f"Brain LLM structured output failed: {e}. Trying fallback...")
            fallback_decision: BrainDecisionFallback = self.llm.with_structured_output(BrainDecisionFallback).invoke(messages)
            
            # Map fallback to primary model
            quality_assessment = None
            if fallback_decision.quality_verdict:
                quality_assessment = QualityVerdict(
                    verdict=fallback_decision.quality_verdict,
                    reason=fallback_decision.quality_reason or "Fallback reason"
                )
                
            decision = BrainDecision(
                reasoning=fallback_decision.reasoning,
                action=fallback_decision.action,
                worker=fallback_decision.worker,
                task=fallback_decision.task,
                context=fallback_decision.context,
                response=fallback_decision.response,
                quality_assessment=quality_assessment
            )

        # 4. Quality Gate Decision Tree
        latest_result = state.get("latest_worker_result")
        rejection_count = state.get("rejection_count", 0)
        verdict = None
        
        if latest_result:
            worker = latest_result.get("worker")
            result_data = latest_result.get("result", {})
            status = result_data.get("status")
            artifacts = result_data.get("artifacts", {})
            
            if worker == "story_state_manager" and status == "blocked":
                # HANDOFF §5.2 / spec: deterministic route to resolution (LLM cannot override).
                decision.action = "delegate"
                decision.worker = "resolution_subagent"
                decision.task = "Analyse KG contradiction blocking persistence"
                decision.response = None
                decision.quality_assessment = None
                inbound = _ensure_dict(latest_result.get("context"))
                decision.context = {
                    "mode": "ANALYSE",
                    "contradiction_record": _ensure_dict(artifacts.get("contradiction_record")),
                    "blocked_write": {
                        "write_type": "story_state_manager",
                        "proposed_context": inbound,
                    },
                    "prefetched_docs": [],
                }
            elif worker in ("story_state_manager", "resolution_subagent"):
                # Skip quality gate for other infrastructure outcomes
                pass
            elif status == "failed":
                decision.action = "respond"
                decision.response = f"Worker {worker} failed: {result_data.get('summary')}"
            elif status == "need_input":
                decision.action = "clarify"
                decision.response = result_data.get("summary")
            elif status == "success":
                # Evaluate artifacts
                if not artifacts:
                    verdict = "reject"
                elif decision.quality_assessment and decision.quality_assessment.verdict == "needs_clarification":
                    verdict = "needs_clarification"
                elif decision.quality_assessment and decision.quality_assessment.verdict == "reject":
                    verdict = "reject"
                else:
                    verdict = "accept"
                    
                if verdict == "reject":
                    # Reject Budget Check
                    task = latest_result.get("task")
                    if rejection_count >= self.config.max_rejection_budget:
                        decision.action = "respond"
                        decision.response = f"Worker {worker} failed to complete task after {rejection_count + 1} attempts."
                    else:
                        decision.action = "delegate"
                        decision.worker = worker
                        decision.task = task
                        decision.context = latest_result.get("context")
                elif verdict == "needs_clarification":
                    decision.action = "clarify"
                    # Use LLM response if provided, else generic
                    if not decision.response:
                        decision.response = "Need clarification on the worker's output."
                elif verdict == "accept":
                    # Proceed with LLM's decision (usually delegate to story_state_manager or respond)
                    pass

        # 5. State Update
        updates = {
            "iteration_count": iteration_count + 1,
        }
        
        if decision.action in ("respond", "clarify"):
            updates["final_response"] = decision.response or "No response provided."
            updates["active_worker"] = None
            updates["worker_request"] = None
            updates["rejection_count"] = 0
        elif decision.action == "delegate":
            updates["final_response"] = None
            updates["active_worker"] = decision.worker
            updates["worker_request"] = {
                "task": decision.task,
                "context": decision.context or {},
                "reasoning": decision.reasoning
            }
            # If we are re-delegating due to a rejection, increment the counter
            if latest_result and latest_result.get("worker") == decision.worker and latest_result.get("task") == decision.task and verdict == "reject":
                updates["rejection_count"] = rejection_count + 1
            else:
                updates["rejection_count"] = 0
            
        return updates
