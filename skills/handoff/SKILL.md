---
name: handoff
description: >
  Compact the current conversation into a handoff doc another agent or Sofia
  tomorrow can resume from. Trigger on "/her:handoff", "handoff this",
  "write a handoff", "compact this session", "I need to stop here".
argument-hint: "what will the next session focus on"
disable-model-invocation: true
---

Mode: adhd

A hook nudges Sofia to run this when context passes 75% (once per session) or a usage limit window passes 85% (once per window). It never runs the handoff itself.

Write a plain, scannable markdown file to
`${TMPDIR:-/tmp}/her-handoff-<yyyy-mm-dd>-<slug>.md`, slug from the topic.

Sections, in this order:

1. **Goal**: one or two lines, what this session was trying to do.
2. **Current state**: three short lists, done, in progress, not started.
3. **Decisions made and why**: one line per decision, the why not the what.
4. **Open questions**: things nobody has answered yet.
5. **Files and references**: by path or URL, never paste code or long content.
6. **Exact next action**: one concrete step, no vague "continue work."
7. **Suggested HER skills**: which `/her:` skills fit the next step, from `/her:ask-her`'s list.

Redact secrets: API keys, tokens, passwords, personal data. Replace with
`[redacted]`, never guess or reconstruct the value.

Do not duplicate content that already lives in a spec, plan, ADR, ticket,
commit or diff, point at it by path instead.

If Sofia gave arguments, treat them as what the next session is for and
shape the doc around that focus.

When done, print the file path and one short resume prompt Sofia can paste
into a fresh session to continue.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Collect repo state: branch, `git status`, last commits, open PRs, running processes | `haiku` | In parallel while you write |
| The summary itself | main | Needs the conversation, never delegated |
