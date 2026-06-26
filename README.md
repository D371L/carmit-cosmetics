# Carmit Cosmetics

Website for **Carmit Assulin Advanced Cosmetics** — a beauty clinic in Kiryat Haim, Israel.

Mobile-first, RTL Hebrew layout with a centered 500px column. Pure HTML, CSS, and vanilla JavaScript — no build step, no framework.

**Live site:** [carmitcosmetics.co.il](https://carmitcosmetics.co.il)

---

## Features

- **Homepage** — hero, services, customer club signup, reviews, appointment CTA, gallery, contact
- **Blog** — listing page and static post pages with per-post Open Graph meta for messenger previews
- **Gallery** — image carousel and lightbox with video support
- **Customer club** — modal form that opens WhatsApp with a pre-filled message
- **Contact** — one-tap Google Maps and Waze navigation
- **Accessibility menu** (תפריט נגישות) — floating widget with contrast, text size, dyslexia font, motion reduction, page outline, and more; settings persist in `localStorage`
- **SEO** — Open Graph, Twitter Cards, JSON-LD (`BeautySalon`, `BlogPosting`), `robots.txt`, and `sitemap.xml`

---

## Quick start

```bash
git clone <repo-url>
cd carmit-cosmetics
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

Any static file server works — there is nothing to compile.

---

## Project structure

```
index.html              Homepage
blog.html               Blog listing
post.html               Legacy post URL (redirects to post/{id}.html)
post/{id}.html          Static blog posts with server-rendered OG meta
accessibility.html      Accessibility statement
privacy.html            Privacy policy

data/
  external-articles.json  External blog posts (MyNet, press, etc.)

css/
  styles.css            Main styles
  a11y.css              Accessibility widget

js/
  site-config.js        Business info, URLs, SEO constants
  main.js               Customer club modal, scroll animations
  contact-nav.js        Maps / Waze links from SITE_CONFIG
  gallery-data.js       Gallery items (images + videos)
  gallery.js            Carousel and lightbox
  blog-posts.js         Blog post data (+ seoTitle, ogImage, description)
  blog-content.js       Pre-fetched article canvas + details HTML
  blog.js               Blog listing renderer
  post.js               Single post loader
  scroll-progress.js    Top scroll progress bar
  scroll-top.js         Back-to-top button
  a11y-widget.js        Accessibility menu logic

scripts/
  seo_config.py         Single source of truth for base URL and OG defaults
  seo_utils.py          SEO title/description/image helpers
  seo_head.py           Shared OG/Twitter meta tag renderer
  sync-seo.py           Propagate base URL + regenerate js/site-config.js
  generate-site-meta.py Update SEO blocks in index/blog/privacy/accessibility
  audit-seo.py          Validate OG tags and image reachability (CI gate)
  fetch-blog-posts.py   Refresh blog data from Broadcust API
  merge-external-articles.py  Merge data/external-articles.json into blog JS
  enrich-blog-posts.py  Add SEO fields to blog-posts.js (no API)
  fetch-post-content.py Fetch article details into blog-content.js
  generate-post-pages.py  Build post/{id}.html with static OG tags
  generate-sitemap.py   Regenerate sitemap.xml

.github/workflows/
  deploy-pages.yml      GitHub Pages deployment
```

---

## Deployment (GitHub Pages)

1. Push the code to the `main` branch on GitHub.
2. Go to **Settings → Pages → Build and deployment** and set the source to **GitHub Actions** (not “Deploy from a branch”). This is required — if both `pages build and deployment` and `Deploy to GitHub Pages` run on push, the Actions deploy may fail with **409 Conflict** (“in progress deployment”).
3. Push to `main` — the workflow runs `merge-external-articles`, `enrich-blog-posts`, `generate-site-meta`, `generate-post-pages`, `generate-sitemap`, and `audit-seo.py` before deploy.

To fix a 409 deploy error, confirm Pages source is **GitHub Actions**, then re-run **Actions → Deploy to GitHub Pages → Run workflow**.

### Changing the domain

1. Update `BASE_URL` in [`scripts/seo_config.py`](scripts/seo_config.py).
2. Run:
   ```bash
   python3 scripts/sync-seo.py
   python3 scripts/generate-site-meta.py
   python3 scripts/generate-post-pages.py
   python3 scripts/generate-sitemap.py
   ```
3. For a custom domain, add a `CNAME` file at the repo root and configure it under Pages → Custom domain.

---

## Updating content

| What | Where / how |
|------|-------------|
| Clinic address, phone, social links | `scripts/seo_config.py` + `python3 scripts/sync-seo.py` |
| Gallery images and alt text | `js/gallery-data.js` |
| Blog posts (Broadcust) | `fetch-blog-posts.py` → `enrich-blog-posts.py` → `fetch-post-content.py` → `generate-post-pages.py` → `generate-sitemap.py` |
| External articles (MyNet, press) | Edit `data/external-articles.json` → `merge-external-articles.py` → same SEO pipeline as above |
| Instagram link | `index.html` |
| Media assets | Hosted on Cloudinary CDN |

---

## Sharing links / SEO

Messenger apps (WhatsApp, Telegram, Facebook) **do not run JavaScript**. Each blog post has a dedicated static page at `post/{id}.html` with pre-rendered Open Graph and Twitter Card meta — including a **1200×630** preview image.

**After updating blog posts:**

```bash
python3 scripts/merge-external-articles.py   # merge external articles from data/
python3 scripts/fetch-blog-posts.py          # optional — refresh from API (re-runs merge)
python3 scripts/enrich-blog-posts.py       # add seoTitle, description, ogImage
python3 scripts/fetch-post-content.py      # download article details (Broadcust only)
python3 scripts/sync-seo.py                # regenerate site-config.js
python3 scripts/generate-site-meta.py      # update index/blog/legal page meta
python3 scripts/generate-post-pages.py     # rebuild post/*.html
python3 scripts/generate-sitemap.py
python3 scripts/audit-seo.py               # validate all OG tags + images
```

### External articles

Press and third-party articles live in [`data/external-articles.json`](data/external-articles.json). Each entry has `id`, `title`, `sections` (body), `sourceUrl`, and optional `imageFallback` (Cloudinary clinic photo if the source cover cannot be fetched).

After editing the JSON:

```bash
python3 scripts/merge-external-articles.py
python3 scripts/enrich-blog-posts.py
python3 scripts/generate-post-pages.py
python3 scripts/generate-sitemap.py
python3 scripts/audit-seo.py
```

Posts are marked `"external": true` in `blog-posts.js` so `fetch-post-content.py` does not overwrite their body. `fetch-blog-posts.py` re-runs merge automatically after an API refresh.

**Test previews after deploy:**

| Tool | URL |
|------|-----|
| Facebook Sharing Debugger | https://developers.facebook.com/tools/debug/ |
| WhatsApp | Send the link to yourself |
| Telegram | Send to Saved Messages |
| Local check | `curl -sL URL \| grep -E 'og:\|twitter:'` |
| SEO audit | `python3 scripts/audit-seo.py` |
| Google Search Console | Add property `carmitcosmetics.co.il`, submit sitemap |

**Share canonical post URLs only:** `https://carmitcosmetics.co.il/post/{id}.html`

---

## Configuration

`js/site-config.js` is **auto-generated** from `scripts/seo_config.py` via `python3 scripts/sync-seo.py`. Edit Python constants there (base URL, OG images, contact info), then run the sync script.

---

## Notes

- **Google Reviews** — no API integration; the reviews section links out to Google.
- **Broadcust API fetch** may return 403 from some networks; use `enrich-blog-posts.py` on committed `blog-posts.js`. Article body content is stored locally in `blog-content.js` — no runtime API call needed for visitors.

---

## Credits

Developed by [HellSec](https://hellsec.dev/).
