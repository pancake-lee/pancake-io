#!/usr/bin/env python3
"""Check post URL identifiers before the Pages build."""

from pathlib import Path
import re
import sys


posts = Path(__file__).resolve().parents[1] / "_posts"
seen = {}
errors = []

for post in sorted(posts.rglob("*.md")):
    text = post.read_text(encoding="utf-8")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not front:
        errors.append(f"{post}: missing YAML front matter")
        continue

    slugs = re.findall(r"^slug:\s*(.*?)\s*$", front.group(1), re.M)
    if len(slugs) > 1:
        errors.append(f"{post}: multiple slug fields")
        continue
    explicit = slugs[0].strip('"\'') if slugs else None
    filename_slug = post.stem[11:]
    if not re.match(r"^\d{4}-\d{2}-\d{2}-.+$", post.stem):
        errors.append(f"{post}: expected YYYY-MM-DD-title.md")
        continue
    if any(ord(char) > 127 for char in filename_slug) and not explicit:
        errors.append(f"{post}: Chinese filename requires an English slug")
        continue

    slug = explicit or filename_slug.lower()
    if explicit and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        errors.append(f"{post}: invalid English slug {slug!r}")
        continue
    if slug in seen:
        errors.append(f"duplicate post URL /posts/{slug}/: {seen[slug]} and {post}")
    else:
        seen[slug] = post

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Checked {len(seen)} post URL identifiers; no conflicts.")
