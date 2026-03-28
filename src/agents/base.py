import json
from pathlib import Path
from typing import Any, Dict, List

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from src.config import NovelWriterConfig


class WorkerResponse(BaseModel):
    """Structured response returned by every worker node."""
    status: str = Field(description="Overall worker execution status (completed, need_input, failed).")
    summary: str = Field(description="Concise summary of what the worker did or found.")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific structured outputs produced by the worker.")
    follow_up_questions: List[str] = Field(default_factory=list, description="Questions that the orchestrator may need to relay to the user.")
    recommended_next_worker: str | None = Field(default=None, description="Optional recommendation for which worker should act next.")


class BaseWorkerSubagent:
    """Base class for all worker subagents."""
    
    def __init__(self, name: str, config: NovelWriterConfig, tools: List[Any], prompt_file: str):
        self.name = name
        self.config = config
        self.tools = tools
        self.llm_config = self.config.get_llm_config(self.name)
        
        # Load prompt
        src_dir = Path(__file__).resolve().parent.parent
        prompt_path = src_dir / "prompts" / prompt_file
        self.base_prompt = prompt_path.read_text(encoding="utf-8")
        
        self.agent = self._build_agent()

    def _build_agent(self) -> Any:
        """Create the LangGraph worker agent."""
        # Handle provider prefix if present
        model_name = self.llm_config.model_name
        model_provider = self.llm_config.model_provider
            
        model_kwargs = {
            "temperature": self.llm_config.temperature,
        }
        if self.llm_config.top_p is not None:
            model_kwargs["top_p"] = self.llm_config.top_p
        if self.llm_config.top_k is not None:
            model_kwargs["top_k"] = self.llm_config.top_k

        llm = ChatOpenRouter(
            model=model_name,
            **model_kwargs)
        
        return create_agent(
            model=llm,
            tools=self.tools,
            system_prompt=self._build_runtime_prompt(),
            response_format=WorkerResponse,
            name=self.name,
        )

    def _build_runtime_prompt(self) -> str:
        """Create the system prompt for the worker node."""
        tool_instruction = (
            "You have direct access to the World Bible knowledge-graph tools. Use them "
            "for reads and writes instead of inventing persisted state."
        ) if self.name in {"worldbible_manager", "resolution_subagent"} else (
            "You have access to `progressive_skill_loader`. Before performing specialized "
            "domain work, load the relevant skill instructions from the skills directory."
        )

        return (
            f"{self.base_prompt}\n\n"
            "## LangGraph Runtime Contract\n"
            "You are an internal worker node. The human user never speaks to you directly.\n"
            "- Execute only the task provided by the orchestrator brain.\n"
            "- Do not answer as the top-level assistant.\n"
            f"- {tool_instruction}\n"
            "- Place domain-specific structured outputs in the `artifacts` field.\n"
            "- Keep `summary` concise and factual.\n"
        )

    def _serialize_for_prompt(self, payload: Any) -> str:
        """Serialize arbitrary data for prompt injection."""
        try:
            return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
        except TypeError:
            return str(payload)

    def _message_content_to_text(self, content: Any) -> str:
        """Normalize message content into plain text."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: List[str] = []
            for part in content:
                if isinstance(part, str):
                    chunks.append(part)
                elif isinstance(part, dict) and part.get("type") == "text":
                    chunks.append(str(part.get("text", "")))
            return "\n".join(chunk for chunk in chunks if chunk.strip())
        return str(content)

    def _messages_to_transcript(self, messages: List[BaseMessage], max_messages: int = 10) -> str:
        """Render recent conversation as a compact transcript."""
        transcript_lines: List[str] = []
        for message in messages[-max_messages:]:
            role = message.type.upper()
            content = self._message_content_to_text(message.content).strip()
            if content:
                transcript_lines.append(f"{role}: {content}")
        return "\n\n".join(transcript_lines)

    def _extract_last_message_text(self, messages: List[BaseMessage]) -> str:
        """Extract the final message text from an agent result."""
        if not messages:
            return ""
        return self._message_content_to_text(messages[-1].content).strip()

    def _coerce_worker_response(self, result: Dict[str, Any]) -> WorkerResponse:
        """Normalize worker output into the shared structured schema."""
        structured_response = result.get("structured_response")
        if isinstance(structured_response, WorkerResponse):
            return structured_response
        if isinstance(structured_response, dict):
            return WorkerResponse.model_validate(structured_response)

        fallback_text = self._extract_last_message_text(result.get("messages", []))
        artifacts = {"raw_output": fallback_text} if fallback_text else {}
        return WorkerResponse(
            status="completed",
            summary=fallback_text or "Worker completed without structured output.",
            artifacts=artifacts,
        )

    def invoke(self, state: Dict[str, Any], stream: bool = False) -> Dict[str, Any]:
        """Execute the worker node and store its structured result."""
        worker_request = state.get("worker_request")
        if not worker_request:
            return {
                "latest_worker_result": {
                    "worker": self.name,
                    "task": "missing_request",
                    "context": {},
                    "result": WorkerResponse(
                        status="failed",
                        summary="Worker was invoked without an active request.",
                    ).model_dump(),
                },
                "worker_request": None,
                "active_worker": None,
            }

        worker_payload = {
            "task": worker_request["task"],
            "context": worker_request.get("context", {}),
            "reasoning_from_brain": worker_request.get("reasoning", ""),
            "conversation_transcript": self._messages_to_transcript(state.get("messages", [])),
            "recent_worker_history": state.get("worker_history", [])[-3:],
        }

        try:
            if stream:
                result = self.agent.stream(
                    {
                        "messages": [
                            HumanMessage(
                                content=(
                                    "Execute the following orchestrator request and return a structured worker result.\n\n"
                                    f"{self._serialize_for_prompt(worker_payload)}"
                                )
                            )
                        ]
                    }
                )
            else:
                result = self.agent.invoke(
                    {
                        "messages": [
                            HumanMessage(
                                content=(
                                    "Execute the following orchestrator request and return a structured worker result.\n\n"
                                    f"{self._serialize_for_prompt(worker_payload)}"
                                )
                            )
                        ]
                    }
                )
            structured_result = self._coerce_worker_response(result).model_dump()
        except Exception as error:
            structured_result = WorkerResponse(
                status="failed",
                summary=f"Worker execution failed: {error}",
            ).model_dump()

        worker_record = {
            "worker": self.name,
            "task": worker_request["task"],
            "context": worker_request.get("context", {}),
            "result": structured_result,
        }
        return {
            "latest_worker_result": worker_record,
            "worker_history": [worker_record],
            "worker_request": None,
            "active_worker": None,
        }
