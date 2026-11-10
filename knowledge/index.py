#!/usr/bin/env python3
"""Regenerate a knowledge module's index.md files from page descriptions.

Usage: index.py MODULE_DIR [--check]
Each folder gets an index.md listing its subfolders and its pages (`description` frontmatter).
An existing index keeps its own description and heading. Optional `MODULE_DIR/.index-groups.tsv`
(title<TAB>regex, first match wins) groups the root pages under headings.
--check writes nothing and exits 1 if any index would change (the lint check).
"""
import os, re, sys

root = os.path.abspath(sys.argv[1]); check = "--check" in sys.argv
desc_re = re.compile(r'\A---\n(?:.*\n)*?description:\s*"?(.*?)"?\s*\n(?:.*\n)*?---\n')

def meta(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None, None
    m = desc_re.match(text); h = re.search(r"^# (.+)$", text, re.M)
    return (m.group(1).replace('\\"', '"') if m else None), (h.group(1) if h else None)

def skip(d):  # hidden folders and nested git repositories are not part of this module
    return os.path.basename(d).startswith(".") or (d != root and os.path.exists(os.path.join(d, ".git")))

groups = []
gfile = os.path.join(root, ".index-groups.tsv")
if os.path.exists(gfile):
    groups = [l.rstrip("\n").split("\t", 1) for l in open(gfile, encoding="utf-8") if "\t" in l]

# A folder gets an index if it already has one or holds described pages, directly or below.
keep = set()
for d, dirs, files in os.walk(root, topdown=True):
    dirs[:] = [x for x in dirs if not skip(os.path.join(d, x))]
    if "index.md" in files or any(f.endswith(".md") and meta(os.path.join(d, f))[0] for f in files):
        p = d
        while p.startswith(root) and p not in keep:
            keep.add(p); p = os.path.dirname(p)

changed = []
for d, dirs, files in os.walk(root, topdown=True):
    dirs[:] = sorted(x for x in dirs if os.path.join(d, x) in keep)
    if d not in keep:
        continue
    own_desc, own_title = meta(os.path.join(d, "index.md"))
    rel = os.path.relpath(d, root)
    title = own_title or os.path.basename(d)
    desc = own_desc or f"Pages in {title}."
    out = [f'---\ndescription: "{desc.replace(chr(34), chr(92) + chr(34))}"\n---\n', f"# {title}\n"]
    if dirs:
        out.append("## Folders\n" if rel == "." and groups else "")
        for s in dirs:
            sd, _ = meta(os.path.join(d, s, "index.md"))
            out.append(f"- [{s}]({s.replace(' ', '%20')}/index.md): {sd or 'Pages in ' + s + '.'}")
        out.append("")
    pages = []
    for f in sorted(files, key=str.lower):
        if f.endswith(".md") and f != "index.md":
            pd, _ = meta(os.path.join(d, f))
            if pd:
                pages.append((f[:-3], pd))
    if rel == "." and groups:
        for gt, rx in groups:
            hit = [p for p in pages if re.search(rx, p[0] + ".md")]
            pages = [p for p in pages if p not in hit]
            if hit:
                out += [f"## {gt}\n"] + [f"- [[{n}]]: {t}" for n, t in hit] + [""]
    out += [f"- [[{n}]]: {t}" for n, t in pages]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip("\n") + "\n"
    path = os.path.join(d, "index.md")
    if not os.path.exists(path) or open(path, encoding="utf-8").read() != text:
        changed.append(os.path.relpath(path, root))
        if not check:
            open(path, "w", encoding="utf-8").write(text)

print("\n".join(changed) if changed else "indexes up to date")
sys.exit(1 if check and changed else 0)
