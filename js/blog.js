(function () {
  'use strict';

  const HOME_LIMIT = 3;
  const FALLBACK_IMG =
    'https://res.cloudinary.com/broadcust/image/upload/c_scale,h_200/v1706174206/production/users/12148/logo/d0efa39d-d056-4105-9285-88e6eddfcca1.png';
  const posts = window.BLOG_POSTS || [];

  function isTransformSegment(part) {
    return part.startsWith('t_') || part.startsWith('e_') || part.startsWith('l_text:') || part.includes(',');
  }

  function cloudinaryDeliveryPath(url) {
    if (!url) return { resource: '', path: '' };
    for (const resource of ['image', 'video']) {
      const marker = `/${resource}/upload/`;
      const idx = url.indexOf(marker);
      if (idx === -1) continue;
      const parts = url.slice(idx + marker.length).split('/');
      const filename = parts[parts.length - 1];
      const folders = parts.slice(0, -1).filter((p) => !isTransformSegment(p));
      return { resource, path: [...folders, filename].join('/') };
    }
    return { resource: '', path: '' };
  }

  function videoThumbUrl(videoUrl) {
    const { path } = cloudinaryDeliveryPath(videoUrl);
    if (!path) return '';
    const jpg = path.replace(/\.mp4$/i, '.jpg');
    return `https://res.cloudinary.com/broadcust/video/upload/so_0,f_jpg,q_auto:eco,w_360,h_202,c_fill/${jpg}`;
  }

  function postThumb(post) {
    if (post.type === 'video' && post.video) return videoThumbUrl(post.video);
    return post.image || '';
  }

  function thumbFallbacks(post) {
    const urls = [postThumb(post)];
    if (post.image && !urls.includes(post.image)) urls.push(post.image);
    return urls;
  }

  function formatDate(raw) {
    if (!raw) return '';
    const m = raw.match(/^(\d{2}\/\d{2}\/\d{4})\s+(\d{2}:\d{2})/);
    if (!m) return raw;
    return `פורסם בתאריך: ${m[1]} ${m[2]}`;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderCard(post, eager) {
    const badge =
      post.type === 'video'
        ? '<span class="blog-badge"><i class="fas fa-play" aria-hidden="true"></i> סרטון</span>'
        : '';
    const loading = eager ? 'eager' : 'lazy';
    const fetchPriority = eager ? ' fetchpriority="high"' : '';
    const posStyle = post.thumbPosition
      ? ` style="object-position: ${escapeHtml(post.thumbPosition)}"`
      : '';
    return `
      <article class="blog-card">
        <a class="blog-card-link" href="post/${post.id}.html">
          <div class="blog-card-media">
            <img src="${escapeHtml(postThumb(post))}" alt="${escapeHtml(post.title)}" loading="${loading}" decoding="async"${fetchPriority}${posStyle}>
            ${badge}
          </div>
          <div class="blog-card-body">
            <h3 class="blog-card-title">${escapeHtml(post.title)}</h3>
            <time class="blog-card-date">${escapeHtml(formatDate(post.date))}</time>
          </div>
        </a>
      </article>`;
  }

  function bindMedia(img) {
    const media = img.closest('.blog-card-media');
    if (!media) return;

    const postId = media.closest('.blog-card')?.querySelector('a')?.href?.match(/post\/(\d+)\.html/)?.[1];
    const post = posts.find((p) => String(p.id) === String(postId));
    const candidates = post ? thumbFallbacks(post) : [img.getAttribute('src') || ''];
    let attempt = 0;

    const markLoaded = () => media.classList.add('is-loaded');
    const tryNext = () => {
      attempt += 1;
      if (attempt < candidates.length) {
        img.src = candidates[attempt];
        return;
      }
      media.classList.add('is-error');
      if (img.src !== FALLBACK_IMG) img.src = FALLBACK_IMG;
      markLoaded();
    };

    if (img.complete && img.naturalWidth > 0) {
      markLoaded();
      return;
    }

    img.addEventListener('load', markLoaded, { once: true });
    img.addEventListener('error', tryNext);
  }

  function renderList(container, limit) {
    const slice = limit > 0 ? posts.slice(0, limit) : posts;
    container.innerHTML = slice
      .map((post, i) => renderCard(post, limit > 0 && i < HOME_LIMIT))
      .join('');
    container.querySelectorAll('.blog-card-media img').forEach(bindMedia);
  }

  function initHomeBlog() {
    const list = document.getElementById('blogList');
    const link = document.getElementById('showAllBlog');
    if (!list || posts.length === 0) return;

    renderList(list, HOME_LIMIT);

    if (link) {
      link.hidden = posts.length <= HOME_LIMIT;
    }
  }

  function initAllBlog() {
    const list = document.getElementById('blogAllList');
    if (!list || posts.length === 0) return;
    renderList(list, 0);
  }

  function boot() {
    initHomeBlog();
    initAllBlog();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
