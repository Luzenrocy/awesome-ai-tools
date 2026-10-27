#!/usr/bin/env python3
"""Check structural invariants of a writing-workshop artifact directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from council_schema import (
    ALLOWED_STATUS,
    ITERATION_RE,
    ITERATION_FILENAMES,
    MAX_ITERATIONS_PER_ROUND,
    MAX_ROUNDS,
    PATH_SOURCES,
    PROCESS_PATH_SOURCES,
    ROUND_GATES,
    ROUND_RE,
    ROUND_FILENAMES,
)


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, str) else value
        except json.JSONDecodeError:
            return value
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def nested_scalar(text: str, section: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(section)}:\s*\n((?:^\s+.*\n?)*)", text, re.MULTILINE)
    if not match:
        return None
    return scalar(match.group(1), key)


def require_files(directory: Path, filenames: tuple[str, ...], errors: list[str], label: str) -> None:
    """Append missing-file diagnostics for one typed artifact directory."""

    for name in filenames:
        if not (directory / name).is_file():
            errors.append(f"{label} is missing {name}")


def validate_coverage(directory: Path, hard_ids: list[str], errors: list[str], label: str) -> None:
    """Ensure every hard requirement is represented in a coverage file."""

    coverage_path = directory / "coverage.yaml"
    coverage = coverage_path.read_text(encoding="utf-8") if coverage_path.is_file() else ""
    for item_id in hard_ids:
        if item_id not in coverage:
            errors.append(f"{label}/coverage.yaml does not mention hard requirement {item_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("council_dir", type=Path)
    args = parser.parse_args()
    council = args.council_dir.expanduser()
    errors: list[str] = []

    if not council.is_dir():
        errors.append(f"directory does not exist: {council}")
    manifest_path = council / "manifest.yaml"
    manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else ""
    if not manifest_path.is_file():
        errors.append("missing manifest.yaml")

    limit = scalar(manifest, "round_limit")
    round_limit_value: int | None = None
    if limit is None:
        errors.append("manifest is missing round_limit")
    else:
        try:
            round_limit_value = int(limit)
            if not 1 <= round_limit_value <= MAX_ROUNDS:
                errors.append(f"round_limit must be between 1 and {MAX_ROUNDS}")
        except ValueError:
            errors.append("round_limit is not an integer")

    iteration_limit = scalar(manifest, "iterations_per_round")
    iteration_limit_value: int | None = None
    if iteration_limit is None:
        errors.append("manifest is missing iterations_per_round")
    else:
        try:
            iteration_limit_value = int(iteration_limit)
            if not 1 <= iteration_limit_value <= MAX_ITERATIONS_PER_ROUND:
                errors.append(
                    f"iterations_per_round must be between 1 and {MAX_ITERATIONS_PER_ROUND}"
                )
        except ValueError:
            errors.append("iterations_per_round is not an integer")

    status = scalar(manifest, "status")
    if status not in ALLOWED_STATUS:
        errors.append(f"unknown or missing status: {status!r}")

    current_round = scalar(manifest, "current_round")
    if current_round is None:
        errors.append("manifest is missing current_round")
    else:
        try:
            current_round_value = int(current_round)
            if current_round_value < 1 or (
                round_limit_value is not None and current_round_value > round_limit_value
            ):
                errors.append("current_round is outside round_limit")
        except ValueError:
            errors.append("current_round is not an integer")

    current_iteration = scalar(manifest, "current_iteration")
    if current_iteration is None:
        errors.append("manifest is missing current_iteration")
    else:
        try:
            current_iteration_value = int(current_iteration)
            if current_iteration_value < 0 or (
                iteration_limit_value is not None and current_iteration_value > iteration_limit_value
            ):
                errors.append("current_iteration is outside iterations_per_round")
        except ValueError:
            errors.append("current_iteration is not an integer")

    round_gate = scalar(manifest, "round_gate")
    if round_gate not in ROUND_GATES:
        errors.append(f"invalid or missing round_gate: {round_gate!r}")

    for name in (
        "intake.md",
        "user-brief.md",
        "requirements-ledger.yaml",
        "adaptive-contract.yaml",
        "source-index.md",
        "rules-snapshot.yaml",
        "reload-events.md",
        "progress.md",
        "memory.md",
    ):
        if not (council / name).is_file():
            errors.append(f"missing {name}")

    target_path = nested_scalar(manifest, "publication", "target_path")
    path_source = nested_scalar(manifest, "publication", "target_path_source")
    if not target_path:
        errors.append("publication.target_path is missing")
    if path_source not in PATH_SOURCES:
        errors.append(f"invalid or missing publication.target_path_source: {path_source!r}")
    process_base_path = nested_scalar(manifest, "artifacts", "process_base_path")
    process_path = nested_scalar(manifest, "artifacts", "process_path")
    process_path_source = nested_scalar(manifest, "artifacts", "process_path_source")
    if not process_base_path:
        errors.append("artifacts.process_base_path is missing")
    elif Path(process_base_path).expanduser().resolve() != council.parent.resolve():
        errors.append("artifacts.process_base_path does not match the process directory parent")
    if not process_path:
        errors.append("artifacts.process_path is missing")
    elif Path(process_path).expanduser().resolve() != council.resolve():
        errors.append("artifacts.process_path does not match the validated process directory")
    if process_path_source not in PROCESS_PATH_SOURCES:
        errors.append(f"invalid or missing artifacts.process_path_source: {process_path_source!r}")

    target_skill = scalar(manifest, "target_skill")
    if target_skill and target_skill != "none" and "contract_snapshot: null" in manifest:
        errors.append("target_skill is set but contract_snapshot is null")

    ledger_path = council / "requirements-ledger.yaml"
    ledger = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else ""
    ids = re.findall(r"^\s*-\s*id:\s*(U-[A-Za-z0-9._-]+)\s*$", ledger, re.MULTILINE)
    if len(ids) != len(set(ids)):
        errors.append("requirements-ledger.yaml contains duplicate U-* IDs")
    hard_ids: list[str] = []
    for block in re.split(r"^\s*-\s*id:\s*", ledger, flags=re.MULTILINE)[1:]:
        entry_id = re.match(r"(U-[A-Za-z0-9._-]+)", block)
        if entry_id and re.search(r"^\s*hardness:\s*hard\s*$", block, re.MULTILINE):
            hard_ids.append(entry_id.group(1))

    rounds_dir = council / "rounds"
    if rounds_dir.is_dir():
        for path in sorted(rounds_dir.iterdir()):
            if not path.is_dir():
                continue
            match = ROUND_RE.fullmatch(path.name)
            if not match:
                errors.append(f"invalid round directory name: {path.name}")
                continue
            number = int(match.group(1))
            if number < 1 or (round_limit_value is not None and number > round_limit_value):
                errors.append(f"round outside configured limit: {path.name}")
            require_files(path, ROUND_FILENAMES, errors, path.name)
            validate_coverage(path, hard_ids, errors, path.name)

            iterations_dir = path / "iterations"
            if not iterations_dir.is_dir():
                errors.append(f"{path.name} is missing iterations/")
            else:
                for iteration_path in sorted(iterations_dir.iterdir()):
                    if not iteration_path.is_dir():
                        continue
                    iteration_match = ITERATION_RE.fullmatch(iteration_path.name)
                    if not iteration_match:
                        errors.append(f"invalid iteration directory name: {path.name}/{iteration_path.name}")
                        continue
                    iteration_number = int(iteration_match.group(1))
                    if iteration_number < 1 or (
                        iteration_limit_value is not None and iteration_number > iteration_limit_value
                    ):
                        errors.append(f"iteration outside configured limit: {path.name}/{iteration_path.name}")
                    label = f"{path.name}/{iteration_path.name}"
                    require_files(iteration_path, ITERATION_FILENAMES, errors, label)
                    validate_coverage(iteration_path, hard_ids, errors, label)
    else:
        errors.append("missing rounds/")
    publish = council / "publish.md"
    if publish.exists() and status != "published":
        errors.append("publish.md exists but manifest status is not published")
    if status == "published" and not publish.is_file():
        errors.append("manifest status is published but publish.md is missing")

    summary = council / "completion-summary.md"
    if summary.exists() and status != "published":
        errors.append("completion-summary.md exists but manifest status is not published")
    if status == "published" and not summary.is_file():
        errors.append("manifest status is published but completion-summary.md is missing")

    unresolved = council / "unresolved.md"
    if status in {"blocked", "stopped_by_user"} and not unresolved.is_file():
        errors.append(f"manifest status is {status} but unresolved.md is missing")
    if unresolved.exists() and status not in {"blocked", "stopped_by_user"}:
        errors.append(f"unresolved.md exists but manifest status is {status}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {council}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
