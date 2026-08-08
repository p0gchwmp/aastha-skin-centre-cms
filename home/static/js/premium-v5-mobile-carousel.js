(() => {
  if (!document.body.classList.contains("cms-home-page")) return;

  const mobile = window.matchMedia("(max-width: 700px)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let cleanup = null;

  const setup = () => {
    if (cleanup) {
      cleanup();
      cleanup = null;
    }
    if (!mobile.matches) return;

    const grid = document.querySelector(".treatment-grid");
    if (!grid) return;
    const cards = [...grid.querySelectorAll(":scope > .treatment-card")];
    if (cards.length < 2) return;

    const controls = document.querySelector(".v5-treatment-controls");
    const prev = controls?.querySelector("button:first-of-type") || null;
    const next = controls?.querySelector("button:last-of-type") || null;
    const progress = controls?.querySelector(".v5-treatment-progress") || null;

    grid.classList.add("v5-mobile-pager");
    let index = 0;

    const render = () => {
      cards.forEach((card, cardIndex) => {
        const active = cardIndex === index;
        card.classList.toggle("v5-mobile-active", active);
        card.hidden = !active;
        card.setAttribute("aria-hidden", active ? "false" : "true");
      });
      if (progress) progress.textContent = `${index + 1} / ${cards.length}`;
      if (prev) prev.disabled = index === 0;
      if (next) next.disabled = index === cards.length - 1;
    };

    const go = nextIndex => {
      const safe = Math.max(0, Math.min(cards.length - 1, nextIndex));
      if (safe === index) return;
      const old = cards[index];
      index = safe;
      render();
      const active = cards[index];
      if (!reducedMotion && active?.animate) {
        active.animate(
          [
            { opacity: 0, transform: "translateX(12px)" },
            { opacity: 1, transform: "translateX(0)" },
          ],
          { duration: 260, easing: "cubic-bezier(.2,.72,.2,1)" }
        );
      }
      if (old) old.getAnimations?.().forEach(animation => animation.cancel());
    };

    const onPrev = event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      go(index - 1);
    };
    const onNext = event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      go(index + 1);
    };
    prev?.addEventListener("click", onPrev, true);
    next?.addEventListener("click", onNext, true);

    let startX = null;
    const onPointerDown = event => {
      if (event.pointerType === "mouse" && event.button !== 0) return;
      startX = event.clientX;
    };
    const onPointerUp = event => {
      if (startX === null) return;
      const delta = event.clientX - startX;
      startX = null;
      if (Math.abs(delta) < 44) return;
      go(delta < 0 ? index + 1 : index - 1);
    };
    const onPointerCancel = () => { startX = null; };
    grid.addEventListener("pointerdown", onPointerDown, { passive: true });
    grid.addEventListener("pointerup", onPointerUp, { passive: true });
    grid.addEventListener("pointercancel", onPointerCancel, { passive: true });

    render();

    cleanup = () => {
      prev?.removeEventListener("click", onPrev, true);
      next?.removeEventListener("click", onNext, true);
      grid.removeEventListener("pointerdown", onPointerDown);
      grid.removeEventListener("pointerup", onPointerUp);
      grid.removeEventListener("pointercancel", onPointerCancel);
      grid.classList.remove("v5-mobile-pager");
      cards.forEach(card => {
        card.hidden = false;
        card.removeAttribute("aria-hidden");
        card.classList.remove("v5-mobile-active");
      });
    };
  };

  const boot = () => {
    /* V5 reference controls are created by the preceding deferred script. */
    window.setTimeout(setup, 0);
  };

  mobile.addEventListener?.("change", setup);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
