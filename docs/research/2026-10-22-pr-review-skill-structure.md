# PR review skill: what to check, by project, vs GitHub AI review

**Confidence:** High for kinebot-cosmos automation boundaries (Tier 1 repo docs); medium for cross-industry human focus (Tier 2 blogs agree, no single spec).

## Findings

### 1. What HER already specifies (baseline)

`/her:pr-review` delegates **item-level** rules to each target repo and keeps **process + bar** in HER:

| Layer | Where | What it says |
|---|---|---|
| Process | `skills/pr-review/references/pr-review.md` §1–8 | Isolated worktree, load repo checklists, read existing GitHub reviews, read diff + PR context, **run PR QA steps before commenting**, post inlines + empty review body, chat report to Sofia |
| Repo files | Same file §2 | **kinebot-standard:** `checklist-general`, layer maps, `frontend-extras`; **cosmos:** `checklist-general` + `checklist-python`; **lambda:** `CLAUDE.md`; **research:** cosmos checklists via API with relaxed §6 |
| Human-only bar | Same file §6 | Google-style code health; every changed line; extra scrutiny on auth, money, migrations, concurrency, hot paths; size/template gates; stacked-PR rules |
| When checklist silent | Same file §6 | Design, correctness/edge cases, complexity, tests on new paths, naming, security, performance, docs, AI smells |
| vs bot | Same file §2, §3 | Do **not** reuse `review_script.sh` / `prompt.md`; do not re-flag issues already raised (reinforce wrong dismissals only) |

HER does **not** embed the text of `checklist-general.md` or `checklist-python.md`; reviewers must open them in the PR repo ([`references/pr-review.md`](../../skills/pr-review/references/pr-review.md) §2).

### 2. What kinebot-cosmos GitHub Actions already review (automation layer)

From `docs/ai-pr-review/README.md` on **pixfy/kinebot-cosmos** (Tier 1):

- **Triggers:** `ai-review.yml` on PR open / ready_for_review; `/review` command workflow ([README](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md)).
- **Scope:** Two passes, `python` (`app/`, `tests/`) and `general` (migrations, CI, config, docs, etc.), each with its own prompt + checklist.
- **Output:** Inline Conventional Comments on **added lines only**, plus one **upserted bot summary** with verdict ([README](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md)).
- **Idempotency:** Re-run replaces prior bot output; respects human `CHANGES_REQUESTED` as context so the model does not repeat ([README](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md)).
- **CI gates the bot explicitly does not duplicate:** Ruff, Ruff-format, mypy strict ([`prompt.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/prompt.md) “Linters own mechanical style”).
- **Separate automation:** `scripts/guidelines_review/` (Jev) owns **repo conventions** (layering, exception types, schema placement, logging layout, etc.); bot prompt says do not flag conventions unless breaking them causes a defect ([`checklist-python.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/checklist-python.md), [`prompt.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/prompt.md)).
- **Bot mission:** Exhaustive defect pass on every added line against checklists (security, bugs, async, SQLAlchemy, tests that do not test, etc.) ([`prompt.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/prompt.md) “NEVER SKIP CHECKS”).

