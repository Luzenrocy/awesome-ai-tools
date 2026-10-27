# Optional external-skill integration

`writing-workshop` is standalone. It does not depend on any other skill, plugin, template, repository, or validator. Public standards in the style references are guidance, not runtime dependencies.

An external skill becomes an optional contract overlay only when the user names it or asks for its exact output. Examples include planning, coding, requirements, design, or publishing skills. The same council workflow works with no overlay.

## Precedence

1. the user's explicit content, format, filename, path, scope, and audience;
2. a named external skill's hard contract, only where it does not conflict with an explicit user instruction;
3. the adaptive internal contract and this skill's defaults.

## Discovery procedure

When an external skill is named:

1. locate and read its current instructions, templates, examples, and validator if available;
2. extract the exact required files, names, paths, frontmatter, section order, IDs, validation, and handoff fields;
3. save a `contract_snapshot` with source paths, hashes/version, and `integration_mode: optional-overlay` in the manifest;
4. give the same snapshot to writer, reviewer, and approver; and
5. run its validator on each draft revision when practical. A failure is a
   review finding within the current round's iteration budget; moving to a new
   round still requires the user's explicit continuation decision and remains
   subject to the configured round limit.

If the named skill cannot be found, continue with the internal adaptive contract when the user only wants help writing. If the user explicitly requires that skill's exact handoff, do not invent a filename or path: record the missing contract and invoke the host's native structured question component when a decision is required. This is the only situation in which an absent external skill can block delivery.

## Generic adapter record

```yaml
integration_mode: none | optional-overlay
skill_id: "..."
contract_source: ["absolute or project-relative paths"]
contract_version: "hash/date"
required_files:
  - path: "..."
    purpose: "..."
format: "..."
section_order: ["..."]
validation: "command or tool"
handoff_inputs: ["..."]
post_publish_action: "..."
```

An adapter records a discovered contract; it never changes or installs another skill and never overrides an explicit user path or scope.
