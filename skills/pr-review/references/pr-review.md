# Pull-request review procedure

Review the PR named in the request. Post **inline GitHub comments** plus one summary review. Read `../COMMENT-VOICE.md` for how each comment is written.

**GitHub only.** This skill does not write Kineloop cards. Log the review on Kineloop yourself if the team expects it.

If no PR is given:

```
gh pr view --json number,url,headRefName
```

If that fails, ask Sofia which PR.

## 1. Isolated worktree

Never review in the main working copy.

```
gh pr view <PR> --json number,headRefName,baseRefName,title,url,additions,deletions
git fetch origin
git worktree add .agents/worktrees/<branch-or-PR> <headRefName>
```

Run the whole review from that worktree. Remove it when done:

```
git worktree remove .agents/worktrees/<branch-or-PR>
```

## 2. Repo review standard

Read **checklists and layer maps only** from `docs/ai-pr-review/` when present:

| Repo | Standard |
|---|---|
| **kinebot-standard** | `checklist-general.md`, `frontend-layer-map.md`, `backend-layer-map.md`, `frontend-extras.md` |
| **kinebot-cosmos** | `checklist-general.md`, `checklist-python.md` |
| **kinebot-lambda** | No `docs/ai-pr-review/`: use repo `CLAUDE.md` |
| **kinebot-research** or missing folder | Same files as cosmos via `gh api repos/pixfy/kinebot-cosmos/contents/docs/ai-pr-review/...`, applied with the **research** strictness below (not production bar) |

Do **not** run or reuse `review_script.sh` / `prompt.md` (the AI bot machinery). This review catches what the bot misses; copying its prompt copies its blind spots.

Detect repo from `gh pr view --json headRepository,nameWithOwner` or the PR URL. When strictness differs, **kinebot-cosmos wins** if you are unsure.

## 3. Existing reviews first

```
gh api repos/{owner}/{repo}/pulls/<number>/reviews
gh api repos/{owner}/{repo}/pulls/<number>/comments
```

- Do not re-flag the same issue in new words.
- If the bot or a human raised something real and the author dismissed it wrongly, one short **ISSUE:** reinforcing it is fine.

## 4. Context

- PR description, linked issues, `gh pr diff <PR>`.
- If the why is missing and not obvious from the diff, that is a finding.
- Read surrounding code for non-trivial hunks. Never approve a block you did not read.

## 5. Run QA before you comment

Use the **QA Instructions** section of the PR body (and any linked test plan). Do this in the worktree **before** drafting inline comments or submitting the review.

1. List each QA step and what it needs (deps, env vars, data, network, hardware).
2. Run every step that can run in this environment: `uv sync` / `npm test` / docker compose / negative paths (bad URL, missing file), etc.
3. If a step needs assets you do not have (SharePoint videos, `.env`, VPN, GPU server), check whether they already exist under the paths the QA names. Do not skip without looking.
4. Record outcomes: command, pass/fail, one line of stderr or output when fail.

**Do not post the review until QA is attempted.** Record outcomes for Sofia's chat report: commands, pass/fail, blocked steps and why (missing asset, service, weights). A blocked step in the reviewer's environment is not auto **ISSUE** on **kinebot-research** unless the PR claims QA that is impossible for humans too.

Findings from QA trump diff-only guesses: failed QA step → **ISSUE** when output is wrong; flaky server → chat for Sofia; on GitHub only if it is a **code** finding the author must fix (not "go run the test plan").

**kinebot-standard** (Sofia last approver): post a separate PR comment `# Evidence` with QA commands and results before **APPROVE** (existing rule). **Other repos:** no QA log or test-plan reminders in the GitHub summary body; QA evidence and Sofia's remaining checks live in chat only.

## 6. Bar

Checklist first. Bar is **code health, not perfection** (Google eng-practices): approve when the change clearly improves the system. Valid alternatives are not blockers.

### Repo strictness

**kinebot-research** (less strict):

