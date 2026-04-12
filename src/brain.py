import json
from pathlib import Path
import re
from typing import Any, Dict, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from src.bootstrap_artifact_audit import audit_worker_artifacts
from src.bootstrap_trace import (
    append_brain_quality_gate_trace,
    fingerprint_logical_ids,
    redact_context,
    trace_path,
)
from src.brain_persistence_mapper import PersistPayloadMapper, PersistPayloadMapperResult
from src.config import NovelWriterConfig
from src.state import BrainDecision, BrainDecisionFallback, OrchestratorState, QualityVerdict, VALID_WORKERS


INFRASTRUCTURE_WORKERS = {"story_state_manager", "resolution_subagent"}
MVP_WORKER_SEQUENCE = [
    "planning_subagent",
    "character_subagent",
    "plotting_subagent",
    "writing_subagent",
]
def _maybe_bootstrap_trace_quality_gate(
    *,
    latest: Dict[str, Any],
    worker: str,
    artifacts: Dict[str, Any],
    result_status: str,
    quality_verdict: str | None,
    quality_reason: str | None,
    mapper_result: PersistPayloadMapperResult | None,
) -> None:
    if not trace_path():
        return
    raw_ctx = _ensure_dict(latest.get("context"))
    validation_errors = audit_worker_artifacts(worker, artifacts, raw_ctx)
    mapper_has_payload: bool | None = None
    mapper_errors: list[str] | None = None
    mapper_counts: Dict[str, int] | None = None
    nodes_fingerprint: str | None = None
    if mapper_result is not None:
        mapper_has_payload = mapper_result.has_payload
        mapper_errors = list(mapper_result.errors)
        mctx = _ensure_dict(mapper_result.context)
        na = mctx.get("nodes_to_add")
        nu = mctx.get("nodes_to_update")
        ea = mctx.get("edges_to_add")
        eu = mctx.get("edges_to_update")
        mapper_counts = {
            "nodes_to_add": len(na) if isinstance(na, list) else 0,
            "nodes_to_update": len(nu) if isinstance(nu, list) else 0,
            "edges_to_add": len(ea) if isinstance(ea, list) else 0,
            "edges_to_update": len(eu) if isinstance(eu, list) else 0,
        }
        if isinstance(na, list) and na:
            dict_nodes = [x for x in na if isinstance(x, dict)]
            if dict_nodes:
                nodes_fingerprint = fingerprint_logical_ids(dict_nodes)
    append_brain_quality_gate_trace(
        worker=worker,
        task=str(latest.get("task") or ""),
        result_status=result_status,
        quality_verdict=quality_verdict,
        quality_reason=quality_reason,
        context_redacted=redact_context(raw_ctx),
        raw_artifacts=artifacts,
        validation_errors=validation_errors,
        mapper_has_payload=mapper_has_payload,
        mapper_errors=mapper_errors,
        mapper_counts=mapper_counts,
        nodes_logical_id_fingerprint=nodes_fingerprint,
    )


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


