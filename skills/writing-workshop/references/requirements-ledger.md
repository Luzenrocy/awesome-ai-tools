# User-intent and requirements ledger

The ledger is the source of truth for what the user asked for. It is separate from the document contract: the contract describes how to express the request; the ledger describes what must be preserved.

## Capture rules

- Save the original user request verbatim in `user-brief.md` with timestamp, locale, and source reference. Do not replace it with a summary.
- Normalize each goal, must-have, must-not, scope boundary, audience, tone, format, path, source fact, success criterion, and open question into a stable `U-*` entry.
- Treat later user changes as append-only amendments. An amendment may supersede an earlier entry, but never delete its history.
- Every role and iteration reads the same ledger version. Record
  `last_checked_round`, `last_checked_iteration`, `document_refs`, and a
  verification or acceptance check for each hard item.

## Entry schema

```yaml
version: 1
source_message: "user turn or file reference"
entries:
  - id: U-001
    type: goal | must | must-not | scope | non-scope | format | path | audience | tone | fact | success | open
    verbatim: "exact user wording or source quote"
    normalized: "precise interpretation"
    hardness: hard | soft
    priority: P0 | P1 | P2 | P3
    acceptance: "observable condition"
    verification: "inspection, test, demonstration, or structured user input"
    owner: "person or team, if known"
    status: open | satisfied | deferred-by-user | conflict | superseded
    document_refs: []
    last_checked_round: 0
    last_checked_iteration: 0
amendments:
  - id: A-001
    supersedes: U-001
    user_text: "later user instruction"
    effective_round: 2
```

## Coverage rules

Each iteration writes `coverage.yaml` under its `iteration-MM` directory,
mapping every `U-*` item to a draft location, status, evidence, and
verification. The round-level copy points to the latest iteration. A hard item
may be `satisfied` or `deferred-by-user`; an open or conflicting hard item
blocks approval. Any draft content without a ledger/source mapping must be
labeled as an assumption, derived consequence, or optional suggestion and
challenged for scope impact.