**General checklist** adds the same “no mechanical style” rule for non-core paths ([`checklist-general.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/checklist-general.md): Ruff/mypy own formatting; focus correctness, secrets, migrations, CI YAML, etc.).

### 3. Tier-1 “what human review is for” (Google)

[Google eng-practices – Standard](https://google.github.io/eng-practices/review/reviewer/standard.html): primary goal is **overall code health improving over time**; approve when the CL **clearly improves** the system even if not perfect; nits prefixed, not blockers.

[Google – What to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html) orders human attention as:

1. **Design** (fit in codebase, integration, timing of the feature)
2. **Functionality** (intent, users, edge cases, concurrency; validate behavior when user-facing)
3. **Complexity** / over-engineering
4. **Tests** (existence **and** whether tests are meaningful, not self-invalidating)
5. Naming, comments, style, consistency, documentation
6. **Every line** in scope, plus **whole-file and whole-system context**

Google treats style blocked only when the **style guide** requires it; otherwise “Nit:” ([looking-for – Style](https://google.github.io/eng-practices/review/reviewer/looking-for.html)).

### 4. Tier-2 industry consensus when bots + CI exist

Sources agree on a **three-layer** model (mechanical → automated review → human judgment):

| Layer | Typical owner | Examples |
|---|---|---|
| Pre-human gate | CI / linters / tests | Format, types, unit tests green, SAST, secrets scan ([Codacy blog](https://blog.codacy.com/ai-breaking-code-review-how-engineering-teams-survive-pr-bottleneck), Tier 2) |
| First pass on diff | AI bot | Line-anchored defects, severity grouping ([cosmos README](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md), Tier 1) |
| Human | Teammate / HER skill | Architecture, product fit, trace critical paths, duplication across repo, dismissals audit, merge accountability ([GitHub – merge button](https://github.blog/ai-and-ml/generative-ai/code-review-in-the-age-of-ai-why-developers-will-always-own-the-merge-button/), [GitHub – agent PRs](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/), [Anthropic – code review](https://claude.dev/blog/solving-code-review-at-anthropic/), Tier 2) |

**High-ROI human checks** called out for agent-written PRs ([GitHub – agent PRs](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)):

- **Reuse blindness:** new helpers that duplicate existing utilities (search repo, require consolidation).
- **Hallucinated correctness:** compiles and tests pass but wrong on boundaries, permissions, races; trace one critical path; prefer a test that would fail pre-fix.

**Anthropic** scales human approvals by **risk tier** (docs vs auto-updater vs highest-risk paths); agents never count as humans ([Anthropic blog](https://claude.dev/blog/solving-code-review-at-anthropic/)). Humans still own “should we build this?”, risky domains, and reading **evidence** (test output, commands run).

### 5. By project type (your matrix + where automation differs)

| Project | HER strictness today | Checklist source | Typical GHA bot (cosmos pattern) | Human skill should emphasize |
|---|---|---|---|---|
| **kinebot-cosmos** | Strict §6; 750 line gate; template gate | Full python + general checklists | Exhaustive added-line defect scan + summary | QA execution (§5), design/stack context, bot dismissals, cross-file reuse, integration behavior QA catches |
| **kinebot-standard** | Middle; `# Evidence` comment before approve | Layer maps + general (+ frontend extras) | May or may not have same `ai-review` (not verified in this note) | Layer violations that need product judgment, E2E/QA evidence, Sofia-last-approver workflow |
| **kinebot-research** | Relaxed §6; science/data-loss blockers | Cosmos checklists, loose verdict | Often no bot or same bot with wrong bar | Runnable PR QA, wrong science, artifact clobbering; not missing unit tests |
| **kinebot-lambda** | `CLAUDE.md` | Repo-specific | Unknown per repo | Whatever `CLAUDE.md` + CI actually run |

### 6. What **not** to ask on GitHub when cosmos bot + CI already ran

Do **not** duplicate (Tier 1 cosmos docs + HER §3):

| Already covered | Do not re-ask author on GitHub |
|---|---|
| Ruff / format / import order / `%s` logs / missing type hints | Style nits ([`prompt.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/prompt.md)) |
| Guidelines review (Jev) conventions | Layering, “use custom exception”, schema folder placement, unless you tie to a **defect** ([`checklist-python.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/checklist-python.md)) |
| Bot inline on same hunk | Same issue reworded (HER §3) |
| Green CI test job | “Add tests” when tests exist and pass unless **quality** of tests is wrong ([Google – Tests](https://google.github.io/eng-practices/review/reviewer/looking-for.html)) |
| Bot exhaustive checklist on added lines | Second pass of identical checklist items with no new evidence |
| PR template QA steps as homework | “Please run the test plan” to author ([`COMMENT-VOICE.md`](../../skills/pr-review/COMMENT-VOICE.md)) |

**Still fair game for human/HER review** even after bot:

| Gap | Why bot/CI weak here |
|---|---|
| **Run PR QA** in worktree | Bot reads diff + metadata, does not execute PR QA steps ([HER §5](../../skills/pr-review/references/pr-review.md)) |
| **Design / belongs in system?** | Not in defect checklist ([Google – Design](https://google.github.io/eng-practices/review/reviewer/looking-for.html)) |
| **Duplicate utility elsewhere in repo** | Bot context is diff-local ([GitHub – agent PRs](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md) deliberately does not feed all prior comments) |
| **Wrong dismiss** of bot/human | HER §3 |
| **Stacked PR / deferred wiring** | Product merge order ([HER §6 stacked PRs](../../skills/pr-review/references/pr-review.md)) |
| **Template/intent** | Missing “why”, unusable QA (HER §4, §6 template gate) before deep pass |
| **Merge accountability** | Human owns approve ([GitHub – merge button](https://github.blog/ai-and-ml/generative-ai/code-review-in-the-age-of-ai-why-developers-will-always-own-the-merge-button/)) |

### 7. Comment format (Conventional Comments vs your empty summary)

[Conventional Comments](https://conventionalcomments.org/) (Tier 1 for label semantics): structured `label [decorations]: subject` + optional discussion; suggests occasional **praise**; machine-parseable.

HER [`COMMENT-VOICE.md`](../../skills/pr-review/COMMENT-VOICE.md): uppercase **ISSUE:** / **SUGGESTION:** inlines; **empty** review `body` (no bot-style summary recap). Compatible with conventional labels on inlines; conflicts with conventional “leave praise” and cosmos bot **summary upsert** (you already chose no HER summary).

## Conflicts

| Topic | A | B | Resolution for your skill |
|---|---|---|---|
| Checklist depth | Cosmos bot: exhaustive every line ([`prompt.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/prompt.md)) | HER §6: human “apply checklist fully” on cosmos | When `ai-review` green: human skill should **not** mirror bot checklist; switch to §6 “where checklist silent” + QA + dismissals + design ([HER §2 “catches what the bot misses”](../../skills/pr-review/references/pr-review.md)) |
| Approve bar | Google: approve if clear improvement ([standard](https://google.github.io/eng-practices/review/reviewer/standard.html)) | HER cosmos: strict REQUEST_CHANGES on borderline | Keep repo strictness table; research vs cosmos unchanged |
| Praise | Conventional Comments encourages sincere praise ([conventionalcomments.org](https://conventionalcomments.org/)) | HER sparse inlines, no summary | Optional **PRAISE:** inline only when rare and specific; not required |

## What this means for you

1. **Split the skill into two explicit modes** in `references/pr-review.md`: **`automation_present`** (cosmos-style: read bot + CI + guidelines_review first; human adds only gaps above) vs **`automation_absent`** (research/lambda/no workflow: keep checklist-first §6 as today).
2. **Make §5 (QA)** the non-negotiable human differentiator everywhere; the bot docs never replace it.
3. **Replace “apply checklist-python fully” for cosmos** with a short **human add-on list**: design, QA outcomes, cross-repo duplication search, critical-path trace, stacked-PR scope, audit bot dismissals.
4. **Structure doc sections** you can paste into the skill: (A) Preconditions (CI green? bot finished? read bot summary?), (B) Do-not-duplicate table, (C) Must-check table by repo strictness, (D) Output (inlines only, empty body, chat recap).
5. **kinebot-standard** may need its own row in the do-not-duplicate table once you confirm which GHA jobs exist there (this note only verified cosmos `docs/ai-pr-review`).

## Further reading

- [Google eng-practices reviewer guide](https://google.github.io/eng-practices/review/)
- [pixfy/kinebot-cosmos `docs/ai-pr-review/README.md`](https://github.com/pixfy/kinebot-cosmos/blob/main/docs/ai-pr-review/README.md)
- [GitHub: agent pull requests how to review](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)
- [Anthropic: solving code review](https://claude.dev/blog/solving-code-review-at-anthropic/)
- [AkitaOnRails deploy/review premissa (your voice reference)](https://akitaonrails.github.io/2026/09/22/parem-de-inventar-desculpas-e-facam-mais-deploy-a-premissa-mudou/) (Tier 3 for process philosophy, not checklist items)

## Implemented spec (grilling 2026-10-22)

Canonical procedure: [`skills/pr-review/references/pr-review.md`](../../skills/pr-review/references/pr-review.md).

| Topic | Rule |
|---|---|
| Automation present | Green ai-review check **or** bot inlines |
| Fallback §7 | Both missing → full repo checklists |
| Depth | **Deep** on single PR and stack-top; **light** on lower stack subs |
| Stack-top | Highest `Order` in proposal merge table (`to-pr/TEMPLATE.md`) |
| Routing | Inlines name **PR #** when fix belongs elsewhere in stack |
| Layer wrong | **SUGGESTION**; **ISSUE** only explicit map + `app/` risk |
| Dead code | **ISSUE** public unused unless stack scaffold; stack carve-out |
| Deep pass | Not judge; max 1–2 extra commands; producer notes in chat |
| Evidence | `# Evidence` via `gh pr comment --body-file --attach` before **APPROVE** on standard **and** cosmos |
| Sofia screenshots | Chat block: commands + must show + target PR # |
| GitHub review | Inlines only; `body` empty |
