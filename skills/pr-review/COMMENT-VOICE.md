# How Sofia's PR review comments sound

**Two audiences.** **Inline comments** on the diff are the only author-facing review text on GitHub. **Chat to Sofia** holds recap, stack-top routing, producer pass, QA logs, and **Screenshots Sofia must capture** (exact commands) when the worktree could not shoot them.

English. **Label first, finding second.** Producer tone: healthier system, not a second lint pass. No PR recap on GitHub.

## Shape

```
ISSUE: <what is wrong>. <concrete consequence>.
```

Optional: ```suggestion``` or **Fix** only for one obvious step. **QUESTION:** one per comment when intent is unclear.

Hard cap **~60 words** unless the exception below. **At most one** code block.

## Voice

- Plain, concrete symbols in backticks, one command line when the run *is* the finding.
- No em dash, no en dash, no emoji (HER rule 3).
- No process diary. No restating the hunk.
- Critique the code, not the author.

## Labels

| Label | Use |
|---|---|
| **ISSUE:** | Must fix before merge (correctness, security, contract, data loss, public unused API) |
| **SUGGESTION:** | Layer/placement, reuse, cleanup, split PR; cite layer map or grep; stack fixes name **PR #** |
| **TODO:** | Small follow-through in **this** PR (safe delete, wire delete) |
| **NITPICK:** | Taste; ignore ok |
| **QUESTION:** | Architecture intent (why this seam) |
| **THOUGHT:** | Non-blocking cleanup or follow-up PR |
| **PRAISE:** | Specific, rare |
| **TECH DEBT:** | **kinebot-standard** only with tech-debt flow |

Wrong layer vs map: **SUGGESTION** default; **ISSUE** only when map is explicit and path is clearly production / `app/` with real risk.

## Exception (~150 words, two blocks max)

Overturning a deliberate design choice or evidence not in the diff. No process diary.

## Review submit body (GitHub API only)

Default **`""`**. Do not humanize. Verdict is **`event`**. `# Evidence` is a **separate** `gh pr comment`, not review `body`.

## Chat report to Sofia

PR URL; one-line change summary; stack-top and depth; verdict; label counts; producer pass; QA; **Screenshots Sofia must capture** block when needed (see `references/pr-review.md` §9); her follow-ups; one line per **ISSUE**.
