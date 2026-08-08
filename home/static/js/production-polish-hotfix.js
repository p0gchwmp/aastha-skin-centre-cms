(() => {
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const isHome = () => document.body.classList.contains("cms-home-page");
  const isClinical = () => ["treatmentpage", "conditionpage"].includes(document.body.dataset.pageType || "");
  const isAcne = () => document.body.dataset.pageSlug === "acne-treatment" || location.pathname === "/treatments/acne-treatment/";

  const installRuntimePolish = () => {
    if (document.getElementById("production-runtime-polish")) return;
    const style = document.createElement("style");
    style.id = "production-runtime-polish";
    style.textContent = `
      body.cms-home-page { --v5-hybrid-shift: 0px !important; }
      body.cms-home-page .v5-home-rail { display: none !important; }
      body.cms-home-page .treatment-grid > .treatment-card:nth-child(n) {
        margin-block: 0 !important;
        translate: none !important;
        transform: none !important;
        align-self: stretch !important;
      }
      body.cms-home-page :is(.concern-card,.treatment-card,.why-card,.location-pro-card) p {
        font-size: 1.04rem !important;
        line-height: 1.6 !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) .release-toc {
        display: none !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.luxury-page-rail,.v5-page-rail) ol::before,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.luxury-page-rail,.v5-page-rail) li::before,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) article.prose :is(ul,ol) > li::before {
        display: none !important;
        content: none !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.luxury-page-rail,.v5-page-rail) li,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) article.prose :is(ul,ol) > li {
        padding-left: 0 !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.luxury-page-rail,.v5-page-rail) a {
        font-size: .82rem !important;
        line-height: 1.42 !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) .prose p,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) .prose li {
        font-size: 1.06rem !important;
        line-height: 1.62 !important;
      }
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.sidebar-card,.care-sidebar-card) p,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.sidebar-card,.care-sidebar-card) li,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.sidebar-card,.care-sidebar-card) dt,
      body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) :is(.sidebar-card,.care-sidebar-card) dd {
        font-size: .94rem !important;
      }
      @media (max-width: 760px) {
        body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) .prose p,
        body.release-v24:is([data-page-type="treatmentpage"],[data-page-type="conditionpage"]) .prose li,
        body.cms-home-page :is(.concern-card,.treatment-card,.why-card,.location-pro-card,.v5-hero-card) p {
          font-size: 1.08rem !important;
          line-height: 1.62 !important;
        }
      }
    `;
    document.head.append(style);
  };

  const fixDoctorLinks = (root = document) => {
    qsa('a[href="/doctor/dr-cheena-langer/"]', root).forEach(link => {
      link.href = "/dr-cheena-langer/";
    });
  };

  const unlockContent = (root = document) => {
    const selector = [
      "[data-v5-motion]",
      "[data-luxury-reveal]",
      ".v5-heading-reveal",
      ".v5-mask-reveal",
      ".v5-reveal",
      ".v5-image-reveal",
      ".luxury-image-reveal",
    ].join(",");

    const nodes = [];
    if (root instanceof Element && root.matches(selector)) nodes.push(root);
    nodes.push(...qsa(selector, root));

    nodes.forEach(node => {
      node.classList.add("v5-motion-visible", "v5-visible", "luxury-visible");
      node.removeAttribute("data-v5-motion");
      node.removeAttribute("data-luxury-reveal");
      node.style.removeProperty("--v5-motion-delay");
      node.style.removeProperty("--v5-heading-delay");
      node.style.removeProperty("--v5-mask-delay");
      node.style.removeProperty("--luxury-delay");
      node.style.removeProperty("transition-delay");
    });
  };

  const flattenHomeLayout = () => {
    if (!isHome()) return;
    document.body.style.setProperty("--v5-hybrid-shift", "0px", "important");
    qsa(".v5-home-rail").forEach(node => node.remove());
    qsa(".concern-card, .treatment-card, .why-card, .location-pro-card").forEach(card => {
      card.style.setProperty("margin-top", "0", "important");
      card.style.setProperty("translate", "none", "important");
      card.style.setProperty("transform", "none", "important");
    });
  };

  const cleanClinicalNavigation = () => {
    if (!isClinical()) return;

    /* The old inline chip TOC duplicates the new desktop editorial rail. */
    qsa(".release-toc, .article-toc").forEach(node => node.remove());
    qsa(".v5-reading-progress, .luxury-reading-progress, .v4-reading-progress").forEach(node => node.remove());

    if (isAcne()) {
      /* Acne keeps the shorter hand-curated V5 rail only. */
      qsa(".luxury-page-rail, .luxury-rail-help").forEach(node => node.remove());
      const rails = qsa(".v5-page-rail");
      rails.slice(1).forEach(node => node.remove());
      const rail = rails[0];
      if (!rail) return;
      rail.querySelector(".v5-rail-help")?.remove();
      qsa(":scope > ol > li", rail).slice(9).forEach(node => node.remove());
      return;
    }

    /* Other clinical pages keep one concise rail, without the colliding help box. */
    qsa(".v5-page-rail").forEach(node => node.remove());
    const rails = qsa(".luxury-page-rail");
    rails.slice(1).forEach(node => node.remove());
    const rail = rails[0];
    if (!rail) return;
    rail.querySelector(".luxury-rail-help")?.remove();
    qsa(":scope > ol > li", rail).slice(10).forEach(node => node.remove());
  };

  const removeDecorativeChrome = () => {
    qsa(".doctor-points li").forEach(item => item.classList.add("production-clean-point"));
    qsa(".v5-sidebar-trust > div, .luxury-sidebar-trust > div").forEach(item => item.classList.add("production-clean-point"));
  };

  const run = (root = document) => {
    installRuntimePolish();
    fixDoctorLinks(root);
    unlockContent(root);
    flattenHomeLayout();
    cleanClinicalNavigation();
    removeDecorativeChrome();
  };

  const boot = () => {
    run();

    let cleanupQueued = false;
    const queueCleanup = () => {
      if (cleanupQueued) return;
      cleanupQueued = true;
      queueMicrotask(() => {
        cleanupQueued = false;
        flattenHomeLayout();
        cleanClinicalNavigation();
        removeDecorativeChrome();
      });
    };

    const observer = new MutationObserver(records => {
      records.forEach(record => {
        record.addedNodes.forEach(node => {
          if (!(node instanceof Element)) return;
          fixDoctorLinks(node);
          unlockContent(node);
        });
      });
      queueCleanup();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    window.addEventListener("load", () => {
      run();
      window.setTimeout(run, 250);
      window.setTimeout(run, 800);
      window.setTimeout(run, 1600);
    }, { once: true });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
