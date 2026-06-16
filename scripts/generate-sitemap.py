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
from seo_utils import parse_date_iso_date  # noqa: E402

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
SITEMAP = ROOT.parent / "sitemap.xml"

STATIC_PAGES = [
    ("", "weekly", "1.0", None),
    ("blog.html", "weekly", "0.8", None),
    ("accessibility.html", "yearly", "0.3", None),
    ("privacy.html", "yearly", "0.3", None),
]


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def file_lastmod(path: Path) -> str:
    if path.exists():
        mtime = date.fromtimestamp(path.stat().st_mtime)
        return mtime.isoformat()
    return date.today().isoformat()


def url_entry(
    loc: str,
    lastmod: str,
    changefreq: str = "monthly",
    priority: str = "0.7",
    image: str | None = None,
    image_title: str | None = None,
) -> str:
    image_block = ""
    if image:
        title_line = ""
        if image_title:
            title_line = f"\n      <image:title>{_xml_esc(image_title)}</image:title>"
        image_block = f"""
    <image:image>
      <image:loc>{_xml_esc(image)}</image:loc>{title_line}
    </image:image>"""
    return f"""  <url>
    <loc>{_xml_esc(loc)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>{image_block}
  </url>"""


def _xml_esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def main() -> None:
    base = BASE_URL.rstrip("/")
    posts = load_posts()
    today = date.today().isoformat()
    entries: list[str] = []

    for page, changefreq, priority, _ in STATIC_PAGES:
        loc = f"{base}/" if not page else f"{base}/{page}"
        path = ROOT.parent / page if page else ROOT.parent / "index.html"
        lastmod = file_lastmod(path)
        entries.append(url_entry(loc, lastmod, changefreq, priority))

    for post in posts:
        post_id = post.get("id")
        if not post_id:
            continue
        loc = f"{base}/post/{post_id}.html"
        lastmod = parse_date_iso_date(post.get("date", "")) or today
        og_image = post.get("ogImage", "")
        title = post.get("seoTitle") or post.get("title", "")
        entries.append(
            url_entry(loc, lastmod, "monthly", "0.6", og_image or None, title or None)
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    SITEMAP.write_text(xml, encoding="utf-8")
    print(f"Wrote {SITEMAP} ({len(entries)} URLs)")


if __name__ == "__main__":
    main()
