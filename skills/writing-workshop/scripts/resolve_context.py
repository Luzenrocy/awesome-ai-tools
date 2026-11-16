#!/usr/bin/env python3
"""Build a least-privilege input packet for one writing-workshop role call."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pack_catalog import document_catalogue, role_catalogue, sha256


ROLES = ("writer", "reviewer", "checker")
FULL_CONTEXT_REASONS = ("user-request", "p0-p1-conflict", "cross-document-consistency", "safety-or-compliance")


def scalar(text: str, key: str) -> str | None:
    found = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    if not found:
        return None
    value = found.group(1).strip()
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, str) else value
        except json.JSONDecodeError:
            pass
    return value.strip("'")


def section_scalar(text: str, section: str, key: str) -> str | None:
    block = re.search(rf"^\s*{re.escape(section)}:\s*\n((?:^\s+.*\n?)*)", text, re.MULTILINE)
    return scalar(block.group(1), key) if block else None


def record(path: Path, reason: str) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256(path), "reason": reason}


def active_fragments(local_root: Path | None, document_pack: str, role_pack: str) -> list[dict[str, object]]:
    if not local_root:
        return []
    root = local_root.expanduser().resolve() / "prompt-fragments"
    selected: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.json")) if root.is_dir() else []:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        applies = item.get("applies_to", [])
        if item.get("status") != "active" or not isinstance(applies, list):
            continue
        if item.get("kind") == "document" and document_pack in applies or item.get("kind") == "role" and role_pack in applies:
            selected.append({"path": str(path), "sha256": sha256(path), "fragment": item})
    return selected


def role_artifact_paths(council: Path, role: str, round_number: int, iteration_number: int) -> list[tuple[Path, str]]:
    iteration = council / "rounds" / f"round-{round_number:02d}" / "iterations" / f"iteration-{iteration_number:02d}"
    common = [
        (council / "user-brief.md", "immutable original request"),
        (council / "requirements-ledger.yaml", "normalized user constraints"),
        (council / "adaptive-contract.yaml", "effective document contract"),
        (council / "intake-confirmation.yaml", "user-confirmed type, style, and roles"),
        (council / "rules-snapshot.yaml", "loaded-rule provenance"),
    ]
    if role == "writer":
        prior = council / "rounds" / f"round-{round_number:02d}" / "iterations" / f"iteration-{iteration_number - 1:02d}"
        return common + ([(prior / "draft.md", "previous draft"), (prior / "review.md", "findings to resolve"), (prior / "decision.md", "checker decision")] if iteration_number > 1 else [])
    if role == "reviewer":
        return common + [(iteration / "draft.md", "draft under review"), (iteration / "coverage.yaml", "requirement coverage evidence")]
    return common + [
        (iteration / "draft.md", "candidate final draft"),
        (iteration / "review.md", "review findings to adjudicate"),
        (iteration / "revision.md", "writer disposition of review findings"),
        (iteration / "coverage.yaml", "requirement coverage evidence"),
    ]


def selected_source_subset(path: Path, source_ids: list[str]) -> list[str]:
    """Return only requested Markdown-table entries, never the whole index by default."""

    if not source_ids:
        return []
    rows = path.read_text(encoding="utf-8").splitlines()
    wanted = tuple(f"| {source_id} " for source_id in source_ids)
    return [row for row in rows if row.startswith(wanted)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--council-dir", required=True, type=Path)
    parser.add_argument("--role", required=True, choices=ROLES)
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--iteration", type=int, default=1)
    parser.add_argument("--source-id", action="append", default=[], help="source IDs required by this role; source index remains excluded otherwise")
    parser.add_argument("--local-root", type=Path, help="user-local fragment root")
    parser.add_argument("--full-context-reason", choices=FULL_CONTEXT_REASONS)
    args = parser.parse_args()
    council = args.council_dir.expanduser().resolve()
    manifest_path = council / "manifest.yaml"
    if not manifest_path.is_file():
        parser.error(f"missing manifest: {manifest_path}")
    manifest = manifest_path.read_text(encoding="utf-8")
    if scalar(manifest, "workflow_protocol_version") != "2":
        parser.error("precise role packets require workflow_protocol_version: 2")
    if scalar(manifest, "status") not in {"drafting", "reviewing", "revising", "approval"} or section_scalar(manifest, "intake", "confirmed") != "true":
        parser.error("a confirmed, active intake is required before resolving role context")

    document_pack = section_scalar(manifest, "prompt_packs", "document_pack")
    role_pack = section_scalar(manifest, "role_packs", args.role)
    if not document_pack or not role_pack:
        parser.error("manifest is missing selected prompt packs")
    document_catalogue_path, documents = document_catalogue()
    role_catalogue_path, roles = role_catalogue()
    if document_pack != "custom" and document_pack not in documents:
        parser.error(f"unknown document pack in manifest: {document_pack}")
    if role_pack != "custom" and role_pack not in roles:
        parser.error(f"unknown role pack in manifest: {role_pack}")

    iteration_dir = council / "rounds" / f"round-{args.round:02d}" / "iterations" / f"iteration-{args.iteration:02d}"
    if not iteration_dir.is_dir():
        parser.error(f"missing iteration directory: {iteration_dir}")
    artifacts = role_artifact_paths(council, args.role, args.round, args.iteration)
    if args.full_context_reason:
        for candidate in (council / "memory.md", council / "progress.md", council / "source-index.md", council / "reload-events.md"):
            artifacts.append((candidate, "full-context exception: " + args.full_context_reason))
    deduped: dict[Path, str] = {}
    for path, reason in artifacts:
        deduped[path] = reason
    missing = [str(path) for path in deduped if not path.is_file()]
    if missing:
        parser.error("required input artifacts are missing: " + ", ".join(missing))

    packet = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "role": args.role,
        "round": args.round,
        "iteration": args.iteration,
        "context_policy": "full-exception" if args.full_context_reason else "least-privilege",
        "full_context_reason": args.full_context_reason,
        "allowed_artifacts": [record(path, reason) for path, reason in deduped.items()],
        "selected_source_ids": args.source_id,
        "source_subset": selected_source_subset(council / "source-index.md", args.source_id),
        "selected_packs": {
            "document": {
                "id": document_pack,
                "catalogue_path": str(document_catalogue_path),
                "catalogue_sha256": sha256(document_catalogue_path),
                "payload": documents.get(document_pack, {}),
            },
            "role": {
                "id": role_pack,
                "catalogue_path": str(role_catalogue_path),
                "catalogue_sha256": sha256(role_catalogue_path),
                "payload": roles.get(role_pack, {}),
            },
        },
        "active_local_fragments": active_fragments(args.local_root, document_pack, role_pack),
        "excluded_by_default": ["source-index.md unless --source-id", "memory.md", "progress.md", "other role packets", "other iterations"],
        "output_path": str(iteration_dir / {"writer": "draft.md", "reviewer": "review.md", "checker": "decision.md"}[args.role]),
    }
    output_dir = iteration_dir / "role-inputs"
    output_dir.mkdir(exist_ok=True)
    packet_path = output_dir / f"{args.role}.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    snapshot = {
        "schema_version": 2,
        "role_packets": sorted(str(path) for path in output_dir.glob("*.json")),
        "last_updated": packet["created_at"],
        "packet_digest": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
    }
    (iteration_dir / "input-snapshot.yaml").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(packet_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
