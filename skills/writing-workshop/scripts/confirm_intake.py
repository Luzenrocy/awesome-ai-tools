#!/usr/bin/env python3
"""Persist a user-selected intake and create the first writable iteration.

This is deliberately separate from routing: an agent may recommend choices, but
only this command changes a run from ``awaiting_intake_confirmation`` to
``drafting``.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from init_council import write_iteration_artifacts, yaml_quote
from pack_catalog import document_catalogue, role_catalogue


SOURCES = (
    "codex-structured-question",
    "claude-ask-user-question",
    "cli-resume",
    "explicit-user-message",
)


def replace_scalar(text: str, key: str, value: str, indent: str = "") -> str:
    pattern = rf"^{re.escape(indent)}{re.escape(key)}:\s*.*$"
    replacement = f"{indent}{key}: {yaml_quote(value)}"
    return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)


def replace_bool(text: str, key: str, value: bool, indent: str = "") -> str:
    return re.sub(
        rf"^{re.escape(indent)}{re.escape(key)}:\s*.*$",
        f"{indent}{key}: {str(value).lower()}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def replace_integer(text: str, key: str, value: int) -> str:
    return re.sub(
        rf"^{re.escape(key)}:\s*.*$", f"{key}: {value}", text, count=1, flags=re.MULTILINE
    )


def selected_combination(council: Path, combination_id: str) -> dict[str, str]:
    pending = council / "pending-user-input.json"
    if not pending.is_file():
        raise ValueError("missing pending-user-input.json; route the intake first")
    contents = json.loads(pending.read_text(encoding="utf-8"))
    for option in contents.get("role_combination_candidates", []):
        if option.get("id") == combination_id and isinstance(option.get("roles"), dict):
            return {key: str(option["roles"][key]) for key in ("writer", "reviewer", "checker")}
    raise ValueError(f"unknown role combination: {combination_id}")


def require_known(value: str, known: dict[str, dict[str, str]], label: str) -> None:
    if value != "custom" and value not in known:
        raise ValueError(f"{label} is not a built-in pack or custom: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--council-dir", required=True, type=Path)
    parser.add_argument("--document-pack", required=True)
    parser.add_argument("--style-or-channel", required=True)
    parser.add_argument("--role-combination-id")
    parser.add_argument("--writer-role")
    parser.add_argument("--reviewer-role")
    parser.add_argument("--checker-role")
    parser.add_argument("--source", required=True, choices=SOURCES)
    args = parser.parse_args()
    council = args.council_dir.expanduser().resolve()
    manifest_path = council / "manifest.yaml"
    if not manifest_path.is_file():
        parser.error(f"missing manifest: {manifest_path}")
    manifest = manifest_path.read_text(encoding="utf-8")
    if re.search(r"^status: (?!awaiting_intake_confirmation$)", manifest, re.MULTILINE):
        parser.error("intake can only be confirmed from awaiting_intake_confirmation")

    if args.role_combination_id:
        if any((args.writer_role, args.reviewer_role, args.checker_role)):
            parser.error("use --role-combination-id or all three explicit role arguments, not both")
        try:
            roles = selected_combination(council, args.role_combination_id)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
    else:
        if not all((args.writer_role, args.reviewer_role, args.checker_role)):
            parser.error("provide --role-combination-id or all writer/reviewer/checker roles")
        roles = {"writer": args.writer_role, "reviewer": args.reviewer_role, "checker": args.checker_role}

    _, documents = document_catalogue()
    _, role_packs = role_catalogue()
    try:
        require_known(args.document_pack, documents, "document pack")
        for role, pack in roles.items():
            require_known(pack, role_packs, f"{role} role")
    except ValueError as exc:
        parser.error(str(exc))

    round_dir = council / "rounds" / "round-01"
    iteration_dir = round_dir / "iterations" / "iteration-01"
    if round_dir.exists():
        parser.error("rounds already exist; refusing to overwrite the process record")

    manifest = replace_scalar(manifest, "status", "drafting")
    manifest = replace_integer(manifest, "current_iteration", 1)
    manifest = replace_bool(manifest, "confirmed", True, "  ")
    manifest = replace_scalar(manifest, "style_or_channel", args.style_or_channel, "  ")
    manifest = replace_scalar(manifest, "document_pack", args.document_pack, "  ")
    for role, value in roles.items():
        manifest = replace_scalar(manifest, role, value, "    ")
    manifest = replace_scalar(manifest, "writer", roles["writer"], "  ")
    manifest = replace_scalar(manifest, "reviewer", roles["reviewer"], "  ")
    manifest = replace_scalar(manifest, "approver", roles["checker"], "  ")
    manifest_path.write_text(manifest, encoding="utf-8")

    answered_at = datetime.now(timezone.utc).isoformat()
    confirmation = "\n".join(
        [
            "intake_confirmation:",
            "  confirmed: true",
            f"  document_pack: {yaml_quote(args.document_pack)}",
            f"  style_or_channel: {yaml_quote(args.style_or_channel)}",
            "  roles:",
            f"    writer: {yaml_quote(roles['writer'])}",
            f"    reviewer: {yaml_quote(roles['reviewer'])}",
            f"    checker: {yaml_quote(roles['checker'])}",
            f"  user_confirmation_source: {yaml_quote(args.source)}",
            f"  answered_at: {yaml_quote(answered_at)}",
            "",
        ]
    )
    (council / "intake-confirmation.yaml").write_text(confirmation, encoding="utf-8")

    pending = council / "pending-user-input.json"
    if pending.is_file():
        decision = council / "intake-decision.json"
        contents = json.loads(pending.read_text(encoding="utf-8"))
        contents.update({"status": "confirmed", "answered_at": answered_at, "confirmation_source": args.source})
        decision.write_text(json.dumps(contents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pending.unlink()

    iteration_dir.mkdir(parents=True)
    for output_dir in (round_dir, iteration_dir):
        write_iteration_artifacts(output_dir, round_number=1, iteration_number=1)
    (round_dir / "round-summary.md").write_text("# Remaining findings summary: round 01\n\n[TBD]\n", encoding="utf-8")
    (round_dir / "user-decision.md").write_text("# User continuation decision: round 01\n\n[TBD]\n", encoding="utf-8")
    print(iteration_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
