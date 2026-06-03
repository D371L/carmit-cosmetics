/**
 * Site-wide constants for SEO, canonical URLs, and structured data.
 * Update baseUrl when deploying to a custom domain, then run: python3 scripts/sync-seo.py
 */
(function () {
  const address = {
    street: 'הראשונים 39',
    city: 'קרית חיים',
    country: 'IL',
  };
  const addressQuery = encodeURIComponent(`${address.street}, ${address.city}`);

  window.SITE_CONFIG = {
    baseUrl: 'https://d371l.github.io/carmit-cosmetics',
    siteName: 'כרמית אסולין קוסמטיקה מתקדמת',
    name: 'כרמית אסולין קוסמטיקה מתקדמת בקרית חיים',
    description: 'היופי שלך בידים טובות | קוסמטיקאית בקרית חיים',
    tagline: 'היופי שלך בידים טובות | קוסמטיקאית בקרית חיים',
    locale: 'he_IL',
    phone: '+972524677347',
    email: 'carmit150@gmail.com',
    address,
    mapsDirUrl: `https://www.google.com/maps/dir/?api=1&destination=${addressQuery}`,
    wazeUrl: `https://waze.com/ul?q=${addressQuery}&navigate=yes`,
    ogImage:
      'https://res.cloudinary.com/broadcust/image/upload/c_fill,w_1200,h_630,q_auto,f_jpg/v1704278440/production/users/12148/gallery/1d560099-f6e1-47af-8f84-68ba72f35c48__184914.png',
    defaultOgImage:
      'https://res.cloudinary.com/broadcust/image/upload/c_fill,w_1200,h_630,q_auto,f_jpg/v1704278440/production/users/12148/gallery/1d560099-f6e1-47af-8f84-68ba72f35c48__184914.png',
    defaultOgImageAlt: 'כרמית אסולין קוסמטיקה מתקדמת בקרית חיים — טיפולי פנים וקוסמטיקה',
    logo: 'https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png',
    sameAs: ['https://www.facebook.com/101576059040639'],
  };
})();
