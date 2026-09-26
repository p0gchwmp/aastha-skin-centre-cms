(() => {
  const patchHydratedShell = () => {
    const brand = document.querySelector('[data-site-header] a.brand[href="/"]');
    if (brand) {
      const visibleName = brand.querySelector('strong')?.textContent?.trim() || 'Aastha Skin Centre';
      brand.setAttribute('aria-label', `${visibleName} — home`);
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
