# HER orchestrator design

Status: agreed with Sofia on 2026-10-05 (grilling session, q1 to q17).

## Goal

Run HER pipelines inside the chat, the way obra/superpowers does, but with HER
skills. The chat agent is the controller. No detached runner, no terminal
dashboard, no background process.

## What changes

- Removed: `her start`, `her exec`, `her watch`, `her stop`, `her answer`,
  `her logs`, the threaded `Executor`, `watch.py`, the CLI process spawning in
  `agents.py`, and the Ghostty or gnome-terminal launch.
- Kept as plain Python helpers: plan validation, pre-flight checks, branch
  rules, dirty-tree refusal, judge verdict parsing, the run ledger in
  `~/.her/runs/<id>/`.
- The `fable` tier is gone. Risky decisions, final review and verdicts use
  `opus`.

## Roles

- Controller: the chat session where Sofia typed `/her`. It grills, writes the
  plan, dispatches subagents, reads their reports, and talks to Sofia. It never
  does step work itself.
- Implementer: a fresh subagent per step, with the model named in the plan,
  given a self-contained brief from `her begin`. It ends with one status line:
  `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` or `BLOCKED`.
- Reviewer: a fresh read-only subagent after every writing step. First it
  checks the step against its task (spec), then quality. Verdict `approve` or
  `changes`. At most 3 fix rounds, then the step is blocked and goes to Sofia.
- Judge: the `judge` skill as a read-only step at the end of each repo. A
  `to-pr` step after it runs only on `ship`.

## Ledger

`~/.her/runs/<id>/` holds `request.md`, `decisions.md`, `plan.json`,
`state.json`, `steps/<sid>.md` (implementer report), `steps/<sid>.review.md`,
`steps/<sid>.verdict.json` (judge) and `summary.md`. Writes are atomic. The
ledger is the memory: a new chat can resume a run from it.

## CLI (for the controller, not for Sofia)

| Command | What it does |
|---|---|
| `her guide` | Skills, models, plan rules, schema, the in-chat flow |
| `her new` | Create a run from stdin |
| `her check <id>` | Validate the plan and print it |
| `her approve <id>` | Record Sofia's approval, required before `begin` |
| `her next <id>` | Ready steps as JSON, marks skipped ones |
| `her begin <id> <sid>` | Pre-flight (dirty tree, branch checkout), mark running, print the brief |
| `her finish <id> <sid> <status>` | Store the implementer report (stdin) |
| `her review <id> <sid> <verdict>` | Store the review (stdin) and settle the step |
| `her status [id]`, `her show <id> <sid>`, `her runs`, `her config` | Read only |
| `her summary <id>` | Write `summary.md` |

## Cursor

The same skill runs in cursor-agent. Subagents live in
`orchestrator/cursor-agents/*.md`, linked into `~/.cursor/agents/` by
`scripts/install-cursor-skills.sh`: `her-implementer` and `her-reader`
(`readonly: true`) use `model: inherit` and the controller names the step model
at dispatch; `her-reviewer` is read-only with a fixed opus slug. Each dispatch pastes the brief and the skill paths, because Cursor
subagents may not load skills by name. Nesting is one level, so only the
controller dispatches. Progress lives in the ledger, not in a todo tool.

## Kineloop

Cards live in Kineloop (https://loop.zslippy.com/), reached through the
claude.ai Kineloop MCP tools. A plan may set `card` (for example `ML-86`). The
controller then reads the card while grilling, moves it to started on approve,
comments with the summary and PR links at the end, and moves it to review when
PRs are open. The card ID goes into the branch name. Python never calls
Kineloop.
