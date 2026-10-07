---
name: memory
description: >
  Install and wire akitaonrails/ai-memory for cross-harness project memory;
  explain what goes in the wiki vs Kineloop, orchestrator, Obsidian, or
  /her:handoff. Trigger on "/her:memory", "ai-memory", "project memory",
  "wire memory hooks", "memory server", "where should this be remembered".
argument-hint: "[install | status | wire | boundaries]"
---

Mode: adhd

ai-memory is HER **infra**, not a replacement for skills. It captures session
work into a git-backed markdown wiki and delivers typed handoffs on the next
SessionStart. `/her:handoff` stays for **this thread** under context pressure
and for HER routing (next action + suggested `/her:` skills).

Read `BOUNDARIES.md` before writing anything into memory.

## When to use what

| Situation | Use |
|---|---|
| Normal stop; next session same or different harness | Rely on ai-memory hooks (session end + SessionStart brief). Nothing to run. |
| Context or rate limit nudge (~75% / ~85%) | `/her:handoff` now; publish to ai-memory if wired (see handoff skill). |
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

HER plugin hooks (`hooks/hooks.json`) stay separate: they load `rules/RULES.md`
and nudge `/her:handoff`. ai-memory hooks capture lifecycle; both can run.

## status

Run `ai-memory status` (or `docker` equivalent). Report: server up, data dir,
which clients have MCP/hooks. If status fails, handoffs fall back to
`/her:handoff` and repo artifacts only.

## wire

Re-run the `install-mcp` / `install-hooks` lines for any harness she added.
After HER edits, re-run `~/HER/orchestrator/scripts/install-cursor-skills.sh`
for Cursor skills; ai-memory is independent.

## boundaries

Explain using `BOUNDARIES.md` in chat in three bullets max unless she asked
for the full table.

## Publish from `/her:handoff`

When handoff runs and ai-memory is up, after the tmp file:

1. Fill `HANDOFF-PAGE.md` from the handoff sections.
2. Call MCP `memory_handoff_begin` with that body (owner-scoped; `shared=true`
   only if Sofia asked for team visibility).
3. Tell her the next SessionStart should claim it; she can also
   `memory_handoff_list` / `memory_handoff_accept`.

If MCP is not in this session, skip publish and say the tmp handoff path only.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Check binary, systemd, docker, hook files on disk | `haiku` | Before install |
| Install commands and config edits | main | Needs Sofia's yes |
