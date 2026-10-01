---
name: her
description: >
  Run the HER orchestrator from this chat. You plan the pipeline (ask-her),
  settle decisions with Sofia (grilling), write a plan, and after she approves
  the CLI runs the steps detached with a live dashboard. Triggers: "run the
  orchestrator", "her pipeline", "orchestrate this", "/her <what to do>", or
  /her:her.
argument-hint: "[<what to do>]"
---

Mode: adhd

Everything happens in this chat. Sofia never types `her` commands and no second
claude session is opened. The same skill is installed in Cursor as `her-her`.

## With no argument

Run `her` and `her runs` through the shell and show the recent runs with their
status. Offer `her watch <id>` to reopen a dashboard.

## With a request

You do steps 1 to 7 yourself. Do not skip a step.

1. Create the run. Pipe the request verbatim through stdin with a quoted
   heredoc so parentheses and multi-line text survive. Capture the id and path.

   ```bash
   her new <<'EOF'
   <request exactly as Sofia wrote it>
   EOF
   ```

2. Run `her guide` and read it: skill catalog, allowed agents, tiers and
   models, planning rules, plan JSON schema.
3. Act as ask-her: decide which HER skills the pipeline needs. Read the repos
   involved yourself. Facts are your job: dispatch cheap subagents for lookups
   when useful.
4. Grill Sofia here in the conversation for every decision that needs her
   judgment. Follow `skills/grilling/SKILL.md`: rounds, frontier, numbered
   questions with a recommendation. Only when the frontier is empty and she
   confirms, write `<path>/decisions.md`, one bullet per decision: question,
   answer, why.
5. Write `<path>/plan.json` following the schema from `her guide`:
   - short `title`
   - steps with `skill`, `tier`, `agent`, `model`, `cwd`, `add_dirs`,
     `writes`, `depends_on` and a self-contained `task`
   - `missing_skills` for work no HER skill covers

   Run `her check <id>`. Fix the plan and recheck until it passes.
6. Show Sofia the rendered plan from `her check` and the missing skills. Ask
   her to approve. For each missing skill, suggest creating it afterwards
   (`/her:grill-me`, then a new `SKILL.md`). Never create one silently.
7. On approval run `her start <id>`. The run goes detached and a live
   dashboard opens in a new Ghostty window. Tell her the id, that
   `her watch <id>` reopens the dashboard and `her stop <id>` stops the run.

## Blocked steps

A step that needs Sofia ends with `QUESTION: ...` and shows as `needs answer`
in `her watch` and `her status` (state `blocked`). When a run has BLOCKED steps,
show Sofia each question exactly as written, with its step id. After she
replies, run `her answer <step_id> "<her reply>"` for her and keep watching the
run. Never answer on her behalf, never rephrase her reply into a decision she
did not make.

## Later

When Sofia asks how it went: run `her status <id>`, `her show <id> <step>`,
read `<path>/summary.md`, and report in chat. Use `her logs <id> <step>` when a
step failed. `her config` shows the tier to model mapping.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Look up facts in the repos involved | `haiku` for a lookup, `sonnet` when it needs reading code | Background while the grilling round continues |
| Grilling, plan writing, approval | main | Needs the conversation |
| The run steps | per `plan.json` | Run by the `her` CLI, not by this chat |
