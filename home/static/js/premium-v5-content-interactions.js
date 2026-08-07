(() => {
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

      if (!distinct) {
        grid.classList.remove("v5-comparison-enhanced");
        grid.classList.add("v5-comparison-static");
        qsa(".v5-comparison-handle, .v5-comparison-range", grid).forEach(node => node.remove());
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
        range.setAttribute("aria-label", "Compare before and after photographs");
        grid.append(range);
      }

      const sync = () => {
        const value = Math.max(0, Math.min(100, Number(range.value || 50)));
        grid.style.setProperty("--v5-compare", `${value}%`);
        grid.style.setProperty("--v4-compare", `${value}%`);
        range.setAttribute("aria-valuetext", `${Math.round(value)}% first image, ${Math.round(100 - value)}% second image`);
      };
      range.addEventListener("input", sync, { passive: true });
      range.addEventListener("dblclick", () => { range.value = "50"; sync(); });
      sync();

      if (!grid.nextElementSibling?.classList.contains("v5-comparison-instruction")) {
        const help = document.createElement("p");
        help.className = "v5-comparison-instruction";
        help.textContent = "Drag the divider, swipe it, or use the keyboard arrow keys to compare.";
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
    if (!targets.length) return;

    targets.forEach((node, index) => {
      let direction = "up";
      if (node.matches(".doctor-visual, .page-hero-art")) direction = "left";
      else if (node.matches(".doctor-copy, .sidebar-card")) direction = "right";
      else if (node.matches(".treatment-card, .concern-card, .location-pro-card, .v5-proof-item")) {
        direction = index % 2 === 0 ? "left" : "right";
      }
      node.dataset.v5Motion = direction;
      node.style.setProperty("--v5-motion-delay", `${Math.min(index % 4, 3) * 55}ms`);
    });

    const maskFrames = qsa(".home-hero-media, .doctor-visual, .page-hero-art, .treatment-card");
    maskFrames.forEach((frame, index) => {
      const image = frame.matches("img") ? frame : frame.querySelector("img");
      if (!image) return;
      image.classList.add("v5-mask-reveal");
      if (index % 2) image.classList.add("v5-mask-reveal--right");
      image.style.setProperty("--v5-mask-delay", `${80 + (index % 3) * 55}ms`);
    });

    if (reduceMotion || !("IntersectionObserver" in window)) {
      targets.forEach(node => node.classList.add("v5-motion-visible"));
      qsa(".v5-mask-reveal").forEach(node => node.classList.add("v5-motion-visible"));
      return;
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v5-motion-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -7% 0px" });

    targets.forEach(node => observer.observe(node));
    qsa(".v5-mask-reveal").forEach(node => observer.observe(node));
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
          { duration: opening ? 360 : 300, easing: "cubic-bezier(.2,.72,.2,1)" }
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

  /* Other V5 scripts enhance retained markup after DOMContentLoaded. Re-run only
     the idempotent comparison setup once more after the page settles. */
  window.addEventListener("load", setupComparison, { once: true });
})();
