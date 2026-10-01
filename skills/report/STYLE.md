# Kinebot report style

Shared by `/her:report`. Derived from the reports in `~/kinebot-latex-templates/relatorios/`. `pesquisa-identificacao-medidas` is the reference: when in doubt, do what it does.

## Files

- Folder `relatorios/<slug>/`, file `relatorio-<slug>.tex`. Slug in pt-BR, lowercase, hyphenated, no accents.
- Copy `latexmkrc` from `relatorios/pesquisa-identificacao-medidas/` (it points TEXINPUTS at the repo root so `kinebot.sty` and the footer banner resolve).
- `images/` for raster figures, named in descriptive snake_case (`erro_por_video.png`), never `Pasted image.png`.
- `scripts/` only if a script generates a figure, and every figure it generates must be included in the `.tex`.
- Never edit `kinebot.sty`. Never commit PDFs or aux files (the `.gitignore` covers them).

## Preamble

Start from `SKELETON.tex`. It holds the fixed order: metadata macros, `\pagenumbering{gobble}`, `\makecover`, `\tableofcontents`, `\cleardoublepage`, `\pagenumbering{arabic}`, `\pagestyle{fancy}`. Add a package only when the report uses it (`longtable` for tables that break pages, `amsmath` for equations, `listings` for SQL or code appendices). `\reportref` starts at `v1.0`; bump it when revising a delivered report.

## Sections

Always `Introdução`, `Metodologia`, `Resultados`, `Conclusão`, in that order. Optional sections go between Metodologia and Conclusão (data model, discussion, confiabilidade) or after Conclusão (Apêndices, Fontes).

Appendices are numbered, never lettered: use the `\apendice{Título}{sec:apendice-x}` macro from `SKELETON.tex` (not `\appendix`). It prints `Apêndice 1 - Título` in the heading and the sumário, and the text refers to it as `Apêndice~\ref{sec:apendice-x}`.

## No empty pages

No page except the last may be mostly blank. `[H]` floats that do not fit jump whole to the next page and leave a hole, so:

- No `\clearpage` or `\newpage` in the body. Appendices follow the Conclusão on the same page.
- A table longer than about 15 rows is a `longtable` (with `\endfirsthead`, a "(continuação)" line and `\endhead`), never `table[H]`, so it breaks across pages.
- A section heading is never the last thing on a page: `\apendice` already reserves space with `\Needspace`. Use `\Needspace{8\baselineskip}` before other headings that end up stranded.
- A figure that leaves a gap is made smaller or moved next to the paragraph that cites it, never pushed to its own page.

- **Introdução**: context, the purpose question from the ledger, what the report answers. Short.
- **Metodologia**: data and scope (with counts), method and why, alternatives rejected and why.
- **Resultados**: one subsection per Main result, in ledger order, each opened by a framing sentence, then the table or figure, then 1 to 3 sentences of interpretation. Supporting results sit inside the Main subsection they explain.
- **Conclusão**: first paragraph answers the purpose question with the headline number. Then `Pontos em aberto:` as an enumerated list (limitations, unresolved doubts, next steps).

## Voice

- pt-BR, impersonal (`foi avaliado`, `observa-se`), past tense for findings, present tense for how the system works.
- Every number comes with its meaning and a comparison: "erro médio de 3,6 cm, contra 11,2 cm do método anterior".
- Decimal comma, period for thousands (`1.465`, `29,3\%`). Units written as text after a space, no siunitx.
- Name failures plainly with the case that caused them ("um único vídeo eleva o erro médio em 40 vezes"). Never smooth them over.
- Terms in English that the team uses (ground truth, bounding box, pipeline) stay in English, in italics the first time.
- Bold only for the one phrase a skimmer must see. Lists for 3 or more parallel items.
- No semicolons in the prose, list items included. Split into two sentences, or join with a comma or `e`.
- No em dash, no en dash, no emojis, in the report too.
- Never mention a document the reader does not have: no ADRs, specs, `CONTEXT.md`, canvases, the ledger, Linear issues or file paths in the research repo. They shape the content but are not cited. Only name one when Sofia explicitly asks for it.
- No run IDs or timestamps (`20260923T140931Z`), commit hashes, result file names or script names in the text. Name the dataset or test in plain words instead.

## Source layout

The `.tex` is read and edited in Cursor, so it must read without horizontal scrolling.

- One sentence per line. Wrap a sentence longer than about 100 characters at a word boundary. Never write a whole paragraph on one line.
- Paragraphs are separated by one blank line. Continuation lines of an `\item` are indented two spaces past `\item`.
- Table rows, `\url{}` and pgfplots coordinates may stay on one line.

## Tables and figures

- Tables: `booktabs` only (`\toprule`, `\midrule`, `\bottomrule`, never `\hline`), caption above the tabular, fixed `p{}` columns when text wraps, totals row in bold after a `\midrule`.
- Figures: caption below. Placement `[H]` everywhere (the `float` package), plus the `\FloatBarrier` section redefinition from the skeleton.
- Charts: prefer pgfplots with the `kinebotgraph` style and `kinebotbarA/B/C` fills, with numbers typed from the ledger, so the chart rebuilds from source. Use a PNG only for things that are not charts (video frames, overlays, diagrams).
- Labels `tab:<name>` and `fig:<name>`, referenced as `Tabela~\ref{...}` and `Figura~\ref{...}`. Every table and figure is referenced in the text before it appears.

## Sources

No biblatex. One external source mentioned in passing: italic title plus `\url{}` inline. Several sources: a final `\section{Fontes}` with ABNT-style manual entries (author, title, venue, year, `\url{}` to DOI or arXiv, access date). Internal sources (specs, ADRs, Linear issues) are not cited unless Sofia explicitly asks (see Voice).
