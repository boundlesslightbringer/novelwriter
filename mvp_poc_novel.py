"""Terminal-first MVP proof-of-concept runner for Novelwriter.

Requirements:
- Run from repository root: python mvp_poc_novel.py
- Configure .env / environment for MongoDB and Vertex Gemini access.
- Ensure project dependencies are installed.

Optional character direction:
- Pass --character-concept "..." for a short natural-language brief, or
- Pass --character-concept-json '{...}' for a structured dict, or
- Press Enter at the prompt to let the MVP brain auto-fill from genre/themes + planning seed.

Progress output:
- By default this script uses graph.stream (like main.py) so you can see brain delegations and worker completions.
- Pass --quiet to use graph.invoke with no incremental prints.
"""

import argparse
import json
import sys
import uuid
import warnings
from typing import Any

from langchain_core.messages import HumanMessage

warnings.filterwarnings("ignore", message=".*quota project.*")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bare-bones Novelwriter MVP flow in terminal.",
    )
    parser.add_argument("--genre", type=str, default="", help="Novel genre.")
    parser.add_argument(
        "--themes",
        type=str,
        default="",
        help="Comma-separated themes (for example: loyalty,betrayal,ambition).",
    )
    parser.add_argument("--thread-id", type=str, default="", help="Optional graph thread ID.")
    parser.add_argument(
        "--max-major-characters",
        type=int,
        default=5,
        help="Maximum number of major characters the MVP flow should request.",
    )
    parser.add_argument(
        "--character-concept",
        type=str,
        default="",
        help="Optional free-text direction for character creation (merged into MVP character_concept).",
    )
    parser.add_argument(
        "--character-concept-json",
        type=str,
        default="",
        help='Optional JSON object for character_concept (overrides --character-concept text if both are set).',
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable live graph progress prints (uses graph.invoke instead of graph.stream).",
    )
    return parser.parse_args()


def _prompt_if_blank(label: str, current_value: str) -> str:
    if current_value.strip():
        return current_value.strip()
    return input(f"{label}: ").strip()


def _parse_themes(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _parse_character_concept_inputs(args: argparse.Namespace) -> Any | None:
    raw_json = str(args.character_concept_json or "").strip()
    raw_text = str(args.character_concept or "").strip()
    if raw_json and raw_text:
        raise SystemExit("Use only one of --character-concept-json or --character-concept, not both.")
    if raw_json:
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as error:
            raise SystemExit(f"Invalid JSON for --character-concept-json: {error}") from error
        if not isinstance(parsed, dict):
            raise SystemExit("--character-concept-json must be a JSON object (dictionary).")
        return parsed
    if raw_text:
        return raw_text

    prompted = input(
        "Character concept (optional; press Enter to auto-fill from genre/themes/planning seed): "
    ).strip()
    return prompted or None


def _render_worker_history(worker_history: Any) -> str:
    if not isinstance(worker_history, list) or not worker_history:
        return "No worker history recorded."

    lines: list[str] = []
    for idx, entry in enumerate(worker_history, start=1):
        row = entry if isinstance(entry, dict) else {}
        result = row.get("result", {}) if isinstance(row.get("result"), dict) else {}
        lines.append(
            f"{idx}. {row.get('worker', 'unknown')} -> {result.get('status', 'unknown')}: "
            f"{result.get('summary', '')}"
        )
    return "\n".join(lines)


def _print_graph_progress(orchestrator: Any, event_type: str, event_data: Any) -> None:
    """Mirror main.py-style visibility: show brain delegations and worker completions."""
    if event_type == "updates":
        for node_name, state_update in event_data.items():
            if node_name == "brain":
                worker = state_update.get("active_worker")
                if worker:
                    print(f"\n[Brain] Delegating to: {worker}", flush=True)
                    task = (state_update.get("worker_request") or {}).get("task", "")
                    if task:
                        print(f"[Brain] Task: {task}", flush=True)
            elif node_name in orchestrator.workers:
                print(f"\n[{node_name}] Completed.", flush=True)
                result = (state_update.get("latest_worker_result") or {}).get("result", {})
                if isinstance(result, dict):
                    print(f"[{node_name}] Status: {result.get('status')}", flush=True)
                    summary = str(result.get("summary") or "").strip()
                    if summary:
                        print(f"[{node_name}] Summary: {summary}", flush=True)
    elif event_type == "messages":
        chunk, metadata = event_data
        if metadata.get("langgraph_node") == "respond" and getattr(chunk, "content", None):
            content = chunk.content
            if isinstance(content, str) and content:
                print(content, end="", flush=True)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, str) and part:
                        print(part, end="", flush=True)
                    elif isinstance(part, dict) and part.get("type") == "text":
                        print(part.get("text", ""), end="", flush=True)


def main() -> None:
    try:
        from src.config import NovelWriterConfig
        from src.orchestrator import GRRMOrchestrator
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Could not import project modules. Run this script from repo root after installing dependencies."
        ) from error

    args = _parse_args()
    genre = _prompt_if_blank("Genre", args.genre)
    themes_raw = _prompt_if_blank("Themes (comma-separated)", args.themes)
    themes = _parse_themes(themes_raw)

    if not genre or not themes:
        raise SystemExit("Both genre and at least one theme are required.")

    character_concept = _parse_character_concept_inputs(args)

    config = NovelWriterConfig()
    orchestrator = GRRMOrchestrator(
        config,
        worker_impls=GRRMOrchestrator.real_worker_impls(),
    )
    thread_id = args.thread_id.strip() or str(uuid.uuid4())
    run_config = {"configurable": {"thread_id": thread_id}}

    user_prompt = f"genre: {genre}\nthemes: {', '.join(themes)}"
    turn_input = {
        "messages": [HumanMessage(content=user_prompt)],
        "iteration_count": 0,
        "rejection_count": 0,
        "final_response": None,
        "active_worker": None,
        "worker_request": None,
        "latest_worker_result": None,
        "worker_history": [],
        "mvp_mode": True,
        "mvp_requirements": {
            "genre": genre,
            "themes": themes,
            "chapter_context": config.mvp_default_chapter_context,
            "max_major_characters": min(max(args.max_major_characters, 1), config.mvp_max_major_characters),
            "target_scene_pages": config.mvp_target_scene_pages,
            **({"character_concept": character_concept} if character_concept is not None else {}),
        },
    }

    print("\nRunning MVP flow...")
    if args.quiet:
        final_state = orchestrator.graph.invoke(turn_input, config=run_config)
    else:
        print("(Live updates enabled; use --quiet for silent graph.invoke)\n", flush=True)
        for event_type, event_data in orchestrator.graph.stream(
            turn_input,
            config=run_config,
            stream_mode=["messages", "updates"],
        ):
            _print_graph_progress(orchestrator, event_type, event_data)
        print(flush=True)
        final_state = dict(orchestrator.graph.get_state(run_config).values)

    final_response = str(final_state.get("final_response") or "").strip()
    if not final_response:
        final_response = "No scene output returned."

    print("\n=== Scene Output ===\n")
    print(final_response)
    print("\n=== Worker History ===\n")
    print(_render_worker_history(final_state.get("worker_history")))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
