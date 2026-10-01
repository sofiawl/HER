---
name: grilling
description: >
  Round-based interview on a plan, decision, or idea until shared understanding.
  Model-invoked primitive: use when a plan-code flow is blocked on Sofia's judgment
  (not a look-up-able fact), or when she asks for batch/frontier grilling. Adapted
  from Matt Pocock's grilling skill (MIT).
argument-hint: "[plan, idea, or path to a spec]"
---

# Grilling

Mode: professor.

Adapted from Matt Pocock's `grilling` skill (MIT license). This is the model-fired engine. For the user-only one-question-at-a-time door, use `/her:grill-me`.

Interview Sofia relentlessly until shared understanding. Map the subject as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds and frontier

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask now without guessing at unanswered ones. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for her answers before the next round.

Each question:

```
**Q<n> - <short title>**
<the question, with options if any>

Recommendation: <your answer>, because <the reason>.
```

Each round of answers reshapes the tree: settled decisions push the frontier outward and unblock what depended on them. Recompute the frontier and ask the next round. A question that depends on another still open in this round belongs to a later round, not this one.

## Facts vs decisions

Finding facts is your job, never Sofia's. When a frontier question needs something from the environment (filesystem, tools, docs), look it up or dispatch a subagent. Do not block the round: only questions downstream of a running lookup wait; ask the rest now. Decisions are hers: put each to her and wait.

## End

The session is done when the frontier is empty: every branch visited, nothing left silently assumed. Do not act on it until she confirms shared understanding. No summary artifact and no debate handoff here; if she wants the richer exit, suggest `/her:grill-me` next time or `/her:debate` only if she asks.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Answer a factual question from the codebase instead of asking Sofia | `haiku` for a lookup, `sonnet` when it needs reading code | Background while the round continues |
| The interview | main | Needs the conversation |
