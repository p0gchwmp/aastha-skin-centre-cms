(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;
  const root = document.querySelector(".v37-home");
  if (!root) return;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Concern explorer: navigation only, never diagnosis. */
  const explorer = root.querySelector("[data-v37-concern-explorer]");
  if (explorer) {
    const tabs = [...explorer.querySelectorAll("[data-v37-concern]")];
    const title = explorer.querySelector("[data-v37-concern-title]");
    const copy = explorer.querySelector("[data-v37-concern-copy]");
    const link = explorer.querySelector("[data-v37-concern-link]");

    const selectConcern = (tab) => {
      tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
      if (title) title.textContent = tab.dataset.title || "Explore care";
      if (copy) copy.textContent = tab.dataset.copy || "";
      if (link) link.href = tab.dataset.href || "/conditions/";
    };
    tabs.forEach((tab) => tab.addEventListener("click", () => selectConcern(tab)));
  }

  /* Route finder: a deterministic site-navigation matrix, not medical advice. */
  const finder = root.querySelector("[data-v37-route-finder]");
  if (finder) {
    const choices = [...finder.querySelectorAll("[data-v37-route-choice]")];
    const title = finder.querySelector("[data-v37-route-title]");
    const copy = finder.querySelector("[data-v37-route-copy]");
    const link = finder.querySelector("[data-v37-route-link]");
    const state = { area: "face", concern: "acne" };

    const routes = {
      acne: {
        face: ["Acne & breakouts", "Explore active acne, marks and scar pathways.", "/treatments/acne-treatment/"],
        scalp: ["Scalp bumps & inflammation", "Scalp lesions can have several causes. Start with a medical dermatology assessment.", "/conditions/"],
        body: ["Body acne & breakouts", "Explore acne information and discuss body-site treatment during assessment.", "/treatments/acne-treatment/"]
      },
      pigmentation: {
        face: ["Pigmentation & uneven tone", "Explore melasma, post-inflammatory pigmentation, freckles and related facial colour changes.", "/treatments/pigmentation-treatment/"],
        scalp: ["Scalp colour change", "Start with medical assessment because scalp pigmentation or discoloration can have different causes.", "/conditions/"],
        body: ["Body pigmentation", "Explore pigmentation care and discuss the exact site, trigger and skin type during consultation.", "/treatments/pigmentation-treatment/"]
      },
      hair: {
        face: ["Facial hair concern", "For unwanted facial hair, explore laser hair reduction. For patchy facial hair loss, start with assessment.", "/treatments/laser-hair-reduction/"],
        scalp: ["Hair fall & scalp", "Explore shedding, thinning, alopecia patterns and scalp assessment.", "/treatments/hair-fall-treatment/"],
        body: ["Unwanted body hair", "Explore dermatologist-guided laser hair reduction by skin type, hair thickness and treatment area.", "/treatments/laser-hair-reduction/"]
      },
      rash: {
        face: ["Facial rash or irritation", "Rashes can look similar but have different causes. Start with medical dermatology information.", "/conditions/"],
        scalp: ["Scalp rash, itch or dandruff", "Explore scalp concerns and dermatitis pathways before choosing treatment.", "/treatments/seborrheic-dermatitis-dandruff/"],
        body: ["Rash, itching or infection", "Explore eczema, allergy, fungal infection and other medical skin pathways.", "/conditions/"]
      },
      ageing: {
        face: ["Skin quality & ageing", "Explore options for texture, hydration, fine lines, volume and firmness after facial assessment.", "/treatments/"],
        scalp: ["Age-related hair change", "Explore hair thinning and scalp assessment rather than an aesthetic skin pathway.", "/treatments/hair-fall-treatment/"],
        body: ["Body skin quality", "Start from the treatment directory and discuss the exact concern and expected outcome during assessment.", "/treatments/"]
      }
    };

    const renderRoute = () => {
      const result = routes[state.concern]?.[state.area] || routes.acne.face;
      if (title) title.textContent = result[0];
      if (copy) copy.textContent = result[1];
      if (link) link.href = result[2];
    };

    choices.forEach((button) => button.addEventListener("click", () => {
      const group = button.dataset.group;
      if (!group) return;
      state[group] = button.dataset.value || state[group];
      choices
        .filter((item) => item.dataset.group === group)
        .forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      renderRoute();
    }));
  }

  /* Mouse/touch-friendly horizontal treatment rail. */
  const rail = root.querySelector("[data-v37-drag-rail]");
  if (rail) {
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
    const endDrag = (event) => {
      if (!active) return;
      active = false;
      rail.releasePointerCapture?.(event.pointerId);
      rail.classList.remove("is-dragging");
    };
    rail.addEventListener("pointerup", endDrag);
    rail.addEventListener("pointercancel", endDrag);
    rail.addEventListener("click", (event) => {
      if (moved) {
        event.preventDefault();
        moved = false;
      }
    }, true);
  }

  /* Progressive reveal: cosmetic only and disabled for reduced motion. */
  if (!reducedMotion && "IntersectionObserver" in window) {
    const targets = [...root.querySelectorAll(".v37-section-head, .v37-concern-explorer, .v37-route-finder, .v37-doctor-grid, .v37-clinic-grid")];
    targets.forEach((node) => node.classList.add("v37-reveal"));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8%", threshold: 0.08 });
    targets.forEach((node) => observer.observe(node));
  }
})();
