---
name: to-pr
description: Plan a feature as a stack of PRs (feat, proposal, subs of at most 750 changed lines each) and write every PR description with Sofia's template and voice. Use when Sofia says "/her:to-pr", "split into PRs", "break this down", "slice this", "plan the stack", "write the PR", "PR description", "open the PR", "update the stack table", or has a plan ready to implement or a branch ready to ship.
argument-hint: "[plan <source> | write <feat|proposal|sub|single> [branch] | update]"
---

# /her:to-pr

Mode: caveman (chat only). The PR text itself follows VOICE.md, never caveman.

Two jobs: cut a feature into a reviewable PR stack, then write each PR so reviewing it is pleasant.

Pick the job from the argument. No argument: a plan or idea in the conversation means `plan`, commits on the current branch mean `write`. Unclear: ask one question.

## The stack

```
main <- feat/<ID>_<slug>            feat: the umbrella, bottom of the stack
          <- proposal/<ID>_<slug>   proposal: one slice of the feature, integration branch
               <- sub 1 <- sub 2 <- sub 3 ...   subs: the reviewable pieces
```

- **feat**: the whole feature. Targets `main`. Almost no code, mostly the why and the future scope. A feature can have several proposals over time.
- **proposal**: one part of the feature that ships as a unit. Targets the feat branch. Holds the merge-order table and the graveyard. Review happens on its subs; the proposal gets a final look once all subs are in.
- **sub**: one PR, at most 750 changed lines, independently testable, tests included. Sub 1 targets the proposal, each next sub targets the previous one. Merged in order.
- **single**: a PR outside any stack (bug fix, small refactor). Same 750 limit.

Branch names, commit messages and ticket URLs: HER rule 9.

`.scratch/` is ignored globally (`~/.config/git/ignore`), so plans and PR description drafts live there and are never committed.

## plan

1. **Gather.** Read the source (argument path, else the conversation) fully. Explore the repo areas it touches: modules, tests, schema, generated files. Use the project's own words.
2. **Decide the level.** New feature: feat + proposal + subs. More work on an existing feat: new proposal + subs. Small work: single, or a proposal with subs if over 750.
3. **Slice subs vertically.** Each sub is a thin path through every layer it needs and works end to end with its own tests. Never split by layer (all DB, then all API). First sub: the thinnest path that proves the design. Pure moves or housekeeping that unblock later subs may be their own sub, placed right before what needs them.
4. **Size.** Size = additions + deletions, what `git diff --shortstat` reports. Everything counts, generated files and lockfiles too. Estimate from files touched and similar past diffs (`git log --shortstat`). Over 750: split again along a behavior seam. Over 600: note the risk. Generated churn alone breaking 750: ask Sofia (own sub, or accept).
5. **Order.** Subs form a line because they stack. Order them so each one only needs what is below it. Name the real dependency behind each position.
6. **Quiz Sofia.** Show the stack: level, branch, title, estimated lines, PR type, depends on. Ask: right granularity, right order, anything to merge, split, drop, any sub not testable alone. Iterate. Write nothing before she approves.
7. **Write the plan** under the repo root:
   - `.scratch/<feature-slug>/stack.md`: the stack diagram, then a table `Order | Branch | Scope | Issue | Est. lines | Type`, then the graveyard (empty at first).
   - `.scratch/<feature-slug>/subs/NN-<slug>.md` per sub, `NN` in stack order: Goal, Scope in/out (and which sub does the out part), Acceptance criteria as checkboxes, How to test with expected results, Depends on, Estimated lines, Type, Issue (Linear ID, blank if none yet).
   Touch nothing else, not even `.gitignore`.
8. **Hand off.** Path of `stack.md` and the first sub. Per sub: `/her:lazy <sub file>`, then `/her:to-pr write sub` (it self-verifies thin). Add `/her:judge` before write for risky or perf subs.

## write

