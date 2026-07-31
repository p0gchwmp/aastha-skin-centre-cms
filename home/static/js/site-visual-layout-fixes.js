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

  const normalise = value => (value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[’']/g, '')
    .replace(/[^a-z0-9\s-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const loadAssets = () => {
    const manifest = document.getElementById(MANIFEST_ID);
    if (!manifest) return {};
    try {
      return JSON.parse(manifest.textContent || '{}');
    } catch (error) {
      console.warn('Aastha visual cue asset manifest is invalid.', error);
      return {};
    }
  };

  const ASSETS = loadAssets();

  const cueForText = value => {
    const text = normalise(value);
    if (!text) return '';
    const rule = EXACT_RULES.find(item => (
      item.phrases.some(phrase => text.includes(normalise(phrase)))
    ));
    return rule?.cue || '';
  };

  const ownedVisuals = owner => [...owner.querySelectorAll('.message-visual')]
    .filter(visual => visual.closest(OWNER_SELECTOR) === owner);

  const buildImage = cue => {
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

  const applyCue = (host, cue) => {
    if (!host || !ASSETS[cue]) return false;

    const image = buildImage(cue);
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

  const ensureVisual = (owner, cue) => {
    if (!owner || !cue) return null;

    const existing = ownedVisuals(owner)[0];
    const host = existing || document.createElement('span');
    if (!existing) host.dataset.visualInjected = 'true';
    if (!applyCue(host, cue)) return null;

    owner.classList.add('visual-cue-card', 'visual-cue-card--managed');

    /* Hub headings already provide a dedicated media column. Keep the icon
       inside that heading and let CSS reserve the correct width. */
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

    /* Other managed cards use a normal-flow media row, never an overlay. */
    if (host.parentElement !== owner || host !== owner.firstElementChild) {
      owner.insertBefore(host, owner.firstElementChild);
    }
    return host;
  };

  const fixSemanticOwners = () => {
    document.querySelectorAll(OWNER_SELECTOR).forEach(owner => {
      const cue = cueForText(owner.textContent);
      if (!cue) return;
      ensureVisual(owner, cue);
    });
  };

  const diversifyProcessSteps = () => {
    document.querySelectorAll('.process-grid').forEach(grid => {
      const steps = [...grid.querySelectorAll(':scope > .process-step')];
      steps.forEach((step, index) => {
        const explicit = cueForText(step.textContent);
        const cue = explicit || PROCESS_FALLBACKS[index % PROCESS_FALLBACKS.length];
        ensureVisual(step, cue);
      });
    });
  };

  const removeOwnedDuplicates = () => {
    document.querySelectorAll(OWNER_SELECTOR).forEach(owner => {
      const visuals = ownedVisuals(owner);
      visuals.slice(1).forEach(visual => visual.remove());
    });
  };

  const install = () => {
    fixSemanticOwners();
    diversifyProcessSteps();
    removeOwnedDuplicates();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install, { once: true });
  } else {
    install();
  }
})();
