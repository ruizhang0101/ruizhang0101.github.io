# ruizhang0101.github.io

Personal academic website for Rui Zhang — https://ruizhang0101.github.io

Plain static HTML/CSS. No build step, no Jekyll (`.nojekyll` is present), no dependencies.
Push to `main` and GitHub Pages serves it.

## Files

| Path | What it is |
|------|-----------|
| `index.html` | The entire site. All content lives here, section by section. |
| `style.css`  | All styling. Design tokens are the `--*` variables at the top. |
| `assets/profile.jpg` | Headshot. Replace with your own; portrait crop, ~450×540 or larger. |
| `assets/figs/*.png` | Publication thumbnails, one per paper (`cachescout`, `apsys`, `vericache`, `evicpress`, `lmcache`, `fairness`). Each is the paper's architecture figure. A missing file removes itself and the entry reflows to text-only. |
| `assets/lmcache-logo.png` | LMCache wordmark, used as the project card title. |
| `assets/production-stack-logo.png` | vLLM Production Stack wordmark, same role. |


The header's **CV** button points back at this page (`#top`) rather than a PDF. To swap in a
real CV, drop `assets/cv.pdf` into the repo and change that link's `href` in `index.html`.

## Editing

**Add a news item** — put a new `<dt>`/`<dd>` pair at the *top* of the `<dl>` inside
`<section id="news">`. Move the `<span class="new-tag">NEW</span>` marker to it and remove
it from the previous entry.

**Add a publication** — copy an `<article class="pub">` block into the `<div
class="pub-group">` for its year, newest first within the group. For a new year, copy a
whole `pub-group` (its `<h3 class="pub-year">` is the year label in the left gutter) and
put it above the others. Wrap your own name in `<span class="me">Rui Zhang</span>` so it
renders bold. Peer-reviewed venues use `<span class="badge accepted">` — the accent
colour — while preprints use plain `<span class="badge">`; the badge omits the year
because the gutter already shows it.

**Education and work history** live as prose in the closing "Previously, ..." paragraph of
`<section id="about">`, and research threads live in the `I've worked on:` list just above it.
Both are deliberately short — the full record is the CV and Google Scholar, not this page.

**Add a service or teaching entry** — add an `<li>` under the matching `<h3>` in
`<section id="services">`. To add a new category (e.g. Conference Reviewing), copy one of
the `<div>` blocks.

**Change the accent color** — edit `--accent`, `--accent-soft`, and `--accent-wash` in
`style.css`. Both the light and dark palettes need updating; they are defined in three
places (`:root`, the `prefers-color-scheme: dark` block, and `:root[data-theme="dark"]`).

## Preview locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000
