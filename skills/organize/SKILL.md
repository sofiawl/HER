---
name: organize
description: >
  Make purpose obvious from names and layout: what each repo, directory and
  file is for, and how it differs from its neighbors (for example research vs
  cosmos). Proposes a small naming map, applies only what Sofia approves.
  Trigger on "/her:organize", "organize this", "what is this repo for",
  "these names are confusing", "clean up the layout", "rename things so it
  makes sense". Not a refactor skill, not a formatter.
argument-hint: "[path, repo or set of repos, e.g. '~/kinebot-research ~/cosmos']"
---

# Organize

Mode: adhd.

Goal: someone reading only the names and the top-level layout can tell what
each thing is for and why it is not its neighbor. Facts from the filesystem
are the agent's job, decisions are Sofia's.

## 1. Inventory the scope

Resolve the scope from the argument, default the current repo. For each repo
and top-level directory collect facts only: name, README first line, main
language, entry points, last commit date, what imports or calls what. Do not
judge yet.

## 2. Write one purpose line per thing

One sentence each: "`<name>` exists to <purpose>, unlike `<neighbor>` which
<purpose>." If two things get the same sentence, that is an overlap. If a
thing gets no clear sentence, that is an unclear purpose. Ask Sofia only
about the ones you could not derive from the files.

## 3. Find the confusions, by level

Check three levels separately, list at most 5 findings total, worst first:

- **Repo purpose labels**: repo names, README titles and descriptions that hide or blur purpose, or two repos that claim the same one.
- **Directory and layout clarity**: folders that mix purposes, one purpose split across folders, dumping grounds (`misc`, `stuff`, `new`, `old2`).
- **Naming consistency**: the same concept under different names, different concepts under one name, mixed casing or language (pt-BR vs en) for the same kind of thing.

Each finding cites the real paths it came from.

## 4. Propose a small naming map

A table Sofia can approve row by row, 10 rows max:

| # | Now | Proposed | Level | Why | Blast radius |
|---|---|---|---|---|---|

Blast radius counts what breaks: imports, config paths, CI, links, remotes,
Obsidian wikilinks. Prefer renames with a small radius; mark anything that
touches a remote, a published package or a shared path as `ask`.

## 5. Apply only approved rows

Stop and ask before any rename, move or delete. After Sofia picks rows:
use `git mv` inside repos, update every reference found in step 4, run the
project's tests or build if it has one, then show `git status`. Never rename
a remote repo, never commit or push. Leftover rows go in one "later:" line.

## Boundaries

Changing behavior, splitting functions or reformatting code is out of scope,
offer `/her:lazy` for that. If a finding is really a design choice between
two structures, offer `/her:debate`. To show the before and after layout,
offer `/her:diagram`.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Inventory facts per repo or top-level dir | `haiku` | One per repo, in parallel |
| Find every reference to a name before rename (imports, config, links) | `sonnet` | One per approved row |
| Review the naming map when it touches shared paths or remotes | `opus` | Before asking Sofia |
| Purpose lines, findings, naming map | main | Needs the whole picture, never delegated |
