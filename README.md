# Carmit Cosmetics

Website for **Carmit Assulin Advanced Cosmetics** — a beauty clinic in Kiryat Haim, Israel.

Mobile-first, RTL Hebrew layout with a centered 500px column. Pure HTML, CSS, and vanilla JavaScript — no build step, no framework.

**Live site:** [d371l.github.io/carmit-cosmetics](https://d371l.github.io/carmit-cosmetics)

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
  sync-seo.py           Propagate base URL changes across HTML files
  fetch-blog-posts.py   Refresh blog data from Broadcust API
  enrich-blog-posts.py  Add SEO fields to blog-posts.js (no API)
  fetch-post-content.py Fetch article canvas (html) + body (details) into blog-content.js
  generate-post-pages.py  Build post/{id}.html with static OG tags
  generate-sitemap.py   Regenerate sitemap.xml

.github/workflows/
  deploy-pages.yml      GitHub Pages deployment
```

---

## Deployment (GitHub Pages)

1. Push the code to the `main` branch on GitHub.
2. Go to **Settings → Pages → Build and deployment** and set the source to **GitHub Actions**.
3. Push to `main` — the workflow runs `enrich-blog-posts`, `generate-post-pages`, and `generate-sitemap` before deploy.

### Changing the domain

1. Update `baseUrl` in [`js/site-config.js`](js/site-config.js) and [`scripts/seo_config.py`](scripts/seo_config.py).
2. Run:
   ```bash
   python3 scripts/sync-seo.py
   python3 scripts/generate-post-pages.py
   python3 scripts/generate-sitemap.py
   ```
3. For a custom domain, add a `CNAME` file at the repo root and configure it under Pages → Custom domain.

---

## Updating content

| What | Where / how |
|------|-------------|
| Clinic address, phone, social links | `js/site-config.js` |
| Gallery images and alt text | `js/gallery-data.js` |
| Blog posts | `fetch-blog-posts.py` → `fetch-post-content.py` → `generate-post-pages.py` → `generate-sitemap.py` |
| Instagram link | `index.html` |
| Media assets | Hosted on Cloudinary CDN |

---

## Sharing links / SEO

Messenger apps (WhatsApp, Telegram, Facebook) **do not run JavaScript**. Each blog post has a dedicated static page at `post/{id}.html` with pre-rendered Open Graph and Twitter Card meta — including a **1200×630** preview image.

**After updating blog posts:**

```bash
python3 scripts/fetch-blog-posts.py      # optional — refresh from API
python3 scripts/enrich-blog-posts.py     # add seoTitle, description, ogImage
python3 scripts/fetch-post-content.py    # download article canvas + details (19 posts)
python3 scripts/generate-post-pages.py   # rebuild post/*.html
python3 scripts/generate-sitemap.py
```

**Test previews after deploy:**

| Tool | URL |
|------|-----|
| Facebook Sharing Debugger | https://developers.facebook.com/tools/debug/ |
| WhatsApp | Send the link to yourself |
| Telegram | Send to Saved Messages |
| Local check | `curl -sL URL \| grep 'og:'` |

**Example post URL:** `https://d371l.github.io/carmit-cosmetics/post/3099653.html`

Legacy links `post.html?id=3099653` redirect in the browser to the static page.

---

## Configuration

All site-wide constants live in `js/site-config.js`:

```js
window.SITE_CONFIG = {
  baseUrl: 'https://d371l.github.io/carmit-cosmetics',
  siteName: 'כרמית אסולין קוסמטיקה מתקדמת',
  phone: '+972524677347',
  email: 'carmit150@gmail.com',
  address: { street: 'הראשונים 39', city: 'קרית חיים', country: 'IL' },
  defaultOgImage: '...', // 1200×630 hero image
};
```

Python scripts use the same values from `scripts/seo_config.py`.

---

## Notes

- **Google Reviews** — no API integration; the reviews section links out to Google.
- **Broadcust API fetch** may return 403 from some networks; use `enrich-blog-posts.py` on committed `blog-posts.js`. Article content (hero canvas + body text/images) is stored locally in `blog-content.js` — no runtime API call needed for visitors.

---

## Credits

Developed by [HellSec](https://hellsec.dev/).
