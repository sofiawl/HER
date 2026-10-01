---
name: diagram
description: Draw a small, correct diagram that answers one question. Use when Sofia asks to diagram, draw, sketch, visualize or map something (a flow, sequence, state machine, architecture, data model, dependency graph, timeline), wants to "see" how code or a plan fits together, or after /her:grill-me, /her:grilling or /her:debate settled a design worth showing.
argument-hint: "[what to diagram, e.g. 'auth flow' or 'src/billing']"
---

# Diagram

Mode: professor.

A diagram exists to answer one question faster than prose can. Decide the question first, then draw the smallest picture that answers it.

## 1. Name the question

Write one sentence: "This diagram shows <question>." If you cannot, ask Sofia one clarifying question before drawing. If the request holds two questions, plan two diagrams.

## 2. Pick the type from the question

| Question shape | Type | Mermaid |
|---|---|---|
| What steps or branches happen? | flow | `flowchart` |
| Who talks to whom, in what order? | sequence | `sequenceDiagram` |
| What states can this be in, and what moves it? | state | `stateDiagram-v2` |
| What are the big parts and how do they connect? | architecture (C4-ish: context, then containers) | `flowchart` with `subgraph` |
| What data exists and how is it related? | ER | `erDiagram` |
| What depends on what? | dependency | `flowchart` (LR) |
| What happened or will happen when? | timeline | `timeline` or `gantt` |

Say in one line why this type fits and the runner-up was worse.

## 3. Keep it small

- One idea per diagram. Aim for under about 15 nodes; past that, split into an overview plus detail diagrams.
- Merge nodes that always travel together. Drop nodes that do not change the answer.
- Label edges with verbs ("calls", "writes to", "emits"), not nouns.
- Pick one direction (TB for hierarchy and steps, LR for pipelines and dependencies) and keep it.
- Arrange to avoid crossing edges; if crossings remain, the layout or the scope is wrong.
- Use short, real names. Use at most one highlight style, on the focal element.

## 4. Codebase diagrams: derive, never invent

When the diagram describes code, every node and edge must come from something you read.

1. Find the real files, modules, tables or services (Glob, Grep, Read, or an Explore sub-agent for wide sweeps).
2. Map each node to a path and each edge to an import, call, query or event you saw.
3. Re-check any edge you are unsure of. If you could not verify it, draw it dashed and say so.
4. Never fill gaps with plausible-looking structure.

## 5. Output

- Default: a fenced `mermaid` block inside Markdown. Obsidian renders it natively and GitHub renders it in repos.
- If Sofia wants it saved, write it into the note or doc she names (for a repo, near the code it describes, such as `docs/`).
- Validate before handing over: balanced brackets, quoted labels that contain punctuation, no reserved words (`end`) as bare ids.
- For rich, shareable, polished or interactive visuals, hand off to the `artifact-diagramming` skill (and `artifact-design`) if they are available in this session. Mermaid stays the default otherwise.

## 6. Teach it

After the diagram, write 2-4 lines:
- how to read it (where to start, what direction to follow),
- the one insight it reveals (a bottleneck, a cycle, a missing state, a surprising coupling).

If the insight suggests a decision, offer `/her:debate`; if it opens a plan, offer `/her:grill-me`.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Derive nodes and edges from code, each with path:line | `sonnet` | One agent per subsystem, in parallel for large repos |
| Validate Mermaid syntax (mermaid-cli when installed) | `haiku` | After drawing |
| Pick the question, the type and draw | main | |
