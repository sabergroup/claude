# Project showcase

A replacement for the inside of a portfolio project page
(`sabergroup-eg.com/portfolio/<slug>`). It reads the same public projects API
the site uses, so nothing has to be re-uploaded or re-entered.

## What it does automatically

Each material (section) in the CMS gets a layout chosen from its photos'
count and real shapes:

| Section content                 | Layout      | What you see                                   |
|---------------------------------|-------------|------------------------------------------------|
| 1 landscape photo               | `bleed`     | full-width frame                               |
| 1 portrait / square photo       | `single`    | tall frame beside the section text             |
| 2–3 portrait photos             | `row`       | one large row at screen height                 |
| 4–8 portrait photos             | `spotlight` | lead photo stays in place, the rest scroll by  |
| 9+ portrait photos              | `strip`     | full-height filmstrip you swipe or arrow       |
| landscape or mixed shapes       | `justified` | equal-height rows, nothing cropped             |
| videos                          | motion      | play muted on screen, tap for sound            |
| before / after                  | compare     | drag slider                                    |

Other rules:

- The cover becomes a full-width hero only when it is wide and at least
  1800px; smaller covers sit beside the title so they never look blurry.
- Back-to-back video materials merge into one "In motion" section.
- Untitled photo materials with no text join the section before them.
- The text editors type (double spaces, short first line) is split into a
  headline and paragraphs.
- Every photo opens in a full-screen viewer (arrows, swipe, Esc).
- Crew, one "Want a shoot like this?" call to action (WhatsApp with the
  project name filled in) and up to 4 related projects close the page.
- English / Arabic toggle with full right-to-left layout.

To force a layout for one section, set that material's `viewStyle` in the
dashboard to one of the layout names above. `default` keeps it automatic.

## Files

- `showcase.js`, `showcase.css`: the engine. No framework, no build step.
- `index.html`: live page. Open `index.html?slug=<project-slug>`; the
  dropdown at the top switches between all published projects.
- `build_preview.py`: packages one project (data + resized media) for an
  offline preview: `python3 build_preview.py <slug> <out_dir>`.

## Run it locally

```
cd portfolio_showcase
python3 -m http.server 8000
# open http://localhost:8000/?slug=jewelry---new-year-2026-photoshoot
```

## Putting it on the site

The site is a React app, so the cleanest path is to port `normalize()`,
`chooseLayout()` and the render functions into the project page component
and keep `showcase.css`. As a quicker first step, the project route can
render `<main id="showcase">` and load `showcase.js` with
`window.SHOWCASE = { source: "api", imageProxy: "https://images.weserv.nl",
slug }`.
