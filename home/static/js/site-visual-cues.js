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

  const buildClayImage = cue => {
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
    image.loading = 'lazy';
    image.fetchPriority = 'low';
    image.decoding = 'async';
    image.draggable = false;
    image.setAttribute('aria-hidden', 'true');
    return image;
  };

  const setCue = (element, cue) => {
    if (!element || !CUE_NAMES.has(cue) || isExcluded(element)) return false;

    const image = buildClayImage(cue);
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

/* Semantic correction pass. It runs after the broad installer above so exact
   message mappings win without adding another JavaScript request. */
(() => {
  const MANIFEST_ID = 'visual-cue-assets';
  const OWNER_SELECTOR = [
    '.hub-category',
    '.process-step',
    '.value-card',
    '.about-story-card',
    '.clinic-location-card',
    '.location-contact-card',
    '.hours-card',
    '.category-card',
    '.feature-card',
    '.benefit-card',
    '.why-card',
    '.service-card',
    '.guide-card',
    '.support-card',
    '.appointment-card',
    '.clinic-card',
    '.cms-card',
    '.contact-action-card',
    '.care-path-card',
    '.step-card',
    '.process-card',
    '.info-card'
  ].join(',');

  const EXACT_RULES = [
    {
      cue: 'plan',
      phrases: [
        'doctor led care',
        'consultations and treatment planning',
        'treatment planning are led by a qualified dermatologist'
      ]
    },
    {
      cue: 'diagnosis',
      phrases: [
        'diagnosis first',
        'assessment comes before procedure choice',
        'similar looking concerns can have different causes'
      ]
    },
    {
      cue: 'clinical',
      phrases: [
        'fungal and recurrent infections',
        'ringworm jock itch athletes foot',
        'steroid modified infections'
      ]
    },
    {
      cue: 'complete',
      phrases: [
        'allergy eczema and itching',
        'skin allergy eczema contact dermatitis',
        'urticaria psoriasis and recurring rashes'
      ]
    },
    {
      cue: 'acne',
      phrases: [
        'acne pimples and breakouts',
        'teenage adult and hormonal acne'
      ]
    },
    {
      cue: 'pigmentation',
      phrases: [
        'pigmentation and colour changes',
        'pigmentation and color changes',
        'melasma general pigmentation dark lips'
      ]
    },
    {
      cue: 'hair',
      phrases: [
        'hair scalp and unwanted hair',
        'hair fall and thinning',
        'alopecia areata dandruff and itchy scalp'
      ]
    },
    {
      cue: 'laser',
      phrases: [
        'advanced laser care',
        'laser hair reduction',
        'scar revision and rejuvenation'
      ]
    },
    {
      cue: 'locations',
      phrases: [
        'visit our clinics in jammu',
        'karan nagar clinic',
        'paloura clinic'
      ]
    },
    {
      cue: 'experience',
      phrases: [
        'years of experience',
        'clinical experience',
        'trusted medical care'
      ]
    }
  ];

  const PROCESS_FALLBACKS = ['plan', 'diagnosis', 'complete', 'experience'];

  const normaliseExact = value => (value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[’']/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const loadExactAssets = () => {
    const manifest = document.getElementById(MANIFEST_ID);
    if (!manifest) return {};
    try {
      return JSON.parse(manifest.textContent || '{}');
    } catch (error) {
      console.warn('Aastha visual cue asset manifest is invalid.', error);
      return {};
    }
  };

  const exactCueForText = value => {
    const text = normaliseExact(value);
    if (!text) return '';
    const rule = EXACT_RULES.find(item => (
      item.phrases.some(phrase => text.includes(normaliseExact(phrase)))
    ));
    return rule?.cue || '';
  };

  const ownedVisuals = owner => [...owner.querySelectorAll('.message-visual')]
    .filter(visual => visual.closest(OWNER_SELECTOR) === owner);

  const buildExactImage = (cue, assets) => {
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
    image.sizes = '(max-width: 540px) 88px, 96px';
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

  const installFailureFallback = (host, image) => {
    image.addEventListener('error', () => {
      host.classList.add('message-visual--failed');
      host.setAttribute('hidden', '');
    }, { once: true });
  };

  const applyExactCue = (host, cue, assets) => {
    if (!host || !assets[cue]) return false;

    const image = buildExactImage(cue, assets);
    if (!image) return false;

    [...host.classList]
      .filter(name => name.startsWith('message-visual--'))
      .forEach(name => host.classList.remove(name));

    host.removeAttribute('hidden');
    host.classList.add('message-visual', `message-visual--${cue}`);
    host.dataset.clayCue = cue;
    host.setAttribute('aria-hidden', 'true');
    host.setAttribute('role', 'presentation');
    host.replaceChildren(image);
    installFailureFallback(host, image);
    return true;
  };

  const ensureVisual = (owner, cue, assets) => {
    if (!owner || !cue) return null;

    const existing = ownedVisuals(owner)[0];
    const host = existing || document.createElement('span');
    if (!existing) host.dataset.visualInjected = 'true';
    if (!applyExactCue(host, cue, assets)) return null;

    owner.classList.add('visual-cue-card', 'visual-cue-card--managed');

    const hubHeading = owner.matches('.hub-category')
      ? owner.querySelector(':scope > .hub-category-heading')
      : null;
    if (hubHeading) {
      if (host.parentElement !== hubHeading || host !== hubHeading.firstElementChild) {
        hubHeading.insertBefore(host, hubHeading.firstElementChild);
      }
      hubHeading.classList.add('hub-category-heading--clay');
      return host;
    }

    if (host.parentElement !== owner || host !== owner.firstElementChild) {
      owner.insertBefore(host, owner.firstElementChild);
    }
    return host;
  };

  const installExactCorrections = () => {
    const assets = loadExactAssets();
    if (!Object.keys(assets).length) return;

    document.querySelectorAll(OWNER_SELECTOR).forEach(owner => {
      const cue = exactCueForText(owner.textContent);
      if (cue) ensureVisual(owner, cue, assets);
    });

    document.querySelectorAll('.process-grid').forEach(grid => {
      const steps = [...grid.querySelectorAll(':scope > .process-step')];
      steps.forEach((step, index) => {
        const explicit = exactCueForText(step.textContent);
        const cue = explicit || PROCESS_FALLBACKS[index % PROCESS_FALLBACKS.length];
        ensureVisual(step, cue, assets);
      });
    });

    document.querySelectorAll(OWNER_SELECTOR).forEach(owner => {
      const visuals = ownedVisuals(owner);
      visuals.slice(1).forEach(visual => visual.remove());
    });
  };

  const scheduleInstall = () => window.setTimeout(installExactCorrections, 0);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleInstall, { once: true });
  } else {
    scheduleInstall();
  }
})();