1. **Facts first.** Branch, base, commits (`git log <base>..HEAD`), real size (`git diff --shortstat <base>...HEAD`, files count too), the sub file from `.scratch/` if one exists (planning aid only, never cited in the PR body), linked issue IDs from branch and commits, the judge table if `/her:judge` ran this session.
2. **Ticket link.** Build it from the card ID in the branch or from what Sofia gives: `https://loop.zslippy.com/issue/<CARD>`. Confirm the card ID with her if it is not in the branch name. Never ship a bare `ML-14` / `DES2-xxx`.
3. **Verify.** Apply `../judge/VERIFY.md` before writing any claim: every "N passed", "ruff clean", "expected output" in the PR comes from a command run now, in this session. No fresh evidence: run it, or leave the claim out and tell Sofia. Do this on its own, Sofia does not have to ask.
   - Judge table from this session and no commits since: reuse its numbers, no rerun.
   - No table (or commits landed after it): run the thin gate now. Project tests plus the lint/types checks CI runs (read CI config, Makefile, package scripts), whole target, read exit code and counts. No worktree, no before/after.
   - Full `/her:judge` only if Sofia asks; suggest it when the sub is risky or perf.
   - Gate fails: report real numbers, claim stays out, fix goes back to `/her:lazy`.
4. **Draft** with TEMPLATE.md for the PR level, in the voice of VOICE.md. Language: the language of the repo's recent PRs, English by default. Sub bodies stay direct and short; skip `Things worth knowing` unless TEMPLATE.md's bar is met. Package diagrams go on the proposal (ask Sofia if unsure).
5. **Never invent** screenshots, Figma links, issue IDs or PR numbers. Leave a placeholder like `[screenshot: updated_* fields in the Bruno response]` and list every placeholder for Sofia at the end. The GIF section stays empty, Sofia always picks it herself.
6. **Never put local-only material in the PR body.** No `.scratch/` paths, no uncommitted specs, no local QA records, no "files on my disk" references. Related links must open for a reviewer on a fresh clone or on GitHub.
7. **Save** to `.scratch/<feature-slug>/prs/<level>-<ID>.md` (or `.scratch/prs/<branch>.md` without a plan) and show it. The save path is agent-local; it is not mentioned inside the PR text.
8. **Open** only after Sofia says yes: `gh pr create --base <base> --title "<title>" --body-file <file>`, draft if she asks. Never push or open without her yes.

Title: see TEMPLATE.md Titles. Defaults: `feat: <ID> - <summary>`, `proposal: <ID> - <summary>`, `sub: <ID> - <summary>`. Lowercase type. Subs are never titled `feat:`.

## update

Stack changed (a sub merged, re-cut, canceled, or a new one added): refresh the proposal's merge-order table with real sizes from `gh pr view <n> --json additions,deletions,changedFiles`, move dead PRs to the graveyard with one line on why they died and which PR replaced them, and fix the "Stacked on top of" line in any sub whose base changed. Show the diff of the description, update on GitHub only after her yes (`gh pr edit <n> --body-file <file>`).

## Headless

Prompt says it runs headless under the HER orchestrator: never ask or quiz Sofia (skip the plan quiz, the card confirmation and the open-PR yes). Take decisions from the `decisions.md` path in the prompt. Opening or editing a PR needs a decision there or the task saying so, else only save the draft. Card ID, base branch or granularity missing and not in the branch or decisions: end with `BLOCKED: needs Sofia: <decision>`.

## Hand off

Reply with the saved path, the placeholders Sofia must fill, and the exact `gh` command waiting for her yes.

Decision line: one terse line on the main slicing or framing choice.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Size counts (`git diff --shortstat`), branch creation, stack table updates | `haiku` | Parallel per PR |
| Map the changed files and behaviors, gather test commands and QA steps, run the QA | `sonnet` | Parallel per PR |
| Write each PR description from TEMPLATE.md and VOICE.md | `opus` | One agent per PR, in parallel, each gets VOICE.md and TEMPLATE.md in full |
| Review the stack split and each final diff, then open the PR after Sofia's yes | `opus` | Last, one PR at a time |
