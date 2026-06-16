"""Single source of truth for SEO constants — synced to js/site-config.js via sync-seo.py."""

BASE_URL = "https://carmitcosmetics.co.il"
SITE_NAME = "כרמית אסולין קוסמטיקה מתקדמת"
FULL_NAME = "כרמית אסולין קוסמטיקה מתקדמת בקרית חיים"
TAGLINE = "היופי שלך בידים טובות | קוסמטיקאית בקרית חיים"
LOCALE = "he_IL"
OLD_BASE_URL = "https://d371l.github.io/carmit-cosmetics"
THEME_COLOR = "#C5A880"

PHONE = "+972524677347"
EMAIL = "carmit150@gmail.com"
ADDRESS_STREET = "הראשונים 39"
ADDRESS_CITY = "קרית חיים"
ADDRESS_COUNTRY = "IL"
FACEBOOK_URL = "https://www.facebook.com/101576059040639"

GEO_LAT = 32.8203
GEO_LNG = 35.0703

LOGO_PATH = (
    "v1706174206/production/users/12148/logo/"
    "d0efa39d-d056-4105-9285-88e6eddfcca1.png"
)
HERO_PATH = (
    "v1704278440/production/users/12148/gallery/"
    "1d560099-f6e1-47af-8f84-68ba72f35c48__184914.png"
)

OG_TRANSFORM = "c_fill,w_1200,h_630,q_80,f_jpg"

DEFAULT_OG_IMAGE = (
    f"https://res.cloudinary.com/broadcust/image/upload/{OG_TRANSFORM}/{HERO_PATH}"
)
DEFAULT_OG_IMAGE_ALT = f"{FULL_NAME} — טיפולי פנים וקוסמטיקה"

LOGO_OG_IMAGE = (
    "https://res.cloudinary.com/broadcust/image/upload/"
    "c_fit,w_1200,h_630,q_80,f_jpg,b_rgb:FAF6F0/"
    + LOGO_PATH
)
LOGO_OG_IMAGE_ALT = f"לוגו — {SITE_NAME}"

FAVICON = f"https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/{LOGO_PATH}"
APPLE_TOUCH_ICON = (
    f"https://res.cloudinary.com/broadcust/image/upload/"
    f"c_fill,w_180,h_180,q_80,f_jpg/{LOGO_PATH}"
)
LOGO = FAVICON

MAPS_DIR_URL = (
    "https://www.google.com/maps/dir/?api=1&destination="
    + "הראשונים%2039%2C%20קרית%20חיים"
)
WAZE_URL = "https://waze.com/ul?q=הראשונים%2039%2C%20קרית%20חיים&navigate=yes"

# Static page meta (blog og:image resolved at generation time from latest post)
PAGE_META: dict[str, dict[str, str]] = {
    "index.html": {
        "title": FULL_NAME,
        "description": f"{FULL_NAME} — {TAGLINE}",
        "og_title": FULL_NAME,
        "og_description": TAGLINE,
        "path": "/",
        "og_type": "website",
        "og_image": DEFAULT_OG_IMAGE,
        "og_image_alt": DEFAULT_OG_IMAGE_ALT,
    },
    "blog.html": {
        "title": f"בלוג ופרסומים — {SITE_NAME}",
        "description": f"בלוג ופרסומים מקצועיים — {FULL_NAME}",
        "og_title": f"בלוג ופרסומים — {SITE_NAME}",
        "og_description": "טיפים, מאמרים וסרטונים מקצועיים בקוסמטיקה מתקדמת",
        "path": "/blog.html",
        "og_type": "website",
        "og_image": "",  # filled from latest post
        "og_image_alt": f"בלוג ופרסומים — {FULL_NAME}",
    },
    "privacy.html": {
        "title": f"מדיניות פרטיות — {SITE_NAME}",
        "description": f"מדיניות הגנת פרטיות — {FULL_NAME}",
        "og_title": f"מדיניות פרטיות — {SITE_NAME}",
        "og_description": "מדיניות הגנת פרטיות לאתר כרמית אסולין קוסמטיקה מתקדמת",
        "path": "/privacy.html",
        "og_type": "website",
        "og_image": LOGO_OG_IMAGE,
        "og_image_alt": LOGO_OG_IMAGE_ALT,
    },
    "accessibility.html": {
        "title": f"הצהרת נגישות — {SITE_NAME}",
        "description": f"הצהרת נגישות — {FULL_NAME}",
        "og_title": f"הצהרת נגישות — {SITE_NAME}",
        "og_description": "הצהרת נגישות לאתר כרמית אסולין קוסמטיקה מתקדמת",
        "path": "/accessibility.html",
        "og_type": "website",
        "og_image": LOGO_OG_IMAGE,
        "og_image_alt": LOGO_OG_IMAGE_ALT,
    },
}
