---
name: grill-me
description: >
  User-only one-question-at-a-time interview on a plan, design, feature or idea
  until shared understanding. Use when Sofia says grill me, /her:grill-me,
  stress-test this, poke holes, challenge my plan, am I missing something, or
  before building anything non-trivial. Adapted from Matt Pocock's grilling
  skill (MIT); HER door with professor extras.
argument-hint: "[plan, idea, or path to a spec]"
disable-model-invocation: true
---

# Grill-me

Mode: professor.

User-only door. The model-fired round-based engine is `/her:grilling`.

Goal: reach a shared understanding of the plan, with nothing silently assumed.

## The decision tree

Treat the plan as a tree of decisions: each choice opens the choices that depend on it. The **frontier** is the set of open decisions whose prerequisites are already settled. Only ask from the frontier; a question that depends on an unanswered one waits.

## The loop

1. Restate the plan in 2-3 sentences and list the top-level decisions you see. Ask Sofia to correct the framing if it is off.
2. Pick the most important frontier question. Ask **one question at a time**, in this shape:

   ```
   **Q<n> - <short title>**
   <the question, with the options if there are any>

   Recommendation: <your answer>, because <the reason>.
   ```

3. Wait for her answer. Record it as a decision. Recompute the frontier: settled answers unlock new questions and can make old ones moot.
4. Repeat until the frontier is empty: every branch visited, every assumption named.

## Rules

- **Facts are your job, decisions are hers.** Before asking anything the codebase, docs or environment can answer, look it up (Read, Grep, or an Explore subagent for wide searches). Ask only what requires her judgment. When you looked something up, cite the file.
- Keep going when answers are vague. Push for specifics: numbers, names, edge cases, failure modes, who is affected.
- When an answer contradicts an earlier decision, point at both and ask which wins.
- Professor mode: when a question involves a concept she may not know, define it in one line inside the question.
- **Genuine trade-offs:** if a question has no clearly better answer (both options have real costs and the evidence is balanced), say so and offer: "This is a real trade-off. Want to switch to /her:debate for this point?" Resume grill-me after the debate returns a decision.
- Do not start building. Grill-me ends in understanding, not code.

## Ending

When the frontier is empty (or Sofia calls it), confirm shared understanding, then output:

```
## Grilling summary: <plan name>

### Decisions
1. <decision> - <one-line reason>

### Open questions
- <question> - <what is needed to answer it>

### Assumptions still unverified
- <assumption>
```

Then suggest the next step that fits:
- `/her:to-pr plan` if the plan is ready to split into a PR stack,
- `/her:debate` for any open question that is a real trade-off.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Answer a factual question from the codebase instead of asking Sofia | `haiku` for a lookup (where is X), `sonnet` when it needs reading code | Background while the interview continues |
| The interview and the summary | main | Needs the conversation |
