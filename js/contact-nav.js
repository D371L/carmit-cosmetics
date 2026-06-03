(function () {
  'use strict';

  const cfg = window.SITE_CONFIG;
  if (!cfg) return;

  const mapsLink = document.getElementById('mapsLink');
  const wazeLink = document.getElementById('wazeLink');

  if (mapsLink && cfg.mapsDirUrl) mapsLink.href = cfg.mapsDirUrl;
  if (wazeLink && cfg.wazeUrl) wazeLink.href = cfg.wazeUrl;
})();
