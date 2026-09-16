(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;
  const root = document.querySelector(".v37-detail");
  if (!root) return;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  root.querySelectorAll("[data-v37-choice-matrix]").forEach((matrix) => {
    const choices = [...matrix.querySelectorAll("[data-v37-choice]")];
    const title = matrix.querySelector("[data-v37-choice-title]");
    const copy = matrix.querySelector("[data-v37-choice-copy]");
    const select = (choice) => {
      choices.forEach((item) => item.setAttribute("aria-selected", String(item === choice)));
      if (title) title.textContent = choice.dataset.title || "Selected pattern";
      if (copy) copy.textContent = choice.dataset.copy || "";
    };
    choices.forEach((choice) => choice.addEventListener("click", () => select(choice)));
  });

  root.querySelectorAll("[data-v37-atlas]").forEach((atlas) => {
    const choices = [...atlas.querySelectorAll("[data-v37-atlas-choice]")];
    const title = atlas.querySelector("[data-v37-atlas-title]");
    const copy = atlas.querySelector("[data-v37-atlas-copy]");
    const links = atlas.querySelector("[data-v37-atlas-links]");
    const select = (choice) => {
      choices.forEach((item) => item.setAttribute("aria-selected", String(item === choice)));
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
    };
    choices.forEach((choice) => choice.addEventListener("click", () => select(choice)));
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
    const name = clinicSwitch.querySelector("[data-v37-clinic-name]");
    const address = clinicSwitch.querySelector("[data-v37-clinic-address]");
    const hours = clinicSwitch.querySelector("[data-v37-clinic-hours]");
    const details = clinicSwitch.querySelector("[data-v37-clinic-details]");
    const directions = clinicSwitch.querySelector("[data-v37-clinic-directions]");
    tabs.forEach((tab) => tab.addEventListener("click", () => {
      tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
      if (name) name.textContent = tab.dataset.name || "Aastha Skin Centre";
      if (address) address.textContent = tab.dataset.address || "";
      if (hours) hours.innerHTML = tab.dataset.hours || "";
      if (details) details.href = tab.dataset.details || "/locations/";
      if (directions) directions.href = tab.dataset.directions || "/locations/";
    }));
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
