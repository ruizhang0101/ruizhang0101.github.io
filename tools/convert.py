"""Convert the Claude Docs prose XML for the coordinator post into body HTML.

Handles every element the doc actually uses (enumerated from the source, not
guessed): doc, paragraph, text, bold, italic, code, link, list, listItem,
table, row, cell, codeBlock, embed, date, mention.
"""

import html
import pathlib
import re
import xml.etree.ElementTree as ET

SRC = pathlib.Path(__file__).parent / "lmcache-coordinator.xml"
OUT = pathlib.Path(__file__).parent / "post" / "body.html"

# Anchor ids in the doc are block ids like "mx1peyxx9jn.363"; the table of
# contents links to them, so headings must carry the same ids.
SLUG_RE = re.compile(r"[^a-z0-9]+")


def esc(s):
    return html.escape(s, quote=False)


def inline(el):
    """Render a <text> node's children (bold/italic/code/link) plus its text."""
    out = []
    if el.text:
        out.append(esc(el.text))
    for child in el:
        tag = child.tag
        inner = inline(child)
        if tag == "bold":
            out.append(f"<strong>{inner}</strong>")
        elif tag == "italic":
            out.append(f"<em>{inner}</em>")
        elif tag == "code":
            out.append(f"<code>{inner}</code>")
        elif tag == "link":
            href = esc(child.get("href", ""))
            out.append(f'<a href="{href}">{inner}</a>')
        elif tag == "date":
            v = esc(child.get("value", ""))
            out.append(f'<time datetime="{v}">{v}</time>')
        elif tag == "mention":
            out.append(esc(child.get("name", "")))
        else:
            out.append(inner)
        if child.tail:
            out.append(esc(child.tail))
    return "".join(out)


def para_content(el):
    """A <paragraph>'s inline content: its <text>/<date>/<mention> children."""
    out = []
    if el.text:
        out.append(esc(el.text))
    for child in el:
        if child.tag == "text":
            out.append(inline(child))
        elif child.tag == "date":
            v = esc(child.get("value", ""))
            out.append(f'<time datetime="{v}">{v}</time>')
        elif child.tag == "mention":
            out.append(esc(child.get("name", "")))
        if child.tail:
            out.append(esc(child.tail))
    return "".join(out).strip()


def render(el, out, skip_title=True):
    tag = el.tag

    if tag == "paragraph":
        heading = el.get("heading")
        content = para_content(el)
        if not content:
            return
        if heading:
            lvl = int(heading)
            if lvl == 1 and skip_title:
                return  # the title is rendered by the page template
            out.append(f'<h{lvl} id="{el.get("id","")}">{content}</h{lvl}>')
        else:
            out.append(f'<p id="{el.get("id","")}">{content}</p>')

    elif tag == "list":
        t = "ol" if el.get("kind") == "ordered" else "ul"
        out.append(f"<{t}>")
        for item in el:
            out.append("<li>")
            for sub in item:
                render(sub, out)
            out.append("</li>")
        out.append(f"</{t}>")

    elif tag == "table":
        rows = list(el)
        head = [r for r in rows if all(c.get("header") == "true" for c in r)]
        body = [r for r in rows if r not in head]
        out.append('<div class="table-wrap"><table>')
        if head:
            out.append("<thead>")
            for r in head:
                out.append("<tr>")
                for c in r:
                    out.append(f"<th>{''.join(para_content(p) for p in c)}</th>")
                out.append("</tr>")
            out.append("</thead>")
        out.append("<tbody>")
        for r in body:
            out.append("<tr>")
            for c in r:
                cell = []
                for p in c:
                    render(p, cell)
                inner = "".join(cell)
                # single-paragraph cells read better unwrapped
                m = re.fullmatch(r'<p id="[^"]*">(.*)</p>', inner, re.S)
                out.append(f"<td>{m.group(1) if m else inner}</td>")
            out.append("</tr>")
        out.append("</tbody></table></div>")

    elif tag == "codeBlock":
        lang = el.get("language", "")
        code = "".join(t.text or "" for t in el) or (el.text or "")
        cls = f' class="language-{esc(lang)}"' if lang else ""
        out.append(f"<pre><code{cls}>{esc(code)}</code></pre>")

    elif tag == "embed":
        ref = el.get("ref", "")
        node = ref.split("/")[-1]
        cap = esc(el.get("caption", ""))
        # filled in with the rendered SVG by build.py
        out.append(f'<figure data-embed="{node}"><figcaption>{cap}</figcaption></figure>')


def main():
    root = ET.fromstring(SRC.read_text())
    out = []
    for el in root:
        render(el, out)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out))
    print(f"wrote {OUT}  ({len(''.join(out))} chars, {len(out)} blocks)")


if __name__ == "__main__":
    main()
