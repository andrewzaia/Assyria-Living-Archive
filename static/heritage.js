/* Client-side display filter only; no network requests, media uploads or storage. */
(() => {
  'use strict';
  const filter = document.getElementById('heritage-category');
  const items = [...document.querySelectorAll('[data-heritage-category]')];
  const status = document.getElementById('heritage-count');
  const empty = document.getElementById('heritage-empty');
  if (!filter || !status || !empty || !items.length) return;
  const apply = () => {
    let count = 0;
    items.forEach(item => {
      const show = filter.value === 'all' || item.dataset.heritageCategory === filter.value;
      item.hidden = !show;
      if (show) count++;
    });
    status.textContent = 'Showing ' + count + ' external reference' + (count === 1 ? '' : 's');
    empty.hidden = count !== 0;
  };
  filter.addEventListener('change', apply);
  apply();
})();
