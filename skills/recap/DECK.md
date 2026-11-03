# Recap deck

Shared by `/her:recap`. Derived from the S07E06 deck built for the 2026-10-20 to 2026-10-26 recap (`~/Documents/kinebot-reports/presentations/niosh-semana-20-26-10/`). When in doubt, do what that deck does.

## 1. Slide plan (shown before building)

Text only, in pt-BR. At most 5 content slides, "pretty simple", plus a last next-steps slide when open cards exist. Format per slide:

- Title and kicker (card IDs and repo, for example `ML-184 · cosmos`)
- 2 to 5 bullets, each short, before to after where something changed ("Video travado no ffmpeg → agora tem timeout")
- The metrics, bold: counts, time per video, cost per video, error before and after, with n
- The image: file path and why it proves the slide
- Source of every number (file or card)

Typical slides:

1. **Resumo**: the 2 to 4 headline numbers of the week and one image.
2. **Robustez ou correções** (one per big theme): bullets of before to after, the success count, a small before and after strip, a table of what still fails and why.
3. **Precisão**: a before and after table of mean error per measure, the note about ground truth and n, an image of the method working.
4. **Exemplo**: one real run, every input and output side by side with the user's value when it exists, the KPI strip (risk index, time, cost), tokens and cost per model.
5. **Processo e ferramentas**: only when it carries a number (reviews pending, PR split). A simple flow diagram is fine as the image.
6. **Próximos passos**: open questions and decisions, one card per column with a link (`https://loop.zslippy.com/issue/<CARD>`), due dates, and review counts when she asks for them.

Questions to put at the end of the plan, only for real gaps: cost source, an image that does not exist, an ambiguous word, a number you could not verify.

## 2. Folder and template

- Template: `~/kinebot-latex-templates/templates/apresentacao/index.html` (single file deck, CSS and navigation inside).
- Output: `~/Documents/kinebot-reports/presentations/<slug>/` with `index.html` and `img/`. Slug: `<tema>-semana-<d>-<d>-<m>`, lowercase, no accents. Decks are never committed to the templates repo.
- Copy the template, replace the `<section class="slide">` blocks, the footer text in `.frame-footer` and the `DATA` object. Delete example slides and any `chart()` call that points to a removed chart. Add the extra CSS the slides need after the template styles.
- Do not add comments to the HTML.
- Images: copy into `img/` with descriptive snake_case names. Check sizes with PIL before placing them.

## 3. Slide rules

- **Cover:** simple. The cycle label (for example `S07E06`) as the big blue title and her name below. Nothing else.
- **Footer on every slide:** the cycle label only.
- Decimal comma, units after a space (`21,7 cm`, `US$ 0,012`), `→` for before to after, `n` stated under any table.
- Words a reader could take two ways get defined in the same line: "relatórios produzidos" is not "relatórios com métricas confiáveis". Prefer plain words over internal jargon.
- Cost and time: say the statistic (mean error, median) and the unit. Cost shows tokens too when part of the pipeline runs on own hardware at zero API cost.
- The image on a slide must match its text: a distance above the table limit shows the real measured value and the clamped value, a "now works" claim shows the frame from the run that now works.
- A table row she asked to drop stays dropped on every later render.

## 4. Render and check

Render from the deck folder (the window must be 1280x720, the charts are drawn at screen size):

```bash
google-chrome --headless=new --disable-gpu --window-size=1280,720 --no-pdf-header-footer --virtual-time-budget=3000 --print-to-pdf=<slug>.pdf index.html
pdfinfo <slug>.pdf | grep Pages
pdftoppm -r 60 -png <slug>.pdf <scratchpad>/pg
```

Then read the PNGs (a contact sheet of two columns is enough, one page at full size for any doubt) and check:

- no image cut by text, no text cut by the slide edge, images as large as the layout allows
- portrait video or image: make it taller, not wider; text goes beside it, never over it
- the page count equals the planned slide count, the cover and the footer show the cycle label
- every number matches the plan and its source (a subagent re-checks, see SKILL.md step 7)
- `grep -nP '[\x{2013}\x{2014}]|[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]' index.html` returns nothing
- no key, token or personal address in the HTML: `grep -niE 'api[_-]?key|token=|secret|@[a-z0-9.-]+\.[a-z]{2,}' index.html` shows nothing unexpected

## 5. Optional video

Only when she asks. Invoke `/remotion-create` through a `sonnet` subagent. Brief it with: output project `<deck folder>/video-<tema>/`, render `<deck folder>/video-<tema>.mp4`, 1920x1080, 30 fps, about 12 s, on-screen text in pt-BR and short, which real images from the research folder to use, which example was untrusted before and trusted now, and "do not commit or touch other projects".

Embed it in the slide as `<video>` with a poster frame. Slow it down for reading (an ffmpeg `setpts` stretch), keep text beside it and the frame uncropped. If she says it is bloated or cut, shrink the video column, enlarge the images and move captions beside it, then re-render and look again.

## 6. Her edits

She iterates in short messages ("remove this slide", "add a column", "this count is wrong"). Edit `index.html` in place with exact replacements (assert the old string occurs once), re-render, look at the changed page, and re-check any number you touched against its source. A correction of a number is a prompt to re-verify the neighbouring numbers, not only that one.
