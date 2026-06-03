(function () {
  'use strict';

  const STORAGE_KEY = 'carmit-a11y-v1';

  const FEATURES = [
    { id: 'highContrast', class: 'a11y-high-contrast', label: '+ ניגודיות', icon: 'fa-adjust' },
    { id: 'smartContrast', class: 'a11y-smart-contrast', label: 'ניגודיות חכמה', icon: 'fa-circle-half-stroke' },
    { id: 'largeText', class: 'a11y-large-text', label: 'טקסט גדול', icon: 'fa-text-height' },
    { id: 'highlightLinks', class: 'a11y-highlight-links', label: 'הדגשת קישורים', icon: 'fa-link' },
    { id: 'stopAnimations', class: 'a11y-stop-animations', label: 'ביטול הנפשות', icon: 'fa-pause-circle' },
    { id: 'textSpacing', class: 'a11y-text-spacing', label: 'ריווח טקסט', icon: 'fa-arrows-left-right' },
    { id: 'dyslexia', class: 'a11y-dyslexia', label: 'תמיכה בדיסלקסיה', icon: 'fa-font' },
    { id: 'hideImages', class: 'a11y-hide-images', label: 'הסתרת תמונות', icon: 'fa-image' },
    { id: 'lineHeight', class: 'a11y-line-height', label: 'גובה שורה', icon: 'fa-align-justify' },
    { id: 'pageStructure', class: 'a11y-page-structure', label: 'מבנה הדף', icon: 'fa-sitemap' },
  ];

  const PROFILES = {
    blind: ['largeText', 'highlightLinks', 'pageStructure'],
    colorBlind: ['highContrast'],
    dyslexia: ['dyslexia', 'textSpacing', 'lineHeight'],
    seizure: ['stopAnimations', 'hideImages'],
  };

  const PROFILE_LABELS = {
    blind: { label: 'עיוור', icon: 'fa-assistive-listening-systems' },
    colorBlind: { label: 'עיוור צבעים', icon: 'fa-droplet' },
    dyslexia: { label: 'דיסלקציה', icon: 'fa-font' },
    seizure: { label: 'התקף ואפילפסיה', icon: 'fa-brain' },
  };

  const active = new Set();
  let fabBtn = null;
  let panel = null;
  let structureEl = null;
  let lastFocus = null;

  function featureById(id) {
    return FEATURES.find((f) => f.id === id);
  }

  function applyClasses() {
    const root = document.documentElement;
    FEATURES.forEach((f) => root.classList.remove(f.class));
    active.forEach((id) => {
      const f = featureById(id);
      if (f) root.classList.add(f.class);
    });
    syncToggleButtons();
    if (active.has('pageStructure')) buildPageStructure();
    else removePageStructure();
    if (active.has('hideImages')) hideMediaAria(true);
    else hideMediaAria(false);
  }

  function hideMediaAria(hide) {
    document.querySelectorAll('img, video').forEach((el) => {
      if (hide) el.setAttribute('aria-hidden', 'true');
      else el.removeAttribute('aria-hidden');
    });
  }

  function syncToggleButtons() {
    if (!panel) return;
    panel.querySelectorAll('[data-feature]').forEach((btn) => {
      const on = active.has(btn.dataset.feature);
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function toggleFeature(id) {
    if (active.has(id)) active.delete(id);
    else active.add(id);
    applyClasses();
    persist();
  }

  function applyProfile(name) {
    const ids = PROFILES[name];
    if (!ids) return;
    ids.forEach((id) => active.add(id));
    applyClasses();
    persist();
  }

  function resetAll() {
    active.clear();
    applyClasses();
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) { /* ignore */ }
  }

  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...active]));
    } catch (_) { /* ignore */ }
  }

  function restore() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const list = JSON.parse(raw);
      if (!Array.isArray(list)) return;
      list.forEach((id) => {
        if (featureById(id)) active.add(id);
      });
      applyClasses();
    } catch (_) { /* ignore */ }
  }

  function buildPageStructure() {
    if (structureEl) {
      fillStructureList();
      return;
    }
    structureEl = document.createElement('aside');
    structureEl.className = 'a11y-structure';
    structureEl.setAttribute('aria-label', 'מבנה הדף');
    structureEl.innerHTML = `
      <button type="button" class="a11y-structure__close" aria-label="סגור מבנה דף">&times;</button>
      <h2 class="a11y-structure__title">מבנה הדף</h2>
      <ul class="a11y-structure__list"></ul>`;
    document.body.appendChild(structureEl);
    structureEl.querySelector('.a11y-structure__close').addEventListener('click', () => {
      active.delete('pageStructure');
      applyClasses();
      persist();
    });
    fillStructureList();
  }

  function fillStructureList() {
    if (!structureEl) return;
    const list = structureEl.querySelector('.a11y-structure__list');
    const headings = document.querySelectorAll('h1, h2, h3');
    if (!headings.length) {
      list.innerHTML = '<li>לא נמצאו כותרות בדף זה</li>';
      return;
    }
    list.innerHTML = '';
    headings.forEach((h, i) => {
      if (!h.id) h.id = `a11y-heading-${i}`;
      const level = parseInt(h.tagName.charAt(1), 10);
      const li = document.createElement('li');
      li.className = `level-${level}`;
      const a = document.createElement('a');
      a.href = `#${h.id}`;
      a.textContent = h.textContent.trim().slice(0, 80) || h.tagName;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        h.focus({ preventScroll: true });
      });
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  function removePageStructure() {
    if (structureEl) {
      structureEl.remove();
      structureEl = null;
    }
  }

  function adjustFabPosition() {
    if (!fabBtn) return;
    const hasWhatsApp = document.querySelector('.fab-whatsapp');
    fabBtn.classList.toggle('fab-a11y--solo', !hasWhatsApp);
  }

  function createFab() {
    fabBtn = document.createElement('button');
    fabBtn.type = 'button';
    fabBtn.className = 'fab-a11y';
    fabBtn.setAttribute('aria-label', 'פתח תפריט נגישות');
    fabBtn.innerHTML = '<i class="fas fa-universal-access" aria-hidden="true"></i>';
    fabBtn.addEventListener('click', openPanel);
    document.body.appendChild(fabBtn);
    adjustFabPosition();
  }

  function createPanel() {
    const featureButtons = FEATURES.map(
      (f) => `
      <button type="button" class="a11y-feature" data-feature="${f.id}" aria-pressed="false">
        <i class="fas ${f.icon}" aria-hidden="true"></i>
        <span>${f.label}</span>
      </button>`
    ).join('');

    const profileButtons = Object.entries(PROFILE_LABELS)
      .map(
        ([key, p]) => `
      <button type="button" class="a11y-profile-btn" data-profile="${key}">
        <i class="fas ${p.icon}" aria-hidden="true"></i>
        <span>${p.label}</span>
      </button>`
      )
      .join('');

    panel = document.createElement('div');
    panel.className = 'a11y-panel';
    panel.hidden = true;
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.setAttribute('aria-labelledby', 'a11yPanelTitle');

    panel.innerHTML = `
      <div class="a11y-panel__dialog">
        <div class="a11y-panel__header">
          <h2 class="a11y-panel__title" id="a11yPanelTitle">תפריט נגישות</h2>
          <button type="button" class="a11y-panel__close" aria-label="סגור">&times;</button>
        </div>
        <div class="a11y-panel__body">
          <div class="a11y-lang">
            <span class="a11y-lang__badge">HE</span>
            <span>עברית (Hebrew)</span>
          </div>
          <div class="a11y-profiles">
            <button type="button" class="a11y-profiles__toggle" aria-expanded="false">
              <span><i class="fas fa-universal-access" aria-hidden="true"></i> פרופילי נגישות</span>
              <i class="fas fa-chevron-left a11y-profiles__chevron" aria-hidden="true"></i>
            </button>
            <div class="a11y-profiles__list">${profileButtons}</div>
          </div>
          <div class="a11y-grid">${featureButtons}</div>
          <div class="a11y-panel__footer">
            <button type="button" class="a11y-reset">איפוס הגדרות</button>
            <a href="accessibility.html" class="a11y-statement-link">הצהרת נגישות</a>
          </div>
        </div>
      </div>`;

    document.body.appendChild(panel);

    panel.querySelector('.a11y-panel__close').addEventListener('click', closePanel);
    panel.querySelector('.a11y-reset').addEventListener('click', () => {
      resetAll();
      syncToggleButtons();
    });

    panel.querySelector('.a11y-profiles__toggle').addEventListener('click', function () {
      const wrap = panel.querySelector('.a11y-profiles');
      const open = wrap.classList.toggle('is-open');
      this.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    panel.querySelectorAll('[data-feature]').forEach((btn) => {
      btn.addEventListener('click', () => toggleFeature(btn.dataset.feature));
    });

    panel.querySelectorAll('[data-profile]').forEach((btn) => {
      btn.addEventListener('click', () => applyProfile(btn.dataset.profile));
    });

    panel.addEventListener('click', (e) => {
      if (e.target === panel) closePanel();
    });

    panel.addEventListener('keydown', trapFocus);
  }

  function openPanel() {
    if (!panel) return;
    lastFocus = document.activeElement;
    panel.hidden = false;
    document.body.style.overflow = 'hidden';
    panel.querySelector('.a11y-panel__close').focus();
  }

  function closePanel() {
    if (!panel) return;
    panel.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function trapFocus(e) {
    if (e.key === 'Escape') {
      closePanel();
      return;
    }
    if (e.key !== 'Tab' || panel.hidden) return;
    const focusable = panel.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const list = [...focusable].filter((el) => !el.disabled && el.offsetParent !== null);
    if (!list.length) return;
    const first = list[0];
    const last = list[list.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function init() {
    createFab();
    createPanel();
    restore();
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel && !panel.hidden) closePanel();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
