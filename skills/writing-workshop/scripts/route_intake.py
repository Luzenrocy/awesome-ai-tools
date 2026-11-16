#!/usr/bin/env python3
"""Recommend document and role packs, then create a portable intake question file."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pack_catalog import digest_text, recommend_documents, recommend_role_combinations


def brief_from_args(args: argparse.Namespace) -> str:
    if args.brief:
        return args.brief
    if args.brief_file:
        return args.brief_file.read_text(encoding="utf-8")
    brief_path = args.council_dir / "user-brief.md"
    return brief_path.read_text(encoding="utf-8") if brief_path.is_file() else ""


def persist_verbatim_brief(council: Path, brief: str, supplied: bool) -> None:
    """Replace only the initializer placeholder; amendments remain append-only."""

    if not supplied:
        return
    target = council / "user-brief.md"
    existing = target.read_text(encoding="utf-8") if target.is_file() else ""
    if "Paste the user's original request here verbatim." in existing or not existing.strip():
        target.write_text("# User brief\n\n" + brief.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--council-dir", required=True, type=Path)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--brief")
    source.add_argument("--brief-file", type=Path)
    args = parser.parse_args()
    council = args.council_dir.expanduser().resolve()
    if not council.is_dir():
        parser.error(f"council directory does not exist: {council}")
    manifest_path = council / "manifest.yaml"
    manifest = manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else ""
    if not re.search(r"^status: awaiting_intake_confirmation\s*$", manifest, re.MULTILINE):
        parser.error("intake can only be routed while manifest status is awaiting_intake_confirmation")
    brief = brief_from_args(args).strip()
    if not brief:
        parser.error("a non-empty brief is required via --brief, --brief-file, or user-brief.md")
    persist_verbatim_brief(council, brief, bool(args.brief or args.brief_file))

    document_candidates = recommend_documents(brief)
    role_candidates = recommend_role_combinations(str(document_candidates[0]["id"]))
    output = {
        "schema_version": 1,
        "status": "awaiting_intake_confirmation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "brief_sha256": digest_text(brief),
        "document_candidates": document_candidates,
        "role_combination_candidates": role_candidates,
        "questions": [
            {
                "id": "document_pack",
                "question": "请选择文档类型/文档包，或选择 custom。",
                "options": [candidate["id"] for candidate in document_candidates],
            },
            {
                "id": "role_combination",
                "question": "请选择 writer、reviewer、checker 的角色组合，或自行指定。",
                "options": [candidate["id"] for candidate in role_candidates],
            },
            {
                "id": "style_or_channel",
                "question": "请确认输出渠道或风格。",
                "options": [],
            },
        ],
    }
    target = council / "pending-user-input.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
