#!/usr/bin/env python3
"""Audit SEO meta tags and OG image reachability across static pages."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_OG = [
    "og:title",
    "og:description",
    "og:url",
    "og:type",
    "og:locale",
    "og:image",
    "og:image:secure_url",
    "og:image:width",
    "og:image:height",
    "og:image:alt",
    "og:image:type",
]
REQUIRED_TWITTER = [
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "twitter:image:alt",
]
HEBREW_IN_URL_RE = re.compile(r"[\u0590-\u05FF]")
META_RE = re.compile(
    r'<meta\s+(?:property|name)=["\']([^"\']+)["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
JSONLD_RE = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CarmitSEOAudit/1.0)"}
MAX_IMAGE_BYTES = 300 * 1024


def parse_meta(html: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for match in META_RE.finditer(html):
        meta[match.group(1)] = match.group(2)
    return meta


def audit_html_file(path: Path, check_image: bool = True) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    html = path.read_text(encoding="utf-8")
    meta = parse_meta(html)

    for key in REQUIRED_OG + REQUIRED_TWITTER:
        if key not in meta or not meta[key].strip():
            errors.append(f"{rel}: missing {key}")

    canonical = CANONICAL_RE.search(html)
    if canonical and meta.get("og:url") and canonical.group(1) != meta["og:url"]:
        errors.append(f"{rel}: canonical != og:url")

    og_image = meta.get("og:image", "")
    if og_image:
        if not og_image.startswith("https://"):
            errors.append(f"{rel}: og:image not absolute HTTPS")
        if "f_jpg" not in og_image and "f_jpg," not in og_image:
            if "/upload/" in og_image and "f_jpg" not in og_image.split("/upload/", 1)[1]:
                errors.append(f"{rel}: og:image missing f_jpg transform")
        if HEBREW_IN_URL_RE.search(og_image):
            errors.append(f"{rel}: og:image contains unencoded Hebrew")
        if check_image:
            errors.extend(check_og_image_url(rel, og_image))

    for block in JSONLD_RE.findall(html):
        try:
            json.loads(block.strip())
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON-LD — {exc}")

    return errors


def check_og_image_url(rel: Path, url: str) -> list[str]:
    errors: list[str] = []
    req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = resp.status
            ctype = resp.headers.get("Content-Type", "")
            length = int(resp.headers.get("Content-Length", "0") or 0)
    except urllib.error.HTTPError as exc:
        errors.append(f"{rel}: og:image HEAD {exc.code} — {url[:80]}…")
        return errors
    except Exception as exc:
        errors.append(f"{rel}: og:image unreachable — {exc.__class__.__name__}")
        return errors

    if status != 200:
        errors.append(f"{rel}: og:image status {status}")
    if "image" not in ctype.lower():
        errors.append(f"{rel}: og:image content-type {ctype!r}")
    if length and length > MAX_IMAGE_BYTES:
        errors.append(f"{rel}: og:image size {length // 1024}KB > 300KB")
    return errors


def collect_pages() -> list[Path]:
    pages = [
        ROOT / "index.html",
        ROOT / "blog.html",
        ROOT / "privacy.html",
        ROOT / "accessibility.html",
    ]
    post_dir = ROOT / "post"
    if post_dir.exists():
        pages.extend(sorted(post_dir.glob("*.html")))
    return pages


def main() -> None:
    check_images = "--no-images" not in sys.argv
    all_errors: list[str] = []
    pages = collect_pages()

    print(f"Auditing {len(pages)} pages…")
    for path in pages:
        all_errors.extend(audit_html_file(path, check_image=check_images))

    if all_errors:
        print(f"\n{len(all_errors)} issue(s):")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print("All SEO checks passed.")


if __name__ == "__main__":
    main()
