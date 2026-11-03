# Pull-request review procedure

Review the PR named in the request. Post **inline GitHub comments** and submit one atomic review (`event` + empty `body`). Read `../COMMENT-VOICE.md` for how each inline is written.

**GitHub only.** This skill does not write Kineloop cards.

If no PR is given:

```
gh pr view --json number,url,headRefName
```

If that fails, ask Sofia which PR.

## 1. Isolated worktree

Never review in the main working copy.

```
gh pr view <PR> --json number,headRefName,baseRefName,title,url,additions,deletions,body
git fetch origin
git worktree add .agents/worktrees/<branch-or-PR> <headRefName>
```

Run the whole review from that worktree only. Do not run QA from the main checkout.

**While the review runs:**

- Write ephemeral artifacts (`review.json`, `/tmp/evidence-<PR>.md`, screenshots under `/tmp/pr-<PR>-evidence/`) under `/tmp/` or the main repo root, never inside the worktree path.
- `uv sync` in the worktree is allowed; it creates a nested `.venv` there that must not survive cleanup.

**Cleanup is mandatory.** Run it even when the GitHub review post fails, QA aborts, or the verdict is REQUEST_CHANGES.

```
WT=.agents/worktrees/<branch-or-PR>
git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
git worktree prune
git worktree list
```

- Always use `--force` (or `rm -rf` the path) so an untracked `.venv` or other ignored files cannot block removal.
- After cleanup, `git worktree list` must show no rows under `.agents/worktrees/` for this review. If one remains, delete it and report the path to Sofia in chat.

## 2. Stack map and review depth

Parse the PR body using `../../to-pr/TEMPLATE.md` (and `../../to-pr/kinebot-pdi.md` when that repo applies). Do not guess stack position from branch prefix alone.

**Stack detection**

- **Related** links, merge-order table (`| Order | PR | ...`), parent **proposal** / **feat** links, and chains like `#a -> #b` in **Tests** or **QA**.
- Open the **proposal** PR body when this PR is a **sub** and the table lives there.

**Stack-top PR** = the row with the **highest `Order`** in the merge-order table (that PR number). If there is no table but the body describes a single stacked chain, stack-top = the **last** PR number in the chain.

**Single PR** = no merge-order table and no stacked **Related** chain (standalone bug fix, refactor, or one-off).

**Depth**

| Situation | Pass |
|---|---|
| **Single PR** | **Deep** (§6) |
| **Stack-top PR** | **Deep** (§6) |
| **Lower stack PR** (not stack-top) | **Light** (§6, no extra producer commands) |

Record in scratch: `stack-top: #N`, `this PR: #M`, `depth: deep|light`.

## 3. Automation: present vs fallback

```
gh pr checks <PR>
gh api repos/{owner}/{repo}/pulls/<number>/reviews
gh api repos/{owner}/{repo}/pulls/<number>/comments
```

Identify the **ai-review** check (or the repo workflow name from `docs/ai-pr-review/README.md`) and **bot inline comments** (account from that README or workflow).

**Automation present** when **either**:

- the ai-review (or equivalent) check is **success** on the PR head, **or**
- at least one **inline review comment** from the bot on this PR.

**Fallback** when **both** are missing: run **§7** (full defect checklist). Do not run §6 human-only pass in fallback mode.

When automation **is** present:

- Do **not** run or reuse `review_script.sh` / `prompt.md`.
- Do **not** re-flag the same bot issue in new words.
- Do **not** duplicate Ruff/mypy/Jev convention nits unless QA or behavior proves them wrong.
- Wrong dismiss of a real bot/human point → one short **ISSUE:** reinforcing it.

**Placement maps** (§6 human pass; not the defect checklists):

