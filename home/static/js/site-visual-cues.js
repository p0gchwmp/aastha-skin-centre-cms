(() => {
  const MISSING_ATTRIBUTE = '__clay_missing__';
  const ASSET_MANIFEST_ID = 'visual-cue-assets';
  const DISPLAY_SIZES = '(max-width: 700px) 112px, 116px';

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

  const ASSETS = loadAssets();

  /* Order is intentional: specific services win before broad clinical terms. */
  const CUES = [
    {
      name: 'acne',
      terms: [
        'acne', 'pimple', 'breakout', 'blackhead', 'whitehead',
        'acne mark', 'acne scar', 'comedone'
      ]
    },
    {
      name: 'pigmentation',
      terms: [
        'pigmentation', 'melasma', 'dark spot', 'dark patch', 'uneven tone',
        'freckle', 'sun damage', 'dark lip', 'under eye', 'hyperpigmentation',
        'post inflammatory pigmentation', 'black neck'
      ]
    },
    {
      name: 'laser',
      terms: [
        'laser hair reduction', 'laser treatment', 'laser therapy', 'laser care',
        'q switched', 'q-switched', 'fractional co2', 'co2 laser', 'diode laser',
        'ipl', 'photofacial', 'carbon peel', 'tattoo removal', 'scar revision',
        'mnrf', 'micro needling radiofrequency', 'radiofrequency', 'rf treatment',
        'hifu', 'skin tightening', 'skin rejuvenation', 'advanced technology'
      ]
    },
    {
      name: 'hair',
      terms: [
        'hair fall', 'hair loss', 'scalp', 'dandruff', 'follicle', 'alopecia',
        'trichology', 'hair growth', 'prp hair', 'gfc hair', 'hair transplant',
        'white hair'
      ]
    },
    {
      name: 'clinical',
      terms: [
        'skin infection', 'fungal infection', 'ringworm', 'tinea', 'candidiasis',
        'bacterial infection', 'viral infection', 'erythrasma', 'impetigo',
        'folliculitis', 'boil', 'cellulitis', 'scabies', 'molluscum',
        'eczema', 'dermatitis', 'skin allergy', 'rash', 'sensitive skin',
        'psoriasis', 'vitiligo', 'urticaria', 'hives', 'rosacea', 'lichen planus',
        'seborrheic', 'wart', 'mole', 'skin tag', 'corn', 'cyst', 'xanthelasma',
        'nail surgery', 'ingrown nail', 'nail fungus', 'std', 'pediatric dermatology',
        'paediatric dermatology', 'skin cancer screening', 'medical dermatology',
        'minor procedure', 'dermato surgery', 'dermatosurgery'
      ]
    },
    {
      name: 'diagnosis',
      terms: [
        'diagnosis', 'consultation', 'dermatologist-led', 'doctor-led',
        'medical assessment', 'examination', 'dermatoscope', 'skin check',
        'clinical evaluation', 'expert assessment', 'qualified dermatologist'
      ]
    },
    {
      name: 'experience',
      terms: [
        'experience', 'years in medicine', 'years of experience', '20 years',
        '25 years', 'clinical excellence', 'expertise', 'trusted care',
        'medical experience', 'credentials', 'established care'
      ]
    },
    {
      name: 'locations',
      terms: [
        'two clinic', 'clinic location', 'locations', 'branches', 'branch',
        'karan nagar', 'paloura', 'find a clinic', 'visit us', 'directions',
        'contact us', 'call us', 'jammu clinics'
      ]
    },
    {
      name: 'complete',
      terms: [
        'complete care', 'comprehensive care', 'skin hair and aesthetic',
        'skin, hair and aesthetic', 'all-in-one care', 'full spectrum',
        'medical and aesthetic', 'complete dermatology', 'aesthetic care',
        'anti ageing', 'anti-aging', 'botox', 'filler', 'skin booster',
        'chemical peel', 'hydrafacial', 'medifacial'
      ]
    },
    {
      name: 'plan',
      terms: [
        'personalised', 'personalized', 'treatment plan', 'care plan',
        'customised', 'customized', 'tailored', 'your journey',
        'how care is planned', 'next steps', 'care pathway', 'appointment',
        'book consultation', 'book your consultation', 'aftercare', 'follow up'
      ]
    }
  ];

  const CUE_NAMES = new Set(CUES.map(cue => cue.name));

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
    '.info-card',
    '.cms-card',
    '.service-card',
    '.guide-card',
    '.support-card',
    '.appointment-card',
    '.clinic-card'
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
    .replace(/[^a-z0-9\s,+-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const cueForText = value => {
    const text = normalise(value);
    if (!text) return '';
    const match = CUES.find(cue => cue.terms.some(term => text.includes(term)));
    return match?.name || '';
  };

  const isExcluded = element => Boolean(
    !element || element.closest(EXCLUDED_SELECTOR)
  );

  const nearestContext = element => {
    const owner = element.closest([
      '.concern-card', '.trust-item', '.directory-link', '.category-card',
      '.feature-card', '.benefit-card', '.process-card', '.step-card',
      '.why-card', '.contact-card', '.info-card', '.cms-card',
      '.service-card', '.guide-card', '.support-card', '.appointment-card',
      '.clinic-card', 'li', 'article', 'section'
    ].join(','));
    return owner || element.parentElement || element;
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

  const buildClayImage = (cue, priority = false) => {
    const asset = ASSETS[cue];
    if (!asset?.['128'] || !asset?.['256'] || !asset?.['512']) return null;

    const image = document.createElement('img');
    image.className = 'message-visual__img';
    image.src = asset['128'];
    image.srcset = [
      `${asset['128']} 128w`,
      `${asset['256']} 256w`,
      `${asset['512']} 512w`
    ].join(', ');
    image.sizes = DISPLAY_SIZES;
    image.width = 512;
    image.height = 512;
    image.alt = '';
    image.loading = priority ? 'eager' : 'lazy';
    image.decoding = 'async';
    image.draggable = false;
    image.setAttribute('aria-hidden', 'true');
    return image;
  };

  const setCue = (element, cue) => {
    if (!element || !CUE_NAMES.has(cue) || isExcluded(element)) return false;

    const image = buildClayImage(
      cue,
      Boolean(element.closest('.concern-card, .trust-item'))
    );
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
    return true;
  };

  const hasMeaningfulVisual = card => Boolean(card.querySelector([
    'img', 'picture', 'svg', 'video',
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

  const upgradeExistingPlaceholders = root => {
    root.querySelectorAll(PLACEHOLDER_SELECTOR).forEach(element => {
      if (element.classList.contains('message-visual') || isExcluded(element)) return;
      const requested = normalise(element.dataset.visualCue || '');
      const context = nearestContext(element);
      const cue = CUE_NAMES.has(requested)
        ? requested
        : cueForText(context.textContent);
      if (cue) setCue(element, cue);
    });
  };

  const upgradeEmojiPlaceholders = root => {
    root.querySelectorAll('main span, main i').forEach(element => {
      if (element.children.length || isExcluded(element)) return;
      const marker = `${element.className || ''} ${element.parentElement?.className || ''}`;
      if (!/(icon|emoji|bubble|motif|symbol)/i.test(marker)) return;
      const raw = (element.textContent || '').trim();
      const isShortSymbol = raw.length > 0
        && raw.length <= 4
        && /[^\p{L}\p{N}\s]/u.test(raw);
      if (!isShortSymbol) return;
      const cue = cueForText(nearestContext(element).textContent);
      if (cue) setCue(element, cue);
    });
  };

  const addCardNavigationCues = root => {
    root.querySelectorAll(CARD_SELECTOR).forEach(card => {
      if (isExcluded(card) || hasMeaningfulVisual(card)) return;
      const cue = cueForText(card.textContent);
      if (!cue) return;

      const visual = document.createElement('span');
      visual.dataset.visualInjected = 'true';
      if (!setCue(visual, cue)) return;
      card.classList.add('visual-cue-card');

      const directLink = card.matches('a') ? card : card.querySelector(':scope > a');
      const target = directLink || card;
      target.insertBefore(visual, target.firstChild);
    });
  };

  const install = (root = document) => {
    if (root === document) installHomepageCues();
    upgradeExistingPlaceholders(root);
    upgradeEmojiPlaceholders(root);
    addCardNavigationCues(root);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => install(), { once: true });
  } else {
    install();
  }
})();
