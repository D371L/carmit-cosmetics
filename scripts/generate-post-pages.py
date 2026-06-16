#!/usr/bin/env python3
"""Generate static post/{id}.html pages with server-rendered Open Graph meta."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seo_config import BASE_URL, DEFAULT_OG_IMAGE, FULL_NAME, LOGO  # noqa: E402
from seo_head import render_icon_links, render_social_meta  # noqa: E402

BLOG_POSTS = ROOT.parent / "js" / "blog-posts.js"
OUT_DIR = ROOT.parent / "post"


def load_posts() -> list[dict]:
    text = BLOG_POSTS.read_text(encoding="utf-8")
    match = re.search(r"window\.BLOG_POSTS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(1))


def blog_posting_json_ld(post: dict, page_url: str, og_image: str, seo_title: str) -> dict:
    payload: dict = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": seo_title,
        "description": post.get("description", ""),
        "image": {
            "@type": "ImageObject",
            "url": og_image,
            "width": 1200,
            "height": 630,
            "caption": seo_title,
        },
        "url": page_url,
        "mainEntityOfPage": page_url,
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
        payload["dateModified"] = post["datePublished"]
    return payload


def breadcrumb_json_ld(post: dict, page_url: str, seo_title: str) -> dict:
    base = BASE_URL.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "דף הבית",
                "item": f"{base}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "בלוג",
                "item": f"{base}/blog.html",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": seo_title,
                "item": page_url,
            },
        ],
    }


def video_json_ld(post: dict, page_url: str, og_image: str, seo_title: str) -> dict | None:
    video_url = post.get("video")
    if not video_url or post.get("type") != "video":
        return None
    payload: dict = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": seo_title,
        "description": post.get("description", ""),
        "thumbnailUrl": og_image,
        "contentUrl": video_url,
        "uploadDate": post.get("datePublished", ""),
        "url": page_url,
    }
    return payload


def render_post(post: dict) -> str:
    post_id = post["id"]
    seo_title = post.get("seoTitle") or post.get("title", "פרסום")
    description = post.get("description") or seo_title
    og_image = post.get("ogImage") or DEFAULT_OG_IMAGE
    page_url = f"{BASE_URL.rstrip('/')}/post/{post_id}.html"

    social = render_social_meta(
        title=seo_title,
        description=description,
        url=page_url,
        og_image=og_image,
        og_image_alt=seo_title,
        og_type="article",
        article_published_time=post.get("datePublished") or None,
        article_author="כרמית אסולין",
    )

    ld_scripts = []
    ld_scripts.append(blog_posting_json_ld(post, page_url, og_image, seo_title))
    ld_scripts.append(breadcrumb_json_ld(post, page_url, seo_title))
    video_ld = video_json_ld(post, page_url, og_image, seo_title)
    if video_ld:
        ld_scripts.append(video_ld)

    json_ld_html = ""
    for block in ld_scripts:
        json_ld_html += (
            f'  <script type="application/ld+json">\n'
            f"{json.dumps(block, ensure_ascii=False, indent=2)}\n"
            f"  </script>\n"
        )

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{social}
{render_icon_links()}
{json_ld_html}  <link rel="preconnect" href="https://fonts.googleapis.com">
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
  <script src="../js/site-config.js"></script>
  <script src="../js/scroll-progress.js"></script>
  <script src="../js/scroll-top.js"></script>
  <script src="../js/blog-posts.js"></script>
  <script src="../js/blog-content.js"></script>
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
