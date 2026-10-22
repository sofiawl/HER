# HER log

Dated snapshots of how HER looked, newest first. Each entry is copied as it was, not edited.

## 2026-10-19 - snapshot v0.5.0 (from Obsidian `+/Skill issues.md`, commit 73cf217)


Personal Claude Code plugin. Source in `~/HER`, installed as `her@her` (v0.5.0). Every skill is called as `/her:<name>`. Not sure which one fits: `/her:ask-her`.


### What to add
- detect when is will hit session limit, before that hit /handoff 
- Remove compaction jev stuff, apply my own jev compaction that fixes that application
- /organize, organize code, names, repos to make it clear for the purpose (research, cosmos are different from each other)
- make multiple subagents run this per sub /her:lazy .scratch/weight_estimation/subs/01-mass-cli.md → /her:judge → /her:to-pr write sub (there should be also someone to verify and follow the QA instructions) (actually, to-pr write should do this alone without me telling it explictly to do that) (but review that, it should not take toooo long to be done)
- I want a way for my skills learn from their own mistakes that i correct them, maybe not a skill but a autolearn rule but before asking me if it can be updated (recognize that it did some shitty thing or that i did not like and asking for updating)
- update teach to add what i wrote as the explanation back to it into some obsidian vault (), i do not want the current tech it is too complext and produces much content. I want it to explain to me in the chat, then ask me a few questioning so that i can fixate my knowledge then what i write as response (or the general explanation given by me) is written into a new obsidian file that links everything that i asked /teach 
- if i /grilling it directs to matt-grilling but i need her grilling
- a skill validator or reviewer, a precaution to unbloat the skills, if they are getting too big or they are not working for their porpuse on old sessions or they are being wrongly used or if i need a suggestion to make them better. This will be the expert that does that


- Where can i use jev too? Explore other options to use jev
### Rules (always on)

Loaded at every session start from `~/HER/rules/RULES.md`.

1. **Verify my writing**: every reply ends with a `Writing check:` line fixing the English in my last message.
2. **Never comment in code**: names and structure carry the meaning, explanations go in chat.
3. **No em dash, no en dash, no emojis**: only exception is the PR template shortcodes.
4. **Professor and helper at once**: Claude does the work and explains the key decision in 1 or 2 sentences; deeper study goes to `/her:teach`.
5. **Nudge toward HER skills**: when a request fits a skill I did not call, the reply opens with `HER fit: /her:<name>`.
6. **Delegate to the right model**: independent, reading-heavy or parallel chores go to subagents on the model that fits (table below). Each skill has its own `## Subagents` section.

### Talking modes

| Mode | How it talks |
|---|---|
| professor | Explains the reasoning, defines new terms, small examples |
| caveman | Terse, no filler, technical terms and numbers exact |
| adhd | Next action first, numbered steps, max 5 items, one next action under 2 minutes |

`/her:caveman` and `/her:adhd` turn a mode on for the whole session ("normal mode" turns it off).

### Skills

- learn (professor)
	- `/her:understand` -> chat session inside each repo to ask anything about the project, backed by the Understand-Anything graph when it exists
	- `/her:teach` -> stateful teaching workspace with learning checks (3 to 5 per lesson) and spaced review
- research (professor)
	- `/her:last30days` -> what people said in the last 30 days, wraps the last30days plugin plus a skeptical readback
	- `/her:research` -> cited, primary-source research note ranked by trust
	- `/her:prototype` -> throwaway prototype that answers one design question (logic or UI variants)
	- `/her:report` -> Kinebot LaTeX report in `~/kinebot-latex-templates/relatorios/` from a kinebot-research folder; ranks results in a claim ledger, I approve, then it writes and compiles
- plan code (professor)
	- `/her:diagram` -> small Mermaid-first diagram that answers one question
	- `/her:grilling` -> one question at a time interview on a plan
	- `/her:debate` -> argue with me to discover the best decision, ends in a decision record
- produce code (caveman)
	- `/her:lazy` -> least code that solves the task (ladder from ponytail)
	- `/her:to-pr` -> plans the PR stack (feat, proposal, subs of at most 750 changed lines, additions plus deletions, each testable) and writes every description with my template and voice; replaced to-tickets
	- `/her:judge` -> picks the metrics that matter for the project, measures before and after, gives a verdict (ship, fix first, needs discussion); holds the verification gate `VERIFY.md` (from superpowers)
