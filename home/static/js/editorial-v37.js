(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;

  const body = document.body;
  if (!body) return;
  body.classList.add("editorial-v37-active");

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const path = window.location.pathname;

  // Small route marker: useful hierarchy without altering page semantics.
  const hero = document.querySelector(".page-hero, .page-hero--professional");
  if (hero && !hero.querySelector(".v37-route-label")) {
    const heading = hero.querySelector("h1");
    const host = heading?.parentElement;
    if (host) {
      const route = document.createElement("span");
      route.className = "v37-route-label";
      route.textContent = path.startsWith("/treatments/")
        ? "Clinical guide · Jammu"
        : path.startsWith("/locations/")
          ? "Clinic · Jammu"
          : path.startsWith("/blog/")
            ? "Skin journal"
            : "Aastha Skin Centre · Jammu";
      host.insertBefore(route, heading || host.firstChild);
    }
  }

  // Keep the first meaningful image high priority; defer the rest.
  const contentImages = [...document.querySelectorAll("main img")];
  contentImages.forEach((img, index) => {
    img.decoding = "async";
    if (index === 0) {
      img.loading = "eager";
      img.fetchPriority = "high";
    } else if (!img.hasAttribute("loading")) {
      img.loading = "lazy";
    }
  });

  // Replace only old generic SVG placeholders. Real Wagtail/clinical-result
  // images are never overwritten.
  const placeholderMap = [
    ["hero-care.svg", "/assets/images/visual-cues/personalised-plan-512.webp"],
    ["doctor-care.svg", "/assets/images/visual-cues/dermatologist-diagnosis-512.webp"],
    ["acne-care.svg", "/assets/images/visual-cues/acne-care-512.webp"],
    ["hair-care.svg", "/assets/images/visual-cues/hair-scalp-care-512.webp"],
    ["laser-care.svg", "/assets/images/visual-cues/complete-care-512.webp"],
    ["medical-care.svg", "/assets/images/visual-cues/clinical-skin-care-512.webp"],
    ["clinic-care.svg", "/assets/images/visual-cues/two-clinic-locations-512.webp"],
  ];
  document.querySelectorAll('img[src*="/professional/"]').forEach((img) => {
    const current = img.getAttribute("src") || "";
    const match = placeholderMap.find(([needle]) => current.includes(needle));
    if (!match) return;
    const original = current;
    img.src = match[1];
    img.classList.add("v37-image-upgraded");
    img.addEventListener("error", () => {
      if (img.src.includes(match[1])) img.src = original;
    }, { once: true });
  });

  // Reading progress for long clinical pages.
  const progress = document.createElement("div");
  progress.className = "v37-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.appendChild(progress);
  let progressQueued = false;
  const updateProgress = () => {
    const root = document.documentElement;
    const max = Math.max(1, root.scrollHeight - window.innerHeight);
    progress.style.width = `${Math.min(100, Math.max(0, (window.scrollY / max) * 100))}%`;
    progressQueued = false;
  };
  window.addEventListener("scroll", () => {
    if (progressQueued) return;
    progressQueued = true;
    requestAnimationFrame(updateProgress);
  }, { passive: true });
  updateProgress();

  // Persistent actions read existing CMS settings from body data attributes.
  if (!document.querySelector(".v37-quickbar")) {
    const primary = (body.dataset.primaryMobile || "7006613362").replace(/\D/g, "").slice(-10);
    const whatsapp = body.dataset.whatsappUrl || `https://wa.me/91${primary}`;
    const bar = document.createElement("nav");
    bar.className = "v37-quickbar";
    bar.setAttribute("aria-label", "Quick clinic actions");
    bar.innerHTML = `
      <a href="tel:+91${primary}">Call</a>
      <a href="${whatsapp}" target="_blank" rel="noopener">WhatsApp</a>
      <a href="/book-appointment/">Book</a>`;
    document.body.appendChild(bar);
  }

  // Keep FAQ stacks tidy: opening one closes its siblings only.
  document.querySelectorAll(".faq-pro-list, .faq-list").forEach((stack) => {
    const items = [...stack.querySelectorAll(":scope > details")];
    items.forEach((item) => item.addEventListener("toggle", () => {
      if (!item.open) return;
      items.forEach((other) => {
        if (other !== item) other.removeAttribute("open");
      });
    }));
  });

  // Restore the stronger sticky How Care Works behaviour if that component is
  // present in an ExactPageLayout/editor section.
  const approach = document.querySelector("#approach");
  const chapters = approach ? [...approach.querySelectorAll(".process-chapter")] : [];
  const processButtons = approach ? [...approach.querySelectorAll(".process-nav button")] : [];
  if (chapters.length && processButtons.length) {
    processButtons.forEach((button, index) => {
      button.addEventListener("click", () => {
        chapters[index]?.scrollIntoView({
          behavior: reducedMotion ? "auto" : "smooth",
          block: "center",
        });
      });
    });
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      const index = chapters.indexOf(visible.target);
      processButtons.forEach((button, buttonIndex) => {
        button.classList.toggle("is-active", buttonIndex === index);
        button.setAttribute("aria-current", buttonIndex === index ? "step" : "false");
      });
    }, { rootMargin: "-30% 0px -45%", threshold: [0.1, 0.35, 0.6] });
    chapters.forEach((chapter) => observer.observe(chapter));
  }

  // Add active state without interfering with existing menu JS.
  document.querySelectorAll(".primary-nav a").forEach((link) => {
    try {
      const href = new URL(link.href, window.location.origin).pathname;
      if (href === path || (href !== "/" && path.startsWith(href))) {
        link.setAttribute("aria-current", "page");
      }
    } catch (_) {}
  });
})();
