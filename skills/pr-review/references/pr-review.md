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
