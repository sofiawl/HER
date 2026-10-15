# How Sofia's PR review comments sound

**Two audiences.** Inline comments and the GitHub **summary review body** are for the PR author and anyone reading the thread later: only **code review** outcome (blockers, inline threads). The **chat reply to Sofia** is her control panel: verdict counts, full QA logs, what blocked in your environment, and **what she still owes** (run the PR test plan, fetch SharePoint videos, spot-check before merge). Never paste the chat report into GitHub. Never assign Sofia's follow-ups to the author on GitHub ("please run QA", "verify on kinebot videos").

Inline GitHub comments only. English. ADHD shape: **label first, finding second**. One breath.

## Shape

```
ISSUE: <what is wrong>. <concrete consequence>.
```

Optional third beat (default off):

- **Fix** or a ```suggestion block: only when one obvious step (typo, missing `raise_for_status`, wrong key name). Not for design or multi-line rewrites.
- **Question**: separate **QUESTION:** comment when you cannot judge without intent; one question per comment. Do not tack a question onto **ISSUE:** unless the bug itself is ambiguous.

If neither case applies, stop after the consequence.

Hard cap **~60 words** unless the exception below applies. **At most one** code block: a ```suggestion or up to 4 lines of evidence.

## Voice (same family as PR writing, tighter)

- Plain, a little wry when it helps honesty ("this reads like the bot already caught it, but the dismiss was wrong"), never jokes about people.
- Concrete: real symbols in backticks, real numbers, one command line if the result *is* the finding.
- No em dash, no en dash, no emoji (HER rule 3).
- No narrating your process ("I read the doc", "I ran the suite"). One clause max if the run *is* the finding.
- No restating the PR or the hunk. They have the diff.
- Critique the code, not the author.

## Labels (conventionalcomments.org, UPPERCASE)

| Label | Use |
|---|---|
| **ISSUE:** | Must fix before merge (correctness, security, contract, data loss) |
| **SUGGESTION:** | Real improvement **and** cites checklist, layer map, or objective rule; else **NITPICK:** |
| **TODO:** | Small follow-through in this PR (missing test, rename) |
| **NITPICK:** | Taste; author may ignore |
| **QUESTION:** | Need intent before judging (one question per comment) |
| **THOUGHT:** | Reflection; no action |
| **PRAISE:** | Specific, rare |
| **TECH DEBT:** | Only **kinebot-standard** repos with the tech-debt flow; on **kinebot-cosmos** use SUGGESTION or a manual Kineloop issue |

## Exception (~150 words, two blocks max)

When the claim is not verifiable from the diff alone, or you are overturning a deliberate design choice. Still no process diary.

## Summary review body (GitHub only, for the author)

Write for someone who already read the PR. **≤3 lines.**

- Outcome in plain words: approved, changes requested, or comment-only (no label tallies like `0 ISSUE, 1 SUGGESTION`).
- **REQUEST_CHANGES:** one line per blocking **ISSUE** with `file:line`, or "see inline ISSUE comments". Do not repeat SUGGESTION/NITPICK text.
- **APPROVE** / **COMMENT:** if useful, one short note such as "Non-blocking suggestions inline." Otherwise the inline threads are enough; an empty or one-word body is fine.

**Never on GitHub:** PR recap, QA/test-plan homework for anyone, nudges to run the PR template steps, process diary, reviewer environment (SharePoint, missing weights, symlinks), command dumps.

## Chat report to Sofia (not posted on GitHub)

After submit, tell Sofia what **she** needs to steer: PR URL, verdict, counts by label, QA you ran (pass/fail, commands), what blocked in **your** environment and why, **her** follow-ups (e.g. full PR QA not covered in review, merge only after she runs steps X-Y), and one line per **ISSUE**. This is where "please run the PR QA steps" belongs, addressed to Sofia, not the author.
