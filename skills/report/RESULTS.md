# Finding and ranking the main results

Shared by `/her:report`. The goal is a short, approved list of results, each one traceable to a file. Nothing here writes LaTeX.

## 1. Pin the purpose first

The purpose decides what counts as a main result, so find it before opening any result file. Look in this order and stop when it is clear:

1. What Sofia said when she pointed at the folder.
2. `docs/specs/DES2-*.md` and `docs/adr/*.md` in `~/kinebot-research` that mention the folder: the research question, what was rejected and why, what stays research-only.
3. `CONTEXT.md` and `CONTEXT-MAP.md` (root and folder): the glossary and what counts as ground truth.
4. `<folder>/README.md`: what a run produces. The root README is stale, never trust it for purpose.
5. `git -C ~/kinebot-research log --oneline -20 -- <folder>`: recent intent, and renames (content can move between folders under the same Linear epic).

Write the purpose as one question plus the decision it feeds, for example: "Can we estimate horizontal distance from video with error under X cm, so NIOSH can be filled automatically?" If two sources disagree, or none states it, ask Sofia with AskUserQuestion (2 to 4 candidate purposes, recommended one first). Do not guess.

## 2. Inventory the evidence

List candidate artifacts before reading them:

- Result manifests: `summary.json`, `results.jsonl`, `*.csv`, `manifest.csv`, `ground_truth*.csv`. Use `head`, never open a full dataset or video.
- Timestamped runs: `benchmark/results/<ts>/`, `out*/`. The newest run is not automatically the one to report; check which run the spec or ADR points to.
- Superseded runs: `old_runs/`, `*_wrong_*`, `out_old`. Usually excluded; say so in the ledger.
- Outlier cases inside a run are not superseded runs: keep them in every average unless Sofia explicitly excludes them.
- Databases (`*.db`, SQL dumps): for app or data-collection tools the real results may live only there. Query read-only (`sqlite3 -readonly`).
- Plots already produced, and the scripts that produced them.

There are no notebooks in kinebot-research today; if one appears, read saved outputs only, never execute it.

## 3. Build the claim ledger

One row per candidate result. Every number in the final report must come from a row.

| # | Claim (one sentence) | Number(s) and unit | Source (path + key/row/query) | Compared to | Answers purpose? | Limitation |
|---|---|---|---|---|---|---|

Rules:
- Read the number from the source in this session (see `../judge/VERIFY.md`). If you computed it (mean, share, delta), write the command next to it.
- A number without a baseline or target is a weak claim. Find the comparison (previous method, threshold, ground truth, product requirement).
- Record sample size. A result on 3 videos is a lead, not a finding.

## 4. Rank

Sort rows into three tiers:

1. **Main**: directly answers the purpose question, has a baseline, and the effect is large enough to change the decision. At most 3. One of them is the headline: the single number the Conclusão leads with.
2. **Supporting**: explains why a main result holds (ablations, per-category breakdowns, error sources).
3. **Out**: superseded, research-only per ADR, off-purpose, or too thin. Keep the reason.

Rank by practical impact on the decision, not by how impressive the number looks. A negative result that answers the purpose ("the method does not reach the target") is Main, never hidden.

## 5. Steelman the doubt

For each Main row, try to explain it away before accepting it:
- Could one outlier drive it? Check the median and the worst case.
- Is the comparison fair (same data, same conditions)?
- Could the ground truth itself be wrong?
- Would it survive on a different subset?

If a doubt holds, downgrade the row or add it to its Limitation. Unresolved doubts go to the Conclusão's open points.

## 6. Propose and wait

Show Sofia, in chat:
1. The purpose question (and where it came from).
2. The headline in one sentence.
3. The ledger, grouped by tier, with the reason for each Out.
4. Figures and tables you plan, one line each.
5. Anything you need from her (missing data, unclear purpose).

Save the same content to `${TMPDIR:-/tmp}/her-report-<slug>/LEDGER.md`. Wait for her OK or edits. Do not write the `.tex` before that.
