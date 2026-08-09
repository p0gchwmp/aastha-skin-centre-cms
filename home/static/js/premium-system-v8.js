(() => {
  "use strict";

  const body = document.body;
  const root = document.documentElement;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const qsa = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const pageType = body.dataset.pageType || "";
  const isArticlePage = [
    "treatmentpage",
    "conditionpage",
    "blogpage",
    "doctorpage",
    "clinicpage",
  ].includes(pageType);

  const uniqueId = (heading, index, used) => {
    let base = heading.id || (heading.textContent || `section-${index + 1}`)
      .trim()
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || `section-${index + 1}`;
    let id = base;
    let suffix = 2;
    while (used.has(id) || (document.getElementById(id) && document.getElementById(id) !== heading)) {
      id = `${base}-${suffix}`;
      suffix += 1;
    }
    used.add(id);
    heading.id = id;
    return id;
  };

  const removeLegacyChrome = () => {
    qsa(".luxury-proof-strip, .v5-proof-strip").forEach(node => node.remove());

    /* Generic trust strips repeated the same claims across the directory and
       article templates. Doctor credentials and clinic-hour summaries remain
       because they carry page-specific information. */
    if (!["doctorpage", "clinicpage"].includes(pageType)) {
      qsa("main > .premium-summary-strip").forEach(node => node.remove());
    }

    if (["treatmentpage", "conditionpage", "doctorpage", "clinicpage"].includes(pageType)) {
      qsa(".article-cta").forEach(node => node.remove());
    }
  };

  const setupPageRail = () => {
    if (!isArticlePage) return;
    const layout = document.querySelector(".content-layout");
    const article = layout?.querySelector(":scope > .article-stack, :scope > article.prose");
    if (!layout || !article) return;

    qsa(".release-toc, .article-toc, .v5-page-rail, .luxury-page-rail, .v8-page-rail, .v8-mobile-toc", layout)
      .forEach(node => node.remove());
    layout.classList.remove(
      "luxury-clinical-grid-ready",
      "luxury-clinical-grid-fallback",
      "luxury-clinical-grid-approved",
    );
    layout.classList.add("v8-content-layout");
    article.classList.add("v8-article-content");
    layout.querySelector(":scope > .care-sidebar")?.classList.add("v8-care-sidebar");

    const headings = qsa(".article-section > h2", article)
      .filter(heading => !heading.closest(".article-cta") && heading.textContent.trim());
    if (headings.length < 2) return;

    const used = new Set();
    const entries = headings.map((heading, index) => ({
      heading,
      id: uniqueId(heading, index, used),
      label: heading.textContent.trim().replace(/\s+/g, " "),
    }));

    const makeList = className => {
      const list = document.createElement("ol");
      list.className = className;
      entries.forEach(entry => {
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#${entry.id}`;
        link.textContent = entry.label;
        link.addEventListener("click", event => {
          event.preventDefault();
          entry.heading.scrollIntoView({
            behavior: reduceMotion.matches ? "auto" : "smooth",
            block: "start",
          });
          history.replaceState(null, "", `#${entry.id}`);
        });
        item.append(link);
        list.append(item);
      });
      return list;
    };

    const rail = document.createElement("nav");
    rail.className = "v8-page-rail";
    rail.setAttribute("aria-label", "On this page");
    const railTitle = document.createElement("p");
    railTitle.className = "v8-page-rail__title";
    railTitle.textContent = "On this page";
    rail.append(railTitle, makeList("v8-page-rail__list"));
    layout.insertBefore(rail, article);

    const mobile = document.createElement("details");
    mobile.className = "v8-mobile-toc";
    const summary = document.createElement("summary");
    summary.textContent = "On this page";
    mobile.append(summary, makeList("v8-mobile-toc__list"));
    article.prepend(mobile);

    const links = qsa('a[href^="#"]', rail);
    const activate = id => {
      links.forEach(link => {
        const active = link.getAttribute("href") === `#${id}`;
        link.parentElement?.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    };
    activate(entries[0].id);

    if (!("IntersectionObserver" in window)) return;
    const visible = new Map();
    const observer = new IntersectionObserver(changes => {
      changes.forEach(change => {
        if (change.isIntersecting) visible.set(change.target.id, change.boundingClientRect.top);
        else visible.delete(change.target.id);
      });
      const next = [...visible.entries()].sort((a, b) => Math.abs(a[1]) - Math.abs(b[1]))[0];
      if (next) activate(next[0]);
    }, { rootMargin: "-18% 0px -66% 0px", threshold: [0, .08, .4] });
    entries.forEach(entry => observer.observe(entry.heading));
  };

  const setupNumberedFeatures = () => {
    qsa(".doctor-points, .clean-list--three").forEach(list => {
      list.classList.add("v8-numbered-features");
      qsa(":scope > li", list).forEach((item, index) => {
        if (!item.querySelector(":scope > .v8-feature-index")) {
          const marker = document.createElement("span");
          marker.className = "v8-feature-index";
          marker.setAttribute("aria-hidden", "true");
          marker.textContent = String(index + 1).padStart(2, "0");
          item.prepend(marker);
        }
      });
    });
  };

  const setupAccordions = () => {
    qsa("details").forEach(original => {
      let details = original;

      /* V5 attached a second click interceptor to these native disclosures.
         Replace only that already-enhanced node so one component owns the
         open/close lifecycle and a click cannot immediately toggle twice. */
      if (details.dataset.v5Accordion === "true") {
        const cleanDetails = details.cloneNode(true);
        delete cleanDetails.dataset.v5Accordion;
        delete cleanDetails.dataset.v8Accordion;
        cleanDetails.classList.remove("v5-accordion-animated");
        details.replaceWith(cleanDetails);
        details = cleanDetails;
      }

      const summary = details.querySelector(":scope > summary");
      if (!summary || details.dataset.v8Accordion === "true") return;
      details.dataset.v8Accordion = "true";
      details.classList.add("v8-accordion");
      details.style.setProperty("border-bottom", "1px solid var(--v6-line)", "important");

      summary.addEventListener("click", event => {
        if (reduceMotion.matches || typeof details.animate !== "function") return;
        event.preventDefault();
        const startHeight = details.offsetHeight;
        const wasOpen = details.open;
        if (!wasOpen) details.open = true;
        const endHeight = wasOpen ? summary.offsetHeight : details.scrollHeight;
        details.style.overflow = "hidden";
        const animation = details.animate(
          { height: [`${startHeight}px`, `${endHeight}px`] },
          { duration: 260, easing: "cubic-bezier(.22,1,.36,1)" },
        );
        animation.onfinish = () => {
          if (wasOpen) details.open = false;
          details.style.removeProperty("overflow");
          details.style.removeProperty("height");
        };
        animation.oncancel = animation.onfinish;
      });
    });
  };

  const setupClinicalResults = () => {
    qsa(".clinical-results__hero-label").forEach(label => {
      label.style.setProperty("background", "transparent", "important");
      label.style.setProperty("color", "var(--v6-gold-soft)", "important");
      label.style.setProperty("border", "0", "important");
      label.style.setProperty("border-bottom", "1px solid var(--v6-line-strong)", "important");
    });
  };

  const revealAll = () => {
    qsa(".v8-reveal").forEach(node => node.classList.add("is-visible"));
    root.classList.remove("v8-motion-ready");
  };

  const setupReveals = () => {
    const selector = [
      ".section-heading",
      ".value-card",
      ".hub-category",
      ".concern-card",
      ".treatment-card",
      ".why-card",
      ".location-pro-card",
      ".clinic-choice-card",
      ".article-section > h2",
      ".home-cta-grid",
    ].join(",");
    const targets = qsa(selector).filter((node, index, all) => all.indexOf(node) === index);
    if (!targets.length || reduceMotion.matches || !("IntersectionObserver" in window)) {
      targets.forEach(node => node.classList.add("v8-reveal", "is-visible"));
      return;
    }
    root.classList.add("v8-motion-ready");
    targets.forEach((node, index) => {
      node.classList.add("v8-reveal");
      node.style.setProperty("--v8-reveal-delay", `${Math.min(index % 4, 3) * 55}ms`);
    });
    const observer = new IntersectionObserver(changes => {
      changes.forEach(change => {
        if (!change.isIntersecting) return;
        change.target.classList.add("is-visible");
        observer.unobserve(change.target);
      });
    }, { threshold: .06, rootMargin: "0px 0px -6% 0px" });
    targets.forEach(node => observer.observe(node));
    window.setTimeout(revealAll, 1800);
  };

  const normaliseLivePunctuation = (scope = document.body) => {
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue?.includes("—") && !node.nodeValue?.includes("â€”")) {
          return NodeFilter.FILTER_REJECT;
        }
        if (node.parentElement?.closest("script, style, code, pre")) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      node.nodeValue = node.nodeValue.replace(/â€”/g, "—").replace(/\s*—\s*/g, ", ");
    });
  };

  const setupPrintDetails = () => {
    window.addEventListener("beforeprint", () => {
      qsa("details").forEach(details => {
        details.dataset.v8PrintWasOpen = details.open ? "true" : "false";
        const mirror = document.createElement("div");
        mirror.className = "v8-print-details";
        if (details.classList.contains("v8-mobile-toc")) {
          mirror.classList.add("v8-print-toc");
        }
        const summary = details.querySelector(":scope > summary");
        if (summary) {
          const title = document.createElement("p");
          title.className = "v8-print-details__summary";
          title.textContent = summary.textContent.trim();
          mirror.append(title);
        }
        [...details.children]
          .filter(child => child !== summary)
          .forEach(child => mirror.append(child.cloneNode(true)));
        details.before(mirror);
        details.classList.add("v8-print-original");
      });
    });
    window.addEventListener("afterprint", () => {
      qsa("details[data-v8-print-was-open]").forEach(details => {
        details.open = details.dataset.v8PrintWasOpen === "true";
        details.classList.remove("v8-print-original");
        delete details.dataset.v8PrintWasOpen;
      });
      qsa(".v8-print-details").forEach(mirror => mirror.remove());
    });
  };

  const boot = () => {
    removeLegacyChrome();
    setupPageRail();
    setupNumberedFeatures();
    setupAccordions();
    setupClinicalResults();
    setupReveals();
    setupPrintDetails();
    normaliseLivePunctuation();
    body.classList.add("v8-ready");
  };

  reduceMotion.addEventListener?.("change", event => {
    if (event.matches) revealAll();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", () => {
    window.setTimeout(() => {
      removeLegacyChrome();
      setupPageRail();
      setupAccordions();
      setupClinicalResults();
      normaliseLivePunctuation();
    }, 180);
  }, { once: true });
})();
