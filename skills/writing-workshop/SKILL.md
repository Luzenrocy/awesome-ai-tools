---
name: writing-workshop
description: Help create, review, and refine any written artifact through isolated writer, reviewer, and approver roles, with user-intent traceability, adaptive document contracts, preserved work files, and direct publication after AI approval.
compatibility: Claude Code, Codex, and other file-based skill hosts. Requires Python 3.9+ only when the bundled helper scripts are used.
---

# Writing council

Use this skill as a standalone writing and review layer for any requested written artifact: specifications, plans, requirements, design notes, learning notes, blog posts, guides, runbooks, RFCs, ADRs, reports, policies, checklists, or a user-defined genre. The listed genres are examples, not a closed taxonomy. No other skill is required.

## Reload rules before doing work

At the start of every invocation, resolve this skill's current directory and read the current `SKILL.md`, `agents/openai.yaml`, the selected references, the selected built-in prompt packs, and any active user-local prompt fragments. Do not rely on a previously loaded copy. Compute a rules snapshot (path, modification time, and SHA-256 where available) and save it in the manifest. Before each role, iteration, and round, re-check the selected snapshot by modification time/hash. Reload only a changed selected rule or pack, append a reload event, recompute the contract, and mark any draft based on the old rules as stale. Do not reset the round or iteration counter because of a reload. Do not load unrelated packs merely to create a snapshot.

## Non-negotiable operating rules

1. Keep three roles separate: **主写者 (writer)** owns completeness and drafts; **Review 者 (reviewer)** challenges fidelity, clarity, coverage, and risk; **审核者/检查者 (approver/checker)** makes the final AI decision. Use a fresh subagent/fresh context for each role when available. Without subagents, use role-specific input/output files and a clean prompt boundary. Never carry hidden reasoning or conversational history between roles.
2. The immutable brief, ledger, adaptive contract, confirmed intake, and rules snapshot are canonical constraints. Do **not** pass the whole workflow to every role: generate `role-inputs/{role}.json` with `scripts/resolve_context.py` before each call. That allow-list is the complete permitted context. Sources, memory, progress, other roles, and earlier iterations are excluded unless the packet names them; a full-context exception requires a recorded reason.
3. Before any writer call, ask the user to confirm the document type/pack, channel or style, and writer/reviewer/checker roles. A recommendation may be inferred, but `intake_confirmed: true` is required before drafting. A round is a batch of iterations, and `iterations_per_round` defaults to the current default iteration count (**10**). One iteration is exactly one complete `writer → reviewer → checker` cycle. The checker always runs, including when the reviewer reports findings. Do not silently reset either counter or manufacture an approval after the configured limit.
4. The checker must return `approve`, `revise`, or `blocked` with itemized decisions. A reviewer finding or checker `revise` ends the current iteration; the next iteration's writer receives the draft, review, decision, and unresolved finding IDs. Do not insert a second writer call into the same iteration. Use `blocked` only when a missing fact, permission, rule conflict, or user decision prevents responsible work. When the batch reaches `iterations_per_round` with unresolved findings, summarize them and ask whether to start the next round. Only an explicit user decision can start the next round; never advance rounds automatically. A `blocked` result, a user decision to stop, or exhaustion of the configured round limit writes `unresolved.md` and stops. Only `approve` may publish the clean final artifact.
5. Preserve every round under the chosen council path. Keep the final artifact clean: no prompts, role debate, hidden reasoning, or unresolved council comments.
6. Do not invent facts, metrics, citations, API behavior, security guarantees, dates, or decisions. Mark unknowns as `[TBD]`, `[Open question]`, `[Assumption]`, or `[Decision]` and link them to the ledger.
7. After AI approval, publish the clean final artifact directly to the exact target path and record the publication. Do not add a chat-based confirmation gate.

## Workflow

