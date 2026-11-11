/* Self-hosted map and progressive filtering for Assyrian persecution records. */
(() => {
  'use strict';
  const root = document.querySelector('[data-persecution]');
  if (!root) return;
  const $ = id => document.getElementById(id);
  const base = document.querySelector('meta[name="site-base-path"]')?.content || '';
  const svg = $('ap-map');
  const ns = 'http://www.w3.org/2000/svg';
  const records = JSON.parse($('ap-data').textContent).records;
  const cards = new Map([...document.querySelectorAll('[data-ap-id]')].map(node => [node.dataset.apId, node]));
  const fields = {
    country: $('ap-country'), type: $('ap-type'), period: $('ap-period'),
    evidence: $('ap-evidence'), search: $('ap-search'), sort: $('ap-sort')
  };
  const list = $('ap-case-list');
  const status = $('ap-map-status');
  const countryLayer = $('ap-map-countries');
  const markerLayer = $('ap-map-markers');
  let mapFeatures = [];
  let mapReady = false;
  let mapView = 'world';
  const point = (lon, lat) => [(lon + 180) * 3, (90 - lat) * 3];
  const element = (tag, attrs = {}, label) => {
    const item = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attrs)) item.setAttribute(key, String(value));
    if (label !== undefined) item.textContent = label;
    return item;
  };
  const ring = coordinates => {
    let path = '';
    let previous = null;
    for (const coordinatesPair of coordinates) {
      const [lon, lat] = coordinatesPair;
      const [x, y] = point(lon, lat);
      const discontinuity = previous && Math.abs(previous[0] - lon) > 180;
      path += (previous && !discontinuity ? 'L' : 'M') + x.toFixed(2) + ',' + y.toFixed(2);
      previous = coordinatesPair;
    }
    return path + 'Z';
  };
  const geometryPath = geometry => {
    if (geometry.type === 'Polygon') return geometry.coordinates.map(ring).join('');
    if (geometry.type === 'MultiPolygon') return geometry.coordinates.map(polygon => polygon.map(ring).join('')).join('');
    return '';
  };
  const periodMatch = (year, period) => {
    if (!period) return true;
    if (period === 'before1900') return year < 1900;
    if (period === '2020+') return year >= 2020;
    const [start, end] = period.split('-').map(Number);
    return year >= start && year <= end;
  };
  const matched = (record, includeCountry = true) => {
    const query = fields.search.value.trim().toLocaleLowerCase();
    const card = cards.get(record.id);
    return (!includeCountry || !fields.country.value || record.country === fields.country.value) &&
      (!fields.type.value || record.type === fields.type.value) &&
      (!fields.evidence.value || record.evidence === fields.evidence.value) &&
      periodMatch(record.year, fields.period.value) &&
      (!query || query.split(/\s+/).every(term => card.dataset.apSearch.includes(term)));
  };
  const heatLevel = count => count >= 11 ? 4 : count >= 6 ? 3 : count >= 3 ? 2 : count >= 1 ? 1 : 0;

  function setView(view) {
    mapView = view;
    svg.setAttribute('viewBox', view === 'homeland' ? '609 113 132 81' : '0 0 1080 540');
    $('ap-world').setAttribute('aria-pressed', String(view === 'world'));
    $('ap-homeland').setAttribute('aria-pressed', String(view === 'homeland'));
    paint();
  }

  function paint() {
    if (!mapReady) return;
    // Country shading uses all matching filters except country selection. This
    // preserves the geographic comparison when a single country is selected.
    const heatRecords = records.filter(record => matched(record, false));
    const counts = new Map();
    for (const record of heatRecords) counts.set(record.country, (counts.get(record.country) || 0) + 1);
    for (const {node, country} of mapFeatures) {
      const count = counts.get(country) || 0;
      const active = count > 0;
      node.setAttribute('class', 'ap-country ap-level-' + heatLevel(count));
      node.dataset.active = String(active);
      node.dataset.selected = String(fields.country.value === country && active);
      if (active) {
        node.setAttribute('tabindex', '0');
        node.setAttribute('role', 'button');
      } else {
        node.removeAttribute('tabindex');
        node.removeAttribute('role');
      }
      node.setAttribute('aria-label', country + ': ' + count + ' matching catalogue records. Filter by country.');
      node.querySelector('title').textContent = country + ' - ' + count + ' catalogue records';
    }
    markerLayer.replaceChildren();
    const places = new Map();
    for (const record of heatRecords) {
      if (fields.country.value && fields.country.value !== record.country) continue;
      const key = record.country + '|' + record.place;
      const current = places.get(key);
      if (current) current.count++;
      else places.set(key, {name:record.place, country:record.country,
        lon:record.lon, lat:record.lat, count:1});
    }
    for (const place of places.values()) {
      const [cx, cy] = point(place.lon, place.lat);
      const group = element('g');
      const radius = mapView === 'homeland' ? 1.10 : 4.3;
      const circle = element('circle', {cx, cy, r:radius, class:'ap-marker'});
      group.append(circle);
      group.append(element('title', {}, place.name + ', ' + place.country + ': ' +
        place.count + ' matching records. Approximate location.'));
      if (place.count > 1) {
        group.append(element('text', {x:cx, y:cy, class:'ap-marker-label',
          'font-size': mapView === 'homeland' ? 1.08 : 4.0}, String(place.count)));
      }
      markerLayer.append(group);
    }
    const visible = records.filter(record => matched(record));
    const countryCount = new Set(visible.map(record => record.country)).size;
    status.textContent = 'Map shows ' + heatRecords.length +
      ' catalogue records across ' + counts.size + ' countries. ' +
      (fields.country.value ? fields.country.value + ' selected. ' : '') +
      'Select a shaded country or use the country filter. ' +
      visible.length + ' records currently shown below.';
  }

  function apply() {
    const visible = records.filter(record => matched(record));
    const oldest = fields.sort.value === 'oldest';
    visible.sort((a, b) => (oldest ? a.year - b.year : b.year - a.year) ||
      a.id.localeCompare(b.id));
    const present = new Set(visible.map(record => record.id));
    for (const [id, card] of cards) card.hidden = !present.has(id);
    for (const record of visible) list.append(cards.get(record.id));
    const countryCount = new Set(visible.map(record => record.country)).size;
    const placeCount = new Set(visible.map(record => record.country + '|' + record.place)).size;
    $('ap-total').textContent = String(visible.length);
    $('ap-countries').textContent = String(countryCount);
    $('ap-places').textContent = String(placeCount);
    $('ap-empty').hidden = visible.length !== 0;
    $('ap-results').textContent = 'Showing ' + visible.length + ' of ' + records.length +
      ' source-linked records. Map shading reflects report counts, not victims.';
    paint();
  }

  function filterCountry(country) {
    fields.country.value = fields.country.value === country ? '' : country;
    apply();
    fields.country.focus({preventScroll:true});
  }

  function addGeography(geojson) {
    if (!geojson || !Array.isArray(geojson.features)) throw Error('Invalid geography');
    const fragment = document.createDocumentFragment();
    for (const feature of geojson.features) {
      const country = feature.properties?.ADMIN || feature.properties?.NAME;
      if (!country) continue;
      const path = element('path', {d:geometryPath(feature.geometry), class:'ap-country ap-level-0'});
      path.dataset.country = country;
      path.append(element('title', {}, country));
      path.addEventListener('click', () => {
        if (path.dataset.active === 'true') filterCountry(country);
      });
      path.addEventListener('keydown', event => {
        if (path.dataset.active !== 'true') return;
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          filterCountry(country);
        }
      });
      fragment.append(path);
      mapFeatures.push({node:path,country});
    }
    countryLayer.replaceChildren(fragment);
    mapReady = true;
    paint();
  }

  Object.values(fields).forEach(field => field.addEventListener(
    field === fields.search ? 'input' : 'change', apply));
  $('ap-world').addEventListener('click', () => setView('world'));
  $('ap-homeland').addEventListener('click', () => setView('homeland'));
  $('ap-reset').addEventListener('click', () => {
    fields.search.value = '';
    fields.country.value = '';
    fields.type.value = '';
    fields.period.value = '';
    fields.evidence.value = '';
    fields.sort.value = 'newest';
    setView('world');
    apply();
  });
  apply();
  fetch(base + '/archive/maps/natural-earth-countries.geojson')
    .then(response => {
      if (!response.ok) throw Error('Local map resource was not found');
      return response.json();
    })
    .then(addGeography)
    .catch(() => {
      status.textContent = 'Map geography could not load. All catalogue records, source links and filters remain available.';
    });
})();
