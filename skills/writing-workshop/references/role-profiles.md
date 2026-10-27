# Dynamic role profiles and routing

The three process roles are stable; their domain lens is adaptive. A role title is not limited to a fixed list of professions. Infer a useful lens from the reader job, domain, risk, evidence level, medium, and the user's explicit identity request.

## Routing inputs

Record `role_profile_id` and rationale in the manifest:

```yaml
roles:
  writer:
    profile: "..."
    rationale: "..."
  reviewer:
    profile: "..."
    rationale: "..."
  approver:
    profile: "..."
    rationale: "..."
```

Useful lenses include product, domain SME, engineer, architect, educator, technical writer, editor, researcher, operations, security, accessibility, novice reader, or an explicit user-defined identity. Combine lenses when the artifact requires it. User-specified roles take precedence.

## Process responsibilities

**主写者 / writer** owns completeness and coherence. It must use the selected contract, preserve the user's scope and tone, distinguish facts from assumptions, assign stable IDs where useful, and create a coverage matrix for every hard ledger item.

**Review 者 / reviewer** is an independent, defect-first challenger. It checks user fidelity, source support, reader fit, structure, clarity, evidence, risk, and contract compliance. It reports actionable findings rather than rewriting the whole artifact.

**审核者 / 检查者 / approver / checker** is the final AI gate. It verifies every hard ledger item, must-not constraint, coverage row, review disposition, contract field, path/format requirement, and clean-final condition. It returns only `approve`, `revise`, or `blocked` with evidence. The checker does not authorize a new round; the user makes that decision after the current round's iteration budget is exhausted.

## Fresh-context invocation

When collaboration tools are available, create one subagent per role and pass a narrow prompt:

```text
You are the {role} for round {N}, iteration {I}. Read only these files: {paths}.
The immutable user brief and normalized ledger are the current constraints.
Do not infer facts not present in the files. Write your result to {output-path}.
Return concise evidence and decisions; omit hidden reasoning and role debate.
```

Without subagents, use separate role input/output files and a clean prompt boundary. The reviewer and approver do not edit the draft directly; the writer is the only role that produces drafts or revisions.
