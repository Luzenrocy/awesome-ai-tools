# Prompt packs

Prompt packs are short, composable prompt fragments. They are not standalone
agents and do not replace the writer → reviewer → checker workflow.

- `documents.yaml` defines document shape, required intake fields, content
  form, and document-specific quality checks.
- `roles.yaml` defines the lens used by a writer, reviewer, or checker.
- `registry.yaml` maps stable IDs to those two catalogues.

At runtime load only the selected document pack, the selected role packs, and
the current run context. The active user-local fragment, if any, is loaded
after the built-in fragment and cannot override a core workflow or safety rule.

The YAML files deliberately contain data and concise instructions only. The
workflow lives in `SKILL.md`; source citations and project-specific facts stay
in the current council workspace.
