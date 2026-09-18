(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;

  const routes = [
    { group: "Start here", label: "Concerns", note: "Browse by symptom or concern", href: "/conditions/" },
    { group: "Start here", label: "Find your route", note: "Choose area + concern", href: "/#v37-finder" },
    { group: "Start here", label: "Treatments", note: "Full treatment directory", href: "/treatments/" },
    { group: "Start here", label: "Book consultation", note: "Request an appointment", href: "/book-appointment/" },
    { group: "Common guides", label: "Acne", note: "Breakouts, marks and active acne", href: "/treatments/acne-treatment/" },
    { group: "Common guides", label: "Acne scars", note: "Scar-type planning and resurfacing", href: "/treatments/acne-scar-treatment/" },
    { group: "Common guides", label: "Pigmentation", note: "Melasma, marks and uneven tone", href: "/treatments/pigmentation-treatment/" },
    { group: "Common guides", label: "Melasma", note: "Triggers, maintenance and treatment", href: "/treatments/melasma-treatment/" },
    { group: "Common guides", label: "Hair fall", note: "Shedding, thinning and scalp assessment", href: "/treatments/hair-fall-treatment/" },
    { group: "Common guides", label: "Hair transplant", note: "Donor planning and suitability", href: "/treatments/hair-transplant/" },
    { group: "Common guides", label: "Fungal infection", note: "Ringworm, recurrence and steroid-modified tinea", href: "/treatments/fungal-infection-treatment/" },
    { group: "Common guides", label: "Laser hair reduction", note: "Hair, skin type and session planning", href: "/treatments/laser-hair-reduction/" },
    { group: "Clinic", label: "Dr. Cheena Langer", note: "Consultant dermatologist", href: "/dr-cheena-langer/" },
    { group: "Clinic", label: "Karan Nagar", note: "Clinic details, timings and directions", href: "/locations/karan-nagar/" },
    { group: "Clinic", label: "Paloura", note: "Clinic details, timings and directions", href: "/locations/paloura/" },
    { group: "Clinic", label: "Journal", note: "Dermatology articles and patient education", href: "/blog/" },
    { group: "Clinic", label: "Contact", note: "Phone, WhatsApp and clinic information", href: "/contact/" },
  ];

  const normalize = (value) => String(value || "").trim().toLowerCase();

  let kokonutModulePromise = null;
  async function loadKokonutExplore() {
    if (window.AasthaKokonutExplore?.open) return true;
    if (!kokonutModulePromise) {
      kokonutModulePromise = import("/assets/ui/kokonut-explore.js")
        .then(() => new Promise((resolve) => {
          if (window.AasthaKokonutExplore?.open) return resolve(true);
          const done = () => resolve(Boolean(window.AasthaKokonutExplore?.open));
          window.addEventListener("aastha:kokonut-ready", done, { once: true });
          window.setTimeout(() => resolve(Boolean(window.AasthaKokonutExplore?.open)), 900);
        }))
        .catch(() => false);
    }
    return kokonutModulePromise;
  }

  function buildExplore() {
    if (document.querySelector(".v37-explore")) return document.querySelector(".v37-explore");
    const overlay = document.createElement("div");
    overlay.className = "v37-explore";
    overlay.hidden = true;
    overlay.innerHTML = `
      <div class="v37-explore-backdrop" data-v37-explore-close></div>
      <section class="v37-explore-panel" role="dialog" aria-modal="true" aria-labelledby="v37-explore-title">
        <header class="v37-explore-head">
          <div><span>Aastha · Jammu</span><h2 id="v37-explore-title">Where do you want to go?</h2></div>
          <button type="button" class="v37-explore-close" data-v37-explore-close aria-label="Close Explore">Close</button>
        </header>
        <label class="v37-explore-search">
          <span class="sr-only">Search website routes</span>
          <input type="search" autocomplete="off" placeholder="Search concerns, treatments, doctor, clinics…" data-v37-explore-search>
        </label>
        <div class="v37-explore-groups" data-v37-explore-results></div>
      </section>`;
    document.body.appendChild(overlay);

    const results = overlay.querySelector("[data-v37-explore-results]");
    const input = overlay.querySelector("[data-v37-explore-search]");
    const groups = [...new Set(routes.map((route) => route.group))];

    const render = (query = "") => {
      const q = normalize(query);
      const matches = routes.filter((route) => !q || normalize(`${route.label} ${route.note} ${route.group}`).includes(q));
      results.innerHTML = groups.map((group) => {
        const items = matches.filter((route) => route.group === group);
        if (!items.length) return "";
        return `<section class="v37-explore-group"><h3>${group}</h3><div>${items.map((route) => `
          <a href="${route.href}" class="v37-explore-route">
            <strong>${route.label}</strong><span>${route.note}</span><i aria-hidden="true">↗</i>
          </a>`).join("")}</div></section>`;
      }).join("") || `<p class="v37-explore-empty">No matching route. Try a broader term.</p>`;
    };

    render();
    input.addEventListener("input", () => render(input.value));
    overlay.querySelectorAll("[data-v37-explore-close]").forEach((control) => control.addEventListener("click", () => closeExplore()));
    return overlay;
  }

  let previousFocus = null;
  async function openExplore() {
    previousFocus = document.activeElement;
    const enhanced = await loadKokonutExplore();
    if (enhanced && window.AasthaKokonutExplore?.open) {
      window.AasthaKokonutExplore.open();
      return;
    }
    const overlay = buildExplore();
    overlay.hidden = false;
    document.body.classList.add("v37-explore-open");
    window.requestAnimationFrame(() => overlay.classList.add("is-open"));
    const input = overlay.querySelector("[data-v37-explore-search]");
    window.setTimeout(() => input?.focus(), 30);
  }

  function closeExplore() {
    if (window.AasthaKokonutExplore?.close) {
      window.AasthaKokonutExplore.close();
      return;
    }
    const overlay = document.querySelector(".v37-explore");
    if (!overlay || overlay.hidden) return;
    overlay.classList.remove("is-open");
    document.body.classList.remove("v37-explore-open");
    window.setTimeout(() => { overlay.hidden = true; }, 160);
    previousFocus?.focus?.();
  }

  function installNav() {
    const nav = document.querySelector("#primary-nav.primary-nav");
    if (!nav || nav.dataset.v37Shell === "true") return Boolean(nav);
    nav.dataset.v37Shell = "true";
    nav.innerHTML = `
      <a href="/conditions/">Concerns</a>
      <a href="/#v37-finder">Find your route</a>
      <a href="/treatments/">Treatments</a>
      <a href="/dr-cheena-langer/">Doctor</a>
      <a href="/#v37-clinics">Clinics</a>
      <button type="button" class="v37-explore-trigger" data-v37-explore-trigger aria-haspopup="dialog">Explore</button>
      <a class="button button-small v37-book" href="/book-appointment/">Book consultation</a>`;

    const current = window.location.pathname.replace(/index\.html$/, "");
    nav.querySelectorAll("a").forEach((link) => {
      const url = new URL(link.href, window.location.origin);
      const href = url.pathname.replace(/index\.html$/, "");
      const active = !url.hash && (href === current || (href !== "/" && current.startsWith(href)));
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });

    if (current === "/" && "IntersectionObserver" in window) {
      const pairs = [...nav.querySelectorAll('a[href*="#"]')]
        .map((link) => {
          const url = new URL(link.href, window.location.origin);
          if (url.origin !== window.location.origin || url.pathname !== "/" || !url.hash) return null;
          return { link, section: document.querySelector(url.hash) };
        })
        .filter(Boolean)
        .filter(({ section }) => section);

      if (pairs.length) {
        const ratios = new Map();
        const setCurrentSection = (section) => {
          pairs.forEach(({ link, section: target }) => {
            if (target === section) link.setAttribute("aria-current", "location");
            else if (link.getAttribute("aria-current") === "location") link.removeAttribute("aria-current");
          });
        };

        const observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => ratios.set(entry.target, entry.intersectionRatio));
          let best = null;
          let score = -1;
          pairs.forEach(({ section }) => {
            const ratio = ratios.get(section) || 0;
            if (ratio > score) {
              best = section;
              score = ratio;
            }
          });
          if (best && score > 0) setCurrentSection(best);
        }, {
          rootMargin: "-22% 0px -58% 0px",
          threshold: [0, .05, .15, .3, .55],
        });

        pairs.forEach(({ link, section }) => {
          observer.observe(section);
          link.addEventListener("click", () => setCurrentSection(section));
        });
      }
    }

    nav.querySelector("[data-v37-explore-trigger]")?.addEventListener("click", openExplore);
    return true;
  }

  function init() {
    if (!installNav()) {
      const host = document.querySelector("[data-site-header]") || document.body;
      const observer = new MutationObserver(() => {
        if (installNav()) observer.disconnect();
      });
      observer.observe(host, { childList: true, subtree: true });
      window.setTimeout(() => observer.disconnect(), 8000);
    }

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeExplore();
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openExplore();
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
