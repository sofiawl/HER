# Cursor models for HER subagents

Probed on Sofia's Cursor account (Task + `generalPurpose`, 2026-10-15). Re-probe if delegation starts failing.

## Routing (read before picking a slug)

| Model | Actually good at | Weak at | Use for |
|---|---|---|---|
| `grok-4.7-high-fast` | gh/git, running tests and CI locally, fixing threads, reading code for **facts**, spikes | Sofia voice, steelman, ISSUE vs SUGGESTION on someone else's PR, careful pt-BR prose | **Default implement + QA pipeline** |
| `composer-2.5-fast` | Tiny in-repo edits, append one file, grep | Long reasoning, voice | Haiku chores with **no** shell pipeline |
| `gemini-4-argon-medium` | Huge read-only pass over folders/docs | Writes, voice, verdicts | Inventory and source **reading** only |
| `claude-sonnet-5-5-high` | Voice (humanizer), ledger rows with numbers, nuanced English | — | **All Sofia-facing copy** and evidence ledgers |
| `gpt-5.6-sol-medium` | Cross-vendor check | Voice | **Second agent** on numbers after a Sonnet/Grok writer |
| `claude-opus-5-5-medium` | High judgment | Cost/quota | Verdicts, steelman, orchestrator review; else **main** |

Do **not** spread jobs evenly across vendors. Prefer **Grok** whenever the chore is "clone, run, read code, fix, push evidence". Prefer **Sonnet** only when the output is **your voice** or **ledger accuracy**. Prefer **Gemini** only for **bulk read**. **Composer** is the small-tool fallback when Grok would be idle overhead.

## Allowlist

| Slug | Subagent OK | HER tier | Notes |
|---|---|---|---|
| `inherit` | Yes | parent | Parent chat when allowed |
| `grok-4.7-high-fast` | Yes | sonnet | **Primary** for implement/QA (tier sonnet, not "cheap haiku") |
| `cursor-grok-4.6-high-fast` | Yes | sonnet | Fallback if 4.7 fails |
| `composer-2.5-fast` | Yes | haiku | Narrow file/grep chores |
| `gemini-4-argon-medium` | Yes | haiku | Read-heavy inventory |
| `muse-spark-1.3-high` | Yes | haiku | Optional haiku if others busy |
| `claude-sonnet-5-5-high` | Yes | sonnet | Voice + ledger + opus fallback for review |
| `gpt-5.6-sol-medium` | Yes | sonnet | Independent number check |
| `claude-opus-5-5-medium` | Quota-dependent | opus | High judgment |
| `claude-opus-5-thinking-high` | No | — | Not on allowlist |
| `claude-fable-5-1-thinking-high` | Policy gate | — | Accept policy in UI |

Orchestrator `plan.json` `model` must be an OK slug. **`lazy` / `judge` implement steps:** default `grok-4.7-high-fast`. **`to-pr write` / report `.tex`+humanizer:** `claude-sonnet-5-5-high`.

## Tier defaults (only when no job row matches)

| Tier | Primary | Fallback |
|---|---|---|
| haiku | `composer-2.5-fast` | `gemini-4-argon-medium` |
| sonnet (implement) | `grok-4.7-high-fast` | `cursor-grok-4.6-high-fast`, then `claude-sonnet-5-5-high` |
| sonnet (voice/ledger) | `claude-sonnet-5-5-high` | `gpt-5.6-sol-medium` (never Grok for voice) |
| opus | `claude-opus-5-5-medium` | main, then `claude-sonnet-5-5-high` (not Grok for verdicts) |

## Job → slug

| Job | Cursor slug | Fallback |
|---|---|---|
| Fetch PR metadata, threads, reviews, diff stats | `grok-4.7-high-fast` | `composer-2.5-fast` |
| `git diff --shortstat`, branch create, stack table updates | `grok-4.7-high-fast` | `composer-2.5-fast` |
| Judge: detect stack/tools, worktree + deps setup | `grok-4.7-high-fast` | `composer-2.5-fast` |
| Handoff: repo state, open PRs, processes | `grok-4.7-high-fast` | `composer-2.5-fast` |
| Lazy: mechanical multi-file edits, installs, versions | `grok-4.7-high-fast` | `composer-2.5-fast` |
| to-pr: map diff, QA commands, run thin gate | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| pr-review: read changed files vs checklist | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| pr-review: run PR QA steps in worktree | `grok-4.7-high-fast` | `gpt-5.6-sol-medium` |
| Lazy: codebase search (ladder rung 2) | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| address-review: large thread fix | `grok-4.7-high-fast` | `gpt-5.6-sol-medium` |
| Judge: correctness metrics (tests, lint, types), interpret | `grok-4.7-high-fast` | `gpt-5.6-sol-medium` |
| Judge: timing metrics (sequential, never parallel) | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| Research: last30days run, build spike | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| Grill / grill-me / grilling: read code for fact | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| Debate: check factual claim | `grok-4.7-high-fast` | `claude-sonnet-5-5-high` |
| Report: latexmk, log grep (shell) | `grok-4.7-high-fast` | `composer-2.5-fast` |
| Memory install: binaries, systemd, docker, hooks on disk | `grok-4.7-high-fast` | `composer-2.5-fast` |
| Report: folder inventory, copy images (read tree) | `gemini-4-argon-medium` | `composer-2.5-fast` |
| Research: read sources (sources mode) | `gemini-4-argon-medium` | `grok-4.7-high-fast` |
| Report: read sources, draft ledger rows | `claude-sonnet-5-5-high` | `gpt-5.6-sol-medium` |
| Report: independent number check (not the writer) | `gpt-5.6-sol-medium` | `claude-sonnet-5-5-high` |
| to-pr: draft + humanizer (`pr-body`) | `claude-sonnet-5-5-high` | main |
| Report: write `.tex` + humanizer (`report-prose`) | `claude-sonnet-5-5-high` | main |
| Teach: append block to effort note | `composer-2.5-fast` | `grok-4.7-high-fast` |
| Research: verify cited URLs | `composer-2.5-fast` | `grok-4.7-high-fast` |
| Grill / grill-me / grilling: path lookup | `composer-2.5-fast` | `grok-4.7-high-fast` |
| to-pr: final stack/diff review before open | `claude-opus-5-5-medium` | main |
| Report: rank + steelman Main results | `claude-opus-5-5-medium` | main |
| pr-review: draft inline + summary (ISSUE vs SUGGESTION) | `claude-opus-5-5-medium` | `claude-sonnet-5-5-high` |
| Judge: verdict (risky change) | `claude-opus-5-5-medium` | main |
| Lazy: multi-file design | `claude-opus-5-5-medium` | main |
| Lazy: final review (risky diff) | `claude-opus-5-5-medium` | main |
| Debate: steelman costly option | `claude-opus-5-5-medium` | main |
| Research: heavy synthesis | `claude-opus-5-5-medium` | main |
| address-review: optional final pass (many threads) | `claude-opus-5-5-medium` | main |
| `/her:her` orchestrator: step review | `claude-opus-5-5-medium` | main |
| Judge: normal verdict | main | — |
| Lazy: small change | main | — |
| pr-review: post review (`gh api`) | main | — |
| address-review: dismiss/fix small thread | main | — |
| `/her:her`: grill, plan, loop, Kineloop with Sofia | main | — |
