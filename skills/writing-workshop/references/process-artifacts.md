# Process artifact paths and document types

## Process path resolution

Publication and process artifacts are separate concerns, but a process path is
always derived deterministically from the user's requested target unless the
user explicitly supplies a process/artifact directory.

1. An existing file target uses its parent directory as the process base.
2. A path that has a filename suffix (for example, `ai-docs/xxxx.md`) is
   treated as a file target and uses `ai-docs/` as the process base.
3. An existing directory target uses that directory itself as the process base.
4. A path without a suffix (for example, `ai-docs/test2`) is treated as a
   directory target and uses `ai-docs/test2/` itself as the process base.

The process base is never used directly for process files. By default, place
all process files in its dedicated `council/` child: `ai-docs/xxxx.md` becomes
`ai-docs/council/`, and `ai-docs/test2` becomes `ai-docs/test2/council/`. The
resolved process directory is the single root for the manifest, intake, role
records, round records, publication record, and completion summary. An
explicit user-supplied process path always wins and is used exactly. Record
`publication.target_path`, `artifacts.process_base_path`,
`artifacts.process_path`, the resolution rule, and their sources in
`manifest.yaml`.

### Annotated process directory tree

The diagram is the canonical layout for a run. Braced filenames under a round
are the current/latest indexes; the complete history is kept under the
corresponding iteration directory.

```text
{process-path}/
├── manifest.yaml                    # state, counters, roles, target, and resolved paths
├── intake.md                         # human-readable initialization summary
├── user-brief.md                     # immutable request and dated amendments
├── requirements-ledger.yaml          # U-* requirements, constraints, and acceptance checks
├── adaptive-contract.yaml            # effective document type, structure, and quality checks
├── source-index.md                   # source inventory, versions, and usage purpose
├── rules-snapshot.yaml               # loaded skill files and hashes
├── reload-events.md                  # rule reloads and stale-record events
├── progress.md                       # append-only execution timeline
├── memory.md                         # durable decisions, terminology, and constraints
├── rounds/
│   └── round-01/                    # one user-approved batch
│       ├── iterations/
│       │   └── iteration-01/        # one writer → reviewer → checker cycle
│       │       ├── draft.md         # writer output
│       │       ├── review.md        # reviewer findings and evidence
│       │       ├── revision.md      # finding-to-change map
│       │       ├── decision.md      # checker approve/revise/blocked verdict
│       │       ├── coverage.yaml    # requirement-to-draft evidence map
│       │       └── input-snapshot.yaml # role input rule/contract snapshot
│       ├── {draft,review,revision,decision}.md # latest iteration indexes
│       ├── {coverage,input-snapshot}.yaml      # latest iteration indexes
│       ├── round-summary.md         # remaining findings at the round gate
│       └── user-decision.md         # explicit continue/stop decision
├── publish.md                       # publication evidence after approval
├── completion-summary.md             # final inventory and conclusion
└── unresolved.md                    # blockers, user stop, or round-limit findings only
```

## Round and iteration records

The manifest starts at `current_round: 1` and uses the current default
`iterations_per_round: 10`. An iteration is one writer/reviewer/checker cycle;
a round is the batch containing up to that many iterations. A `revise` decision
continues the current round while its iteration budget remains. The skill never
starts another round by itself. After the final iteration, if findings remain,
write the remaining-finding summary and ask the user whether to start the next
round. Record the answer before advancing or stopping. A `blocked` decision
stops immediately without asking this continuation question. `round_limit`
defaults to 10 as the existing hard upper bound for user-approved rounds.

## Required process document classes and file responsibilities

Keep process documents in clearly named classes so a reader can distinguish
evidence, state, decisions, and output. The following is a file-by-file
responsibility map; `round-NN` and `iteration-MM` are zero-padded numbers.

| Class | File | Purpose and boundary |
| --- | --- | --- |
| Run metadata | `manifest.yaml` | Machine-readable state, counters, role routing, publication target, process-base path, dedicated council path, and path provenance. It is the authoritative run index. |
| Run metadata | `intake.md` | Human-readable startup summary copied from initialization arguments; useful for quickly understanding the run without parsing YAML. |
| User intake | `user-brief.md` | Immutable verbatim user request plus dated amendments. Never replace the original with a summary. |
| Requirements | `requirements-ledger.yaml` | Normalized `U-*` requirements, must/must-not constraints, acceptance checks, open questions, and user decisions. |
| Contract | `adaptive-contract.yaml` | Effective document type, audience, purpose, structure, terminology, output format, and quality checks for this run. |
| Sources | `source-index.md` | Source inventory with version/date and the exact purpose for which each source is used. |
| Rule provenance | `rules-snapshot.yaml` | Loaded skill files, modification metadata, hashes, and the rule version used by the current records. |
| Rule provenance | `reload-events.md` | Append-only record of rule changes/reloads, affected drafts, and stale-record handling. |
| Progress | `progress.md` | Append-only timeline of round/iteration start and end, role completion, reloads, user decisions, and next action. It is not a review or verdict. |
| Memory | `memory.md` | Durable cross-iteration/cross-round decisions, terminology, constraints, assumptions, unresolved items, and links to typed records. It must not contain hidden reasoning. |
| Iteration draft | `rounds/round-NN/iterations/iteration-MM/draft.md` | Complete writer output for one iteration; the next iteration starts from this artifact or its approved successor. |
| Iteration review | `rounds/round-NN/iterations/iteration-MM/review.md` | Reviewer findings only. Every finding records ID, severity, location, evidence, impact, action, and acceptance check. |
| Iteration revision | `rounds/round-NN/iterations/iteration-MM/revision.md` | Finding-by-finding modification map and evidence, including accepted-risk or rejected-finding reasons. It never replaces `review.md`. |
| Iteration decision | `rounds/round-NN/iterations/iteration-MM/decision.md` | Checker/approver verdict (`approve`, `revise`, or `blocked`) and itemized dispositions. |
| Iteration coverage | `rounds/round-NN/iterations/iteration-MM/coverage.yaml` | Requirement ID to draft location/evidence mapping for the iteration. |
| Iteration inputs | `rounds/round-NN/iterations/iteration-MM/input-snapshot.yaml` | Exact rule, ledger, and contract snapshot identifiers supplied to the role calls. |
| Current-round index | `rounds/round-NN/{draft,review,revision,decision}.md` | Copy/index of the latest iteration's corresponding record for quick access; historical evidence remains under `iterations/`. |
| Current-round index | `rounds/round-NN/{coverage,input-snapshot}.yaml` | Latest coverage and input snapshot index for the round; never delete or rewrite earlier iteration files. |
| Round gate | `rounds/round-NN/round-summary.md` | At the end of a batch, summarizes remaining reviewer/checker findings and why they are still open. |
| Round gate | `rounds/round-NN/user-decision.md` | Records the user's explicit continue/stop decision after the round budget; no next round may start without it. |
| Publication | `publish.md` | Evidence that the approved clean artifact was written to the exact target: path, format, version, rule/ledger snapshots, timestamp, and validation result. |
| Completion | `completion-summary.md` | Final inventory and conclusion linking the target, council records, completed rounds, publication evidence, validation, and unresolved items. |
| Blocker | `unresolved.md` | Remaining blockers when checker blocks, the user stops, or the configured round limit is reached. Do not create it for a successful approval. |

Do not merge review findings into progress or memory, and do not use a generic
`notes.md` when one of the typed records above applies. Every role reads the
current typed records named in its input snapshot.