- optimization (caveman)
	- `/her:caveman`
	- infra, not HER skills: pxpipe (token proxy, `claudex` alias) and [fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction)
- unbloat (adhd)
	- `/her:adhd` -> next action first
	- `/her:handoff` -> compacts the session into a handoff doc plus a resume prompt
- her (adhd)
	- `/her:ask-her` -> router that picks the skill and names the exact command; triggers on its own

### Models per chore

| Model | Cost in/out per 1M | Use for |
|---|---|---|
| Haiku 4.5 | $1 / $5 | Mechanical, zero decision: inventory, grep, versions, installs, copying, running a known command |
| Sonnet 5 | $2 / $10 | Moderate judgment: explore code, run builds and tests and interpret failures, read sources |
| Opus 5.5 | $4 / $20 | Deep work: multi-file design, long writing in my voice (PR descriptions, reports), synthesis |
| Fable 5.1 | $10 / $50 | Risk and final say: risky decisions, final diff review, verdicts, opening PRs |

Cheapest tier first, one tier up if it fails; independent chores run in parallel; a subagent's report is a claim until its checks are rerun.

### Main flows

- New repo: `/her:understand` -> `/her:teach` for what deserves study
- New feature: `/her:grilling` -> `/her:debate` on trade-offs -> `/her:diagram` -> `/her:to-pr plan` -> `/her:lazy` per sub -> `/her:judge` -> `/her:to-pr write`
- Research: `/her:research` or `/her:last30days` -> `/her:prototype` -> `/her:report`
- Context overload: `/her:handoff`, `/her:caveman`, `/her:adhd`

### Sources

| Skill                                                                                               | What it is                                                                                                                                                                                      | Where to use it                                                                   |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [obra/superpowers](https://github.com/obra/superpowers)                                             | An agentic skills framework & software development methodology that works.                                                                                                                      | verification-before-completion became `judge/VERIFY.md`, shared with `/her:to-pr` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)                               | Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote                                                                                    | `/her:lazy`                                                                       |
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)                                 | Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph                                                                                              | Not used, overlaps Understand-Anything                                            |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)                                   | Viral skill + proxy for coding agents that cuts 65% of tokens by talking like a caveman.                                                                                                        | `/her:caveman` (core skill only, no proxy)                                        |
| [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)                   | Turn any code into an interactive knowledge graph you can explore, search, and ask questions about                                                                                              | `/her:understand` (optional plugin)                                               |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)                           | AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - then synthesizes a grounded summary                                                           | `/her:last30days` (wraps the plugin)                                              |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)                                         | A skill to stop your coding agent from burying the answer. ADHD-friendly output.                                                                                                                | `/her:adhd`                                                                       |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)         | 165 ready-to-use validated skills plus 100+ scientific databases covering biology, chemistry, medicine, and drug discovery                                                                      | Surveyed for `/her:report`, not installed                                         |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)                     | Editorial diagram design for Claude Code, Codex, and Pi. Self-contained HTML + SVG. No shadows. No Mermaid slop.                                                                                | Not used, `/her:diagram` is Mermaid-first                                         |
| [unclebob/swarm-forge](https://github.com/unclebob/swarm-forge)                                     | SwarmForge coordinates AI agents in isolated git worktrees and tmux sessions.                                                                                                                   | Not used, rule 6 subagents cover delegation                                       |
| [ask-matt](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md)     | Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.                                                                                                | `/her:ask-her` (structure only)                                                   |
| [to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md) | Break any plan, spec, or conversation into a set of tracer-bullet tickets, each declaring its blocking edges.                                                                                   | Merged into `/her:to-pr`                                                          |
| [prototype](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md)   | Build a throwaway prototype to answer a design question, either a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route. | `/her:prototype`                                                                  |
| [research](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md)     | Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo, run as a background agent.                                             | `/her:research`                                                                   |
| [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)    | Interview the user relentlessly about a plan, decision, or idea until every branch of the design tree is resolved.                                                                              | `/her:grilling`                                                                   |
| [handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)      | Compact the current conversation into a handoff document so another agent can continue the work.                                                                                                | `/her:handoff`                                                                    |
| [teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md)          | Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.                                                                     | `/her:teach`                                                                      |
