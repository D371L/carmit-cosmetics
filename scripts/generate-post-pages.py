#!/usr/bin/env python3
"""Generate static post/{id}.html pages with server-rendered Open Graph meta."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_config import (  # noqa: E402
    BASE_URL,
    DEFAULT_OG_IMAGE,
    DEFAULT_OG_IMAGE_ALT,
    FULL_NAME,
    LOCALE,
    SITE_NAME,
)

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
OUT_DIR = ROOT.parent / "post"

OG_IMAGE = DEFAULT_OG_IMAGE
LOGO = (
    "https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/"
    "v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png"
)


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def json_ld(post: dict, page_url: str, og_image: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.get("seoTitle") or post.get("title", ""),
        "description": post.get("description", ""),
        "image": og_image,
        "url": page_url,
        "inLanguage": "he-IL",
        "author": {"@type": "Person", "name": "כרמית אסולין"},
        "publisher": {
            "@type": "Organization",
            "name": FULL_NAME,
            "logo": {"@type": "ImageObject", "url": LOGO},
        },
    }
    if post.get("datePublished"):
        payload["datePublished"] = post["datePublished"]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_post(post: dict) -> str:
    post_id = post["id"]
    seo_title = post.get("seoTitle") or post.get("title", "פרסום")
    description = post.get("description") or seo_title
    og_image = post.get("ogImage") or OG_IMAGE
    page_url = f"{BASE_URL.rstrip('/')}/post/{post_id}.html"
    image_alt = esc(seo_title)

    article_time = ""
    if post.get("datePublished"):
        article_time = (
            f'  <meta property="article:published_time" content="{esc(post["datePublished"])}">\n'
        )

    ld = json_ld(post, page_url, og_image)

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(page_url)}">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="{esc(seo_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(page_url)}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="{LOCALE}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta property="og:image:secure_url" content="{esc(og_image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{image_alt}">
{article_time}  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(seo_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image)}">
  <title>{esc(seo_title)}</title>
  <script type="application/ld+json">
{ld}
  </script>
  <link rel="icon" href="{LOGO}" type="image/png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;600;700&family=Heebo:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous">
  <link rel="stylesheet" href="../css/styles.css">
  <link rel="stylesheet" href="../css/a11y.css">
</head>
<body>
  <script src="../js/page-loader.js"></script>
  <div class="scroll-progress" id="scrollProgress" aria-hidden="true"></div>

  <div class="ambient-glows" aria-hidden="true">
    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>
    <div class="ambient-glow glow-3"></div>
  </div>

  <div class="app">
    <header class="post-header">
      <a href="../blog.html" class="post-back">
        <i class="fas fa-arrow-right" aria-hidden="true"></i>
        חזרה לבלוג
      </a>
      <h1 id="postTitle" class="post-title">טוען…</h1>
      <p id="postDate" class="post-date"></p>
    </header>

    <main class="post-main">
      <p id="postLoading" class="post-loading">טוען פרסום…</p>
      <p id="postError" class="post-error" hidden></p>
      <div id="postBody" class="post-body"></div>
    </main>

    <footer class="site-footer">
      <p><a href="../index.html">דף הבית</a></p>
      <p class="copyright">
        <span>2026 ©</span>
        <span>כרמית אסולין קוסמטיקה מתקדמת</span>
      </p>
      <div class="footer-credit">
        <p class="footer-credit-text">
          פותח עם <span aria-hidden="true">❤️</span> על ידי
          <a href="https://hellsec.dev/" target="_blank" rel="noopener noreferrer">HellSec</a>
        </p>
        <a href="https://hellsec.dev/" class="footer-credit-logo" target="_blank" rel="noopener noreferrer" aria-label="HellSec — פיתוח אתרים">
          <img src="../images/hellsec-logo.png" alt="" width="52" height="52">
        </a>
      </div>
    </footer>

    <a href="https://wa.me/972524677347" class="fab-whatsapp" target="_blank" rel="noopener" aria-label="ווטסאפ">
      <i class="fab fa-whatsapp"></i>
    </a>

    <button type="button" class="fab-scroll-top" id="scrollTopBtn" aria-label="חזרה למעלה">
      <i class="fas fa-chevron-up" aria-hidden="true"></i>
    </button>
  </div>

  <script>window.POST_ID = {post_id};</script>
  <script src="../js/scroll-progress.js"></script>
  <script src="../js/scroll-top.js"></script>
  <script src="../js/blog-posts.js"></script>
  <script src="../js/post.js"></script>
  <script src="../js/a11y-widget.js"></script>
</body>
</html>
"""


def main() -> None:
    posts = load_posts()
    if not posts:
        print("No posts found in blog-posts.js")
        return

    OUT_DIR.mkdir(exist_ok=True)
    for path in OUT_DIR.glob("*.html"):
        path.unlink()

    for post in posts:
        out = OUT_DIR / f"{post['id']}.html"
        out.write_text(render_post(post), encoding="utf-8")

    print(f"Wrote {len(posts)} pages to {OUT_DIR}/")


if __name__ == "__main__":
    main()
