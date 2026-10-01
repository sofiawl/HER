# Sofia's PR template, and what goes in each part

The skeleton is fixed. Keep the headings in this order. Emoji shortcodes in the type list are the one allowed emoji exception.

```markdown
# What type of PR is this? (check all applicable)

-   [ ] :pizza: Feature
-   [ ] :bug: Bug Fix
-   [ ] :fire: Optimization
-   [ ] :man_technologist: Refactor
-   [ ] :books: Documentation Update
-   [ ] :test_tube: Tests

## Description

## Related Tickets & Documents

## Screenshots, Recordings

### Before

### After

## QA Instructions

## Added/updated tests?

_We encourage you to keep the code coverage percentage at 80% and above._

-   [ ] Yes
-   [ ] No, and this is why: _please replace this line with details on why tests
        have not been included_
-   [ ] I need help with writing tests

## [optional] Are there any post deployment tasks we need to perform?

## [optional] What gif best describes this PR or how does it make you feel?
```

General rules:

- Tick every type that applies, based on the diff (a sub that adds tests and docs ticks those too).
- Tests section: keep only the ticked option, delete the other two lines. Keep the coverage line on sub and single PRs.
- `### Before` and `### After` stay even when empty.
- Optional post-deployment section: delete it when there is nothing to do. Fill it with migrations, env vars, flags, backfills.
- GIF section: always present, left empty for Sofia. She picks the GIF herself: never suggest one, never write a URL.
- **Related tickets need a real URL.** Ask Sofia for the tracker link **before writing** the PR body. Never invent Linear/Loop/Jira URLs, never put plain IDs with no link, and never reuse a link from an older PR until she confirms it. Never link or name paths that are only on Sofia's machine (`.scratch/`, local QA notes, uncommitted specs).
- Links that do belong: issue tracker URLs Sofia gave, other open PRs in the stack, docs that are **in the diff or already on the target branch**.
- Sizes are written `N files · +A/-D`.
- **Reviewer-facing only.** Another developer reviews from the GitHub diff and a fresh clone. Anything they cannot open from that clone does not go in the PR body.

## Titles

Copy the repo's pattern from recent PRs. Defaults:

| Level | Title |
|---|---|
| feat | `feat: <ID> - <summary>` |
| proposal | `proposal: <ID> - <summary>` |
| sub | `sub: <ID> - <summary>` |
| single | `<type>: <ID> - <summary>` (or no ID if none) |

Lowercase type prefix. Sub PRs are never titled `feat:`.

## feat

The umbrella. Short, it's a promise, not a diff.

- **Description**: what the feature is for and who uses it, what this feat covers now, what comes later (versions, other repos that will join).
- **Related**: the feature issue as a real link (ask Sofia if missing), the design (Figma) with one line on why it's worth a look even if this repo doesn't use it directly.
- **Before / After**: prose. How the user worked before, what changes for them after.
- **QA**: "No QA in this PR, the tests and instructions live in the proposals and subs." List them: `#124`.
- **Tests**: `No, and this is why: this is only a feature PR, the tests live in the proposal PRs.`
- **Commit override**, at the very end, if the repo uses it (seen in past PRs or release config):
  ```
  BEGIN_COMMIT_OVERRIDE
  feat: <ID> - <summary> (#<PR number>)
  END_COMMIT_OVERRIDE
  ```

## proposal

The integration PR. The reviewer's map of the whole stack.

- **Description**, in this order:
  1. One line: integration PR for <what> (<issue link>), root of an **N-PR stack**.
  2. **Out of scope:** only cuts that change what a reviewer should expect from the shipped stack (product surface, sibling repos, later proposals). Not local process choices (what stays off git, what Sofia keeps on disk, research notes). Drop the heading when there is nothing reviewer-relevant to exclude.
  3. The end-to-end flow once the whole stack is merged, told as a story: input, what happens, output, why it is trustworthy.
  4. Merge instructions: review and merge **in order 1 -> N** into this branch, then review the consolidated work here. Say which branch this targets when it's not `main`.
  5. The merge-order table:
     `| Order | PR | Scope | Linear Issue | Size |`, one row per sub, Scope in one sentence with code names in backticks.
  6. **Package / folder diagram** (mermaid or short tree), when the stack adds a new package layout. Lives on the proposal, never on a sub. If unsure whether a diagram belongs here or nowhere, ask Sofia; do not guess onto a sub.
- **Canceled branches & PRs**: the graveyard. One bullet per dead group: bold name, PR numbers, why it died (scope change, too big, re-cut in another order), what replaced it. End with "Nothing in the live stack depends on any of it." Drop the section if nothing died.
- **Related**: parent feature issue as a real link, design, parent feat PR.
- **After**: when the UI lives in another repo, title it `### After, what will happen` and open with a bold line saying it is not implemented here, it only answers "where will this show up".
- **QA**: full end-to-end, numbered, each step with the command and the expected result. Say which things look like bugs but are expected ("one or two options instead of three is on purpose").
- **Tests**: `Yes, each stacked PR (#a -> #b) includes unit tests under ...`, plus the full-suite command.

## sub

One reviewable piece. The reviewer reads this with the diff open. Keep it direct: shorter than a blog post, closer to the geometry-foundations style (what landed, why it matters, how to test).

- **Description**: what this PR adds and why, in plain sentences. Prefer a short file/module list when that orients the reviewer faster than narrative. Compare to something the team already knows when it helps ("the NIOSH equivalent of what REBA/RULA already does").
- **`Things worth knowing before reviewing:` is optional.** Include it only when the reviewer will misread the diff or the QA without a trap callout (behavior that looks like a bug, a non-obvious contract, a required merge order that is not obvious from the base branch). Omit it when Description + QA already cover the review. Never use it for:
  - cosmetic debt, unused imports, duplicate constants, "I left X alone"
  - `.gitignore` churn, ignore-list policy, or what is not committed
  - process meta ("Sofia accepted the size", "left alone on purpose", local decisions attributed to the agent)
  - anything only visible on Sofia's machine
- When the section is present: few bullets, each a **bold claim** then the reason. Prefer moving a trap into QA expected output over adding the section.
- **Related**: `Ref: [<issue>](<url>)` with a real tracker URL (ask Sofia if missing). Parent proposal PR and stacked-on PR with GitHub links. Plus analysis docs **only if those paths are in git on this branch**. Never `.scratch/`, never local QA records, never uncommitted specs.
- **Screenshots**: a real response or UI capture when behavior changed, as placeholder for Sofia. No package-wide diagrams here (those go on the proposal).
- **QA**: a code block with the exact commands and the pass counts from this session's run as trailing comments (`# 60 passed`), then numbered manual steps with concrete input values and expected output, including one negative case (what must fail, and how). Expected traps belong here as expected output, not as a diary of what was deferred.
- **Tests**: `Yes`, then which test files are new or changed and what each one proves, in a sentence or a short list. Or honest `No` with why.

## single

A standalone PR (bug fix, refactor, small feature).

- **Description**: the change, the reason, the rules or references it follows (domain rules, specs, with images if Sofia has them). Keep deliberate deferrals short and only when they change how the reviewer reads this diff.
- **Related**: the issue as a real link (ask if missing), and any PR or document in another repo it depends on. Same local-path ban as subs.
- **QA**: full setup when it spans repos (clone layout, branches to check out, migration order), numbered, exact commands, the expected output in a block, and the known traps with the workaround ("if you see X, it's Y, do Z instead").
- **Tests**: honest status, including when they only pass after another repo merges, and why.
