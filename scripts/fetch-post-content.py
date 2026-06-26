#!/usr/bin/env python3
"""Fetch article details from Broadcust API into js/blog-content.js."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_POSTS = ROOT / "js" / "blog-posts.js"
OUT = ROOT / "js" / "blog-content.js"

API = "https://broadcust.co.il/api/deal/get/{post_id}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CarmitCosmetics/1.0)",
    "Accept": "application/json",
}

SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
DETAILS_WRAPPER_RE = re.compile(
    r'^<p[^>]*ng-bind-html[^>]*class="ng-binding"[^>]*>',
    re.IGNORECASE | re.DOTALL,
)


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def load_existing_content() -> dict[str, str]:
    if not OUT.exists():
        return {}
    text = OUT.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_CONTENT\s*=\s*(\{.*?\});", text, re.DOTALL)
    if not match:
        return {}
    return json.loads(match.group(1))


def sanitize_html(html: str) -> str:
    return SCRIPT_RE.sub("", html or "").strip()


def clean_details(raw: str) -> str:
    details = sanitize_html(raw)
    if not details:
        return ""

    details = DETAILS_WRAPPER_RE.sub("", details)
    details = re.sub(r"^<p[^>]*>", "", details, count=1, flags=re.IGNORECASE)
    if details.endswith("</p>"):
        details = details[: -len("</p>")].rstrip()

    return details.strip()


def build_full_content(details: str) -> str:
    body = clean_details(details)
    if not body:
        return ""
    return f'<div class="post-details">{body}</div>'


def fetch_post(post_id: int) -> tuple[str | None, str, bool]:
    """Return stored HTML, status, details_ok."""
    req = urllib.request.Request(API.format(post_id=post_id), headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        details = clean_details(data.get("details") or "")
        combined = build_full_content(details)

        if combined:
            return combined, "ok", bool(details)
        return None, "empty", bool(details)
    except urllib.error.HTTPError as exc:
        return None, f"http_{exc.code}", False
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}", False


def write_content(content: dict[str, str]) -> None:
    with OUT.open("w", encoding="utf-8") as f:
        f.write("/* Auto-generated — article body (details) from Broadcust API */\n")
        f.write("window.BLOG_CONTENT = ")
        json.dump(content, f, ensure_ascii=False, indent=2)
        f.write(";\n")


def audit_content(html: str) -> bool:
    return "post-details" in html and bool(
        re.search(r"post-details[\s\S]*(<p|<table|<img|<video)", html, re.IGNORECASE)
    )


def audit_all_posts(posts: list[dict], content: dict[str, str]) -> bool:
    print("\nAudit:")
    print(f"{'id':<10} {'type':<8} {'image':<8} {'details':<8} ok")
    print("-" * 46)
    all_ok = True

    for post in posts:
        post_id = post["id"]
        ptype = post.get("type", "?")

        if ptype == "video":
            ok = bool(post.get("video"))
            print(f"{post_id:<10} {'video':<8} {'n/a':<8} {'n/a':<8} {'yes' if ok else 'NO'}")
            if not ok:
                all_ok = False
            continue

        if post.get("external"):
            html = content.get(str(post_id), "")
            image_ok = bool(post.get("image"))
            details_ok = audit_content(html)
            ok = image_ok and details_ok
            print(
                f"{post_id:<10} {'article':<8} "
                f"{'yes' if image_ok else 'NO':<8} "
                f"{'yes' if details_ok else 'NO':<8} "
                f"{'yes' if ok else 'NO'} (external)"
            )
            if not ok:
                all_ok = False
            continue

        html = content.get(str(post_id), "")
        image_ok = bool(post.get("image"))
        details_ok = audit_content(html)
        ok = image_ok and details_ok
        print(
            f"{post_id:<10} {'article':<8} "
            f"{'yes' if image_ok else 'NO':<8} "
            f"{'yes' if details_ok else 'NO':<8} "
            f"{'yes' if ok else 'NO'}"
        )
        if not ok:
            all_ok = False

    return all_ok


def main() -> None:
    posts = load_posts()
    articles = [p for p in posts if p.get("type") == "article"]
    if not articles:
        print("No article posts found.")
        return

    content = load_existing_content()
    ok: list[int] = []
    empty: list[int] = []
    failed: list[tuple[int, str]] = []
    kept: list[int] = []

    for post in articles:
        if post.get("external"):
            print(f"  skip external {post['id']}")
            continue
        post_id = int(post["id"])
        combined, status, details_ok = fetch_post(post_id)
        key = str(post_id)

        if combined and details_ok:
            content[key] = combined
            ok.append(post_id)
        elif combined:
            content[key] = combined
            ok.append(post_id)
            print(f"  partial {post_id}: details={details_ok}")
        elif key in content and content[key]:
            kept.append(post_id)
            failed.append((post_id, f"{status}(kept cached)"))
        elif status == "empty":
            empty.append(post_id)
        else:
            failed.append((post_id, status))

        time.sleep(0.15)

    if not content:
        print("No content to write — keeping existing file if any.")
        sys.exit(1)

    write_content(content)

    print(f"\nWrote {OUT} ({len(content)} articles)")
    print(f"  fetched ok: {len(ok)}")
    if kept:
        print(f"  kept cached: {len(kept)}")
    if empty:
        print(f"  empty: {empty}")
    if failed:
        print(f"  failed: {failed}")

    missing = [
        p["id"]
        for p in articles
        if not p.get("external") and str(p["id"]) not in content
    ]
    if missing:
        print(f"  WARNING missing content for: {missing}")
        sys.exit(1)

    if not audit_all_posts(posts, content):
        sys.exit(1)


if __name__ == "__main__":
    main()
