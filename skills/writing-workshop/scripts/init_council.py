#!/usr/bin/env python3
"""Create a traceable, standalone writing-workshop workspace."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from council_schema import (
    DEFAULT_ITERATIONS_PER_ROUND,
    DEFAULT_PROCESS_DIRECTORY,
    MAX_ITERATIONS_PER_ROUND,
    MAX_ROUNDS,
)


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
ITERATION_FILES = (
    ("draft.md", "Draft"),
    ("review.md", "Review findings"),
    ("revision.md", "Revision map"),
    ("decision.md", "Checker decision"),
)


def yaml_quote(value: str) -> str:
    # JSON string syntax is a valid YAML scalar and also handles newlines and
    # control characters that a hand-rolled quote would leave invalid.
    return json.dumps(value, ensure_ascii=False)


def write_iteration_artifacts(output_dir: Path, round_number: int, iteration_number: int) -> None:
    """Create one iteration's structural files without duplicating templates."""

    (output_dir / "coverage.yaml").write_text("ledger_version: 1\nentries: []\n", encoding="utf-8")
    (output_dir / "input-snapshot.yaml").write_text(
        'rules_snapshot: "[TBD]"\nledger_version: 1\ncontract_snapshot: "[TBD]"\n',
        encoding="utf-8",
    )
    for name, heading in ITERATION_FILES:
        (output_dir / name).write_text(
            f"# {heading}: round {round_number:02d}, iteration {iteration_number:02d}\n\n[TBD]\n",
            encoding="utf-8",
        )


def resolve_target_directory(target: Path) -> Path:
    """Resolve the user-facing directory that owns the target.

    A target that already exists as a file, or that has a filename suffix, is
    treated as a document and uses its parent directory.  A target that exists
    as a directory, or has no suffix yet, is treated as the document directory
    itself.  This keeps the process files beside a file target while allowing a
    directory target such as ``ai-docs/test2`` to be used directly.
    """

    if target.exists():
        return target if target.is_dir() else target.parent
    return target.parent if target.suffix else target


