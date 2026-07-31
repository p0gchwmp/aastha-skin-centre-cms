(() => {
  const CUES = [
    {
      name: 'acne',
      terms: [
        'acne', 'pimple', 'breakout', 'blackhead', 'whitehead',
        'acne mark', 'acne scar'
      ]
    },
    {
      name: 'pigmentation',
      terms: [
        'pigmentation', 'melasma', 'dark spot', 'dark patch', 'uneven tone',
        'freckle', 'sun damage', 'dark lip', 'under eye', 'hyperpigmentation'
      ]
    },
    {
      name: 'hair',
      terms: [
        'hair', 'scalp', 'hair fall', 'dandruff', 'follicle', 'alopecia',
        'trichology'
      ]
    },
    {
      name: 'diagnosis',
      terms: [
        'diagnosis', 'consultation', 'dermatologist-led', 'doctor-led',
        'medical assessment', 'examination', 'dermatoscope', 'skin check',
        'clinical evaluation'
      ]
    },
    {
      name: 'experience',
      terms: [
        'experience', 'years in medicine', 'clinical excellence', 'expertise',
        'trusted care', 'medical experience', 'qualified', 'credentials'
      ]
    },
    {
      name: 'locations',
      terms: [
        'two clinic', 'clinic location', 'locations', 'branches', 'branch',
        'karan nagar', 'paloura', 'find a clinic', 'visit us', 'directions'
      ]
    },
    {
      name: 'complete',
      terms: [
        'complete care', 'comprehensive care', 'skin hair and aesthetic',
        'skin, hair and aesthetic', 'all-in-one care', 'full spectrum',
        'medical and aesthetic', 'complete dermatology'
      ]
    },
    {
      name: 'plan',
      terms: [
        'personalised', 'personalized', 'treatment plan', 'care plan',
        'customised', 'customized', 'tailored', 'your journey',
        'how care is planned', 'next steps', 'care pathway'
      ]
    }
  ];

  const PLACEHOLDER_SELECTOR = [
    '.icon-bubble',
    '.trust-icon',
    '.feature-icon',
    '.benefit-icon',
    '.process-icon',
    '.step-icon',
    '.care-icon',
    '.location-icon',
    '.plan-icon',
    '.why-icon',
    '.info-icon',
    '.mini-icon',
    '.card-icon',
    '[data-visual-cue]'
  ].join(',');

  const CARD_SELECTOR = [
    '.directory-link',
    '.category-card',
    '.feature-card',
    '.benefit-card',
    '.process-card',
    '.step-card',
    '.why-card',
    '.contact-card',
    '.info-card'
  ].join(',');

  const EXCLUDED_SELECTOR = [
    '.treatment-card',
    '.condition-card',
    '.doctor-card',
    '.doctor-profile',
    '.doctor-feature',
    '.doctor-visual',
    '.page-hero-art',
    '.gallery',
    '.image-gallery',
    '.blog-card',
    '.blog-teaser',
    '[class*="treatment-image"]',
    '[class*="condition-image"]',
    '[class*="doctor-image"]'
  ].join(',');

  const normalise = value => (value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9\s,-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const cueForText = value => {
    const text = normalise(value);
    if (!text) return '';
    const match = CUES.find(cue => cue.terms.some(term => text.includes(term)));
    return match?.name || '';
  };

  const isExcluded = element => {
    if (!element || element.closest(EXCLUDED_SELECTOR)) return true;

    const main = element.closest('main');
    const path = window.location.pathname.toLowerCase();
    const clinicalDetailPage =
      /^\/treatments\/[^/]+\/$/.test(path) ||
      /^\/conditions\/[^/]+\/$/.test(path) ||
      path === '/dr-cheena-langer/';

    return Boolean(clinicalDetailPage && main?.contains(element));
  };

  const nearestContext = element => {
    const owner = element.closest([
      '.concern-card', '.trust-item', '.directory-link', '.category-card',
      '.feature-card', '.benefit-card', '.process-card', '.step-card',
      '.why-card', '.contact-card', '.info-card', 'li', 'article', 'section'
    ].join(','));
    return owner || element.parentElement || element;
  };

  const setCue = (element, cue) => {
    if (!element || !cue || isExcluded(element)) return false;
    element.classList.add('message-visual', `message-visual--${cue}`);
    element.setAttribute('aria-hidden', 'true');
    element.setAttribute('role', 'presentation');
    return true;
  };

  const hasMeaningfulVisual = card => Boolean(card.querySelector([
    'img', 'picture', 'svg:not(.icon)', 'video',
    '.message-visual', '.location-art', '.doctor-visual', '.page-hero-art'
  ].join(',')));

  const installHomepageCues = () => {
    document.querySelectorAll('.concern-card .icon-bubble').forEach((icon, index) => {
      const cue = ['acne', 'pigmentation', 'hair'][index];
      if (cue) setCue(icon, cue);
    });

    document.querySelectorAll('.trust-item .trust-icon').forEach((icon, index) => {
      const cue = ['diagnosis', 'experience', 'locations', 'complete', 'plan'][index];
      if (cue) setCue(icon, cue);
    });
  };

  const upgradeExistingPlaceholders = () => {
    document.querySelectorAll(PLACEHOLDER_SELECTOR).forEach(element => {
      if (element.classList.contains('message-visual') || isExcluded(element)) return;
      const requested = normalise(element.dataset.visualCue || '');
      const context = nearestContext(element);
      const cue = CUES.some(item => item.name === requested)
        ? requested
        : cueForText(context.textContent);
      if (cue) setCue(element, cue);
    });
  };

  const upgradeEmojiPlaceholders = () => {
    document.querySelectorAll('main span, main i').forEach(element => {
      if (element.children.length || isExcluded(element)) return;
      const raw = (element.textContent || '').trim();
      const isShortSymbol = raw.length > 0 && raw.length <= 4 && /[^\p{L}\p{N}\s]/u.test(raw);
      if (!isShortSymbol) return;
      const context = nearestContext(element);
      const cue = cueForText(context.textContent);
      if (cue) setCue(element, cue);
    });
  };

  const addCardNavigationCues = () => {
    document.querySelectorAll(CARD_SELECTOR).forEach(card => {
      if (isExcluded(card) || hasMeaningfulVisual(card)) return;
      const cue = cueForText(card.textContent);
      if (!cue) return;

      const visual = document.createElement('span');
      setCue(visual, cue);
      card.classList.add('visual-cue-card');

      const directLink = card.matches('a') ? card : card.querySelector(':scope > a');
      const target = directLink || card;
      target.insertBefore(visual, target.firstChild);
    });
  };

  const install = () => {
    installHomepageCues();
    upgradeExistingPlaceholders();
    upgradeEmojiPlaceholders();
    addCardNavigationCues();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install, { once: true });
  } else {
    install();
  }
})();
