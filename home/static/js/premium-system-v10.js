/* Aastha V10 compatibility and long-article rail safeguards. */
(() => {
  const isRetiredAcneAsset = node => {
    if (!(node instanceof Element)) return false;
    const source = node.getAttribute("href") || node.getAttribute("src") || "";
    return source.includes("premium-v5-acne-structure") ||
      source.includes("premium-v5-acne-results");
  };

  /* A previous cached bundle appended acne-only CSS after the shared system.
     Block only those two retired assets while that cached bundle ages out. */
  if (location.pathname === "/treatments/acne-treatment/") {
    document.querySelectorAll(
      '[data-v5-acne-structure], [data-v5-acne-results]',
    ).forEach(node => node.remove());

    const originalAppendChild = Node.prototype.appendChild;
    Node.prototype.appendChild = function appendSharedArticleAsset(node) {
      if (isRetiredAcneAsset(node)) return node;
      return originalAppendChild.call(this, node);
    };

    window.addEventListener("DOMContentLoaded", () => {
      window.setTimeout(() => {
        Node.prototype.appendChild = originalAppendChild;
        document.querySelectorAll(
          '[data-v5-acne-structure], [data-v5-acne-results]',
        ).forEach(node => node.remove());
      }, 0);
    }, { once: true });
  }

  const keepActiveRailLinkVisible = rail => {
    const link = rail.querySelector('a[aria-current="location"]');
    if (!link || rail.scrollHeight <= rail.clientHeight) return;
    const railRect = rail.getBoundingClientRect();
    const linkRect = link.getBoundingClientRect();
    const linkTop = linkRect.top - railRect.top + rail.scrollTop;
    const linkBottom = linkTop + linkRect.height;
    const visibleTop = rail.scrollTop + 52;
    const visibleBottom = rail.scrollTop + rail.clientHeight - 18;
    if (linkTop >= visibleTop && linkBottom <= visibleBottom) return;
    rail.scrollTo({
      top: Math.max(0, linkTop - rail.clientHeight * .42),
      behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
    });
  };

  window.addEventListener("DOMContentLoaded", () => {
    window.setTimeout(() => {
      const rail = document.querySelector(".v8-page-rail");
      if (!rail) return;
      keepActiveRailLinkVisible(rail);
      const observer = new MutationObserver(() => keepActiveRailLinkVisible(rail));
      observer.observe(rail, {
        subtree: true,
        attributes: true,
        attributeFilter: ["aria-current"],
      });
      rail.addEventListener("click", () => {
        window.setTimeout(() => keepActiveRailLinkVisible(rail), 80);
      });
    }, 0);
  }, { once: true });
})();
