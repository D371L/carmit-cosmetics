(function () {
  'use strict';

  const btn = document.getElementById('scrollTopBtn');
  if (!btn) return;

  const hero = document.querySelector('.hero');
  const fallbackThreshold = Number(btn.dataset.threshold) || 180;

  function getThreshold() {
    return hero ? hero.offsetHeight : fallbackThreshold;
  }

  function updateScrollTop() {
    btn.classList.toggle('is-visible', window.scrollY >= getThreshold());
  }

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  window.addEventListener('scroll', updateScrollTop, { passive: true });
  window.addEventListener('resize', updateScrollTop, { passive: true });
  updateScrollTop();
})();
