---
name: pr-review
description: >
  PR review on repos with CI + ai-review: stack-aware deep pass on singles and
  stack-top, light pass on lower subs; architecture, placement, cleanup, QA;
  fallback checklist when automation missing; inline only (empty body).
  GitHub only, not Kineloop. Triggers: "/her:pr-review", "review this PR",
  "PR review", "gh pr review", "leave review comments on".
argument-hint: "[PR number or URL]"
---

Mode: adhd

Follow `references/pr-review.md` end to end. Comment voice: `COMMENT-VOICE.md`. Before posting to GitHub, run `../humanizer/PASS.md` on each inline (`pr-review-inline`); review `body` stays `""`.

**Audiences:** GitHub inline threads only (`event` for verdict). Chat = Sofia (recap, stack routing, producer pass, QA, screenshot command list, her follow-ups).

**Next action first:** worktree → parse stack depth → CI + bot baseline → layer maps → QA → §6 or §7 pass → inlines → `# Evidence` via `gh` if approving → post review → force-remove worktree → chat report.

Do not commit, push, or open Kineloop issues unless Sofia asks outside this skill.

**Not for Sofia's own PRs.** If the PR author is Sofia (or the branch is hers from a HER implementer run), do not use this skill as a substitute for a teammate review. Tell her to assign a reviewer; never `gh pr review --approve` or merge on her stack (HER rule 10).

## Subagents

Model tiers: HER rule 6. Cursor slugs per chore: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Fetch PR metadata, stack links, diff stats | `haiku` | Before deep read |
| Parse proposal merge-order table, stack-top # | `haiku` | When reviewing a sub |
| Architecture pass (layer map, grep dup/dead code) | `sonnet` | Per area in parallel |
| Run PR QA + deep 1–2 commands (stack-top / single only) | `sonnet` | In worktree |
| Draft inlines + stack PR routing | `opus` | Diff + QA + bot context |
| Post `gh api` review + `gh pr comment` evidence | main | Sofia's account |
