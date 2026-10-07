---
name: judge
description: Evaluate a change with the metrics that matter for this project, measured before (base branch) and after (current changes) under the same conditions, then give a verdict (ship, fix first, needs discussion). Use when Sofia says "judge", "/her:judge", "evaluate metrics", "measure this", "benchmark before and after", "did this regress", "is it ready", or before /her:to-pr. Picks metrics from the stack (tests, coverage, latency p50/p95, throughput, memory, bundle size, build time, query count, cold start, lint/type errors, accessibility) and asks when in doubt. Enforces the verification gate.
argument-hint: "[base branch, default main] [metric hints]"
---

# /her:judge

Mode: caveman.

Measure before and after. Evidence only. Verdict at the end.

## 1. Inspect the project

- Stack: manifests, lockfiles, language, framework, runtime.
- The change: `git diff --stat <base>...HEAD` plus uncommitted work. What it touches (hot path, UI, DB, build, API, docs only).
- Existing tooling: test runner, coverage config, benchmarks, perf scripts, load tests, bundle analyzer, lint, type checker, CI workflows (`.github/workflows`, etc). Prefer the commands CI runs.
- Base: argument, else `main`.

## 2. Pick metrics

Choose the 2-5 metrics that matter most for this change. Always include tests pass and lint/type errors when the project has them. Then add by what the change touches:

| Change touches | Candidate metrics |
|---|---|
| Any logic | Test pass count, coverage (target 80%) |
| Request/hot path | Latency p50/p95, throughput |
| Data layer | Query count per request, query time |
| Frontend | Bundle size, accessibility violations, render time |
| Long-running/service | Memory peak, cold start |
| Build/tooling | Build time, CI duration |

Any doubt (unclear which metric matters, no tooling exists, measurement is costly or slow, metric needs a new dependency): ask Sofia with the AskUserQuestion tool. Offer the best 2-4 options, mark one as recommended with a one-line why, and allow her to choose her own. Never install tools without asking.

## 3. Measure

Same machine, same commands, same inputs, same env for both sides.

- BEFORE: prefer a temporary worktree of the base: `git worktree add ../<repo>-judge-base <base>`, install deps there if needed, run. Fallback `git stash` only if a worktree is impossible, and restore with `git stash pop` right after.
- AFTER: run in the current tree with current changes.
- Noisy metrics (latency, throughput, memory, build time): warm up once, then at least 5 runs per side. Report the median, note the spread.
- Deterministic metrics (tests, lint, bundle size, query count): one run per side.
- Cleanup: `git worktree remove ../<repo>-judge-base`. Confirm the working tree matches its state before judge ran.

## 4. Verification gate

Iron law: no success claim without fresh evidence from a command run in this turn. For each claim: identify the proving command, run it fully, read the output and exit code, then state the claim with evidence. Red flags: "should", "probably", "seems", "looks fine", trusting old runs or agent reports. Full gate: [VERIFY.md](VERIFY.md).

## 5. Report

```
| Metric | Before | After | Delta | Verdict |
|---|---|---|---|---|
| Tests | 212 pass | 219 pass | +7 | PASS |
| Coverage | 78.1% | 81.4% | +3.3 pt | PASS |
| p95 latency | 41 ms | 44 ms | +7% | WARN |
```

Row verdict: PASS (same or better, or target met), WARN (small regression or within noise), FAIL (regression, test failures, target missed).

Then:

```
Overall: <ship | fix first | needs discussion>
Why: <one terse line>
Evidence: <commands run, exit codes>
```

- ship: no FAIL, WARNs explained.
- fix first: any FAIL with a clear fix. List the fixes.
- needs discussion: tradeoff (gain vs regression), or metrics conflict.

Coverage under 80%: FAIL for new code, WARN if it only fails to raise a legacy low baseline.

## Headless

Prompt says it runs headless under the HER orchestrator: never ask Sofia (no AskUserQuestion, no quiz). Take metric choices from the `decisions.md` path in the prompt. A needed decision missing: end with `BLOCKED: needs Sofia: <decision>`.

Write the verdict JSON to the path given in the prompt: `{"verdict": "ship|fix|needs-discussion", "why": "<one sentence>", "table": "<metrics table as markdown>"}`. Can't run commands: write verdict `needs-discussion`, why saying so, and end with `BLOCKED: cannot run commands`.

## Next

Verdict ship: suggest `/her:to-pr`, and pass the table to it. Otherwise: list fixes, suggest `/her:lazy` for them, rerun judge.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Detect stack, available tools and versions | `haiku` | First |
| Set up the base worktree and install deps | `haiku` | In parallel with the above |
| Run correctness metrics (tests, coverage, lint, types) and interpret failures | `sonnet` | Base and current in parallel |
| Run timing metrics (latency, build time, cold start) | `sonnet` | One agent, sequential, never in parallel with other runs |
| Verdict when the change is risky (auth, data, migrations, money, public API) | `opus` | Gets the diff and the metrics table |
| Verdict otherwise | main | |
