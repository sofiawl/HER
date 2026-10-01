---
name: research
description: >
  Investigate a question against high-trust primary sources (official docs,
  specs, source code, papers, maintainers) and write a cited, ranked-by-trust
  Markdown note with a confidence line and a plain "what this means for you"
  section. Use when Sofia wants a topic researched, API or spec facts checked
  against the source that owns them, or reading legwork handed to a
  background agent. Triggers: "research this", "look into", "what does the
  spec actually say", "check the docs for", "find a primary source on",
  "is this actually true", "cite your sources".
argument-hint: "<question to research>"
---

Mode: professor.

## 1. Spin up a background agent

Investigate in the background so Sofia keeps working while it reads. Give the
agent the question and the source-trust and citation rules below verbatim.

## 2. Rank sources by trust, explicitly

- Tier 1, trust by default: official docs, specs and RFCs, the actual source
  code, first-party API references, direct maintainer statements.
- Tier 2, trust but verify against Tier 1 when one exists: papers, changelogs,
  release notes, write-ups from named practitioners with a track record.
- Tier 3, use only to find leads, never as the final word: blog posts,
  Stack Overflow answers, forum threads, secondary tutorials.
- Tier 4, colour only, never cite as fact: social media takes, marketing copy.

Chase every claim up to the highest tier that actually addresses it. Note the
tier next to each source in the note so Sofia can tell at a glance how solid
a claim is.

## 3. Every claim gets a citation

No sentence in the findings states a fact without a link (or a `path:line`
for source code) right next to it, pointing at the source that owns that
fact, not a secondary write-up of it.

## 4. Call out conflicts, do not average them away

When two trustworthy sources disagree, say so plainly: name both, quote what
each one claims, and say which one wins and why (tier, recency, specificity),
or say the conflict is unresolved if it genuinely is.

## 5. Write the note

Structure, in this order:

1. **Confidence**: one line, high, medium or low, plus the one-clause reason
   (source tier, agreement across sources, how current the sources are).
2. **Findings**: the actual answer, organized by sub-question, each claim
   cited inline.
3. **Conflicts**: only if any showed up, per rule 4.
4. **What this means for you**: two to four sentences translating the
   findings into the concrete implication for Sofia's actual question, not a
   restatement of the findings.
5. **Further reading**: sources worth a look that were not central enough to
   cite inline.

## 6. Save it in the right place

Inside a git repo: `docs/research/<yyyy-mm-dd>-<slug>.md`. Outside one: the
Obsidian vault at `~/ObsidianPipa/+/<Title>.md`, with frontmatter

```
map:
  - "[[Research Map]]"
tags:
  - research
```

plus whatever extra tags fit the topic. If it is unclear which applies, ask
before writing.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Read sources and extract claims with citations | `sonnet` | One agent per source kind (docs, source code, papers, maintainers), in parallel |
| Check every cited URL resolves and the quote is in it | `haiku` | Before saving |
| Write the note when sources conflict or are many | `opus` | Gets all findings |
| Write the note otherwise | main | |
