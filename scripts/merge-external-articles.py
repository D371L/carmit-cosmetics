#!/usr/bin/env python3
"""Merge external articles from data/external-articles.json into blog JS files."""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_utils import image_thumb, og_image_url, parse_date_published  # noqa: E402

DATA = ROOT.parent / "data" / "external-articles.json"
BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
BLOG_CONTENT = ROOT.parent / "js" / "blog-content.js"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CarmitCosmetics/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}

META_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\'](?:og:image(?::secure_url)?|twitter:image)["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
META_IMAGE_RE_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image(?::secure_url)?|twitter:image)["\']',
    re.IGNORECASE,
)
ARTICLE_IMG_RE = re.compile(
    r'<img[^>]+(?:itemprop=["\']image["\']|class=["\'][^"\']*article)[^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
LOADED_FILES_IMG_RE = re.compile(
    r'src=["\'](https?://[^"\']+/loadedFiles/[^"\']+\.(?:jpe?g|png|webp))["\']',
    re.IGNORECASE,
)


def load_js_array(path: Path, var_name: str) -> list | dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{var_name}\s*=\s*(\[.*?\]|\{{.*?\}});", text, re.DOTALL)
    if not match:
        return [] if var_name == "BLOG_POSTS" else {}
    return json.loads(match.group(1))


def write_blog_posts(posts: list[dict]) -> None:
    with BLOG_POSTS.open("w", encoding="utf-8") as f:
        f.write("/* Auto-generated — Broadcust API + external articles */\n")
        f.write("window.BLOG_POSTS = ")
        json.dump(posts, f, ensure_ascii=False, indent=2)
        f.write(";\n")


def write_blog_content(content: dict[str, str]) -> None:
    with BLOG_CONTENT.open("w", encoding="utf-8") as f:
        f.write("/* Auto-generated — Broadcust API + external articles */\n")
        f.write("window.BLOG_CONTENT = ")
        json.dump(content, f, ensure_ascii=False, indent=2)
        f.write(";\n")


def fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def validate_image_url(url: str) -> str | None:
    if not url or not url.startswith("https://"):
        return None
    req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if resp.status == 200 and "image" in ctype.lower():
                return resp.url if hasattr(resp, "url") else url
    except urllib.error.HTTPError:
        pass
    except Exception:
        pass
    return None


SKIP_IMAGE_PATTERNS = ("logo", "hamlatza-home", "interuse-animated", "favicon")


def is_skip_image(url: str) -> bool:
    lower = url.lower()
    return any(p in lower for p in SKIP_IMAGE_PATTERNS)


def extract_images_from_html(page_html: str, page_url: str) -> list[str]:
    urls: list[str] = []
    for pattern in (LOADED_FILES_IMG_RE, ARTICLE_IMG_RE, META_IMAGE_RE, META_IMAGE_RE_ALT):
        for match in pattern.finditer(page_html):
            raw = match.group(1).strip()
            if raw.startswith("//"):
                raw = "https:" + raw
            elif raw.startswith("/"):
                from urllib.parse import urljoin

                raw = urljoin(page_url, raw)
            if raw.startswith("https://") and raw not in urls and not is_skip_image(raw):
                urls.append(raw)
    return urls


def resolve_cover_image(article: dict) -> tuple[str, str]:
    """Return (image_url, source_label)."""
    if article.get("image"):
        return article["image"], "json"

    source_url = article.get("sourceUrl", "")
    if source_url:
        try:
            page = fetch_page(source_url)
            for candidate in extract_images_from_html(page, source_url):
                validated = validate_image_url(candidate)
                if validated:
                    print(f"  cover from {source_url}: {validated[:80]}…")
                    return validated, "source"
        except Exception as exc:
            print(f"  cover fetch failed for {source_url}: {exc.__class__.__name__}")

    fallback = article.get("imageFallback", "")
    if fallback:
        print(f"  cover fallback for id {article['id']}")
        return fallback, "fallback"
    return "", "none"


def render_section(section: dict) -> str:
    stype = section.get("type", "p")
    if stype == "h2":
        return f"<h2>{html.escape(section['text'])}</h2>"
    if stype == "p":
        return f"<p>{html.escape(section['text'])}</p>"
    if stype == "ul":
        items = "".join(f"<li>{html.escape(item)}</li>" for item in section.get("items", []))
        return f"<ul>{items}</ul>"
    return ""


def build_body_html(article: dict) -> str:
    parts = [render_section(s) for s in article.get("sections", [])]
    source_url = html.escape(article.get("sourceUrl", ""), quote=True)
    source_name = html.escape(article.get("sourceName", "המקור"))
    parts.append(
        f'<aside class="post-source">'
        f'<p>המאמר פורסם במקור ב-'
        f'<a href="{source_url}" rel="noopener noreferrer" target="_blank">{source_name}</a>'
        f"</p></aside>"
    )
    return f'<div class="post-details">{"".join(parts)}</div>'


def parse_post_date(date_str: str) -> datetime:
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.min


def article_to_post(article: dict, image_url: str) -> dict:
    thumb = image_thumb(image_url) if image_url else ""
    post = {
        "id": article["id"],
        "title": article["title"],
        "seoTitle": article.get("seoTitle", article["title"]),
        "description": article.get("description", ""),
        "date": article["date"],
        "datePublished": parse_date_published(article.get("date", "")),
        "image": thumb,
        "ogImage": og_image_url(thumb),
        "type": article.get("type", "article"),
        "external": True,
        "sourceUrl": article.get("sourceUrl", ""),
    }
    if article.get("thumbPosition"):
        post["thumbPosition"] = article["thumbPosition"]
    return post


def merge_posts(existing: list[dict], external_posts: list[dict]) -> list[dict]:
    external_ids = {p["id"] for p in external_posts}
    merged = [p for p in existing if p.get("id") not in external_ids]
    merged.extend(external_posts)
    merged.sort(key=lambda p: parse_post_date(p.get("date", "")), reverse=True)
    return merged


def main() -> None:
    if not DATA.exists():
        print(f"No external articles file at {DATA}")
        return

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    articles = payload.get("articles", [])
    if not articles:
        print("No articles in external-articles.json")
        return

    posts = load_js_array(BLOG_POSTS, "BLOG_POSTS")
    content = load_js_array(BLOG_CONTENT, "BLOG_CONTENT")

    external_posts: list[dict] = []
    for article in articles:
        print(f"Processing external article {article['id']}: {article['title'][:50]}…")
        image_url, _ = resolve_cover_image(article)
        post = article_to_post(article, image_url)
        external_posts.append(post)
        content[str(article["id"])] = build_body_html(article)

    merged = merge_posts(posts, external_posts)
    write_blog_posts(merged)
    write_blog_content(content)

    print(f"Merged {len(external_posts)} external articles into {BLOG_POSTS}")
    print(f"Updated {len(content)} entries in {BLOG_CONTENT}")


if __name__ == "__main__":
    main()
