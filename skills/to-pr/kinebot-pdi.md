# kinebot-pdi PR body

Use this file instead of TEMPLATE.md when the repo is `kinebot-pdi`. Detection: `.github/pull_request_template.md` exists and contains `Validation Performed` and `Reviewer Context`. Read that file first and copy its headings and order exactly. VOICE.md still sets the tone.

```markdown
## Summary

## Root Cause / Motivation

## Scope of Changes

## Validation Performed

### Validation Output

## Evidence

## Risk Assessment and Rollback

## Reviewer Context

## Author Checklist
```

## Global rules

- **Never write `N/A`, `None` or `n/a`** in any section. Nothing to say: omit the bullet, or leave the section empty under its heading.
- Delete the template's HTML comments from the final body.
- No diff stats anywhere in Reviewer Context (`~119 lines vs base`, `N files`, `+A/-D`). TEMPLATE.md's `N files · +A/-D` size format does not apply here.
- Never invent screenshots, issue links or PR numbers. Placeholder and tell Sofia.
- Same local-path ban as VOICE.md: no `.scratch/`, uncommitted specs or local QA notes in the body.
- Title, branch and commit rules are unchanged (HER rule 9 and TEMPLATE.md Titles).

## Summary

2 to 5 bullets, each substantive. A reviewer should understand what landed without opening every file. Bold lead, reason right after. Concrete names in backticks (modules, fields, CLI flags, real numbers).

Not a changelog of files (that is Scope of Changes) and not one vague line like "adds NIOSH support".

## Root Cause / Motivation

What problem triggered this and why now. Tracker link as `[<CARD>](https://loop.zslippy.com/issue/<CARD>)` when the card is known. Bug fix: the failing behavior in one or two sentences. Feature or refactor: the need it answers. Empty when there is no motivation worth stating beyond Summary.

## Scope of Changes

Major files and modules touched, grouped so a reviewer can navigate. Paths in backticks, one short phrase each. Sub PRs: only what this PR touches.

## Validation Performed

A checklist for the **reviewer** to run, not a record of what the author ran. Every box stays unchecked `[ ]`.

Keep the commands CI and AGENTS.md define, and drop the ones that do not apply:

```markdown
- [ ] `uv run --extra dev ruff check .`
- [ ] `uv run --extra dev mypy --config-file pyproject.toml`
- [ ] `uv run --extra dev pytest -q tests`
- [ ] `uvx --from pre-commit pre-commit run --all-files`
```

Add a PR-specific line when a focused command helps (a single test file, a CLI run such as `uv run python scripts/kinebot_reba.py <video> --debug`), with the expected result in plain words.

Never tick a box. Never paste author CI output here.

### Validation Output

Reviewer territory: they paste output after running QA. Leave the heading and an empty `text` fence, or only the heading. Never fill it with the author's run.

## Evidence

A real proof artifact: a screenshot, a CLI capture, a before/after of the behavior.

- Sofia will add it later: one placeholder line, `[screenshot: <what to capture>]` (e.g. `[screenshot: scripts/kinebot_reba.py output with unmeasured_segments on frame 0]`). List every placeholder for Sofia at the end of the reply.
- Never use agent prose, a test narrative, or sentences like "tests replay fixture cases" or "pytest passes" as evidence.
- Nothing to show yet and no capture is expected: leave the section empty.

## Risk Assessment and Rollback

Keep the template's two bullets, `Risk:` and `Rollback:`. Fill each with a real statement (what could break, how to revert: usually `revert this PR`, plus any config or data to undo). If one has nothing real to say, drop that bullet rather than writing `N/A`.

## Reviewer Context

What the reviewer cannot see from the diff:

- design decisions and the trade-off behind them
- domain method (REBA/RULA/NIOSH rule, formula, worksheet source) and its limits
- traps: behavior that looks like a bug but is expected
- cross-repo dependencies and links to the twin PR
- merge order hints (stack position, what must land first)

Never line counts, diff stats or size comparisons. Never process diary or what was left alone on purpose unless the reviewer would misread the diff without it.

## Author Checklist

Copy the template's items. Tick only what is true of this diff (focused, no secrets, dependencies justified, tests or reproducible evidence present). Leave the rest unchecked.

## Stack levels

- **feat**, **proposal**: same headings. Summary carries the why and scope; proposal Reviewer Context holds the merge-order table (`| Order | PR | Scope | Issue |`, no size column), the end-to-end flow and the graveyard. Package diagrams go on the proposal.
- **sub**, **single**: same headings, shorter. Reviewer Context only when there is something real to say.

## Verify

`../judge/VERIFY.md` still applies to every claim in the body. Because Validation is a reviewer checklist, the author's gate run is not pasted in. Run the gate for Sofia's own confidence and mention the result in chat, not in the PR.
