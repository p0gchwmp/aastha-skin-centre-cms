(() => {
  const MISSING_ATTRIBUTE = '__clay_missing__';
  const ASSET_MANIFEST_ID = 'visual-cue-assets';

  const CUE_NAMES = new Set([
    'acne',
    'pigmentation',
    'hair',
    'diagnosis',
    'experience',
    'locations',
    'complete',
    'plan',
    'laser',
    'clinical'
  ]);

  /* These labels are deliberately matched from the nearest heading only.
     Never inspect an entire category or card collection: child links such as
     "Laser hair reduction" must not turn the parent "Hair and scalp" icon
     into the laser artwork. */
  const EXACT_LABEL_CUES = new Map([
    ['medical dermatology', 'clinical'],
    ['procedural and aesthetic care', 'laser'],
    ['acne scars and resurfacing', 'acne'],
    ['pigmentation and laser treatments', 'pigmentation'],
    ['hair and scalp treatments', 'hair'],
    ['aesthetic and anti ageing', 'complete'],
    ['minor procedures and dermatosurgery', 'diagnosis'],
    ['doctor led care', 'plan'],
    ['diagnosis first', 'diagnosis'],
    ['fungal and recurrent infections', 'clinical'],
    ['allergy eczema and itching', 'complete'],
    ['acne pimples and breakouts', 'acne'],
    ['pigmentation and colour changes', 'pigmentation'],
    ['pigmentation and color changes', 'pigmentation'],
    ['hair scalp and unwanted hair', 'hair'],
    ['advanced laser care', 'laser'],
    ['visit our clinics in jammu', 'locations'],
    ['karan nagar clinic', 'locations'],
    ['paloura clinic', 'locations'],
    ['complete care', 'complete'],
    ['personalised plans', 'plan'],
    ['personalized plans', 'plan']
  ]);

  const LABEL_RULES = [
    {
      cue: 'acne',
      terms: ['acne', 'pimple', 'breakout', 'blackhead', 'whitehead', 'comedone', 'acne scar']
    },
    {
      cue: 'pigmentation',
      terms: [
        'pigmentation', 'melasma', 'dark spot', 'dark patch', 'uneven tone',
        'freckle', 'sun damage', 'dark lip', 'dark circle', 'under eye',
        'hyperpigmentation', 'black neck'
      ]
    },
    {
      cue: 'hair',
      terms: [
        'hair and scalp', 'hair fall', 'hair loss', 'alopecia', 'dandruff',
        'scalp', 'prp and gfc', 'hair transplant', 'white and grey hair'
      ]
    },
    {
      cue: 'laser',
      terms: [
        'laser hair reduction', 'laser treatment', 'q switched', 'fractional co2',
        'ipl', 'photofacial', 'tattoo removal', 'mnrf', 'radiofrequency',
        'rf tightening', 'hifu', 'energy based', 'procedural and aesthetic'
      ]
    },
    {
      cue: 'clinical',
      terms: [
        'medical dermatology', 'fungal infection', 'skin infection', 'eczema',
        'dermatitis', 'skin allergy', 'psoriasis', 'vitiligo', 'urticaria',
        'hives', 'rosacea', 'scabies', 'paediatric dermatology',
        'pediatric dermatology', 'clinical skin care'
      ]
    },
    {
      cue: 'diagnosis',
      terms: [
        'diagnosis', 'medical assessment', 'clinical assessment', 'skin check',
        'consultation', 'dermatoscopy', 'minor procedures', 'dermatosurgery'
      ]
    },
    {
      cue: 'experience',
      terms: ['20 years', 'years of experience', 'experience in medicine', 'clinical experience']
    },
    {
      cue: 'locations',
      terms: ['two clinics', 'clinic location', 'branches', 'karan nagar', 'paloura', 'directions']
    },
    {
      cue: 'complete',
      terms: [
        'complete care', 'comprehensive care', 'aesthetic and anti ageing',
        'aesthetic and anti aging', 'medical and aesthetic', 'botulinum toxin',
        'dermal fillers', 'hydrafacial', 'medifacial'
      ]
    },
    {
      cue: 'plan',
      terms: [
        'doctor led', 'personalised', 'personalized', 'treatment plan',
        'care plan', 'care pathway', 'next steps', 'appointment', 'follow up'
      ]
    }
  ];

  const PLACEHOLDER_SELECTOR = [
    '.icon-bubble',
    '.trust-icon',
    '.hub-icon',
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
    .replace(/[’']/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const loadAssets = () => {
    const manifest = document.getElementById(ASSET_MANIFEST_ID);
    if (!manifest) return {};
    try {
      return JSON.parse(manifest.textContent || '{}');
    } catch (error) {
      console.warn('Aastha visual cue asset manifest is invalid.', error);
      return {};
    }
  };

  const isExcluded = element => Boolean(!element || element.closest(EXCLUDED_SELECTOR));

  const headingLabel = element => {
    const explicit = normalise(element.dataset.visualCue || '');
    if (CUE_NAMES.has(explicit)) return explicit;

    const headingScope = element.closest([
      '.hub-category-heading',
      '.concern-card',
      '.trust-item',
      '.feature-card',
      '.benefit-card',
      '.process-step',
      '.process-card',
      '.step-card',
      '.why-card',
      '.contact-card',
      '.info-card',
      '.service-card',
      '.guide-card',
      '.support-card',
      '.appointment-card',
      '.clinic-card',
      '.value-card',
      '.about-story-card',
      '.clinic-location-card',
      '.location-contact-card',
      '.hours-card',
      'article'
    ].join(','));

    const heading = headingScope?.querySelector('h1, h2, h3, h4, strong');
    return normalise(heading?.textContent || element.getAttribute('aria-label') || '');
  };

  const cueForLabel = label => {
    const text = normalise(label);
    if (!text) return '';
    if (CUE_NAMES.has(text)) return text;

    const exact = EXACT_LABEL_CUES.get(text);
    if (exact) return exact;

    const match = LABEL_RULES.find(rule => rule.terms.some(term => text.includes(term)));
    return match?.cue || '';
  };

  const rememberOriginal = element => {
    if (element.hasAttribute('data-visual-original-html')) return;
    element.dataset.visualOriginalHtml = element.innerHTML;
    element.dataset.visualOriginalAriaHidden = element.hasAttribute('aria-hidden')
      ? element.getAttribute('aria-hidden')
      : MISSING_ATTRIBUTE;
    element.dataset.visualOriginalRole = element.hasAttribute('role')
      ? element.getAttribute('role')
      : MISSING_ATTRIBUTE;
  };

  const restoreAttribute = (element, attribute, datasetName) => {
    const value = element.dataset[datasetName];
    if (!value || value === MISSING_ATTRIBUTE) {
      element.removeAttribute(attribute);
    } else {
      element.setAttribute(attribute, value);
    }
  };

  const restoreOriginal = element => {
    if (!element.hasAttribute('data-visual-original-html')) return;
    element.innerHTML = element.dataset.visualOriginalHtml;
    restoreAttribute(element, 'aria-hidden', 'visualOriginalAriaHidden');
    restoreAttribute(element, 'role', 'visualOriginalRole');
    delete element.dataset.visualOriginalHtml;
    delete element.dataset.visualOriginalAriaHidden;
    delete element.dataset.visualOriginalRole;
    delete element.dataset.clayCue;
    [...element.classList]
      .filter(name => name.startsWith('message-visual'))
      .forEach(name => element.classList.remove(name));
  };

  const displaySizeFor = element => {
    if (element.matches('.trust-icon')) return '42px';
    if (element.matches('.hub-icon')) return '(max-width: 700px) 46px, 54px';
    if (element.matches('.icon-bubble')) return '54px';
    return '48px';
  };

  const buildImage = (element, cue, assets) => {
    const asset = assets[cue];
    if (!asset?.['128'] || !asset?.['256'] || !asset?.['512']) return null;

    const image = document.createElement('img');
    image.className = 'message-visual__img';
    image.src = asset['128'];
    image.srcset = [
      `${asset['128']} 128w`,
      `${asset['256']} 256w`,
      `${asset['512']} 512w`
    ].join(', ');
    image.sizes = displaySizeFor(element);
    image.width = 512;
    image.height = 512;
    image.alt = '';
    image.loading = 'lazy';
    image.fetchPriority = 'low';
    image.decoding = 'async';
    image.draggable = false;
    image.setAttribute('aria-hidden', 'true');
    return image;
  };

  const applyCue = (element, cue, assets) => {
    if (!element || !CUE_NAMES.has(cue) || isExcluded(element)) return false;

    const image = buildImage(element, cue, assets);
    if (!image) return false;

    rememberOriginal(element);
    [...element.classList]
      .filter(name => name.startsWith('message-visual--'))
      .forEach(name => element.classList.remove(name));

    element.classList.add('message-visual', `message-visual--${cue}`);
    element.dataset.clayCue = cue;
    element.setAttribute('aria-hidden', 'true');
    element.setAttribute('role', 'presentation');
    element.replaceChildren(image);

    image.addEventListener('error', () => restoreOriginal(element), { once: true });
    return true;
  };

  const installTrustRibbon = assets => {
    const cues = ['diagnosis', 'experience', 'locations', 'complete', 'plan'];
    document.querySelectorAll('.trust-item .trust-icon').forEach((icon, index) => {
      const cue = cues[index];
      if (cue) applyCue(icon, cue, assets);
    });
  };

  const installExistingPlaceholders = assets => {
    document.querySelectorAll(PLACEHOLDER_SELECTOR).forEach(element => {
      if (element.classList.contains('message-visual') || isExcluded(element)) return;
      if (element.matches('.trust-item .trust-icon')) return;

      const requested = normalise(element.dataset.visualCue || '');
      const cue = CUE_NAMES.has(requested)
        ? requested
        : cueForLabel(headingLabel(element));
      if (cue) applyCue(element, cue, assets);
    });
  };

  const install = () => {
    const assets = loadAssets();
    if (!Object.keys(assets).length) return;
    installTrustRibbon(assets);
    installExistingPlaceholders(assets);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install, { once: true });
  } else {
    install();
  }
})();
