(() => {
  const isAcne = document.body.dataset.pageSlug === "acne-treatment" || location.pathname === "/treatments/acne-treatment/";
  if (!isAcne) return;

  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const anchorFor = (heading, index) => {
    if (heading.id) return heading.id;
    const base = (heading.textContent || `section-${index + 1}`)
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || `section-${index + 1}`;
    let id = base;
    let suffix = 2;
    while (document.getElementById(id)) id = `${base}-${suffix++}`;
    heading.id = id;
    return id;
  };

  const moveClinicalResultIntoStory = () => {
    const heroGallery = qs(".page-hero-art > .clinical-results--hero");
    const prose = qs(".prose.article-stack");
    if (!heroGallery || !prose || heroGallery.dataset.v5Moved === "true") return;

    const sections = qsa(":scope > .article-section", prose);
    const trigger = sections.find(section =>
      qs("h2", section)?.textContent.trim().toLowerCase().startsWith("when should acne be examined")
    );
    if (!trigger) return;

    /* The route currently has one clinic-supplied composite result image. Keep
       it as a truthful result gallery — never manufacture a fake before/after
       slider from one image. Moving it out of the hero also restores the normal
       Wagtail hero image/illustration slot, matching the approved page design. */
    heroGallery.dataset.v5Moved = "true";
    heroGallery.classList.remove("clinical-results--hero");
    heroGallery.classList.add("v5-results-feature");

    const inner = qs(".clinical-results__inner", heroGallery);
    if (inner) {
      const existingLabel = qs(".clinical-results__hero-label", inner);
      if (existingLabel) existingLabel.remove();
      const header = document.createElement("header");
      header.className = "v5-results-header";
      header.innerHTML = `
        <p class="v5-results-kicker">Real results · real confidence</p>
        <h2>Acne treatment results</h2>
        <p>Clinic-supplied photography. Individual response, treatment plans and timelines vary.</p>
      `;
      inner.prepend(header);
    }
    trigger.insertAdjacentElement("afterend", heroGallery);
  };

  const sectionEntries = prose => {
    const selectors = [
      ":scope > .article-section > h2",
      ":scope > .v5-section-pair > .article-section > h2",
      ":scope > .faq-section > h2",
      ":scope > .article-cta > h2",
      ":scope > .article-cta > h3",
    ];
    const headings = qsa(selectors.join(","), prose).filter(heading => heading.textContent.trim());
    const seen = new Set();
    return headings.filter(heading => {
      const text = heading.textContent.trim();
      if (seen.has(text)) return false;
      seen.add(text);
      return true;
    });
  };

  const buildRail = () => {
    const layout = qs(".content-layout");
    const prose = qs(".prose.article-stack", layout || document);
    if (!layout || !prose) return;

    qsa(".v5-page-rail", layout).forEach(node => node.remove());
    const headings = sectionEntries(prose);
    if (!headings.length) return;

    const rail = document.createElement("nav");
    rail.className = "v5-page-rail";
    rail.setAttribute("aria-label", "On this page");
    rail.innerHTML = '<p class="v5-page-rail-title">On this page</p>';
    const list = document.createElement("ol");

    const entries = headings.map((heading, index) => {
      const id = anchorFor(heading, index);
      const li = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${id}`;
      link.textContent = heading.textContent.trim().replace(/\s+/g, " ");
      link.addEventListener("click", event => {
        event.preventDefault();
        heading.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
        history.replaceState(null, "", `#${id}`);
      });
      li.append(link);
      list.append(li);
      return { heading, li };
    });
    rail.append(list);

    const help = document.createElement("div");
    help.className = "v5-rail-help";
    help.innerHTML = '<strong>Still have questions?</strong><p>Talk to the clinic team about a consultation.</p>';
    const whatsapp = document.createElement("a");
    whatsapp.href = document.body.dataset.whatsappUrl || "#";
    whatsapp.textContent = "WhatsApp us →";
    help.append(whatsapp);
    rail.append(help);

    layout.prepend(rail);

    if (!("IntersectionObserver" in window)) {
      entries[0]?.li.classList.add("v5-active");
      return;
    }
    const observer = new IntersectionObserver(items => {
      const visible = items
        .filter(item => item.isIntersecting)
        .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))[0];
      if (!visible) return;
      entries.forEach(entry => entry.li.classList.toggle("v5-active", entry.heading === visible.target));
    }, { rootMargin: "-18% 0px -66% 0px", threshold: [0, .1, .5] });
    entries.forEach(entry => observer.observe(entry.heading));
    entries[0]?.li.classList.add("v5-active");
  };

  const pairSignsAndCauses = () => {
    const prose = qs(".prose.article-stack");
    if (!prose || qs(".v5-section-pair", prose)) return;
    const sections = qsa(":scope > .article-section", prose);
    const signs = sections.find(section => qs("h2", section)?.textContent.trim().toLowerCase() === "common signs of acne");
    const causes = sections.find(section => qs("h2", section)?.textContent.trim().toLowerCase() === "what causes acne?");
    if (!signs || !causes || signs.nextElementSibling !== causes) return;
    const wrapper = document.createElement("div");
    wrapper.className = "v5-section-pair";
    signs.before(wrapper);
    wrapper.append(signs, causes);
  };

  const enrichSidebar = () => {
    const card = qs(".care-sidebar-card");
    if (!card || qs(".v5-sidebar-trust", card)) return;
    const trust = document.createElement("div");
    trust.className = "v5-sidebar-trust";
    [
      "Dermatologist-led assessment",
      "Personalised treatment planning",
      "Evidence-based medical and aesthetic care",
      "Clear counselling and aftercare",
    ].forEach(text => {
      const row = document.createElement("div");
      row.textContent = text;
      trust.append(row);
    });
    card.append(trust);
  };

  const boot = () => {
    pairSignsAndCauses();
    moveClinicalResultIntoStory();
    buildRail();
    enrichSidebar();
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
