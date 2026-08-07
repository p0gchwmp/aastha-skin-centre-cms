(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const desktopRail = window.matchMedia("(min-width: 1321px)");

  const slugify = value => value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 72) || "section";

  const setupHeaderCompression = () => {
    let ticking = false;
    const apply = () => {
      document.body.classList.toggle("v4-scrolled", window.scrollY > 48);
      ticking = false;
    };
    apply();
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(apply);
    }, { passive: true });
  };

  const setupRevealChoreography = () => {
    const selectors = [
      ".home-section .section-heading",
      ".concern-card",
      ".doctor-copy > *",
      ".treatment-card",
      ".why-card",
      ".location-pro-card",
      "body:not(.cms-home-page) .page-hero-copy > *",
      "body:not(.cms-home-page) .prose > h2",
      "body:not(.cms-home-page) .prose > h3",
      "body:not(.cms-home-page) .inline-cta",
      ".clinical-results__inner"
    ];
    const nodes = [...document.querySelectorAll(selectors.join(","))];
    const images = [...document.querySelectorAll(
      ".home-hero-media > img, .doctor-visual img, .treatment-card img, .page-hero-art img"
    )];

    if (reduceMotion.matches || !("IntersectionObserver" in window)) {
      nodes.forEach(node => node.classList.add("v4-visible"));
      images.forEach(image => image.classList.add("v4-visible"));
      return;
    }

    nodes.forEach((node, index) => {
      node.classList.add("v4-reveal");
      node.style.setProperty("--v4-delay", String(index % 4));
    });
    images.forEach(image => image.classList.add("v4-image-reveal"));

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v4-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -6% 0px" });

    [...nodes, ...images].forEach(node => observer.observe(node));
  };

  const setupTreatmentCarousel = () => {
    const grid = document.querySelector("body.cms-home-page .treatment-grid");
    if (!grid || grid.children.length < 2) return;

    grid.classList.add("v4-carousel-ready");
    const controls = document.createElement("div");
    controls.className = "v4-carousel-controls";
    controls.setAttribute("aria-label", "Selected treatment carousel controls");
    controls.innerHTML = `
      <button class="v4-carousel-button" type="button" data-v4-carousel-prev aria-label="Previous treatment">←</button>
      <div class="v4-carousel-progress" aria-hidden="true"><span></span></div>
      <button class="v4-carousel-button" type="button" data-v4-carousel-next aria-label="Next treatment">→</button>
    `;
    grid.insertAdjacentElement("afterend", controls);

    const cards = [...grid.querySelectorAll(".treatment-card")];
    const progress = controls.querySelector(".v4-carousel-progress > span");
    const scrollToIndex = index => {
      const safe = Math.max(0, Math.min(cards.length - 1, index));
      cards[safe].scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "nearest", inline: "start" });
    };
    const activeIndex = () => {
      const left = grid.scrollLeft;
      let best = 0;
      let distance = Infinity;
      cards.forEach((card, index) => {
        const d = Math.abs(card.offsetLeft - left);
        if (d < distance) {
          best = index;
          distance = d;
        }
      });
      return best;
    };
    const update = () => {
      const index = activeIndex();
      progress.style.setProperty("--v4-progress", `${((index + 1) / cards.length) * 100}%`);
      controls.querySelector("[data-v4-carousel-prev]").disabled = index === 0;
      controls.querySelector("[data-v4-carousel-next]").disabled = index === cards.length - 1;
    };
    controls.querySelector("[data-v4-carousel-prev]").addEventListener("click", () => scrollToIndex(activeIndex() - 1));
    controls.querySelector("[data-v4-carousel-next]").addEventListener("click", () => scrollToIndex(activeIndex() + 1));
    grid.addEventListener("scroll", () => window.requestAnimationFrame(update), { passive: true });
    update();
  };

  const setupReadingProgress = () => {
    if (document.body.classList.contains("cms-home-page")) return;
    const prose = document.querySelector(".prose");
    if (!prose) return;
    const headings = [...prose.querySelectorAll(":scope > h2")].filter(h => h.textContent.trim().length > 2);
    if (headings.length < 4) return;

    const used = new Set();
    headings.forEach((heading, index) => {
      if (!heading.id) {
        let id = slugify(heading.textContent);
        if (used.has(id) || document.getElementById(id)) id = `${id}-${index + 1}`;
        heading.id = id;
      }
      used.add(heading.id);
    });

    const nav = document.createElement("nav");
    nav.className = "v4-reading-progress";
    nav.setAttribute("aria-label", "On this page");
    headings.slice(0, 8).forEach(heading => {
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent.trim().replace(/\s+/g, " ");
      link.addEventListener("click", event => {
        if (reduceMotion.matches) return;
        event.preventDefault();
        heading.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", `#${heading.id}`);
      });
      nav.appendChild(link);
    });
    document.body.appendChild(nav);

    if (!("IntersectionObserver" in window)) return;
    const links = [...nav.querySelectorAll("a")];
    const map = new Map(headings.map((heading, index) => [heading, links[index]]).filter(([,link]) => link));
    const observer = new IntersectionObserver(entries => {
      const visible = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top));
      if (!visible.length) return;
      links.forEach(link => link.removeAttribute("aria-current"));
      const current = map.get(visible[0].target);
      if (current) current.setAttribute("aria-current", "true");
    }, { rootMargin: "-18% 0px -68% 0px", threshold: [0, 1] });
    headings.forEach(heading => observer.observe(heading));

    const syncRail = () => nav.hidden = !desktopRail.matches;
    desktopRail.addEventListener?.("change", syncRail);
    syncRail();
  };

  const setupBeforeAfter = () => {
    document.querySelectorAll("[data-before-after]").forEach(root => {
      const input = root.querySelector('input[type="range"]');
      if (!input || root.dataset.v4Enhanced === "true") return;
      root.dataset.v4Enhanced = "true";
      const update = () => {
        const min = Number(input.min || 0);
        const max = Number(input.max || 100);
        const value = Number(input.value || 50);
        const percent = ((value - min) / Math.max(1, max - min)) * 100;
        root.style.setProperty("--v4-compare", `${percent}%`);
        input.setAttribute("aria-valuetext", `${Math.round(percent)}% before / ${Math.round(100 - percent)}% after`);
      };
      input.addEventListener("input", update);
      update();
    });
  };

  const setupClinicalSwipe = () => {
    document.querySelectorAll("[data-clinical-carousel]").forEach(carousel => {
      const viewport = carousel.querySelector(".clinical-results__viewport");
      const previous = carousel.querySelector("[data-clinical-previous]");
      const next = carousel.querySelector("[data-clinical-next]");
      if (!viewport || !previous || !next) return;
      let startX = null;
      viewport.addEventListener("pointerdown", event => {
        if (event.pointerType === "mouse" && event.button !== 0) return;
        startX = event.clientX;
      });
      viewport.addEventListener("pointerup", event => {
        if (startX === null) return;
        const delta = event.clientX - startX;
        startX = null;
        if (Math.abs(delta) < 46) return;
        (delta > 0 ? previous : next).click();
      });
      viewport.addEventListener("pointercancel", () => { startX = null; });
    });
  };

  const boot = () => {
    setupHeaderCompression();
    setupRevealChoreography();
    setupTreatmentCarousel();
    setupReadingProgress();
    setupBeforeAfter();
    setupClinicalSwipe();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();

/* Load the retained-markup structure correction only on the acne preview. */
(() => {
  if (location.pathname !== "/treatments/acne-treatment/") return;

  if (!document.querySelector('link[data-v5-acne-structure]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/static/css/premium-v5-acne-structure.css";
    link.dataset.v5AcneStructure = "true";
    document.head.appendChild(link);
  }

  if (!document.querySelector('script[data-v5-acne-structure]')) {
    const script = document.createElement("script");
    script.src = "/static/js/premium-v5-acne-structure.js";
    script.dataset.v5AcneStructure = "true";
    document.body.appendChild(script);
  }
})();
