/**
 * Browser-free regression exercise for the real, entire static/app.js.
 *
 * Earlier, calling forEach on querySelector('.search-open') threw before the
 * Explore filters could bind. Execute the actual app startup with a small
 * DOM contract, not a copy of its filtering algorithm.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const script = readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), '../static/app.js'), 'utf8');
const topics = [
  'History & archaeology',
  'Language & literature',
  'Arts & traditions',
  'Faith & communities',
  'Places & heritage',
  'People & diaspora',
];
const examples = [
  ['Ashur', topics[0], 'ashur first city history'],
  ['Nineveh', topics[0], 'nineveh ancient city history'],
  ['Aramaic', topics[1], 'aramaic language words'],
  ['Music', topics[2], 'music arts assyrian'],
  ['Church of the East', topics[3], 'church faith east'],
  ['Citadel of Erbil', topics[4], 'citadel erbil heritage'],
  ['Assyrian diaspora', topics[5], 'assyrian diaspora migration'],
];

function element(textContent = '', dataset = {}) {
  const listeners = new Map();
  const attrs = new Map();
  const classes = new Set();
  return {
    textContent, dataset, hidden: false,
    listeners, attrs,
    classList: {
      toggle(name, enabled) { if (enabled) classes.add(name); else classes.delete(name); },
      contains(name) { return classes.has(name); },
    },
    setAttribute(name, value) { attrs.set(name, value); },
    addEventListener(name, cb) {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(cb);
    },
    click() { for (const cb of listeners.get('click') || []) cb({ target: this }); },
    input() { for (const cb of listeners.get('input') || []) cb({ target: this }); },
    change() { for (const cb of listeners.get('change') || []) cb({ target: this }); },
    getAttribute(name) { return attrs.get(name); },
  };
}

function start(query = '') {
  const url = new URL('https://example.org/Assyria-Living-Archive/explore/' + query);
  const buttons = [
    element('All topics', {topic: 'all'}),
    ...topics.map((label, i) => element(label, {topic: String(i)})),
  ];
  const cards = examples.map(([name, category, search]) => {
    const card = element('', {category, search});
    card.querySelector = (selector) => selector === 'h3' ? {textContent: name} : null;
    return card;
  });
  const grid = element();
  grid.querySelectorAll = (s) => s === '.article-card' ? cards : [];
  grid.appendChild = card => { const idx = cards.indexOf(card); cards.splice(idx, 1); cards.push(card); };
  const search = element();
  search.value = '';
  const sort = element();
  sort.value = 'curated';
  const count = element();
  const empty = element();
  empty.hidden = true;
  const reset = element();
  const headerSearch = element();
  const registry = new Map([
    ['#article-grid', grid], ['#article-search', search], ['#sort', sort],
    ['#result-count', count], ['#no-results', empty],
    ['#clear-filters', reset], ['.search-open', headerSearch],
  ]);
  const document = {
    querySelector: s => registry.get(s) || null,
    querySelectorAll: s => {
      if (s === '.chip[data-topic]') return buttons;
      if (s === '.search-open') return [headerSearch];
      return [];
    },
    documentElement: {dataset: {theme: 'light'}},
    addEventListener() {},
  };
  const window = {matchMedia: () => ({matches: false}), addEventListener() {}, innerWidth: 1200};
  const localStorage = {getItem() {return null;}, setItem() {}};
  const history = {replaceState(_a, _b, target) {url.href = String(target);}};
  assert.doesNotThrow(
    () => runInNewContext(script, {
      document, window, location: url, history, localStorage, URL, URLSearchParams,
      setTimeout, clearTimeout, navigator: {}, console,
    }, {timeout: 2000}),
    'The whole app must initialise - errors above the Explore setup break all category buttons',
  );
  return {url, buttons, cards, search, sort, count, empty, reset, headerSearch};
}

function visible(state) {return state.cards.filter(c => !c.hidden).map(c => c.querySelector('h3').textContent);}

test('page startup binds the header search and every Explore category', () => {
  const s = start();
  assert.equal(s.headerSearch.listeners.get('click')?.length, 1);
  assert.deepEqual(visible(s), examples.map(e => e[0]));
  assert.equal(s.count.textContent, '7 reading entries');
  assert.equal(s.buttons[0].getAttribute('aria-pressed'), 'true');
  for (const [index, category] of topics.entries()) {
    s.buttons[index + 1].click();
    assert.deepEqual(visible(s), examples.filter(e => e[1] === category).map(e => e[0]), category);
    assert.equal(s.url.searchParams.get('topic'), String(index));
    assert.equal(s.buttons[index + 1].getAttribute('aria-pressed'), 'true');
    assert.equal(s.buttons[0].getAttribute('aria-pressed'), 'false');
    assert.equal(s.empty.hidden, true);
  }
  s.buttons[0].click();
  assert.equal(s.url.searchParams.has('topic'), false);
  assert.equal(visible(s).length, 7);
});

test('homepage topic deep links filter correctly on first visit', () => {
  const s = start('?topic=2');
  assert.deepEqual(visible(s), ['Music']);
  assert.equal(s.count.textContent, '1 reading entry');
  assert.equal(s.buttons[3].getAttribute('aria-pressed'), 'true');
});

test('out-of-range and malformed topic URLs show the whole archive', () => {
  for (const q of ['?topic=900', '?topic=invalid', '?topic=-1']) {
    const s = start(q);
    assert.equal(visible(s).length, examples.length, q);
    assert.equal(s.buttons[0].getAttribute('aria-pressed'), 'true');
  }
});

test('search composes with a category and reset clears both', () => {
  const s = start();
  s.buttons[1].click();
  assert.equal(visible(s).length, 2);
  s.search.value = 'nineveh';
  s.search.input();
  assert.deepEqual(visible(s), ['Nineveh']);
  s.search.value = 'unmatched';
  s.search.input();
  assert.deepEqual(visible(s), []);
  assert.equal(s.count.textContent, '0 reading entries');
  assert.equal(s.empty.hidden, false);
  s.reset.click();
  assert.equal(s.search.value, '');
  assert.equal(s.url.searchParams.has('topic'), false);
  assert.equal(s.empty.hidden, true);
  assert.equal(visible(s).length, examples.length);
});

test('sort retains active category filtering', () => {
  const s = start();
  s.buttons[1].click();
  s.sort.value = 'az';
  s.sort.change();
  assert.deepEqual(visible(s), ['Ashur', 'Nineveh']);
  s.buttons[2].click();
  assert.deepEqual(visible(s), ['Aramaic']);
});
