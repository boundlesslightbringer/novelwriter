"""Extract replay fixture records from an E2E JSONL trace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.e2e_stub_replay import DEFAULT_CANONICAL_TRACE, load_fixture_from_trace, write_fixture_or_raise


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract worker replay records from trace JSONL.")
    parser.add_argument(
        "--trace-file",
        type=Path,
        default=DEFAULT_CANONICAL_TRACE,
        help="Source JSONL trace file (default: src/e2e_full_stack_trace.jsonl)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tmp/stub_replay_fixture.json"),
        help="Output JSON replay fixture path",
    )
    parser.add_argument(
        "--exclude-worker",
        action="append",
        default=["writing_subagent"],
        help="Worker names to exclude from extracted records (repeatable)",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    trace_file: Path = args.trace_file
    if not trace_file.exists():
        print(f"error: trace file not found: {trace_file}", file=sys.stderr)
        return 2

    excluded = set(args.exclude_worker or [])
    fixture, stats = load_fixture_from_trace(trace_file, exclude_workers=excluded)
    write_fixture_or_raise(fixture, args.output)

    print(json.dumps(fixture.model_dump(), ensure_ascii=True, indent=2))
    print(
        (
            "[extractor] source_line_count={source_lines} matched_update_events={matched} "
            "extracted_before_filter={before} extracted_after_filter={after} invalid_json_lines={invalid} "
            "workers_seen={workers}"
        ).format(
            source_lines=fixture.meta.source_line_count,
            matched=fixture.meta.matched_update_events,
            before=stats["extracted_record_count_before_filter"],
            after=fixture.meta.extracted_record_count,
            invalid=stats["invalid_json_lines"],
            workers=",".join(fixture.meta.workers_seen),
        ),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
