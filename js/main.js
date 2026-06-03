(function () {
  'use strict';

  // Scroll to top (visible after hero)
  const hero = document.querySelector('.hero');
  const scrollTopBtn = document.getElementById('scrollTopBtn');

  if (hero && scrollTopBtn) {
    const updateScrollTop = () => {
      scrollTopBtn.classList.toggle('is-visible', window.scrollY >= hero.offsetHeight);
    };

    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', updateScrollTop, { passive: true });
    window.addEventListener('resize', updateScrollTop, { passive: true });
    updateScrollTop();
  }

  // Customer list form → WhatsApp (modal)
  const clubForm = document.getElementById('clubForm');
  const clubModal = document.getElementById('clubModal');
  const clubOpenBtn = document.getElementById('clubOpenBtn');
  const clubModalClose = document.getElementById('clubModalClose');
  const clubModalBackdrop = document.getElementById('clubModalBackdrop');
  const WA_PHONE = '972524677347';

  function openClubModal() {
    if (!clubModal) return;
    clubModal.hidden = false;
    document.body.style.overflow = 'hidden';
    const first = document.getElementById('clubFirstName');
    if (first) first.focus();
  }

  function closeClubModal() {
    if (!clubModal) return;
    clubModal.hidden = true;
    document.body.style.overflow = '';
    if (clubOpenBtn) clubOpenBtn.focus();
  }

  if (clubOpenBtn) clubOpenBtn.addEventListener('click', openClubModal);
  if (clubModalClose) clubModalClose.addEventListener('click', closeClubModal);
  if (clubModalBackdrop) clubModalBackdrop.addEventListener('click', closeClubModal);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && clubModal && !clubModal.hidden) closeClubModal();
  });

  if (clubForm) {
    const fields = {
      firstName: document.getElementById('clubFirstName'),
      lastName: document.getElementById('clubLastName'),
      phone: document.getElementById('clubPhone'),
      email: document.getElementById('clubEmail'),
      address: document.getElementById('clubAddress'),
      city: document.getElementById('clubCity'),
      birthDay: document.getElementById('clubBirthDay'),
      birthMonth: document.getElementById('clubBirthMonth'),
      birthYear: document.getElementById('clubBirthYear'),
      consent: document.getElementById('clubConsent'),
    };

    const errors = {
      firstName: document.getElementById('clubFirstNameError'),
      phone: document.getElementById('clubPhoneError'),
      consent: document.getElementById('clubConsentError'),
    };

    function setFieldError(input, errorEl, show) {
      if (input) input.classList.toggle('is-invalid', show);
      if (errorEl) errorEl.hidden = !show;
    }

    function validateClubForm() {
      let valid = true;
      const firstName = fields.firstName.value.trim();
      const phone = fields.phone.value.trim();

      if (!firstName) {
        setFieldError(fields.firstName, errors.firstName, true);
        valid = false;
      } else {
        setFieldError(fields.firstName, errors.firstName, false);
      }

      if (!phone) {
        setFieldError(fields.phone, errors.phone, true);
        valid = false;
      } else {
        setFieldError(fields.phone, errors.phone, false);
      }

      if (!fields.consent.checked) {
        if (errors.consent) errors.consent.hidden = false;
        valid = false;
      } else if (errors.consent) {
        errors.consent.hidden = true;
      }

      return valid;
    }

    function buildWhatsAppMessage() {
      const lines = [
        'שלום,',
        'אני מעוניין/ת להצטרף לרשימת הלקוחות. אלו הפרטים שלי:',
        '',
      ];

      const add = (label, value) => {
        const v = (value || '').trim();
        if (v) lines.push(`${label}: ${v}`);
      };

      add('שם פרטי', fields.firstName.value);
      add('שם משפחה', fields.lastName.value);
      add('טלפון נייד', fields.phone.value);
      add('אימייל', fields.email.value);
      add('כתובת', fields.address.value);
      add('עיר', fields.city.value);

      const day = fields.birthDay.value.trim();
      const month = fields.birthMonth.value.trim();
      const year = fields.birthYear.value.trim();
      if (day || month || year) {
        lines.push(`יום הולדת: ${day}/${month}/${year}`);
      }

      return lines.join('\n');
    }

    Object.values(fields).forEach((el) => {
      if (!el || el.type === 'checkbox') return;
      el.addEventListener('input', () => {
        if (el === fields.firstName) setFieldError(el, errors.firstName, !el.value.trim());
        if (el === fields.phone) setFieldError(el, errors.phone, !el.value.trim());
      });
    });

    fields.consent.addEventListener('change', () => {
      if (errors.consent) errors.consent.hidden = fields.consent.checked;
    });

    clubForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!validateClubForm()) return;

      const text = encodeURIComponent(buildWhatsAppMessage());
      window.open(`https://wa.me/${WA_PHONE}?text=${text}`, '_blank', 'noopener');
      closeClubModal();
    });
  }

})();
