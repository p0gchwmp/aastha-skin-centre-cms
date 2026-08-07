(() => {
  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const pageType = document.body.dataset.pageType || "";
  const isClinical = pageType === "treatmentpage" || pageType === "conditionpage";
  const isHome = document.body.classList.contains("cms-home-page");

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

  const classifyImages = () => {
    qsa(".page-hero-art img, .cms-split-media img, .journal-card > img, .cms-comparison-grid img").forEach(image => {
      const src = (image.currentSrc || image.getAttribute("src") || "").toLowerCase();
      const real = src.includes("/media/") && !src.endsWith(".svg") && !src.includes("professional/");
      image.classList.toggle("v3-real-photo", real);
    });
  };

  const setupClinicalProof = () => {
    if (!isClinical) return;
    if (qs(".luxury-proof-strip") || qs(".v5-proof-strip")) return;
    const hero = qs(".page-hero");
    if (!hero) return;

    const labels = pageType === "conditionpage"
      ? [
          "Dermatologist-led assessment",
          "Evidence-based guidance",
          "Personalised care plan",
          "Clear counselling & follow-up",
          "Two Jammu clinics",
        ]
      : [
          "Dermatologist-led care",
          "Evidence-based approach",
          "Personalised treatment plan",
          "Clear counselling & aftercare",
          "Two Jammu clinics",
        ];

    const strip = document.createElement("div");
    strip.className = "luxury-proof-strip";
    strip.setAttribute("aria-label", "Care highlights");
    labels.forEach(label => {
      const item = document.createElement("div");
      item.className = "luxury-proof-item";
      item.textContent = label;
      strip.append(item);
    });
    hero.insertAdjacentElement("afterend", strip);
  };

  const setupClinicalRail = () => {
    if (!isClinical) return;
    const layout = qs(".content-layout");
    const prose = qs(".prose", layout || document);
    if (!layout || !prose || qs(".luxury-page-rail", layout) || qs(".v5-page-rail", layout)) return;

    const headings = qsa(":scope > h2", prose).filter(node => (node.textContent || "").trim());
    if (headings.length < 2) return;

    const rail = document.createElement("nav");
    rail.className = "luxury-page-rail";
    rail.setAttribute("aria-label", "On this page");

    const title = document.createElement("p");
    title.className = "luxury-page-rail-title";
    title.textContent = "On this page";
    rail.append(title);

    const list = document.createElement("ol");
    const entries = headings.map((heading, index) => {
      const id = safeAnchor(heading, index);
      const li = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${id}`;
      link.textContent = heading.textContent.trim().replace(/\s+/g, " ");
      link.addEventListener("click", event => {
        event.preventDefault();
        heading.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
        history.replaceState(null, "", `#${id}`);
      });
      li.append(link);
      list.append(li);
      return { heading, li };
    });
    rail.append(list);

    const help = document.createElement("div");
    help.className = "luxury-rail-help";
    help.innerHTML = "<strong>Still have questions?</strong><p>Speak with the clinic about consultation availability and the next appropriate step.</p>";
    const whatsapp = document.createElement("a");
    whatsapp.href = document.body.dataset.whatsappUrl || "#";
    whatsapp.textContent = "WhatsApp the clinic →";
    help.append(whatsapp);
    rail.append(help);

    layout.prepend(rail);

    if (!("IntersectionObserver" in window)) {
      entries[0]?.li.classList.add("luxury-active");
      return;
    }
    const observer = new IntersectionObserver(items => {
      const visible = items
        .filter(item => item.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      entries.forEach(entry => entry.li.classList.toggle("luxury-active", entry.heading === visible.target));
    }, { rootMargin: "-18% 0px -68% 0px", threshold: [0, .1, .5] });
    entries.forEach(entry => observer.observe(entry.heading));
    entries[0]?.li.classList.add("luxury-active");
  };

  const setupSidebarTrust = () => {
    if (!isClinical) return;
    const card = qs(".care-sidebar-card") || qs(".sidebar-card");
    if (!card || qs(".luxury-sidebar-trust", card) || qs(".v5-sidebar-trust", card)) return;
    const trust = document.createElement("div");
    trust.className = "luxury-sidebar-trust";
    [
      "Dermatologist-led consultation",
      "Personalised plan after assessment",
      "Clear guidance and aftercare",
      "Clinic choice in Jammu",
    ].forEach(text => {
      const row = document.createElement("div");
      row.textContent = text;
      trust.append(row);
    });
    card.append(trust);
  };

  const setupReadingProgress = () => {
    if (!isClinical || qs(".luxury-reading-progress") || qs(".v5-reading-progress")) return;
    const main = qs("#main-content");
    if (!main) return;

    const progress = document.createElement("div");
    progress.className = "luxury-reading-progress";
    progress.setAttribute("aria-hidden", "true");
    progress.innerHTML = "<span></span>";
    document.body.append(progress);
    const bar = qs("span", progress);

    const sync = () => {
      const rect = main.getBoundingClientRect();
      const start = window.scrollY + rect.top;
      const end = start + main.scrollHeight - window.innerHeight;
      const ratio = end <= start ? 0 : Math.min(1, Math.max(0, (window.scrollY - start) / (end - start)));
      progress.style.setProperty("--luxury-progress", `${ratio * 100}%`);
      if (bar) bar.style.height = `${ratio * 100}%`;
    };
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
  };

  const setupReveal = () => {
    const selectors = [
      ".page-hero-copy",
      ".page-hero-art",
      ".journal-section .section-heading",
      ".journal-card",
      ".cms-split-section",
      ".cms-comparison-section",
      ".cms-card-grid",
      ".cms-feature-grid",
      ".cms-gallery-section",
      ".cms-faq",
      ".cms-accordion",
      ".article-cta",
    ];
    if (isClinical) selectors.push(".prose > h2", ".clinical-results", ".location-pro-card");
    if (isHome) return; // Home has its approved dedicated choreography.

    const targets = qsa(selectors.join(",")).filter((node, index, list) => list.indexOf(node) === index);
    targets.forEach((node, index) => {
      let direction = "up";
      if (node.matches(".page-hero-art")) direction = "right";
      else if (node.matches(".journal-card")) direction = index % 2 ? "right" : "left";
      else if (node.matches(".cms-split-section")) {
        direction = node.querySelector(".cms-split--media-left") ? "right" : "left";
      }
      node.dataset.luxuryReveal = direction;
      node.style.setProperty("--luxury-delay", `${Math.min(index % 4, 3) * 55}ms`);
    });

    const images = qsa(".page-hero-art img, .cms-split-media img, .journal-card > img");
    images.forEach((image, index) => {
      image.classList.add("luxury-image-reveal");
      if (index % 2) image.classList.add("luxury-image-reveal--right");
      image.style.setProperty("--luxury-delay", `${70 + (index % 3) * 55}ms`);
    });

    if (reduceMotion || !("IntersectionObserver" in window)) {
      targets.forEach(node => node.classList.add("luxury-visible"));
      images.forEach(node => node.classList.add("luxury-visible"));
      return;
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("luxury-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: .06, rootMargin: "0px 0px -7% 0px" });
    targets.forEach(node => observer.observe(node));
    images.forEach(node => observer.observe(node));
  };

  const setupDirectoryKeyboard = () => {
    qsa(".journal-card").forEach(card => {
      card.addEventListener("focus", () => card.classList.add("luxury-focus"));
      card.addEventListener("blur", () => card.classList.remove("luxury-focus"));
    });
  };

  const setupSplitRhythm = () => {
    qsa(".cms-split-section").forEach((section, index) => {
      section.dataset.luxurySplitIndex = String(index + 1);
      const split = qs(".cms-split", section);
      if (!split) return;
      /* If editors leave all media on one side, preserve their explicit choice.
         Otherwise this class lets CSS/animation give adjacent sections a natural
         alternating editorial rhythm without rewriting CMS content. */
      section.classList.toggle("luxury-split-even", index % 2 === 1);
    });
  };

  const boot = () => {
    classifyImages();
    setupClinicalProof();
    setupClinicalRail();
    setupSidebarTrust();
    setupReadingProgress();
    setupSplitRhythm();
    setupReveal();
    setupDirectoryKeyboard();
    window.setTimeout(classifyImages, 900);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
