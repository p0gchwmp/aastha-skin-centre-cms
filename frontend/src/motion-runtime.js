/** Self-hosted Motion.dev runtime for editorial v37. Motion package pinned in frontend/package.json. */
import { animate, inView, scroll, stagger } from "motion";

if (document.documentElement.classList.contains("editorial-v37")) {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.dataset.motionEngine = "motion-13.4.0";

  if (!reduced) {
    const hero = document.querySelector(".v37-home .v37-editorial-hero, .v37-detail .v37-detail-hero");
    if (hero) {
      const parts = [...hero.querySelectorAll(".v37-kicker, h1, p, .v37-actions a, .v37-actions button")];
      if (parts.length) {
        animate(parts, { opacity: [0, 1], y: [18, 0] }, {
          duration: 0.62,
          delay: stagger(0.055),
          ease: [0.22, 1, 0.36, 1],
        });
      }

      const visual = hero.querySelector(".v37-hero-art img, .v37-detail-media img, picture img, img");
      if (visual) {
        const parallax = animate(visual, { transform: ["translateY(10px) scale(1.015)", "translateY(-18px) scale(1.015)"] }, { ease: "linear" });
        scroll(parallax, { target: hero, offset: ["start end", "end start"] });
      }
    }

    const revealSelectors = [
      ".v37-directory > a",
      ".v37-drag-rail > a",
      ".v37-choice-matrix",
      ".v37-atlas",
      ".v37-facts",
      ".v37-reading-grid",
      ".process-chapter",
      ".clinical-result",
    ].join(",");

    inView(revealSelectors, (element) => {
      animate(element, { opacity: [0, 1], y: [22, 0] }, {
        duration: 0.48,
        ease: [0.22, 1, 0.36, 1],
      });
    }, { margin: "0px 0px -8% 0px", amount: 0.12 });

    document.querySelectorAll(
      ".v37-drag-rail > a, .v37-directory > a, .v37-choice-matrix button, .v37-route-controls button, .v37-concern-tabs button, [data-v37-clinic-choice]"
    ).forEach((element) => {
      element.addEventListener("pointerenter", () => {
        animate(element, { scale: 1.012, y: -2 }, { duration: 0.2, ease: [0.22, 1, 0.36, 1] });
      });
      element.addEventListener("pointerleave", () => {
        animate(element, { scale: 1, y: 0 }, { duration: 0.24, ease: [0.22, 1, 0.36, 1] });
      });
      element.addEventListener("pointerdown", () => {
        animate(element, { scale: 0.992 }, { duration: 0.09 });
      });
      element.addEventListener("pointerup", () => {
        animate(element, { scale: 1.012 }, { duration: 0.18, ease: [0.22, 1, 0.36, 1] });
      });
    });

    document.querySelectorAll(".process-nav button").forEach((button) => {
      button.addEventListener("click", () => {
        animate(button, { x: [0, 4, 0] }, { duration: 0.34, ease: [0.22, 1, 0.36, 1] });
      });
    });

    window.addEventListener("aastha:v37-motion", (event) => {
      const target = event.detail?.target;
      if (!(target instanceof Element)) return;
      if (event.detail?.kind === "swap") {
        const parts = [...target.querySelectorAll("h3, p, address, a, small")];
        if (!parts.length) return;
        animate(parts, { opacity: [0.72, 1], y: [7, 0] }, {
          duration: 0.28,
          delay: stagger(0.025),
          ease: [0.22, 1, 0.36, 1],
        });
      }
    });

    document.querySelectorAll(".v37-accordion details").forEach((details) => {
      details.addEventListener("toggle", () => {
        if (!details.open) return;
        const answer = details.querySelector(".v37-answer");
        if (!answer) return;
        animate(answer, { opacity: [0.45, 1], y: [6, 0] }, {
          duration: 0.24,
          ease: [0.22, 1, 0.36, 1],
        });
      });
    });
  }
}
