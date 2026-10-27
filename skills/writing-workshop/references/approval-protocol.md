# Approval protocol

## State machine

```text
intake -> drafting -> reviewing -> revising -> approval/checker
                                      |               |
                                      +--revise-------+ (same round, budget remains)
                                                      |
                         budget exhausted + findings |
                                                      v
                                           round-summary -> user decision
                                           continue -> next round
                                           stop -----> unresolved
checker --blocked--> blocked
checker --approve--> published
```

`round` starts at 1. Each round has an `iterations_per_round` budget, which
defaults to 10 to preserve the current default iteration count. An iteration is
one writer/reviewer/checker cycle. A `revise` decision consumes one iteration
and stays in the current round while budget remains. After the final iteration,
any remaining findings are summarized in `round-summary.md`, and the user is
asked whether to begin the next round. Only an explicit “continue” answer may
increment `round`; “stop” writes `unresolved.md` and ends the run. A `blocked`
decision stops immediately. The configured `round_limit` remains the hard
upper bound for user-approved rounds.

## Checker/approver gate

Before `approve`, the approver verifies:

- the current rules snapshot and adaptive contract were loaded;
- every hard `U-*` item and every `must-not` is satisfied or explicitly deferred by the user;
- the current iteration's `coverage.yaml` maps every ledger item to a location and evidence;
- no content is out of scope, unsupported, or silently invented;
- all review findings have a disposition, with no unresolved P0/P1 or intent conflict;
- required/forbidden sections, audience, tone, medium, locale, and source style are correct;
- requested filename, format, and exact target path are correct;
- process artifacts are stored in the dedicated resolved process path: a file
  target such as `ai-docs/xxxx.md` uses `ai-docs/council/`, and a directory
  target such as `ai-docs/test2` uses `ai-docs/test2/council/`; an explicit
  process path remains exact;
- relevant risk, security, privacy, accessibility, maintenance, and failure concerns are handled; and
- the final artifact contains no prompts, role debate, hidden reasoning, or council notes.

An unmet check returns `revise`. Use `blocked` when a missing fact, user decision, permission, rule conflict, or external contract prevents a responsible judgment.

## Decision schema

```yaml
verdict: approve | revise | blocked
round: 1
iteration: 1
rules_snapshot: "hash or manifest path"
ledger_version: 1
summary: "..."
coverage_status: complete | incomplete | conflict
findings:
  - id: R-001
    disposition: fixed | accepted-risk | rejected-with-evidence | open
    rationale: "..."
    verification: "..."
blocking_items: []
```

## Round continuation gate

When the reviewer or checker still reports actionable findings after the
round's final iteration:

1. Write `round-summary.md` with each remaining finding's ID, severity,
   location, impact, required action, and acceptance check.
2. Present that summary to the user and ask one structured yes/no question:
   “本轮迭代已完成，但仍有上述问题。是否开始下一轮迭代？”
3. Record the exact answer, timestamp, and next action in `user-decision.md`
   and append the same event to `progress.md` and `memory.md`.
4. On “continue”, create the next numbered round and reset only the iteration
   counter. On “stop”, write `unresolved.md` and do not publish an unapproved
   artifact.

Do not ask this question when the checker returns `approve` or `blocked`, or
when the configured round limit has already been reached.

## Direct publication

On `approve`, copy the current draft directly to the exact target path without adding council commentary. Record the exact target path, target format, published version, rule snapshot, ledger version, decision path, timestamp, short summary, and validation result in `publish.md`. Do not wait for or request a chat confirmation.

After publication, write `completion-summary.md` in the resolved process
directory. It must inventory the final output, process directory, manifest,
intake and source files, requirements ledger, contract and rules snapshots,
every round's files, `publish.md`, validation results, and any unresolved
items. Return the same inventory and conclusion in the final response.

## Blocking questions

When a missing fact or decision prevents a responsible draft or approval, invoke the host's native structured question component (or the equivalent question component exposed by another agent host) with one concise question and bounded choices when possible. Record the question, answer, and ledger amendment. Nonblocking uncertainty becomes an explicit assumption and does not interrupt publication.