class BrainNode:
    """Autonomous-but-bounded orchestrator brain with hard runtime guardrails."""

    def __init__(self, config: NovelWriterConfig):
        self.config = config
        self.persist_mapper = PersistPayloadMapper()
        self.iteration_limit_response = "Iteration limit reached. Summarizing progress..."
        llm_config = self.config.get_llm_config("brain")
        self.llm = ChatGoogleGenerativeAI(
            model=llm_config.model_name,
            temperature=llm_config.temperature,
            top_p=llm_config.top_p,
            top_k=llm_config.top_k,
            vertexai=True,
        )
        prompt_path = Path(__file__).resolve().parent / "prompts" / "brain.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def _build_context_block(self, state: OrchestratorState) -> str:
        latest_result = _ensure_dict(state.get("latest_worker_result"))
        history = state.get("worker_history", [])
        lines: list[str] = []

        if latest_result:
            lines.append("[Last worker result]")
            lines.append(f"  Worker  : {latest_result.get('worker')}")
            lines.append(f"  Task    : {latest_result.get('task')}")
            result_data = _ensure_dict(latest_result.get("result"))
            lines.append(f"  Status  : {result_data.get('status')}")
            lines.append(f"  Summary : {result_data.get('summary')}")
            artifacts = _ensure_dict(result_data.get("artifacts"))
            truncated_artifacts: Dict[str, Any] = {}
            for key, value in artifacts.items():
                if isinstance(value, str) and len(value) > 600:
                    truncated_artifacts[key] = value[:600] + "... [truncated]"
                else:
                    truncated_artifacts[key] = value
            lines.append(f"  Artifacts: {json.dumps(truncated_artifacts, ensure_ascii=True, default=str)}")
        else:
            lines.append("[Last worker result]: None")

        lines.append("\n[Recent worker history]")
        if history:
            for entry in history[-3:]:
                row = _ensure_dict(entry)
                status = _ensure_dict(row.get("result")).get("status")
                lines.append(f"  - {row.get('worker')} -> {status}")
        else:
            lines.append("  None")

        return "\n".join(lines)

    def _last_user_text(self, state: OrchestratorState) -> str:
        messages = state.get("messages", [])
        for message in reversed(messages):
            content = getattr(message, "content", "")
            if isinstance(content, str):
                text = content.strip()
                if text:
                    return text
            elif isinstance(content, list):
                chunks = []
                for part in content:
                    if isinstance(part, str):
                        chunks.append(part)
                    elif isinstance(part, dict) and part.get("type") == "text":
                        chunks.append(str(part.get("text", "")))
                text = " ".join(item.strip() for item in chunks if item.strip()).strip()
                if text:
                    return text
        return ""

    def _extract_bootstrap_constraints(self, user_text: str) -> tuple[str, list[str]]:
        genre_match = re.search(r"genre\s*:\s*([^,\n]+)", user_text, flags=re.IGNORECASE)
        themes_match = re.search(r"themes?\s*:\s*([^\n]+)", user_text, flags=re.IGNORECASE)
        genre = genre_match.group(1).strip() if genre_match else ""
        themes_raw = themes_match.group(1).strip() if themes_match else ""
        themes_raw = re.split(r"\s+\w+\s*:\s*", themes_raw, maxsplit=1)[0]
        pieces = re.split(r",|\band\b|;", themes_raw)
        themes = [piece.strip() for piece in pieces if piece.strip()]
        return genre, themes

    def _is_mvp_mode(self, state: OrchestratorState) -> bool:
        return bool(state.get("mvp_mode"))

    def _normalize_themes(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if _is_non_empty_text(str(item))]
        if isinstance(value, str):
            return [part.strip() for part in re.split(r",|\band\b|;", value) if part.strip()]
        return []

    def _find_worker_history_entry(self, state: OrchestratorState, worker: str) -> Dict[str, Any]:
        history = state.get("worker_history", [])
        if not isinstance(history, list):
            return {}
        for entry in reversed(history):
            row = _ensure_dict(entry)
            if str(row.get("worker") or "") == worker:
                return row
        return {}

    def _latest_worker_artifacts(self, state: OrchestratorState, worker: str) -> Dict[str, Any]:
        entry = self._find_worker_history_entry(state, worker)
        result_data = _ensure_dict(entry.get("result"))
        return _ensure_dict(result_data.get("artifacts"))

    def _mvp_plotting_scene_parameters(self, state: OrchestratorState) -> Dict[str, Any]:
        artifacts = self._latest_worker_artifacts(state, "plotting_subagent")
        return _ensure_dict(artifacts.get("scene_parameters"))

    def _mvp_resolve_pov_character_id(self, requirements: Dict[str, Any], state: OrchestratorState) -> str:
        explicit = str(requirements.get("pov_character_id") or "").strip()
        if explicit:
            return explicit

        scene_params = self._mvp_plotting_scene_parameters(state)
        from_scene = str(scene_params.get("pov_character_id") or "").strip()
        if from_scene:
            return from_scene

        character_artifacts = self._latest_worker_artifacts(state, "character_subagent")
        from_characters = self._first_character_logical_id(character_artifacts)
        if from_characters:
            return from_characters

        return ""

    def _mvp_writing_problem_description(self, requirements: Dict[str, Any], state: OrchestratorState) -> str:
        explicit = str(requirements.get("writing_problem_description") or "").strip()
        if explicit:
            return explicit

        themes = requirements.get("themes") or []
        themes_text = ", ".join(str(theme) for theme in themes if _is_non_empty_text(str(theme)))
        seed_summary = str(requirements.get("planning_seed_summary") or "").strip()
        scene_params = self._mvp_plotting_scene_parameters(state)

        parts = [
            "MVP request: draft a single chapter-1 opening scene (target roughly 1-2 pages of prose).",
            f"Genre: {str(requirements.get('genre') or '').strip()}",
            f"Themes: {themes_text or '(none)'}",
        ]
        if seed_summary:
            parts.append(f"Planning seed summary: {seed_summary}")
        if scene_params:
            parts.append("Gardener scene parameters (JSON):\n" + json.dumps(scene_params, ensure_ascii=True, default=str))
        parts.append(
            "Constraints: one POV, one scene goal, one obstacle, one meaningful choice, end on a concrete beat."
        )
        return "\n".join(parts)

    def _extract_seed_text_from_planning_artifacts(self, artifacts: Dict[str, Any]) -> str:
        seed_doc = _ensure_dict(artifacts.get("seed_document"))
        seed_text = str(seed_doc.get("seed") or "").strip()
        if seed_text:
            return seed_text
        premise = str(artifacts.get("premise") or "").strip()
        if premise:
            return premise
        logline = str(artifacts.get("logline") or "").strip()
        if logline:
            return logline
        return ""

    def _mvp_planning_seed_summary(self, state: OrchestratorState) -> str:
        planning = self._find_worker_history_entry(state, "planning_subagent")
        result_data = _ensure_dict(planning.get("result"))
        artifacts = _ensure_dict(result_data.get("artifacts"))
        seed_text = self._extract_seed_text_from_planning_artifacts(artifacts)
        if seed_text:
            return seed_text
        summary = str(result_data.get("summary") or "").strip()
        if summary:
            return summary
        return "No planning seed text found in worker history; infer from genre and themes."

    def _mvp_default_character_concept(self, requirements: Dict[str, Any], state: OrchestratorState) -> Dict[str, Any]:
        themes = requirements.get("themes") or []
        themes_text = ", ".join(str(theme) for theme in themes if _is_non_empty_text(str(theme)))
        seed_summary = str(requirements.get("planning_seed_summary") or self._mvp_planning_seed_summary(state)).strip()
        return {
            "genre": str(requirements.get("genre") or "").strip(),
            "themes": themes,
            "seed_summary": seed_summary,
            "mvp_brief": (
                f"Create up to {int(requirements.get('max_major_characters') or 5)} major characters for chapter "
                f"{int(requirements.get('chapter_context') or 1)}. "
                f"Genre: {str(requirements.get('genre') or '').strip()}. "
                f"Themes: {themes_text or '(none)'}."
            ),
        }

    def _character_concept_has_user_signal(self, value: Any) -> bool:
        if _is_non_empty_text(value):
            return True
        if not isinstance(value, dict):
            return False
        for nested in value.values():
            if self._character_concept_has_user_signal(nested):
                return True
        return False

    def _resolve_mvp_character_concept(
        self,
        raw: Any,
        base_requirements: Dict[str, Any],
        state: OrchestratorState,
    ) -> Dict[str, Any]:
        defaults = self._mvp_default_character_concept(base_requirements, state)
        if raw is None:
            return defaults
        if _is_non_empty_text(raw):
            merged = dict(defaults)
            merged["user_brief"] = str(raw).strip()
            merged["mvp_brief"] = (
                f"{merged.get('mvp_brief', '').strip()}\n\n"
                f"User direction (highest priority):\n{merged['user_brief']}"
            ).strip()
            return merged
        if isinstance(raw, dict):
            if not self._character_concept_has_user_signal(raw):
                return defaults
            merged = dict(defaults)
            merged.update({key: value for key, value in raw.items() if value is not None})
            return merged
        return defaults

    def _mvp_requirements(self, state: OrchestratorState) -> Dict[str, Any]:
        context = _ensure_dict(state.get("mvp_requirements"))
        user_text = self._last_user_text(state)
        parsed_genre, parsed_themes = self._extract_bootstrap_constraints(user_text)
        genre = str(context.get("genre") or parsed_genre).strip()
        themes = self._normalize_themes(context.get("themes")) or parsed_themes
        chapter_context = int(context.get("chapter_context") or self.config.mvp_default_chapter_context)
        max_major_characters = int(context.get("max_major_characters") or self.config.mvp_max_major_characters)
        target_scene_pages = str(context.get("target_scene_pages") or self.config.mvp_target_scene_pages).strip()
        pov_character_id = str(context.get("pov_character_id") or "").strip()
        last_scene_outcome = str(context.get("last_scene_outcome") or "").strip()
        if not pov_character_id:
            latest = _ensure_dict(state.get("latest_worker_result"))
            if str(latest.get("worker") or "") == "character_subagent":
                result_data = _ensure_dict(latest.get("result"))
                artifacts = _ensure_dict(result_data.get("artifacts"))
                pov_character_id = self._first_character_logical_id(artifacts)
            else:
                character_entry = self._find_worker_history_entry(state, "character_subagent")
                result_data = _ensure_dict(character_entry.get("result"))
                artifacts = _ensure_dict(result_data.get("artifacts"))
                pov_character_id = self._first_character_logical_id(artifacts)
        if not pov_character_id:
            pov_character_id = self._mvp_resolve_pov_character_id(
                {
                    "genre": genre,
                    "themes": themes,
                    "chapter_context": chapter_context,
                    "max_major_characters": max_major_characters,
                    "pov_character_id": "",
                },
                state,
            )
        planning_seed_summary = str(context.get("planning_seed_summary") or "").strip()
        if not planning_seed_summary:
            planning_seed_summary = self._mvp_planning_seed_summary(state)
        character_concept = self._resolve_mvp_character_concept(
            context.get("character_concept"),
            {
                "genre": genre,
                "themes": themes,
                "chapter_context": chapter_context,
                "max_major_characters": max_major_characters,
                "planning_seed_summary": planning_seed_summary,
            },
            state,
        )
        return {
            "genre": genre,
            "themes": themes,
            "chapter_context": chapter_context,
            "max_major_characters": max_major_characters,
            "target_scene_pages": target_scene_pages or "1-2",
            "pov_character_id": pov_character_id,
            "last_scene_outcome": last_scene_outcome,
            "planning_seed_summary": planning_seed_summary,
            "character_concept": character_concept,
            "writing_problem_description": str(context.get("writing_problem_description") or "").strip(),
        }

    def _build_mvp_worker_request(
        self,
        worker: str,
        requirements: Dict[str, Any],
        state: OrchestratorState,
    ) -> tuple[str, Dict[str, Any]]:
        chapter_context = int(requirements["chapter_context"])
        base_context = {
            "chapter_context": chapter_context,
            "genre": requirements["genre"],
            "themes": requirements["themes"],
            "mvp_mode": True,
        }
        if worker == "planning_subagent":
            return (
                "Run finding-a-seed for a bare-bones novel bootstrap focused on chapter 1 setup.",
                {
                    **base_context,
                    "skill": "finding-a-seed",
                    "operation": "finding-a-seed",
                },
            )
        if worker == "plotting_subagent":
            pov_id = str(requirements.get("pov_character_id") or "").strip()
            last_outcome = str(requirements.get("last_scene_outcome") or "").strip()
            if not last_outcome:
                last_outcome = (
                    "Cold open at the start of chapter 1: no prior in-story scene exists; "
                    "establish tone, setting, and immediate pressure from the premise."
                )
            if not pov_id:
                pov_id = "mvp_placeholder_pov"
            plotting_ctx = {
                **base_context,
                "skill": "gardener-plotting-system",
                "operation": "gardener-plotting-system",
                "last_scene_outcome": last_outcome,
                "pov_character_id": pov_id,
            }
            return (
                "Run gardener-plotting-system to build world scaffolding and chapter-1 scene setup.",
                plotting_ctx,
            )
        if worker == "character_subagent":
            return (
                "Run character-creation and produce up to five major characters for chapter 1.",
                {
                    **base_context,
                    "skill": "character-creation",
                    "operation": "character-creation",
                    "max_major_characters": int(requirements["max_major_characters"]),
                    "character_concept": _ensure_dict(requirements.get("character_concept")),
                },
            )
        pov_for_writing = str(requirements.get("pov_character_id") or "").strip() or self._mvp_resolve_pov_character_id(
            requirements,
            state,
        )
        scene_parameters = self._mvp_plotting_scene_parameters(state)
        problem_description = self._mvp_writing_problem_description(requirements, state)
        writing_ctx = {
            **base_context,
            "skill": "scene-construction",
            "operation": "scene-construction",
            "target_scene_pages": requirements["target_scene_pages"],
            "target_output": "single_scene_chapter_1",
            "problem_description": problem_description,
            "pov_character_id": pov_for_writing,
            "scene_parameters": scene_parameters,
        }
        return (
            "Write one chapter-1 opening scene (target length: 1-2 pages) using established world and major characters.",
            writing_ctx,
        )

    def _scene_text_from_result(self, result_data: Dict[str, Any]) -> str:
        artifacts = _ensure_dict(result_data.get("artifacts"))
        for key in (
            "draft_prose",
            "scene_text",
            "scene_draft",
            "draft_scene",
            "chapter_scene",
            "chapter_opening_scene",
            "final_scene",
            "output_text",
            "prose",
        ):
            value = artifacts.get(key)
            if _is_non_empty_text(value):
                return str(value).strip()
        for value in artifacts.values():
            if isinstance(value, dict):
                for nested in value.values():
                    if _is_non_empty_text(nested):
                        return str(nested).strip()
        summary = str(result_data.get("summary") or "").strip()
        if summary:
            return summary
        return "MVP run completed, but no scene text was returned by the writing worker."

    def _count_character_records(self, artifacts: Dict[str, Any]) -> int:
        for key in ("major_characters", "character_profiles", "characters"):
            candidate = artifacts.get(key)
            if isinstance(candidate, list):
                return len(candidate)

        count = 0
        for value in artifacts.values():
            if not isinstance(value, list):
                continue
            for item in value:
                row = _ensure_dict(item)
                node_type = str(row.get("node_type") or row.get("type") or "").strip().lower()
                if node_type == "character":
                    count += 1
        return count

    def _first_character_logical_id(self, artifacts: Dict[str, Any]) -> str:
        for key in ("major_characters", "character_profiles", "characters"):
            candidate = artifacts.get(key)
            if not isinstance(candidate, list):
                continue
            for item in candidate:
                row = _ensure_dict(item)
                logical_id = str(row.get("logical_id") or "").strip()
                if logical_id:
                    return logical_id
                node_type = str(row.get("node_type") or row.get("type") or "").strip().lower()
                if node_type == "character":
                    logical_id = str(row.get("logical_id") or "").strip()
                    if logical_id:
                        return logical_id

        for value in artifacts.values():
            if not isinstance(value, list):
                continue
            for item in value:
                row = _ensure_dict(item)
                node_type = str(row.get("node_type") or row.get("type") or "").strip().lower()
                if node_type != "character":
                    continue
                logical_id = str(row.get("logical_id") or "").strip()
                if logical_id:
                    return logical_id
        return ""

    def _latest_creative_result_from_history(self, state: OrchestratorState) -> Dict[str, Any]:
        history = state.get("worker_history", [])
        if not isinstance(history, list):
            return {}
        for entry in reversed(history):
            row = _ensure_dict(entry)
            worker = str(row.get("worker") or "")
            if worker in MVP_WORKER_SEQUENCE:
                return row
        return {}

    def _next_mvp_worker(self, current_worker: str) -> str | None:
        if current_worker not in MVP_WORKER_SEQUENCE:
            return MVP_WORKER_SEQUENCE[0]
        idx = MVP_WORKER_SEQUENCE.index(current_worker)
        if idx + 1 >= len(MVP_WORKER_SEQUENCE):
            return None
        return MVP_WORKER_SEQUENCE[idx + 1]

    def _mvp_decision(self, state: OrchestratorState) -> BrainDecision:
        requirements = self._mvp_requirements(state)
        if not requirements["genre"] or not requirements["themes"]:
            return BrainDecision(
                reasoning="MVP mode requires explicit genre and themes.",
                action="clarify",
                response=(
                    "MVP mode needs both genre and themes before I can run.\n"
                    "Please provide input like:\n"
                    "genre: political fantasy\n"
                    "themes: loyalty, betrayal"
                ),
            )

        latest = _ensure_dict(state.get("latest_worker_result"))
        if not latest:
            task, context = self._build_mvp_worker_request("planning_subagent", self._mvp_requirements(state), state)
            return BrainDecision(
                reasoning="MVP sequencer kickoff starts with planning.",
                action="delegate",
                worker="planning_subagent",
                task=task,
                context=context,
            )

        worker = str(latest.get("worker") or "")
        result_data = _ensure_dict(latest.get("result"))
        status = str(result_data.get("status") or "").strip()
        summary = str(result_data.get("summary") or "").strip()
        follow_up_questions = result_data.get("follow_up_questions")
        follow_up_list = follow_up_questions if isinstance(follow_up_questions, list) else []
        artifacts = _ensure_dict(result_data.get("artifacts"))

        if status == "need_input":
            return BrainDecision(
                reasoning=f"{worker} requested additional details in MVP mode.",
                action="clarify",
                response=self._format_follow_up(summary, follow_up_list),
            )

        if status in {"blocked", "failed"}:
            return BrainDecision(
                reasoning=f"{worker} could not complete MVP step.",
                action="respond",
                response=summary or f"MVP flow stopped because {worker} returned status '{status}'.",
            )

        if status != "success":
            return BrainDecision(
                reasoning=f"{worker} returned unsupported status in MVP mode.",
                action="respond",
                response=f"MVP flow stopped because {worker} returned unsupported status '{status}'.",
            )

        if worker == "story_state_manager":
            latest_creative = self._latest_creative_result_from_history(state)
            creative_worker = str(latest_creative.get("worker") or "")
            if creative_worker == "writing_subagent":
                writing_result = _ensure_dict(latest_creative.get("result"))
                return BrainDecision(
                    reasoning="Writing is complete; finish MVP flow.",
                    action="respond",
                    response=self._scene_text_from_result(writing_result),
                )
            next_worker = self._next_mvp_worker(creative_worker)
            if not next_worker:
                return BrainDecision(
                    reasoning="No remaining MVP steps after persistence.",
                    action="respond",
                    response="MVP flow completed.",
                )
            task, context = self._build_mvp_worker_request(next_worker, self._mvp_requirements(state), state)
            return BrainDecision(
                reasoning=f"MVP sequencer continues after persistence with {next_worker}.",
                action="delegate",
                worker=next_worker,
                task=task,
                context=context,
            )

        if worker == "writing_subagent":
            return BrainDecision(
                reasoning="Writing step completed in MVP mode.",
                action="respond",
                response=self._scene_text_from_result(result_data),
            )

        if worker == "character_subagent":
            character_count = self._count_character_records(artifacts)
            requirements = self._mvp_requirements(state)
            if character_count > int(requirements["max_major_characters"]):
                return BrainDecision(
                    reasoning="Character cap exceeded in MVP mode.",
                    action="respond",
                    response=(
                        f"MVP flow stopped because character output exceeded the cap of "
                        f"{requirements['max_major_characters']} (received {character_count})."
                    ),
                )

        requirements = self._mvp_requirements(state)
        mapper_result = self.persist_mapper.build_context(latest, {})
        if mapper_result.has_payload:
            return BrainDecision(
                reasoning=f"MVP sequencer persists accepted output from {worker}.",
                action="delegate",
                worker="story_state_manager",
                task="Persist accepted records to story state",
                context=mapper_result.context,
            )

        next_worker = self._next_mvp_worker(worker)
        if not next_worker:
            return BrainDecision(
                reasoning="Final MVP worker already completed.",
                action="respond",
                response=self._scene_text_from_result(result_data),
            )
        task, context = self._build_mvp_worker_request(next_worker, requirements, state)
        return BrainDecision(
            reasoning=f"MVP sequencer advances from {worker} to {next_worker}.",
            action="delegate",
            worker=next_worker,
            task=task,
            context=context,
        )

    def _bootstrap_kickoff_decision(self, state: OrchestratorState) -> BrainDecision | None:
        if state.get("latest_worker_result"):
            return None
        if int(state.get("iteration_count", 0)) != 0:
            return None

        user_text = self._last_user_text(state)
        genre, themes = self._extract_bootstrap_constraints(user_text)
        if not genre or not themes:
            return None

        return BrainDecision(
            reasoning="Bootstrap kickoff guardrail: explicit genre/themes provided, so start with finding-a-seed.",
            action="delegate",
            worker="planning_subagent",
            task="Run finding-a-seed for novel bootstrap.",
            context={
                "skill": "finding-a-seed",
                "genre": genre,
                "themes": themes,
                "chapter_context": 1,
            },
            response=None,
            quality_assessment=None,
        )

    def _bootstrap_constraints_satisfied(self, state: OrchestratorState) -> bool:
        genre, themes = self._extract_bootstrap_constraints(self._last_user_text(state))
        return bool(genre) and bool(themes)

    @staticmethod
    def _context_skill_hint(context: Dict[str, Any]) -> str:
        return str(context.get("skill") or context.get("operation") or "").strip().lower()

    def _worker_history_list(self, state: OrchestratorState) -> list[Dict[str, Any]]:
        history = state.get("worker_history", [])
        if not isinstance(history, list):
            return []
        return [_ensure_dict(entry) for entry in history]

    def _latest_finding_seed_planning_entry(self, history: list[Dict[str, Any]]) -> Dict[str, Any]:
        for entry in reversed(history):
            if str(entry.get("worker") or "") != "planning_subagent":
                continue
            result_data = _ensure_dict(entry.get("result"))
            if str(result_data.get("status") or "") != "success":
                continue
            ctx = _ensure_dict(entry.get("context"))
            sk = self._context_skill_hint(ctx)
            if sk in {"finding-a-seed", "finding_a_seed"}:
                artifacts = _ensure_dict(result_data.get("artifacts"))
                if isinstance(artifacts.get("seed_document"), dict) and artifacts.get("seed_document"):
                    return entry
        return {}

    def _latest_pass1_planning_entry(self, history: list[Dict[str, Any]]) -> Dict[str, Any]:
        for entry in reversed(history):
            if str(entry.get("worker") or "") != "planning_subagent":
                continue
            result_data = _ensure_dict(entry.get("result"))
            if str(result_data.get("status") or "") != "success":
                continue
            artifacts = _ensure_dict(result_data.get("artifacts"))
            if artifacts.get("pass") == 1 and isinstance(artifacts.get("character_slot_sketches"), list):
                return entry
        return {}

    def _latest_pass2_planning_entry(self, history: list[Dict[str, Any]]) -> Dict[str, Any]:
        for entry in reversed(history):
            if str(entry.get("worker") or "") != "planning_subagent":
                continue
            result_data = _ensure_dict(entry.get("result"))
            if str(result_data.get("status") or "") != "success":
                continue
            artifacts = _ensure_dict(result_data.get("artifacts"))
            if artifacts.get("pass") == 2:
                return entry
        return {}

    def _pass2_compass_for_worldbuilding(self, pass2_artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Pass-through copy suitable for worldbuilding subgraph (expects a dict)."""
        return dict(pass2_artifacts) if pass2_artifacts else {}

    def _entry_before_latest_ssm(self, history: list[Dict[str, Any]]) -> Dict[str, Any]:
        if len(history) < 2:
            return {}
        last = history[-1]
        if str(last.get("worker") or "") != "story_state_manager":
            return {}
        return _ensure_dict(history[-2])

    def _last_pass1_history_index(self, history: list[Dict[str, Any]]) -> int:
        for idx in range(len(history) - 1, -1, -1):
            entry = history[idx]
            if str(entry.get("worker") or "") != "planning_subagent":
                continue
            result_data = _ensure_dict(entry.get("result"))
            if str(result_data.get("status") or "") != "success":
                continue
            art = _ensure_dict(result_data.get("artifacts"))
            if art.get("pass") == 1 and isinstance(art.get("character_slot_sketches"), list):
                return idx
        return -1

    def _early_concepts_since_pass1(self, history: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        idx = self._last_pass1_history_index(history)
        if idx < 0:
            return []
        concepts: list[Dict[str, Any]] = []
        for entry in history[idx + 1 :]:
            if str(entry.get("worker") or "") != "character_subagent":
                continue
            ctx = _ensure_dict(entry.get("context"))
            if not isinstance(ctx.get("character_slot_sketch"), dict):
                continue
            result_data = _ensure_dict(entry.get("result"))
            if str(result_data.get("status") or "") != "success":
                continue
            slot_sk = _ensure_dict(ctx.get("character_slot_sketch"))
            slot_id = str(slot_sk.get("slot_id") or "").strip()
            art = _ensure_dict(result_data.get("artifacts"))
            char_concept = _ensure_dict(art.get("character_concept"))
            concepts.append(
                {
                    "slot_id": slot_id,
                    "character_id": str(char_concept.get("character_id") or "").strip()
                    or str(char_concept.get("assigned_narrative_role") or slot_id or "char_slot").replace(
                        " ", "_"
                    ).lower(),
                    "name": str(char_concept.get("name") or char_concept.get("assigned_narrative_role") or "").strip()
                    or slot_id
                    or "Character",
                    "core_contradiction": str(char_concept.get("core_contradiction") or "").strip()
                    or "Contradiction to refine in creation.",
                }
            )
        return concepts

    def _missing_slot_sketches(
        self,
        pass1_artifacts: Dict[str, Any],
        covered_slot_ids: set[str],
    ) -> list[Dict[str, Any]]:
        slots = _ensure_list(pass1_artifacts.get("character_slot_sketches"))
        missing: list[Dict[str, Any]] = []
        for slot in slots:
            row = _ensure_dict(slot)
            sid = str(row.get("slot_id") or "").strip()
            if sid and sid not in covered_slot_ids:
                missing.append(row)
        return missing

    def _world_context_sketch_from_pass1(self, pass1_artifacts: Dict[str, Any]) -> str:
        parts = [
            str(pass1_artifacts.get("starting_situation") or "").strip(),
            str(pass1_artifacts.get("draft_ending_destination") or "").strip(),
            str(pass1_artifacts.get("draft_core_conflict_question") or "").strip(),
            str(pass1_artifacts.get("compass_notes") or "").strip(),
        ]
        text = "\n\n".join(p for p in parts if p).strip()
        return text or "Bootstrap world context pending detailed worldbuilding."

    def _bootstrap_progression_decision(self, state: OrchestratorState) -> BrainDecision | None:
        if self._is_mvp_mode(state):
            return None
        if not self._bootstrap_constraints_satisfied(state):
            return None

        latest = _ensure_dict(state.get("latest_worker_result"))
        if not latest:
            return None

        history = self._worker_history_list(state)
        accept = QualityVerdict(verdict="accept", reason="Bootstrap sequencer accepts prior worker output.")
        genre, themes = self._extract_bootstrap_constraints(self._last_user_text(state))

        worker = str(latest.get("worker") or "")
        result_data = _ensure_dict(latest.get("result"))
        status = str(result_data.get("status") or "").strip()
        artifacts = _ensure_dict(result_data.get("artifacts"))
        context = _ensure_dict(latest.get("context"))

        if worker == "story_state_manager" and status == "success":
            prior = self._entry_before_latest_ssm(history)
            if not prior:
                return None
            prior_worker = str(prior.get("worker") or "")
            prior_result = _ensure_dict(prior.get("result"))
            prior_status = str(prior_result.get("status") or "").strip()
            prior_art = _ensure_dict(prior_result.get("artifacts"))
            prior_ctx = _ensure_dict(prior.get("context"))

            if prior_worker == "planning_subagent" and prior_status == "success":
                if prior_art.get("pass") == 2 and prior_art.get("plot_thread_seeds"):
                    compass = self._pass2_compass_for_worldbuilding(prior_art)
                    return BrainDecision(
                        reasoning="Bootstrap sequencer: after persisting Pass 2 plot seeds, run worldbuilding with endpoint_compass.",
                        action="delegate",
                        worker="planning_subagent",
                        task="Construct foundational world architecture from the Pass 2 endpoint compass.",
                        context={
                            "skill": "worldbuilding",
                            "operation": "worldbuilding",
                            "chapter_context": int(prior_ctx.get("chapter_context") or 1),
                            "endpoint_compass": compass,
                        },
                        quality_assessment=None,
                    )
                if self._context_skill_hint(prior_ctx) in {"worldbuilding", "world_building"} or prior_art.get(
                    "political_power_map"
                ):
                    return None
                sk = self._context_skill_hint(prior_ctx)
                if sk in {"finding-a-seed", "finding_a_seed"}:
                    pass1_entry = self._latest_pass1_planning_entry(history)
                    if pass1_entry:
                        return None
                    seed_entry = self._latest_finding_seed_planning_entry(history)
                    seed_doc = _ensure_dict(
                        _ensure_dict(seed_entry.get("result")).get("artifacts", {}).get("seed_document")
                    )
                    if not seed_doc:
                        return None
                    return BrainDecision(
                        reasoning="Bootstrap sequencer: after seed persistence, run defining-rough-endpoints Pass 1.",
                        action="delegate",
                        worker="planning_subagent",
                        task="Run defining-rough-endpoints Pass 1 from the validated seed document.",
                        context={
                            "skill": "defining-rough-endpoints",
                            "operation": "defining-rough-endpoints",
                            "pass": "1",
                            "chapter_context": 1,
                            "seed_document": seed_doc,
                            "genre": genre,
                            "themes": themes,
                        },
                        quality_assessment=None,
                    )

            if prior_worker == "character_subagent" and prior_status == "success":
                seed_entry = self._latest_finding_seed_planning_entry(history)
                seed_doc = _ensure_dict(
                    _ensure_dict(seed_entry.get("result")).get("artifacts", {}).get("seed_document")
                )
                pass1_entry = self._latest_pass1_planning_entry(history)
                if not pass1_entry:
                    if not seed_doc:
                        return None
                    return BrainDecision(
                        reasoning="Bootstrap sequencer: recover ordering — run defining-rough-endpoints Pass 1.",
                        action="delegate",
                        worker="planning_subagent",
                        task="Run defining-rough-endpoints Pass 1 from the validated seed document.",
                        context={
                            "skill": "defining-rough-endpoints",
                            "operation": "defining-rough-endpoints",
                            "pass": "1",
                            "chapter_context": 1,
                            "seed_document": seed_doc,
                            "genre": genre,
                            "themes": themes,
                        },
                        quality_assessment=None,
                    )
                pass1_art = _ensure_dict(_ensure_dict(pass1_entry.get("result")).get("artifacts"))
                covered = {
                    str(_ensure_dict(c).get("slot_id") or "").strip()
                    for c in self._early_concepts_since_pass1(history)
                }
                missing_slots = self._missing_slot_sketches(pass1_art, covered)
                if missing_slots:
                    slot = missing_slots[0]
                    return BrainDecision(
                        reasoning="Bootstrap sequencer: early character-conception for next slot after persistence.",
                        action="delegate",
                        worker="character_subagent",
                        task=(
                            f"Run character-conception in early invocation mode for slot {slot.get('slot_id', '')}."
                        ),
                        context={
                            "skill": "character-conception",
                            "chapter_context": 1,
                            "character_slot_sketch": slot,
                            "world_context_sketch": self._world_context_sketch_from_pass1(pass1_art),
                            "thematic_constraints": {"genre": genre, "themes": themes},
                        },
                        quality_assessment=None,
                    )
                pass2_entry = self._latest_pass2_planning_entry(history)
                if not pass2_entry:
                    concepts = self._early_concepts_since_pass1(history)
                    if not concepts:
                        return None
                    return BrainDecision(
                        reasoning="Bootstrap sequencer: all slots conceived — run defining-rough-endpoints Pass 2.",
                        action="delegate",
                        worker="planning_subagent",
                        task="Run defining-rough-endpoints Pass 2 to refine milestones with character concepts.",
                        context={
                            "skill": "defining-rough-endpoints-pass-2",
                            "pass": "2",
                            "chapter_context": 1,
                            "pass_1_output": pass1_art,
                            "character_concepts": concepts,
                        },
                        quality_assessment=None,
                    )
            return None

        if worker == "planning_subagent" and status == "success" and artifacts.get("pass") == 1:
            pass1_art = artifacts
            if self._last_pass1_history_index(history) < 0:
                return None
            covered_ids = {
                str(_ensure_dict(c).get("slot_id") or "").strip()
                for c in self._early_concepts_since_pass1(history)
            }
            missing = self._missing_slot_sketches(pass1_art, covered_ids)
            if missing:
                slot = missing[0]
                return BrainDecision(
                    reasoning="Bootstrap sequencer: delegate early character-conception for Pass 1 slot.",
                    action="delegate",
                    worker="character_subagent",
                    task=f"Run character-conception in early invocation mode for slot {slot.get('slot_id', '')}.",
                    context={
                        "skill": "character-conception",
                        "chapter_context": 1,
                        "character_slot_sketch": slot,
                        "world_context_sketch": self._world_context_sketch_from_pass1(pass1_art),
                        "thematic_constraints": {"genre": genre, "themes": themes},
                    },
                    quality_assessment=accept,
                )
            concepts = self._early_concepts_since_pass1(history)
            if not concepts:
                return None
            return BrainDecision(
                reasoning="Bootstrap sequencer: Pass 1 complete — run defining-rough-endpoints Pass 2.",
                action="delegate",
                worker="planning_subagent",
                task="Run defining-rough-endpoints Pass 2 to refine milestones with character concepts.",
                context={
                    "skill": "defining-rough-endpoints-pass-2",
                    "pass": "2",
                    "chapter_context": 1,
                    "pass_1_output": pass1_art,
                    "character_concepts": concepts,
                },
                quality_assessment=accept,
            )

        if worker == "character_subagent" and status == "success":
            if not isinstance(context.get("character_slot_sketch"), dict):
                return None
            pass1_entry = self._latest_pass1_planning_entry(history)
            if not pass1_entry:
                return None
            pass1_art = _ensure_dict(_ensure_dict(pass1_entry.get("result")).get("artifacts"))
            covered_ids = {
                str(_ensure_dict(c).get("slot_id") or "").strip()
                for c in self._early_concepts_since_pass1(history)
            }
            missing = self._missing_slot_sketches(pass1_art, covered_ids)
            if missing:
                slot = missing[0]
                return BrainDecision(
                    reasoning="Bootstrap sequencer: next early character-conception slot.",
                    action="delegate",
                    worker="character_subagent",
                    task=f"Run character-conception in early invocation mode for slot {slot.get('slot_id', '')}.",
                    context={
                        "skill": "character-conception",
                        "chapter_context": 1,
                        "character_slot_sketch": slot,
                        "world_context_sketch": self._world_context_sketch_from_pass1(pass1_art),
                        "thematic_constraints": {"genre": genre, "themes": themes},
                    },
                    quality_assessment=accept,
                )
            concepts = self._early_concepts_since_pass1(history)
            if not concepts:
                return None
            return BrainDecision(
                reasoning="Bootstrap sequencer: all slots conceived — run defining-rough-endpoints Pass 2.",
                action="delegate",
                worker="planning_subagent",
                task="Run defining-rough-endpoints Pass 2 to refine milestones with character concepts.",
                context={
                    "skill": "defining-rough-endpoints-pass-2",
                    "pass": "2",
                    "chapter_context": 1,
                    "pass_1_output": pass1_art,
                    "character_concepts": concepts,
                },
                quality_assessment=accept,
            )

        if worker == "planning_subagent" and status == "success" and artifacts.get("pass") == 2:
            return BrainDecision(
                reasoning="Bootstrap sequencer: accept defining-rough-endpoints Pass 2 and persist plot/payoff seeds.",
                action="delegate",
                worker="story_state_manager",
                task="Persist accepted records to story state",
                context={},
                quality_assessment=accept,
            )

        return None

    def _merge_bootstrap_worldbuilding_compass(self, decision: BrainDecision, state: OrchestratorState) -> None:
        """If LLM delegates worldbuilding without endpoint_compass, inject from Pass 2 history when possible."""
        if self._is_mvp_mode(state) or not self._bootstrap_constraints_satisfied(state):
            return
        if decision.action != "delegate" or decision.worker != "planning_subagent":
            return
        ctx = _ensure_dict(decision.context)
        task = str(decision.task or "").lower()
        sk = self._context_skill_hint(ctx)
        if sk not in {"worldbuilding", "world_building"} and "worldbuilding" not in task and "world building" not in task:
            return
        if isinstance(ctx.get("endpoint_compass"), dict):
            return
        pass2_entry = self._latest_pass2_planning_entry(self._worker_history_list(state))
        if not pass2_entry:
            return
        pass2_art = _ensure_dict(_ensure_dict(pass2_entry.get("result")).get("artifacts"))
        ctx["endpoint_compass"] = self._pass2_compass_for_worldbuilding(pass2_art)
        decision.context = ctx

    def _bootstrap_planning_need_input_override(self, state: OrchestratorState) -> BrainDecision | None:
        """Recover from planning need_input (e.g. worldbuilding without compass) without ending the turn."""
        if self._is_mvp_mode(state) or not self._bootstrap_constraints_satisfied(state):
            return None
        latest = _ensure_dict(state.get("latest_worker_result"))
        if str(latest.get("worker") or "") != "planning_subagent":
            return None
        result_data = _ensure_dict(latest.get("result"))
        if str(result_data.get("status") or "") != "need_input":
            return None
        art = _ensure_dict(result_data.get("artifacts"))
        history = self._worker_history_list(state)
        skill_attempted = str(art.get("skill_attempted") or "").lower()
        missing = art.get("missing_fields") or []
        missing_list = missing if isinstance(missing, list) else []

        if skill_attempted == "worldbuilding" or "endpoint_compass" in missing_list:
            pass2_entry = self._latest_pass2_planning_entry(history)
            if pass2_entry:
                pass2_art = _ensure_dict(_ensure_dict(pass2_entry.get("result")).get("artifacts"))
                return BrainDecision(
                    reasoning="Bootstrap recovery: retry worldbuilding with endpoint_compass from Pass 2.",
                    action="delegate",
                    worker="planning_subagent",
                    task="Construct foundational world architecture from the Pass 2 endpoint compass.",
                    context={
                        "skill": "worldbuilding",
                        "operation": "worldbuilding",
                        "chapter_context": 1,
                        "endpoint_compass": self._pass2_compass_for_worldbuilding(pass2_art),
                    },
                    quality_assessment=None,
                )
            seed_entry = self._latest_finding_seed_planning_entry(history)
            seed_doc = _ensure_dict(
                _ensure_dict(seed_entry.get("result")).get("artifacts", {}).get("seed_document")
            )
            if seed_doc and not self._latest_pass1_planning_entry(history):
                genre, themes = self._extract_bootstrap_constraints(self._last_user_text(state))
                return BrainDecision(
                    reasoning="Bootstrap recovery: run defining-rough-endpoints Pass 1 before worldbuilding.",
                    action="delegate",
                    worker="planning_subagent",
                    task="Run defining-rough-endpoints Pass 1 from the validated seed document.",
                    context={
                        "skill": "defining-rough-endpoints",
                        "operation": "defining-rough-endpoints",
                        "pass": "1",
                        "chapter_context": 1,
                        "seed_document": seed_doc,
                        "genre": genre,
                        "themes": themes,
                    },
                    quality_assessment=None,
                )
        return None

    def _invoke_decision_model(self, state: OrchestratorState) -> BrainDecision:
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(state.get("messages", []))
        messages.append(HumanMessage(content=self._build_context_block(state)))

        try:
            return self.llm.with_structured_output(BrainDecision).invoke(messages)
        except Exception as error:
            print(f"Brain LLM structured output failed: {error}. Trying fallback...")
            fallback = self.llm.with_structured_output(BrainDecisionFallback).invoke(messages)
            quality_assessment = None
            if fallback.quality_verdict:
                quality_assessment = QualityVerdict(
                    verdict=fallback.quality_verdict,
                    reason=fallback.quality_reason or "Fallback quality reason unavailable.",
                )
            return BrainDecision(
                reasoning=fallback.reasoning,
                action=fallback.action,
                worker=fallback.worker,
                task=fallback.task,
                context=fallback.context,
                response=fallback.response,
                quality_assessment=quality_assessment,
            )

    def _set_response(
        self,
        decision: BrainDecision,
        action: Literal["respond", "clarify"],
        response: str,
    ) -> BrainDecision:
        decision.action = action
        decision.worker = None
        decision.task = None
        decision.context = {}
        decision.response = response.strip()
        decision.quality_assessment = None
        return decision

    def _sanitize_and_validate_decision(self, decision: BrainDecision, state: OrchestratorState) -> BrainDecision:
        decision.context = _ensure_dict(decision.context)
        if decision.action == "delegate":
            if decision.worker not in VALID_WORKERS:
                return self._set_response(
                    decision,
                    "clarify",
                    (
                        "I need one clarification before I continue.\n"
                        "1) Which part should I work on next: planning, character, plotting, writing, consequence, or persistence?\n"
                        "2) What specific outcome should that step produce?"
                    ),
                )
            if not _is_non_empty_text(decision.task):
                latest_task = str(_ensure_dict(state.get("latest_worker_result")).get("task") or "").strip()
                if latest_task:
                    decision.task = latest_task
                elif decision.worker == "story_state_manager":
                    decision.task = "Persist accepted records to story state"
                else:
                    return self._set_response(
                        decision,
                        "clarify",
                        (
                            "I need a bit more direction before proceeding.\n"
                            "1) What should the next worker accomplish?\n"
                            "2) Are there mandatory constraints for that step?"
                        ),
                    )
            decision.task = str(decision.task).strip()
            decision.response = None
            decision.quality_assessment = decision.quality_assessment
            return decision

        decision.worker = None
        decision.task = None
        decision.context = {}
        if not _is_non_empty_text(decision.response):
            if decision.action == "clarify":
                decision.response = (
                    "I need clarification before proceeding.\n"
                    "1) What exact output do you want next?\n"
                    "2) Any constraints I should enforce?"
                )
            else:
                decision.response = "I can continue as soon as you share the next concrete objective."
        return decision

    def _format_follow_up(self, summary: str, follow_up_questions: list[Any]) -> str:
        cleaned = [str(q).strip() for q in follow_up_questions if _is_non_empty_text(str(q))]
        if cleaned:
            question_lines = [f"{idx}. {question}" for idx, question in enumerate(cleaned[:3], start=1)]
            prefix = summary.strip() if summary.strip() else "I need a little more information."
            return f"{prefix}\n" + "\n".join(question_lines)
        return summary.strip() if summary.strip() else "I need a little more information before continuing."

    def _build_resolution_analyse_response(self, artifacts: Dict[str, Any]) -> str:
        briefing = str(artifacts.get("briefing") or "I found a contradiction that needs your decision.")
        options = artifacts.get("resolution_options")
        option_lines: list[str] = []
        if isinstance(options, list):
            for option in options[:4]:
                if not isinstance(option, dict):
                    continue
                option_id = str(option.get("option_id") or "").strip()
                label = str(option.get("label") or "").strip()
                description = str(option.get("description") or "").strip()
                text = f"{option_id}: {label}" if label else option_id
                if description:
                    text = f"{text} - {description}".strip()
                if text:
                    option_lines.append(text)
        if option_lines:
            return f"{briefing}\n\nOptions:\n" + "\n".join(f"- {line}" for line in option_lines)
        return briefing

    def _has_write_payload(self, context: Dict[str, Any]) -> bool:
        for key in ("nodes_to_add", "nodes_to_update", "edges_to_add", "edges_to_update"):
            if isinstance(context.get(key), list) and context.get(key):
                return True
        return False

    def _prepare_persistence_retry_context(
        self,
        context: Dict[str, Any],
        artifacts: Dict[str, Any],
    ) -> Dict[str, Any]:
        retry_context = dict(context)
        updated_ids = {
            str(item).strip()
            for item in artifacts.get("records_updated", [])
            if _is_non_empty_text(str(item))
        }
        failed_records = artifacts.get("records_failed", [])
        failed_ids = {
            str(_ensure_dict(entry).get("logical_id") or "").strip()
            for entry in failed_records
            if _is_non_empty_text(str(_ensure_dict(entry).get("logical_id") or ""))
        }

        def select_records(records: Any) -> list[Dict[str, Any]]:
            chosen: list[Dict[str, Any]] = []
            if not isinstance(records, list):
                return chosen
            for record in records:
                record_dict = _ensure_dict(record)
                logical_id = str(record_dict.get("logical_id") or "").strip()
                if not logical_id:
                    continue
                if failed_ids:
                    if logical_id in failed_ids:
                        chosen.append(record_dict)
                    continue
                if logical_id not in updated_ids:
                    chosen.append(record_dict)
            return chosen

        for key in ("nodes_to_add", "nodes_to_update", "edges_to_add", "edges_to_update"):
            retry_context[key] = select_records(context.get(key))

        retry_context["persistence_retry_count"] = int(context.get("persistence_retry_count", 0)) + 1
        return retry_context

    def _apply_infrastructure_overrides(self, decision: BrainDecision, state: OrchestratorState) -> BrainDecision:
        latest = _ensure_dict(state.get("latest_worker_result"))
        if not latest:
            return decision

        worker = str(latest.get("worker") or "")
        result_data = _ensure_dict(latest.get("result"))
        status = str(result_data.get("status") or "")
        summary = str(result_data.get("summary") or "")
        artifacts = _ensure_dict(result_data.get("artifacts"))
        context = _ensure_dict(latest.get("context"))

        if worker == "story_state_manager" and status == "blocked":
            decision.action = "delegate"
            decision.worker = "resolution_subagent"
            decision.task = "Analyse KG contradiction blocking persistence"
            decision.context = {
                "mode": "ANALYSE",
                "contradiction_record": _ensure_dict(artifacts.get("contradiction_record")),
                "blocked_write": {
                    "write_type": "story_state_manager",
                    "proposed_context": context,
                },
                "prefetched_docs": [],
            }
            decision.response = None
            decision.quality_assessment = None
            return decision

        if worker == "story_state_manager" and status == "failed":
            retry_count = int(context.get("persistence_retry_count", 0))
            if retry_count < 1 and self._has_write_payload(context):
                retry_context = self._prepare_persistence_retry_context(context, artifacts)
                if self._has_write_payload(retry_context):
                    decision.action = "delegate"
                    decision.worker = "story_state_manager"
                    decision.task = "Retry persistence for previously failed records"
                    decision.context = retry_context
                    decision.response = None
                    decision.quality_assessment = None
                    return decision

            if artifacts.get("records_updated"):
                # Partial persistence may still be usable; keep workflow autonomous.
                return decision

            return self._set_response(
                decision,
                "clarify",
                (
                    f"{summary or 'Story State persistence failed.'}\n"
                    "1) Should I retry persistence with stricter validation?\n"
                    "2) Or should I proceed without persisting this step?"
                ),
            )

        if worker == "resolution_subagent":
            mode = str(context.get("mode") or "").strip().upper()
            if status == "success" and mode in {"ANALYSE", "ANALYZE"}:
                return self._set_response(decision, "respond", self._build_resolution_analyse_response(artifacts))
            if status == "success" and mode == "IMPLEMENT":
                blocked_write = _ensure_dict(context.get("blocked_write"))
                proposed_context = _ensure_dict(blocked_write.get("proposed_context"))
                if proposed_context:
                    decision.action = "delegate"
                    decision.worker = "story_state_manager"
                    decision.task = "Re-issue previously blocked write after contradiction resolution"
                    decision.context = proposed_context
                    decision.response = None
                    decision.quality_assessment = None
                    return decision
                return self._set_response(
                    decision,
                    "respond",
                    "The contradiction was resolved, but I could not recover the blocked write context to re-issue automatically.",
                )
            if status == "need_input":
                follow_ups = result_data.get("follow_up_questions", [])
                return self._set_response(
                    decision,
                    "clarify",
                    self._format_follow_up(summary, follow_ups if isinstance(follow_ups, list) else []),
                )
            if status == "failed":
                return self._set_response(
                    decision,
                    "respond",
                    summary or "Contradiction resolution failed. I need guidance before continuing.",
                )

        return decision

    def _apply_quality_gate(
        self,
        decision: BrainDecision,
        state: OrchestratorState,
    ) -> tuple[BrainDecision, str | None, bool]:
        latest = _ensure_dict(state.get("latest_worker_result"))
        if not latest:
            return decision, None, False

        worker = str(latest.get("worker") or "")
        if worker in INFRASTRUCTURE_WORKERS:
            return decision, None, False

        result_data = _ensure_dict(latest.get("result"))
        status = str(result_data.get("status") or "")
        summary = str(result_data.get("summary") or "")
        artifacts = _ensure_dict(result_data.get("artifacts"))
        follow_up_questions = result_data.get("follow_up_questions", [])

        if status == "failed":
            return (
                self._set_response(
                    decision,
                    "respond",
                    summary or f"Worker {worker} failed. Please provide direction for the next step.",
                ),
                None,
                False,
            )

        if status == "need_input":
            override = self._bootstrap_planning_need_input_override(state)
            if override is not None:
                return override, None, False
            questions = follow_up_questions if isinstance(follow_up_questions, list) else []
            return self._set_response(decision, "clarify", self._format_follow_up(summary, questions)), None, False

        if status != "success":
            return (
                self._set_response(
                    decision,
                    "clarify",
                    (
                        f"Worker {worker} returned an unrecognized status '{status}'.\n"
                        "1) Should I retry this worker step?\n"
                        "2) Or should I change strategy?"
                    ),
                ),
                None,
                False,
            )

        quality = decision.quality_assessment
        verdict = "reject"
        reason = "Missing quality assessment on creative success."
        if not artifacts:
            verdict = "reject"
            reason = "Artifacts were empty."
        elif quality and quality.verdict in {"accept", "reject", "needs_clarification"}:
            verdict = quality.verdict
            reason = quality.reason or reason

        if verdict == "needs_clarification":
            if not _is_non_empty_text(decision.response):
                decision.response = (
                    f"I need clarification to proceed from {worker}'s output.\n"
                    "1) Which part should be revised first?\n"
                    "2) What quality bar should I enforce?"
                )
            _maybe_bootstrap_trace_quality_gate(
                latest=latest,
                worker=worker,
                artifacts=artifacts,
                result_status=status,
                quality_verdict=verdict,
                quality_reason=reason,
                mapper_result=None,
            )
            return self._set_response(decision, "clarify", str(decision.response)), verdict, False

        if verdict == "reject":
            rejection_count = int(state.get("rejection_count", 0))
            if rejection_count >= self.config.max_rejection_budget:
                _maybe_bootstrap_trace_quality_gate(
                    latest=latest,
                    worker=worker,
                    artifacts=artifacts,
                    result_status=status,
                    quality_verdict=verdict,
                    quality_reason=reason,
                    mapper_result=None,
                )
                return (
                    self._set_response(
                        decision,
                        "clarify",
                        (
                            "I still cannot validate the latest worker output after multiple retries.\n"
                            "1) Should I retry this step one more time with stricter schema constraints?\n"
                            "2) Or should I pivot to a different step before returning here?"
                        ),
                    ),
                    verdict,
                    False,
                )

            prior_task = str(latest.get("task") or "").strip() or "Retry the prior task with corrected artifacts."
            retry_task = f"{prior_task} Retry requirement: {reason}"
            retry_context = _ensure_dict(latest.get("context"))
            retry_context["quality_rejection_reason"] = reason
            decision.action = "delegate"
            decision.worker = worker if worker in VALID_WORKERS else decision.worker
            decision.task = retry_task
            decision.context = retry_context
            decision.response = None
            _maybe_bootstrap_trace_quality_gate(
                latest=latest,
                worker=worker,
                artifacts=artifacts,
                result_status=status,
                quality_verdict=verdict,
                quality_reason=reason,
                mapper_result=None,
            )
            return decision, verdict, True

        # Accept path: persist automatically when records are present.
        mapper_result = self.persist_mapper.build_context(latest, _ensure_dict(decision.context))
        _maybe_bootstrap_trace_quality_gate(
            latest=latest,
            worker=worker,
            artifacts=artifacts,
            result_status=status,
            quality_verdict=verdict,
            quality_reason=reason,
            mapper_result=mapper_result,
        )
        if mapper_result.has_payload:
            decision.action = "delegate"
            decision.worker = "story_state_manager"
            decision.task = "Persist accepted records to story state"
            decision.context = mapper_result.context
            decision.response = None
            decision.quality_assessment = None
            return decision, verdict, False

        if decision.action == "delegate" and decision.worker == "story_state_manager":
            return (
                self._set_response(
                    decision,
                    "respond",
                    "No structured records were produced for persistence in this step. Tell me what you want next.",
                ),
                verdict,
                False,
            )

        return decision, verdict, False

    def _build_state_updates(
        self,
        decision: BrainDecision,
        state: OrchestratorState,
        rejection_retry: bool,
    ) -> Dict[str, Any]:
        updates: Dict[str, Any] = {
            "iteration_count": int(state.get("iteration_count", 0)) + 1,
        }

        if decision.action in {"respond", "clarify"}:
            updates["final_response"] = str(decision.response or "No response provided.")
            updates["active_worker"] = None
            updates["worker_request"] = None
            updates["rejection_count"] = 0
            return updates

        updates["final_response"] = None
        updates["active_worker"] = decision.worker
        updates["worker_request"] = {
            "task": decision.task,
            "context": _ensure_dict(decision.context),
            "reasoning": decision.reasoning,
        }
        updates["rejection_count"] = int(state.get("rejection_count", 0)) + 1 if rejection_retry else 0
        return updates

    def __call__(self, state: OrchestratorState, config: RunnableConfig | None = None) -> Dict[str, Any]:
        iteration_count = int(state.get("iteration_count", 0))
        if iteration_count >= self.config.max_brain_iterations:
            print(f"[DEBUG] Iteration limit hit at {iteration_count}", flush=True)
            return {
                "final_response": self.iteration_limit_response,
                "iteration_count": iteration_count + 1,
                "active_worker": None,
                "worker_request": None,
                "rejection_count": 0,
            }

        if self._is_mvp_mode(state):
            decision = self._mvp_decision(state)
            decision = self._sanitize_and_validate_decision(decision, state)
            return self._build_state_updates(decision, state, rejection_retry=False)

        decision = (
            self._bootstrap_kickoff_decision(state)
            or self._bootstrap_progression_decision(state)
            or self._invoke_decision_model(state)
        )
        decision = self._sanitize_and_validate_decision(decision, state)
        self._merge_bootstrap_worldbuilding_compass(decision, state)
        decision = self._apply_infrastructure_overrides(decision, state)
        decision, _, rejection_retry = self._apply_quality_gate(decision, state)
        decision = self._sanitize_and_validate_decision(decision, state)
        return self._build_state_updates(decision, state, rejection_retry)
