---
name: prototype
description: >
  Build a throwaway prototype that answers exactly one design question, then
  either delete it or fold the validated answer back into the real code and
  notes. Logic questions get a small runnable state model; UI questions get
  several structurally different variants switchable on one route or file.
  Triggers: "prototype this", "does this state machine feel right", "sanity
  check this logic", "spike this", "show me a few options for this screen",
  "quick throwaway to test", "try a different layout for".
argument-hint: "<the design question to answer>"
---

Mode: professor.

A prototype is throwaway code that answers a question. The question decides
its shape, get the branch wrong and the whole thing is wasted effort.

## 1. Name the question, then pick a branch

Write the question as one sentence before touching code, and put that
sentence at the top of the prototype itself, not just in chat.

- "Does this state model or logic hold up?" -> read `LOGIC.md`, build a
  single runnable HTML file with a pure state model behind it.
- "What should this look like?" -> read `UI.md`, build several structurally
  different variants switchable in one place.

If the question is genuinely ambiguous and Sofia is not around to ask,
default by the surrounding code (a backend module means logic, a page or
component means UI) and state that assumption at the top of the prototype.

## 2. Build the minimum

No tests, no error handling beyond what keeps it runnable, no abstractions,
no framework or bundler for a logic demo. State lives in memory; only reach
for a real database or file if persistence itself is the question, and if so
give it an unmistakable "wipe me" name.

## 3. No comments in the prototype code either

HER rule 2 applies here too: names and structure carry the meaning, not
comments. This still holds for code that will be deleted in an hour.

## 4. Surface the state

After every action (logic) or on every variant switch (UI), show the full
relevant state so the question is visible while it is being answered, not
just implied by the code.

## 5. Close the loop

Once the prototype has answered its question:

1. State the answer to the design question in one or two sentences, and what
   it implies for the real build. This line is the actual deliverable, the
   prototype is just how you got there.
2. Fold the validated part (the reducer, the winning variant) into real code,
   or into the ticket, plan or notes it was checking.
3. Either delete the throwaway shell, or push it to a throwaway branch as a
   primary source and leave a pointer to that branch on the ticket. It never
   lands on main.

See `LOGIC.md` and `UI.md` for how each branch builds and hands off its
artifact.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Build the logic prototype | `sonnet` | One agent |
| Build UI variants | `sonnet` | One agent per variant, in parallel, each told how its structure must differ |
| Serve, open and later delete the prototype files | `haiku` | |
| Fold the validated answer into the real code when it spans several files | `opus` | After Sofia picks |
