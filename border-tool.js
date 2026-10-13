/* Border truck traffic lookup.
   Data: U.S. Bureau of Transportation Statistics, Border Crossing/Entry Data (public domain).
   No dependencies. No tracking. Runs entirely in the browser. */
(function () {
  'use strict';

  var D = window.__BORDER_DATA;
  var app = document.getElementById('bt-app');
  if (!app) { return; }
  if (!D) {
    app.innerHTML = '<p class="bt-err">The data file did not load. You can still open <a href="border-data.json">border-data.json</a> directly.</p>';
    return;
  }

  var MON = D.months;
  var PORTS = D.ports;
  var BORDER = D.border;
  var MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var N = MON.length;

  /* ---------- small helpers ---------- */

  function monthLabel(m) { var a = m.split('-'); return MN[parseInt(a[1], 10) - 1] + ' ' + a[0]; }
  function shortLabel(m) { var a = m.split('-'); return MN[parseInt(a[1], 10) - 1] + " '" + a[0].slice(2); }

  function full(n) {
    if (n === null || n === undefined || isNaN(n)) { return '—'; }
    return Math.round(n).toLocaleString('en-US');
  }
  function compact(n) {
    if (n === null || n === undefined || isNaN(n)) { return '—'; }
    var a = Math.abs(n);
    if (a >= 1e6) { return (n / 1e6).toFixed(a >= 1e7 ? 1 : 2).replace(/\.0+$/, '') + 'M'; }
    if (a >= 1e3) { return Math.round(n / 1e3) + 'k'; }
    return String(Math.round(n));
  }
  function pct(n) {
    if (n === null || n === undefined || isNaN(n)) { return '—'; }
    return (n >= 0 ? '+' : '') + n.toFixed(1) + '%';
  }
  function tick(v, isPct) {
    if (isPct) { return (v > 0 ? '+' : '') + Math.round(v) + '%'; }
    return compact(v);
  }

  /* ---------- series builders ---------- */

  function sumAllPorts() {
    var out = new Array(N);
    var i, k;
    for (i = 0; i < N; i++) { out[i] = 0; }
    for (k = 0; k < PORTS.length; k++) {
      var t = PORTS[k].t;
      for (i = 0; i < N; i++) { if (t[i]) { out[i] += t[i]; } }
    }
    return out;
  }

  var ALL_TRUCKS = sumAllPorts();

  function borderSeries(mode, side) {
    var b = BORDER[mode];
    if (!b) { return null; }
    return b[side];
  }

  function portByCode(c) {
    for (var i = 0; i < PORTS.length; i++) { if (PORTS[i].c === c) { return PORTS[i]; } }
    return null;
  }

  function trailingSum(a, w) {
    var s = 0, i, from = Math.max(0, a.length - w);
    for (i = from; i < a.length; i++) { if (a[i]) { s += a[i]; } }
    return s;
  }

  function rolling(a, w) {
    var out = new Array(a.length), i, k, s;
    for (i = 0; i < a.length; i++) {
      if (i < w - 1) { out[i] = null; continue; }
      s = 0;
      for (k = i - w + 1; k <= i; k++) { if (a[k]) { s += a[k]; } }
      out[i] = s;
    }
    return out;
  }

  function yoy(a) {
    var out = new Array(a.length), i, prev, cur;
    for (i = 0; i < a.length; i++) {
      if (i < 12) { out[i] = null; continue; }
      prev = a[i - 12];
      cur = a[i];
      if (!prev || cur === null || cur === undefined) { out[i] = null; continue; }
      out[i] = (cur - prev) / prev * 100;
    }
    return out;
  }

  /* ---------- chart ---------- */

  function drawChart(el, series, months, opt) {
    opt = opt || {};
    el.innerHTML = '';
    var W = 720, H = 320, padL = 64, padR = 18, padT = 18, padB = 42;
    var n = months.length;
    var i, k, v, si;

    var lo = 0, hi = 0, seen = false;
    for (si = 0; si < series.length; si++) {
      for (i = 0; i < n; i++) {
        v = series[si].values[i];
        if (v === null || v === undefined || isNaN(v)) { continue; }
        seen = true;
        if (v > hi) { hi = v; }
        if (v < lo) { lo = v; }
      }
    }
    if (!seen) { el.innerHTML = '<p class="bt-err">No figures in this range.</p>'; return; }

    if (!opt.pct) { lo = Math.min(0, lo); }
    if (hi === lo) { hi = lo + 1; }
    var pad = (hi - lo) * 0.08;
    hi = hi + pad;
    if (lo < 0) { lo = lo - pad; }

    var plotW = W - padL - padR, plotH = H - padT - padB;
    function X(idx) { return n <= 1 ? padL : padL + (idx / (n - 1)) * plotW; }
    function Y(val) { return padT + (hi - val) / (hi - lo) * plotH; }

    var parts = [];
    parts.push('<svg class="bt-svg" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid meet" role="img" aria-label="' + (opt.aria || 'Chart') + '">');

    /* gridlines + y labels */
    for (k = 0; k <= 4; k++) {
      var gv = lo + (hi - lo) * k / 4;
      var gy = Y(gv);
      parts.push('<line x1="' + padL + '" y1="' + gy.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + gy.toFixed(1) + '" stroke="' + (Math.abs(gv) < 1e-9 ? '#b9a98f' : '#e0d6c4') + '" stroke-width="1"/>');
      parts.push('<text x="' + (padL - 8) + '" y="' + (gy + 4).toFixed(1) + '" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="11" fill="#6b6b6b">' + tick(gv, opt.pct) + '</text>');
    }

    /* x labels */
    var step = Math.max(1, Math.ceil(n / 7));
    for (i = 0; i < n; i++) {
      if (i % step !== 0 && i !== n - 1) { continue; }
      if (i !== n - 1 && (n - 1 - i) < step * 0.5 && n > 3) { continue; }
      parts.push('<text x="' + X(i).toFixed(1) + '" y="' + (H - padB + 18) + '" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="11" fill="#6b6b6b">' + shortLabel(months[i]) + '</text>');
    }

    /* area fill for a single series */
    if (series.length === 1 && !opt.pct) {
      var d0 = '', open = false, first = true;
      for (i = 0; i < n; i++) {
        v = series[0].values[i];
        if (v === null || v === undefined || isNaN(v)) { open = false; continue; }
        if (!open) { d0 += (first ? 'M' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); open = true; first = false; }
        else { d0 += ' L' + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); }
      }
      if (d0) {
        var lastIdx = -1, firstIdx = -1;
        for (i = 0; i < n; i++) {
          v = series[0].values[i];
          if (v === null || v === undefined || isNaN(v)) { continue; }
          if (firstIdx < 0) { firstIdx = i; }
          lastIdx = i;
        }
        var areaD = d0 + ' L' + X(lastIdx).toFixed(1) + ' ' + Y(lo).toFixed(1) + ' L' + X(firstIdx).toFixed(1) + ' ' + Y(lo).toFixed(1) + ' Z';
        parts.push('<path d="' + areaD + '" fill="' + series[0].color + '" opacity="0.10" stroke="none"/>');
      }
    }

    /* lines */
    for (si = 0; si < series.length; si++) {
      var d = '', drawing = false;
      var vals = series[si].values;
      for (i = 0; i < n; i++) {
        v = vals[i];
        if (v === null || v === undefined || isNaN(v)) { drawing = false; continue; }
        d += (drawing ? ' L' : ' M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1);
        drawing = true;
      }
      parts.push('<path d="' + d.trim() + '" fill="none" stroke="' + series[si].color + '" stroke-width="2" stroke-linejoin="round"/>');
    }

    /* zero line for the percent view */
    if (opt.pct && lo < 0 && hi > 0) {
      parts.push('<line x1="' + padL + '" y1="' + Y(0).toFixed(1) + '" x2="' + (W - padR) + '" y2="' + Y(0).toFixed(1) + '" stroke="#8a7a60" stroke-width="1" stroke-dasharray="3 3"/>');
    }

    parts.push('<line x1="' + padL + '" y1="' + padT + '" x2="' + padL + '" y2="' + (H - padB) + '" stroke="#c9bda6" stroke-width="1"/>');
    parts.push('<line x1="' + padL + '" y1="' + (H - padB) + '" x2="' + (W - padR) + '" y2="' + (H - padB) + '" stroke="#c9bda6" stroke-width="1"/>');
    parts.push('<line class="bt-cross" x1="0" y1="' + padT + '" x2="0" y2="' + (H - padB) + '" stroke="#1a1a1a" stroke-width="1" stroke-dasharray="2 3" opacity="0"/>');
    parts.push('<rect class="bt-hit" x="' + padL + '" y="' + padT + '" width="' + plotW + '" height="' + plotH + '" fill="transparent" style="cursor:crosshair"/>');
    parts.push('</svg>');

    if (series.length > 1) {
      var lg = '<div class="bt-legend">';
      for (si = 0; si < series.length; si++) {
        lg += '<span><i style="background:' + series[si].color + '"></i>' + series[si].name + '</span>';
      }
      lg += '</div>';
      el.insertAdjacentHTML('beforeend', lg);
    }

    el.insertAdjacentHTML('beforeend', parts.join(''));
    var tip = document.createElement('div');
    tip.className = 'bt-tip';
    el.appendChild(tip);

    var svg = el.querySelector('svg');
    var cross = el.querySelector('.bt-cross');
    var hit = el.querySelector('.bt-hit');

    function onMove(ev) {
      var rect = svg.getBoundingClientRect();
      var scale = rect.width / W;
      var px = (ev.clientX - rect.left) / scale;
      var idx = Math.round((px - padL) / plotW * (n - 1));
      if (idx < 0) { idx = 0; }
      if (idx > n - 1) { idx = n - 1; }
      cross.setAttribute('x1', X(idx).toFixed(1));
      cross.setAttribute('x2', X(idx).toFixed(1));
      cross.setAttribute('opacity', '0.5');

      var html = '<strong>' + monthLabel(months[idx]) + '</strong>';
      for (var s = 0; s < series.length; s++) {
        var vv = series[s].values[idx];
        var shown = (vv === null || vv === undefined || isNaN(vv)) ? 'no figure' : (opt.pct ? pct(vv) : full(vv));
        html += '<span><i style="background:' + series[s].color + '"></i>' + series[s].name + ' <b>' + shown + '</b></span>';
      }
      tip.innerHTML = html;
      tip.style.opacity = '1';
      var left = X(idx) * scale;
      var hostW = el.clientWidth;
      var tw = tip.offsetWidth;
      var want = left - tw / 2;
      if (want < 0) { want = 0; }
      if (want + tw > hostW) { want = hostW - tw; }
      tip.style.left = want + 'px';
    }

    hit.addEventListener('mousemove', onMove);
    hit.addEventListener('touchmove', function (ev) {
      if (ev.touches && ev.touches[0]) { onMove(ev.touches[0]); }
    }, { passive: true });
    el.addEventListener('mouseleave', function () {
      tip.style.opacity = '0';
      cross.setAttribute('opacity', '0');
    });
  }

  /* ---------- state ---------- */

  var state = { scope: 'ALL', range: 12, metric: 'monthly', mode: 'Trucks' };

  var RANGES = { '12': 12, '60': 60, '120': 120, 'all': N };

  /* Shareable links: ?port=2304&range=all&metric=rolling&mode=Trains */
  function readParams() {
    var q = {};
    try {
      var s = String(window.location.search || '').replace(/^\?/, '');
      var h = String(window.location.hash || '').replace(/^#/, '');
      var str = h.indexOf('=') >= 0 ? (s ? s + '&' + h : h) : s;
      if (!str) { return q; }
      var parts = str.split('&');
      for (var i = 0; i < parts.length; i++) {
        var e = parts[i].indexOf('=');
        if (e < 0) { continue; }
        q[decodeURIComponent(parts[i].slice(0, e))] = decodeURIComponent(parts[i].slice(e + 1));
      }
    } catch (err) { return {}; }
    return q;
  }

  var P = readParams();
  if (P.port === 'ALL' || P.port === 'MX' || P.port === 'CA') { state.scope = P.port; }
  else if (P.port && portByCode(P.port)) { state.scope = P.port; }
  if (P.range && RANGES[String(P.range)]) { state.range = String(P.range); }
  if (P.metric === 'monthly' || P.metric === 'rolling' || P.metric === 'yoy') { state.metric = P.metric; }
  if (P.mode && BORDER[P.mode]) { state.mode = P.mode; }

  function syncUrl() {
    if (!window.history || !history.replaceState) { return; }
    var qs = '?port=' + encodeURIComponent(state.scope);
    if (String(state.range) !== '12') { qs += '&range=' + encodeURIComponent(state.range); }
    if (state.metric !== 'monthly') { qs += '&metric=' + encodeURIComponent(state.metric); }
    if (state.mode !== 'Trucks') { qs += '&mode=' + encodeURIComponent(state.mode); }
    try { history.replaceState(null, '', window.location.pathname + qs); } catch (e) { /* file:// or blocked */ }
  }

  function scopeRaw() {
    if (state.scope === 'ALL') { return ALL_TRUCKS; }
    if (state.scope === 'MX') { return borderSeries('Trucks', 'MX'); }
    if (state.scope === 'CA') { return borderSeries('Trucks', 'CA'); }
    var p = portByCode(state.scope);
    return p ? p.t : ALL_TRUCKS;
  }

  function scopeName() {
    if (state.scope === 'ALL') { return 'All US land ports'; }
    if (state.scope === 'MX') { return 'US–Mexico border'; }
    if (state.scope === 'CA') { return 'US–Canada border'; }
    var p = portByCode(state.scope);
    return p ? p.n : 'All US land ports';
  }

  function scopeNote() {
    if (state.scope === 'ALL' || state.scope === 'MX' || state.scope === 'CA') { return ''; }
    var p = portByCode(state.scope);
    if (!p) { return ''; }
    return 'Port-level figures cover trucks only. This crossing sits on the US–' + (p.b === 'MX' ? 'Mexico' : 'Canada') + ' border.';
  }

  /* ---------- render ---------- */

  function buildScopeSelect() {
    var sel = document.getElementById('bt-scope');
    if (!sel) { return; }
    var html = '';
    html += '<optgroup label="Whole border">';
    html += '<option value="ALL">All US land ports</option>';
    html += '<option value="MX">US–Mexico border (all crossings)</option>';
    html += '<option value="CA">US–Canada border (all crossings)</option>';
    html += '</optgroup>';

    var ranked = PORTS.slice().sort(function (a, b) { return trailingSum(b.t, 12) - trailingSum(a.t, 12); });
    var sides = [['MX', 'US–Mexico crossings'], ['CA', 'US–Canada crossings']];
    for (var s = 0; s < sides.length; s++) {
      html += '<optgroup label="' + sides[s][1] + '">';
      for (var i = 0; i < ranked.length; i++) {
        if (ranked[i].b !== sides[s][0]) { continue; }
        html += '<option value="' + ranked[i].c + '">' + ranked[i].n + ' — ' + compact(trailingSum(ranked[i].t, 12)) + ' trucks/yr</option>';
      }
      html += '</optgroup>';
    }
    sel.innerHTML = html;
    sel.value = state.scope;
  }

  function render() {
    var raw = scopeRaw();
    var range = RANGES[String(state.range)] || 12;

    var full12 = rolling(raw, 12);
    var fullYoY = yoy(raw);
    var src, metricLabel, isPct = false;

    if (state.metric === 'rolling') { src = full12; metricLabel = 'Trucks per 12 months'; }
    else if (state.metric === 'yoy') { src = fullYoY; metricLabel = 'Change vs same month a year earlier'; isPct = true; }
    else { src = raw; metricLabel = 'Trucks per month'; }

    var cut = Math.max(0, N - range);
    var months = MON.slice(cut);
    var values = src.slice(cut);

    var chartHost = document.getElementById('bt-chart');
    drawChart(chartHost, [{ name: scopeName(), color: '#0b3d2e', values: values }], months, {
      pct: isPct,
      aria: metricLabel + ' at ' + scopeName()
    });

    var cap = document.getElementById('bt-cap');
    if (cap) {
      cap.textContent = metricLabel + ' · ' + scopeName() + ' · ' + monthLabel(months[0]) + ' to ' + monthLabel(months[months.length - 1]);
    }

    /* stats */
    var last = raw[N - 1];
    var prevYear = raw[N - 13];
    var yoyNow = (prevYear && last) ? (last - prevYear) / prevYear * 100 : null;
    var t12 = trailingSum(raw, 12);
    var grand = trailingSum(ALL_TRUCKS, 12);
    var share = grand ? t12 / grand * 100 : null;

    document.getElementById('bt-s1v').textContent = full(last);
    document.getElementById('bt-s1k').textContent = monthLabel(MON[N - 1]);
    document.getElementById('bt-s2v').textContent = pct(yoyNow);
    document.getElementById('bt-s2v').className = 'bt-v ' + (yoyNow === null ? '' : (yoyNow >= 0 ? 'bt-up' : 'bt-down'));
    document.getElementById('bt-s3v').textContent = full(t12);
    var k4 = document.getElementById('bt-s4k');
    var s4 = document.getElementById('bt-s4s');
    var v4 = document.getElementById('bt-s4v');
    if (state.scope === 'ALL') {
      v4.textContent = String(PORTS.length);
      if (k4) { k4.textContent = 'Crossings covered'; }
      if (s4) { s4.textContent = 'land ports of entry, both borders'; }
    } else {
      v4.textContent = share === null ? '—' : share.toFixed(1) + '%';
      if (k4) { k4.textContent = 'Share of the border'; }
      if (s4) { s4.textContent = 'of all US land truck crossings'; }
    }

    /* rank */
    var rankEl = document.getElementById('bt-rank');
    if (rankEl) {
      if (state.scope === 'ALL') { rankEl.textContent = 'Every crossing on both land borders, added together.'; }
      else if (state.scope === 'MX' || state.scope === 'CA') { rankEl.textContent = 'One side of the border, every crossing on it.'; }
      else {
        var code = state.scope;
        var order = PORTS.slice().sort(function (a, b) { return trailingSum(b.t, 12) - trailingSum(a.t, 12); });
        var r = 0;
        for (var i = 0; i < order.length; i++) { if (order[i].c === code) { r = i + 1; } }
        rankEl.textContent = 'Ranked ' + r + ' of ' + PORTS.length + ' crossings by truck volume over the last 12 months.';
      }
      var noteEl = document.getElementById('bt-portnote');
      if (noteEl) {
        var nt = scopeNote();
        noteEl.textContent = nt;
        noteEl.style.display = nt ? 'block' : 'none';
      }
    }

    renderBorderChart();
    renderTable();
    syncUrl();
  }

  function renderBorderChart() {
    var host = document.getElementById('bt-bchart');
    if (!host) { return; }
    var mx = borderSeries(state.mode, 'MX');
    var ca = borderSeries(state.mode, 'CA');
    if (!mx || !ca) { return; }
    var range = RANGES[String(state.range)] || 12;
    var cut = Math.max(0, N - range);
    var months = MON.slice(cut);
    var label = state.mode === 'Personal Vehicles' ? 'personal vehicles' : state.mode.toLowerCase();

    drawChart(host, [
      { name: 'US–Mexico', color: '#8c2f1c', values: mx.slice(cut) },
      { name: 'US–Canada', color: '#0b3d2e', values: ca.slice(cut) }
    ], months, { aria: 'Monthly ' + label + ' crossings on each land border' });

    var cap = document.getElementById('bt-bcap');
    if (cap) {
      cap.textContent = 'Monthly ' + label + ' entering the United States, by border · ' + monthLabel(months[0]) + ' to ' + monthLabel(months[months.length - 1]);
    }
  }

  function renderTable() {
    var body = document.getElementById('bt-rows');
    if (!body) { return; }
    var ranked = PORTS.slice().sort(function (a, b) { return trailingSum(b.t, 12) - trailingSum(a.t, 12); });
    var grand = trailingSum(ALL_TRUCKS, 12);
    var html = '';
    for (var i = 0; i < 15; i++) {
      var p = ranked[i];
      if (!p) { break; }
      var t12 = trailingSum(p.t, 12);
      var last = p.t[N - 1];
      var py = p.t[N - 13];
      var g = (py && last) ? (last - py) / py * 100 : null;
      var share = grand ? t12 / grand * 100 : null;
      html += '<tr class="bt-row" data-c="' + p.c + '" tabindex="0">' +
        '<td class="bt-rk">' + (i + 1) + '</td>' +
        '<td>' + p.n + '</td>' +
        '<td class="bt-sd">' + (p.b === 'MX' ? 'US–Mexico' : 'US–Canada') + '</td>' +
        '<td class="bt-nm">' + full(t12) + '</td>' +
        '<td class="bt-nm">' + (share === null ? '—' : share.toFixed(1) + '%') + '</td>' +
        '<td class="bt-nm ' + (g === null ? '' : (g >= 0 ? 'bt-up' : 'bt-down')) + '">' + pct(g) + '</td>' +
        '</tr>';
    }
    body.innerHTML = html;

    var rows = body.querySelectorAll('.bt-row');
    for (var k = 0; k < rows.length; k++) {
      rows[k].addEventListener('click', function () { pick(this.getAttribute('data-c')); });
      rows[k].addEventListener('keypress', function (ev) {
        if (ev.key === 'Enter') { pick(this.getAttribute('data-c')); }
      });
    }
  }

  function pick(code) {
    state.scope = code;
    var sel = document.getElementById('bt-scope');
    if (sel) { sel.value = code; }
    render();
    var top = document.getElementById('bt-top');
    if (top && top.scrollIntoView) { top.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }

  /* ---------- wiring ---------- */

  buildScopeSelect();

  var selScope = document.getElementById('bt-scope');
  if (selScope) {
    selScope.addEventListener('change', function () { state.scope = this.value; render(); });
  }

  var selRange = document.getElementById('bt-range');
  if (selRange) {
    selRange.value = String(state.range);
    selRange.addEventListener('change', function () { state.range = this.value; render(); });
  }

  var selMetric = document.getElementById('bt-metric');
  if (selMetric) {
    selMetric.value = state.metric;
    selMetric.addEventListener('change', function () { state.metric = this.value; render(); });
  }

  var selMode = document.getElementById('bt-mode');
  if (selMode) {
    selMode.value = state.mode;
    selMode.addEventListener('change', function () { state.mode = this.value; renderBorderChart(); });
  }

  var quick = document.querySelectorAll('.bt-quick');
  for (var q = 0; q < quick.length; q++) {
    quick[q].addEventListener('click', function () { pick(this.getAttribute('data-c')); });
  }

  var reset = document.getElementById('bt-reset');
  if (reset) {
    reset.addEventListener('click', function () {
      state.scope = 'ALL';
      state.metric = 'monthly';
      state.range = 12;
      state.mode = 'Trucks';
      if (selScope) { selScope.value = 'ALL'; }
      if (selMetric) { selMetric.value = 'monthly'; }
      if (selRange) { selRange.value = '12'; }
      if (selMode) { selMode.value = 'Trucks'; }
      render();
    });
  }

  var stamp = document.getElementById('bt-stamp');
  if (stamp && D.meta) {
    stamp.textContent = 'Data retrieved ' + D.meta.retrieved + '. Latest month in the file: ' + monthLabel(MON[N - 1]) + '.';
  }

  render();
})();
