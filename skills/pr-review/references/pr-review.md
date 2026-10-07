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
| **kinebot-research** or missing folder | Use kinebot-cosmos checklists via `gh api repos/pixfy/kinebot-cosmos/contents/docs/ai-pr-review/...` |

Do **not** run or reuse `review_script.sh` / `prompt.md` (the AI bot machinery). This review catches what the bot misses; copying its prompt copies its blind spots.

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

## 5. Bar

Checklist first. Bar is **code health, not perfection** (Google eng-practices): approve when the change clearly improves the system. Valid alternatives are not blockers.

**Look at every changed line.** More scrutiny on auth, money, migrations, concurrency, hot paths.

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

**Template gate:** ignores template, unreadable description, or QA nobody can run → **REQUEST_CHANGES** before deep pass.

**Rejection heuristic:** ~10+ substantiated ISSUE/TODO/SUGGESTION (grounded) → stop piling comments; summary + talk with author; reject for rework. NITPICK/QUESTION/THOUGHT do not count.

## 6. Post the review

English. Inline comments + atomic review:

```
gh api --method POST repos/{owner}/{repo}/pulls/<number>/reviews --input review.json
```

```json
{
  "event": "REQUEST_CHANGES | COMMENT | APPROVE",
  "body": "<summary, ≤6 lines>",
  "comments": [
    { "path": "src/foo.ts", "line": 42, "side": "RIGHT", "body": "ISSUE: …" }
  ]
}
```

Verdict:

- Any **ISSUE** → `REQUEST_CHANGES`
- Only SUGGESTION/TODO/NITPICK/QUESTION/THOUGHT → `COMMENT` or `APPROVE` if you trust the author
- Clean improvement → `APPROVE`

**kinebot-standard, two reviewers, Sofia is last approver:** QA evidence in a **separate** PR comment starting with `# Evidence`, before approve. Summary still ≤6 lines.

**kinebot-cosmos, single reviewer:** no separate `# Evidence` comment unless a run result *is* a finding.

## 7. Clean up and report

Remove the worktree. Tell Sofia: verdict, counts by label, PR URL.
