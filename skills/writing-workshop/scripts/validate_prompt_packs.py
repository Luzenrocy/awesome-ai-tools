#!/usr/bin/env python3
"""Validate the lightweight built-in writing-workshop prompt-pack catalogues."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PACK_RE = re.compile(r"^  - id: ([a-z0-9][a-z0-9._-]+)$", re.MULTILINE)


def validate_catalogue(path: Path, required_fields: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing catalogue: {path}"]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("schema_version: 1\nkind: "):
        errors.append(f"{path}: missing schema_version or kind")
    matches = list(PACK_RE.finditer(text))
    if not matches:
        errors.append(f"{path}: no pack IDs found")
        return errors
    ids = [match.group(1) for match in matches]
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate pack ID")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start() : end]
        for field in required_fields:
            if f"    {field}:" not in block:
                errors.append(f"{path}: {match.group(1)} is missing {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "prompt-packs",
    )
    args = parser.parse_args()
    pack_dir = args.pack_dir.expanduser()
    errors = []
    registry = pack_dir / "registry.yaml"
    if not registry.is_file():
        errors.append(f"missing registry: {registry}")
    else:
        registry_text = registry.read_text(encoding="utf-8")
        for expected in ("documents: documents.yaml", "roles: roles.yaml"):
            if expected not in registry_text:
                errors.append(f"{registry}: missing {expected}")
    errors.extend(validate_catalogue(pack_dir / "documents.yaml", ("label", "family", "intake_fields", "required_sections", "writer_fragment", "review_delta", "check_delta")))
    errors.extend(validate_catalogue(pack_dir / "roles.yaml", ("label", "writer_fragment", "review_delta", "check_delta")))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {pack_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
