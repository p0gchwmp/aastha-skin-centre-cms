(() => {
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const reduceMotion = reduceMotionQuery.matches;

  const sectionIndexFor = node => {
    const sections = qsa("main section, .home-hero");
    const owner = node.closest("section, .home-hero");
    const index = sections.indexOf(owner);
    return index < 0 ? 0 : index;
  };

  const setupComparison = () => {
    qsa(".cms-comparison-grid").forEach(grid => {
      const figures = qsa(":scope > figure", grid);
      if (figures.length !== 2) return;
      const first = figures[0].querySelector("img");
      const second = figures[1].querySelector("img");
      if (!first || !second) return;

      const firstSrc = first.currentSrc || first.src;
      const secondSrc = second.currentSrc || second.src;
      const distinct = firstSrc && secondSrc && firstSrc !== secondSrc;
      const firstLabel = figures[0].querySelector("figcaption")?.textContent?.trim() || "Before";
      const secondLabel = figures[1].querySelector("figcaption")?.textContent?.trim() || "After";
      const section = grid.closest(".cms-comparison-section");

      if (section) {
        section.classList.add("v5-comparison-stage");
        section.classList.toggle("v5-comparison-stage--home", document.body.classList.contains("cms-home-page"));
      }

      if (!distinct) {
        grid.classList.remove("v5-comparison-enhanced");
        grid.classList.add("v5-comparison-static");
        qsa(".v5-comparison-handle, .v5-comparison-range, .v5-comparison-hint", grid).forEach(node => node.remove());
        return;
      }

      grid.classList.remove("v5-comparison-static");
      grid.classList.add("v5-comparison-enhanced");

      let handle = grid.querySelector(".v5-comparison-handle");
      if (!handle) {
        handle = document.createElement("span");
        handle.className = "v5-comparison-handle";
        handle.setAttribute("aria-hidden", "true");
        grid.append(handle);
      }

      let range = grid.querySelector(".v5-comparison-range");
      if (!range) {
        range = document.createElement("input");
        range.className = "v5-comparison-range";
        range.type = "range";
        range.min = "0";
        range.max = "100";
        range.step = "1";
        range.value = "50";
        grid.append(range);
      }
      range.setAttribute("aria-label", `Compare ${firstLabel} and ${secondLabel} photographs`);

      let hint = grid.querySelector(".v5-comparison-hint");
      if (!hint) {
        hint = document.createElement("span");
        hint.className = "v5-comparison-hint";
        hint.setAttribute("aria-hidden", "true");
        hint.textContent = "Drag to compare";
        grid.append(hint);
      }

      const sync = () => {
        const value = Math.max(0, Math.min(100, Number(range.value || 50)));
        grid.style.setProperty("--v5-compare", `${value}%`);
        grid.style.setProperty("--v4-compare", `${value}%`);
        range.setAttribute("aria-valuetext", `${firstLabel} ${Math.round(value)}%, ${secondLabel} ${Math.round(100 - value)}%`);
      };
      const markUsed = () => grid.dataset.v5ComparisonUsed = "true";

      if (range.dataset.v5Bound !== "true") {
        range.dataset.v5Bound = "true";
        range.addEventListener("input", () => { markUsed(); sync(); }, { passive: true });
        range.addEventListener("pointerdown", markUsed, { passive: true });
        range.addEventListener("keydown", event => {
          if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "PageUp", "PageDown"].includes(event.key)) markUsed();
        });
        range.addEventListener("dblclick", () => {
          range.value = "50";
          markUsed();
          sync();
        });
      }
      sync();

      if (!grid.nextElementSibling?.classList.contains("v5-comparison-instruction")) {
        const help = document.createElement("p");
        help.className = "v5-comparison-instruction";
        help.textContent = "Drag or swipe the divider. Keyboard users can use the arrow keys.";
        grid.insertAdjacentElement("afterend", help);
      }
    });
  };

  const motionTargets = () => {
    const home = document.body.classList.contains("cms-home-page");
    if (home) {
      return qsa([
        ".home-hero-copy",
        ".home-hero-media",
        ".v5-hero-card",
        ".home-section .section-heading",
        ".concern-card",
        ".doctor-feature > .doctor-visual",
        ".doctor-feature > .doctor-copy",
        ".treatment-card",
        ".cms-comparison-section",
        ".clinical-results__inner",
        ".why-card",
        ".location-pro-card",
        ".home-main details",
      ].join(","));
    }
    return qsa([
      ".page-hero-copy",
      ".page-hero-art",
      ".v5-proof-item",
      ".prose > h2",
      ".prose > h3",
      ".cms-block",
      ".clinical-results__inner",
      ".location-pro-card",
      ".sidebar-card",
      ".article-cta",
    ].join(","));
  };

  const setupRevealChoreography = () => {
    const targets = motionTargets().filter((node, index, list) => list.indexOf(node) === index);
    const headings = qsa([
      ".home-hero h1",
      ".doctor-copy h2",
      ".home-section .section-heading h2",
      ".page-hero h1",
      ".cms-comparison-section h2",
    ].join(",")).filter((node, index, list) => list.indexOf(node) === index);

    targets.forEach(node => {
      const sectionIndex = sectionIndexFor(node);
      const owner = node.closest("section, .home-hero") || document.body;
      const siblings = qsa("[data-v5-motion], .concern-card, .treatment-card, .location-pro-card, .v5-proof-item", owner);
      const localIndex = Math.max(0, siblings.indexOf(node));
      let direction = "up";

      if (node.matches(".home-hero-media, .doctor-visual, .page-hero-art")) {
        direction = sectionIndex % 2 === 0 ? "right" : "left";
      } else if (node.matches(".doctor-copy, .sidebar-card")) {
        direction = sectionIndex % 2 === 0 ? "left" : "right";
      } else if (node.matches(".treatment-card, .concern-card, .location-pro-card, .v5-proof-item")) {
        direction = (sectionIndex + localIndex) % 2 === 0 ? "left" : "right";
      }

      node.dataset.v5Motion = direction;
      node.style.setProperty("--v5-motion-delay", `${Math.min(localIndex, 4) * 65}ms`);
    });

    headings.forEach((heading, index) => {
      heading.classList.add("v5-heading-reveal");
      heading.style.setProperty("--v5-heading-delay", `${Math.min(index % 3, 2) * 55}ms`);
    });

    const maskFrames = qsa(".home-hero-media, .doctor-visual, .page-hero-art, .treatment-card, .cms-comparison-grid");
    maskFrames.forEach(frame => {
      const image = frame.matches("img") ? frame : frame.querySelector("img");
      if (!image) return;
      const sectionIndex = sectionIndexFor(frame);
      image.classList.add("v5-mask-reveal");
      image.classList.toggle("v5-mask-reveal--right", sectionIndex % 2 === 1);
      image.style.setProperty("--v5-mask-delay", `${95 + (sectionIndex % 3) * 45}ms`);
    });

    const allObserved = [...targets, ...headings, ...qsa(".v5-mask-reveal")];
    if (!allObserved.length) return;

    if (reduceMotion || !("IntersectionObserver" in window)) {
      allObserved.forEach(node => node.classList.add("v5-motion-visible"));
      return;
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v5-motion-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -9% 0px" });

    allObserved.forEach(node => observer.observe(node));
  };

  const setupAnimatedDetails = () => {
    qsa("details").forEach(details => {
      const summary = details.querySelector(":scope > summary");
      if (!summary || details.dataset.v5Accordion === "true") return;
      details.dataset.v5Accordion = "true";
      details.classList.add("v5-accordion-animated");

      if (reduceMotion || typeof details.animate !== "function") return;

      summary.addEventListener("click", event => {
        event.preventDefault();
        if (details.dataset.v5Animating === "true") return;
        details.dataset.v5Animating = "true";

        const startHeight = details.getBoundingClientRect().height;
        const opening = !details.open;
        let endHeight;

        if (opening) {
          details.classList.add("v5-accordion-opening");
          details.open = true;
          endHeight = details.getBoundingClientRect().height;
        } else {
          details.open = false;
          endHeight = details.getBoundingClientRect().height;
          details.open = true;
        }

        details.style.height = `${startHeight}px`;
        const animation = details.animate(
          { height: [`${startHeight}px`, `${endHeight}px`] },
          { duration: opening ? 390 : 310, easing: "cubic-bezier(.18,.76,.18,1)" }
        );

        animation.onfinish = () => {
          details.style.height = "";
          if (!opening) details.open = false;
          details.classList.remove("v5-accordion-opening");
          delete details.dataset.v5Animating;
        };
        animation.oncancel = animation.onfinish;
      });
    });
  };

  const setupClinicalSwipe = () => {
    qsa("[data-clinical-carousel]").forEach(carousel => {
      if (carousel.dataset.v5Swipe === "true") return;
      const viewport = carousel.querySelector(".clinical-results__viewport");
      const previous = carousel.querySelector("[data-clinical-previous]");
      const next = carousel.querySelector("[data-clinical-next]");
      if (!viewport || !previous || !next) return;
      carousel.dataset.v5Swipe = "true";

      let startX = null;
      let pointerId = null;
      viewport.addEventListener("pointerdown", event => {
        if (event.pointerType === "mouse" && event.button !== 0) return;
        startX = event.clientX;
        pointerId = event.pointerId;
        viewport.setPointerCapture?.(event.pointerId);
      });
      viewport.addEventListener("pointerup", event => {
        if (startX === null || (pointerId !== null && event.pointerId !== pointerId)) return;
        const delta = event.clientX - startX;
        startX = null;
        pointerId = null;
        if (Math.abs(delta) < 44) return;
        (delta > 0 ? previous : next).click();
      });
      viewport.addEventListener("pointercancel", () => { startX = null; pointerId = null; });

      const animateVisibleSlide = () => {
        const slide = qsa(".clinical-results__slide", viewport).find(item => !item.hidden);
        if (!slide || reduceMotion) return;
        slide.classList.remove("v5-result-enter");
        requestAnimationFrame(() => requestAnimationFrame(() => slide.classList.add("v5-result-enter")));
      };
      const mutations = new MutationObserver(records => {
        if (records.some(record => record.type === "attributes" && record.attributeName === "hidden")) animateVisibleSlide();
      });
      mutations.observe(viewport, { subtree: true, attributes: true, attributeFilter: ["hidden"] });
      animateVisibleSlide();
    });
  };

  const boot = () => {
    setupComparison();
    setupRevealChoreography();
    setupAnimatedDetails();
    setupClinicalSwipe();
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();

  /* Other V5 scripts enhance retained markup after DOMContentLoaded. Re-run the
     idempotent comparison setup once more after all deferred preview scripts. */
  window.addEventListener("load", setupComparison, { once: true });
})();
