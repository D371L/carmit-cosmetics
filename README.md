# Carmit Cosmetics

Website for **Carmit Assulin Advanced Cosmetics** — a beauty clinic in Kiryat Haim, Israel.

Mobile-first, RTL Hebrew layout with a centered 500px column. Pure HTML, CSS, and vanilla JavaScript — no build step, no framework.

---

## Features

- **Homepage** — hero, services, customer club signup, reviews, appointment CTA, gallery, contact
- **Blog** — listing page and individual post pages with dynamic meta tags
- **Gallery** — image carousel and lightbox with video support
- **Customer club** — modal form that opens WhatsApp with a pre-filled message
- **Contact** — one-tap Google Maps and Waze navigation
- **Accessibility menu** (תפריט נגישות) — floating widget with contrast, text size, dyslexia font, motion reduction, page outline, and more; settings persist in `localStorage`
- **SEO** — Open Graph, Twitter Cards, JSON-LD `BeautySalon` schema, `robots.txt`, and `sitemap.xml`

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
post.html               Single blog post
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
  blog-posts.js         Blog post data
  blog.js               Blog listing renderer
  post.js               Single post loader + dynamic meta
  scroll-progress.js    Top scroll progress bar
  scroll-top.js         Back-to-top button
  a11y-widget.js        Accessibility menu logic

scripts/
  fetch-blog-posts.py   Refresh blog data
  generate-sitemap.py   Regenerate sitemap.xml

.github/workflows/
  deploy-pages.yml      GitHub Pages deployment
```

---

## Deployment (GitHub Pages)

The site deploys as-is — upload the repo root, no build pipeline.

1. Push the code to the `main` branch on GitHub.
2. Go to **Settings → Pages → Build and deployment** and set the source to **GitHub Actions**.
3. Push to `main` — the workflow in `.github/workflows/deploy-pages.yml` deploys automatically.
4. Replace the placeholder base URL across the project:
   - Search for `YOUR_GITHUB_USERNAME.github.io/carmit-cosmetics`
   - Update `js/site-config.js`, HTML meta/canonical tags, `robots.txt`, `js/post.js`, and `scripts/generate-sitemap.py`
5. Regenerate the sitemap and commit:
   ```bash
   python3 scripts/generate-sitemap.py
   ```
6. **Custom domain (optional):** add a `CNAME` file at the repo root, configure it under Pages → Custom domain, and update the base URL everywhere.

---

## Updating content

| What | Where / how |
|------|-------------|
| Clinic address, phone, social links | `js/site-config.js` |
| Gallery images and alt text | `js/gallery-data.js` |
| Blog posts | `python3 scripts/fetch-blog-posts.py`, then regenerate sitemap |
| Instagram link | `index.html` |
| Media assets | Hosted on Cloudinary CDN |

---

## Configuration

All site-wide constants live in `js/site-config.js`:

```js
window.SITE_CONFIG = {
  baseUrl: 'https://your-domain.com',
  phone: '+972524677347',
  email: 'carmit150@gmail.com',
  address: { street: 'הראשונים 39', city: 'קרית חיים', country: 'IL' },
  // mapsDirUrl and wazeUrl are derived from address
};
```

Google Maps and Waze links are generated automatically from the address.

---

## Notes

- **Google Reviews** — no API integration; the reviews section links out to Google.
- **Blog post previews in messengers** — meta tags update via JavaScript on `post.html`. For perfect previews in every app, consider static meta tags or pre-rendering for popular posts.

---

## Credits

Developed by [HellSec](https://hellsec.dev/).
