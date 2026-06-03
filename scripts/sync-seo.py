#!/usr/bin/env python3
"""Replace legacy base URLs across HTML, robots.txt, and JS with seo-config.BASE_URL."""

from __future__ import annotations

import re
from pathlib import Path

from seo_config import BASE_URL, OLD_BASE_URL

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    ROOT / "index.html",
    ROOT / "blog.html",
    ROOT / "post.html",
    ROOT / "accessibility.html",
    ROOT / "privacy.html",
    ROOT / "robots.txt",
    ROOT / "js" / "site-config.js",
    ROOT / "js" / "post.js",
    ROOT / "scripts" / "generate-sitemap.py",
]

POST_DIR = ROOT / "post"


def sync_file(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    updated = text.replace(OLD_BASE_URL, BASE_URL)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def sync_post_pages() -> int:
    count = 0
    if not POST_DIR.exists():
        return 0
    for path in POST_DIR.glob("*.html"):
        if sync_file(path):
            count += 1
    return count


def main() -> None:
    changed = 0
    for path in TARGETS:
        if sync_file(path):
            print(f"Updated {path.relative_to(ROOT)}")
            changed += 1
    post_changed = sync_post_pages()
    if post_changed:
        print(f"Updated {post_changed} post/*.html files")
    if not changed and not post_changed:
        print("All files already use the current BASE_URL.")


if __name__ == "__main__":
    main()
