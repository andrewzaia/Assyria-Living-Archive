(() => {
  'use strict';
  const query = document.getElementById('concordance-query');
  const category = document.getElementById('concordance-type');
  const count = document.getElementById('concordance-count');
  const empty = document.getElementById('concordance-no-results');
  if (!query || !category || !count || !empty) return;
  const terms = [...document.querySelectorAll('.concordance-term')];
  const normal = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
  const update = () => {
    const text = normal(query.value);
    const kind = category.value;
    let visible = 0;
    for (const term of terms) {
      const matched = (!text || normal(term.dataset.search || '').includes(text)) && (!kind || term.dataset.type === kind);
      term.hidden = !matched;
      if (matched) visible += 1;
    }
    count.textContent = visible === terms.length ? 'Showing all ' + visible + ' curated terms.' :
      'Showing ' + visible + ' of ' + terms.length + ' curated terms.';
    empty.hidden = visible !== 0;
  };
  query.addEventListener('input', update);
  category.addEventListener('change', update);
  const focusHash = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id || !id.startsWith('entry-')) return;
    const target = document.getElementById(id);
    if (!target || !target.hidden) return;
    query.value = '';
    category.value = '';
    update();
  };
  window.addEventListener('hashchange', focusHash);
  focusHash();
})();