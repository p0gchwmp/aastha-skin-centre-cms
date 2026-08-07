(() => {
  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];

  const slug = document.body.dataset.pageSlug || "";
  const isHome = document.body.classList.contains("cms-home-page");
  const isAcne = slug === "acne-treatment" || location.pathname === "/treatments/acne-treatment/";
  if (isAcne && !document.body.dataset.pageSlug) document.body.dataset.pageSlug = "acne-treatment";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const setupHeader = () => {
    const header = qs(".site-header");
    if (!header) return;
    const sync = () => header.classList.toggle("v5-header-compact", window.scrollY > 24);
    sync();
    window.addEventListener("scroll", sync, { passive: true });
  };

  const makeButton = (href, label, secondary = false) => {
    const a = document.createElement("a");
    a.className = `button${secondary ? " button-secondary" : ""}`;
    a.href = href;
    a.textContent = label;
    return a;
  };

  const setupHomeHeroSide = () => {
    if (!isHome) return;
    const grid = qs(".home-hero-grid");
    if (!grid || qs(".v5-hero-side", grid)) return;

    const whatsapp = document.body.dataset.whatsappUrl || "#";
    const side = document.createElement("aside");
    side.className = "v5-hero-side";
    side.setAttribute("aria-label", "Consultation options");

    const doctorCard = document.createElement("article");
    doctorCard.className = "v5-hero-card";
    doctorCard.innerHTML = `
      <p class="v5-card-kicker">Consult with</p>
      <h2>Dr. Cheena Langer</h2>
      <p>MBBS, MD Dermatology · Dermatologist-led skin, hair and aesthetic care.</p>
    `;
    doctorCard.append(makeButton("/doctor/dr-cheena-langer/", "View doctor profile"));
    const doctorLink = document.createElement("a");
    doctorLink.className = "v5-text-link";
    doctorLink.href = "/doctor/dr-cheena-langer/";
    doctorLink.textContent = "Know more about Dr. Cheena →";
    doctorCard.append(doctorLink);

    const readyCard = document.createElement("article");
    readyCard.className = "v5-hero-card v5-hero-card--accent";
    readyCard.innerHTML = `
      <p class="v5-card-kicker">Ready to begin?</p>
      <h3>Book a personalised consultation.</h3>
      <p>Choose the clinic and request an appointment at a convenient time.</p>
    `;
    readyCard.append(makeButton("/book-appointment/", "Book now"));
    readyCard.append(makeButton(whatsapp, "WhatsApp us", true));

    side.append(doctorCard, readyCard);
    grid.append(side);
  };

  const setupTreatmentCarousel = () => {
    if (!isHome) return;
    const grid = qs(".treatment-grid");
    if (!grid || grid.dataset.v5Carousel === "true") return;
    const cards = qsa(".treatment-card", grid);
    if (cards.length < 2) return;
    grid.dataset.v5Carousel = "true";

    const section = grid.closest("section") || grid.parentElement;
    const heading = qs(".section-heading", section);
    if (!heading) return;

    const controls = document.createElement("div");
    controls.className = "v5-treatment-controls";
    controls.setAttribute("aria-label", "Treatment carousel controls");

    const prev = document.createElement("button");
    prev.type = "button";
    prev.setAttribute("aria-label", "Previous treatments");
    prev.textContent = "←";

    const progress = document.createElement("span");
    progress.className = "v5-treatment-progress";

    const next = document.createElement("button");
    next.type = "button";
    next.setAttribute("aria-label", "Next treatments");
    next.textContent = "→";

    controls.append(prev, progress, next);
    heading.append(controls);

    const cardWidth = () => {
      const card = cards[0];
      const styles = getComputedStyle(grid);
      const gap = parseFloat(styles.columnGap || styles.gap || "0");
      return card.getBoundingClientRect().width + gap;
    };

    const update = () => {
      const step = Math.max(1, cardWidth());
      const index = Math.min(cards.length - 1, Math.max(0, Math.round(grid.scrollLeft / step)));
      progress.textContent = `${index + 1} / ${cards.length}`;
      prev.disabled = index === 0;
      next.disabled = index >= cards.length - 1;
    };

    prev.addEventListener("click", () => grid.scrollBy({ left: -cardWidth(), behavior: reducedMotion ? "auto" : "smooth" }));
    next.addEventListener("click", () => grid.scrollBy({ left: cardWidth(), behavior: reducedMotion ? "auto" : "smooth" }));
    grid.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  };

  const safeAnchor = (heading, index) => {
    if (heading.id) return heading.id;
    const base = (heading.textContent || `section-${index + 1}`)
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
    heading.id = base || `section-${index + 1}`;
    return heading.id;
  };

  const setupAcneProof = () => {
    if (!isAcne || qs(".v5-proof-strip")) return;
    const hero = qs(".page-hero");
    if (!hero) return;
    const labels = [
      "Dermatologist-led care",
      "Evidence-based approach",
      "Personalised treatment plan",
      "Clear counselling & aftercare",
      "Two Jammu clinics",
    ];
    const strip = document.createElement("div");
    strip.className = "v5-proof-strip";
    strip.setAttribute("aria-label", "Consultation highlights");
    labels.forEach(label => {
      const item = document.createElement("div");
      item.className = "v5-proof-item";
      item.textContent = label;
      strip.append(item);
    });
    hero.insertAdjacentElement("afterend", strip);
  };

  const setupAcneRail = () => {
    if (!isAcne) return;
    const layout = qs(".content-layout");
    const prose = qs(".prose", layout || document);
    if (!layout || !prose || qs(".v5-page-rail", layout)) return;

    const headings = qsa(":scope > h2", prose).filter(h => (h.textContent || "").trim());
    if (!headings.length) return;

    const rail = document.createElement("nav");
    rail.className = "v5-page-rail";
    rail.setAttribute("aria-label", "On this page");
    rail.innerHTML = '<p class="v5-page-rail-title">On this page</p>';

    const list = document.createElement("ol");
    const entries = headings.map((heading, index) => {
      const id = safeAnchor(heading, index);
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = `#${id}`;
      a.textContent = heading.textContent.trim().replace(/\s+/g, " ");
      a.addEventListener("click", event => {
        event.preventDefault();
        heading.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
        history.replaceState(null, "", `#${id}`);
      });
      li.append(a);
      list.append(li);
      return { heading, li };
    });
    rail.append(list);

    const help = document.createElement("div");
    help.className = "v5-rail-help";
    help.innerHTML = '<strong>Still have questions?</strong><p>Speak with the clinic team about consultation availability.</p>';
    const whatsapp = document.createElement("a");
    whatsapp.href = document.body.dataset.whatsappUrl || "#";
    whatsapp.textContent = "WhatsApp us →";
    help.append(whatsapp);
    rail.append(help);

    layout.prepend(rail);

    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(items => {
      const visible = items
        .filter(item => item.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      entries.forEach(entry => entry.li.classList.toggle("v5-active", entry.heading === visible.target));
    }, { rootMargin: "-18% 0px -68% 0px", threshold: [0, .1, .5] });
    entries.forEach(entry => observer.observe(entry.heading));
    if (entries[0]) entries[0].li.classList.add("v5-active");
  };

  const setupSidebarTrust = () => {
    if (!isAcne) return;
    const card = qs(".sidebar-card");
    if (!card || qs(".v5-sidebar-trust", card)) return;
    const trust = document.createElement("div");
    trust.className = "v5-sidebar-trust";
    [
      "Dermatologist-led consultation",
      "Personalised plan based on assessment",
      "Clear treatment guidance and aftercare",
      "Clinic choice in Jammu",
    ].forEach(text => {
      const row = document.createElement("div");
      row.textContent = text;
      trust.append(row);
    });
    card.append(trust);
  };

  const setupReadingProgress = () => {
    if (!isAcne || qs(".v5-reading-progress")) return;
    const progress = document.createElement("div");
    progress.className = "v5-reading-progress";
    progress.setAttribute("aria-hidden", "true");
    progress.innerHTML = "<span></span>";
    document.body.append(progress);
    const bar = qs("span", progress);
    const sync = () => {
      const main = qs("#main-content") || document.documentElement;
      const rect = main.getBoundingClientRect();
      const start = window.scrollY + rect.top;
      const end = start + main.scrollHeight - innerHeight;
      const ratio = end <= start ? 0 : Math.min(1, Math.max(0, (window.scrollY - start) / (end - start)));
      progress.style.setProperty("--v5-progress", `${ratio * 100}%`);
      if (bar) bar.style.height = `${ratio * 100}%`;
    };
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
  };

  const setupComparisons = () => {
    qsa(".cms-comparison-grid").forEach(grid => {
      if (grid.dataset.v5Enhanced === "true") return;
      const figures = qsa(":scope > figure", grid);
      if (figures.length !== 2 || !qs("img", figures[0]) || !qs("img", figures[1])) return;
      grid.dataset.v5Enhanced = "true";
      grid.classList.add("v5-comparison-enhanced");
      grid.style.setProperty("--v5-compare", "50%");

      const handle = document.createElement("span");
      handle.className = "v5-comparison-handle";
      handle.setAttribute("aria-hidden", "true");

      const range = document.createElement("input");
      range.className = "v5-comparison-range";
      range.type = "range";
      range.min = "0";
      range.max = "100";
      range.value = "50";
      range.step = "1";
      range.setAttribute("aria-label", "Compare before and after photographs");
      range.addEventListener("input", () => grid.style.setProperty("--v5-compare", `${range.value}%`));
      grid.append(handle, range);
    });
  };

  const setupReveal = () => {
    if (reducedMotion) return;
    const selectors = isHome
      ? [
          ".home-hero-copy",
          ".home-hero-media",
          ".v5-hero-card",
          ".trust-item",
          ".home-section .section-heading",
          ".concern-card",
          ".doctor-feature > *",
          ".treatment-card",
          ".why-card",
          ".location-pro-card",
        ]
      : isAcne
        ? [
            ".page-hero-copy",
            ".page-hero-art",
            ".v5-proof-strip",
            ".prose > h2",
            ".clinical-results",
            ".location-pro-card",
            ".article-cta",
          ]
        : [];
    const targets = qsa(selectors.join(",")).filter(Boolean);
    if (!targets.length) return;

    targets.forEach((node, index) => {
      node.classList.add("v5-reveal");
      node.style.transitionDelay = `${Math.min(index % 4, 3) * 45}ms`;
    });
    qsa(".home-hero-media, .doctor-visual, .page-hero-art").forEach(node => node.classList.add("v5-image-reveal"));

    if (!("IntersectionObserver" in window)) {
      targets.forEach(node => node.classList.add("v5-visible"));
      qsa(".v5-image-reveal").forEach(node => node.classList.add("v5-visible"));
      return;
    }
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v5-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -7% 0px", threshold: .05 });
    targets.forEach(node => observer.observe(node));
    qsa(".v5-image-reveal").forEach(node => observer.observe(node));
  };

  const setupDetails = () => {
    qsa("details").forEach(details => {
      details.addEventListener("toggle", () => details.classList.toggle("v5-open", details.open));
    });
  };

  const boot = () => {
    setupHeader();
    setupHomeHeroSide();
    setupTreatmentCarousel();
    setupAcneProof();
    setupAcneRail();
    setupSidebarTrust();
    setupReadingProgress();
    setupComparisons();
    setupDetails();
    setupReveal();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
