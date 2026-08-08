(() => {
  if (!document.body.classList.contains("cms-home-page")) return;
  if (document.querySelector('link[data-v5-home-contrast]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/assets/css/premium-v5-home-contrast.css";
  link.dataset.v5HomeContrast = "true";
  document.head.appendChild(link);
})();
