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

Follow `references/pr-review.md` end to end. Comment voice: `COMMENT-VOICE.md`.

**Next action first:** worktree → load checklist → read existing reviews → diff → comment → post → remove worktree → report verdict to Sofia.

Do not commit, push, or open Kineloop issues unless Sofia asks outside this skill.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Fetch PR metadata, existing reviews, diff stats | `haiku` | Before deep read |
| Read changed files against checklist | `sonnet` | Per area or package in parallel |
| Draft comments + summary | `opus` | Needs full picture for ISSUE vs SUGGESTION |
| Post `gh api` review | main | Needs Sofia's account; confirm before REQUEST_CHANGES if borderline |
