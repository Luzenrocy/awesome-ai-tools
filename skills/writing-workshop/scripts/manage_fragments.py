#!/usr/bin/env python3
"""Create, activate, list, and disable user-local writing-workshop fragments."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
FORBIDDEN_PHRASES = ("ignore previous", "system prompt", "core-workflow", "safety override")


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def path_for(root: Path, status: str, kind: str, fragment_id: str) -> Path:
    if status == "candidate":
        return root / "candidates" / f"{fragment_id}.json"
    if status == "active":
        return root / "prompt-fragments" / kind / f"{fragment_id}.json"
    return root / "history" / f"{fragment_id}-{timestamp().replace(':', '-')}.json"


def read_record(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read fragment {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"fragment {path} must contain a JSON object")
    return value


def write_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_text(value: str, label: str) -> None:
    lowered = value.lower()
    if any(phrase in lowered for phrase in FORBIDDEN_PHRASES):
        raise ValueError(f"{label} attempts to override a protected workflow or safety rule")


def add_candidate(args: argparse.Namespace) -> int:
    fragment_id = args.id or f"user.{args.kind}.{args.applies_to.replace('.', '-')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if not ID_RE.fullmatch(fragment_id):
        raise ValueError("--id must use lowercase letters, digits, dots, underscores, or hyphens")
    validate_text(args.change, "--change")
    validate_text(args.acceptance, "--acceptance")
    destination = path_for(args.local_root, "candidate", args.kind, fragment_id)
    if destination.exists():
        raise ValueError(f"candidate already exists: {destination}")
    record: dict[str, object] = {
        "id": fragment_id,
        "kind": args.kind,
        "applies_to": [args.applies_to],
        "version": 1,
        "status": "candidate",
        "source": "user-feedback",
        "source_document": args.source_document,
        "change": args.change,
        "acceptance_test": args.acceptance,
        "created_at": timestamp(),
        "supersedes": args.supersedes,
    }
    write_record(destination, record)
    print(destination)
    return 0


def activate(args: argparse.Namespace) -> int:
    candidates = list((args.local_root / "candidates").glob(f"{args.id}.json"))
    if len(candidates) != 1:
        raise ValueError(f"candidate not found: {args.id}")
    record = read_record(candidates[0])
    kind = record.get("kind")
    if kind not in {"role", "document"}:
        raise ValueError("candidate has invalid kind")
    record["status"] = "active"
    record["activated_at"] = timestamp()
    history = path_for(args.local_root, "history", str(kind), args.id)
    write_record(history, record)
    destination = path_for(args.local_root, "active", str(kind), args.id)
    if destination.exists():
        raise ValueError(f"active fragment already exists: {destination}")
    write_record(destination, record)
    candidates[0].unlink()
    print(destination)
    return 0


def disable(args: argparse.Namespace) -> int:
    matches = list((args.local_root / "prompt-fragments").glob(f"*/{args.id}.json"))
    if len(matches) != 1:
        raise ValueError(f"active fragment not found: {args.id}")
    record = read_record(matches[0])
    record["status"] = "disabled"
    record["disabled_at"] = timestamp()
    write_record(path_for(args.local_root, "history", str(record.get("kind", "role")), args.id), record)
    matches[0].unlink()
    print(args.id)
    return 0


def list_fragments(args: argparse.Namespace) -> int:
    for status, directory in (("candidate", args.local_root / "candidates"), ("active", args.local_root / "prompt-fragments")):
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            record = read_record(path)
            print(f"{status}\t{record.get('id', path.stem)}\t{record.get('kind', 'unknown')}\t{path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-root", required=True, type=Path, help="user-local writing-workshop directory")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add-candidate", help="persist a user suggestion as a candidate")
    add.add_argument("--id")
    add.add_argument("--kind", choices=("role", "document"), required=True)
    add.add_argument("--applies-to", required=True)
    add.add_argument("--change", required=True)
    add.add_argument("--acceptance", required=True)
    add.add_argument("--source-document", default=None)
    add.add_argument("--supersedes", default=None)
    add.set_defaults(handler=add_candidate)

    activate_parser = commands.add_parser("activate", help="promote a candidate to an active local fragment")
    activate_parser.add_argument("--id", required=True)
    activate_parser.set_defaults(handler=activate)

    disable_parser = commands.add_parser("disable", help="disable an active fragment and retain history")
    disable_parser.add_argument("--id", required=True)
    disable_parser.set_defaults(handler=disable)

    listing = commands.add_parser("list", help="list candidates and active fragments")
    listing.set_defaults(handler=list_fragments)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
