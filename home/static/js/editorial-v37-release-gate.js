(() => {
  const patchHydratedShell = () => {
    const brand = document.querySelector('[data-site-header] a.brand[href="/"]');
    if (brand) {
      // Let the visible brand text provide the accessible name. An explicit
      // aria-label hid visible copy from Lighthouse's label-content-name audit.
      brand.removeAttribute('aria-label');
    }
  };

  const headerRoot = document.querySelector('[data-site-header]');
  if (!headerRoot) return;

  patchHydratedShell();
  const observer = new MutationObserver(() => {
    patchHydratedShell();
    if (headerRoot.querySelector('a.brand[href="/"]')) observer.disconnect();
  });
  observer.observe(headerRoot, { childList: true, subtree: true });
})();
