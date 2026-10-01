# HER verification gate

Shared by `/her:judge` and `/her:to-pr`. Read and apply before any claim that work is done, fixed, passing or ready.

## The law

No claim of completion or success without fresh evidence. Fresh means: produced by a command you ran in this turn, whose full output you read. Evidence from an earlier turn, from memory, from a subagent's report or from "it worked last time" does not count.

This law covers more than the literal words "done" or "fixed". It covers any hedged, roundabout or implied way of saying the work is finished or correct, and rewording the claim does not get you out of it. It also fires before you move on to the next task and before you hand work off to another agent or subagent, not only at the moment you announce success.

## The gate

Before saying anything like "done", "fixed", "tests pass", "builds", "ready for PR":

1. **Identify** the command that would prove the claim. One claim, one proving command.
2. **Run** it fully, now. The whole suite or target, not a subset picked to pass. No cached or partial runs unless the project caches correctly by design.
3. **Read** the whole output and the exit code. Count failures, errors, skips and warnings.
4. **Compare** the output to the claim. Does it actually prove it?
5. **State** the claim together with the evidence: command, exit code, key numbers. If the evidence does not support the claim, state what it does show instead.

Skipping any step means the claim is unverified. Say "unverified" rather than claim success.

## What proves what

| Claim | Needs | Not enough |
|---|---|---|
| Tests pass | Test command, exit 0, 0 failures | A previous run, "should pass" |
| Build succeeds | Build command, exit 0 | Lint passing, editor with no red |
| Lint/types clean | Linter/type checker, 0 errors | Tests passing |
| Bug fixed | Reproduction that failed before, passes now | Code changed and looks right |
| Regression test valid | Test fails without the fix, passes with it | Test passes once |
| Requirements met | Each acceptance criterion checked against output | Tests green |
| Subagent finished task | Its diff inspected and checks rerun by you | Its success message |
| Metric improved | Before and after runs, same conditions | One after-run |

For a regression test, run it once with the fix removed and confirm it fails, then put the fix back and confirm it passes. A test you only ran once, already in the fixed state, has not proven anything.

## Red flags

Stop and run the gate when you notice:

- Words like "should", "probably", "seems to", "likely", "I think it works", "looks good".
- Satisfaction before evidence: "Great", "Perfect", "All set".
- About to commit, push or open a PR without a fresh run.
- Trusting a tool or agent report without checking.
- "Just this once", "it is a tiny change", "I am confident".
- Being tired of the task and wanting it over.
- Checking half the surface and treating that as good enough.
- Phrasing a claim differently so it feels like it slips past this rule.

Confidence is not evidence. A tiny change still needs its proving command. A rule broken in spirit is still broken even when the wording avoids the exact trigger phrase.

## Reporting format

```
Claim: <what is true>
Evidence: <command> -> exit <code>, <key numbers>
```

Failures are reported the same way, with the real numbers. Never soften a failure into "mostly works".