def resolve_process_path(target: Path) -> Path:
    """Place process artifacts in a dedicated subdirectory under the target directory."""

    return resolve_target_directory(target) / DEFAULT_PROCESS_DIRECTORY


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="explicit artifact root; otherwise use the target file's parent directory")
    parser.add_argument("--council-path", help="exact process-artifact directory; overrides --root")
    parser.add_argument("--document-slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--type", dest="doc_type", default="custom")
    parser.add_argument("--contract-mode", choices=("known", "custom", "hybrid"), default="custom")
    parser.add_argument("--family", default="custom")
    parser.add_argument("--purpose", default="[TBD]")
    parser.add_argument("--audience", default="[TBD]")
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--target-format", default="markdown")
    parser.add_argument("--target-path-source", choices=("user", "external_contract", "default"), default="user")
    parser.add_argument("--overwrite-policy", choices=("refuse", "replace"), default="refuse")
    parser.add_argument("--target-skill", default="none")
    parser.add_argument("--author", default="pending")
    parser.add_argument("--locale", default="zh-CN")
    parser.add_argument(
        "--round-limit",
        type=int,
        default=MAX_ROUNDS,
        help=f"maximum number of user-approved rounds (default: {MAX_ROUNDS})",
    )
    parser.add_argument(
        "--iterations-per-round",
        "--iteration-limit",
        dest="iterations_per_round",
        type=int,
        default=DEFAULT_ITERATIONS_PER_ROUND,
        help=(
            "maximum writer/reviewer/checker iterations in each round "
            f"(current default: {DEFAULT_ITERATIONS_PER_ROUND})"
        ),
    )
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.document_slug):
        parser.error("--document-slug must be a lowercase slug (letters, digits, ., _, -)")
    if not 1 <= args.round_limit <= MAX_ROUNDS:
        parser.error(f"--round-limit must be between 1 and {MAX_ROUNDS}")
    if not 1 <= args.iterations_per_round <= MAX_ITERATIONS_PER_ROUND:
        parser.error(f"--iterations-per-round must be between 1 and {MAX_ITERATIONS_PER_ROUND}")

    target = Path(args.target_path).expanduser()
    if args.council_path:
        council = Path(args.council_path).expanduser()
        process_base_path = council.parent
        process_path_source = "user"
        process_path_resolution = "explicit"
    elif args.root:
        process_base_path = Path(args.root).expanduser() / args.document_slug
        council = process_base_path / DEFAULT_PROCESS_DIRECTORY
        process_path_source = "user"
        process_path_resolution = "explicit-root"
    else:
        council = resolve_process_path(target)
        process_base_path = council.parent
        process_path_source = "default"
        process_path_resolution = "derived-from-target/council"
    council = council.resolve()
    process_base_path = process_base_path.resolve()
    council.mkdir(parents=True, exist_ok=True)
    round_dir = council / "rounds" / "round-01"
    round_dir.mkdir(parents=True, exist_ok=True)
    iteration_dir = round_dir / "iterations" / "iteration-01"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    integration_mode = "none" if args.target_skill == "none" else "optional-overlay"
    manifest = "\n".join(
        [
            f"document_id: {yaml_quote(args.document_slug)}",
            f"title: {yaml_quote(args.title)}",
            f"document_type: {yaml_quote(args.doc_type)}",
            f"locale: {yaml_quote(args.locale)}",
            f"owner: {yaml_quote(args.author)}",
            f"created: {today}",
            f"updated: {today}",
            "version: \"0.1\"",
            "status: drafting",
            f"round_limit: {args.round_limit}",
            f"iterations_per_round: {args.iterations_per_round}",
            "current_round: 1",
            "current_iteration: 0",
            "round_gate: none",
            "roles:",
            "  writer: pending-profile",
            "  reviewer: pending-profile",
            "  approver: pending-profile",
            "document_contract:",
            f"  mode: {args.contract_mode}",
            f"  family: {yaml_quote(args.family)}",
            f"  label: {yaml_quote(args.doc_type)}",
            f"  purpose: {yaml_quote(args.purpose)}",
            f"  audience: [{yaml_quote(args.audience)}]",
            "  required_sections: []",
            "  optional_sections: []",
            "  forbidden_sections: []",
            "  quality_checks: []",
            "publication:",
            f"  target_path: {yaml_quote(args.target_path)}",
            f"  target_path_source: {args.target_path_source}",
            f"  target_format: {yaml_quote(args.target_format)}",
            f"  final_filename: {yaml_quote(Path(args.target_path).name)}",
            f"  overwrite_policy: {args.overwrite_policy}",
            "artifacts:",
            f"  artifact_root: {yaml_quote(str(process_base_path))}",
            f"  process_base_path: {yaml_quote(str(process_base_path))}",
            f"  council_path: {yaml_quote(str(council))}",
            f"  process_path: {yaml_quote(str(council))}",
            f"  process_path_resolution: {yaml_quote(process_path_resolution)}",
            f"  process_path_source: {process_path_source}",
            f"integration_mode: {integration_mode}",
            f"target_skill: {yaml_quote(args.target_skill)}",
            "contract_snapshot: null",
            "skill_snapshot: null",
            "sources: []",
            "",
        ]
    )
    (council / "manifest.yaml").write_text(manifest, encoding="utf-8")
    (council / "intake.md").write_text(
        f"# Intake: {args.title}\n\n- Document type: `{args.doc_type}`\n- Contract mode: `{args.contract_mode}`\n- Family: `{args.family}`\n- Audience: `{args.audience}`\n- Purpose: {args.purpose}\n- Target path: `{args.target_path}`\n- Process path: `{council}` ({process_path_resolution})\n- Target format: `{args.target_format}`\n- Integration mode: `{integration_mode}`\n",
        encoding="utf-8",
    )
    (council / "user-brief.md").write_text(
        "# User brief\n\nPaste the user's original request here verbatim. Add dated amendments below it; do not replace the original text.\n",
        encoding="utf-8",
    )
    (council / "requirements-ledger.yaml").write_text(
        "version: 1\nsource_message: \"[TBD]\"\nentries: []\namendments: []\n",
        encoding="utf-8",
    )
    (council / "adaptive-contract.yaml").write_text(
        "document_contract:\n  mode: " + args.contract_mode + "\n  family: " + yaml_quote(args.family) + "\n  label: " + yaml_quote(args.doc_type) + "\n  purpose: " + yaml_quote(args.purpose) + "\n  audience: [" + yaml_quote(args.audience) + "]\n  required_sections: []\n  optional_sections: []\n  forbidden_sections: []\n  quality_checks: []\n",
        encoding="utf-8",
    )
    (council / "source-index.md").write_text(
        "# Source index\n\n| ID | Source | Version/date | Used for |\n| --- | --- | --- | --- |\n| S-001 | `[TBD]` | `[TBD]` | `[TBD]` |\n",
        encoding="utf-8",
    )
    (council / "rules-snapshot.yaml").write_text(
        "skill_snapshot:\n  loaded_at: \"[TBD]\"\n  files: []\n",
        encoding="utf-8",
    )
    (council / "reload-events.md").write_text("# Rule reload events\n\nNo reloads recorded.\n", encoding="utf-8")
    (council / "progress.md").write_text(
        "# Progress log\n\n"
        "Append one dated entry for each round, iteration, role completion, reload, user decision, and next action. "
        "Record the round and iteration counters; a new round requires an explicit user decision.\n",
        encoding="utf-8",
    )
    (council / "memory.md").write_text(
        "# Working memory\n\n"
        "Record only durable decisions, terminology, constraints, assumptions, unresolved items, and links to typed process records.\n",
        encoding="utf-8",
    )
    for output_dir in (round_dir, iteration_dir):
        write_iteration_artifacts(output_dir, round_number=1, iteration_number=1)
    (round_dir / "round-summary.md").write_text("# Remaining findings summary: round 01\n\n[TBD]\n", encoding="utf-8")
    (round_dir / "user-decision.md").write_text("# User continuation decision: round 01\n\n[TBD]\n", encoding="utf-8")
    print(council)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
