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

  // Preserve the native anchor as the only keyboard target. Pointer users may
  // click the card surface, while keyboard users activate the real link with
  // its valid semantics and visible focus treatment.
  document.querySelectorAll("[data-card-link]").forEach(card => {
    const link = card.querySelector("a[href]");
    if (!link) return;
    card.addEventListener("click", event => {
      if (event.target.closest("a,button,input,select,textarea")) return;
      link.click();
    });
  });
})();
