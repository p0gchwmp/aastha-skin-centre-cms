(() => {
  document.documentElement.classList.add("professional-site");

  const header = document.querySelector(".site-header");
  if (header) {
    const updateHeader = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
    window.addEventListener("scroll", updateHeader, { passive: true });
    updateHeader();
  }

  // Do not let the generic long-article TOC clutter the curated homepage.
  if (document.querySelector(".home-main")) {
    document.querySelectorAll(".article-toc, .reading-progress").forEach(node => node.remove());
  }

  // Native FAQ details: keep one open at a time for a cleaner experience.
  document.querySelectorAll(".faq-pro-list details").forEach(item => {
    item.addEventListener("toggle", () => {
      if (!item.open) return;
      item.parentElement?.querySelectorAll("details[open]").forEach(other => {
        if (other !== item) other.open = false;
      });
    });
  });

  // Make cards keyboard accessible when the entire card contains one main link.
  document.querySelectorAll("[data-card-link]").forEach(card => {
    const link = card.querySelector("a[href]");
    if (!link) return;
    card.tabIndex = 0;
    card.setAttribute("role", "link");
    card.addEventListener("click", event => {
      if (event.target.closest("a,button,input,select,textarea")) return;
      link.click();
    });
    card.addEventListener("keydown", event => {
      if (event.key === "Enter") link.click();
    });
  });
})();
