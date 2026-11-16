# Role-context policy

Every writer, reviewer, and checker call begins with a generated
`role-inputs/{role}.json` packet. The packet is the allow-list: the role reads
only the listed artifacts and inline selected pack/fragment payloads.

Default least-privilege scope:

- Writer: immutable brief, ledger, contract, confirmed intake, rules snapshot,
  and—after iteration 1—the immediately prior draft/review/decision.
- Reviewer: the same immutable constraints plus only the current draft and
  coverage matrix.
- Checker: the immutable constraints plus current draft, review, revision, and
  coverage matrix.
- A source is passed as a selected `S-*` row, not the whole source index,
  unless the caller explicitly requests it.

Full context is exceptional and must carry one recorded reason:
`user-request`, `p0-p1-conflict`, `cross-document-consistency`, or
`safety-or-compliance`. The exception is logged in the packet; it is not an
implicit role privilege.

Create a packet with:

```sh
python3 scripts/resolve_context.py --council-dir /path/to/council \
  --role reviewer --round 1 --iteration 1 --source-id S-002
```
