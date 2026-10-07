---
name: research
description: >
  One skill, three modes: cited primary-source research (default), optional
  last-30-days discourse when the plugin is installed, or a throwaway spike
  when only code can answer the question. Triggers: "research this", "look
  into", "what does the spec say", "cite your sources", "what's the vibe on",
  "last 30 days", "prototype this", "spike this", "sanity check this logic".
argument-hint: "<question> [mode: sources | discourse | spike]"
---

Mode: professor.

Pick the mode from Sofia's words. Default is **sources**. If unclear, ask
once: primary sources, recent chatter, or a throwaway spike?

| Mode | When |
|---|---|
| **sources** | Facts, specs, docs, code, papers, "is this true" |
| **discourse** | Recent public chatter, hype vs signal (needs last30days plugin) |
| **spike** | One design question only running code can settle |

---

## Mode: sources

Investigate against high-trust primary sources. Spin up background reading so
Sofia keeps working.

### Source tiers

- Tier 1: official docs, specs, RFCs, source code, first-party APIs, maintainers.
- Tier 2: papers, changelogs, named practitioners (verify against Tier 1 when possible).
- Tier 3: leads only, never final word: blogs, SO, forums.
- Tier 4: colour only: social takes, marketing.

Chase claims to the highest tier that owns them. Note tier beside each source.

### Citations and conflicts

Every fact: inline link or `path:line`. When sources disagree, name both, say
which wins and why, or say unresolved.

### Note shape

1. **Confidence**: high / medium / low + one clause why.
2. **Findings**: by sub-question, cited.
3. **Conflicts**: if any.
4. **What this means for you**: 2-4 sentences for Sofia's actual question.
5. **Further reading**: optional.

Save: `docs/research/<yyyy-mm-dd>-<slug>.md` in a repo, else
`~/ObsidianPipa/+/<Title>.md` with `map: [[Research Map]]` and `tags: [research]`.

---

## Mode: discourse

Never reimplement scraping. Requires the last30days plugin.

Check `/last30days:last30days` or `claude plugin list` for `last30days-skill`.
If missing, give install and stop:

```bash
claude plugin marketplace add mvanhorn/last30days-skill
claude plugin install last30days@last30days-skill
```

Delegate the topic to `/last30days:last30days`. Then read the digest back:

1. Signal vs hype (same claim on several platforms vs one viral post).
2. What proof would settle each claim; does the digest have it or only reaction?
3. Flag claims that still need **sources** mode.
4. Close with "worth acting on" vs "noise" in 1-2 sentences.

Save the professor digest like sources mode (not the plugin's raw autosave in
`~/Documents/Last30Days` unless Sofia asks).

---

## Mode: spike

Throwaway code for **one** question. Write the question as one sentence at the
top of the artifact before coding.

- Logic / state / data shape → `LOGIC.md`
- Look and layout → `UI.md`

Minimum build: no tests, no extra abstraction, HER rule 2 (no comments).
Show state after every action or variant switch. Deliverable is the answer in
1-2 sentences, then fold validated bits into real code or the ticket, delete
or branch the shell, never merge throwaway to main.

---

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Read sources (sources mode) | `sonnet` | Parallel by source kind |
| Verify cited URLs | `haiku` | Before save |
| Run last30days | `sonnet` | Background (discourse) |
| Build spike | `sonnet` | logic or UI variants |
| Heavy synthesis | `opus` | many conflicts or sources |
