---
name: teach
description: Teach Sofia one concept in chat, have her write one line of what she understood, ask 1 to 3 checks, then append the lesson to her skill-issue effort note. Use when she says "teach me X", "I want to learn X", "explain X properly", "quiz me on X", or accepts a /her:teach offer from another skill.
argument-hint: "[topic]"
disable-model-invocation: true
---

Mode: professor.

One topic per session. Explain it, she writes one understanding line, you ask 1 to 3 questions, then append to the effort note.

## 1. Explain in chat

1. One concept per session. Start from something she already knows, then the new idea, then one small concrete example, then the misconception people usually hit.
2. Keep it under 10 minutes of reading. Define every new term the first time it appears.
3. Prefer high-trust sources (official docs, specs, source code) and name them inline. If the topic is code in the current repo, anchor on the real file and cite `path:line`.
4. Answer her questions until she stops asking. Only then move on.

## 2. Her line, then 1 to 3 checks

1. Ask her to write **one line** of what she understood. Wait for that line. Keep it verbatim.
2. Ask **at least 1 and at most 3** short questions, one per message, waiting for each answer. Pick how many from how shaky the line and the topic are (one if the line is already solid and the topic is small; up to three if gaps remain). Prefer mixing recall, explain, and apply when you ask more than one. Do not hardcode three.
3. Grade honestly after each answer: what was right, what was off, and the correct answer. Do not round up to be kind. Keep her answers verbatim.

## 3. Append to the effort note

After the checks, append one block to:

`/home/sofia/ObsidianPipa/Efforts/On/skill issue.md`

Match the sample format already in that file. Do not create a separate note under `+/learn/` or elsewhere.

```
## <Title of the learning>
<Her one line of what she understood, verbatim aside from tiny grammar fixes.>

**<the question>**
- <What she answered.>
- Correction. <Only if necessary; omit this bullet when her answer was solid.>
```

Questions are always bold (`**...**`). Repeat the question / answer / optional correction block once per check you asked (1 to 3 times). Title is the topic in plain words. Append at the end of the file; leave the sample (or earlier lessons) above untouched.

Then tell her the path in one line and stop.

If she asks for a review later, quiz her from that file instead of teaching it again.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Append the formatted block to `skill issue.md` | `haiku` | After the checks, given the exact text to append |
| Explaining and the checks | main | Needs the conversation |