| Repo | Architecture / what-goes-where |
|---|---|
| **kinebot-standard** | `frontend-layer-map.md`, `backend-layer-map.md`, `frontend-extras.md` under `docs/ai-pr-review/` |
| **kinebot-cosmos** | `CLAUDE.md`, layering docs, `scripts/guidelines_review/` expectations if documented |
| **kinebot-lambda** | `CLAUDE.md` |
| **kinebot-research** | Same map files as cosmos via API when missing locally; **research** verdict bar in §7 only applies in fallback |

Detect repo from `gh pr view --json headRepository,nameWithOwner`.

## 4. Context

- PR description, linked issues, stack links, `gh pr diff <PR>`, `git diff --stat` vs base.
- Missing **why** when not obvious from the diff → **QUESTION:** or **ISSUE:** if merge would be blind.
- Read surrounding code for non-trivial hunks. Never approve a block you did not read.

## 5. Run QA before you comment

Use **QA Instructions** / **QA** from the PR body. Run in the worktree **before** inlines or review submit.

1. List each step and what it needs (deps, env, data, network, hardware).
2. Run every step that can run here.
3. If assets are missing, check paths the QA names before calling it blocked.
4. Record: command, pass/fail, one line of stderr or output on fail.

Findings from QA trump diff-only guesses: failed QA → **ISSUE** when output is wrong; flaky infra → Sofia chat; on GitHub only for **code** the author must fix.

Visual QA steps: capture PNG/video in `/tmp/pr-<PR>-evidence/` when the environment allows (ffmpeg frame, Playwright if the repo already has it, exported UI). When capture is not possible, use **§9** screenshot block for Sofia (exact commands, not vague).

## 6. Human pass (automation present only)

Skip this section in **fallback** (§7). Bar: **code health improving**, producer tone (not a second lint pass).

### Architecture and placement

- **Layer / seam:** Wrong folder or call direction vs layer map → **SUGGESTION** by default; **ISSUE** only when the map is explicit and the path is clearly production / `app/` with a real defect risk.
- **Design fit:** Belongs in this repo, module, and **this PR in the stack**? Deep module vs shallow pass-through?
- **Stack routing:** If the fix belongs in another stack PR, say so in the inline: `SUGGESTION: … (belongs in PR #<n>, stack order <k>).` Do not ask the author to fix stack-top integration in a lower sub when the body already assigns that work to a later PR.
- **Reuse:** Grep before suggesting new helpers; duplicate of existing util → **SUGGESTION** with path.

### Dead weight and duplication

- **ISSUE:** new **public** unused surface (exports, API) that will mislead the next change, **unless** a named later stack PR will wire it and the default path is noop-safe.
- **TODO:** safe delete in this PR (imports, dead branch introduced here).
- **SUGGESTION** / **THOUGHT:** wider cleanup out of scope.

Stack rules: no **SUGGESTION** to wire before merge when noop-safe and a later PR owns it; scaffold params for the next corrector are not **TODO** unless CI blocks.

### Deep pass (singles and stack-top only)

Not `/her:judge`. At most **1–2** extra commands beyond §5 QA, chosen from what the PR already documents or CI runs. Stop early; cite output in chat and in `# Evidence`, not a metric table.

Use deep to answer: happy path + one failure path proved? revert safe? wrong integration point? split needed (cosmos 750 +100 lines)?

**Light pass** (lower stack): §5 QA + architecture/dead-weight rules above, **no** extra §6 deep commands.

Do **not** duplicate bot defect checklist items unless QA proves the bot wrong.

**Size gate** (additions + deletions): cosmos 750 (+100); other team repos 1500 → **REQUEST_CHANGES** (split). >30 files → one **SUGGESTION** smell.

**Template gate:** unreadable description or QA nobody can run → **REQUEST_CHANGES** after §5 attempt.

## 7. Fallback (automation absent)

When §3 fallback triggers, read defect checklists from `docs/ai-pr-review/`:

| Repo | Checklists |
|---|---|
| **kinebot-standard** | `checklist-general.md`, layer maps, `frontend-extras.md` |
| **kinebot-cosmos** | `checklist-general.md`, `checklist-python.md` |
| **kinebot-lambda** | `CLAUDE.md` |
| **kinebot-research** | Cosmos checklists via API; **research** bar below |

