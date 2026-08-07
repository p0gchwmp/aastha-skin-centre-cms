(() => {
  if (!document.body.classList.contains("cms-home-page")) return;

  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const labelFor = (section, index) => {
    if (section.classList.contains("home-hero")) return "Welcome";
    const heading = qs("h2, h3", section);
    if (!heading) return `Section ${index + 1}`;
    const text = (heading.textContent || "").trim().replace(/\s+/g, " ");
    if (/concern/i.test(text)) return "Concerns";
    if (/cheena|dermatologist/i.test(text)) return "Doctor";
    if (/treatment|advanced care/i.test(text)) return "Treatments";
    if (/clinic|jammu/i.test(text)) return "Clinics";
    if (/frequently|before your visit|question/i.test(text)) return "FAQ";
    return text.length > 24 ? `${text.slice(0, 22).trim()}…` : text;
  };

  const safeId = (section, index) => {
    if (section.id) return section.id;
    const label = labelFor(section, index)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    section.id = `v5-${label || `section-${index + 1}`}`;
    return section.id;
  };

  const setupHomeRail = () => {
    if (innerWidth < 1100 || qs(".v5-home-rail")) return;
    const candidates = [qs(".home-hero"), ...qsa(".home-main > section.home-section, .home-main > section")]
      .filter(Boolean)
      .filter((node, index, list) => list.indexOf(node) === index)
      .filter(section => section.getBoundingClientRect().height > 180);

    const preferred = [];
    const wanted = [/concern/i, /cheena|dermatologist/i, /treatment|advanced care/i, /clinic|jammu/i, /frequently|before your visit|question/i];
    const hero = candidates.find(section => section.classList.contains("home-hero"));
    if (hero) preferred.push(hero);
    wanted.forEach(pattern => {
      const match = candidates.find(section => pattern.test(labelFor(section, candidates.indexOf(section))));
      if (match && !preferred.includes(match)) preferred.push(match);
    });
    candidates.forEach(section => {
      if (preferred.length < 7 && !preferred.includes(section)) preferred.push(section);
    });
    const sections = preferred.slice(0, 7);
    if (sections.length < 2) return;

    const rail = document.createElement("nav");
    rail.className = "v5-home-rail";
    rail.setAttribute("aria-label", "Homepage sections");

    const entries = sections.map((section, index) => {
      const id = safeId(section, index);
      const button = document.createElement("button");
      button.type = "button";
      button.setAttribute("aria-label", `Go to ${labelFor(section, index)}`);
      button.innerHTML = `<span>${labelFor(section, index)}</span>`;
      button.addEventListener("click", () => {
        section.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
        history.replaceState(null, "", `#${id}`);
      });
      rail.append(button);
      return { section, button };
    });

    document.body.append(rail);

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(items => {
        const visible = items
          .filter(item => item.isIntersecting)
          .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))[0];
        if (!visible) return;
        entries.forEach(entry => {
          entry.button.setAttribute("aria-current", entry.section === visible.target ? "true" : "false");
        });
      }, { rootMargin: "-22% 0px -60% 0px", threshold: [0, .08, .35] });
      entries.forEach(entry => observer.observe(entry.section));
    }
    entries[0]?.button.setAttribute("aria-current", "true");
  };

  const setupConcernKeyboard = () => {
    const cards = qsa(".concern-card").filter(card => card.matches("a, button") || qs("a, button", card));
    if (cards.length < 2) return;
    cards.forEach((card, index) => {
      card.addEventListener("keydown", event => {
        if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
        event.preventDefault();
        const delta = event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 1;
        const next = cards[(index + delta + cards.length) % cards.length];
        const target = next.matches("a,button") ? next : qs("a,button", next);
        target?.focus();
      });
    });
  };

  const setupExclusiveFaq = () => {
    const details = qsa(".home-main details");
    details.forEach(item => {
      item.addEventListener("toggle", () => {
        if (!item.open) return;
        details.forEach(other => {
          if (other !== item && other.open) other.open = false;
        });
      });
    });
  };

  const boot = () => {
    document.body.classList.add("v5-hybrid-ready");
    setupHomeRail();
    setupConcernKeyboard();
    setupExclusiveFaq();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
