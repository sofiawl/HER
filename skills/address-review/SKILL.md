---
name: address-review
description: >
  Triage open GitHub PR review threads on Sofia's branch: fix or dismiss each
  item, reply in one line, one conventional commit per fix, push. GitHub only.
  Triggers: "/her:address-review", "address review comments", "fix PR feedback",
  "respond to PR review", "answer review comments".
argument-hint: "[PR number or URL]"
---

Mode: caveman

Follow `references/address-review.md` end to end. Thread replies: `REPLY-VOICE.md` via `../humanizer/PASS.md` channel `pr-thread-reply` before each post. Code changes: `/her:lazy` ladder and HER rule 9.

**Next action first:** resolve PR and branch → list **unresolved** threads only → order by blocker severity → for each thread fix or dismiss → commit → push → one-line reply → resolve thread → narrow check → chat summary.

**Author side only.** Use on PRs Sofia (or HER on her branch) opened. Not for reviewing someone else's PR (`/her:pr-review`).

Do not merge, approve, or request review on her behalf (HER rule 10). Do not open Kineloop issues unless she asks outside this skill.

## Subagents

Model tiers: HER rule 6. Cursor slugs per chore: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Fetch PR metadata, unresolved threads, check status | `haiku` | Before edits |
| Implement one thread's fix | `sonnet` | One dispatch per thread when diffs are large or unrelated |
| Dismiss vs fix vs escalate | main | Security, product, or scope: auto-fire `/her:grilling` then continue |
| Final pass over commits and replies | `opus` | Optional when many threads |
