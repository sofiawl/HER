---
name: her
description: >
  Run the HER orchestrator in this chat, superpowers-style: grill Sofia, write
  a plan, then act as controller and dispatch one fresh subagent per step with
  a reviewer after each writing step, using HER skills. Triggers: "run the
  orchestrator", "her pipeline", "orchestrate this", "/her <what to do>", or
  /her:her.
argument-hint: "[<what to do> | <run id>]"
---

Mode: adhd

You are the controller. Everything happens in this chat: no detached process,
no dashboard, no second terminal. The `her` CLI is your ledger and your guard
rails: it validates the plan, checks branches and dirty trees, writes the
briefs and stores every report. Sofia never types `her` commands. The same
skill runs in Cursor as `her-her`.

You never do step work yourself. Each step goes to a fresh subagent that
starts with a clean context and gets only its brief.

## With no argument

Run `her runs` and show the recent runs with their phase. Offer to resume one.

## With a run id

Resume it: `her status <id>`, then continue the loop below from where the
ledger says it is. The ledger is the memory, not this chat.

## With a request

1. Create the run. Pipe the request verbatim with a quoted heredoc:

   ```bash
   her new <<'EOF'
   <request exactly as Sofia wrote it>
   EOF
   ```

2. Run `her guide` and read it all: skills, models, planning rules, flow,
   schema.
3. If the request names a Kineloop card (like `ML-86`), read it with the
   Kineloop tools (`kineloop_get_issue`). Read the repos involved. Facts are
   your job: dispatch cheap lookup subagents while you grill.
4. Grill Sofia here, following `skills/grilling/SKILL.md`: rounds, frontier,
   numbered questions with a recommendation. When the frontier is empty and she
   confirms, write `<path>/decisions.md`, one bullet per decision: question,
   answer, why.
5. Write `<path>/plan.json` per the schema. Set `host` to the app you run in
   (`claude` or `cursor`) and `card` when there is one. Run `her check <id>`
   and fix the plan until it passes.
6. Show Sofia the plan from `her check` and any missing skills. Suggest
   creating each missing skill afterwards, never silently. Wait for her yes.
7. On approval run `her approve <id>`. With a card, move it to started.
8. Run the loop.

## The loop

Repeat until `her next <id>` prints `"finished": true`.

1. `her next <id>` lists ready steps. Dispatch at most the configured number in
   parallel, in one message. `her next` already keeps writing steps in the
   same repo one at a time.
2. For each ready step, `her begin <id> <sid>` checks the tree and branch and
   prints `model`, `readonly` and, after `---`, the brief. If it refuses, tell
   Sofia why and stop for that step.
3. Dispatch the implementer: a fresh subagent on that model, with the brief
   pasted verbatim. Nothing else from this chat goes in.
   - Claude Code: the `Agent` tool, `model` set to the step tier
     (`haiku`, `sonnet`, `opus`).
   - Cursor: the `her-implementer` subagent, or `her-reader` when
     `readonly` is true, naming the step model.
4. Pipe its reply to `her finish <id> <sid> <STATUS>` with the status from its
   last line (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`). Use
   `FAILED` when it crashed or ended without a status.
5. A writing step comes back as `review`. Run `her review-brief <id> <sid>`
   and dispatch a fresh read-only reviewer on `opus` (Cursor: `her-reviewer`)
   with that brief. Pipe its reply to `her review <id> <sid> approve` or
   `changes`, matching its last line.
   - `changes`: `her begin` again and dispatch a fresh implementer. The brief
     now carries the review. After 3 rounds the step is blocked.
6. A blocked step goes to Sofia. Show her the reason exactly as written, with
   the step id. Never answer for her. With her reply, run
   `her begin <id> <sid> --note "<her reply>"` and dispatch again. If the step
   blocked because the model was not strong enough, move it up a tier in
   `plan.json` and run `her check` first.
7. Between rounds, say one line of progress: which steps finished, which run.

## Finish

Run `her summary <id>` and report in chat: what each step did, the judge
verdicts, PR links, open questions, missing skills. With a card, comment the
summary on it (`kineloop_add_issue_comment`) and move it to review when PRs are
open.

## Later

`her status <id>` and `her show <id> <sid>` show a step report, review and
verdict. `her config` shows the tier to model mapping.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Look up facts in the repos involved | `haiku` for a lookup, `sonnet` when it needs reading code | Background while the grilling round continues |
| Grilling, plan writing, approval, the loop | main | Needs the conversation |
| A step | per `plan.json` | Fresh implementer, brief from `her begin` |
| Review of a writing step | `opus` | Fresh read-only reviewer, brief from `her review-brief` |
