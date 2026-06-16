"""Render social meta tags and icon links for static pages."""

from __future__ import annotations

import html

from seo_config import (
    APPLE_TOUCH_ICON,
    FAVICON,
    LOCALE,
    SITE_NAME,
    THEME_COLOR,
)


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def render_icon_links() -> str:
    return f"""  <meta name="theme-color" content="{THEME_COLOR}">
  <link rel="icon" href="{esc(FAVICON)}" type="image/png">
  <link rel="apple-touch-icon" href="{esc(APPLE_TOUCH_ICON)}">"""


def render_social_meta(
    *,
    title: str,
    description: str,
    url: str,
    og_image: str,
    og_image_alt: str,
    og_type: str = "website",
    article_published_time: str | None = None,
    article_author: str | None = None,
) -> str:
    article_lines = ""
    if article_published_time:
        article_lines += (
            f'  <meta property="article:published_time" '
            f'content="{esc(article_published_time)}">\n'
        )
    if article_author:
        article_lines += (
            f'  <meta property="article:author" content="{esc(article_author)}">\n'
        )

    return f"""  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(url)}">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:type" content="{esc(og_type)}">
  <meta property="og:locale" content="{LOCALE}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta property="og:image:secure_url" content="{esc(og_image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{esc(og_image_alt)}">
  <meta property="og:image:type" content="image/jpeg">
{article_lines}  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image)}">
  <meta name="twitter:image:alt" content="{esc(og_image_alt)}">
  <title>{esc(title)}</title>"""
