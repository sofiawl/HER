# How Sofia's PR review comments sound

Inline GitHub review comments only. English. ADHD shape: **label first, finding second, fix third**, one breath.

## Shape

```
ISSUE: <what is wrong>. <concrete consequence>. <fix or question>.
```

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

## Summary review body

**≤6 lines:** what the PR does, verdict + counts by label, one line per ISSUE with `file:line`. No praise paragraph, no rerun of inline comments.
