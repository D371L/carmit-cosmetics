/**
 * Site-wide constants for SEO, canonical URLs, and structured data.
 * Update SITE_BASE_URL when deploying (GitHub Pages or custom domain).
 */
(function () {
  const address = {
    street: 'הראשונים 39',
    city: 'קרית חיים',
    country: 'IL',
  };
  const addressQuery = encodeURIComponent(`${address.street}, ${address.city}`);

  window.SITE_CONFIG = {
    baseUrl: 'https://YOUR_GITHUB_USERNAME.github.io/carmit-cosmetics',
    name: 'כרמית אסולין קוסמטיקה מתקדמת בקרית חיים',
    description: 'היופי שלך בידים טובות | קוסמטיקאית בקרית חיים',
    locale: 'he_IL',
    phone: '+972524677347',
    email: 'carmit150@gmail.com',
    address,
    mapsDirUrl: `https://www.google.com/maps/dir/?api=1&destination=${addressQuery}`,
    wazeUrl: `https://waze.com/ul?q=${addressQuery}&navigate=yes`,
    ogImage:
      'https://res.cloudinary.com/broadcust/image/upload/c_fill,w_1200,h_630,q_auto,f_jpg/v1704278440/production/users/12148/gallery/1d560099-f6e1-47af-8f84-68ba72f35c48__184914.png',
    logo: 'https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png',
    sameAs: ['https://www.facebook.com/101576059040639'],
  };
})();
