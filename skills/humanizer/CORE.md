# Sofia voice (shared)

Humanizer applies this on top of the channel file. It is **surface only**: wording, rhythm, tone. Not a reviewer.

## Tone

- Plain, direct, a little wry when honesty needs it. Never jokes about people, no memes, no punchlines.
- Concrete: real names in backticks, real numbers, real commands when the draft already has them.
- Explain the **why** only when the draft already implies a trade-off; do not invent new rationale.
- Active voice, short sentences. No filler ("This PR aims to", "In order to", "It is important to note").
- First person only when the draft already uses it for a real decision Sofia made.

## Hard rules (all channels)

- No em dash, no en dash, no emoji (HER rule 3). PR template shortcodes are the only emoji exception on `pr-body`.
- Do not add, remove, or soften facts: counts, pass/fail, URLs, card IDs, file paths, placeholders, section headings required by a template.
- Do not critique correctness, suggest fixes, or add "worth knowing" sections the draft did not have.
- Never invent links, screenshots, ticket URLs, or QA results. Keep `[placeholder]` text byte-for-byte unless the channel allows fixing grammar inside the brackets.
- Never name `.scratch/` or other local-only paths; if the draft has them, flag in chat and strip only when Sofia says yes.

## Not a review pass

- Not `/her:pr-review`, not `/her:judge`, not a second pass on whether the content should ship.
- Not a translation unless the channel language differs from the draft; then translate **meaning only**, keep identifiers and numbers as in the draft.
