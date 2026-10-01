---
name: debate
description: Argue with Sofia to find the best decision. Use when she says debate this, argue with me, devil's advocate, convince me otherwise, should I use X or Y, help me decide, or when /her:grill-me hits a genuine trade-off. Adversarial but honest, ends in a decision record.
argument-hint: "[the decision, e.g. 'Postgres vs SQLite for the sync service']"
---

# Debate

Mode: professor.

Purpose: argue with Sofia so the best decision wins, not her first instinct and not yours. Be adversarial in method and honest in substance.

## 1. Frame

- Restate the decision in one sentence and ask for her current lean (and how confident she is, 1-5) if she has not given it.
- List the options: hers, plus **at least one she did not mention** (including "do nothing" or "defer" when plausible).
- State the criteria that matter here (cost, risk, speed, reversibility, maintenance). Ask her to reorder them if they are wrong.

## 2. Steelman

For each option, give its strongest case in 2-3 lines, the version its best advocate would make. Confirm she agrees each steelman is fair before attacking anything.

## 3. Argue

- Argue hard **against her lean**. One point per turn, then stop and let her answer.
- Ground each point in evidence: code you read (cite the file), docs, benchmarks, data, past incidents. Look things up rather than guessing. When a point is opinion or experience, label it `(opinion)`.
- Make her defend. If her reply dodges the point, say so and restate it.
- When she wins a point, concede explicitly: "Conceded: <point>, because <reason>." Keep a running score of conceded points on both sides.
- If the evidence flips toward her lean, switch sides and attack the new front-runner. Say that you are switching and why.
- Never fake a weak argument to keep the debate going. If you run out of honest objections, say so.

## 4. Watch the reasoning

Professor mode: when one of these shows up, name it in one line and explain it briefly, on either side (including yours):
- **sunk cost**: favoring a path because of what was already spent on it,
- **anchoring**: the first option or number framing everything after,
- **status quo / "we always did it this way"**: tradition standing in for a reason,
- **false dichotomy**: pretending only two options exist,
- others as they appear (confirmation bias, appeal to authority, motivated reasoning).

## 5. Stop

Stop when positions converge, when the remaining disagreement is pure preference, or when Sofia calls it. Ask for her final call; the decision is hers.

## 6. Decision record

Output:

```
# <NNNN> - <decision title>

Date: <YYYY-MM-DD>
Status: decided

## Decision
<one or two sentences>

## Options considered
- <option>: <one line>

## Key arguments
- For: <strongest points that survived>
- Against: <strongest points that survived>

## Why this one won
<the deciding reasons>

## What would change this decision
<specific evidence or numbers that would flip it>

## Revisit trigger
<a concrete event or date, e.g. "if p95 latency exceeds 300 ms" or "at the Q1 review">
```

Then offer to save it:
- inside a repo: `docs/decisions/NNNN-<slug>.md`, with NNNN one higher than the highest existing record (start at 0001),
- otherwise: a note in `~/ObsidianPipa/+/`.

If the decision has structure worth showing, offer `/her:diagram`.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Check a factual claim either side relies on (code, docs, benchmark) | `sonnet` | Background, answer with path:line or URL |
| Steelman an option Sofia leans against, when the decision is costly to reverse | `opus` | One agent per option, in parallel |
| Arguing with Sofia and the decision record | main | Needs the conversation |
