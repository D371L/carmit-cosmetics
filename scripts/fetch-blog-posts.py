#!/usr/bin/env python3
"""Fetch blog posts from Broadcust API and write js/blog-posts.js with SEO fields."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_utils import (  # noqa: E402
    build_description,
    build_seo_title,
    image_thumb,
    og_image_url,
    parse_date_published,
    video_thumb,
)

API = (
    "https://broadcust.co.il/api/business/campaigns"
    "?uid=12148&types=10,40,50,60,70,75,80,110,120,130&from=0&count=50"
)
OUT = ROOT.parent / "js" / "blog-posts.js"


def clean_title(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def main() -> None:
    with urllib.request.urlopen(API, timeout=30) as resp:
        campaigns = json.load(resp)["campaigns"]

    seen: set[str] = set()
    posts = []
    for c in sorted(campaigns, key=lambda x: x.get("send_timestamp", 0), reverse=True):
        pic = c.get("picture") or ""
        if not pic:
            continue
        title = clean_title(c.get("subject"))
        if not title or title in seen:
            continue
        seen.add(title)
        ct = c.get("content_type")
        vu = c.get("video_url") or ""
        is_video = ct == 3
        if is_video and vu:
            thumb = video_thumb(vu)
        else:
            thumb = image_thumb(pic)

        post = {
            "id": c["id"],
            "title": title,
            "seoTitle": build_seo_title(title),
            "description": build_description(title),
            "date": c.get("send_time", ""),
            "datePublished": parse_date_published(c.get("send_time", "")),
            "image": thumb,
            "ogImage": og_image_url(thumb, vu if is_video else None),
            "type": "video" if is_video else "article",
        }
        if is_video and ".mp4" in vu:
            post["video"] = vu
        posts.append(post)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("/* Auto-generated from Broadcust API — business uid 12148 */\n")
        f.write("window.BLOG_POSTS = ")
        json.dump(posts, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"Wrote {len(posts)} posts to {OUT}")

    merge_script = ROOT / "merge-external-articles.py"
    if merge_script.exists():
        subprocess.run([sys.executable, str(merge_script)], check=True)


if __name__ == "__main__":
    main()
