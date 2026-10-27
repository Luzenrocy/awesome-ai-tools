# Adaptive document contracts

Document type is an input to the contract, not a fixed list of allowed outputs. Use the smallest contract that serves the reader and the requested channel.

## Contract fields

Use the shared field schema in [document-contracts.md](document-contracts.md).
This reference adds the routing heuristic and family-specific quality lenses;
it does not duplicate the field definitions.

## Routing heuristic

Infer a family from purpose, reader job, audience, medium, risk, and evidence level. A learning note may need concepts, questions, examples, and review prompts; a blog may need a thesis, narrative flow, evidence, and a call to action; an RFC may need alternatives, decisions, and operational impact. These are examples only. User-provided headings or templates take precedence.

If the genre is unclear, use `custom` and invoke at most one native structured question for the blocking choice. Store the answer or assumption in the ledger. Never add engineering sections merely because they are present in a known template.

## Quality checks by family

Families provide lenses, not mandatory content:

- **normative/specification:** unambiguous statements, traceability, applicability, acceptance/verification, versioning;
- **explanatory:** accurate concepts, prerequisites, examples, logical progression, source attribution;
- **instructional:** task outcome, prerequisites, ordered steps, expected results, recovery paths;
- **reference:** findability, stable definitions, complete fields, examples, compatibility/version notes;
- **narrative/editorial:** thesis or purpose, audience fit, evidence, structure, voice, attribution;
- **learning/notes:** source links, distinction between fact and interpretation, questions, spaced-review cues;
- **record/decision:** participants/context, options, decision, rationale, consequences, follow-ups;
- **custom:** only the checks specified by the user or inferred from the reader job.

The writer, reviewer, and approver must record which checks were selected and why.
