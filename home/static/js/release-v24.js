(() => {
  document.body.classList.add('release-v24');

  const slugify = value => value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 70) || 'section';

  // Compact article navigation. It uses only the main visible sections.
  document.querySelectorAll('article.article-stack').forEach(article => {
    if (article.querySelector('.release-toc')) return;
    const headings = [...article.querySelectorAll(':scope > .article-section > h2')]
      .filter(h => !/frequently asked|choose a clinic|how care is planned/i.test(h.textContent || ''))
      .slice(0, 7);
    if (headings.length < 3) return;

    const used = new Set();
    headings.forEach((heading, index) => {
      let id = heading.id || slugify(heading.textContent);
      let candidate = id;
      let suffix = 2;
      while (used.has(candidate) || (document.getElementById(candidate) && document.getElementById(candidate) !== heading)) {
        candidate = `${id}-${suffix++}`;
      }
      used.add(candidate);
      heading.id = candidate;
    });

    const nav = document.createElement('nav');
    nav.className = 'release-toc';
    nav.setAttribute('aria-label', 'On this page');
    nav.innerHTML = `<strong>On this page</strong><div class="release-toc-links">${headings.map(h => `<a href="#${h.id}">${h.textContent.trim()}</a>`).join('')}</div>`;
    article.insertBefore(nav, article.firstElementChild);
  });

  // Keep FAQ interaction tidy without turning ordinary content into accordions.
  document.querySelectorAll('.faq-clean-list').forEach(list => {
    list.querySelectorAll('details').forEach(item => {
      item.addEventListener('toggle', () => {
        if (!item.open) return;
        list.querySelectorAll('details[open]').forEach(other => {
          if (other !== item) other.open = false;
        });
      });
    });
  });

  // Remove empty disclosures left by older content imports.
  document.querySelectorAll('details').forEach(item => {
    const body = item.querySelector('.faq-answer, .deep-dive-body, .premium-details-body');
    if (body && !body.textContent.trim() && !body.querySelector('img,input,select,textarea,button')) {
      item.remove();
    }
  });

  const onlyDigits = input => {
    if (!input) return;
    input.addEventListener('input', () => {
      input.value = input.value.replace(/\D/g, '').slice(0, 10);
    });
  };

  const appointmentForm = document.querySelector('[data-appointment-form]');
  if (appointmentForm) {
    const mobile = appointmentForm.querySelector('[name="mobile"]');
    const date = appointmentForm.querySelector('[data-appointment-date]');
    const type = appointmentForm.querySelector('[data-patient-type]');
    const opdField = appointmentForm.querySelector('[data-opd-field]');
    onlyDigits(mobile);

    if (date) {
      const today = new Date();
      const local = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
      date.min = local;
    }

    const updatePatientType = () => {
      if (!opdField || !type) return;
      opdField.hidden = type.value !== 'Existing patient';
    };
    type?.addEventListener('change', updatePatientType);
    updatePatientType();

    appointmentForm.addEventListener('submit', event => {
      event.preventDefault();
      if (!appointmentForm.reportValidity()) return;
      if (!/^\d{10}$/.test(mobile?.value || '')) {
        mobile?.setCustomValidity('Enter a valid 10-digit mobile number.');
        mobile?.reportValidity();
        mobile?.addEventListener('input', () => mobile.setCustomValidity(''), { once: true });
        return;
      }

      const data = new FormData(appointmentForm);
      const lines = [
        'Appointment request - Aastha Skin Centre',
        `Name: ${data.get('name') || ''}`,
        `Mobile: ${data.get('mobile') || ''}`,
        data.get('age') ? `Age: ${data.get('age')}` : '',
        data.get('gender') ? `Gender: ${data.get('gender')}` : '',
        `Clinic: ${data.get('clinic') || 'No preference'}`,
        `Concern: ${data.get('concern') || ''}`,
        `Patient type: ${data.get('patient_type') || ''}`,
        data.get('opd') ? `OPD / patient number: ${data.get('opd')}` : '',
        data.get('date') ? `Preferred date: ${data.get('date')}` : '',
        `Preferred time: ${data.get('time') || 'Any available time'}`,
        data.get('message') ? `Message: ${data.get('message')}` : ''
      ].filter(Boolean);

      window.open(`https://wa.me/917006613362?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
    });
  }

  // Normalise old blog links and make sure local and Render URLs both work.
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (href === '/blog' || href === 'blog' || href === 'blog/' || href === './blog/') {
      link.setAttribute('href', '/blog/');
    }
    if (link.target === '_blank') {
      const rel = new Set((link.rel || '').split(/\s+/).filter(Boolean));
      rel.add('noopener');
      rel.add('noreferrer');
      link.rel = [...rel].join(' ');
    }
  });
})();
