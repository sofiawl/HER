# HER

Sofia's personal kit for coding agents. Skills, always-on rules, an optional project wiki, and an orchestrator that does not care which model brand is on the other end. Skills name a **tier** (`haiku`, `sonnet`, `opus`), not a vendor. Claude Code gets the tier name on Agent. Cursor gets a concrete `model` slug from that tier (`skills/MODELS-CURSOR.md` and rule 6): e.g. Haiku → `composer-2.5-fast` / `grok-4.7-high-fast`, Sonnet → `grok-4.7-high-fast` / `claude-sonnet-5-5-high`, Opus → `claude-opus-5-5-medium`.

Claude Code installs it as the plugin `her@her` (`/her:<name>`). Cursor gets the same files through one install script (`her-<name>`). The portable core is this repo.

This tree is opinionated and local: my name, Obsidian paths, Kinebot reports, Kineloop habits. Fork only after you change those.

## Layout

| Piece | Path | Job |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | The workflows |
| Rules | `rules/RULES.md` | Always on (writing check, no code comments, modes, subagents, commits, Kineloop) |
| Memory | `skills/memory/` + [ai-memory](https://github.com/akitaonrails/ai-memory) | Cross-harness wiki (`/her:memory`) |
| Orchestrator | `orchestrator/` | `her` CLI; plans set `host` to `claude` or `cursor` |
| Humanizer | `skills/humanizer/` | Voice pass inside writing skills, not a skill you invoke |
| Inspirations | `INSPIRATIONS.md` | Upstream projects + MIT credit |

Modes per skill: **professor**, **caveman**, **adhd**. Session toggles: `/her:caveman`, `/her:adhd` (say `normal mode` to clear).

## Skills

| Group | Command | Mode | What it does |
|---|---|---|---|
| learn | `/her:teach` | professor | Explain in chat, short checks, append to my teach note |
| learn | `/her:master` | professor | Course project: contract from the rubric, teach gates, lazy builds |
| research | `/her:research` | professor | sources (default), discourse (last30days if installed), or spike |
| research | `/her:report` | professor | Kinebot LaTeX report from a research folder |
| research | `/her:recap` | professor | Weekly recap + short pt-BR deck (`plan` / `build`) |
| plan | `/her:grill-me` | professor | You drive; one question at a time |
| plan | `/her:grilling` | professor | Model-fired rounds when a decision is stuck |
| plan | `/her:debate` | professor | Argue until there is a real decision |
| produce | `/her:lazy` | caveman | Least code that works |
| produce | `/her:judge` | caveman | Before/after metrics, ship or fix |
| produce | `/her:to-pr` | caveman | Stack plan + PR bodies in my voice |
| produce | `/her:address-review` | caveman | Fix open review threads on my PR, push, one-line reply |
| review | `/her:pr-review` | adhd | Review someone else's GitHub PR (not mine) |
| optimize | `/her:caveman` | caveman | Terse mode on |
| unbloat | `/her:adhd` | adhd | Next-action-first mode on |
| unbloat | `/her:memory` | adhd | Install and wire ai-memory |
| orchestrate | `/her:her` | adhd | Multi-step pipeline in this chat (`/her <request>`) |
| route | `/her:ask-her` | adhd | Which skill fits right now |

Lost? `/her:ask-her`.

## How I usually run it

- Bigger than one skill: `/her <what to do>` (grill here, plan, fresh subagent per step, reviewer after writing steps).
- Idea to ship by hand: `/her:grill-me` → `/her:debate` if needed → `/her:to-pr plan` → `/her:lazy` per sub → `/her:to-pr write` (add `/her:judge` when the risk is real).
- Learn something I want to keep: `/her:teach`.
- Research: `/her:research`; write-up: `/her:report`.
- Their PR: `/her:pr-review`. My PR feedback: `/her:address-review`.
- Cross-session project memory: `/her:memory install` once. To resume another chat, paste its link into the new session.

## Install (this machine)

Source: `~/HER`. Version: `.claude-plugin/plugin.json` (**0.5.0**).

```bash
# Claude Code
claude plugin marketplace add ~/HER
claude plugin install her@her
# after skill/rule edits:
claude plugin marketplace update her

# Cursor (skills + her.mdc rules)
~/HER/orchestrator/scripts/install-cursor-skills.sh

# Orchestrator CLI
uv tool install -e ~/HER/orchestrator
```

Optional wiki: `/her:memory` (local UI often at [http://127.0.0.1:49374](http://127.0.0.1:49374)).

## Local bits (change on a fork)

| Kind | Examples |
|---|---|
| Identity | `plugin.json` author, `rules/RULES.md` writing-check, PR/report voice files |
| Paths | teach/debate/research Obsidian targets, `~/kinebot-latex-templates/relatorios/` |
| Models | rule 6 + `~/.her/config.toml` / `her config` |
| Hooks | `HER_CONTEXT_WINDOW`, `HER_HANDOFF_THRESHOLD`, `HER_LIMIT_THRESHOLD` |

SessionStart only loads `rules/RULES.md`. Details for the CLI live under `orchestrator/`.

## Upstream

Who we borrowed from, and the MIT notice: [`INSPIRATIONS.md`](./INSPIRATIONS.md).
