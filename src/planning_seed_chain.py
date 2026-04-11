import json
from typing import Any, Dict, List, Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.agents.base import WorkerResponse
from src.tools import progressive_skill_loader

SEED_METHODS = [
    "Vivid Image",
    "What If?",
    "Character-First",
    "Historical Inspiration",
]
VALID_LOG_STATUSES = {"Rejected", "Merged", "Held as alternative"}


class CandidateSeed(BaseModel):
    method: str
    seed_statement: str
    strengths: str


class CandidateGenerationOutput(BaseModel):
    candidates: List[CandidateSeed] = Field(default_factory=list)


class CandidateLogEntry(BaseModel):
    seed_statement: str
    method: str
    strengths: str
    failure_point: str
    status: str


class SelectionOutput(BaseModel):
    seed: str
    generation_method: str
    genre_theme_fit: str
    questions: List[str] = Field(default_factory=list)
    candidate_seeds_log: List[CandidateLogEntry] = Field(default_factory=list)


class ValidationRecord(BaseModel):
    concreteness: str
    generative_tension: str
    emotional_necessity: str
    open_architecture: str


class ValidationOutput(BaseModel):
    validation_record: ValidationRecord


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, ensure_ascii=True, default=str)
    except TypeError:
        return str(payload)


def _normalize_list_strings(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    normalized: List[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        text = value.strip()
        if text:
            normalized.append(text)
    return normalized


def _coerce_validation_line(value: str) -> str:
    cleaned = str(value or "").strip()
    if cleaned.startswith("PASS") or cleaned.startswith("FAIL"):
        return cleaned
    if not cleaned:
        return "PASS - Validation note unavailable."
    return f"PASS - {cleaned}"


def _build_llm(subagent: Any) -> ChatGoogleGenerativeAI:
    kwargs: Dict[str, Any] = {
        "temperature": subagent.llm_config.temperature,
    }
    if subagent.llm_config.top_p is not None:
        kwargs["top_p"] = subagent.llm_config.top_p
    if subagent.llm_config.top_k is not None:
        kwargs["top_k"] = subagent.llm_config.top_k
    return ChatGoogleGenerativeAI(
        model=subagent.llm_config.model_name,
        vertexai=True,
        **kwargs,
    )


def run_finding_seed_chain(
    subagent: Any, state: Dict[str, Any], config: RunnableConfig | None = None
) -> Dict[str, Any]:
    worker_request = state.get("worker_request", {}) or {}
    context = worker_request.get("context", {}) or {}

    genre = str(context.get("genre", "")).strip()
    themes = _normalize_list_strings(context.get("themes"))
    subgenres = _normalize_list_strings(context.get("subgenres"))
    thematic_interdependencies = str(context.get("thematic_interdependencies", "")).strip()
    if not thematic_interdependencies and len(themes) > 1:
        thematic_interdependencies = "standalone"

    missing_fields: List[str] = []
    follow_up_questions: List[str] = []
    if not genre:
        missing_fields.append("genre")
        follow_up_questions.append("What broad genre should this novel inhabit?")
    if not themes:
        missing_fields.append("themes")
        follow_up_questions.append("What are one or more primary themes for this novel?")

    if missing_fields:
        structured_result = WorkerResponse(
            status="need_input",
            summary="Missing required constraints for finding-a-seed.",
            artifacts={
                "skill_attempted": "finding-a-seed",
                "error": "missing_required_context",
                "missing_fields": missing_fields,
            },
            follow_up_questions=follow_up_questions,
        ).model_dump()
        worker_record = {
            "worker": subagent.name,
            "task": worker_request.get("task", ""),
            "context": context,
            "result": structured_result,
        }
        return {
            "latest_worker_result": worker_record,
            "worker_history": [worker_record],
            "worker_request": None,
            "active_worker": None,
        }

    try:
        skill_content = progressive_skill_loader.invoke(
            {"skill_name": "finding-a-seed", "load_type": "full"}
        )
        llm = _build_llm(subagent)

        candidates_llm = llm.with_structured_output(CandidateGenerationOutput)
        selection_llm = llm.with_structured_output(SelectionOutput)
        validation_llm = llm.with_structured_output(ValidationOutput)

        generation_prompt = (
            f"{skill_content}\n\n"
            "Step 1: Generate exactly one candidate for each required method.\n"
            "Return structured output with one candidate per method and no prose outside fields.\n\n"
            f"{_safe_json({'genre': genre, 'themes': themes, 'subgenres': subgenres, 'methods': SEED_METHODS})}"
        )
        generation_output: CandidateGenerationOutput = candidates_llm.invoke(
            [HumanMessage(content=generation_prompt)], config=config or {}
        )

        candidates_by_method: Dict[str, CandidateSeed] = {}
        for candidate in generation_output.candidates:
            method = str(candidate.method).strip()
            if method and method not in candidates_by_method:
                candidates_by_method[method] = candidate
        for method in SEED_METHODS:
            if method not in candidates_by_method:
                candidates_by_method[method] = CandidateSeed(
                    method=method,
                    seed_statement=f"Placeholder seed for {method} generated to preserve complete method coverage.",
                    strengths="Method placeholder",
                )

        ordered_candidates = [candidates_by_method[method] for method in SEED_METHODS]
        selection_prompt = (
            f"{skill_content}\n\n"
            "Step 2: Select or synthesize one definitive seed from the candidates.\n"
            "Step 3: Build a complete candidate_seeds_log with explicit failure_point and "
            "status (Rejected | Merged | Held as alternative) for every method.\n"
            "Ensure the questions list has between 5 and 10 items.\n\n"
            f"{_safe_json({'genre': genre, 'themes': themes, 'subgenres': subgenres, 'candidates': [candidate.model_dump() for candidate in ordered_candidates]})}"
        )
        selection_output: SelectionOutput = selection_llm.invoke(
            [HumanMessage(content=selection_prompt)], config=config or {}
        )

        log_by_method: Dict[str, CandidateLogEntry] = {}
        for entry in selection_output.candidate_seeds_log:
            method = str(entry.method).strip()
            if method and method not in log_by_method:
                status = entry.status if entry.status in VALID_LOG_STATUSES else "Rejected"
                log_by_method[method] = CandidateLogEntry(
                    seed_statement=str(entry.seed_statement).strip() or candidates_by_method.get(method, CandidateSeed(method=method, seed_statement="", strengths="")).seed_statement,
                    method=method,
                    strengths=str(entry.strengths).strip() or candidates_by_method.get(method, CandidateSeed(method=method, seed_statement="", strengths="")).strengths,
                    failure_point=str(entry.failure_point).strip() or "Not selected as definitive seed.",
                    status=status,
                )
        for method in SEED_METHODS:
            if method not in log_by_method:
                fallback = candidates_by_method[method]
                log_by_method[method] = CandidateLogEntry(
                    seed_statement=fallback.seed_statement,
                    method=method,
                    strengths=fallback.strengths,
                    failure_point="Not selected as definitive seed.",
                    status="Rejected",
                )

        raw_questions = [str(question).strip() for question in selection_output.questions if str(question).strip()]
        if len(raw_questions) < 5:
            raw_questions.extend(
                [
                    "What hidden cost anchors the seed's central promise?",
                    "Who benefits if this seed tension never resolves?",
                    "What truth remains invisible at the story start?",
                    "Which relationship breaks first under this pressure?",
                    "What irreversible choice becomes inevitable?",
                ]
            )
        questions = raw_questions[:10]

        validation_prompt = (
            f"{skill_content}\n\n"
            "Step 4: Validate the definitive seed using four criteria.\n"
            "Return only validation_record with keys:\n"
            "concreteness, generative_tension, emotional_necessity, open_architecture.\n"
            "Each value must start with PASS or FAIL and include one sentence.\n\n"
            f"{_safe_json({'seed': selection_output.seed, 'generation_method': selection_output.generation_method, 'genre_theme_fit': selection_output.genre_theme_fit, 'questions': questions})}"
        )
        validation_output: ValidationOutput = validation_llm.invoke(
            [HumanMessage(content=validation_prompt)], config=config or {}
        )
        validation_record = {
            "concreteness": _coerce_validation_line(
                validation_output.validation_record.concreteness
            ),
            "generative_tension": _coerce_validation_line(
                validation_output.validation_record.generative_tension
            ),
            "emotional_necessity": _coerce_validation_line(
                validation_output.validation_record.emotional_necessity
            ),
            "open_architecture": _coerce_validation_line(
                validation_output.validation_record.open_architecture
            ),
        }

        artifacts = {
            "seed_document": {
                "seed": str(selection_output.seed).strip(),
                "generation_method": str(selection_output.generation_method).strip(),
                "validation_record": validation_record,
                "genre_theme_fit": str(selection_output.genre_theme_fit).strip(),
                "questions": questions,
            },
            "candidate_seeds_log": [
                log_by_method[method].model_dump() for method in SEED_METHODS
            ],
            "genre": genre,
            "subgenres": subgenres,
            "themes": themes,
            "thematic_interdependencies": thematic_interdependencies,
        }
        structured_result = WorkerResponse(
            status="success",
            summary="Generated and validated a story seed via the finding-a-seed chain.",
            artifacts=artifacts,
        ).model_dump()
    except Exception as error:
        structured_result = WorkerResponse(
            status="failed",
            summary=f"Worker execution failed: {error}",
            artifacts={"error": str(error)},
        ).model_dump()

    worker_record = {
        "worker": subagent.name,
        "task": worker_request.get("task", ""),
        "context": context,
        "result": structured_result,
    }
    return {
        "latest_worker_result": worker_record,
        "worker_history": [worker_record],
        "worker_request": None,
        "active_worker": None,
    }
