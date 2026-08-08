(() => {
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const isHome = () => document.body.classList.contains("cms-home-page");
  const isAcne = () => document.body.dataset.pageSlug === "acne-treatment" || location.pathname === "/treatments/acne-treatment/";

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

  const cleanAcneNavigation = () => {
    if (!isAcne()) return;

    qsa(".release-toc, .article-toc").forEach(node => node.remove());
    qsa(".luxury-page-rail, .luxury-rail-help").forEach(node => node.remove());
    qsa(".v5-reading-progress, .luxury-reading-progress, .v4-reading-progress").forEach(node => node.remove());

    const rails = qsa(".v5-page-rail");
    rails.slice(1).forEach(node => node.remove());
    const rail = rails[0];
    if (!rail) return;

    rail.querySelector(".v5-rail-help")?.remove();
    qsa(":scope > ol > li", rail).slice(9).forEach(node => node.remove());
  };

  const removeDecorativeChrome = () => {
    qsa(".doctor-points li").forEach(item => item.classList.add("production-clean-point"));
    qsa(".v5-sidebar-trust > div, .luxury-sidebar-trust > div").forEach(item => item.classList.add("production-clean-point"));
  };

  const run = (root = document) => {
    fixDoctorLinks(root);
    unlockContent(root);
    flattenHomeLayout();
    cleanAcneNavigation();
    removeDecorativeChrome();
  };

  const boot = () => {
    run();

    /* Late preview/editor adapters can insert DOM after our deferred script.
       Re-clean immediately so there is no persistent duplicate rail, stale
       doctor URL or observer-dependent invisible content. */
    let cleanupQueued = false;
    const queueCleanup = () => {
      if (cleanupQueued) return;
      cleanupQueued = true;
      queueMicrotask(() => {
        cleanupQueued = false;
        flattenHomeLayout();
        cleanAcneNavigation();
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
