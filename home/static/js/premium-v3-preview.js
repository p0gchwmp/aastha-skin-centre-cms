(() => {
  /* Critical contrast rules are injected synchronously by this deferred script.
     They intentionally sit after every legacy stylesheet so the preview can
     keep the quiet-luxury palette without inheriting incompatible button/text
     combinations from earlier design layers. */
  const installContrastGuard = () => {
    if (document.getElementById("premium-v3-contrast-guard")) return;
    const style = document.createElement("style");
    style.id = "premium-v3-contrast-guard";
    style.textContent = `
      body.release-v24:not(.cms-home-page) .article-cta .button:not(.button-secondary),
      body.release-v24:not(.cms-home-page) .article-cta a.button:not(.button-secondary) {
        color: #681d35 !important;
        background: #fffdfa !important;
        border-color: #fffdfa !important;
      }
      body.release-v24:not(.cms-home-page) .article-cta .button-secondary,
      body.release-v24:not(.cms-home-page) .article-cta a.button-secondary {
        color: #ffffff !important;
        background: transparent !important;
        border-color: rgba(255,255,255,.60) !important;
      }
      html body.release-v24 main#main-content .clinical-results .clinical-results__hero-label,
      html[data-theme="dark"] body.release-v24 main#main-content .clinical-results .clinical-results__hero-label {
        color: #4b1427 !important;
        background: rgba(255,253,250,.96) !important;
        text-shadow: none !important;
      }
      html[data-theme="dark"] body.release-v24 .page-hero-copy .breadcrumbs a,
      html[data-theme="dark"] body.release-v24 .page-hero-copy nav a,
      html[data-theme="dark"] body.release-v24:not(.cms-home-page) .breadcrumbs a {
        color: #e0acbb !important;
      }
      html[data-theme="dark"] body.release-v24 .button:not(.button-secondary),
      html[data-theme="dark"] body.release-v24 a.button:not(.button-secondary),
      html[data-theme="dark"] body.release-v24 button.button:not(.button-secondary),
      html[data-theme="dark"] body.release-v24 button[type="submit"],
      html[data-theme="dark"] body.release-v24 a[href$="#appointment-form"].button,
      html[data-theme="dark"] body.release-v24 .care-sidebar-card > .button,
      html[data-theme="dark"] body.release-v24 .page-hero-copy .hero-actions > .button {
        color: #ffffff !important;
        background: #761b3b !important;
        border-color: #761b3b !important;
      }
      html[data-theme="dark"] body.release-v24 .button-secondary,
      html[data-theme="dark"] body.release-v24 a.button-secondary {
        color: #f8f2ec !important;
        background: transparent !important;
        border-color: rgba(255,255,255,.52) !important;
      }
      html[data-theme="dark"] body.release-v24:not(.cms-home-page) .article-cta .button:not(.button-secondary),
      html[data-theme="dark"] body.release-v24:not(.cms-home-page) .article-cta a.button:not(.button-secondary) {
        color: #681d35 !important;
        background: #fffdfa !important;
        border-color: #fffdfa !important;
      }
    `;
    document.head.appendChild(style);
  };

  installContrastGuard();

  const isRealPhoto = image => {
    if (!image) return false;
    const src = (image.currentSrc || image.getAttribute("src") || "").toLowerCase();
    if (!src) return false;
    return (
      src.includes("/media/") &&
      !src.endsWith(".svg") &&
      !src.includes("professional/")
    );
  };

  const classifyImages = () => {
    document.querySelectorAll(
      ".home-hero-media img, .doctor-visual img, .treatment-card img, .page-hero-art img"
    ).forEach(image => {
      image.classList.toggle("v3-real-photo", isRealPhoto(image));
    });
  };

  const revealTargets = () => {
    const selectors = [
      ".home-section .section-heading",
      ".concern-card",
      ".doctor-feature > *",
      ".treatment-card",
      ".why-card",
      ".location-pro-card",
      "body:not(.cms-home-page) .page-hero-copy",
      "body:not(.cms-home-page) .page-hero-art",
      "body:not(.cms-home-page) .prose > h2",
      "body:not(.cms-home-page) .inline-cta"
    ];
    return [...document.querySelectorAll(selectors.join(","))];
  };

  const setupReveal = () => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const targets = revealTargets();
    if (!("IntersectionObserver" in window) || !targets.length) {
      targets.forEach(node => node.classList.add("v3-is-visible"));
      return;
    }
    targets.forEach(node => node.classList.add("v3-reveal"));
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v3-is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -7% 0px", threshold: 0.05 });
    targets.forEach(node => observer.observe(node));
  };

  const boot = () => {
    classifyImages();
    setupReveal();

    // Wagtail preview and the hydrated global header can update the DOM shortly
    // after first paint. Reclassify images once more without keeping an observer
    // alive for the full session.
    window.setTimeout(classifyImages, 900);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
