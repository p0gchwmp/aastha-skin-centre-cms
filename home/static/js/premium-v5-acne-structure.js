/*
 * Retained as a compatibility asset for cached exact-page markup.
 * Acne now uses the same V8/V10 article rail, typography, gallery and
 * responsive grid as every other treatment and condition page.
 */
(() => {
  if (document.body.dataset.pageSlug !== "acne-treatment") return;
  document.body.classList.add("acne-shared-article-system");
})();
