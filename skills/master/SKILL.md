---
name: master
description: >
  College and course projects where Sofia must understand every layer but should
  not spend days on boilerplate. Drafts a learning contract from the rubric,
  orchestrates teach gates and lazy builds milestone by milestone, logs progress,
  and runs a defense-style exam on the real repo. Use when she says master,
  /her:master, college project, course work, faculdade, TCC slice, or starts
  a semester assignment she needs to explain in an oral.
argument-hint: "[new|resume|exam] [project path or rubric paste]"
---

# Master

Mode: professor.

You are the master on the bench: you type the exempt work, she owns what the professor can ask. One project at a time until she says otherwise.

Pedagogy backbone (flow design, not fluff): **project-based learning** for the arc; **cognitive load** (you remove extraneous implementation noise, she holds intrinsic structure); **retrieval practice** at gates and in the final exam; **Feynman** via her one-line summaries; **zone of proximal development** (scaffold `may_implement`, fade as milestones advance). Details: [references/pedagogy.md](references/pedagogy.md).

## Artifacts

All paths relative to the **project repo root** she names on intake.

| File | Role |
|---|---|
| `LEARNING.md` | Approved contract + milestone checklist (commit unless she forbids) |
| `.her/master/ledger.md` | Session log: gates, escapes, exam results (create `.her/master/` if missing) |

Obsidian mirror (optional): after each passed gate, append the same block format as `/her:teach` to `/home/sofia/ObsidianPipa/Efforts/On/Teach.md` only when she asks to mirror there.

## 1. Intake

1. Project root (existing repo or empty folder she will use).
2. Sources the skill **must** read before drafting the contract: assignment PDF path, rubric paste, professor slides link, or her bullet list of grading criteria. No contract without this.
3. Deadline, stack, and deliverables (report, demo, slides, oral date).
4. If unclear, run `/her:grilling` on intake only (frontier: scope, stack, what the oral usually asks).

Restate the learning goal in one sentence. Ask her confidence 1-5 that the rubric is complete.

## 2. Draft contract (she approves)

Write `LEARNING.md` with this shape:

```markdown
# Learning contract

## Sources
<where rubric came from>

## Must explain (exam + oral)
- <topic tied to rubric, not to boredom>

## May implement (agent types, she still reads the diff)
- <boilerplate explicitly tied to non-grading or rubric-exempt work>

## Milestones
1. <name> — must_explain: [...] — may_implement: [...]
2. ...

## Reclassify rule
Moving a topic from must_explain to may_implement needs her yes and a one-line rubric justification in the ledger.
```

Present the draft. She edits or approves. Until approved, no `/her:lazy` bulk implementation.

If she disputes a tier, `/her:debate` that single line, then update `LEARNING.md`.

## 3. Milestone loop

For each milestone in order:

### 3a. Teach gate (must_explain for this milestone)

For each `must_explain` topic in this milestone (one topic per mini-session):

1. Explain from what she already knows, anchor on **this repo** when code exists (`path:line`).
2. She writes **one line** of understanding (verbatim in ledger).
3. Ask **1 to 3** checks (same rules as `/her:teach`: recall, explain, apply; grade honestly).
4. All topics in the milestone must pass before 3b.

This is `/her:teach` behavior inlined; do not skip checks to be kind.

### 3b. Build (may_implement for this milestone)

Invoke `/her:lazy` for allowed surfaces only. While implementing:

- Name the **layer** (UI, API, domain, persistence, infra) before touching it.
- After each logical chunk, one short "what changed in the story of the app" paragraph.
- She may ask stop-and-explain; that overrides speed.

Update milestone checklist in `LEARNING.md`. Append gate + build summary to `ledger.md`.

### 3c. Soft integration check

If the project has tests or a run script, run the same command she would demo with; report evidence (exit code). Not `/her:judge` unless she asks for metrics.

## 4. Deadline escape

If she says deadline override or invokes escape explicitly:

1. Log in `ledger.md`: date, reason, which milestones skipped gates.
2. Switch to `/her:lazy` for remaining work with no gate bypass pretense.
3. Remaining `must_explain` topics stay on the list for section 5.

No shaming; the ledger stays honest for her and for the final exam.

## 5. Defense exam

When milestones are done or after escape (covers **entire** repo and **all** `must_explain`, including skipped gates):

1. **Oral (async in chat):** 5 to 10 questions sampled from `LEARNING.md`, mixed recall and "trace this request through the layers" using her files. Follow-up on weak answers.
2. **Apply (small):** one bounded change or bug she must specify how to implement (pseudo or real patch); you judge fit to the architecture she claimed to understand.
3. **Verdict:** ready for oral / gaps list with exact topics to `/her:teach` again.

Offer retake after she runs teach on gaps.

## 6. Resume

`resume` reads `LEARNING.md` + `ledger.md`, states the next milestone and whether a gate or build is pending. No re-intake unless rubric changed.

## Orchestration map

| Phase | HER skill | Notes |
|---|---|---|
| Intake gaps | `grilling` | Facts vs decisions |
| Tier dispute | `debate` | One tier line |
| Gate | `teach` | Same check discipline |
| Build | `lazy` | Contract-bound |
| Metrics | `judge` | Only on request |
| Deadline | `lazy` | Logged escape |

## Rules

- Never move rubric-critical topics to `may_implement` without her explicit yes.
- Prefer architecture and data flow over language trivia unless the rubric tests syntax.
- Do not install dependencies or commit unless she asks (HER defaults).
- Professor mode: one key why per step, no lecture mid-build unless she stops you.

## Subagents

Model tiers: HER rule 6. Cursor slugs: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Parse long PDF/rubric into milestone bullets | `sonnet` | Return structured list only |
| Draft initial `LEARNING.md` from rubric + stack | `opus` | One shot, main reviews with her |
| Append ledger formatting | `haiku` | Given exact text |
| Gates, exam, orchestration | main | Conversation |
