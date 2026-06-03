(function () {
  'use strict';

  const params = new URLSearchParams(window.location.search);
  const legacyId = params.get('id');
  if (legacyId && /\/post\.html$/i.test(window.location.pathname)) {
    window.location.replace(`post/${legacyId}.html`);
    return;
  }

  function resolvePostId() {
    if (window.POST_ID) return String(window.POST_ID);
    const fromPath = window.location.pathname.match(/\/post\/(\d+)\.html$/);
    if (fromPath) return fromPath[1];
    return params.get('id');
  }

  const id = resolvePostId();
  const posts = window.BLOG_POSTS || [];
  const meta = posts.find((p) => String(p.id) === String(id));
  const isStaticPostPage = /\/post\/\d+\.html$/i.test(window.location.pathname);

  const titleEl = document.getElementById('postTitle');
  const dateEl = document.getElementById('postDate');
  const bodyEl = document.getElementById('postBody');
  const loadingEl = document.getElementById('postLoading');
  const errorEl = document.getElementById('postError');

  const cfg = window.SITE_CONFIG || {};
  const SITE_BASE = (cfg.baseUrl || 'https://d371l.github.io/carmit-cosmetics').replace(/\/$/, '');

  function ogImageUrl(imageUrl, videoUrl) {
    if (meta && meta.ogImage) return meta.ogImage;
    const source = imageUrl || videoUrl;
    if (!source) return cfg.defaultOgImage || cfg.ogImage || '';
    if (source.includes('/video/upload/')) {
      const path = cloudinaryDeliveryPath(source);
      if (path) {
        return `https://res.cloudinary.com/broadcust/video/upload/c_fill,w_1200,h_630,q_auto,f_jpg,so_0/${path.replace(/\.mp4$/i, '.jpg')}`;
      }
    }
    if (source.includes('/image/upload/')) {
      const marker = '/image/upload/';
      const idx = source.indexOf(marker);
      const rest = source.slice(idx + marker.length);
      const parts = rest.split('/');
      const filename = parts[parts.length - 1];
      const folders = parts.slice(0, -1).filter((p) => !isTransformSegment(p));
      return `https://res.cloudinary.com/broadcust/image/upload/c_fill,w_1200,h_630,q_auto,f_jpg/${[...folders, filename].join('/')}`;
    }
    return source;
  }

  function updatePageMeta(post) {
    if (isStaticPostPage) return;

    const title = post.seoTitle || `${post.title} — כרמית אסולין קוסמטיקה`;
    const desc = post.description || post.title.slice(0, 160);
    const url = `${SITE_BASE}/post/${post.id}.html`;
    const image = ogImageUrl(post.image, post.video);

    document.title = title;
    const set = (id, attr, value) => {
      const el = document.getElementById(id);
      if (el) el.setAttribute(attr, value);
    };
    const titleElMeta = document.getElementById('pageTitle');
    if (titleElMeta) titleElMeta.textContent = title;
    set('canonicalLink', 'href', url);
    set('ogTitle', 'content', title);
    set('ogDescription', 'content', desc);
    set('ogUrl', 'content', url);
    set('ogImage', 'content', image);
    set('ogImageSecure', 'content', image);
    set('ogImageAlt', 'content', title);
    set('twitterTitle', 'content', title);
    set('twitterDescription', 'content', desc);
    set('twitterImage', 'content', image);
    const descMeta = document.querySelector('meta[name="description"]');
    if (descMeta) descMeta.setAttribute('content', desc);
  }

  function isTransformSegment(part) {
    return part.startsWith('t_') || part.startsWith('e_') || part.startsWith('l_text:') || part.includes(',');
  }

  function cloudinaryDeliveryPath(url) {
    if (!url) return '';
    for (const resource of ['image', 'video']) {
      const marker = `/${resource}/upload/`;
      const idx = url.indexOf(marker);
      if (idx === -1) continue;
      const parts = url.slice(idx + marker.length).split('/');
      const filename = parts[parts.length - 1];
      const folders = parts.slice(0, -1).filter((p) => !isTransformSegment(p));
      return [...folders, filename].join('/');
    }
    return '';
  }

  function videoThumbUrl(videoUrl) {
    const path = cloudinaryDeliveryPath(videoUrl);
    if (!path) return '';
    return `https://res.cloudinary.com/broadcust/video/upload/so_0,f_jpg,q_auto:eco,w_360,h_202,c_fill/${path.replace(/\.mp4$/i, '.jpg')}`;
  }

  function showError(msg) {
    if (loadingEl) loadingEl.hidden = true;
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.hidden = false;
    }
  }

  function renderVideo(post) {
    if (loadingEl) loadingEl.hidden = true;
    if (titleEl) titleEl.textContent = post.title;
    if (dateEl) {
      dateEl.textContent = post.date
        ? `פורסם בתאריך: ${post.date.split(' ')[0]} ${(post.date.split(' ')[1] || '').slice(0, 5)}`
        : '';
    }
    if (!bodyEl) return;
    bodyEl.innerHTML = `
      <div class="post-video-wrap">
        <video controls playsinline preload="metadata" poster="${(videoThumbUrl(post.video) || post.image).replace(/"/g, '&quot;')}">
          <source src="${post.video.replace(/"/g, '&quot;')}" type="video/mp4">
        </video>
      </div>`;
  }

  async function loadArticle(post) {
    try {
      const res = await fetch(`https://broadcust.co.il/api/deal/get/${post.id}`);
      if (!res.ok) throw new Error('load failed');
      const data = await res.json();
      if (loadingEl) loadingEl.hidden = true;
      if (titleEl) titleEl.textContent = (data.subject || post.title).trim();
      if (dateEl) {
        const d = data.send_time || post.date;
        dateEl.textContent = d ? `פורסם בתאריך: ${d}` : '';
      }
      if (bodyEl && data.html) {
        bodyEl.innerHTML = data.html;
      } else {
        showError('לא נמצא תוכן לפרסום זה.');
      }
    } catch {
      showError('לא ניתן לטעון את הפרסום. נסו שוב מאוחר יותר.');
    }
  }

  if (!id || !meta) {
    showError('פרסום לא נמצא.');
  } else {
    updatePageMeta(meta);
    if (meta.type === 'video' && meta.video) {
      renderVideo(meta);
    } else {
      if (titleEl) titleEl.textContent = meta.title;
      loadArticle(meta);
    }
  }
})();
