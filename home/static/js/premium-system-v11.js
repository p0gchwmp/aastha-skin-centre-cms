(() => {
  const qsa = (selector, scope = document) => [...scope.querySelectorAll(selector)];

  const normaliseQuestions = () => {
    qsa("details > summary").forEach(summary => {
      const walker = document.createTreeWalker(summary, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => { node.nodeValue = node.nodeValue.replace(/\s*\?/g, "\u202f?"); });
    });
  };

  const buildComparison = image => {
    if (image.dataset.v11Comparison === "true" || !/before-and-after/i.test(image.alt || "")) return;
    image.dataset.v11Comparison = "true";
    const install = () => {
      if (!image.naturalWidth || !image.naturalHeight || image.closest(".clinical-before-after")) return;
      const stage = document.createElement("div");
      stage.className = "clinical-before-after";
      stage.style.aspectRatio = `${image.naturalWidth / 2} / ${image.naturalHeight}`;
      const beforeLayer = document.createElement("div");
      beforeLayer.className = "clinical-before-after__layer clinical-before-after__layer--before";
      const afterLayer = document.createElement("div");
      afterLayer.className = "clinical-before-after__layer clinical-before-after__layer--after";
      const before = image.cloneNode(true);
      const after = image.cloneNode(true);
      before.removeAttribute("data-v11-comparison"); after.removeAttribute("data-v11-comparison");
      before.className = "clinical-before-after__image"; after.className = "clinical-before-after__image";
      before.alt = "Before treatment"; after.alt = "After treatment";
      before.removeAttribute("loading"); after.removeAttribute("loading");
      before.removeAttribute("srcset"); after.removeAttribute("srcset");
      before.removeAttribute("sizes"); after.removeAttribute("sizes");
      beforeLayer.append(before); afterLayer.append(after);
      const beforeLabel = document.createElement("span");
      beforeLabel.className = "clinical-before-after__label clinical-before-after__label--before";
      beforeLabel.textContent = "Before";
      const afterLabel = document.createElement("span");
      afterLabel.className = "clinical-before-after__label clinical-before-after__label--after";
      afterLabel.textContent = "After";
      const divider = document.createElement("span");
      divider.className = "clinical-before-after__divider"; divider.setAttribute("aria-hidden", "true");
      const range = document.createElement("input");
      range.className = "clinical-before-after__range"; range.type = "range"; range.min = "0"; range.max = "100"; range.value = "50";
      range.setAttribute("aria-label", "Compare before and after clinical photograph");
      range.addEventListener("input", () => stage.style.setProperty("--clinical-compare", `${range.value}%`), { passive: true });
      stage.append(beforeLayer, afterLayer, beforeLabel, afterLabel, divider, range);
      image.replaceWith(stage);
      before.removeAttribute("id"); after.removeAttribute("id");
    };
    if (image.complete && image.naturalWidth) install();
    else image.addEventListener("load", install, { once: true });
  };

  const setupComparisons = () => qsa(".clinical-results__slide > img").forEach(buildComparison);
  const boot = () => { normaliseQuestions(); setupComparisons(); document.body.classList.add("v11-ready"); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true }); else boot();
  window.addEventListener("load", () => { normaliseQuestions(); setupComparisons(); window.setTimeout(setupComparisons, 450); }, { once: true });
})();