1. **Reload and intake routing.** Read current rules and capture the original request verbatim in `user-brief.md`. Run `scripts/route_intake.py`, which recommends up to three document packs and matching role trios. Present `pending-user-input.json` using the host adapter in [host-question-adapters.md](references/host-question-adapters.md), with a custom option. Persist the answer via `scripts/confirm_intake.py`. While status is `awaiting_intake_confirmation`, no role call or iteration directory may exist.
2. **Confirm intake and build an adaptive contract.** Infer a recommended document pack, purpose, reader job, audience, genre, medium/channel, locale, tone, evidence/citation expectations, risk level, required/optional/forbidden sections, terminology, quality checks, and output format. The user confirms or replaces the document pack/type, channel/style, and writer/reviewer/checker roles before drafting. Normalize the confirmed request into an append-only requirements ledger with IDs such as `U-001`; later user corrections become dated amendments. Use a known pattern when it fits; otherwise create a `custom` or `hybrid` contract. Do not force PRD/SDS sections onto a blog or learning note.
3. **Resolve packs, roles, and paths.** Route personas from reader job, domain, risk, and audience; honor explicit user roles. Select only one or more necessary document packs and one role pack for each process role. Load any matching `active` user-local fragment after the built-in pack; user-local fragments cannot override the workflow, safety rules, or explicit user brief. Resolve publication and process paths separately. Precedence for the final document is: user's explicit path/name/format, then a named external skill's hard contract only when the user has not specified a conflicting path, then the local default. A user-specified process/artifact directory also wins. When the user gives a target file (an existing file or a path with a filename suffix), derive its parent as the process base and place artifacts in `{parent}/council/`; when the user gives a target directory (an existing directory or a path without a suffix), place artifacts in `{target}/council/`. An explicit process-artifact path remains exact. Record the target base, selected pack IDs and versions, dedicated process path, resolution rule, and their sources in `manifest.yaml`; never silently substitute another path.
4. **Optional external contract.** If the user names another skill, inspect that skill's current instructions/templates/validator and snapshot the discovered contract for all three roles. This is an optional overlay, not a dependency. If it is absent or unavailable, continue with the adaptive internal contract unless the user explicitly requires that external format; in that case record the missing contract and use the host's native structured question component when a user decision is required rather than inventing names or paths.
5. **Draft.** Generate the writer packet. In a fresh writer context, read only that packet and its allowed artifacts, then produce a complete draft and coverage matrix. Save the iteration record under `rounds/round-NN/iterations/iteration-MM/`; the round-level files may be lightweight pointers to that latest record.
6. **Challenge and check.** Generate a reviewer packet, then in a fresh reviewer context check every ledger item and the draft. Report actionable omissions, contradictions, scope expansion, unsupported claims, ambiguity, unverifiable success criteria, and relevant risk. Then generate a checker packet and use a separate fresh checker context to verify the contract, hard ledger items, must-not constraints, coverage, review dispositions, selected pack requirements, path/format, and clean-final requirement. The checker always runs.
7. **Next iteration or adjudication.** The checker returns `approve`, `revise`, or `blocked`. A reviewer finding or `revise` starts the next numbered iteration, where the writer receives the preceding draft, review, decision, and unresolved findings. Never overwrite an earlier iteration or run an in-place revision as another hidden writer call. At the end of a round, write `round-summary.md` and `user-decision.md`, present remaining findings, and ask the user whether to begin the next round. Record the answer before continuing or stopping. On `blocked`, a “stop” answer, or an exhausted round limit, write `unresolved.md` and stop.
9. **Publication.** On `approve`, copy the clean draft directly to the exact target path, then record the target path, format, version, rule snapshot, ledger version, decision path, timestamp, and validation result in `publish.md`. Do not wait for a chat reply or ask the user to confirm publication.
10. **Completion summary.** After publication, write `completion-summary.md` under the council path and return a concise final conclusion. Include the final output file, council directory, manifest, user brief, requirements ledger, adaptive contract, source index, rules snapshot, every completed round's files, publication record, validation result, and any unresolved items. Link to the files when the host supports file links. If the run is blocked, report the unresolved items and the available intermediate files instead of presenting an unpublished document as final.

## Default artifact layout

The process path is configurable. By default, resolve a file target such as `ai-docs/xxxx.md` to `ai-docs/council/`, while a directory target such as `ai-docs/test2` uses `ai-docs/test2/council/`. A user-specified process path remains exact. If no custom path is supplied, use the following layout.

The manifest records `process_base_path` (the target's owning directory),
`process_path` (the dedicated `council/` directory), `round_limit` (maximum user-approved rounds),
`iterations_per_round` (default `10`), `current_round`, `current_iteration`,
and `round_gate` so the batch boundary and the user's continuation decision are
auditable.

```text
{process-path}/
  manifest.yaml         # run state, counters, role routing, and resolved paths
  intake.md             # human-readable initialization summary
  intake-confirmation.yaml # user-confirmed document pack, style, and role trio
  pending-user-input.json # exists only while the host awaits the user's selection
  intake-decision.json  # archived routing options and recorded answer
  user-brief.md         # immutable request and dated amendments
  requirements-ledger.yaml # normalized U-* requirements and acceptance checks
  adaptive-contract.yaml # effective document type, structure, and quality checks
  source-index.md       # source inventory and usage purpose
  rules-snapshot.yaml   # loaded skill files and hashes
  reload-events.md      # rule reloads and stale-record events
  progress.md           # append-only round/iteration/role timeline
  memory.md             # durable decisions, terminology, and constraints
  rounds/
    round-01/           # one user-approved batch of iterations
      iterations/
        iteration-01/   # one writer → reviewer → checker cycle
          role-inputs/  # one exact allow-list packet per invoked role
          draft.md      # writer output
          review.md     # reviewer findings and evidence
          revision.md   # changes made for findings
          decision.md   # checker approve/revise/blocked verdict
          coverage.yaml # requirement-to-draft evidence map
          input-snapshot.yaml # role input rule/contract snapshot
      {draft.md,review.md,revision.md,decision.md,coverage.yaml,input-snapshot.yaml} # lightweight latest-record indexes
      round-summary.md  # findings remaining at the round gate
      user-decision.md  # explicit continue/stop decision for next round
    ...
  publish.md            # publication evidence after checker=approve
  completion-summary.md # final inventory and conclusion
  unresolved.md         # only for blockers, user stop, or round-limit exhaustion
```

Use [requirements-ledger.md](references/requirements-ledger.md), [type-adaptation.md](references/type-adaptation.md), [role-profiles.md](references/role-profiles.md), [prompt-fragments.md](references/prompt-fragments.md), [host-question-adapters.md](references/host-question-adapters.md), [context-policy.md](references/context-policy.md), [skill-reload.md](references/skill-reload.md), [process-artifacts.md](references/process-artifacts.md), and [integration.md](references/integration.md) for the detailed contracts. Use `scripts/init_council.py`, `scripts/route_intake.py`, `scripts/confirm_intake.py`, `scripts/resolve_context.py`, `scripts/manage_fragments.py`, `scripts/validate_council.py`, and `scripts/fingerprint_skill.py` when available.
