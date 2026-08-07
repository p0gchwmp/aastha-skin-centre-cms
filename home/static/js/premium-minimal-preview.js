(() => {
  const body = document.body;
  if (!body || !body.classList.contains("cms-home-page")) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const targets = [
    ".home-section .section-heading",
    ".concern-card",
    ".doctor-visual",
    ".doctor-copy",
    ".treatment-card",
    ".why-card",
    ".location-pro-card",
    ".faq-pro-list details",
    ".home-cta-grid",
  ];

  const elements = [...document.querySelectorAll(targets.join(","))];
  if (!elements.length || reducedMotion || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  elements.forEach((element, index) => {
    element.dataset.premiumReveal = "";
    element.style.setProperty("--premium-delay", `${Math.min(index % 4, 3) * 55}ms`);
  });

  body.classList.add("premium-motion-ready");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      rootMargin: "0px 0px -8% 0px",
      threshold: 0.08,
    },
  );

  elements.forEach((element) => observer.observe(element));
})();
