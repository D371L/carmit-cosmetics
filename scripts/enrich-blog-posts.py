#!/usr/bin/env python3
"""Add SEO fields to existing js/blog-posts.js without calling the API."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_utils import (  # noqa: E402
    build_description,
    build_seo_title,
    og_image_url,
    parse_date_published,
)

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def main() -> None:
    posts = load_posts()
    for post in posts:
        title = post.get("title", "")
        post["seoTitle"] = build_seo_title(title)
        post["description"] = build_description(title)
        post["datePublished"] = parse_date_published(post.get("date", ""))
        post["ogImage"] = og_image_url(post.get("image"), post.get("video"))

    with BLOG_POSTS.open("w", encoding="utf-8") as f:
        f.write("/* Auto-generated from Broadcust API — business uid 12148 */\n")
        f.write("window.BLOG_POSTS = ")
        json.dump(posts, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"Enriched {len(posts)} posts in {BLOG_POSTS}")


if __name__ == "__main__":
    main()