Checklist first. **Look at every changed line.** Extra scrutiny on auth, money, migrations, concurrency, hot paths.

**kinebot-research:** **ISSUE** only for clear bugs, wrong results, security, data loss; missing unit tests normal if PR QA runs; prefer **APPROVE**/**COMMENT** when the experiment clearly helps.

**kinebot-cosmos:** apply checklists fully; missing tests/error paths on `app/` → **ISSUE**/**TODO**; template/ticket/QA weak → **REQUEST_CHANGES** before deep read; borderline defect → **REQUEST_CHANGES**.

**kinebot-standard** / **kinebot-lambda:** default bar between research and cosmos unless `CLAUDE.md` says otherwise.

Where checklists are silent: design, correctness, complexity, tests on new paths, naming, security, performance, docs, AI smells.

**Rejection heuristic:** many grounded **ISSUE**s → **REQUEST_CHANGES** with top blockers inline; tell Sofia rework needed.

## 8. Post the review

Before posting, fetch existing inline threads on this PR (`gh api repos/{owner}/{repo}/pulls/<number>/comments`). If the same path and line already has an open **ISSUE** or **QUESTION** from Sofia and the code still has that defect, submit the review with **`comments: []`**: set `event` only, or one short review `body` pointing at the existing thread. Do not post the same finding again in new words after a rebase or re-review.

English. Inline comments + atomic review:

```
gh api --method POST repos/{owner}/{repo}/pulls/<number>/reviews --input review.json
```

```json
{
  "event": "REQUEST_CHANGES | COMMENT | APPROVE",
  "body": "",
  "comments": [
    { "path": "src/foo.ts", "line": 42, "side": "RIGHT", "body": "ISSUE: …" }
  ]
}
```

Humanize each inline via `../../humanizer/PASS.md` (`pr-review-inline`); skip empty `body`.

**Verdict:** any **ISSUE** → `REQUEST_CHANGES`; else **COMMENT** or **APPROVE** when the change improves the system.

### `# Evidence` (before **APPROVE**)

Required on **kinebot-standard** and **kinebot-cosmos**. Separate PR comment, not review `body`.

Write `/tmp/evidence-<PR>.md` starting with `# Evidence`, then QA steps run (pass/fail, one line each) and deep-pass commands when §6 deep ran.

Post with **`gh`**:

```
gh pr comment <PR> --body-file /tmp/evidence-<PR>.md \
  --attach '/tmp/pr-<PR>-evidence/step-3.png#What the frame must show' \
  ...
```

Use `--attach` for each screenshot; alt text after `#` must state what the frame must show. Reference attachments in the markdown when helpful (`![label](./step-3.png)`). Up to 50 attachments per comment per `gh pr comment --help`.

### Sync GitHub state labels

After the review (and `# Evidence` when required) is posted. **GitHub only**, not Kineloop.

**Repos:** **kinebot-cosmos**, **kinebot-research**, **kinebot-pdi** only. Same rules on all three. **Never** add or remove state labels on **kinebot-standard** (`pr-metadata.yml` owns them).

**Scope:** state labels only. Never touch nature (`feature`, `proposal`, `fix`, `refactor`, `evidence-skipped`, …), process (`WIP`, `blocked`, `REJECT`, …), CI (`CONFLICTS`, `under-100-lines`, bot dependency labels), or PDI `type:*` / `area:*` / `priority:*`.

Resolve names with `gh label list` before `gh pr edit`. Skip a logical label when that repo has no matching GitHub label (warn in chat).

| Logical | cosmos / research | pdi |
|---|---|---|
| wait for review | `wait-review` | `status:wait-review` |
| changes requested | `request-changes` | `changes-requested` |
| approved | `approved` | `approved` |
| wait to merge | `wait-to-merge` | `wait-to-merge` (if present) |

