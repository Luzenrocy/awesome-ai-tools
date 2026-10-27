# awesome-ai-tools

Installable skills for AI coding agents.

## Claude Code Marketplace

Inside Claude Code, add this repository as a marketplace and install the plugin:

```text
/plugin marketplace add https://github.com/Luzenrocy/awesome-ai-tools
/plugin install awesome-ai-tools@awesome-ai-tools
```

The Claude manifest is in `.claude-plugin/marketplace.json` and the plugin
contents are declared in `.claude-plugin/plugin.json`.

## Codex Plugin

With a Codex release that supports repository marketplaces:

```bash
codex plugin marketplace add Luzenrocy/awesome-ai-tools
codex plugin add awesome-ai-tools@awesome-ai-tools
codex plugin list --json
```

The Codex manifest is in `.codex-plugin/plugin.json`. It currently exposes the
skill directories under `skills/` and does not install a model or run a server.

## Skill contents

`skills/writing-workshop/` is a host-neutral, file-based skill. Claude Code
loads its `SKILL.md` directly; Codex uses the same directory through the Codex
plugin manifest. The helper scripts are optional and run locally with Python.

The manifests point at the repository's canonical GitHub location.
