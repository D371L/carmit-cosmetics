(function () {
  'use strict';

  const data = window.GALLERY_DATA;
  if (!data) return;

  const imagesTrack = document.getElementById('galleryImagesTrack');
  const videosTrack = document.getElementById('galleryVideosTrack');
  const lightbox = document.getElementById('mediaLightbox');
  if (!imagesTrack || !videosTrack || !lightbox) return;

  const stage = lightbox.querySelector('.media-lightbox__stage');
  const btnClose = lightbox.querySelector('.media-lightbox__close');
  const btnPrev = lightbox.querySelector('.media-lightbox__prev');
  const btnNext = lightbox.querySelector('.media-lightbox__next');
  const counter = lightbox.querySelector('.media-lightbox__counter');

  let activeGroup = 'images';
  let activeIndex = 0;
  let activeVideo = null;
  let touchStartX = 0;
  let touchStartY = 0;

  function escapeAttr(value) {
    return String(value).replace(/"/g, '&quot;');
  }

  function renderCarousels() {
    imagesTrack.innerHTML = data.images
      .map(
        (item, i) => `
      <button type="button" class="gallery-carousel__item gallery-carousel__item--image" data-group="images" data-index="${i}" aria-label="${escapeAttr(item.alt)}">
        <img src="${escapeAttr(item.thumb)}" alt="${escapeAttr(item.alt)}" loading="lazy" width="280" height="280">
      </button>`
      )
      .join('');

    videosTrack.innerHTML = data.videos
      .map(
        (item, i) => `
      <button type="button" class="gallery-carousel__item gallery-carousel__item--video" data-group="videos" data-index="${i}" aria-label="${escapeAttr(item.alt)}">
        <img src="${escapeAttr(item.poster)}" alt="${escapeAttr(item.alt)}" loading="lazy" width="280" height="280">
        <span class="gallery-carousel__play" aria-hidden="true"><i class="fas fa-play"></i></span>
      </button>`
      )
      .join('');
  }

  function currentItems() {
    return activeGroup === 'videos' ? data.videos : data.images;
  }

  function pauseActiveVideo() {
    if (activeVideo) {
      activeVideo.pause();
      activeVideo = null;
    }
  }

  function renderLightboxSlide() {
    const items = currentItems();
    const item = items[activeIndex];
    if (!item) return;

    pauseActiveVideo();

    if (activeGroup === 'videos') {
      stage.innerHTML = `
        <video class="media-lightbox__video" controls playsinline preload="metadata" poster="${escapeAttr(item.poster)}" aria-label="${escapeAttr(item.alt)}">
          <source src="${escapeAttr(item.src)}" type="video/mp4">
        </video>`;
      activeVideo = stage.querySelector('video');
    } else {
      stage.innerHTML = `<img class="media-lightbox__image" src="${escapeAttr(item.full)}" alt="${escapeAttr(item.alt)}">`;
    }

    lightbox.setAttribute('aria-label', item.alt || 'תצוגה מוגדלת');

    if (counter) {
      counter.textContent = `${activeIndex + 1} / ${items.length}`;
    }

    const hasMultiple = items.length > 1;
    btnPrev.hidden = !hasMultiple;
    btnNext.hidden = !hasMultiple;
  }

  function openLightbox(group, index) {
    activeGroup = group;
    activeIndex = index;
    renderLightboxSlide();
    lightbox.hidden = false;
    document.body.classList.add('media-lightbox-open');
    btnClose.focus();
  }

  function closeLightbox() {
    pauseActiveVideo();
    lightbox.hidden = true;
    document.body.classList.remove('media-lightbox-open');
    stage.innerHTML = '';
  }

  function step(delta) {
    const items = currentItems();
    if (items.length <= 1) return;
    activeIndex = (activeIndex + delta + items.length) % items.length;
    renderLightboxSlide();
  }

  function onCarouselClick(e) {
    const btn = e.target.closest('[data-group][data-index]');
    if (!btn) return;
    openLightbox(btn.dataset.group, Number(btn.dataset.index));
  }

  function onKeyDown(e) {
    if (lightbox.hidden) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') step(1);
    if (e.key === 'ArrowRight') step(-1);
  }

  function onTouchStart(e) {
    if (lightbox.hidden || e.touches.length !== 1) return;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }

  function onTouchEnd(e) {
    if (lightbox.hidden || !e.changedTouches.length) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) < 40 || Math.abs(dx) < Math.abs(dy)) return;
    step(dx < 0 ? 1 : -1);
  }

  renderCarousels();

  imagesTrack.addEventListener('click', onCarouselClick);
  videosTrack.addEventListener('click', onCarouselClick);

  btnClose.addEventListener('click', closeLightbox);
  btnPrev.addEventListener('click', () => step(-1));
  btnNext.addEventListener('click', () => step(1));

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', onKeyDown);
  lightbox.addEventListener('touchstart', onTouchStart, { passive: true });
  lightbox.addEventListener('touchend', onTouchEnd, { passive: true });
})();
