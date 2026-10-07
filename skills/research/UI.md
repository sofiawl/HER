# UI prototype

Several structurally different variants of one screen, switchable from a
floating bottom bar, so Sofia flips between them in the browser instead of
picking between vague mockups in her head. If the real question is about
logic or state instead of appearance, stop, see research/LOGIC.md.

## 1. Prefer mounting on the existing page

A UI variant is only judgeable next to the real header, sidebar, data and
density, a bare route is a vacuum where everything looks fine. Default to
mounting the variants on the existing route behind a `?variant=` search
param, keeping all the real data fetching, params and auth above the switch,
only the rendered subtree changes.

Only build a brand new throwaway route when the thing being prototyped truly
has no existing page to live inside (an entirely new top-level surface).
Follow whatever routing convention the project already uses, and put the
word "prototype" in the path or filename so it is obviously not real.
Whichever you pick, the floating switcher below is identical.

## 2. State the question, pick the count

Default to three variants, more than five stops being "radically different"
and starts being noise. Write the plan in one line at the top of the file or
route: what is being varied, how many variants, on which route.

## 3. Make the variants actually different

Each variant must be structurally different from the others: different
layout, different information hierarchy, different primary action, not just
a different colour or copy. If two drafts feel too similar, redo one of them
with an explicit constraint, for example "no card grid here". Hold each
variant to the page's real purpose, the data it actually has, and the
project's existing component library.

## 4. Wire the switcher

One switcher reads the `variant` search param (default to the first variant)
and renders the matching component, `VariantA`, `VariantB`, `VariantC`, and
so on, using the project's router so the URL stays shareable and reload
stable. Put the floating bar in whatever shared UI location the project
already uses:

- fixed to the bottom centre of the screen;
- a previous arrow, the current variant's key and name, a next arrow, both
  arrows wrap around;
- left and right arrow keys also cycle, except while an input, textarea or
  editable element has focus;
- visually distinct from the page itself, a clear pill or bar, not part of
  the design being judged;
- gated so it never renders in a production build.

## 5. Hand it over, then capture the answer

Give Sofia the URL and the variant keys. The useful feedback is usually "the
header from B with the sidebar from C", that combination is the actual
design she wants, build a fourth variant for it if needed. Once one wins,
follow research spike mode (SKILL.md): fold the winner into the real page (rewritten
properly, prototype code skipped tests and error handling on purpose), and
either delete the losing variants and the switcher or push the full set to
a throwaway branch before dropping them from the real page.

## Anti-patterns

Variants that only differ in colour or copy are not variants. Do not share a
full layout component between variants, a shared header is fine, a shared
layout defeats the point. Do not wire a variant to a real mutation, point it
at a stub instead. Never ship the switcher or the losing variants past the
branch that proved the point.
