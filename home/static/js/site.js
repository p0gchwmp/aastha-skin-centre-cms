(() => {
  const DEFAULTS = {"version": 1, "last_updated": "2026-07-28", "clinic": {"name": "Aastha Skin & Dermato-Cosmetic Centre", "short_name": "Aastha Skin Centre", "email": "aasthaskinsurgs@gmail.com", "consultation_fee": 500, "currency_symbol": "₹", "follow_up_days": 10, "follow_up_included": true, "online_response": "30–60 minutes during clinic hours", "appointment_confirmation_text": "Submitting this form requests an appointment. Your appointment is confirmed only after the clinic contacts you.", "emergency_note": "Clinic phone numbers are not emergency-service numbers."}, "contact": {"primary_mobile": "7006613362", "secondary_mobile": "9796676541", "whatsapp_mobile": "7006613362"}, "social": {"instagram": "https://www.instagram.com/aastha_skin_centre/", "youtube": "https://www.youtube.com/@aasthaskincentre", "facebook": "https://www.facebook.com/"}, "locations": {"karan_nagar": {"name": "Karan Nagar", "address": "Lane 2, Karan Nagar, near Amphalla Chowk, Jammu, Jammu & Kashmir – 180005", "landline": "0191-3509230", "google_maps": "https://maps.app.goo.gl/pHCQ1r4crKuZBSi98", "reception_hours": "Mon–Sat 10:00 AM–8:00 PM · Sun 10:00 AM–3:00 PM", "doctor_hours": "Mon–Sat 11:00 AM–4:00 PM · Sun 11:00 AM–3:00 PM", "procedure_hours": "Mon–Sat 11:00 AM–8:00 PM · Sun 11:00 AM–3:00 PM"}, "paloura": {"name": "Paloura Chowk", "address": "Paloura Chowk, Top Paloura, opposite Government Senior Secondary School, Jammu, Jammu & Kashmir – 181121", "landline": "0191-3135864", "google_maps": "https://maps.app.goo.gl/kh4AqZoUkscpEgWc8", "reception_hours": "Mon–Sat 10:00 AM–8:00 PM · Sun 10:00 AM–2:00 PM", "doctor_hours": "Mon–Sat 6:00 PM–8:00 PM · Sun 10:30 AM–12:00 PM", "procedure_hours": "Mon–Sat 10:00 AM–8:00 PM · Sun 10:30 AM–12:00 PM"}}, "theme": {"default": "system", "allow_toggle": true}, "blog": {"enabled": true, "auto_link_max_per_keyword_per_page": 1, "exclude_paths": ["/blog/", "/privacy-policy/", "/terms-and-conditions/", "/medical-disclaimer/", "/book-appointment/", "/contact/"]}};

  const conditionsMenu = `<div class="mega-column"><h3>Acne, Scars &amp; Texture</h3><ul><li><a href="/treatments/acne-treatment/">Acne Treatment</a></li>
<li><a href="/treatments/acne-scar-treatment/">Acne Scar Treatment</a></li>
<li><a href="/treatments/chickenpox-scar-treatment/">Chickenpox Scar Treatment</a></li>
<li><a href="/treatments/keloid-hypertrophic-scar-treatment/">Keloid &amp; Hypertrophic Scar Treatment</a></li></ul></div>
<div class="mega-column"><h3>Pigmentation &amp; Colour Changes</h3><ul><li><a href="/treatments/pigmentation-treatment/">Pigmentation Treatment</a></li>
<li><a href="/treatments/melasma-treatment/">Melasma Treatment</a></li>
<li><a href="/treatments/vitiligo-treatment/">Vitiligo Treatment</a></li>
<li><a href="/treatments/black-neck-acanthosis-nigricans-treatment/">Black Neck &amp; Acanthosis Nigricans</a></li>
<li><a href="/treatments/dark-circles-under-eye-treatment/">Dark Circles &amp; Under-Eye Treatment</a></li>
<li><a href="/treatments/dark-lips-treatment/">Dark Lips &amp; Lip Pigmentation</a></li>
<li><a href="/treatments/freckles-treatment/">Freckles &amp; Sun Spots Treatment</a></li>
<li><a href="/treatments/sun-damage-treatment/">Sun Damage Treatment</a></li></ul></div>
<div class="mega-column"><h3>Hair &amp; Scalp</h3><ul><li><a href="/treatments/hair-fall-treatment/">Hair Fall Treatment</a></li>
<li><a href="/treatments/alopecia-areata-treatment/">Alopecia Areata Treatment</a></li>
<li><a href="/treatments/seborrheic-dermatitis-dandruff/">Seborrhoeic Dermatitis &amp; Dandruff</a></li>
<li><a href="/treatments/white-hair-removal/">White &amp; Grey Hair Removal</a></li></ul></div>
<div class="mega-column"><h3>Allergy &amp; Inflammatory Skin</h3><ul><li><a href="/treatments/skin-allergy-treatment/">Skin Allergy Treatment</a></li>
<li><a href="/treatments/psoriasis-treatment/">Psoriasis Treatment</a></li>
<li><a href="/treatments/rosacea-treatment/">Rosacea Treatment</a></li>
<li><a href="/treatments/urticaria-hives-treatment/">Urticaria &amp; Hives Treatment</a></li>
<li><a href="/treatments/eczema-atopic-dermatitis-treatment/">Eczema &amp; Atopic Dermatitis</a></li>
<li><a href="/treatments/contact-dermatitis-treatment/">Contact Dermatitis Treatment</a></li>
<li><a href="/treatments/lichen-planus-treatment/">Lichen Planus Treatment</a></li></ul></div>
<div class="mega-column"><h3>Infections &amp; Infestations</h3><ul><li><a href="/treatments/fungal-infection-treatment/">Fungal Infection Treatment</a></li>
<li><a href="/treatments/scabies-treatment/">Scabies Treatment</a></li>
<li><a href="/treatments/molluscum-contagiosum-treatment/">Molluscum Contagiosum Treatment</a></li>
<li><a href="/treatments/sti-std-treatment/">STI &amp; STD Treatment</a></li></ul></div>
<div class="mega-column"><h3>Children, Screening &amp; Other Concerns</h3><ul><li><a href="/treatments/paediatric-dermatology/">Paediatric Dermatology</a></li>
<li><a href="/treatments/skin-cancer-screening/">Skin Cancer Screening</a></li>
<li><a href="/treatments/xanthelasma-removal/">Xanthelasma Treatment &amp; Removal</a></li>
<li><a href="/treatments/corn-removal-treatment/">Corn Removal Treatment</a></li>
<li><a href="/treatments/ingrown-toenail-nail-surgery/">Ingrown Toenail &amp; Nail Surgery</a></li></ul></div>`;
  const treatmentsMenu = `<div class="mega-column"><h3>Acne Scar &amp; Skin Resurfacing</h3><ul><li><a href="/treatments/acne-scar-treatment/">Acne Scar Treatment</a></li>
<li><a href="/treatments/mnrf-treatment/">MNRF Treatment</a></li>
<li><a href="/treatments/fractional-co2-laser/">Fractional CO₂ Laser</a></li>
<li><a href="/treatments/chemical-peels/">Chemical Peels</a></li>
<li><a href="/treatments/chickenpox-scar-treatment/">Chickenpox Scar Treatment</a></li></ul></div>
<div class="mega-column"><h3>Pigmentation &amp; Laser</h3><ul><li><a href="/treatments/pigmentation-treatment/">Pigmentation Treatment</a></li>
<li><a href="/treatments/melasma-treatment/">Melasma Treatment</a></li>
<li><a href="/treatments/q-switched-laser-toning/">Q-Switched Laser &amp; Laser Toning</a></li>
<li><a href="/treatments/ipl-photofacial/">IPL Photofacial</a></li>
<li><a href="/treatments/laser-tattoo-removal/">Laser Tattoo Removal</a></li>
<li><a href="/treatments/sun-damage-treatment/">Sun Damage Treatment</a></li></ul></div>
<div class="mega-column"><h3>Hair Treatments</h3><ul><li><a href="/treatments/laser-hair-reduction/">Laser Hair Reduction</a></li>
<li><a href="/treatments/prp-gfc-hair-treatment/">PRP &amp; GFC Hair Treatment</a></li>
<li><a href="/treatments/hair-transplant/">Hair Transplant</a></li>
<li><a href="/treatments/white-hair-removal/">White &amp; Grey Hair Removal</a></li></ul></div>
<div class="mega-column"><h3>Aesthetic &amp; Anti-ageing</h3><ul><li><a href="/treatments/botulinum-toxin-dermal-fillers/">Botulinum Toxin &amp; Dermal Fillers</a></li>
<li><a href="/treatments/hifu-rf-skin-tightening/">HIFU &amp; RF Skin Tightening</a></li>
<li><a href="/treatments/hifu-treatment/">HIFU Treatment</a></li>
<li><a href="/treatments/rf-skin-tightening/">RF Skin Tightening</a></li>
<li><a href="/treatments/hydrafacial-medifacial/">Hydrafacial &amp; Medifacial</a></li></ul></div>
<div class="mega-column"><h3>Minor Procedures</h3><ul><li><a href="/treatments/wart-mole-skin-tag-removal/">Wart, Mole &amp; Skin Tag Removal</a></li>
<li><a href="/treatments/dpn-seborrheic-keratosis-removal/">DPN &amp; Seborrhoeic Keratosis Removal</a></li>
<li><a href="/treatments/cyst-lipoma-removal/">Cyst &amp; Lipoma Removal</a></li>
<li><a href="/treatments/skin-abscess-incision-drainage/">Skin Abscess &amp; Incision and Drainage</a></li>
<li><a href="/treatments/skin-biopsy/">Skin Biopsy</a></li>
<li><a href="/treatments/xanthelasma-removal/">Xanthelasma Treatment &amp; Removal</a></li></ul></div>
<div class="mega-column"><h3>Nail, Foot &amp; Body</h3><ul><li><a href="/treatments/ingrown-toenail-nail-surgery/">Ingrown Toenail &amp; Nail Surgery</a></li>
<li><a href="/treatments/corn-removal-treatment/">Corn Removal Treatment</a></li>
<li><a href="/treatments/cryolipolysis-body-contouring/">Cryolipolysis &amp; Body Contouring</a></li></ul></div>`;

  const get = (obj, path, fallback = "") =>
    path.split(".").reduce((value, key) =>
      value && Object.prototype.hasOwnProperty.call(value, key) ? value[key] : undefined,
      obj
    ) ?? fallback;

  const digits = value => String(value || "").replace(/\D/g, "");

  async function loadConfig() {
    try {
      const response = await fetch("/assets/data/site-config.json", { cache: "no-store" });
      if (!response.ok) throw new Error("Config request failed");
      const remote = await response.json();
      return {
        ...DEFAULTS,
        ...remote,
        clinic: { ...DEFAULTS.clinic, ...(remote.clinic || {}) },
        contact: { ...DEFAULTS.contact, ...(remote.contact || {}) },
        social: { ...DEFAULTS.social, ...(remote.social || {}) },
        locations: {
          karan_nagar: {
            ...DEFAULTS.locations.karan_nagar,
            ...((remote.locations || {}).karan_nagar || {})
          },
          paloura: {
            ...DEFAULTS.locations.paloura,
            ...((remote.locations || {}).paloura || {})
          }
        },
        theme: { ...DEFAULTS.theme, ...(remote.theme || {}) },
        blog: { ...DEFAULTS.blog, ...(remote.blog || {}) }
      };
    } catch (error) {
      console.warn("Using built-in site settings.", error);
      return DEFAULTS;
    }
  }

  function socialIcon(label) {
    const icons = {
      Instagram: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"></rect><circle cx="12" cy="12" r="4"></circle><circle cx="17.5" cy="6.5" r="1"></circle></svg>',
      YouTube: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 12s0-4-1-6c-.5-1-1.4-1.6-2.4-1.8C16.8 4 12 4 12 4s-4.8 0-6.6.2C4.4 4.4 3.5 5 3 6c-1 2-1 6-1 6s0 4 1 6c.5 1 1.4 1.6 2.4 1.8C7.2 20 12 20 12 20s4.8 0 6.6-.2c1-.2 1.9-.8 2.4-1.8 1-2 1-6 1-6Z"></path><path d="m10 9 5 3-5 3Z"></path></svg>',
      Facebook: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h3V4h-3c-3 0-5 2-5 5v3H6v4h3v6h4v-6h3l1-4h-4V9c0-.7.3-1 1-1Z"></path></svg>'
    };
    return icons[label] || "";
  }

  function socialLink(url, label) {
    if (!url) return "";
    return `<a class="social-link" href="${url}" target="_blank" rel="noopener noreferrer" aria-label="${label}">${socialIcon(label)}<span>${label}</span></a>`;
  }

  function buildHeader(config) {
    const fee = `${config.clinic.currency_symbol}${config.clinic.consultation_fee}`;
    const p1 = digits(config.contact.primary_mobile);
    const p2 = digits(config.contact.secondary_mobile);
    return `
      <a class="skip-link" href="#main-content">Skip to content</a>
      <div class="topbar">
        <div class="container topbar-inner">
          <span>Consultation fee: <strong data-global-fee>${fee}</strong></span>
          <span class="topbar-contact">Call/WhatsApp:
            <a href="tel:+91${p1}">${config.contact.primary_mobile}</a> ·
            <a href="tel:+91${p2}">${config.contact.secondary_mobile}</a>
          </span>
          <span class="topbar-social">
            ${socialLink(config.social.instagram, "Instagram")}
            ${socialLink(config.social.youtube, "YouTube")}
          </span>
        </div>
      </div>
      <header class="site-header">
        <div class="container nav-shell">
          <a class="brand" href="/" aria-label="${config.clinic.name} home">
            <span class="brand-mark" aria-hidden="true">A</span>
            <span><strong>${config.clinic.short_name}</strong><small>Dermatology · Laser · Aesthetic Care</small></span>
          </a>
          <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">
            <span></span><span></span><span></span><span class="sr-only">Open menu</span>
          </button>
          <nav id="primary-nav" class="primary-nav" aria-label="Primary">
            <a href="/">Home</a>
            <div class="nav-item has-menu">
              <button type="button" aria-expanded="false">About</button>
              <div class="dropdown compact">
                <a href="/about/">About the Clinic</a>
                <a href="/dr-cheena-langer/">Dr. Cheena Langer</a>
              </div>
            </div>
            <div class="nav-item has-menu mega">
              <button type="button" aria-expanded="false">Conditions</button>
              <div class="dropdown mega-menu">
                <div class="mega-intro">
                  <span class="eyebrow">Conditions</span>
                  <h2>Find care by concern</h2>
                  <p>Explore dermatologist-led information organised by the problem you are experiencing.</p>
                  <a class="text-link" href="/conditions/">View all conditions →</a>
                </div>
                <div class="mega-grid">${conditionsMenu}</div>
              </div>
            </div>
            <div class="nav-item has-menu mega">
              <button type="button" aria-expanded="false">Treatments</button>
              <div class="dropdown mega-menu">
                <div class="mega-intro">
                  <span class="eyebrow">Treatments</span>
                  <h2>Explore treatment options</h2>
                  <p>Suitability is decided after a medical assessment, not from a menu alone.</p>
                  <a class="text-link" href="/treatments/">View all treatments →</a>
                </div>
                <div class="mega-grid">${treatmentsMenu}</div>
              </div>
            </div>
            <div class="nav-item has-menu">
              <button type="button" aria-expanded="false">Locations</button>
              <div class="dropdown compact">
                <a href="/locations/karan-nagar/">Karan Nagar</a>
                <a href="/locations/paloura/">Paloura Chowk</a>
              </div>
            </div>
            <a href="/blog/">Blog</a>
            <a href="/contact/">Contact</a>
            <button class="theme-toggle" type="button" aria-label="Switch colour theme" title="Switch colour theme">
              <span class="theme-icon" aria-hidden="true">◐</span>
              <span class="theme-label">Theme</span>
            </button>
            <a class="button button-small" href="/book-appointment/">Book Appointment</a>
          </nav>
        </div>
      </header>
    `;
  }

  function buildFooter(config) {
    const p1 = digits(config.contact.primary_mobile);
    const p2 = digits(config.contact.secondary_mobile);
    const wa = digits(config.contact.whatsapp_mobile);
    return `
      <footer class="site-footer">
        <div class="container footer-grid">
          <div>
            <a class="brand brand-footer" href="/">
              <span class="brand-mark" aria-hidden="true">A</span>
              <span><strong>${config.clinic.short_name}</strong><small>Jammu</small></span>
            </a>
            <p>Dermatologist-led medical, laser and aesthetic skin care at Karan Nagar and Paloura Chowk.</p>
            <div class="social-row">
              ${socialLink(config.social.instagram, "Instagram")}
              ${socialLink(config.social.youtube, "YouTube")}
            </div>
            <p class="small">${config.clinic.emergency_note}</p>
          </div>
          <div>
            <h2>Quick links</h2>
            <ul>
              <li><a href="/dr-cheena-langer/">Dr. Cheena Langer</a></li>
              <li><a href="/conditions/">Conditions</a></li>
              <li><a href="/treatments/">Treatments</a></li>
              <li><a href="/blog/">Blog</a></li>
              <li><a href="/book-appointment/">Book appointment</a></li>
            </ul>
          </div>
          <div>
            <h2>Clinics & directions</h2>
            <ul>
              <li><a href="/locations/karan-nagar/">Karan Nagar clinic</a></li>
              <li><a href="${config.locations.karan_nagar.google_maps}" target="_blank" rel="noopener">Directions to Karan Nagar ↗</a></li>
              <li><a href="/locations/paloura/">Paloura clinic</a></li>
              <li><a href="${config.locations.paloura.google_maps}" target="_blank" rel="noopener">Directions to Paloura ↗</a></li>
            </ul>
          </div>
          <div>
            <h2>Contact</h2>
            <ul>
              <li><a href="tel:+91${p1}">${config.contact.primary_mobile}</a></li>
              <li><a href="tel:+91${p2}">${config.contact.secondary_mobile}</a></li>
              <li><a href="mailto:${config.clinic.email}">${config.clinic.email}</a></li>
            </ul>
          </div>
        </div>
        <div class="container footer-bottom">
          <p>© <span data-year></span> ${config.clinic.name}. All rights reserved.</p>
          <nav aria-label="Legal">
            <a href="/privacy-policy/">Privacy</a>
            <a href="/terms-and-conditions/">Terms</a>
            <a href="/medical-disclaimer/">Medical disclaimer</a>
          </nav>
        </div>
      </footer>
      <div class="mobile-actions" aria-label="Quick contact">
        <a href="tel:+91${p1}">Call</a>
        <a href="https://wa.me/91${wa}" target="_blank" rel="noopener">WhatsApp</a>
        <a href="/book-appointment/">Book</a>
      </div>
    `;
  }

  function replaceText(root, replacements) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) {
      const parent = walker.currentNode.parentElement;
      if (!parent || parent.closest("script,style,a,button,textarea,code,pre")) continue;
      nodes.push(walker.currentNode);
    }
    nodes.forEach(node => {
      let value = node.nodeValue;
      replacements.forEach(([pattern, replacement]) => {
        value = value.replace(pattern, replacement);
      });
      node.nodeValue = value;
    });
  }

  function applyGlobalFacts(config) {
    const fee = `${config.clinic.currency_symbol}${config.clinic.consultation_fee}`;
    const days = String(config.clinic.follow_up_days);
    const main = document.querySelector("main");
    if (main) {
      replaceText(main, [
        [/₹\s*500/g, fee],
        [/within\s+10\s+days/gi, `within ${days} days`],
        [/ten-day/gi, `${days}-day`],
        [/10-day/gi, `${days}-day`]
      ]);
    }

    document.querySelectorAll('a[href*="maps.app.goo.gl"]').forEach(link => {
      const text = (link.textContent || "").toLowerCase();
      const href = link.getAttribute("href") || "";
      if (text.includes("karan") || href.includes("pHCQ")) {
        link.href = config.locations.karan_nagar.google_maps;
      } else if (text.includes("paloura") || href.includes("kh4A")) {
        link.href = config.locations.paloura.google_maps;
      }
    });
  }

  function setupThemeToggle() {
    const toggle = document.querySelector(".theme-toggle");
    if (!toggle) return;

    const update = () => {
      const dark = document.documentElement.dataset.theme === "dark";
      toggle.setAttribute("aria-pressed", String(dark));
      toggle.querySelector(".theme-icon").textContent = dark ? "☀" : "☾";
      toggle.querySelector(".theme-label").textContent = dark ? "Light" : "Dark";
    };

    toggle.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("aastha-theme", next); } catch (_) {}
      update();
    });
    update();
  }

  function setupNavigation() {
    const navToggle = document.querySelector(".nav-toggle");
    const primaryNav = document.querySelector(".primary-nav");
    if (navToggle && primaryNav) {
      navToggle.addEventListener("click", () => {
        const open = navToggle.getAttribute("aria-expanded") === "true";
        navToggle.setAttribute("aria-expanded", String(!open));
        primaryNav.classList.toggle("is-open", !open);
        document.body.classList.toggle("nav-open", !open);
      });
    }

    document.querySelectorAll(".has-menu > button").forEach(button => {
      button.addEventListener("click", event => {
        const item = event.currentTarget.closest(".has-menu");
        const isOpen = button.getAttribute("aria-expanded") === "true";
        document.querySelectorAll(".has-menu.is-open").forEach(other => {
          if (other !== item) {
            other.classList.remove("is-open");
            other.querySelector(":scope > button")?.setAttribute("aria-expanded", "false");
          }
        });
        button.setAttribute("aria-expanded", String(!isOpen));
        item.classList.toggle("is-open", !isOpen);
      });
    });

    document.addEventListener("click", event => {
      if (!event.target.closest(".has-menu")) {
        document.querySelectorAll(".has-menu.is-open").forEach(item => {
          item.classList.remove("is-open");
          item.querySelector(":scope > button")?.setAttribute("aria-expanded", "false");
        });
      }
    });

    const currentPath = window.location.pathname.replace(/index\.html$/, "");
    document.querySelectorAll(".primary-nav a").forEach(link => {
      const href = new URL(link.href, window.location.origin).pathname;
      if (href === currentPath || (href !== "/" && currentPath.startsWith(href))) {
        link.classList.add("is-current");
      }
    });
  }

  function setupAccordions() {
    document.querySelectorAll("[data-accordion-button]").forEach(button => {
      button.addEventListener("click", () => {
        const panel = document.getElementById(button.getAttribute("aria-controls"));
        const open = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!open));
        if (panel) panel.hidden = open;
      });
    });
  }

  function setupAppointmentForm(config) {
    const form = document.querySelector("[data-appointment-form]");
    if (!form) return;
    const phoneInput = form.querySelector("[name='mobile']");
    phoneInput?.addEventListener("input", () => {
      phoneInput.value = phoneInput.value.replace(/\D/g, "").slice(0, 10);
    });

    form.addEventListener("submit", event => {
      event.preventDefault();
      const data = new FormData(form);
      const mobile = String(data.get("mobile") || "");
      if (!/^\d{10}$/.test(mobile)) {
        alert("Please enter a valid 10-digit mobile number.");
        phoneInput?.focus();
        return;
      }
      const message = [
        "Appointment request — Aastha Skin Centre",
        `Name: ${data.get("name")}`,
        `Mobile: ${mobile}`,
        `Branch: ${data.get("branch")}`,
        `Preferred date: ${data.get("preferred_date") || "Not specified"}`,
        `Preferred time: ${data.get("preferred_time") || "Not specified"}`,
        `Concern category: ${data.get("concern") || "Not specified"}`,
        "",
        config.clinic.appointment_confirmation_text
      ].join("\n");
      const wa = digits(config.contact.whatsapp_mobile);
      window.open(`https://wa.me/91${wa}?text=${encodeURIComponent(message)}`, "_blank", "noopener");
      const status = form.querySelector("[data-form-status]");
      if (status) {
        status.hidden = false;
        status.textContent = "WhatsApp has opened with your appointment request. Please send the message to complete your request.";
      }
    });
  }

  async function boot() {
    const config = await loadConfig();
    window.AASTHA_SITE_CONFIG = config;

    document.querySelectorAll("[data-site-header]").forEach(el => el.innerHTML = buildHeader(config));
    document.querySelectorAll("[data-site-footer]").forEach(el => el.innerHTML = buildFooter(config));
    document.querySelectorAll("[data-year]").forEach(el => el.textContent = new Date().getFullYear());

    applyGlobalFacts(config);
    setupThemeToggle();
    setupNavigation();
    setupAccordions();
    setupAppointmentForm(config);
  }

  boot();
})();
