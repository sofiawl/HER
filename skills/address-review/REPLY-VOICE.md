# How Sofia's PR thread replies sound

GitHub **inline thread replies** only. English. **Hard cap: one line** (one sentence). No bullet lists, no second paragraph.

## Shape

```
<Done|Won't|Need you>: <concrete fact>.
```

- **Done:** merged fix, points at behavior (`raise_for_status` added, test covers empty input).
- **Won't:** moot or out of scope; name the reason in the same line (already handled in `foo`, tracked in DES-123, nit per checklist).
- **Need you:** only when blocked on Sofia; then stop the skill loop and grill (HER rule 8), do not guess.

Optional: `Fixed in <short-sha>.` when the diff is not obvious from the thread location.

## Voice

- Plain, direct, no filler ("Thanks for", "Good catch", "As discussed").
- No em dash, no en dash, no emoji (HER rule 3).
- No narrating process. No restating the whole comment.
- Critique stays about the code; replies stay factual.

## Labels from reviewers

When the reviewer used conventionalcomments (`ISSUE:`, `SUGGESTION:`, etc.), you do not repeat their label. Your line is the answer, not a re-review.
