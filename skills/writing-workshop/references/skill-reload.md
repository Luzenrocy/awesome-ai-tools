# Rule reload and freshness

Skill instructions are mutable local configuration. A run must use the files that exist when each step begins.

## Snapshot

At invocation start, enumerate `SKILL.md`, `agents/openai.yaml`, every
reference explicitly loaded for the request, and every helper script used for
the run. Store:

```yaml
skill_snapshot:
  loaded_at: "ISO-8601 timestamp"
  files:
    - path: "/absolute/path"
      sha256: "..."
      modified: "ISO-8601 timestamp"
```

`scripts/fingerprint_skill.py` can produce the file list and hashes for the
skill's references and scripts. Do not hash or load unrelated secrets or
project content.

## Before each role, iteration, and round

1. Re-read the current files from disk; do not reuse cached text.
2. Compare hashes and modification times with the previous snapshot.
3. If any referenced rule changed, append a dated entry to `reload-events.md`, update the snapshot, and recompute the adaptive contract and gates.
4. Mark any draft based on the old snapshot as `stale`; rerun every affected review and approval step without resetting the round or iteration count.
5. If a change conflicts with an explicit user requirement, the user requirement remains authoritative; record the conflict and invoke the host's native structured question component when it blocks a responsible decision.

The reload event records changed paths, old/new hashes, affected contract fields, and the next required action. A reload never silently changes the final target path, scope, or user ledger.
