#!/usr/bin/env python3
"""Print a deterministic SHA-256 snapshot of a writing-workshop skill."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="skill-relative selected rule or prompt-pack file to snapshot; may be repeated",
    )
    parser.add_argument(
        "--all-support-files",
        action="store_true",
        help="snapshot every reference, prompt pack, and helper script (audit mode)",
    )
    args = parser.parse_args()
    root = args.skill_dir.expanduser().resolve()
    required = [root / "SKILL.md", root / "agents" / "openai.yaml"]
    support_files: list[Path] = []
    if args.all_support_files:
        for directory_name in ("references", "prompt-packs", "scripts"):
            directory = root / directory_name
            if directory.is_dir():
                support_files.extend(sorted(directory.rglob("*")))
    else:
        for relative in args.include:
            candidate = (root / relative).resolve()
            if root not in candidate.parents or not candidate.is_file():
                parser.error(f"--include must name an existing file under the skill directory: {relative}")
            support_files.append(candidate)
    files = [
        path
        for path in required + support_files
        if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts
    ]
    print("skill_snapshot:")
    print(f'  loaded_at: "{datetime.now(timezone.utc).isoformat()}"')
    print("  files:")
    for path in files:
        print(f'    - path: "{path}"')
        print(f'      sha256: "{digest(path)}"')
        print(f'      modified: "{datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
