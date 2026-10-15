---
name: pr-review
description: >
  Review a GitHub pull request from an isolated worktree: repo checklists,
  inline conventionalcomments, short ADHD-shaped comments in Sofia's voice.
  GitHub only, not Kineloop. Triggers: "/her:pr-review", "review this PR",
  "PR review", "gh pr review", "leave review comments on".
argument-hint: "[PR number or URL]"
---

Mode: adhd

Follow `references/pr-review.md` end to end. Comment voice: `COMMENT-VOICE.md`. Before posting to GitHub, run `../humanizer/PASS.md` on summary body and each inline (`pr-review-inline`).

**Audiences:** GitHub summary + inline = author (code review only: verdict, blockers, inline threads). Chat reply = Sofia (QA log, her follow-ups including PR test plan she still runs, environment blockers).

**Next action first:** worktree → load checklist → read existing reviews → diff → **run PR QA (runnable steps)** → draft author-facing GitHub text → post → remove worktree → **chat report to Sofia**.

Do not commit, push, or open Kineloop issues unless Sofia asks outside this skill.

**Not for Sofia's own PRs.** If the PR author is Sofia (or the branch is hers from a HER implementer run), do not use this skill as a substitute for a teammate review. Tell her to assign a reviewer; never `gh pr review --approve` or merge on her stack (HER rule 10).

## Subagents

Model tiers: HER rule 6. Cursor slugs per chore: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Fetch PR metadata, existing reviews, diff stats | `haiku` | Before deep read |
| Read changed files against checklist | `sonnet` | Per area or package in parallel |
| Run runnable QA steps from PR body | `sonnet` | In worktree; return pass/fail per step |
| Draft comments + summary | `opus` | Needs diff + QA evidence for ISSUE vs SUGGESTION |
| Post `gh api` review | main | Needs Sofia's account; confirm before REQUEST_CHANGES if borderline |
