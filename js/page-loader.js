(function () {
  'use strict';

  var LOGO =
    'https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png';
  var MIN_MS = 450;
  var started = Date.now();

  if (document.getElementById('siteLoader')) return;

  document.documentElement.classList.add('is-loading');

  var loader = document.createElement('div');
  loader.id = 'siteLoader';
  loader.className = 'site-loader';
  loader.setAttribute('role', 'status');
  loader.setAttribute('aria-live', 'polite');
  loader.setAttribute('aria-label', 'טוען את האתר');
  loader.innerHTML =
    '<div class="site-loader__inner">' +
    '<img class="site-loader__logo" src="' +
    LOGO +
    '" alt="" width="100" height="100" decoding="async">' +
    '<div class="site-loader__ring" aria-hidden="true"></div>' +
    '</div>';

  document.body.insertBefore(loader, document.body.firstChild);

  function hideLoader() {
    if (!loader.parentNode) return;
    loader.classList.add('is-hidden');
    document.documentElement.classList.remove('is-loading');
    window.setTimeout(function () {
      if (loader.parentNode) loader.remove();
    }, 500);
  }

  function finish() {
    var wait = Math.max(0, MIN_MS - (Date.now() - started));
    window.setTimeout(hideLoader, wait);
  }

  if (document.readyState === 'complete') {
    finish();
  } else {
    window.addEventListener('load', finish);
  }
})();
