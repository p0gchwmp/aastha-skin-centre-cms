
(() => {
  document.body.classList.add('premium-v2');

  // Replace the oversized auto-generated TOC with a compact, usable version.
  document.querySelectorAll('.article-toc').forEach(node => node.remove());
  const prose = document.querySelector('article.prose');
  if (prose && !prose.querySelector('.premium-toc')) {
    const headings = [...prose.querySelectorAll(':scope > .premium-content-section > h2, :scope > h2')]
      .filter(h => !/frequently asked|where is .*available|medical disclaimer/i.test(h.textContent || ''))
      .slice(0, 8);
    if (headings.length >= 3) {
      headings.forEach((h, i) => {
        if (!h.id) h.id = `section-${i+1}`;
      });
      const nav = document.createElement('nav');
      nav.className = 'premium-toc';
      nav.setAttribute('aria-label', 'On this page');
      nav.innerHTML = `<strong>On this page</strong><div class="premium-toc-links">${headings.map(h => `<a href="#${h.id}">${h.textContent.trim()}</a>`).join('')}</div>`;
      prose.insertBefore(nav, prose.firstElementChild);
    }
  }

  // Keep one long-content disclosure open at a time on small screens.
  if (window.matchMedia('(max-width: 720px)').matches) {
    document.querySelectorAll('details.premium-content-details').forEach(item => {
      item.addEventListener('toggle', () => {
        if (!item.open) return;
        item.parentElement?.querySelectorAll('details.premium-content-details[open]').forEach(other => {
          if (other !== item) other.open = false;
        });
      });
    });
  }

  // Contact enquiry: open a prepared WhatsApp message rather than pretending a backend exists.
  const form = document.querySelector('[data-premium-contact-form]');
  if (form) {
    const mobile = form.querySelector('[name="mobile"]');
    mobile?.addEventListener('input', () => mobile.value = mobile.value.replace(/\D/g,'').slice(0,10));
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (mobile && !/^\d{10}$/.test(mobile.value)) {
        alert('Please enter a valid 10-digit mobile number.');
        mobile.focus();
        return;
      }
      const data = new FormData(form);
      const message = [
        'Clinic enquiry - Aastha Skin Centre',
        `Name: ${data.get('name') || ''}`,
        `Mobile: ${data.get('mobile') || ''}`,
        `Clinic: ${data.get('clinic') || 'No preference'}`,
        `Reason: ${data.get('reason') || ''}`,
        `Message: ${data.get('message') || ''}`
      ].join('\n');
      window.open(`https://wa.me/917006613362?text=${encodeURIComponent(message)}`,'_blank','noopener');
    });
  }

  // In case /blog/ was opened through an old relative link, normalise it.
  document.querySelectorAll('a[href="blog"],a[href="blog/"],a[href="./blog/"]').forEach(a => a.href = '/blog/');
})();
