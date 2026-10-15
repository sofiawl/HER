# Humanizer pass (embedded)

Not a skill. Parent skills call this **after** the draft has the right facts and structure, **before** save or post. Surface voice only: not `/her:judge`, not a content review.

Load `CORE.md`, the channel row from `CHANNELS.md`, and that channel's voice file.

## Steps

1. **Ledger** (internal, do not show Sofia unless she asks): every number, URL, card ID, placeholder `[...]`, template heading, LaTeX command line you must not break.
2. **Rewrite** the draft using CORE + channel voice. Cut filler, match Sofia's rhythm. Do not add, remove, or soften facts.
3. **Check** output against the ledger. Fix mismatches before save/post. Cannot fix without guessing: stop and grill (HER rule 8).

## Channels by parent skill

| Parent | Channel |
|---|---|
| `/her:to-pr` write/update | `pr-body` |
| `/her:report` write | `report-prose` |
| `/her:pr-review` post to GitHub | `pr-review-inline` for summary body and each inline (COMMENT-VOICE caps stay) |
| `/her:address-review` thread reply | `pr-thread-reply` |
| `/her:her` Kineloop card or document | `kineloop-card` |
| `/her:her` Kineloop comment (e.g. run summary) | `kineloop-comment` |

Other HER skills do not run this pass unless they post human-facing text; then pick the closest channel or ask Sofia once.
