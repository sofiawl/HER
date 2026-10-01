# How Sofia's PRs sound

A PR is a short brief for a teammate reviewing from GitHub and a fresh clone. Someone should want to read it, not just skim it. Sub PRs stay direct; proposal PRs carry the map.

## Voice

- **Informal and a bit wry, never a joke.** The humor is in the phrasing and the honesty, not in punchlines. Good: "So there's a graveyard worth knowing about", "a chatty model cannot inject its own `updated_risk`", "(kinda boring)". Bad: puns, memes in the text, anything crude or explicit, sarcasm about people.
- **First person only when it clarifies a real trade-off.** Prefer the code and the reviewer over the author's journey. No "I left X alone on purpose" unless Sofia said to say that, and even then only if the reviewer needs it.
- **Explain the why, then the what** when a decision changes how someone reads the diff. Skip why-stories that do not help review or QA.
- **Concrete over abstract.** Real field names in backticks, real numbers ("mass 20, RWL 3.4, LI 5.9"), real commands. No "improved performance", say by how much.
- **Tell the flow as a story** on proposal PRs and on subs that wire several pieces. On a focused sub, a tight module list beats a long narrative.
- **Short asides in parentheses** for side notes ("this will be fixed by X, not in this PR") only when they stop a reviewer from chasing the wrong fix in this diff.
- **Warn about the things that look like bugs but aren't.** Put those as expected QA outcomes first; only promote them to a "Things worth knowing" bullet when QA alone is not enough.
- **Plain words.** Short sentences, active voice, no filler ("This PR aims to", "In order to"), no marketing words.

## Shape

- Sub descriptions: short. Lead with what landed. File or module bullets are fine when they orient faster than prose.
- Proposal descriptions: the map (scope that matters to reviewers, merge order, e2e flow, package diagram when needed).
- Bold lead sentences on bullets, the reason right after, when a bullet list exists.
- Tables for anything with more than 3 rows of the same shape (the merge order).
- Code blocks for every command, with the expected result.
- Headings from TEMPLATE.md only. Do not invent a "Things worth knowing" section by habit; add it only when TEMPLATE.md's bar is met.

## Hard rules

- No em dash, no en dash, no emojis in the text (the template's type shortcodes are the only exception).
- Every number, count or "passes" claim comes from a run in this session (`../judge/VERIFY.md`).
- Never invent links, IDs, PR numbers or screenshots. Placeholder and tell Sofia. The GIF is always Sofia's pick, leave that section empty.
- **Never name local-only paths in the PR body.** `.scratch/`, uncommitted specs, local QA records, private notes: out. If a doc is not on the branch the reviewer checks out, it is not a Related link.
- **Never invent or omit a ticket URL.** Ask Sofia for the real tracker link. Related tickets are clickable or they wait.
- **Never claim Sofia's decisions as the agent's.** If something was deferred because she said so, either omit it or attribute it plainly without "on purpose" theatre.
- Package-wide diagrams go on the proposal. If placement is unclear, ask Sofia.

## Before saving, reread and check

1. Would a teammate who never saw your laptop enjoy the first paragraph?
2. Is every sentence useful for reviewing or running QA? Cut the rest.
3. Could someone run the QA without asking Sofia anything, using only clone + this PR?
4. Any local path, cosmetic debt diary, or gitignore story still in the body? Delete it.
5. Any sentence that is a joke rather than a wry remark? Rewrite it.
