// Render each figs/<node>.jsx (a zero-arg component returning SVG) to a
// standalone .svg file.
//
// Two transforms are applied on the way out:
//   * ids are namespaced per diagram — every diagram defines its own
//     <marker id='...'>, and ten inlined SVGs sharing one id would make all
//     url(#...) references resolve to whichever came first.
//   * the editor-only data-claude-* attributes are stripped.
//
// The --cds-* custom properties are left intact; style.css maps them onto the
// site's own tokens so the diagrams follow light/dark with the page.

import { readdirSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { transformAsync } from "@babel/core";
import presetReact from "@babel/preset-react";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = dirname(fileURLToPath(import.meta.url));
const figDir = join(here, "figs");
const outDir = join(here, "post", "svg");
mkdirSync(outDir, { recursive: true });

const files = readdirSync(figDir).filter((f) => f.endsWith(".jsx"));
if (!files.length) {
  console.error("no .jsx files in figs/");
  process.exit(1);
}

for (const file of files) {
  const node = basename(file, ".jsx");
  const src = readFileSync(join(figDir, file), "utf8");

  const { code } = await transformAsync(src, {
    presets: [[presetReact, { runtime: "classic", pragma: "React.createElement" }]],
    configFile: false,
    babelrc: false,
  });

  // the module is `export default () => <svg…>`; evaluate it with React in scope
  const body = code.replace(/export\s+default\s+/, "return ");
  const component = new Function("React", body)(React);
  let svg = renderToStaticMarkup(React.createElement(component));

  // namespace every id so ten inlined SVGs don't collide
  const prefix = `d${node.slice(0, 8)}-`;
  const ids = [...svg.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
  for (const id of new Set(ids)) {
    const esc = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    svg = svg
      .replace(new RegExp(`(\\sid=")${esc}(")`, "g"), `$1${prefix}${id}$2`)
      .replace(new RegExp(`url\\(#${esc}\\)`, "g"), `url(#${prefix}${id})`)
      .replace(new RegExp(`(\\shref=")#${esc}(")`, "g"), `$1#${prefix}${id}$2`);
  }

  // drop editor-only attributes
  svg = svg.replace(/\sdata-claude-(?:text-id|anchor)="[^"]*"/g, "");

  writeFileSync(join(outDir, `${node}.svg`), svg);
  const ok = !/url\(#(?!d)/.test(svg);
  console.log(
    `${node}.svg  ${svg.length} bytes  ids:${new Set(ids).size}  refs-namespaced:${ok}`,
  );
}
