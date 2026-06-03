# כרמית אסולין — קוסמטיקה מתקדמת

סטטי HTML/CSS/JavaScript — שחזור של [האתר ב-Broadcust](https://broadcust.co.il/business/carmit-cosmetics).

## מבנה

```
index.html          — דף ראשי (3 פרסומים אחרונים)
blog.html           — כל הפרסומים + כפתור חזרה
post.html           — עמוד פרסום בודד
css/styles.css      — עיצוב mobile-first (עמודה 500px)
js/main.js          — מועדון לקוחות (modal → WhatsApp)
js/site-config.js   — קבועי SEO, כתובת, קישורי ניווט (Google Maps + Waze)
js/contact-nav.js   — מילוי קישורי ניווט מ-SITE_CONFIG
js/scroll-progress.js — פס התקדמות גלילה (index, blog, post)
js/scroll-top.js    — כפתור חזרה למעלה
css/a11y.css        — תפריט נגישות (עיצוב)
js/a11y-widget.js   — תפריט נגישות (לוגיקה, localStorage)
js/gallery-data.js  — נתוני גלריה (תמונות + סרטונים)
js/gallery.js       — קרוסלה + lightbox
js/blog-posts.js    — נתוני בלוג (מ-Broadcust)
js/blog.js          — רינדור כרטיסי בלוג
js/post.js          — טעינת פרסום בודד + meta דינמי
scripts/fetch-blog-posts.py — עדכון js/blog-posts.js
scripts/generate-sitemap.py — יצירת sitemap.xml
robots.txt / sitemap.xml    — SEO
accessibility.html  — הצהרת נגישות
privacy.html        — מדיניות פרטיות
.github/workflows/deploy-pages.yml — פריסה ל-GitHub Pages
```

## הרצה מקומית

```bash
cd /home/d371l/Projects/carmit-cosmetics
python3 -m http.server 8080
```

פתחו: http://localhost:8080

## Deploy to GitHub Pages

האתר הוא **סטטי לחלוטין** — אין שלב build. ה-workflow מעלה את שורש הריפו כפי שהוא.

1. צרו ריפו ב-GitHub והעלו את הקוד ל-branch `main`.
2. **Settings → Pages → Build and deployment:** Source = **GitHub Actions**.
3. דחפו ל-`main` — workflow `.github/workflows/deploy-pages.yml` יפרוס אוטומטית.
4. **עדכנו את כתובת הבסיס** (חיפוש/החלפה בכל הפרויקט):
   - `YOUR_GITHUB_USERNAME.github.io/carmit-cosmetics` → ה-URL האמיתי שלכם
   - קבצים: `index.html`, `blog.html`, `post.html`, `accessibility.html`, `privacy.html`, `robots.txt`, `scripts/generate-sitemap.py`, `js/post.js`, `js/site-config.js`
5. הריצו `python3 scripts/generate-sitemap.py` ו-commit ל-`sitemap.xml`.
6. **דומיין מותאם (אופציונלי):** הוסיפו `CNAME` בשורש הריפo, הגדירו ב-Pages → Custom domain, והחליפו את base URL בדומיין שלכם.

## תחזוקת תוכן

- תמונות וסרטונים נטענים מ-Cloudinary (כמו באתר המקורי).
- **בלוג:** לעדכון `python3 scripts/fetch-blog-posts.py` ואז `python3 scripts/generate-sitemap.py`.
- **גלריה:** ערכו `js/gallery-data.js` — כולל שדה `alt` לנגישות.
- **ניווט:** כתובת הקליניקה ב-`js/site-config.js` — ממנה נגזרים Google Maps ו-Waze.
- קישור אינסטגרם: עדכנו ב-`index.html` כשיש URL מדויק.

## SEO

- Open Graph + Twitter Card על כל העמודים (תמונת `og:image` 1200×630).
- JSON-LD `BeautySalon` בדף הבית.
- `robots.txt` + `sitemap.xml` (כולל כל פוסטי הבלוג).
- H1 בדף הבית כולל שם + עיר ל-SEO מקומי.

## הערות

- **Google Reviews:** אין API key / backend — בלוק הביקורות נשאר עם קישור ל-Google (ללא שליפה אוטומטית).
- **WhatsApp preview לפוסטים:** meta מתעדכן ב-JS; לתצוגה מושלמת בכל messenger מומלץ בעתיד pre-render או meta סטטי לפוסטים פופולריים.
