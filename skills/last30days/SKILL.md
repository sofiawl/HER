---
name: last30days
description: >
  What people have actually said about a topic in the last 30 days, pulled from
  Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub and the open web,
  ranked by engagement, then read back with a skeptical eye. Wraps the
  last30days plugin and adds a professor-mode pass that separates signal from
  hype. Triggers: "what's the vibe on X", "last 30 days", "what are people
  saying about", "trending right now", "recent discourse on", "sentiment
  check", "did anything happen with X lately", "zeitgeist".
argument-hint: "<topic or question>"
---

Mode: professor.

## 1. Check whether last30days is installed

Look for the `/last30days:last30days` skill in this session, or run
`claude plugin list` and look for `last30days-skill`. Never install it
yourself, only Sofia does that.

If missing, explain the install and stop there:

```
claude plugin marketplace add mvanhorn/last30days-skill
claude plugin install last30days@last30days-skill
```

It needs Python 3.12 or newer on PATH (it can provision one itself through
`uv` when a system 3.12 is missing). Reddit with comments, Hacker News,
Polymarket and GitHub already work with zero keys.

Every other key just widens coverage, none of it is required:

- `SCRAPECREATORS`: the primary key. It unlocks TikTok and Instagram
  (posts and comments) plus YouTube comments, and backs up Reddit search
  and YouTube transcripts when the free paths come up short. Free for the
  first 10,000 calls, then paid. It does not touch X.
- X/Twitter needs its own separate path: a bearer token, a logged-in
  browser session, or an xAI key, not the ScrapeCreators key.
- Everything else (a local `yt-dlp` install for full YouTube transcripts,
  a GitHub token for higher rate limits, and so on): optional, narrows to
  that one platform if skipped.

If Sofia says it is installed but a run fails, suggest its own `doctor`
check (a subcommand inside the `/last30days:last30days` skill) before
digging further.

## 2. Delegate the run

Do not reimplement any of the scraping or ranking. Hand the topic straight to
`/last30days:last30days` and let it do the actual research and engagement
ranking across all its platforms.

## 3. Read the digest back, in professor mode

Engagement is a popularity signal, not a truth signal, a wrong take can
out-rank a correct quiet one. For the digest you get back:

1. Separate signal from hype: note which claims show up independently across
   several platforms or threads versus which ones ride on a single viral post.
2. For each major claim, ask what kind of proof would settle it (an official
   statement, a spec, released numbers, a maintainer comment) and say whether
   the digest actually has that or only has crowd reaction.
3. Flag the claims that still need a primary source and offer to send exactly
   that question to `/her:research` instead of taking the crowd's word for it.
4. Close with a short "worth acting on" versus "just noise" read, one or two
   sentences, so Sofia is not left to reweigh forty links herself.

## 4. Offer to save it

Ask if Sofia wants the digest kept as a note. If yes, use the same output
location `/her:research` uses: inside a git repo, write
`docs/research/<yyyy-mm-dd>-<slug>.md`; otherwise write to the Obsidian vault
at `~/ObsidianPipa/+/<Title>.md` with frontmatter `map:` pointing at
`"[[Research Map]]"` and a `tags:` list. Ask if it is unclear which applies.

Note this is separate from what `/last30days:last30days` already does on
its own: it autosaves its raw, unread run to `~/Documents/Last30Days` by
default on every call. What we save here is the professor-mode digest
above, not a copy of that raw file.

## Subagents

Model tiers and delegation rules: HER rule 6.

| Chore | Model | How |
|---|---|---|
| Check install and run the doctor | `haiku` | First |
| Run the last30days plugin | `sonnet` | Background |
| Professor-mode readback | main | |
