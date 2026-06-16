#!/usr/bin/env python3
"""Generate SEO meta blocks and JSON-LD for static site pages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_config import (  # noqa: E402
    BASE_URL,
    DEFAULT_OG_IMAGE,
    EMAIL,
    FACEBOOK_URL,
    FULL_NAME,
    GEO_LAT,
    GEO_LNG,
    LOGO,
    MAPS_DIR_URL,
    PAGE_META,
    PHONE,
    SITE_NAME,
    TAGLINE,
)
from seo_head import render_icon_links, render_social_meta  # noqa: E402

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
SEO_BEGIN = "<!-- SEO:BEGIN -->"
SEO_END = "<!-- SEO:END -->"
JSONLD_BEGIN = "<!-- SEO:JSONLD:BEGIN -->"
JSONLD_END = "<!-- SEO:JSONLD:END -->"


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def latest_blog_og_image(posts: list[dict]) -> str:
    for post in posts:
        og = post.get("ogImage")
        if og:
            return og
    return DEFAULT_OG_IMAGE


def page_url(path: str) -> str:
    base = BASE_URL.rstrip("/")
    if path == "/":
        return f"{base}/"
    return f"{base}{path}"


def render_index_jsonld() -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "BeautySalon",
        "name": FULL_NAME,
        "description": TAGLINE,
        "url": page_url("/"),
        "telephone": PHONE,
        "email": EMAIL,
        "image": DEFAULT_OG_IMAGE,
        "priceRange": "₪₪",
        "hasMap": MAPS_DIR_URL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "הראשונים 39",
            "addressLocality": "קרית חיים",
            "addressCountry": "IL",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": GEO_LAT,
            "longitude": GEO_LNG,
        },
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
            ],
            "opens": "09:00",
            "closes": "19:00",
        },
        "sameAs": [FACEBOOK_URL],
    }
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": FULL_NAME,
        "url": page_url("/"),
        "inLanguage": "he-IL",
    }
    return (
        f'  <script type="application/ld+json">\n'
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        f"  </script>\n"
        f'  <script type="application/ld+json">\n'
        f"{json.dumps(website, ensure_ascii=False, indent=2)}\n"
        f"  </script>"
    )


def render_blog_jsonld(posts: list[dict]) -> str:
    base = BASE_URL.rstrip("/")
    blog = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": f"בלוג — {SITE_NAME}",
        "url": f"{base}/blog.html",
        "inLanguage": "he-IL",
        "publisher": {
            "@type": "Organization",
            "name": FULL_NAME,
            "logo": {"@type": "ImageObject", "url": LOGO},
        },
    }
    items = []
    for post in posts[:10]:
        post_id = post.get("id")
        if not post_id:
            continue
        items.append(
            {
                "@type": "ListItem",
                "position": len(items) + 1,
                "url": f"{base}/post/{post_id}.html",
                "name": post.get("seoTitle") or post.get("title", ""),
                "image": post.get("ogImage") or post.get("image", ""),
            }
        )
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": items,
    }
    return (
        f'  <script type="application/ld+json">\n'
        f"{json.dumps(blog, ensure_ascii=False, indent=2)}\n"
        f"  </script>\n"
        f'  <script type="application/ld+json">\n'
        f"{json.dumps(item_list, ensure_ascii=False, indent=2)}\n"
        f"  </script>"
    )



def replace_block(text: str, begin: str, end: str, content: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"Markers {begin} / {end} not found")
    return pattern.sub(f"{begin}\n{content}\n{end}", text, count=1)


def main() -> None:
    posts = load_posts()
    blog_og = latest_blog_og_image(posts)

    for filename, meta in PAGE_META.items():
        path = ROOT.parent / filename
        if not path.exists():
            print(f"Skip missing {filename}")
            continue

        page_meta = dict(meta)
        if filename == "blog.html" and not page_meta["og_image"]:
            page_meta["og_image"] = blog_og

        text = path.read_text(encoding="utf-8")
        social = render_social_meta(
            title=page_meta["title"],
            description=page_meta["description"],
            url=page_url(page_meta["path"]),
            og_image=page_meta["og_image"],
            og_image_alt=page_meta["og_image_alt"],
            og_type=page_meta.get("og_type", "website"),
        )
        seo_block = f"{social}\n{render_icon_links()}"
        text = replace_block(text, SEO_BEGIN, SEO_END, seo_block)

        if filename == "index.html":
            text = replace_block(text, JSONLD_BEGIN, JSONLD_END, render_index_jsonld())
        elif filename == "blog.html":
            text = replace_block(text, JSONLD_BEGIN, JSONLD_END, render_blog_jsonld(posts))

        path.write_text(text, encoding="utf-8")
        print(f"Updated {filename}")


if __name__ == "__main__":
    main()
