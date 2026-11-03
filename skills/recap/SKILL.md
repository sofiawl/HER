---
name: recap
description: >
  Weekly recap and presentation: collects what Sofia did in a window from her
  Claude Code sessions, Cursor transcripts, git commits and Kineloop cards,
  groups it (fixed, debugged, cleaned up, built, investigated), drafts a
  short pt-BR slide plan with metrics and images for her approval, then
  builds the deck from the Kinebot HTML template and checks every number.
  Triggers: "/her:recap", "what did I do this week", "weekly recap", "weekly
  presentation", "summarize my week", "cycle presentation", "resumo da semana",
  "apresentação da semana".
argument-hint: "[start date] [cycle label, e.g. S07E06]"
---

Mode: professor.

Reference files: `collect.py` (deterministic collector), `DECK.md` (slide rules, template, build and render), `../judge/VERIFY.md` (verification gate).

## Inputs

- Window: start and end date. Default: last Tuesday through today. Confirm it in one line, do not interview.
- Cycle label (for example `S07E06`): ask once if not given. It goes on the cover and in every footer.
- Where the metrics live (results folder, summary file, Kineloop card). If the recap names a feature with runs or evals, look in the matching `~/kinebot-research/` folder and results folder first, then ask only for what is still missing.

## Flow

1. **Collect.** Run these in parallel, read-only:
   - `python3 -I ~/HER/skills/recap/collect.py --since <start> --until <end> > <scratchpad>/recap_raw.txt` gives Claude Code user messages per session, distinct commit subjects per repo (author date, worktrees and stashes excluded), and the list of Cursor transcripts in the window.
   - Cursor: send the transcript list to a `sonnet` subagent (split by 6 files if long). Prompt: per transcript, date, repo, approximate user messages, 1 to 3 lines of what she asked and what came out, branch names, PR numbers and card IDs exactly as written, then at most 6 themes. Read only. Ask it to flag any secret pasted into a transcript, without quoting it.
   - Kineloop: load the tools with ToolSearch, then read every card ID found in branches, commits and messages (`kineloop_get_issue`), plus her cards updated in the window (`kineloop_list_issues`). A `haiku` or `sonnet` subagent can transcribe them verbatim: title, state, assignee, description, comments, due date. Never change a card.
2. **Recap in chat.** Group as Corrected, Debugged, Cleaned up, Built, Investigated, Process and tools. One or two lines each with repo, branch or PR and card ID. Count only what the collector shows. End with open items you noticed (commits not pushed, secrets pasted, cards with no update). Say which source each group came from, because Cursor work does not appear in git or Claude sessions.
3. **Slide plan.** Follow `DECK.md` section 1: at most 5 content slides plus a next-steps slide, every slide with a metric and an image candidate, every number with its source file. Show the plan as text only and list what is missing as numbered questions (cost source, an image that does not exist yet, a number you could not verify). **Stop and wait for her OK.** Her edits win.
4. **Fill the gaps she answered.** Find the cost or time figure, copy the images, or run the missing job only if she said so (a stage rerun, a frame export). Never invent a number to close a gap.
5. **Build.** `DECK.md` sections 2 and 3. Copy the template to `~/Documents/kinebot-reports/presentations/<slug>/`, write the slides, render the PDF.
6. **Look at it.** Render each page to PNG and read them yourself (`DECK.md` section 4). Fix cut images, overlapping text, wrong counts, before showing her.
7. **Number check.** One `sonnet` subagent that did not write the deck re-reads each number on the slides from its source and lists mismatches (`../judge/VERIFY.md`). Fix them. Then run the character check in `DECK.md` section 4.
8. **Hand back.** Folder, `index.html`, PDF path, page count, the headline line, open points, anything left as placeholder. Iterate on her edits by editing `index.html` in place and re-rendering. Do not commit anything.

## Hard rules

- No slides before the plan is approved.
- Every number traces to a file, a card or a command output. Say what the statistic is (mean error, median, count of what) and what a word means when it could be read two ways. If she asks "what does X mean", the slide was unclear: rewrite it.
- Never write "fixed" or "now works" unless a run in the window shows it. If the fix is only in code, say "corrigido no código, validação pendente" or offer the rerun.
- Ground truths that came from user input, small n and mixed run dates are stated on the slide in one short note.
- Never drop a case, video or run from a metric on your own. Ask first, and list what was excluded and why.
- An image must come from a real run and prove what the slide says. No decorative picture. If none exists, offer to produce it (rerun with frame output on) or draw a simple flow diagram.
- Things she said "not yet" stay out of the deck until she says so.
- No API keys, tokens or personal data on slides or in the recap. Flag a key pasted into a transcript so she can rotate it.
- Slides in Brazilian Portuguese, short lines, no long sentences. No em dash, en dash or emoji.

## When something is off

- No Kineloop access or a card cannot be read: say which, continue with the other sources, mark the slide that needed it.
- The window has almost no activity: say so, ask whether to widen it.
- A metric exists only for some runs: show it with its n, never as if it covered all.
- Two sources disagree (card says done, git says no commit): list both in the recap, ask which to show.

## Subagents

Model tiers: HER rule 6. Cursor slugs per chore: `../MODELS-CURSOR.md`.

| Chore | Model | How |
|---|---|---|
| Run `collect.py`, find results files, copy images, render PDF and PNGs | `haiku` | Inline if about 3 calls |
| Summarize Cursor transcripts | `sonnet` | One agent per 6 transcripts, in parallel with the other collection |
| Transcribe Kineloop cards verbatim | `haiku` | One agent, read only |
| Group the recap, write the slide plan, write the slides | main session | Needs her answers |
| Optional Remotion video (only if she asks) | `sonnet` | Brief in `DECK.md` section 5 |
| Independent number check | `sonnet` | Not the agent that wrote the slides |
