# HER

My personal agent kit for coding assistants: markdown skills, always-on rules, and an orchestrator that works no matter which model is on the other end. HER does not belong to Anthropic or Claude Code. Skills talk in **tiers** (`haiku`, `sonnet`, `opus`); your harness maps those to whatever models you have (Claude, GPT, Gemini, Grok, Composer, …).

Claude Code gets a first-class **plugin** (`her@her`, skills as `/her:<name>`). **Cursor** gets the same skills, orchestrator agents, and rules via one install script. The portable core is just files in this repo.

This is **opinionated and machine-local**. It names me, my Obsidian vault, Kinebot report paths, and Kineloop habits. Forking? [Local environment (change these)](#local-environment-change-these) first.

## What you get

| Layer | Path | Role |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | Harness-agnostic workflows (invoke as `/her:<name>` on Claude Code, `her-<name>` skill on Cursor) |
| Rules | `rules/RULES.md` | Always on: writing check, no code comments, modes, subagents, autolearn, grilling, commits and Kineloop |
| Hooks | `hooks/` | **Claude Code only:** SessionStart loads rules; UserPromptSubmit nudges `/her:handoff` |
| Orchestrator | `orchestrator/` | `her` CLI: ledger and guard rails; plans set `host` to `claude` or `cursor` |
| PR voice | `skills/to-pr/VOICE.md`, `TEMPLATE.md` | How my PRs sound |
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

## Skills

| Group | Skill | Mode | What it does |
|---|---|---|---|
| learn | `/her:understand` | professor | Chat about the current repo via Understand-Anything |
| learn | `/her:teach` | professor | Explain in chat, one understanding line, 1 to 3 checks, append to my teach note |
| research | `/her:last30days` | professor | What people said in the last 30 days (wraps last30days) |
| research | `/her:research` | professor | Cited, primary-source research note |
| research | `/her:prototype` | professor | Throwaway prototype for one design question |
| research | `/her:report` | professor | Kinebot LaTeX report from a kinebot-research folder |
| plan code | `/her:diagram` | professor | Small Mermaid-first diagrams |
| plan code | `/her:grill-me` | professor | User-only one-question-at-a-time interview (summary + debate handoff) |
| plan code | `/her:grilling` | professor | Model-fired rounds when a decision is unclear |
| plan code | `/her:debate` | professor | Argues against me to find the best decision, ends with a decision record |
| produce code | `/her:lazy` | caveman | Minimum code that works |
| produce code | `/her:judge` | caveman | Metrics before and after, verification gate |
| produce code | `/her:to-pr` | caveman | PR stack plan and write (thin self-verify on write) |
| optimization | `/her:caveman` | caveman | Terse mode toggle |
| unbloat | `/her:adhd` | adhd | Next-action-first mode toggle |
| unbloat | `/her:handoff` | adhd | Compacts the session into a handoff doc |
| unbloat | `/her:organize` | adhd | Purpose taxonomy for repos, folders and names |
| orchestrate | `/her:her` | adhd | Multi-step pipeline in this chat (`/her <request>`) |
| her | `/her:ask-her` | adhd | Router: which HER skill fits now |

Not sure which skill fits: `/her:ask-her`.

## Main flows

- **Multi-step feature or card:** `/her ML-86 fix the thing` (or `/her:her`) when I want grilling, plan, subagents, and review in one thread. Smaller jobs: pick skills directly.
- **Idea to ship (manual):** `/her:grill-me` → `/her:debate` → `/her:diagram` → `/her:to-pr plan` → `/her:lazy` per sub → `/her:to-pr write` (add `/her:judge` when risky or perf). Agent may auto-fire `/her:grilling` when a plan-code decision is missing.
- **New repo:** `/her:understand` then `/her:teach` for concepts worth keeping.
- **Research write-up:** `/her:research` or `/her:last30days` → `/her:prototype` → `/her:report`.
- **Context overload:** `/her:handoff`, `/her:caveman`, `/her:adhd`.

## Install (this machine)

Source repo: `~/HER` (`/home/sofia/HER`). Version: `.claude-plugin/plugin.json` (currently **0.5.0**).

Pick the harness you use day to day (many people run both):

| Harness | Skills | Always-on rules | Handoff nudge hook |
|---|---|---|---|
| **Claude Code** | `claude plugin install her@her` | `hooks/hooks.json` cats `rules/RULES.md` at session start | `hooks/context-handoff-nudge.sh` |
| **Cursor** | `install-cursor-skills.sh` → `~/.cursor/skills/her-*` | same script → `~/.cursor/rules/her.mdc` | not wired yet; run `/her:handoff` yourself or add your own hook |
| **Other** | copy or symlink `skills/` into whatever your tool expects | paste or link `rules/RULES.md` | bring your own |

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

Skills show up as `her-<name>` (e.g. `her-lazy`). Orchestrator steps use `her-implementer`, `her-reader`, `her-reviewer`. Model slugs for rule 6 live in `rules/RULES.md`; defaults and overrides in `her config` / `~/.her/config.toml`.

You may also see HER via Claude plugin cache (`~/.claude/plugins/cache/her/her/<version>/`) or `~/.agents/skills/`. Prefer the HER copy from this repo so you are not on a stale cache.

## Local environment (change these)

Everything below is **Sofia-local or machine-local**. Another person on another machine should change or delete these before treating HER as theirs.

### 1. Identity and voice

| Where | What | What to do on another machine |
|---|---|---|
| `.claude-plugin/plugin.json` | `author.name`: Sofia Lima | Your name and description |
| `rules/RULES.md` | Addresses "Sofia"; writing-check for my English | Rename or drop rule 1 |
| Almost every `skills/*/SKILL.md` | Triggers and prose say "Sofia" | Search-replace or ignore |
| `skills/to-pr/VOICE.md`, `TEMPLATE.md` | My PR tone, GIF habit, tracker URL rules | Your team's PR voice |
| `skills/report/SKELETON.tex` | `\reportauthor{Sofia Wamser Lima}` | Your author line |
| `skills/report/STYLE.md` | Kinebot ABNT / pt-BR | Your style or skip `/her:report` |

### 2. Absolute and home paths (must change)

| Where | Hardcoded path | Purpose |
|---|---|---|
| `skills/teach/SKILL.md` | `/home/sofia/ObsidianPipa/Efforts/On/skill issue.md` | Where `/her:teach` appends |
| `skills/debate/SKILL.md` | `~/ObsidianPipa/+/` | Default decision records |
| `skills/last30days/SKILL.md` | `~/ObsidianPipa/+/<Title>.md` | Optional digest note |
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

HER does not install these. They are assumed or documented for my setup:

| Piece | Role | Another machine |
|---|---|---|
| Understand-Anything | Optional graph for `/her:understand` | Install only if you want it |
| last30days | Required for `/her:last30days` | Install + API keys |
| `mattpocock-skills` | Other Matt skills; HER owns grill-me / grilling | Prefer `/her:…`; avoid duplicate copies |
| pxpipe | Personal token proxy | Optional |
| fast-jev-compaction | Installed but **disabled** | Do not enable without reading risks |

```bash
claude plugin marketplace add Egonex-AI/Understand-Anything
claude plugin install understand-anything@understand-anything

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
5. Retarget Obsidian paths in `debate`, `last30days`, and `NOTES.md`.
6. Retarget or disable `/her:report` (LaTeX paths, author, ABNT / pt-BR).
7. Replace `to-pr` VOICE + TEMPLATE with your team's.
8. Adjust rule 6 and `~/.her/config.toml` model lists for your harness and account.
9. Set `HER_CONTEXT_WINDOW`, `HER_HANDOFF_THRESHOLD`, and `HER_LIMIT_THRESHOLD` for your models and statusline.
10. `claude plugin marketplace update her` and open a new session.

## Rules (always on)

Loaded from `rules/RULES.md` at SessionStart:

1. Writing check on my last message (Sofia-specific).
2. No comments in code you write.
3. No em dash, en dash, or emoji (PR template shortcodes excepted).
4. Do the work; explain the why briefly; deeper study → `/her:teach`.
5. Nudge unused HER skills with `HER fit: /her:<name>`.
6. Delegate to the right model tier / Cursor slug.
7. Autolearn: on behavior corrections, propose a patch and ask before writing.
8. Uncertain decisions → suggest or auto-fire `/her:grilling` (see rule text).
9. Commits, branches, Conventional Commits, Kineloop URLs and pt-BR card text (see rule text).

## Layout

```
HER/
  .claude-plugin/plugin.json
  hooks/hooks.json
  hooks/context-handoff-nudge.sh
  rules/RULES.md
  orchestrator/              # her CLI, Cursor agents, tests
  skills/<skill>/SKILL.md    # plus companions (VERIFY, TEMPLATE, VOICE, report kit, …)
  NOTICE.md
  README.md
```

## Infra / later (not skills)

- pxpipe: token-saving proxy for session context.
- fast-jev-compaction: installed but disabled; native compaction plus `/her:handoff` is enough for me.
- swarm-forge (unclebob): multi-agent CLI. No license in the repo, so nothing copied; ideas only.

Credits and licenses: `NOTICE.md`.
