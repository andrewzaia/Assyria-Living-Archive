/* Local filters and reader navigation. Scripture itself is generated as HTML. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const groups = [...document.querySelectorAll('[data-bible-group]')];
  const guides = [...document.querySelectorAll('[data-bible-guide]')];
  groups.forEach(button => button.addEventListener('click', () => {
    let visible = 0;
    guides.forEach(guide => { guide.hidden = button.dataset.bibleGroup !== 'all' && guide.dataset.bibleGuide !== button.dataset.bibleGroup; if (!guide.hidden) visible++; });
    groups.forEach(item => { const active = item === button; item.classList.toggle('active', active); item.setAttribute('aria-pressed', String(active)); });
    $('bible-guide-count').textContent = `${visible} reading guide${visible === 1 ? '' : 's'}`;
  }));
  const entries = [...document.querySelectorAll('[data-bible-entry]')];
  if (entries.length) {
    let limit = 30;
    const query = $('bible-query'), book = $('bible-book'), collection = $('bible-collection'), term = $('bible-term');
    const normaliseBook = text => text.toLowerCase().replace(/[.\s]/g, '');
    const bookLookup = new Map();
    [...book.options].filter(option => option.value !== 'all').forEach(option => { bookLookup.set(normaliseBook(option.text), option.value); bookLookup.set(normaliseBook(option.value), option.value); });
    bookLookup.set('psalm', 'PSA');
    const apply = () => {
      const words = query.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      const reference = /^(.*?)\s*(\d+)(?::(\d+)(?:-(\d+))?)?$/.exec(query.value.trim());
      const referenceBook = reference && bookLookup.get(normaliseBook(reference[1]));
      const textMatches = el => referenceBook ? el.dataset.book === referenceBook && Number(el.dataset.chapter) === Number(reference[2]) && (!reference[3] || (Number(el.dataset.verse) >= Number(reference[3]) && Number(el.dataset.verse) <= Number(reference[4] || reference[3]))) : words.every(word => el.dataset.search.includes(word));
      const matches = entries.filter(el => textMatches(el) && (book.value === 'all' || el.dataset.book === book.value) && (collection.value === 'all' || el.dataset.collection === collection.value) && (term.value === 'all' || JSON.parse(el.dataset.terms).includes(term.value)));
      const visible = new Set(matches.slice(0, limit));
      entries.forEach(el => el.hidden = !visible.has(el));
      $('bible-result-count').textContent = `Showing ${visible.size} of ${matches.length} matching verse entries (${entries.length} in the complete index).`;
      $('bible-more').hidden = matches.length <= limit;
      $('bible-no-results').hidden = matches.length !== 0;
    };
    [query, book, collection, term].forEach(el => el.addEventListener(el === query ? 'input' : 'change', () => { limit = 30; apply(); }));
    $('bible-more').addEventListener('click', () => { limit += 30; apply(); });
    $('bible-clear').addEventListener('click', () => { query.value = ''; book.value = collection.value = term.value = 'all'; limit = 30; apply(); query.focus(); });
    apply();
  }
  $('bible-verse-jump')?.addEventListener('change', e => { location.hash = e.target.value; });
})();
