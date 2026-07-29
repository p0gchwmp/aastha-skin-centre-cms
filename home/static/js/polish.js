(() => {
  const main = document.querySelector("main");
  if (!main) return;

  // Reading progress for long content pages.
  const prose = main.querySelector(".prose");
  if (prose && prose.textContent.trim().length > 2200) {
    const progress = document.createElement("div");
    progress.className = "reading-progress";
    progress.setAttribute("aria-hidden", "true");
    document.body.appendChild(progress);

    const updateProgress = () => {
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const percentage = documentHeight > 0
        ? Math.min(100, Math.max(0, (window.scrollY / documentHeight) * 100))
        : 0;
      progress.style.width = `${percentage}%`;
    };

    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();
  }

  // Automatic table of contents on long medical pages.
  if (prose && !prose.querySelector(".article-toc")) {
    const headings = [...prose.querySelectorAll(":scope > h2")]
      .filter(heading => !heading.closest(".medical-disclaimer"))
      .slice(0, 12);

    if (headings.length >= 4) {
      headings.forEach((heading, index) => {
        if (!heading.id) {
          const base = heading.textContent
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9\s-]/g, "")
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-")
            .slice(0, 70) || `section-${index + 1}`;
          let candidate = base;
          let suffix = 2;
          while (document.getElementById(candidate)) {
            candidate = `${base}-${suffix++}`;
          }
          heading.id = candidate;
        }
      });

      const toc = document.createElement("nav");
      toc.className = "article-toc";
      toc.setAttribute("aria-label", "On this page");
      toc.innerHTML = `
        <h2>On this page</h2>
        <ol>
          ${headings.map(heading =>
            `<li><a href="#${heading.id}">${heading.textContent.trim()}</a></li>`
          ).join("")}
        </ol>
      `;

      prose.insertBefore(toc, prose.firstElementChild);
    }
  }

  // Back-to-top button.
  const backToTop = document.createElement("button");
  backToTop.type = "button";
  backToTop.className = "back-to-top";
  backToTop.setAttribute("aria-label", "Back to top");
  backToTop.textContent = "↑";
  document.body.appendChild(backToTop);

  const updateBackToTop = () => {
    backToTop.classList.toggle("is-visible", window.scrollY > 650);
  };

  window.addEventListener("scroll", updateBackToTop, { passive: true });
  backToTop.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth"
    });
  });
  updateBackToTop();

  // External links opened in a new tab should be explicitly safe.
  document.querySelectorAll('a[target="_blank"]').forEach(link => {
    const current = new Set((link.getAttribute("rel") || "").split(/\s+/).filter(Boolean));
    current.add("noopener");
    current.add("noreferrer");
    link.setAttribute("rel", [...current].join(" "));
  });

  // Add accessible labels to icon-only controls if any slipped through.
  document.querySelectorAll("button").forEach(button => {
    if (!button.textContent.trim() && !button.getAttribute("aria-label")) {
      button.setAttribute("aria-label", "Website control");
    }
  });
})();
