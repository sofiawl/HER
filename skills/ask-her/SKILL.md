---
name: ask-her
description: >
  Router that picks which HER skill fits right now and names the exact command.
  Use proactively whenever Sofia starts a task that a HER skill covers but she
  did not call one: learning, researching, prototyping, planning or debating a
  design, writing code, splitting work into PRs, writing or reviewing a PR,
  measuring a change, handing off, or when she asks "which HER skill", "what
  should I use", "I don't know which skill", "help me pick a skill",
  "/her:ask-her".
---

Mode: adhd

You don't need to remember every HER skill, ask this one instead.

## Full skill list

**learn** (professor)
- `/her:teach`: explain in chat, her one understanding line, 1 to 3 checks, append to `Efforts/On/skill issue.md`.

**research** (professor)
- `/her:research`: primary sources (default), optional last-30-days discourse, or throwaway spike (`sources` / `discourse` / `spike`).

**report** (professor)
- `/her:report`: Kinebot LaTeX report from a kinebot-research folder (ranks results, you approve, then writes and compiles).

**plan code** (professor)
- `/her:grill-me`: user-only one-question-at-a-time interview (summary + debate handoff).
- `/her:grilling`: model-fired round-based interview when a decision is unclear.
- `/her:debate`: argues against Sofia to find the best decision, ends with a decision record.

**produce code** (caveman)
- `/her:lazy`: laziest senior dev, minimum code that works.
- `/her:judge`: picks and measures the metrics that matter, before vs after, verification gate.
- `/her:to-pr`: plans the PR stack (feat, proposal, subs of at most 750 changed lines) and writes each PR in Sofia's template and voice (write self-verifies thin).
- `/her:pr-review`: GitHub PR review from an isolated worktree, inline comments in Sofia's review voice.

**optimization** (caveman)
- `/her:caveman`: terse mode toggle.

**unbloat** (adhd)
- `/her:adhd`: next-action-first mode toggle.
- `/her:handoff`: emergency compact of **this chat** (context/rate-limit nudge); HER next action + suggested skills.
- `/her:memory`: install/wire ai-memory; project wiki vs handoff vs Kineloop vs orchestrator (`BOUNDARIES.md`).

**orchestrate** (adhd)
- `/her:her`: `/her <what to do>` runs the HER orchestrator from this chat (grills you here, writes a plan, then runs each step as a fresh subagent with a reviewer, in this chat).

**her** (adhd)
- `/her:ask-her`: this router.

Infra without a skill, never suggest as a fit: pxpipe, fast-jev-compaction (installed but disabled; not recommended). ai-memory has `/her:memory`.

## Main flows

- **Idea to ship**: `/her:grill-me` to sharpen the idea, then `/her:debate` for
  trade-offs, then `/her:to-pr plan`, then `/her:lazy` per sub, then `/her:to-pr write`
  (thin self-verify). Add `/her:judge` before write for risky or perf subs. Agent
  may auto-fire `/her:grilling` when a plan-code decision is missing.
- **Learning**: `/her:teach` for one concept (appends to `Efforts/On/skill issue.md`).
- **Unknowns**: `/her:research` (sources mode), or `discourse` / `spike` when that fits.
- **Writing up research**: `/her:report` once experiments in a kinebot-research folder are done.
- **Review someone else's PR**: `/her:pr-review <number>`.
- **Context overload**: `/her:handoff` for this thread; `/her:caveman` or `/her:adhd` for reply shape.
- **Cross-session memory**: `/her:memory install` once; hooks capture project work.

## Router behavior

0. Proactive nudge: When her request fits a skill she did not call, start with
   `HER fit: /her:<name>, <why in a few words>.` Then run it or ask "run it?"
   if it writes, installs, posts reviews, or opens anything. Once per task.
1. If the request is clear, answer with the one skill name and exact command.
2. If unclear, ask exactly one short question, do not dump the menu.
3. Always-on HER rules still apply (writing check, no code comments, no em/en dash or emoji, explain the why).

## Subagents

Model tiers and delegation rules: HER rule 6.

None. Routing needs the conversation and is one step. The chosen skill decides its own subagents.
