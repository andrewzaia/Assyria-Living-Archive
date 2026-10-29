/* Accessible progressive filter: without JavaScript all studies remain visible. */
(function () {
  "use strict";
  const root = document.querySelector(".samaria-room");
  if (!root) return;
  const buttons = [...root.querySelectorAll("[data-samaria-filter]")];
  const articles = [...root.querySelectorAll("[data-samaria-stage]")];
  const count = root.querySelector(".samaria-filter-count");
  const apply = (stage) => {
    let visible = 0;
    for (const article of articles) {
      const show = stage === "all" || article.dataset.samariaStage === stage;
      article.hidden = !show;
      if (show) visible++;
    }
    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.samariaFilter === stage));
    }
    if (count) count.textContent = visible + (visible === 1 ? " study displayed" : " studies displayed");
  };
  for (const button of buttons) {
    button.addEventListener("click", () => apply(button.dataset.samariaFilter));
  }
  // Deep links always reveal their named case, including when a filter was selected.
  window.addEventListener("hashchange", () => {
    const article = articles.find((node) => "#" + node.id === window.location.hash);
    if (article) apply("all");
  });
})();
