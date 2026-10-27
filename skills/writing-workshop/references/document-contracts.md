# Document contracts

This reference describes how to build a contract for the requested artifact. It is not a closed catalog and it does not require another skill.

## Shared contract fields

```yaml
document_contract:
  mode: known | custom | hybrid
  family: normative | explanatory | instructional | reference | narrative | editorial | learning | record | custom
  label: "user-facing document name"
  purpose: "what this artifact must accomplish"
  reader_job: "what the reader should be able to do or understand"
  audience: ["..."]
  medium: markdown | web | email | slide-notes | docx | pdf | other
  locale: "zh-CN"
  tone: "..."
  evidence_style: "..."
  required_sections: []
  optional_sections: []
  forbidden_sections: []
  quality_checks: []
  source: user | inferred | external-contract
```

The final artifact may use frontmatter or a visible metadata block. At minimum, preserve title, document type/label, version, status, owner/author when known, created/updated dates, audience, target format, and publication path. Do not invent an approver or approval date.

## Universal structure

Choose only the sections needed for the reader job. Most artifacts benefit from:

1. purpose and short summary;
2. audience, prerequisites, and context;
3. scope and non-scope;
4. core content in the user's requested order;
5. evidence, examples, or references where relevant;
6. limitations, risks, or failure paths;
7. verification or success indicators;
8. open questions and revision history.

An artifact may omit any item when the contract explains why it is not applicable. Do not fill sections with generic boilerplate.

## Optional patterns

### Normative or requirements-oriented

Use stable IDs, source/rationale, priority, constraints, acceptance conditions, verification method, owner, and status. Requirements should be singular, unambiguous, and observable.

### Technical or design-oriented

When the reader needs implementation decisions, cover the current context, goals/non-goals, alternatives, architecture or model, interfaces, data, security/reliability, testing, rollout/rollback, dependencies, and decisions. Include only the views needed for the decision.

### Instructional or operational

State the task outcome, prerequisites, permissions, inputs, ordered steps, expected results, verification, troubleshooting, recovery, limits, and escalation path.

### Narrative, editorial, or learning

Choose a thesis or learning objective, reader context, evidence/source attribution, examples, structure, voice, questions or reflection prompts, and a clear ending. Separate sourced fact, interpretation, and speculation.

### Reference or record

Optimize for findability and stable fields. For decisions or meeting records, preserve context, participants when known, options, decision, rationale, consequences, and follow-ups.

## Requirement and verification record

When the artifact has requirements or success conditions, use a table or bullets with:

| Field | Meaning |
| --- | --- |
| ID | Stable identifier such as `U-001`, `REQ-001`, or a user-defined scheme |
| Statement | One precise requirement, claim, or outcome |
| Source / rationale | User ledger item, source, policy, or decision |
| Acceptance | Observable condition, threshold, or expected result |
| Verification | Inspection, test, demonstration, analysis, or structured user input |
| Owner | Person/team responsible when applicable |
| Status | Proposed, satisfied, verified, open, or deferred by user |

Use the adaptive contract in [type-adaptation.md](type-adaptation.md) when the genre is unfamiliar. Use [requirements-ledger.md](requirements-ledger.md) to prove that the final content still matches the user's request.
