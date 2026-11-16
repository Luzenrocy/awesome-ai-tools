# Host question adapters

The skill owns routing and the durable question record; the host owns the UI.
`route_intake.py` writes `pending-user-input.json`, which is the portable
question payload. An adapter presents those choices and invokes
`confirm_intake.py` only after an answer is received.

| Host | Ask | Resume/confirm source |
| --- | --- | --- |
| Codex with a structured-question function available | Render `questions` as a choice dialog; include an “other/custom” path | `codex-structured-question` |
| Claude Code interactive / Plan mode | Use `AskUserQuestion` for document type, role trio, and style | `claude-ask-user-question` |
| Any interactive CLI | Print the questions, block for the reply, then invoke confirmation | `cli-resume` |
| Non-interactive CLI or unsupported host | Stop after writing the pending file; a later invocation supplies the answer | `cli-resume` or `explicit-user-message` |

Never claim that a dialog was displayed when the host has no question API. Do
not draft, invoke a role, or create `rounds/` while the pending file exists.

Example resume:

```sh
python3 scripts/confirm_intake.py --council-dir /path/to/council \
  --document-pack product.prd --style-or-channel "internal concise" \
  --role-combination-id product.prd-roles-1 --source cli-resume
```
