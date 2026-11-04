---
name: memory
description: >
  Install and wire akitaonrails/ai-memory for cross-harness project memory;
  explain what goes in the wiki vs Kineloop, orchestrator, or Obsidian.
  Trigger on "/her:memory", "ai-memory", "project memory",
  "wire memory hooks", "memory server", "where should this be remembered".
argument-hint: "[install | status | wire | boundaries]"
---

Mode: adhd

ai-memory is HER **infra**, not a replacement for skills. It captures session
work into a git-backed markdown wiki and can brief the next SessionStart.
To continue a specific chat, paste that session's link into the new Claude
or Cursor session.

Read `BOUNDARIES.md` before writing anything into memory.

## When to use what

| Situation | Use |
|---|---|
| Normal stop; next session same or different harness | Rely on ai-memory hooks (session end + SessionStart brief). Nothing to run. |
| Need the exact other chat | Paste its session link into the new Claude or Cursor chat. |
| Big decisions worth a durable page | Wiki page in ai-memory (or let consolidation run; optional manual page). |
| Active orchestrator run | Point at `~/.her/runs/<id>/`; do not duplicate `plan.json`. |
| Card / team / QA | Kineloop only. |
| Learning a concept for Sofia | Obsidian via `/her:teach`. |

## install

Ask Sofia once: **local server on this machine** (default) or **Docker**. Do not
install without her yes.

**Prereq:** `ai-memory` on PATH. Easiest on Linux:

```bash
mise use -g github:akitaonrails/ai-memory
```

Or download `ai-memory-linux-x86_64.tar.gz` from
[releases](https://github.com/akitaonrails/ai-memory/releases), verify `.sha256`,
install the binary to `~/.local/bin/ai-memory`, keep the extracted `hooks/` tree
(for example under `~/.local/share/ai-memory-install/`).

Or Docker: see [ai-memory README](https://github.com/akitaonrails/ai-memory#quick-start).

**Single-user workstation (native):**

```bash
mkdir -p ~/.config/ai-memory ~/.local/share/ai-memory
ai-memory --data-dir ~/.local/share/ai-memory \
  --config ~/.config/ai-memory/config.toml init
systemctl --user enable --now ai-memory.service
```

If there is no packaged unit yet, run the server the way upstream documents for
your install (`serve` or the Docker wrapper).

**Wire agents** (run each harness Sofia uses):

```bash
HOOKS=~/.local/share/ai-memory-install/hooks   # tarball extract; omit on AUR/Docker

ai-memory install-mcp --client claude-code --apply
ai-memory install-hooks --agent claude-code --hooks-dir "$HOOKS" --apply

ai-memory install-mcp --client cursor --apply
ai-memory install-hooks --agent cursor --hooks-dir "$HOOKS" --apply
```

User systemd unit example: `~/.config/systemd/user/ai-memory.service` with
`ExecStart=... serve --transport http --enable-web` (see upstream
`packaging/systemd/ai-memory-user.service`, fix paths if not `/usr/bin/ai-memory`).

Project-scoped hooks only: run `install-hooks` with `--scope project --apply`
from the repo root. Full detail:
[docs/install.md](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

ai-memory hooks are lifecycle capture only. Cursor always-on HER rules come from
`~/.cursor/rules/her.mdc` via `install-cursor-skills.sh`.

## status

Run `ai-memory status` (or `docker` equivalent). Report: server up, data dir,
which clients have MCP/hooks.

## wire

Re-run the `install-mcp` / `install-hooks` lines for any harness she added.
After HER edits, re-run `~/HER/orchestrator/scripts/install-cursor-skills.sh`
for Cursor skills; ai-memory is independent.

## boundaries

Explain using `BOUNDARIES.md` in chat in three bullets max unless she asked
for the full table.

## Subagents

Model tiers: HER rule 6. Cursor slugs per chore: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Check binary, systemd, docker, hook files on disk | `haiku` | Before install |
| Install commands and config edits | main | Needs Sofia's yes |
