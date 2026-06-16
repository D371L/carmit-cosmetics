#!/usr/bin/env python3
"""Replace legacy base URLs and regenerate js/site-config.js from seo_config.py."""

from __future__ import annotations

from pathlib import Path

from seo_config import (
    ADDRESS_CITY,
    ADDRESS_COUNTRY,
    ADDRESS_STREET,
    BASE_URL,
    DEFAULT_OG_IMAGE,
    DEFAULT_OG_IMAGE_ALT,
    EMAIL,
    FACEBOOK_URL,
    FULL_NAME,
    LOCALE,
    MAPS_DIR_URL,
    OLD_BASE_URL,
    PHONE,
    SITE_NAME,
    TAGLINE,
    WAZE_URL,
)

ROOT = Path(__file__).resolve().parent.parent
SITE_CONFIG = ROOT / "js" / "site-config.js"
TARGETS = [
    ROOT / "index.html",
    ROOT / "blog.html",
    ROOT / "post.html",
    ROOT / "accessibility.html",
    ROOT / "privacy.html",
    ROOT / "robots.txt",
    ROOT / "js" / "post.js",
]

POST_DIR = ROOT / "post"


def generate_site_config_js() -> str:
    return f"""/**
 * Auto-generated from scripts/seo_config.py — run: python3 scripts/sync-seo.py
 */
(function () {{
  const address = {{
    street: '{ADDRESS_STREET}',
    city: '{ADDRESS_CITY}',
    country: '{ADDRESS_COUNTRY}',
  }};
  const addressQuery = encodeURIComponent(`${{address.street}}, ${{address.city}}`);

  window.SITE_CONFIG = {{
    baseUrl: '{BASE_URL}',
    siteName: '{SITE_NAME}',
    name: '{FULL_NAME}',
    description: '{TAGLINE}',
    tagline: '{TAGLINE}',
    locale: '{LOCALE}',
    phone: '{PHONE}',
    email: '{EMAIL}',
    address,
    mapsDirUrl: `https://www.google.com/maps/dir/?api=1&destination=${{addressQuery}}`,
    wazeUrl: `https://waze.com/ul?q=${{addressQuery}}&navigate=yes`,
    ogImage: '{DEFAULT_OG_IMAGE}',
    defaultOgImage: '{DEFAULT_OG_IMAGE}',
    defaultOgImageAlt: '{DEFAULT_OG_IMAGE_ALT}',
    logo: 'https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png',
    sameAs: ['{FACEBOOK_URL}'],
  }};
}})();
"""


def sync_file(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    updated = text.replace(OLD_BASE_URL, BASE_URL)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def sync_post_pages() -> int:
    count = 0
    if not POST_DIR.exists():
        return 0
    for path in POST_DIR.glob("*.html"):
        if sync_file(path):
            count += 1
    return count


def main() -> None:
    SITE_CONFIG.write_text(generate_site_config_js(), encoding="utf-8")
    print(f"Wrote {SITE_CONFIG.relative_to(ROOT)}")

    changed = 0
    for path in TARGETS:
        if sync_file(path):
            print(f"Updated {path.relative_to(ROOT)}")
            changed += 1
    post_changed = sync_post_pages()
    if post_changed:
        print(f"Updated {post_changed} post/*.html files")
    if not changed and not post_changed:
        print("All files already use the current BASE_URL.")


if __name__ == "__main__":
    main()