**Inputs** (current head):

```
gh pr view <PR> --json labels,reviewRequests,headRefOid
gh api repos/{owner}/{repo}/pulls/<number>/reviews
```

- **Head** = `headRefOid`. Only reviews whose `commit_id` equals head count.
- **Requested humans** = `reviewRequests` logins, minus bots (ai-review and other automation accounts from that repo’s `docs/ai-pr-review/` or workflow). Sofia is the authenticated `gh` user.
- **Other human** = a requested human who is not Sofia.
- **Blocking inlines** = any **ISSUE:**, **TODO:**, or **QUESTION:** in **this** review submission (including on **`COMMENT`** when the event is not `REQUEST_CHANGES`).

**Non-blocking pass** (`APPROVE`, or `COMMENT` with only **SUGGESTION**, **NITPICK**, **PRAISE**, **THOUGHT**, …): no label sync except the **APPROVE** row below.

**APPROVE** (no blocking inlines):

1. If any **other human** has `CHANGES_REQUESTED` on head: do **not** add `approved`; do **not** add `wait-to-merge`; apply **changes-requested removal** (below) only; keep **`wait-review`** until every **other requested human** has at least one review on head.
2. Else add **`approved`**.
3. If an **other human** already has **`APPROVE`** on head: add **`wait-to-merge`** when the label exists on the repo.
4. **`wait-review`:** remove only when every **other requested human** has at least one review on head; if any other requested human has **no** review on head, **keep** **`wait-review`**.
5. **Changes-requested removal:** remove the changes-requested label only when Sofia’s earlier `CHANGES_REQUESTED` on this PR is the sole reason it is still there and **no other human** has `CHANGES_REQUESTED` on head. If another reviewer added or owns **`request-changes` / `changes-requested`**, **never** remove it on Sofia’s **APPROVE**.

**Blocking pass** (`REQUEST_CHANGES`, or `COMMENT` with blocking inlines):

1. Add changes-requested if missing; if already present (including from another reviewer), leave it.
2. Remove **`approved`** (including when the other reviewer had approved).
3. Remove **`wait-to-merge`** if present.
4. **`wait-review`:** remove only when Sofia is the **last** requested reviewer (**every other requested human** already has at least one review on head, and Sofia is about to finish the only remaining slot in `reviewRequests`). If any **other requested human** has **no** review on head, **keep** **`wait-review`**.

Apply adds/removes with `gh pr edit <PR> --add-label … --remove-label …`. Record what changed for §9 chat and §10 ML-186.

## 9. Clean up and report

Run §1 cleanup before chat.

**Chat to Sofia:** PR URL; one-line what changed; `depth` and stack-top `#`; verdict; label counts; **producer pass** (architecture, placement, cleanup, split, **which stack PR should change**); full QA; ISSUE file:lines; worktree confirmed gone.

**Screenshots Sofia must capture** (when §5 could not): a numbered block, each item exactly:

```
**Shot <n> - <short name>**
Commands: <copy-paste shell lines from repo root in worktree>
Must show: <what is visible in the frame>
For PR: #<number where fix or evidence applies, if not this PR>
```

No vague "grab UI evidence." If no shots needed, omit the block.

Do not mirror the chat packet on GitHub review `body`.

## 10. Kineloop ML-186

When Sofia is the reviewer (not the author), each completed pass must touch the tracker under https://loop.zslippy.com/issue/ML-186.

1. Locate the sub-issue whose description lists this PR URL or this stack's root PR.
2. Add a comment (pt-BR): one line per PR reviewed with GitHub verdict, link to the submitted review, GitHub state labels changed, and any ISSUE still open.
3. If the sub-issue is missing, create or refresh it using the same rules as the "PR review requests -> Kineloop ML-186" routine (one issue per stack, merge order in the body).

If Kineloop MCP is not authenticated, output the comment body in chat for Sofia and flag `ML-186 not updated`.
