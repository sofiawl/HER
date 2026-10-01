# Logic prototype

One self-contained HTML file that lets anyone drive a state model by clicking
buttons. Use it for questions about business logic, state transitions or data
shape, the kind of thing that looks fine on paper and only feels wrong once
real cases hit it. Because it needs nothing installed, hand it to anyone,
not only a developer, and let them feel the model for themselves.

If the real question is "what should this look like", stop, that is `UI.md`.

## 1. State the question

One paragraph, at the top of the page itself (visible text, not a comment):
what state model this is, and what question it is answering. Write this down
before the code, a prototype that answers the wrong question is pure waste.

## 2. Isolate the logic in a pure module

Put the actual logic in one `<script>` block written so it could be lifted
into the real codebase later: no DOM access, no `document`, no button
handlers reaching inside it. Pick the shape that fits the question:

- a pure reducer, `(state, action) => state`, for discrete events over one
  state value;
- an explicit state machine when "which actions are even legal right now" is
  part of the question;
- a small set of pure functions when there is no ongoing state, only
  transformations;
- a module with a clear method surface when the logic genuinely owns state
  across calls.

The page only calls into this module, nothing flows back the other way. That
is what makes it liftable once the question is settled.

## 3. Build the page around it

One plain HTML file, everything inline, no framework, no bundler, no server,
opens by double-click. Every label reads in plain domain language, not code.
Lay it out top to bottom:

1. Title plus the one-line question from step 1.
2. Current state, rendered as labelled fields, not raw JSON, re-rendered
   after every action.
3. Free-play buttons, one per action, always available, in any order.
4. Guided walkthroughs, one tab per scenario, each with a short plain
   description and the ordered buttons to press. Starting a walkthrough
   resets to a known initial state so it replays the same way every time.

Pick scenarios that are awkward on paper: the happy path, a tricky edge, an
attempt at something that should be illegal. Keep the visual design plain,
one accent colour, no animation, nothing competing with the state and the
buttons.

## 4. Hand it over, then capture the answer

Send the file or open it. The useful moments are "wait, that should not be
possible" or "huh, I expected X" since those are bugs in the idea, which is
the point. Once satisfied, follow step 5 of `SKILL.md`: the validated
reducer or machine lifts into the real module, the HTML shell either gets
deleted or rides along to a throwaway branch.

## Anti-patterns

Do not add tests. Do not wire it to the real database unless persistence is
the actual question. Do not generalize past this one question. Do not let
the pure module touch the DOM, that breaks the whole point of lifting it out
later.
