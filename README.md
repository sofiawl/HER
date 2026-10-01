# HER

Personal Claude Code plugin of skills and always-on rules. Packaged as `her@her`.
Invoke skills as `/her:<name>`. Rules load on every session start via `hooks/hooks.json`.

This repo is **opinionated and machine-local**. Skills, rules, and paths name Sofia,
her Obsidian vault, Kinebot report tooling, and Cursor model slugs. If you clone it
onto another machine or for another person, treat the section
[Local environment (change these)](#local-environment-change-these) as a checklist
before you rely on the plugin.

## What you get

| Layer | Path | Role |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | User or model invoked workflows (`/her:<name>`) |
| Rules | `rules/RULES.md` | Always on: writing check, no code comments, modes, subagents, autolearn, grilling |
| Hooks | `hooks/` | SessionStart loads rules; UserPromptSubmit nudges `/her:handoff` when context is high |
| PR voice | `skills/to-pr/VOICE.md`, `TEMPLATE.md` | How PRs are written |
| Report kit | `skills/report/*` | Kinebot LaTeX report pipeline |
| Credits | `NOTICE.md` | Upstream MIT sources |

Talking modes (set per skill): **professor**, **caveman**, **adhd**. Session toggles:
`/her:caveman`, `/her:adhd` (say `normal mode` to clear).

## Skills

| Group | Skill | Mode | What it does |
|---|---|---|---|
| learn | `/her:understand` | professor | Chat about the current repo, backed by the Understand-Anything knowledge graph |
| learn | `/her:teach` | professor | Explain in chat, one understanding line, 1 to 3 checks, append to the teach effort note |
| research | `/her:last30days` | professor | What people said in the last 30 days (wraps last30days) |
| research | `/her:research` | professor | Cited, primary-source research note |
| research | `/her:prototype` | professor | Throwaway prototype that answers one design question |
| research | `/her:report` | professor | Kinebot LaTeX research report from a kinebot-research folder |
| plan code | `/her:diagram` | professor | Small Mermaid-first diagrams |
| plan code | `/her:grill-me` | professor | User-only one-question-at-a-time interview (summary + debate handoff) |
| plan code | `/her:grilling` | professor | Model-fired round-based interview when a decision is unclear |
| plan code | `/her:debate` | professor | Argues against you to find the best decision, ends with a decision record |
| produce code | `/her:lazy` | caveman | Laziest senior dev: minimum code that works |
| produce code | `/her:judge` | caveman | Metrics before and after, verification gate |
| produce code | `/her:to-pr` | caveman | PR stack plan and write (thin self-verify on write) |
| optimization | `/her:caveman` | caveman | Terse mode toggle |
| unbloat | `/her:adhd` | adhd | Next-action-first mode toggle |
| unbloat | `/her:handoff` | adhd | Compacts the session into a handoff doc |
| unbloat | `/her:organize` | adhd | Purpose taxonomy for repos, folders and names |
| her | `/her:ask-her` | adhd | Router: which HER skill to use now |

Not sure which skill fits: `/her:ask-her`.

## Main flows

- **New repo:** `/her:understand` then `/her:teach` for concepts worth keeping.
- **New feature:** `/her:grill-me` → `/her:debate` → `/her:diagram` → `/her:to-pr plan` → `/her:lazy` per sub → `/her:to-pr write` (add `/her:judge` when risky or perf). Agent may auto-fire `/her:grilling` in plan-code when a decision is missing.
- **Research write-up:** `/her:research` or `/her:last30days` → `/her:prototype` → `/her:report`.
- **Context overload:** `/her:handoff`, `/her:caveman`, `/her:adhd`.

## Install (this machine)

Plugin source lives at `~/HER` (absolute: `/home/sofia/HER`). Claude Code marketplace entry points at that directory.

```bash
claude plugin marketplace add ~/HER
claude plugin install her@her
```

After editing skills or rules:

```bash
claude plugin marketplace update her
```

Then start a new session (hooks and skill text load from the plugin root).

### Cursor note

Cursor can also pick up skills from `~/.agents/skills/` and from enabled Claude plugins.
HER lives under Claude's plugin cache when installed (`~/.claude/plugins/cache/her/her/<version>/`).
Prefer `/her:<name>` so the HER copy wins over any leftover Matt Pocock skills with the same short name.

## Local environment (change these)

Everything below is **Sofia-local or machine-local**. Another person on another machine should change or delete these before treating HER as theirs.

### 1. Identity and voice

| Where | What | What to do on another machine |
|---|---|---|
| `.claude-plugin/plugin.json` | `author.name`: Sofia Lima; description says Sofia | Your name and description |
| `rules/RULES.md` | Addresses "Sofia" everywhere; writing-check for her English | Rename to your name, or drop / rewrite rule 1 if you do not want writing checks |
| Almost every `skills/*/SKILL.md` | Triggers and prose say "Sofia" | Search-replace the owner name, or keep and ignore |
| `skills/to-pr/VOICE.md`, `TEMPLATE.md` | Sofia's PR tone, GIF habit, tracker URL rules | Replace with your team's PR voice and template |
| `skills/report/SKELETON.tex` | `\reportauthor{Sofia Wamser Lima}` | Your author line |
| `skills/report/STYLE.md` | Derived from Kinebot ABNT / pt-BR reports | Point at your report style or skip `/her:report` |

### 2. Absolute and home paths (must change)

| Where | Hardcoded path | Purpose |
|---|---|---|
| `skills/teach/SKILL.md` | `/home/sofia/ObsidianPipa/Efforts/On/skill issue.md` | Where `/her:teach` appends lessons |
| `skills/debate/SKILL.md` | `~/ObsidianPipa/+/` | Default place for decision records when not in a repo |
| `skills/last30days/SKILL.md` | `~/ObsidianPipa/+/<Title>.md` | Optional digest note |
| `skills/report/SKILL.md` | `~/kinebot-latex-templates/relatorios/` | Compiled report output |
| `skills/report/SKILL.md` | example `~/kinebot-research/...` | Research folder examples |
| `skills/report/STYLE.md` | `~/kinebot-latex-templates/relatorios/` | Style reference reports |
| `NOTES.md` | `~/ObsidianPipa/+/Is fast-jev-compaction worth it.md` | Personal research pointer |

Also change the **sample format** at the top of your teach target file if you rename it; `/her:teach` expects that file's sample shape (title, one understanding line, bold questions, answer bullets, optional correction).

### 3. Hooks and shell environment

| Knob | Default | Meaning |
|---|---|---|
| `HER_HANDOFF_THRESHOLD` | `75` | Context % that triggers a one-shot `/her:handoff` nudge |
| `HER_CONTEXT_WINDOW` | `1000000` | Assumed window size for the nudge math (Sofia often runs `opus[1m]`) |
| `TMPDIR` | system temp | Stamp file so the nudge fires once per session |
| `jq` | required on PATH | Hook exits quietly if missing |

On a 200k-context machine, set `HER_CONTEXT_WINDOW=200000` (or your real window) or the nudge may never fire. The hook estimates tokens from the transcript; it does not read the statusline `used_percentage` field.

Hook wiring: `hooks/hooks.json` (portable). Script: `hooks/context-handoff-nudge.sh` (portable logic; defaults are local).

### 4. Model table (Cursor vs Claude Code)

`rules/RULES.md` rule 6 maps HER tiers (`haiku` / `sonnet` / `opus` / `fable`) to **Cursor** `model` slugs (`composer-2.5-fast`, `claude-sonnet-5-5-high`, …).

- On **Cursor**: keep or edit the slug column to match models available on that account.
- On **Claude Code only**: replace the Cursor slug column with whatever your Task / subagent API accepts (often bare `haiku`, `sonnet`, `opus`), or drop the slug column and keep tier names only.

### 5. External plugins and infra (optional, not shipped)

HER does not install these. They are assumed or documented for Sofia's setup:

| Piece | Role | Another machine |
|---|---|---|
| Understand-Anything | Optional graph for `/her:understand` | Install only if you want it |
| last30days | Required for `/her:last30days` | Install + its own API keys |
| `mattpocock-skills` | Still enabled here for other Matt skills; HER owns `grill-me` / `grilling` | Prefer `/her:…` for interviews; avoid duplicate agent skill copies |
| pxpipe | Personal token proxy | Optional |
| fast-jev-compaction | Installed but **disabled**; not recommended | Do not enable without reading the risks |

Install wrappers (if you want them):

```bash
claude plugin marketplace add Egonex-AI/Understand-Anything
claude plugin install understand-anything@understand-anything

claude plugin marketplace add mvanhorn/last30days-skill
claude plugin install last30days@last30days-skill
```

### 6. Repo root leftovers (not part of the plugin runtime)

These are old `/her:teach` demo artifacts and personal notes. Safe to ignore or delete on a fresh fork:

- `MISSION.md`, `RESOURCES.md`, `GLOSSARY.md`, `NOTES.md`
- `learning-record/`, `lessons/`

SessionStart only cats `rules/RULES.md`. It does not load those files.

### 7. Quick fork checklist

1. Copy or clone HER to a path you control; point the Claude marketplace at that path (not `/home/sofia/HER`).
2. Edit `.claude-plugin/plugin.json` author and description.
3. Replace owner name in `rules/RULES.md` (and drop writing-check if unwanted).
4. Point `skills/teach/SKILL.md` at your own markdown file; put the sample format at the top of that file.
5. Retarget or remove Obsidian paths in `debate`, `last30days`, and `NOTES.md`.
6. Retarget or disable `/her:report` (LaTeX paths, author, ABNT / pt-BR style).
7. Replace `to-pr` VOICE + TEMPLATE with your team’s.
8. Adjust rule 6 model slugs for your harness (Cursor vs Claude Code).
9. Set `HER_CONTEXT_WINDOW` / `HER_HANDOFF_THRESHOLD` for your model window.
10. `claude plugin marketplace update her` and open a new session.

## Rules (always on)

Loaded from `rules/RULES.md` at SessionStart:

1. Writing check on the user’s last message (Sofia-specific).
2. No comments in code you write.
3. No em dash, en dash, or emoji (PR template shortcodes excepted).
4. Do the work and explain the why briefly; deeper study → `/her:teach`.
5. Nudge unused HER skills with `HER fit: /her:<name>`.
6. Delegate to the right model tier / Cursor slug.
7. Autolearn: on behavior corrections, propose a patch and ask before writing.
8. Uncertain decisions → suggest or auto-fire `/her:grilling` (see rule text).

## Layout

```
HER/
  .claude-plugin/plugin.json
  hooks/hooks.json
  hooks/context-handoff-nudge.sh
  rules/RULES.md
  skills/<skill>/SKILL.md   # plus companions (VERIFY, TEMPLATE, VOICE, report kit, …)
  NOTICE.md
  README.md
```

## Infra / later (not skills)

- pxpipe: token-saving proxy for session context.
- fast-jev-compaction: plugin installed but disabled in Claude settings; not recommended (native compaction plus `/her:handoff`).
- swarm-forge (unclebob): multi-agent orchestration CLI. No license in the repo, so nothing is copied; ideas only.

Credits and licenses: see `NOTICE.md`.
