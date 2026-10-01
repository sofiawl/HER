---
name: report
description: >
  Write a Kinebot research report (LaTeX, pt-BR, ABNT, kinebot.sty) in
  ~/kinebot-latex-templates/relatorios/ from the results of a kinebot-research
  folder Sofia points to. Finds the research purpose, ranks the main results
  in a claim ledger for her approval, then writes, compiles and checks the
  report. Triggers: "/her:report", "write the report", "relatorio", "report
  paper", "write up this research", "turn these results into a report",
  "update the report for <folder>".
argument-hint: "<kinebot-research folder> [purpose or report slug]"
---

Mode: professor.

Reference files: `RESULTS.md` (finding and ranking results), `STYLE.md` (LaTeX and voice), `SKELETON.tex` (starting file), `../judge/VERIFY.md` (verification gate).

## Inputs

- The research folder, for example `~/kinebot-research/video_measures`. If Sofia did not name one, ask; do not pick.
- Optional: the purpose in her words, an existing report slug to update, the audience (team, product, client).

## Flow

1. **Purpose.** Follow `RESULTS.md` section 1. State the purpose question and its source in one line.
2. **Evidence and ledger.** `RESULTS.md` sections 2 and 3. Read-only in the research repo: never run its code, never modify it. Query databases read-only.
3. **Rank and steelman.** `RESULTS.md` sections 4 and 5. Explain in one sentence per Main result why it ranked there (professor mode).
4. **Approval gate.** `RESULTS.md` section 6. Stop and wait for Sofia's OK. Her edits to the ledger win.
5. **Outline.** Map ledger rows to sections per `STYLE.md`, with the planned tables and figures. Show it in a few lines; continue unless she objects.
6. **Write.** New report: create `relatorios/<slug>/` from `SKELETON.tex` and copy `latexmkrc`. Existing report: edit in place, keep her text unless it contradicts the ledger, bump `\reportref`. Copy needed images from the research folder into `images/` with snake_case names. Every number typed into the `.tex` must match a ledger row.
7. **Compile and check.** From the report folder: `latexmk -pdf relatorio-<slug>.tex`. Fix errors. Then check the log and report:
   - `grep -n "undefined\|Missing\|multiply defined" relatorio-<slug>.log`
   - overfull boxes above 10pt (`grep -n "Overfull" ...`), fix the ones in body text
   - every `\label` referenced, every file in `images/` included
   - `grep -nP '[\x{2013}\x{2014}]|[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]'` on the `.tex` returns nothing
   - no semicolon in the prose: `grep -n ';' relatorio-<slug>.tex` shows only LaTeX or pgfplots code
   - no internal document named: `grep -nwiE 'ADR|CONTEXT\.md|canvas|ledger|linear' relatorio-<slug>.tex` returns nothing unless Sofia asked for it
   - no run IDs: `grep -nE '[0-9]{8}T[0-9]{6}Z' relatorio-<slug>.tex` returns nothing
   - no near-empty pages: `n=$(pdfinfo relatorio-<slug>.pdf | awk '/Pages/{print $2}'); for p in $(seq 3 $((n-1))); do c=$(pdftotext -f $p -l $p -layout relatorio-<slug>.pdf - | grep -cv '^\s*$'); [ $c -lt 18 ] && echo "page $p: $c lines"; done` prints nothing. A page with a figure can have few text lines, so render any flagged page (`pdftoppm -f $p -l $p -r 40 -png`) and look at it before accepting it
   - no long prose lines: `awk 'length>110' relatorio-<slug>.tex` shows only table rows, URLs or plot code
8. **Independent number check.** Launch one `sonnet` subagent that did not write the report. Give it the `.tex` and the ledger path, ask it to re-read each number from its source and list mismatches. Fix them. Per `VERIFY.md`, do not report "done" on the writer's word.
9. **Hand back.** Path to the `.tex` and PDF, page count, the headline sentence, open points, anything left as placeholder. Do not commit unless she asks.

## Hard rules

- No LaTeX before the ledger is approved.
- Never invent a number, citation, DOI, figure or Linear ID. Missing: leave `\textbf{[PREENCHER: ...]}` and list it in the hand-back.
- Negative results that answer the purpose are reported, not buried.
- Results excluded as Out stay out unless Sofia moves them.
- Never drop a case, sample or video from the results on your own, even if it looks like an outlier or the
  source (canvas, summary) already excludes it. Ask Sofia first and exclude only when she explicitly says so.
  Every excluded case is listed in the report with the reason she gave.
- One report per research purpose. If the folder answers two questions, ask whether to split.

## When something is off

- Purpose unclear or conflicting: ask with 2 to 4 options, recommended first.
- Results only in a database or dump she has not given: ask for access or the export; do not connect to production.
- The folder's evidence cannot support the purpose: say so plainly and propose either a narrower purpose or the experiment that is missing (offer `/her:research` for external literature).

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Inventory the research folder, copy images, run latexmk, grep the log | `haiku` | Inventory in parallel per subfolder |
| Read each result source and draft ledger rows | `sonnet` | One agent per subfolder or run, in parallel |
| Rank and steelman the Main results | `fable` | Gets the full ledger and the purpose |
| Write the `.tex` in pt-BR from the approved ledger and STYLE.md | `opus` | One agent |
| Independent number check (Flow step 8) | `sonnet` | A different agent from the writer |
