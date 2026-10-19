# Blog build pipeline

Turns a Claude Docs post into a static page in this repo. Run from `tools/`.

```bash
npm install                     # once: @babel/core, preset-react, react, react-dom
node render.mjs                 # figs/*.jsx  -> post/svg/*.svg
python3 convert.py              # <post>.xml  -> post/body.html
python3 build.py                # -> /blog/<slug>/, /blog/index.html, home section
```

## Why each step exists

**`render.mjs`** — the diagrams in a Claude Docs post are not images. Each is a
zero-argument JSX component returning SVG, so it has to be transpiled (Babel)
and rendered (`react-dom/server`) to get standalone SVG.

It also does two things that are easy to miss:

* **Namespaces every id per diagram.** Each diagram defines its own
  `<marker id='v-arrow'>` or similar. Ten of them inlined on one page would all
  resolve `url(#v-arrow)` to whichever came first, so every arrowhead after the
  first would be wrong — silently, with no error.
* **Strips `data-claude-*`** editor attributes.

The `--cds-*` custom properties are deliberately *left in*. `style.css` maps
them onto the site's own tokens, which is what lets the diagrams follow
light/dark mode. Rasterising to PNG would lose that.

**`convert.py`** — converts the post's prose XML to HTML. It handles every
element the source actually uses (`paragraph`, `text`, `bold`, `italic`,
`code`, `link`, `list`, `listItem`, `table`, `row`, `cell`, `codeBlock`,
`embed`, `date`, `mention`). Enumerate the source's tags before trusting it on
a new post — a converter written from a sample silently drops what it has not
seen.

**`build.py`** — inlines each rendered SVG into its `<figure data-embed>`
placeholder and writes the page, the blog index, and the home-page Blog
section. The home section is regenerated in place between the
`<!-- BLOG:START -->` / `<!-- BLOG:END -->` markers in `/index.html`.

## Adding a post

1. Export the doc's prose XML to `tools/<slug>.xml` and its diagram sources to
   `tools/figs/<node-id>.jsx` (both come from the Claude Docs connector:
   `read` the doc, then its tab, then each `embed` node).
2. Point `SRC` in `convert.py` at the new XML.
3. Append an entry to `POSTS` in `build.py` — slug, title, date, blurb, and
   `preview` (the node id of the diagram to use as the list thumbnail).
4. Re-run the three commands above.

`HOME_LIMIT` controls how many posts the home page shows; the rest stay on
`/blog/`. A News entry on the home page is still added by hand, because that
list interleaves papers and posts.