- Scripts, notebooks, one-off experiments, docs: **ISSUE** only for clear bugs, wrong results, security, or data loss (overwrite, corrupt outputs). No test suite in the path is normal; do not block on missing unit tests if QA in the PR is runnable.
- Robustness gaps (health check edge cases, naming in output files, cap heuristics) → **SUGGESTION** or **NITPICK** unless the consequence is silent wrong science or clobbered artifacts.
- Thin or missing PR template: note in summary or one **SUGGESTION**, not auto **REQUEST_CHANGES**, when the diff and QA still make sense.
- Prefer **APPROVE** or **COMMENT** when the change clearly helps the experiment and defects are non-blocking.

**kinebot-cosmos** (more strict):

- Apply **checklist-general** and **checklist-python** fully. `app/` and consumer paths: missing tests, error paths, async, DB, and external services are **ISSUE** or **TODO**, not optional polish.
- Template, linked ticket, and QA must be usable; weak or missing → **REQUEST_CHANGES** before deep pass (template gate).
- Borderline correctness or checklist defect → **ISSUE** and **REQUEST_CHANGES**, not "trust the author" **APPROVE**.
- Size gate 750 (+100) enforced; split guidance stands.

**kinebot-standard** and **kinebot-lambda**: default bar in this section unless the repo adds its own guide; between research and cosmos unless `CLAUDE.md` says otherwise.

**Look at every changed line.** More scrutiny on auth, money, migrations, concurrency, hot paths (always; stricter verdict class on cosmos).

Where the checklist is silent:

- Design / architecture
- Correctness / edge cases / concurrency
- Complexity (speculative generality is a smell)
- Tests that exercise the new path
- Naming (HER rule 2 applies to code you suggest: no comment spam in suggestions)
- Security, performance, docs
- AI smells: hallucinated APIs, invented config keys, ignored conventions

**Size gate** (additions + deletions):

- **kinebot-cosmos:** 750 (+100 tolerance)
- **Other team repos:** 1500

Over gate → **REQUEST_CHANGES** (split per team guide). >30 files is a one-line smell, not auto-reject.

**Template gate:** ignores template, unreadable description, or QA nobody can run → **REQUEST_CHANGES** before deep pass (after you tried to run it per section 5).

**Rejection heuristic:** ~10+ substantiated ISSUE/TODO/SUGGESTION (grounded) → stop piling comments; summary + talk with author; reject for rework. NITPICK/QUESTION/THOUGHT do not count.

## 7. Post the review

English. Inline comments + atomic review:

```
gh api --method POST repos/{owner}/{repo}/pulls/<number>/reviews --input review.json
```

```json
{
  "event": "REQUEST_CHANGES | COMMENT | APPROVE",
  "body": "<author-facing summary, ≤4 lines; see COMMENT-VOICE.md>",
  "comments": [
    { "path": "src/foo.ts", "line": 42, "side": "RIGHT", "body": "ISSUE: …" }
  ]
}
```

Draft **body** and **inline comments** for the author. Run `../../humanizer/PASS.md` on body and each inline before post (not on the chat report). Draft the **chat report** separately for Sofia (verdict counts, full QA, blocked environment).

Verdict:

- Any **ISSUE** → `REQUEST_CHANGES` (on **kinebot-research**, reserve **ISSUE** for the blockers listed above; do not upgrade SUGGESTION-tier findings to force a reject)
- Only SUGGESTION/TODO/NITPICK/QUESTION/THOUGHT → `COMMENT` or `APPROVE` if you trust the author (**kinebot-cosmos**: do not approve with open **TODO** on new `app/` behavior)
- Clean improvement → `APPROVE`

**kinebot-standard, two reviewers, Sofia is last approver:** QA evidence in a **separate** PR comment starting with `# Evidence`, before approve. GitHub summary body still author-facing, ≤4 lines (not a QA log).

**kinebot-cosmos, single reviewer:** no separate `# Evidence` comment unless a run result *is* a finding.

## 8. Clean up and report

Remove the worktree. **Chat only:** tell Sofia verdict, counts by label, PR URL, full QA (ran / blocked / why), and ISSUE file:lines. Do not mirror that packet in the GitHub review body.
