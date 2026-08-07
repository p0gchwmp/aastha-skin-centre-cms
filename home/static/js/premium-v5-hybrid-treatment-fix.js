(() => {
  if (!document.body.classList.contains("cms-home-page")) return;
  if (document.querySelector('link[data-v5-hybrid-treatment-fix]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/assets/css/premium-v5-hybrid-treatment-fix.css";
  link.dataset.v5HybridTreatmentFix = "true";
  document.head.append(link);
})();
