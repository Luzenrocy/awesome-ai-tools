# Review rubric

The reviewer challenges the current draft against the user brief, requirements ledger, adaptive contract, sources, and prior findings. It reports one actionable issue per finding and never treats the document genre as permission to add unrelated content.

## Required checks every iteration

1. **User fidelity and coverage:** every `U-*` item is present in `coverage.yaml`; hard goals, must-haves, format, audience, tone, path, and success conditions are satisfied or explicitly deferred by the user.
2. **Negative constraints and scope:** no `must-not` is violated; no unrequested feature, section, claim, metric, promise, or future work has entered the draft without a source or recorded rationale.
3. **Contract and handoff:** label, medium, locale, structure, required/forbidden sections, filename, target path, and optional external contract are honored.
4. **Source fidelity:** facts, quotations, citations, examples, and decisions are supported by the source index or marked as assumptions/derived content.
5. **Reader fit:** the level, voice, terminology, accessibility, ordering, and examples match the reader job.
6. **Clarity and completeness:** ambiguity, omissions, contradictions, unstable terms, missing prerequisites, and missing failure paths.
7. **Verification:** success criteria, acceptance conditions, examples, procedures, or conclusions are observable and checkable.
8. **Risk:** relevant safety, security, privacy, operational, legal, dependency, maintenance, and version risks.

## Finding categories

`intent-mismatch`, `unauthorized-scope`, `unsupported-claim`, `ambiguity`, `omission`, `acceptance`, `contract`, `source`, `consistency`, `reader-fit`, `style`, `delivery`, `security`, `risk`.

## Severity

- `P0`: blocks safe interpretation, user fidelity, approval, or publication.
- `P1`: material correctness, scope, source, security, or delivery risk; normally blocks approval.
- `P2`: meaningful clarity, completeness, or maintainability defect; approver may accept with rationale.
- `P3`: polish or low-risk improvement.

## Finding schema

```yaml
- id: R-001
  severity: P1
  category: intent-mismatch | unauthorized-scope | unsupported-claim | ambiguity | omission | acceptance | contract | source | consistency | reader-fit | style | delivery | security | risk
  location: "U-004; heading or line"
  evidence: "The user ledger says ...; the draft says ..."
  challenge: "A reader or user cannot ..."
  impact: "..."
  action: "..."
  acceptance_check: "..."
  status: open | fixed | accepted-risk | rejected-with-evidence
```

`No findings.` is valid only after recording the ledger version, coverage checked, contract snapshot, and all dimensions inspected.

At the end of the configured iteration budget, carry every still-open finding
into `round-summary.md`. Do not silently treat the next round as another
iteration; the user must explicitly choose whether to continue.
