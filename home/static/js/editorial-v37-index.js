(() => {
  if (!document.documentElement.classList.contains("editorial-v37")) return;

  function initDirectory() {
    const grid = document.querySelector("[data-v37-directory-grid]");
    const input = document.querySelector("[data-v37-directory-search]");
    if (!grid || !input) return;
    const cards = [...grid.querySelectorAll("[data-v37-directory-card]")];
    const count = document.querySelector("[data-v37-directory-count]");
    const empty = document.querySelector("[data-v37-directory-empty]");

    const update = () => {
      const query = input.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const haystack = String(card.dataset.search || card.textContent || "").toLowerCase();
        const match = !query || haystack.includes(query);
        card.hidden = !match;
        if (match) visible += 1;
      });
      if (count) count.textContent = `${visible} shown`;
      if (empty) empty.hidden = visible !== 0;
    };

    input.addEventListener("input", update);
    update();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initDirectory, { once: true });
  else initDirectory();
})();
