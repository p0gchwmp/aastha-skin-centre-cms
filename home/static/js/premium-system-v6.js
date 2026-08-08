(() => {
  "use strict";

  const root = document.documentElement;
  const body = document.body;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const qsa = (selector, scope = document) => [...scope.querySelectorAll(selector)];

  const motionSelector = [
    ".home-hero-copy",
    ".home-hero-media",
    ".v5-hero-card",
    ".section-heading",
    ".concern-card",
    ".doctor-feature > *",
    ".treatment-card",
    ".why-card",
    ".location-pro-card",
    ".trust-ribbon",
    ".journal-card",
    ".hub-category",
    ".page-hero-copy",
    ".page-hero-art",
    ".article-section > h2",
    ".article-section > h3",
    ".cms-comparison-section",
    ".clinical-results__inner",
    ".clinic-choice-card",
    ".faq-section",
  ].join(",");

  const cardSelector = [
    ".concern-card",
    ".treatment-card",
    ".why-card",
    ".location-pro-card",
    ".journal-card",
    ".clinic-card",
    ".clinic-choice-card",
    ".hub-category",
    ".hub-link",
    ".cms-card",
    ".feature-card",
    ".service-card",
  ].join(",");

  const revealImmediately = () => {
    qsa(".v6-reveal").forEach(node => node.classList.add("v6-visible"));
    root.classList.remove("v6-motion-ready");
  };

  const setupReveal = () => {
    const targets = qsa(motionSelector).filter((node, index, list) => list.indexOf(node) === index);
    if (!targets.length || reduceMotion.matches || !("IntersectionObserver" in window)) {
      targets.forEach(node => node.classList.add("v6-reveal", "v6-visible"));
      return;
    }

    root.classList.add("v6-motion-ready");
    targets.forEach((node, index) => {
      node.classList.add("v6-reveal");
      node.style.setProperty("--v6-delay", `${Math.min(index % 4, 3) * 60}ms`);
    });

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("v6-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: .08, rootMargin: "0px 0px -7% 0px" });

    targets.forEach(node => observer.observe(node));

    /* Animation is enhancement only. No content can remain hidden if browser
       observers, injected preview scripts or restored sessions misbehave. */
    window.setTimeout(revealImmediately, 1800);
  };

  const setupCardLight = () => {
    if (!finePointer.matches) return;
    qsa(cardSelector).forEach(card => {
      if (card.dataset.v6Pointer === "true") return;
      card.dataset.v6Pointer = "true";
      card.addEventListener("pointermove", event => {
        const box = card.getBoundingClientRect();
        card.style.setProperty("--v6-pointer-x", `${event.clientX - box.left}px`);
        card.style.setProperty("--v6-pointer-y", `${event.clientY - box.top}px`);
      }, { passive: true });
    });
  };

  const toNumber = value => {
    const match = String(value || "").match(/\d+/);
    return match ? Number(match[0]) : null;
  };

  const wordNumber = value => {
    const numbers = {
      one: 1,
      two: 2,
      three: 3,
      four: 4,
      five: 5,
      six: 6,
      seven: 7,
      eight: 8,
      nine: 9,
      ten: 10,
    };
    const word = String(value || "").trim().toLowerCase().split(/\s+/)[0];
    return numbers[word] || null;
  };

  const trustValue = pattern => {
    const item = qsa(".trust-item").find(node => pattern.test(node.textContent || ""));
    if (!item) return null;
    const strong = item.querySelector("strong") || item;
    return {
      number: toNumber(strong.textContent) ?? wordNumber(strong.textContent),
      text: strong.textContent.trim(),
    };
  };

  const animateCounter = valueNode => {
    const finalValue = Number(valueNode.dataset.v6Value || 0);
    if (!Number.isFinite(finalValue) || finalValue < 1) return;

    const suffix = valueNode.dataset.v6Suffix || "";
    const prefix = valueNode.dataset.v6Prefix || "";
    const render = number => {
      valueNode.textContent = `${prefix}${Math.round(number)}${suffix}`;
    };

    if (reduceMotion.matches || !("IntersectionObserver" in window)) {
      render(finalValue);
      return;
    }

    /* Keep the verified final number in the DOM until the counter actually
       enters the viewport. Full-page capture, no-JS recovery and assistive
       technology therefore never see a misleading zero state. */
    render(finalValue);
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        render(0);
        const started = performance.now();
        const duration = 950;
        const tick = now => {
          const progress = Math.min(1, (now - started) / duration);
          const eased = 1 - Math.pow(1 - progress, 3);
          render(finalValue * eased);
          if (progress < 1) window.requestAnimationFrame(tick);
        };
        window.requestAnimationFrame(tick);
      });
    }, { threshold: .4 });
    observer.observe(valueNode);
  };

  const setupStats = () => {
    if (!body.classList.contains("cms-home-page") || document.querySelector(".v6-stats")) return;
    const trustRibbon = document.querySelector(".trust-ribbon");
    if (!trustRibbon) return;

    const years = trustValue(/years?/i);
    const clinics = trustValue(/clinics?/i);
    const followUp = toNumber(body.dataset.followUpDays);
    const stats = [];

    if (years?.number) stats.push({ value: years.number, suffix: years.text.includes("+") ? "+" : "", label: "Years in medicine" });
    if (clinics?.number) stats.push({ value: clinics.number, suffix: "", label: "Clinics in Jammu" });
    if (followUp) stats.push({ value: followUp, suffix: "", label: "Day follow-up window" });
    if (stats.length < 2) return;

    const section = document.createElement("section");
    section.className = "v6-stats";
    section.setAttribute("aria-label", "Clinic at a glance");
    section.style.setProperty("--v6-stat-count", String(stats.length));

    const inner = document.createElement("div");
    inner.className = "v6-stats__inner";
    stats.forEach(stat => {
      const item = document.createElement("div");
      item.className = "v6-stat";

      const value = document.createElement("strong");
      value.className = "v6-stat__value";
      value.dataset.v6Value = String(stat.value);
      value.dataset.v6Suffix = stat.suffix;
      value.setAttribute("aria-label", `${stat.value}${stat.suffix} ${stat.label}`);

      const label = document.createElement("span");
      label.className = "v6-stat__label";
      label.textContent = stat.label;

      item.append(value, label);
      inner.append(item);
    });
    section.append(inner);
    trustRibbon.insertAdjacentElement("afterend", section);
    qsa(".v6-stat__value", section).forEach(animateCounter);
  };

  const enhanceComparison = grid => {
    const figures = qsa(":scope > figure", grid);
    if (figures.length !== 2) return;
    const firstImage = figures[0].querySelector("img");
    const secondImage = figures[1].querySelector("img");
    if (!firstImage || !secondImage) return;

    const firstSource = firstImage.currentSrc || firstImage.src;
    const secondSource = secondImage.currentSrc || secondImage.src;
    if (!firstSource || !secondSource || firstSource === secondSource) return;

    const firstLabel = figures[0].querySelector("figcaption")?.textContent?.trim() || "Before";
    const secondLabel = figures[1].querySelector("figcaption")?.textContent?.trim() || "After";
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
      const amount = Math.max(0, Math.min(100, Number(range.value || 50)));
      grid.style.setProperty("--v5-compare", `${amount}%`);
      range.setAttribute("aria-valuetext", `${firstLabel} ${Math.round(amount)}%, ${secondLabel} ${Math.round(100 - amount)}%`);
    };

    if (range.dataset.v6Bound !== "true") {
      range.dataset.v6Bound = "true";
      range.addEventListener("input", () => {
        grid.dataset.v5ComparisonUsed = "true";
        sync();
      }, { passive: true });
      range.addEventListener("dblclick", () => {
        range.value = "50";
        grid.dataset.v5ComparisonUsed = "true";
        sync();
      });
    }
    sync();

    if (!grid.nextElementSibling?.classList.contains("v5-comparison-instruction")) {
      const instruction = document.createElement("p");
      instruction.className = "v5-comparison-instruction";
      instruction.textContent = "Drag or swipe the divider. Use arrow keys for precise comparison.";
      grid.insertAdjacentElement("afterend", instruction);
    }
  };

  const setupComparisons = (scope = document) => {
    qsa(".cms-comparison-grid", scope).forEach(enhanceComparison);
  };

  const setupScrollProgress = () => {
    if (document.querySelector(".v6-scroll-progress")) return;
    const progress = document.createElement("div");
    progress.className = "v6-scroll-progress";
    progress.setAttribute("aria-hidden", "true");
    body.prepend(progress);

    let scheduled = false;
    const update = () => {
      const available = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const amount = Math.max(0, Math.min(1, window.scrollY / available));
      progress.style.setProperty("--v6-scroll", amount.toFixed(4));
      body.classList.toggle("v6-header-condensed", window.scrollY > 36);
      scheduled = false;
    };

    window.addEventListener("scroll", () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(update);
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  };

  const setupRailTracking = () => {
    const rail = document.querySelector(".v5-page-rail, .luxury-page-rail");
    if (!rail || !("IntersectionObserver" in window)) return;
    const links = qsa('a[href^="#"]', rail);
    const sections = links.map(link => document.querySelector(link.getAttribute("href"))).filter(Boolean);
    if (!sections.length) return;

    const activate = section => {
      links.forEach(link => {
        const active = link.getAttribute("href") === `#${section.id}`;
        if (active) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
    };

    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible[0]) activate(visible[0].target);
    }, { rootMargin: "-22% 0px -64% 0px", threshold: [0, .1, .5] });
    sections.forEach(section => observer.observe(section));
  };

  const setupMutationPass = () => {
    let queued = false;
    const observer = new MutationObserver(records => {
      const added = records.flatMap(record => [...record.addedNodes]).filter(node => node instanceof Element);
      if (!added.length || queued) return;
      queued = true;
      window.requestAnimationFrame(() => {
        added.forEach(node => {
          if (node.matches?.(".cms-comparison-grid")) enhanceComparison(node);
          setupComparisons(node);
        });
        setupCardLight();
        queued = false;
      });
    });
    observer.observe(body, { childList: true, subtree: true });
  };

  const boot = () => {
    setupStats();
    setupComparisons();
    setupCardLight();
    setupScrollProgress();
    setupRailTracking();
    setupReveal();
    setupMutationPass();
  };

  reduceMotion.addEventListener?.("change", event => {
    if (event.matches) revealImmediately();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  /* Exact-page and CMS enhancement scripts finish after DOMContentLoaded. */
  window.addEventListener("load", () => {
    setupComparisons();
    setupCardLight();
    window.setTimeout(setupComparisons, 500);
  }, { once: true });
})();

