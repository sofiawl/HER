---
name: ask-her
description: >
  Router that picks which HER skill fits right now and names the exact command.
  Use proactively whenever Sofia starts a task that a HER skill covers but she
  did not call one: learning a repo or concept, researching, prototyping,
  planning or debating a design, diagramming, writing code, splitting work into
  PRs, writing a PR, measuring a change, handing off, or when she asks "which
  HER skill", "what should I use", "I don't know which skill", "help me pick
  a skill", "/her:ask-her".
---

Mode: adhd

You don't need to remember every HER skill, ask this one instead.

## Full skill list

**learn** (professor)
- `/her:understand`: chat about the current repo through its Understand-Anything knowledge graph.
- `/her:teach`: explain in chat, her one understanding line, 1 to 3 checks, append to `Efforts/On/skill issue.md`.

**research** (professor)
- `/her:last30days`: what people said in the last 30 days, wraps last30days.
- `/her:research`: cited primary-source research note.
- `/her:prototype`: throwaway code to answer one design question.
- `/her:report`: Kinebot LaTeX report from a kinebot-research folder (ranks results, you approve, then writes and compiles).

**plan code** (professor)
- `/her:diagram`: small Mermaid-first diagrams.
- `/her:grill-me`: user-only one-question-at-a-time interview (summary + debate handoff).
- `/her:grilling`: model-fired round-based interview when a decision is unclear.
- `/her:debate`: argues against Sofia to find the best decision, ends with a decision record.

**produce code** (caveman)
- `/her:lazy`: laziest senior dev, minimum code that works.
- `/her:judge`: picks and measures the metrics that matter, before vs after, verification gate.
- `/her:to-pr`: plans the PR stack (feat, proposal, subs of at most 750 changed lines) and writes each PR in Sofia's template and voice (write self-verifies thin).

**optimization** (caveman)
- `/her:caveman`: terse mode toggle.

**unbloat** (adhd)
- `/her:adhd`: next-action-first mode toggle.
- `/her:handoff`: compacts the session into a handoff doc.
- `/her:organize`: purpose taxonomy for repos, folders and names (not a refactor).

**orchestrate** (adhd)
- `/her:her`: `/her <what to do>` runs the HER orchestrator from this chat (grills you here, writes a plan, then runs each step as a fresh subagent with a reviewer, in this chat).

**her** (adhd)
- `/her:ask-her`: this router.

Infra, not HER skills, never suggest these as a fit: pxpipe, fast-jev-compaction (installed but disabled; not recommended).

## Main flows

- **Idea to ship**: `/her:grill-me` to sharpen the idea, then `/her:debate` for
  trade-offs, then `/her:diagram`, then `/her:to-pr plan`, then `/her:lazy` per
  sub, then `/her:to-pr write` (thin self-verify). Add `/her:judge` before write
  for risky or perf subs. Agent may auto-fire `/her:grilling` when a plan-code
  decision is missing.
- **Learning**: `/her:understand` first to see how the repo fits together,
  then `/her:teach` for one concept (appends to `Efforts/On/skill issue.md`).
- **Unknowns**: pick `/her:research` for a cited written answer, `/her:last30days`
  for recent chatter, `/her:prototype` for a question only running code can settle.
- **Writing up research**: `/her:report` once the experiments in a kinebot-research
  folder are done; `/her:research` first if the report needs external sources.
- **Context overload**: `/her:handoff` to save state before a break, `/her:caveman`
  when replies feel too wordy, `/her:adhd` when Sofia needs next-action-first shape.

## Router behavior

0. Proactive nudge: Sofia wants to build the habit of using HER skills. When
   her request fits a skill she did not call, start the reply with one line:
   `HER fit: /her:<name>, <why in a few words>.` Then either run that skill
   (if the fit is obvious and it only reads or plans) or ask "run it?" (if it
   writes files, installs or opens anything). Once per task, never nag again
   in the same task, and stay quiet when she is already inside a HER skill.
1. If the request is clear, answer with the one skill name and the exact
   `/her:<name>` command to run, one line each, nothing else needed.
2. If it is not clear which skill fits, ask exactly one short question to
   narrow it, do not list the whole menu back at Sofia.
3. Always check first whether one of the always-on HER rules already covers
   the ask, writing check, no code comments, no em or en dash or emoji,
   explain the why while working, these apply regardless of skill.

## Subagents

Model tiers and delegation rules: HER rule 6.

None. Routing needs the conversation and is one step. The chosen skill decides its own subagents.
