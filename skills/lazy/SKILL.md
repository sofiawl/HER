---
name: lazy
description: Write the least code that fully solves the task, like the laziest senior dev on the team. Use for any coding work (feature, bug fix, refactor, script, config) when Sofia says "lazy", "/her:lazy", "simplest way", "minimal", "don't overbuild", "YAGNI", or when implementing a sub from /her:to-pr plan. Climbs a ladder (does it need to exist, already in the codebase, stdlib, native platform, installed dependency, one line, minimum new code) and stops at the first rung that works. Levels lite, full (default), ultra.
argument-hint: "[lite|full|ultra] <task or sub plan path>"
---

# /her:lazy

Mode: caveman.

Laziest senior dev: least new code, full correctness. Lazy about code, never about thinking.

## Level

Parse first arg. Default `full`.

- `lite`: prefer existing code and stdlib, allow small helpers if they read clearer.
- `full`: whole ladder, no new abstraction, no new dependency without asking.
- `ultra`: challenge the requirement itself. Propose the smallest change that meets the real need, even if it trims scope. Say what was trimmed.

## Before code

1. Understand the problem. Read the task, the sub plan, the code it touches. Restate it in one line if unclear. Unclear still: ask Sofia.
2. Bug: find the root cause, not the symptom. Grep every caller and every copy of the pattern before editing. Fix at the source so all callers benefit.

## The ladder

Climb in order. Stop at first rung that works.

1. Does it need to exist at all? Speculative need: skip, say so.
2. Already in the codebase? Search for a helper, util, type, component, config doing it. Reuse.
3. Stdlib covers it? Use it.
4. Native platform feature? Browser API, DB constraint, CSS, shell tool, framework built-in.
5. Dependency already installed? Check the lockfile/manifest. Use it. Never add a new one without asking.
6. One line? Write one line.
7. Only then: minimum new code, inline, in the file that needs it.

## Hard rules

- No unrequested abstractions: no interface, factory, base class, config option, plugin point or generic param for a single use.
- Deletion beats addition. Dead code, duplicate paths, unused flags near the change: remove when safe and in scope.
- Smallest diff that is correct. No drive-by reformatting or renames.
- No code comments (HER rule 2). Names carry meaning. Shortcuts are reported in chat, never marked in code.
- Match the existing style of the file.

## Never lazy about

- Input validation at trust boundaries.
- Security: authz, injection, secrets, unsafe deserialization.
- Accessibility: labels, roles, keyboard, contrast.
- Error handling that prevents data loss.
- Understanding the problem.

Cutting any of these is a bug, not laziness.

## Leave one check behind

Non-trivial logic (branch, loop, parser, math, money, date, security path) gets one runnable check: a focused test in the existing test setup, or an assert-based script if none exists. Trivial one-liners and glue: no test needed. Run the check before replying. Paste the command and result.

## Commit and self-check

- Commit along the way: one conventional commit per logical change, following HER rule 9, on the current branch. Run by the HER orchestrator: never create or switch branches, never push.
- Before finishing, run the repo's tests and the lint/type checks CI runs (read CI config, Makefile, package scripts). Fix failures you caused. Cannot fix: end the reply with `BLOCKED: <why>`.

## Output

Code first. Then at most 3 lines:

```
Decision: <key decision and why, one terse line>
Skipped: <thing>, add when <condition>
Check: <command run> -> <result>
```

Drop lines that do not apply. Deliberate shortcuts always get a `Skipped:` line. No preamble, no recap of the diff.

## Next

Working from a sub plan (`.scratch/<feature>/subs/NN-*.md`): tick its acceptance criteria, keep the diff under its 750 lines, then suggest `/her:judge`, then `/her:to-pr write sub`.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Search the codebase for something that already does it (ladder rung 2) | `sonnet` | Before writing code |
| Mechanical edits across many files, installs, version checks | `haiku` | Parallel by file group |
| Multi-file change with real design choices | `opus` | One agent, gets the plan and the ladder |
| Final review of a risky diff (auth, data, migrations, money) | `opus` | Before calling it done |
| Small changes | main | Most of the time |
