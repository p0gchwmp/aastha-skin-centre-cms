(() => {
  const load = () => {
    if (!document.querySelector('link[data-v5-content-interactions]')) {
      const style = document.createElement("link");
      style.rel = "stylesheet";
      style.href = "/assets/css/premium-v5-content-interactions.css";
      style.dataset.v5ContentInteractions = "true";
      document.head.append(style);
    }

    if (!document.querySelector('script[data-v5-content-interactions]')) {
      const script = document.createElement("script");
      script.src = "/assets/js/premium-v5-content-interactions.js";
      script.defer = true;
      script.dataset.v5ContentInteractions = "true";
      document.body.append(script);
    }
  };

  if (document.readyState === "complete") load();
  else window.addEventListener("load", load, { once: true });
})();
