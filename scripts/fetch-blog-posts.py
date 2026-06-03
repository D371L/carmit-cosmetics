#!/usr/bin/env python3
"""Fetch blog posts from Broadcust API and write js/blog-posts.js."""

import json
import re
import urllib.request

API = (
    'https://broadcust.co.il/api/business/campaigns'
    '?uid=12148&types=10,40,50,60,70,75,80,110,120,130&from=0&count=50'
)
OUT = 'js/blog-posts.js'


def clean_title(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').strip())


IMG_TRANSFORM = 'f_auto,q_auto:eco,w_360,h_202,c_fill'
VIDEO_TRANSFORM = 'so_0,f_jpg,q_auto:eco,w_360,h_202,c_fill'


def _is_transform_segment(part: str) -> bool:
    return part.startswith(('t_', 'e_', 'l_text:')) or ',' in part


def cloudinary_delivery_path(url: str) -> tuple[str, str]:
    """Return (resource_type, public_id_path) without overlay/transform segments."""
    if not url:
        return '', ''
    for resource in ('image', 'video'):
        marker = f'/{resource}/upload/'
        if marker not in url:
            continue
        parts = url.split(marker, 1)[1].split('/')
        filename = parts[-1]
        folders = [p for p in parts[:-1] if not _is_transform_segment(p)]
        return resource, '/'.join(folders + [filename])
    return '', ''


def image_thumb(url: str) -> str:
    resource, path = cloudinary_delivery_path(url)
    if not path:
        return url
    if path.lower().endswith('.gif'):
        path = f'{path[:-4]}.jpg'
    bucket = resource or 'image'
    return f'https://res.cloudinary.com/broadcust/{bucket}/upload/{IMG_TRANSFORM}/{path}'


def video_thumb(video_url: str) -> str:
    """First video frame — no Broadcust text, logo, or credit overlays."""
    _, path = cloudinary_delivery_path(video_url)
    if not path:
        return ''
    return (
        f'https://res.cloudinary.com/broadcust/video/upload/{VIDEO_TRANSFORM}/'
        f'{path.replace(".mp4", ".jpg")}'
    )


def main() -> None:
    with urllib.request.urlopen(API, timeout=30) as resp:
        campaigns = json.load(resp)['campaigns']

    seen: set[str] = set()
    posts = []
    for c in sorted(campaigns, key=lambda x: x.get('send_timestamp', 0), reverse=True):
        pic = c.get('picture') or ''
        if not pic:
            continue
        title = clean_title(c.get('subject'))
        if not title or title in seen:
            continue
        seen.add(title)
        ct = c.get('content_type')
        vu = c.get('video_url') or ''
        is_video = ct == 3
        if is_video and vu:
            thumb = video_thumb(vu)
        else:
            thumb = image_thumb(pic)
        post = {
            'id': c['id'],
            'title': title,
            'date': c.get('send_time', ''),
            'image': thumb,
            'type': 'video' if is_video else 'article',
        }
        if is_video and '.mp4' in vu:
            post['video'] = vu
        posts.append(post)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('/* Auto-generated from Broadcust API — business uid 12148 */\n')
        f.write('window.BLOG_POSTS = ')
        json.dump(posts, f, ensure_ascii=False, indent=2)
        f.write(';\n')

    print(f'Wrote {len(posts)} posts to {OUT}')


if __name__ == '__main__':
    main()
