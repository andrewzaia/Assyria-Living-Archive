/* Self-hosted historical atlas. No external libraries, tiles or telemetry. */
(() => {
  'use strict';
  const root = document.querySelector('[data-atlas]');
  if (!root) return;
  const $ = id => document.getElementById(id);
  const svg = $('historical-map');
  const base = document.querySelector('meta[name="site-base-path"]')?.content || '';
  const ns = 'http://www.w3.org/2000/svg';
  const project = ([lon, lat]) => [(lon - 24) * 1000 / 30, (43 - lat) * 820 / 21];
  const node = (tag, attributes = {}, text) => {
    const el = document.createElementNS(ns, tag);
    Object.entries(attributes).forEach(([key, value]) => el.setAttribute(key, value));
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const line = points => points.map((point, i) => `${i ? 'L' : 'M'}${project(point).map(n => n.toFixed(2)).join(',')}`).join('');
  const path = geometry => {
    if (geometry.type === 'Polygon') return geometry.coordinates.map(ring => line(ring) + 'Z').join('');
    if (geometry.type === 'MultiPolygon') return geometry.coordinates.map(poly => path({type:'Polygon', coordinates:poly})).join('');
    if (geometry.type === 'LineString') return line(geometry.coordinates);
    if (geometry.type === 'MultiLineString') return geometry.coordinates.map(line).join('');
    return '';
  };
  const load = async file => {
    const response = await fetch(base + '/archive/maps/' + file);
    if (!response.ok) throw new Error('Local map file unavailable');
    return response.json();
  };
  let data, index = 4, timer = null, dragging = null, moved = false;
  let view = {x:0, y:0, width:1000, height:820};
  function setView() {
    view.x = Math.max(0, Math.min(1000 - view.width, view.x));
    view.y = Math.max(0, Math.min(820 - view.height, view.y));
    svg.classList.toggle('map-zoomed', view.width < 1000);
    svg.setAttribute('viewBox', `${view.x} ${view.y} ${view.width} ${view.height}`);
    $('map-zoom-out').disabled = view.width >= 1000;
    $('map-zoom-in').disabled = view.width <= 250;
  }
  function zoom(factor) {
    const width = Math.max(250, Math.min(1000, view.width * factor));
    const height = width * .82;
    view.x += (view.width - width) / 2;
    view.y += (view.height - height) / 2;
    view.width = width; view.height = height; setView();
  }
  function pause() {
    clearInterval(timer); timer = null;
    $('map-play-text').textContent = 'Play timeline';
    $('map-play').setAttribute('aria-pressed', 'false');
  }
  function choose(value, manual = true) {
    if (manual) pause();
    index = Math.max(0, Math.min(data.snapshots.length - 1, Number(value)));
    const s = data.snapshots[index];
    $('map-date').textContent = `${Math.abs(s.year)} BCE`;
    $('map-period').textContent = s.period;
    $('map-step').textContent = `CHAPTER ${String(index + 1).padStart(2, '0')} / ${data.snapshots.length}`;
    $('map-chapter').textContent = s.title;
    $('map-summary').textContent = s.summary;
    $('map-caution').textContent = s.caution;
    $('map-svg-title').textContent = `Assyria at ${Math.abs(s.year)} BCE - ${s.title}`;
    $('map-svg-description').textContent = s.summary + ' ' + s.caution;
    $('map-year').value = String(index);
    $('map-year').setAttribute('aria-valuetext', `${Math.abs(s.year)} BCE - ${s.title}`);
    $('map-chapter-select').value = String(index);
    $('map-prev').disabled = index === 0;
    $('map-next').disabled = index === data.snapshots.length - 1;
    root.querySelectorAll('[data-map-stage]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.mapStage) === index)));
    const draw = (id, ids, className) => {
      $(id).replaceChildren(...ids.map(regionId => node('path', {d:path(data.regions.features.find(f => f.id === regionId).geometry), class:className, ...(className === 'map-indirect' ? {fill:'url(#atlas-hatch)'} : {})})));
    };
    draw('map-territory', s.control, 'map-control');
    draw('map-influence', s.influence, 'map-indirect');
    $('map-sources').replaceChildren(...s.sources.map(id => {
      const source = data.sources.find(item => item.id === id);
      const li = document.createElement('li');
      const a = document.createElement('a'); a.href = '#atlas-source-' + id; a.textContent = source.title;
      li.append(a); return li;
    }));
    const biblical = $('map-biblical');
    biblical.replaceChildren(); biblical.hidden = !s.biblical;
    if (s.biblical) {
      const heading = document.createElement('span'); heading.className = 'eyebrow'; heading.textContent = 'BIBLICAL PRIMARY REFERENCES';
      const note = document.createElement('p'); note.textContent = s.biblical.note;
      const list = document.createElement('ul');
      s.biblical.passages.forEach(p => { const li = document.createElement('li'); const a = document.createElement('a'); a.href = base + p.url; a.textContent = p.label; li.append(a); list.append(li); });
      biblical.append(heading, note, list);
    }
    $('map-places').querySelectorAll('[data-place]').forEach(marker => {
      marker.classList.toggle('map-place-focus', marker.dataset.place === s.focus);
      marker.classList.toggle('map-place-fallen', s.fallen.includes(marker.dataset.place));
    });
    history.replaceState(null, '', '#year=' + Math.abs(s.year));
    if (index === data.snapshots.length - 1) pause();
  }
  function showPlace(id) {
    const p = data.places.find(place => place.id === id);
    if (!p) return;
    $('map-place-select').value = id;
    $('map-place-detail').textContent = p.name + ': ' + p.description;
    $('map-place-detail').setAttribute('role', 'status');
    const [x,y] = project(p.coordinates);
    if (view.width < 1000) { view.x = x - view.width / 2; view.y = y - view.height / 2; setView(); }
  }
  async function init() {
    try {
      const files = await Promise.all([load('assyria-atlas.json'), load('natural-earth-land.geojson'), load('natural-earth-countries.geojson'), load('natural-earth-rivers.geojson')]);
      data = files[0];
      const land = files[1].features.map(f => path(f.geometry)).join('');
      $('map-land').setAttribute('d', land); $('atlas-land-clip').setAttribute('d', land);
      $('map-modern-borders').replaceChildren(...files[2].features.map(f => node('path', {d:path(f.geometry), class:'map-border'})));
      const rivers = files[3].features.filter(f => ['Tigris', 'Euphrates', 'Nile'].includes(f.properties.name));
      $('map-rivers').replaceChildren(...rivers.map(f => node('path', {d:path(f.geometry), class:'map-river'})));
      for (let lon = 25; lon <= 50; lon += 5) $('map-graticule').append(node('path', {d:line([[lon,22],[lon,43]])}));
      for (let lat = 25; lat <= 40; lat += 5) $('map-graticule').append(node('path', {d:line([[24,lat],[54,lat]])}));
      data.modern_labels.forEach(p => { const [x,y] = project(p.coordinates); $('map-modern-labels').append(node('text', {x,y}, p.name)); });
      [['MEDITERRANEAN SEA',29.4,34.8], ['BLACK SEA',34.5,42.0], ['PERSIAN GULF',51.3,27.2], ['RED SEA',34.4,25.4]].forEach(([name,lon,lat]) => {
        const [x,y] = project([lon,lat]); $('map-water-labels').append(node('text', {x,y},name));
      });
      data.places.forEach(p => {
        const [x,y] = project(p.coordinates);
        const g = node('g', {'data-place':p.id, class:'map-place', transform:`translate(${x},${y})`});
        g.append(node('title', {}, p.name + ': ' + p.description));
        g.append(node('circle', {r:14, class:'map-place-halo'}), node('circle', {r:4.5, class:'map-place-dot'}));
        g.append(node('text', {x:p.label_offset[0], y:p.label_offset[1]}, p.name));
        g.addEventListener('click', () => { if (!moved) showPlace(p.id); });
        $('map-places').append(g);
      });
      const peak = data.snapshots.find(s => s.year === -671);
      $('map-comparison').replaceChildren(...[...peak.control, ...peak.influence].map(id => node('path', {d:path(data.regions.features.find(f => f.id === id).geometry), class:'map-peak'})));
      $('map-comparison').style.display = 'none';
      root.querySelectorAll('button, select, input').forEach(el => el.disabled = false);
      const requested = /^#year=(\d+)$/.exec(location.hash);
      const requestedIndex = requested ? data.snapshots.findIndex(s => Math.abs(s.year) === Number(requested[1])) : -1;
      choose(requestedIndex >= 0 ? requestedIndex : 4); setView();
      $('map-load-status').hidden = true;
      root.dataset.ready = 'true';
    } catch (error) {
      $('map-load-status').textContent = 'The interactive map could not load. Read the text chapters and download the retained data below, or reload to try again.';
      root.dataset.ready = 'error';
    }
  }
  $('map-year').addEventListener('input', e => choose(e.target.value));
  $('map-chapter-select').addEventListener('change', e => choose(e.target.value));
  $('map-prev').addEventListener('click', () => choose(index - 1));
  $('map-next').addEventListener('click', () => choose(index + 1));
  root.querySelectorAll('[data-map-stage]').forEach(button => button.addEventListener('click', () => choose(button.dataset.mapStage)));
  $('map-play').addEventListener('click', () => {
    if (timer) { pause(); return; }
    if (index === data.snapshots.length - 1) choose(0);
    $('map-play-text').textContent = 'Pause timeline'; $('map-play').setAttribute('aria-pressed', 'true');
    timer = setInterval(() => choose(index + 1, false), 3200);
  });
  $('map-place-select').addEventListener('change', e => showPlace(e.target.value));
  $('map-borders').addEventListener('change', e => {
    $('map-modern-borders').style.display = e.target.checked ? '' : 'none';
    $('map-modern-labels').style.display = e.target.checked ? '' : 'none';
  });
  $('map-labels').addEventListener('change', e => $('map-places').classList.toggle('map-hide-names', !e.target.checked));
  $('map-compare').addEventListener('change', e => {
    $('map-comparison').style.display = e.target.checked ? '' : 'none';
    root.querySelector('.legend-comparison').hidden = !e.target.checked;
  });
  $('map-zoom-in').addEventListener('click', () => zoom(.75));
  $('map-zoom-out').addEventListener('click', () => zoom(4 / 3));
  $('map-reset').addEventListener('click', () => { view = {x:0,y:0,width:1000,height:820}; setView(); });
  svg.addEventListener('keydown', e => {
    if (!data) return;
    const moves = {ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
    if (moves[e.key]) { e.preventDefault(); view.x += moves[e.key][0] * view.width / 12; view.y += moves[e.key][1] * view.height / 12; setView(); }
    if (e.key === '+' || e.key === '=') { e.preventDefault(); zoom(.75); }
    if (e.key === '-') { e.preventDefault(); zoom(4 / 3); }
    if (e.key === 'Home') { e.preventDefault(); view = {x:0,y:0,width:1000,height:820}; setView(); }
  });
  svg.addEventListener('pointerdown', e => {
    if (!data || e.button !== 0) return;
    moved = false;
    if (view.width >= 1000) return;
    dragging = {x:e.clientX,y:e.clientY,startX:view.x,startY:view.y,id:e.pointerId};
    svg.setPointerCapture(e.pointerId); svg.classList.add('map-dragging');
  });
  svg.addEventListener('pointermove', e => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const scale = Math.min(rect.width / view.width, rect.height / view.height);
    const dx = e.clientX - dragging.x, dy = e.clientY - dragging.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
    view.x = dragging.startX - dx / scale; view.y = dragging.startY - dy / scale; setView();
  });
  const endDrag = () => { dragging = null; svg.classList.remove('map-dragging'); };
  svg.addEventListener('pointerup', endDrag); svg.addEventListener('pointercancel', endDrag);
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  window.addEventListener('hashchange', () => {
    if (!data) return;
    const match = /^#year=(\d+)$/.exec(location.hash);
    const n = match ? data.snapshots.findIndex(s => Math.abs(s.year) === Number(match[1])) : -1;
    if (n >= 0) choose(n);
  });
  init();
})();
