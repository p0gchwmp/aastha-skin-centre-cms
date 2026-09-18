(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;
  const root = document.querySelector(".v37-home");
  if (!root) return;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Concern explorer: accessible navigation only, never diagnosis. */
  const explorer = root.querySelector("[data-v37-concern-explorer]");
  if (explorer) {
    const tabs = [...explorer.querySelectorAll("[data-v37-concern]")];
    const stage = explorer.querySelector(".v37-concern-stage");
    const title = explorer.querySelector("[data-v37-concern-title]");
    const copy = explorer.querySelector("[data-v37-concern-copy]");
    const link = explorer.querySelector("[data-v37-concern-link]");

    if (stage) {
      stage.id ||= "v37-concern-panel";
      stage.setAttribute("role", "tabpanel");
    }

    const selectConcern = (tab, { focus = false } = {}) => {
      tabs.forEach((item, index) => {
        item.id ||= `v37-concern-tab-${index + 1}`;
        item.setAttribute("aria-selected", String(item === tab));
        item.setAttribute("tabindex", item === tab ? "0" : "-1");
        if (stage) item.setAttribute("aria-controls", stage.id);
      });
      if (stage && tab?.id) stage.setAttribute("aria-labelledby", tab.id);
      if (title) title.textContent = tab.dataset.title || "Explore care";
      if (copy) copy.textContent = tab.dataset.copy || "";
      if (link) link.href = tab.dataset.href || "/conditions/";
      if (focus) tab.focus();
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => selectConcern(tab));
      tab.addEventListener("keydown", (event) => {
        const keys = ["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"];
        if (!keys.includes(event.key)) return;
        event.preventDefault();
        let next = index;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % tabs.length;
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        selectConcern(tabs[next], { focus: true });
      });
    });

    const initial = tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0];
    if (initial) selectConcern(initial);
  }

  /* Route finder: area-specific educational navigation, never diagnosis. */
  const finder = root.querySelector("[data-v37-route-finder]");
  if (finder) {
    const areaChoices = [...finder.querySelectorAll('[data-v37-route-choice][data-group="area"]')];
    const concernFieldset = [...finder.querySelectorAll("fieldset")][1];
    const concernHost = concernFieldset?.querySelector("div");
    const title = finder.querySelector("[data-v37-route-title]");
    const copy = finder.querySelector("[data-v37-route-copy]");
    const link = finder.querySelector("[data-v37-route-link]");
    const routeResult = finder.querySelector(".v37-route-result");
    routeResult?.setAttribute("aria-live", "polite");
    routeResult?.setAttribute("aria-atomic", "true");
    const state = { area: "face", concern: "" };

    const optionsByArea = {
      face: [
        { value: "breakouts", label: "Breakouts", title: "Acne & breakouts", copy: "Explore active acne, recurring breakouts, marks and scar pathways.", href: "/treatments/acne-treatment/" },
        { value: "pigmentation", label: "Pigmentation", title: "Pigmentation & uneven tone", copy: "Explore melasma, post-inflammatory pigmentation, freckles and related facial colour changes.", href: "/treatments/pigmentation-treatment/" },
        { value: "redness", label: "Redness", title: "Redness or irritation", copy: "Persistent facial redness and irritation can have different causes. Start with medical dermatology information.", href: "/conditions/" },
        { value: "ageing", label: "Skin ageing", title: "Skin quality & ageing", copy: "Explore information on texture, hydration, fine lines, volume and firmness before deciding on a procedure.", href: "/treatments/" },
        { value: "unwanted-hair", label: "Unwanted hair", title: "Unwanted facial hair", copy: "Explore dermatologist-guided laser hair reduction by skin type, hair thickness and treatment area.", href: "/treatments/laser-hair-reduction/" }
      ],
      scalp: [
        { value: "hair-fall", label: "Hair fall", title: "Hair fall & thinning", copy: "Explore shedding, thinning, alopecia patterns and scalp assessment before treatment selection.", href: "/treatments/hair-fall-treatment/" },
        { value: "flaking-itch", label: "Flaking & itch", title: "Flaking, itch or dandruff", copy: "Explore scalp flaking and dermatitis information before choosing treatment.", href: "/treatments/seborrheic-dermatitis-dandruff/" },
        { value: "smooth-patches", label: "Smooth patches", title: "Smooth patches of hair loss", copy: "Patchy hair loss has several possible causes. Start with the alopecia areata guide and dermatologist-led assessment pathway.", href: "/treatments/alopecia-areata-treatment/" },
        { value: "scalp-bumps", label: "Scalp bumps", title: "Scalp bumps or inflammation", copy: "Scalp bumps can have several causes. Start with medical dermatology information rather than a procedure.", href: "/conditions/" }
      ],
      body: [
        { value: "rash-infection", label: "Rash / infection", title: "Rash, itching or infection", copy: "Explore eczema, allergy, fungal infection and other medical skin pathways.", href: "/conditions/" },
        { value: "body-acne", label: "Body acne", title: "Body acne & breakouts", copy: "Explore acne information and discuss body-site treatment during assessment.", href: "/treatments/acne-treatment/" },
        { value: "dark-patches", label: "Dark patches", title: "Dark patches & pigmentation", copy: "Explore pigmentation information and discuss the exact site, trigger and skin type during consultation.", href: "/treatments/pigmentation-treatment/" },
        { value: "unwanted-hair", label: "Unwanted hair", title: "Unwanted body hair", copy: "Explore dermatologist-guided laser hair reduction by skin type, hair thickness and treatment area.", href: "/treatments/laser-hair-reduction/" },
        { value: "growth-lump", label: "Growth / lump", title: "Skin growth or lump", copy: "A changing, painful, bleeding or persistent growth should be assessed before any removal pathway is chosen.", href: "/treatments/wart-mole-skin-tag-removal/" }
      ]
    };

    const renderRoute = () => {
      const options = optionsByArea[state.area] || optionsByArea.face;
      const result = options.find((item) => item.value === state.concern) || options[0];
      if (!result) return;
      state.concern = result.value;
      if (title) title.textContent = result.title;
      if (copy) copy.textContent = result.copy;
      if (link) link.href = result.href;
    };

    const renderConcerns = () => {
      if (!concernHost) return;
      const options = optionsByArea[state.area] || optionsByArea.face;
      if (!options.some((item) => item.value === state.concern)) {
        state.concern = options[0]?.value || "";
      }
      concernHost.replaceChildren(...options.map((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.v37RouteChoice = "";
        button.dataset.group = "concern";
        button.dataset.value = item.value;
        button.setAttribute("aria-pressed", String(item.value === state.concern));
        button.textContent = item.label;
        button.addEventListener("click", () => {
          state.concern = item.value;
          [...concernHost.querySelectorAll("button")].forEach((choice) => {
            choice.setAttribute("aria-pressed", String(choice === button));
          });
          renderRoute();
        });
        return button;
      }));
      renderRoute();
    };

    areaChoices.forEach((button) => button.addEventListener("click", () => {
      state.area = button.dataset.value || "face";
      areaChoices.forEach((choice) => {
        choice.setAttribute("aria-pressed", String(choice === button));
      });
      state.concern = "";
      renderConcerns();
    }));

    renderConcerns();
  }

  /* Mouse/touch-friendly horizontal treatment rail. */
  const rail = root.querySelector("[data-v37-drag-rail]");
  if (rail) {
    const cards = [...rail.children].filter((node) => node.matches?.("a"));
    const controls = document.createElement("div");
    controls.className = "v37-actions";
    controls.setAttribute("aria-label", "Treatment library navigation");
    controls.innerHTML = `
      <button type="button" class="button button-secondary" data-v37-rail-prev aria-label="Previous treatment">← Previous</button>
      <span class="v37-kicker" data-v37-rail-counter aria-live="polite">1 / ${Math.max(cards.length, 1)}</span>
      <button type="button" class="button button-secondary" data-v37-rail-next aria-label="Next treatment">Next →</button>`;
    rail.insertAdjacentElement("afterend", controls);

    const previous = controls.querySelector("[data-v37-rail-prev]");
    const next = controls.querySelector("[data-v37-rail-next]");
    const counter = controls.querySelector("[data-v37-rail-counter]");

    const cardLeft = (card) => (
      rail.scrollLeft + card.getBoundingClientRect().left - rail.getBoundingClientRect().left
    );
    const currentIndex = () => {
      if (!cards.length) return 0;
      let best = 0;
      let distance = Infinity;
      cards.forEach((card, index) => {
        const delta = Math.abs(card.getBoundingClientRect().left - rail.getBoundingClientRect().left);
        if (delta < distance) {
          best = index;
          distance = delta;
        }
      });
      return best;
    };
    const updateRailControls = () => {
      const index = currentIndex();
      if (counter) counter.textContent = `${Math.min(index + 1, Math.max(cards.length, 1))} / ${Math.max(cards.length, 1)}`;
      if (previous) previous.disabled = index <= 0;
      if (next) next.disabled = index >= cards.length - 1;
    };
    const moveRail = (direction) => {
      if (!cards.length) return;
      const target = Math.max(0, Math.min(cards.length - 1, currentIndex() + direction));
      rail.scrollTo({ left: cardLeft(cards[target]), behavior: reducedMotion ? "auto" : "smooth" });
    };

    previous?.addEventListener("click", () => moveRail(-1));
    next?.addEventListener("click", () => moveRail(1));
    let railFrame = 0;
    rail.addEventListener("scroll", () => {
      if (railFrame) return;
      railFrame = requestAnimationFrame(() => {
        railFrame = 0;
        updateRailControls();
      });
    }, { passive: true });
    window.addEventListener("resize", updateRailControls, { passive: true });
    updateRailControls();

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

})();\n