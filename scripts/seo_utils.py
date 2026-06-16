"""Shared SEO helpers for blog fetch and post page generation."""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import quote

from urllib.parse import quote, unquote

from seo_config import DEFAULT_OG_IMAGE, FULL_NAME, OG_TRANSFORM, TAGLINE

VIDEO_OG_TRANSFORM = "c_fill,w_1200,h_630,q_80,f_jpg,so_0"

IMG_TRANSFORM = "f_auto,q_auto:eco,w_360,h_202,c_fill"
VIDEO_TRANSFORM = "so_0,f_jpg,q_auto:eco,w_360,h_202,c_fill"

BUSINESS_PATTERNS = [
    r"כרמית\s*אסולין\s*קוסמטיקה\s*מתקדמת\s*בקרית\s*חיים",
    r"קוסמטיקאית\s*בקרית\s*חיים",
    r"בקרית\s*חיים",
]
CTA_PATTERNS = [
    r"חייגי\s*עכשיו",
    r"צלצלי\s*ל",
    r"בואי\s*ל\s*",
    r"!\s*חייגי",
]
PHONE_RE = re.compile(r"0\d{1,2}[-\s]?\d{7}")
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "]+",
    flags=re.UNICODE,
)
SUFFIX = " — כרמית אסולין"


def _is_transform_segment(part: str) -> bool:
    return part.startswith(("t_", "e_", "l_text:")) or "," in part


def normalize_delivery_path(path: str) -> str:
    path = path.strip("/")
    path = re.sub(r"\.(png|gif|webp|mp4)$", ".jpg", path, flags=re.IGNORECASE)
    return path


def encode_cloudinary_path(path: str) -> str:
    decoded = unquote(path)
    normalized = normalize_delivery_path(decoded)
    return quote(normalized, safe="/")


def build_cloudinary_og_url(resource: str, path: str) -> str:
    if not path:
        return DEFAULT_OG_IMAGE
    transform = VIDEO_OG_TRANSFORM if resource == "video" else OG_TRANSFORM
    encoded = encode_cloudinary_path(path)
    return f"https://res.cloudinary.com/broadcust/{resource}/upload/{transform}/{encoded}"


def cloudinary_delivery_path(url: str) -> tuple[str, str]:
    if not url:
        return "", ""
    for resource in ("image", "video"):
        marker = f"/{resource}/upload/"
        if marker not in url:
            continue
        parts = url.split(marker, 1)[1].split("/")
        filename = parts[-1]
        folders = [p for p in parts[:-1] if not _is_transform_segment(p)]
        return resource, "/".join(folders + [filename])
    return "", ""


def og_image_url(image_url: str | None, video_url: str | None = None) -> str:
    if image_url:
        resource, path = cloudinary_delivery_path(image_url)
        if path:
            return build_cloudinary_og_url(resource or "image", path)

    source = video_url
    if not source:
        return DEFAULT_OG_IMAGE
    if "/video/upload/" in source:
        resource, path = cloudinary_delivery_path(source)
        if path:
            return build_cloudinary_og_url(resource or "video", path)
    if source.startswith("https://"):
        return source
    return DEFAULT_OG_IMAGE


def image_thumb(url: str) -> str:
    resource, path = cloudinary_delivery_path(url)
    if not path:
        return url
    if path.lower().endswith(".gif"):
        path = f"{path[:-4]}.jpg"
    bucket = resource or "image"
    return f"https://res.cloudinary.com/broadcust/{bucket}/upload/{IMG_TRANSFORM}/{path}"


def video_thumb(video_url: str) -> str:
    _, path = cloudinary_delivery_path(video_url)
    if not path:
        return ""
    return (
        f"https://res.cloudinary.com/broadcust/video/upload/{VIDEO_TRANSFORM}/"
        f"{path.replace('.mp4', '.jpg')}"
    )


def clean_raw_title(title: str) -> str:
    text = EMOJI_RE.sub("", title or "")
    text = re.sub(r"^[\s🎬\-–—]+", "", text)
    text = re.sub(r"^סרטון\s*[-–—]?\s*", "", text)
    text = PHONE_RE.sub("", text)
    for pattern in CTA_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    for pattern in BUSINESS_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .!-,—")
    return text


def build_seo_title(title: str) -> str:
    core = clean_raw_title(title)
    core = re.sub(r"\s*עם\s+(התשובה|ההסבר|המידע|הטיפים).*$", "", core).strip()
    if not core:
        core = "פרסום מקצועי"
    if "?" in core:
        first_sentence = core.split("?", 1)[0] + "?"
        if len(first_sentence) + len(SUFFIX) <= 72:
            core = first_sentence
    max_core = max(20, 60 - len(SUFFIX))
    if len(core) > max_core:
        cut = core[:max_core].rsplit(" ", 1)[0] or core[:max_core]
        core = cut.rstrip(".,!?-")
    return f"{core}{SUFFIX}"


def build_description(title: str) -> str:
    core = clean_raw_title(title)
    core = re.sub(r"\s*עם\s+(התשובה|ההסבר|המידע|הטיפים).*$", "", core).strip()
    if not core:
        return f"{TAGLINE} — {FULL_NAME}."
    desc = f"{core} — {FULL_NAME}."
    if len(desc) > 155:
        desc = desc[:152].rsplit(" ", 1)[0] + "…"
    return desc


def parse_date_published(date_str: str) -> str:
    if not date_str:
        return ""
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        except ValueError:
            continue
    return ""


def parse_date_iso_date(date_str: str) -> str:
    published = parse_date_published(date_str)
    if published:
        return published[:10]
    return ""
