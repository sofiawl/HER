# HER

My personal agent kit for coding assistants: **16 skills**, always-on rules, optional ai-memory, and an orchestrator that works no matter which model is on the other end. HER does not belong to Anthropic or Claude Code. Skills talk in **tiers** (`haiku`, `sonnet`, `opus`); your harness maps those to whatever models you have (Claude, GPT, Gemini, Grok, Composer, …).

Claude Code gets a first-class **plugin** (`her@her`, skills as `/her:<name>`). **Cursor** gets the same skills, orchestrator agents, and rules via one install script. The portable core is just files in this repo.

This is **opinionated and machine-local**. It names me, my Obsidian vault, Kinebot report paths, and Kineloop habits. Forking? [Local environment (change these)](#local-environment-change-these) first.

## What you get

| Layer | Path | Role |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | Harness-agnostic workflows (`/her:<name>` on Claude Code, `her-<name>` on Cursor) |
| Rules | `rules/RULES.md` | Always on: writing check, no code comments, modes, subagents, autolearn, grilling, commits and Kineloop |
| Hooks | `hooks/` | **Claude Code only:** SessionStart loads rules; UserPromptSubmit nudges `/her:handoff` |
| Memory | `skills/memory/` + [ai-memory](https://github.com/akitaonrails/ai-memory) | Cross-harness project wiki (`/her:memory install`); boundaries in `skills/memory/BOUNDARIES.md` |
| Orchestrator | `orchestrator/` | `her` CLI: ledger and guard rails; plans set `host` to `claude` or `cursor` |
| PR author voice | `skills/to-pr/VOICE.md`, `TEMPLATE.md` | How my PR descriptions sound |
| PR review kit | `skills/pr-review/references/pr-review.md`, `COMMENT-VOICE.md` | GitHub review procedure and inline comment voice |
| Report kit | `skills/report/*` | Kinebot LaTeX report pipeline |
| Credits | `NOTICE.md` | Upstream MIT sources |

Talking modes (per skill): **professor**, **caveman**, **adhd**. Session toggles: `/her:caveman`, `/her:adhd` (say `normal mode` to clear).

## Orchestrator (the big pipeline)

For work that is more than one skill deep, I type **`/her <what to do>`** (skill `/her:her`, Cursor skill `her-her`). Same chat is the controller: it grills me here, writes `decisions.md` and `plan.json`, I approve, then it dispatches **one fresh subagent per step** and a **fresh reviewer after every writing step**. I never type `her` commands; the controller does.

Runs live in `~/.her/runs/<id>/` (or `$HER_HOME/runs/<id>/`). Details: `orchestrator/README.md`, design notes: `orchestrator/DESIGN.md`.

Install the CLI:

```bash
uv tool install -e ~/HER/orchestrator
```

Cursor (skills, subagents, always-on rules):

```bash
~/HER/orchestrator/scripts/install-cursor-skills.sh
```

Re-run after you edit `rules/RULES.md` or any skill. Writes `~/.cursor/rules/her.mdc` from `rules/RULES.md`.

Under the orchestrator, `lazy`, `judge`, and `to-pr` can run **headless** (decisions come from the run's `decisions.md`, not live quizzes).

## Skills (16)

| Group | Skill | Mode | What it does |
|---|---|---|---|
| learn | `/her:teach` | professor | Explain in chat, one understanding line, 1 to 3 checks, append to my teach note |
| research | `/her:research` | professor | **sources** (default): cited primary sources; **discourse**: last30days if installed; **spike**: throwaway code (`LOGIC.md` / `UI.md`) |
| research | `/her:report` | professor | Kinebot LaTeX report from a kinebot-research folder |
| plan code | `/her:grill-me` | professor | User-only one-question-at-a-time interview (summary + debate handoff) |
| plan code | `/her:grilling` | professor | Model-fired rounds when a decision is unclear |
| plan code | `/her:debate` | professor | Argues against me to find the best decision, ends with a decision record |
| produce code | `/her:lazy` | caveman | Minimum code that works |
| produce code | `/her:judge` | caveman | Metrics before and after, verification gate |
| produce code | `/her:to-pr` | caveman | PR stack plan and write (thin self-verify on write) |
| produce code | `/her:pr-review` | adhd | GitHub PR review from a worktree; inline comments (`COMMENT-VOICE.md`); not Kineloop |
| optimization | `/her:caveman` | caveman | Terse mode toggle |
| unbloat | `/her:adhd` | adhd | Next-action-first mode toggle |
| unbloat | `/her:handoff` | adhd | Emergency compact of this chat (nudge + HER next steps); optional publish to ai-memory |
| unbloat | `/her:memory` | adhd | Install/wire ai-memory |
| orchestrate | `/her:her` | adhd | Multi-step pipeline in this chat (`/her <request>`) |
| her | `/her:ask-her` | adhd | Router: which HER skill fits now |

Not sure which skill fits: `/her:ask-her`.

**Removed from older HER docs** (do not look for them): `understand`, `diagram`, `organize`, standalone `prototype` and `last30days` (folded into `/her:research`).

## Main flows

- **Multi-step feature or card:** `/her ML-86 fix the thing` (or `/her:her`) when I want grilling, plan, subagents, and review in one thread. Smaller jobs: pick skills directly.
- **Idea to ship (manual):** `/her:grill-me` → `/her:debate` → `/her:to-pr plan` → `/her:lazy` per sub → `/her:to-pr write` (add `/her:judge` when risky or perf). Agent may auto-fire `/her:grilling` when a plan-code decision is missing.
- **Learning:** `/her:teach` for concepts worth keeping.
- **Research:** `/her:research` (pick mode: sources, discourse, or spike); Kinebot write-up → `/her:report` when the research folder is ready.
- **Review a PR:** `/her:pr-review <number>` (GitHub only; log on Kineloop yourself if the team expects it).
- **Context overload:** `/her:handoff` (this thread); `/her:caveman`, `/her:adhd`.
- **Cross-session memory:** `/her:memory install` once; hooks capture project work. Use `/her:handoff` when nudged or before you lose the thread.

## Install (this machine)

Source repo: `~/HER` (`/home/sofia/HER`). Version: `.claude-plugin/plugin.json` (currently **0.5.0**).

| Harness | Skills | Always-on rules | Handoff nudge hook |
|---|---|---|---|
| **Claude Code** | `claude plugin install her@her` | `hooks/hooks.json` cats `rules/RULES.md` at session start | `hooks/context-handoff-nudge.sh` → `/her:handoff` |
| **Cursor** | `install-cursor-skills.sh` → `~/.cursor/skills/her-*` | same script → `~/.cursor/rules/her.mdc` | HER nudge not wired; `/her:handoff` or ai-memory session end |
| **ai-memory** (optional) | MCP + lifecycle hooks per harness | wiki + SessionStart brief | session-end capture; see `/her:memory` |
| **Other** | copy or symlink `skills/` | paste or link `rules/RULES.md` | bring your own |

### Claude Code plugin

```bash
claude plugin marketplace add ~/HER
claude plugin install her@her
```

After editing skills or rules:

```bash
claude plugin marketplace update her
```

New session so hooks and skill text reload.

### Cursor

```bash
~/HER/orchestrator/scripts/install-cursor-skills.sh
```

Skills show up as `her-<name>` (e.g. `her-lazy`, `her-pr-review`). Orchestrator steps use `her-implementer`, `her-reader`, `her-reviewer`. Model slugs for rule 6 live in `rules/RULES.md`; defaults and overrides in `her config` / `~/.her/config.toml`.

Prefer this repo over a stale plugin cache (`~/.claude/plugins/cache/her/her/<version>/`).

## Local environment (change these)

Everything below is **Sofia-local or machine-local**. Another person on another machine should change or delete these before treating HER as theirs.

### 1. Identity and voice

| Where | What | What to do on another machine |
|---|---|---|
| `.claude-plugin/plugin.json` | `author.name`: Sofia Lima | Your name and description |
| `rules/RULES.md` | Addresses "Sofia"; writing-check for my English | Rename or drop rule 1 |
| Almost every `skills/*/SKILL.md` | Triggers and prose say "Sofia" | Search-replace or ignore |
| `skills/to-pr/VOICE.md`, `TEMPLATE.md` | My PR description tone | Your team's PR voice |
| `skills/pr-review/COMMENT-VOICE.md` | Inline GitHub review comments | Your team's review voice |
| `skills/report/SKELETON.tex` | `\reportauthor{Sofia Wamser Lima}` | Your author line |
| `skills/report/STYLE.md` | Kinebot ABNT / pt-BR | Your style or skip `/her:report` |

### 2. Absolute and home paths (must change)

| Where | Hardcoded path | Purpose |
|---|---|---|
| `skills/teach/SKILL.md` | `/home/sofia/ObsidianPipa/Efforts/On/skill issue.md` | Where `/her:teach` appends |
| `skills/debate/SKILL.md` | `~/ObsidianPipa/+/` | Default decision records |
| `skills/research/SKILL.md` | `~/ObsidianPipa/+/<Title>.md` | Obsidian fallback for research notes |
| `skills/report/SKILL.md` | `~/kinebot-latex-templates/relatorios/` | Compiled report output |
| `skills/report/SKILL.md` | example `~/kinebot-research/...` | Research folder examples |
| `skills/report/STYLE.md` | `~/kinebot-latex-templates/relatorios/` | Style reference reports |
| `orchestrator/scripts/install-cursor-skills.sh` | resolves repo from script path | Cursor skills, agents, and `her.mdc` rules |
| `NOTES.md` | `~/ObsidianPipa/+/Is fast-jev-compaction worth it.md` | Personal research pointer |

Also fix the **sample format** at the top of your teach target file if you rename it; `/her:teach` expects that shape.

### 3. Hooks and shell environment

| Knob | Default | Meaning |
|---|---|---|
| `HER_HANDOFF_THRESHOLD` | `75` | Context % that triggers a one-shot `/her:handoff` nudge |
| `HER_LIMIT_THRESHOLD` | `85` | 5-hour or 7-day usage % (from statusline cache) for the same nudge |
| `HER_CONTEXT_WINDOW` | `1000000` | Assumed window for context math (I often run `opus[1m]`) |
| `TMPDIR` | system temp | Stamp files so each nudge fires once per session or limit window |
| `her-rate-limits.json` in `$TMPDIR` | written by statusline | Hook reads usage limits hooks never get |
| `jq` | required on PATH | Hook exits quietly if missing |

On a 200k-context machine, set `HER_CONTEXT_WINDOW=200000` or the nudge math lies. The hook estimates tokens from the transcript; it does not read the statusline `used_percentage` field.

Hook wiring: `hooks/hooks.json`. Script: `hooks/context-handoff-nudge.sh`.

### 4. Model tiers (any vendor)

HER thinks in three tiers, not one brand. `rules/RULES.md` rule 6 lists chores per tier plus Cursor slug examples. Claude Code uses tier names on the Agent tool. Orchestrator plans pick concrete models per `host` (`claude` or `cursor`); edit `~/.her/config.toml` or run `her config` when your account's model list changes.

### 5. External plugins and infra (optional, not shipped)

| Piece | Role | Another machine |
|---|---|---|
| [ai-memory](https://github.com/akitaonrails/ai-memory) | Project wiki + hooks (`/her:memory`) | Optional; separate server and data dir |
| last30days | Optional for `/her:research` **discourse** mode only | Install + API keys |
| `mattpocock-skills` | Other Matt skills; HER owns grill-me / grilling | Prefer `/her:…`; avoid duplicate copies |
| pxpipe | Personal token proxy | Optional |
| fast-jev-compaction | Installed but **disabled** | Do not enable without reading risks |

```bash
claude plugin marketplace add mvanhorn/last30days-skill
claude plugin install last30days@last30days-skill
```

### 6. Repo root leftovers (not plugin runtime)

Old `/her:teach` demo artifacts and personal notes. Safe to ignore or delete on a fresh fork:

- `MISSION.md`, `RESOURCES.md`, `GLOSSARY.md`, `NOTES.md`
- `learning-record/`, `lessons/`

SessionStart only cats `rules/RULES.md`.

### 7. Quick fork checklist

1. Clone HER to a path you control; point the Claude marketplace there (not `/home/sofia/HER`).
2. Edit `.claude-plugin/plugin.json` author and description.
3. Replace owner name in `rules/RULES.md` (drop writing-check if unwanted).
4. Point `skills/teach/SKILL.md` at your markdown file; put the sample format at the top.
5. Retarget Obsidian paths in `debate`, `research`, and `NOTES.md`.
6. Retarget or disable `/her:report` (LaTeX paths, author, ABNT / pt-BR).
7. Replace `to-pr` VOICE + TEMPLATE and `pr-review` COMMENT-VOICE with your team's.
8. Adjust rule 6 and `~/.her/config.toml` model lists for your harness and account.
9. Set `HER_CONTEXT_WINDOW`, `HER_HANDOFF_THRESHOLD`, and `HER_LIMIT_THRESHOLD` for your models and statusline.
10. `claude plugin marketplace update her`, run `install-cursor-skills.sh`, open a new session.

## Rules (always on)

Loaded from `rules/RULES.md` at SessionStart:

1. Writing check on my last message (Sofia-specific).
2. No comments in code you write.
3. No em dash, en dash, or emoji (PR template shortcodes excepted).
4. Do the work; explain the why briefly; deeper study → `/her:teach`.
5. Nudge unused HER skills with `HER fit: /her:<name>`.
6. Delegate to the right model tier / Cursor slug.
7. Autolearn: on behavior corrections, propose a patch and ask before writing.
8. Uncertain decisions → suggest or auto-fire `/her:grilling` (plan-code flows include `pr-review`; see rule text).
9. Commits, branches, Conventional Commits, Kineloop URLs and pt-BR card text (see rule text).

## Layout

```
HER/
  .claude-plugin/plugin.json
  hooks/
  rules/RULES.md
  orchestrator/                 # her CLI, cursor-agents/, tests
  skills/
    adhd/ ask-her/ caveman/ debate/ grill-me/ grilling/ handoff/ her/
    judge/ lazy/ memory/ pr-review/ report/ research/ teach/ to-pr/
  NOTICE.md
  README.md
```

Companion files per skill (examples): `to-pr/VOICE.md`, `pr-review/references/pr-review.md`, `research/LOGIC.md`, `memory/BOUNDARIES.md`, `judge/VERIFY.md`.

## Infra (not skills except memory)

- **ai-memory:** cross-harness project memory. Install with `/her:memory`; boundaries in `skills/memory/BOUNDARIES.md`. Not vendored in HER.
- pxpipe: token-saving proxy for session context.
- fast-jev-compaction: installed but disabled; not recommended.
- swarm-forge (unclebob): multi-agent CLI. No license in the repo, so nothing copied; ideas only.

Credits and licenses: `NOTICE.md`.
