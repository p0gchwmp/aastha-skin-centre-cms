(() => {
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
