# Prompt fragments and pack selection

Prompt fragments are concise, selected additions to an isolated role input
packet. They reduce context load by adding only the structural and domain
instructions needed for the current artifact. They do not replace the
requirements ledger, adaptive contract, or three-role council.

## Selection and precedence

Before drafting, ask the user to confirm:

1. one or more document pack IDs (or `custom`);
2. channel/style;
3. the writer, reviewer, and checker role pack IDs.

Record the answer in `intake-confirmation.yaml` and `manifest.yaml`. Generate
the packet with `scripts/resolve_context.py`; it embeds only the selected pack
payloads and matching active local fragments. Its artifact allow-list differs
by role, so a reviewer does not inherit writer history and a checker does not
receive unrelated memory. Build the packet in this order:

```text
core workflow and safety rules
→ explicit user brief and confirmed contract
→ selected built-in document pack
→ selected built-in role pack
→ matching active user-local fragments
→ only the role-specific current draft/findings/decision named by the packet
```

An explicit user request wins over an inferred recommendation. A local fragment
may refine a selected pack but must not override a core workflow/safety rule,
the immutable brief, or a current user instruction. Load no unrelated pack.

## Built-in pack schema

The catalogues under `prompt-packs/` use this compact shape:

```yaml
id: product.prd
kind: document | role
label: "..."
intake_fields: []                 # document packs only
required_sections: []             # document packs only
writer_fragment: "..."
review_delta: "..."
check_delta: "..."
```

Document packs describe content organization and medium-specific form. Role
packs describe a professional lens. Compose them instead of creating a separate
agent for every document type; the stable writer/reviewer/checker responsibilities
remain unchanged.

## User-local fragments

Use a user-controlled root such as `~/.codex/skills/writing-workshop-local/`:

```text
writing-workshop-local/
  candidates/                     # persisted, not active yet
  prompt-fragments/
    role/
    document/
  history/
```

`scripts/manage_fragments.py` writes JSON fragments so it needs only Python's
standard library. Example:

```text
python scripts/manage_fragments.py --local-root ~/.codex/skills/writing-workshop-local \
  add-candidate --kind role --applies-to technical.architecture \
  --change "State a dependency fallback and user impact." \
  --acceptance "Every external dependency has a fallback." \
  --source-document design.md
```

The command creates a `candidate` record. After observing the result, the user
can activate it:

```text
python scripts/manage_fragments.py --local-root ~/.codex/skills/writing-workshop-local \
  activate --id user.role.dependency-fallback
```

Activation writes an immutable history record and an `active` fragment. Disable
or supersede a fragment rather than silently overwriting it. Store the abstract
rule and its acceptance test, not private source-document content by default.

## Local fragment record

```json
{
  "id": "user.role.dependency-fallback",
  "kind": "role",
  "applies_to": ["technical.architecture"],
  "version": 1,
  "status": "candidate",
  "source": "user-feedback",
  "source_document": "design.md",
  "change": "State a dependency fallback and user impact.",
  "acceptance_test": "Every external dependency has a fallback.",
  "created_at": "ISO-8601",
  "supersedes": null
}
```

Each active local fragment is hash-recorded in the role packet that selected
it. It is not injected into unrelated roles or document types.
