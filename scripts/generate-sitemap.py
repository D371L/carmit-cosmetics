#!/usr/bin/env python3
"""Generate sitemap.xml from static pages and js/blog-posts.js."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_config import BASE_URL  # noqa: E402

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
SITEMAP = ROOT.parent / "sitemap.xml"


def load_post_ids() -> list[int]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    posts = json.loads(match.group(1))
    return [int(p["id"]) for p in posts if "id" in p]


def url_entry(loc: str, changefreq: str = "monthly", priority: str = "0.7") -> str:
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{date.today().isoformat()}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


def main() -> None:
    base = BASE_URL.rstrip("/")
    entries = [
        url_entry(f"{base}/", changefreq="weekly", priority="1.0"),
        url_entry(f"{base}/blog.html", changefreq="weekly", priority="0.8"),
        url_entry(f"{base}/accessibility.html", changefreq="yearly", priority="0.3"),
        url_entry(f"{base}/privacy.html", changefreq="yearly", priority="0.3"),
    ]
    for post_id in load_post_ids():
        entries.append(
            url_entry(f"{base}/post/{post_id}.html", changefreq="monthly", priority="0.6")
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    SITEMAP.write_text(xml, encoding="utf-8")
    print(f"Wrote {SITEMAP} ({len(entries)} URLs)")


if __name__ == "__main__":
    main()
