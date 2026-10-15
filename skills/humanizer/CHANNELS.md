# Channels

The **parent skill** picks the channel (see `PASS.md`). Do not expose channel names to Sofia unless debugging.

| Channel | Language | Load |
|---|---|---|
| `kineloop-card` | pt-BR | `KINELOOP-VOICE.md` (card/document shape) |
| `kineloop-comment` | pt-BR | `KINELOOP-VOICE.md` (comment shape) |
| `pr-body` | en | `../to-pr/VOICE.md` plus template headings unchanged |
| `pr-thread-reply` | en | `../address-review/REPLY-VOICE.md` (one line; if draft is longer, compress to one line without losing facts) |
| `pr-review-inline` | en | `../pr-review/COMMENT-VOICE.md` (labels and caps preserved) |
| `report-prose` | pt-BR | `../report/STYLE.md` Voice section; keep LaTeX commands and `\label`s untouched |
| `freeform` | match draft | `CORE.md` only |

After loading the channel file, always apply `CORE.md`.

**kinebot-pdi PRs:** when the draft follows `../to-pr/kinebot-pdi.md`, keep that structure; only humanize prose inside sections.

**Report LaTeX:** rewrite sentence lines only; never split or merge `\begin`/`\end` blocks; one sentence per line stays one sentence per line.
