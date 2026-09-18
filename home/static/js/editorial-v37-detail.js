(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;
  const root = document.querySelector(".v37-detail");
  if (!root) return;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  root.querySelectorAll("[data-v37-choice-matrix]").forEach((matrix, matrixIndex) => {
    const choices = [...matrix.querySelectorAll("[data-v37-choice]")];
    const title = matrix.querySelector("[data-v37-choice-title]");
    const copy = matrix.querySelector("[data-v37-choice-copy]");
    const panel = matrix.querySelector(".v37-choice-result");
    if (panel) {
      panel.id ||= `v37-choice-panel-${matrixIndex + 1}`;
      panel.setAttribute("role", "tabpanel");
    }

    const select = (choice, { focus = false } = {}) => {
      choices.forEach((item, index) => {
        item.id ||= `v37-choice-${matrixIndex + 1}-${index + 1}`;
        item.setAttribute("role", "tab");
        item.setAttribute("aria-selected", String(item === choice));
        item.tabIndex = item === choice ? 0 : -1;
        if (panel) item.setAttribute("aria-controls", panel.id);
      });
      if (panel && choice?.id) panel.setAttribute("aria-labelledby", choice.id);
      if (title) title.textContent = choice.dataset.title || "Selected pattern";
      if (copy) copy.textContent = choice.dataset.copy || "";
      if (focus) choice.focus({ preventScroll: true });
    };

    choices.forEach((choice, index) => {
      choice.addEventListener("click", () => select(choice));
      choice.addEventListener("keydown", (event) => {
        let next = null;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % choices.length;
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + choices.length) % choices.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = choices.length - 1;
        if (next === null) return;
        event.preventDefault();
        select(choices[next], { focus: true });
      });
    });

    const initial = choices.find((choice) => choice.getAttribute("aria-selected") === "true") || choices[0];
    if (initial) select(initial);
  });

  root.querySelectorAll("[data-v37-atlas]").forEach((atlas, atlasIndex) => {
    const choices = [...atlas.querySelectorAll("[data-v37-atlas-choice]")];
    const nav = atlas.querySelector(".v37-atlas-nav");
    const stage = atlas.querySelector(".v37-atlas-stage");
    const title = atlas.querySelector("[data-v37-atlas-title]");
    const copy = atlas.querySelector("[data-v37-atlas-copy]");
    const links = atlas.querySelector("[data-v37-atlas-links]");
    if (nav) {
      nav.setAttribute("role", "tablist");
      nav.setAttribute("aria-orientation", "vertical");
    }
    if (stage) {
      stage.id ||= `v37-atlas-panel-${atlasIndex + 1}`;
      stage.setAttribute("role", "tabpanel");
    }

    const select = (choice, { focus = false } = {}) => {
      choices.forEach((item, index) => {
        item.id ||= `v37-atlas-tab-${atlasIndex + 1}-${index + 1}`;
        item.setAttribute("role", "tab");
        item.setAttribute("aria-selected", String(item === choice));
        item.tabIndex = item === choice ? 0 : -1;
        if (stage) item.setAttribute("aria-controls", stage.id);
      });
      if (stage && choice?.id) stage.setAttribute("aria-labelledby", choice.id);
      if (title) title.textContent = choice.dataset.title || "Selected pathway";
      if (copy) copy.textContent = choice.dataset.copy || "";
      if (links) {
        links.innerHTML = "";
        try {
          const data = JSON.parse(choice.dataset.links || "[]");
          data.forEach(([label, href]) => {
            const anchor = document.createElement("a");
            anchor.href = href;
            anchor.textContent = `${label} →`;
            links.appendChild(anchor);
          });
        } catch (_) {}
      }
      if (focus) choice.focus({ preventScroll: true });
    };

    choices.forEach((choice, index) => {
      choice.addEventListener("click", () => select(choice));
      choice.addEventListener("keydown", (event) => {
        let next = null;
        if (event.key === "ArrowDown" || event.key === "ArrowRight") next = (index + 1) % choices.length;
        if (event.key === "ArrowUp" || event.key === "ArrowLeft") next = (index - 1 + choices.length) % choices.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = choices.length - 1;
        if (next === null) return;
        event.preventDefault();
        select(choices[next], { focus: true });
      });
    });

    const initial = choices.find((choice) => choice.getAttribute("aria-selected") === "true") || choices[0];
    if (initial) select(initial);
  });

  root.querySelectorAll("[data-v37-story]").forEach((story) => {
    const steps = [...story.querySelectorAll("[data-v37-story-step]")];
    const title = story.querySelector("[data-v37-story-title]");
    const copy = story.querySelector("[data-v37-story-copy]");
    const activate = (step) => {
      steps.forEach((item) => item.classList.toggle("is-active", item === step));
      if (title) title.textContent = step.dataset.title || step.querySelector("h3")?.textContent || "";
      if (copy) copy.textContent = step.dataset.copy || step.querySelector("p")?.textContent || "";
    };
    if ("IntersectionObserver" in window && !reducedMotion) {
      const observer = new IntersectionObserver((entries) => {
        const active = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (active) activate(active.target);
      }, { rootMargin: "-28% 0px -42%", threshold: [0.15, .35, .6] });
      steps.forEach((step) => observer.observe(step));
    }
  });

  root.querySelectorAll("[data-v37-symptoms]").forEach((host) => {
    const chips = [...host.querySelectorAll("[data-v37-symptom]")];
    const title = host.querySelector("[data-v37-symptom-title]");
    const copy = host.querySelector("[data-v37-symptom-copy]");
    chips.forEach((chip) => chip.addEventListener("click", () => {
      chips.forEach((item) => item.setAttribute("aria-pressed", String(item === chip)));
      if (title) title.textContent = chip.dataset.title || chip.textContent.trim();
      if (copy) copy.textContent = chip.dataset.copy || "";
    }));
  });

  root.querySelectorAll(".v37-accordion").forEach((stack) => {
    const details = [...stack.querySelectorAll(":scope > details")];
    details.forEach((item) => item.addEventListener("toggle", () => {
      if (!item.open) return;
      details.forEach((other) => {
        if (other !== item) other.removeAttribute("open");
      });
    }));
  });

  root.querySelectorAll("[data-v37-drag-rail]").forEach((rail) => {
    let active = false;
    let startX = 0;
    let startScroll = 0;
    let moved = false;
    rail.addEventListener("pointerdown", (event) => {
      if (event.pointerType === "touch") return;
      active = true;
      moved = false;
      startX = event.clientX;
      startScroll = rail.scrollLeft;
      rail.setPointerCapture?.(event.pointerId);
      rail.classList.add("is-dragging");
    });
    rail.addEventListener("pointermove", (event) => {
      if (!active) return;
      const distance = event.clientX - startX;
      if (Math.abs(distance) > 5) moved = true;
      rail.scrollLeft = startScroll - distance;
    });
    const end = (event) => {
      if (!active) return;
      active = false;
      rail.releasePointerCapture?.(event.pointerId);
      rail.classList.remove("is-dragging");
    };
    rail.addEventListener("pointerup", end);
    rail.addEventListener("pointercancel", end);
    rail.addEventListener("click", (event) => {
      if (!moved) return;
      event.preventDefault();
      moved = false;
    }, true);
  });

  const clinicSwitch = root.querySelector("[data-v37-clinic-switch]");
  if (clinicSwitch) {
    const tabs = [...clinicSwitch.querySelectorAll("[data-v37-clinic-choice]")];
    const panel = clinicSwitch.querySelector("[data-v37-clinic-panel]") || clinicSwitch;
    const name = clinicSwitch.querySelector("[data-v37-clinic-name]");
    const address = clinicSwitch.querySelector("[data-v37-clinic-address]");
    const hours = clinicSwitch.querySelector("[data-v37-clinic-hours]");
    const details = clinicSwitch.querySelector("[data-v37-clinic-details]");
    const directions = clinicSwitch.querySelector("[data-v37-clinic-directions]");

    panel.id ||= "v37-clinic-panel";
    panel.setAttribute("role", "tabpanel");

    const select = (tab, { focus = false } = {}) => {
      tabs.forEach((item, index) => {
        item.id ||= `v37-clinic-tab-${index + 1}`;
        item.setAttribute("role", "tab");
        item.setAttribute("aria-selected", String(item === tab));
        item.tabIndex = item === tab ? 0 : -1;
        item.setAttribute("aria-controls", panel.id);
      });
      if (tab?.id) panel.setAttribute("aria-labelledby", tab.id);
      if (name) name.textContent = tab.dataset.name || "Aastha Skin Centre";
      if (address) address.textContent = tab.dataset.address || "";
      if (hours) hours.innerHTML = tab.dataset.hours || "";
      if (details) details.href = tab.dataset.details || "/locations/";
      if (directions) directions.href = tab.dataset.directions || "/locations/";
      if (!reducedMotion) {
        window.dispatchEvent(new CustomEvent("aastha:v37-motion", {
          detail: { target: panel, kind: "swap" },
        }));
      }
      if (focus) tab.focus({ preventScroll: true });
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (event) => {
        let next = null;
        if (event.key === "ArrowDown" || event.key === "ArrowRight") next = (index + 1) % tabs.length;
        if (event.key === "ArrowUp" || event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        if (next === null) return;
        event.preventDefault();
        select(tabs[next], { focus: true });
      });
    });

    const initial = tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0];
    if (initial) select(initial);
  }

  if (!reducedMotion && "IntersectionObserver" in window) {
    const targets = [...root.querySelectorAll(".v37-detail-head, .v37-choice-matrix, .v37-reading-grid, .v37-facts, .v37-atlas, .v37-directory, .v37-fact-table")];
    targets.forEach((node) => node.classList.add("v37-reveal"));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8%", threshold: .08 });
    targets.forEach((node) => observer.observe(node));
  }
})();
