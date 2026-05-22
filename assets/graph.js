/* graph.js — d3-force, layer-banded, multi-lens */

(function () {
  const data = window.GRAPH;
  const svgEl = document.getElementById('graph');
  const canvas = document.querySelector('.graph-canvas');
  const inspectEl = document.getElementById('inspect');
  const searchEl = document.getElementById('search');
  const lensList = document.getElementById('lens-list');
  const layerList = document.getElementById('layer-list');
  const layerBands = document.getElementById('layer-bands');
  const statusEl = document.getElementById('status');

  const state = {
    lenses: new Set(['supply']),
    layers: new Set(data.layers.map(l => l.id)),
    focused: null,
  };

  const layerIndex = Object.fromEntries(data.layers.map((l, i) => [l.id, i]));

  // ─── sidebar: layer bands + filter list ───
  data.layers.forEach(l => {
    const band = document.createElement('div');
    band.className = 'layer-band';
    band.dataset.layer = l.id;
    band.innerHTML = `<span class="label">${l.label}</span>`;
    layerBands.appendChild(band);

    const count = data.nodes.filter(n => n.layer === l.id).length;
    const li = document.createElement('li');
    li.dataset.layer = l.id;
    li.innerHTML = `<span class="dot"></span> ${l.label} <span class="count">${count}</span>`;
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => {
      if (state.layers.has(l.id)) state.layers.delete(l.id);
      else state.layers.add(l.id);
      li.style.opacity = state.layers.has(l.id) ? 1 : 0.35;
      updateVisibility();
    });
    layerList.appendChild(li);
  });

  // ─── lens toggles ───
  lensList.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => {
      const lens = li.dataset.lens;
      if (state.lenses.has(lens)) state.lenses.delete(lens);
      else state.lenses.add(lens);
      lensList.querySelectorAll('li').forEach(item => {
        const isActive = state.lenses.has(item.dataset.lens);
        item.classList.toggle('active', isActive);
        item.classList.toggle('inactive', !isActive);
      });
      updateVisibility();
      if (state.focused) {
        const n = nodes.find(x => x.id === state.focused);
        if (n) focusNode(n);
      }
    });
  });

  // ─── d3 setup ───
  const nodes = data.nodes.map(n => ({ ...n }));
  const edges = data.edges.map(e => ({ ...e, source: e.s, target: e.t }));

  function dims() {
    const r = canvas.getBoundingClientRect();
    return { w: r.width, h: r.height };
  }

  let { w, h } = dims();
  svgEl.setAttribute('viewBox', `0 0 ${w} ${h}`);
  svgEl.setAttribute('preserveAspectRatio', 'xMidYMid meet');

  const layerY = (layer) => (h / data.layers.length) * (layerIndex[layer] + 0.5);

  // arrow markers per lens
  const defs = d3.select(svgEl).append('defs');
  const marker = (id, color, dash) => {
    defs.append('marker')
      .attr('id', id)
      .attr('viewBox', '0 -4 8 8')
      .attr('refX', 14)
      .attr('refY', 0)
      .attr('markerWidth', 7)
      .attr('markerHeight', 7)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-3L7,0L0,3')
      .attr('fill', color)
      .attr('opacity', 0.7);
  };
  marker('arrow-supply', '#d4a017');
  marker('arrow-capital', '#c084fc');
  marker('arrow-resource', '#4ade80');

  const g = d3.select(svgEl).append('g').attr('class', 'view');
  const edgeG = g.append('g').attr('class', 'edges');
  const nodeG = g.append('g').attr('class', 'nodes');

  const sim = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-320))
    .force('link', d3.forceLink(edges).id(d => d.id).distance(80).strength(0.35))
    .force('x', d3.forceX(w / 2).strength(0.03))
    .force('y', d3.forceY(d => layerY(d.layer)).strength(0.6))
    .force('collide', d3.forceCollide(32));

  const edgeSel = edgeG.selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('class', d => `edge ${d.lens}`)
    .attr('stroke-width', d => d.weight ? Math.min(3.5, 0.8 + Math.sqrt(d.weight) * 0.5) : 1)
    .attr('marker-end', d => `url(#arrow-${d.lens})`);

  const nodeSel = nodeG.selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('data-id', d => d.id)
    .call(drag(sim))
    .on('click', (ev, d) => { ev.stopPropagation(); focusNode(d); })
    .on('mouseenter', (ev, d) => hoverNode(d))
    .on('mouseleave', () => hoverNode(null));
  nodeSel.append('circle').attr('r', 5);
  nodeSel.append('text').attr('y', -10).text(d => d.name);

  sim.on('tick', () => {
    edgeSel
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    nodeSel.attr('transform', d => `translate(${d.x}, ${d.y})`);
  });

  function drag(sim) {
    return d3.drag()
      .on('start', (ev, d) => {
        if (!ev.active) sim.alphaTarget(0.25).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => {
        if (!ev.active) sim.alphaTarget(0);
        d.fx = null; d.fy = null;
      });
  }

  // ─── visibility / focus / hover ───
  function isVisibleEdge(e) {
    return state.lenses.has(e.lens) && state.layers.has(getLayer(e.source)) && state.layers.has(getLayer(e.target));
  }
  function getLayer(node) { return typeof node === 'string' ? null : node.layer; }

  function updateVisibility() {
    edgeSel.style('display', d => state.lenses.has(d.lens) ? null : 'none');
    nodeSel.style('opacity', d => state.layers.has(d.layer) ? 1 : 0.15);
    const vN = nodes.filter(n => state.layers.has(n.layer)).length;
    const vE = edges.filter(e => state.lenses.has(e.lens)).length;
    const lensLbl = [...state.lenses].join(' + ') || 'no lens';
    statusEl.textContent = `${vN} nodes · ${vE} edges · ${lensLbl}`;
  }

  function neighborsOf(id) {
    const ns = new Set();
    edges.forEach(e => {
      if (!state.lenses.has(e.lens)) return;
      if (e.source.id === id) ns.add(e.target.id);
      if (e.target.id === id) ns.add(e.source.id);
    });
    return ns;
  }

  function focusNode(d) {
    state.focused = d.id;
    const ns = neighborsOf(d.id);
    nodeSel.classed('focused', n => n.id === d.id);
    nodeSel.classed('dim', n => n.id !== d.id && !ns.has(n.id));
    edgeSel.classed('focused', e => state.lenses.has(e.lens) && (e.source.id === d.id || e.target.id === d.id));
    edgeSel.classed('dim', e => !state.lenses.has(e.lens) || (e.source.id !== d.id && e.target.id !== d.id));
    renderInspect(d);
  }

  function hoverNode(d) {
    if (state.focused) return;
    if (!d) {
      nodeSel.classed('dim', false).classed('focused', false);
      edgeSel.classed('focused', false).classed('dim', false);
      return;
    }
    const ns = neighborsOf(d.id);
    nodeSel.classed('focused', n => n.id === d.id);
    nodeSel.classed('dim', n => n.id !== d.id && !ns.has(n.id));
    edgeSel.classed('focused', e => state.lenses.has(e.lens) && (e.source.id === d.id || e.target.id === d.id));
    edgeSel.classed('dim', e => !state.lenses.has(e.lens) || (e.source.id !== d.id && e.target.id !== d.id));
  }

  function renderInspect(d) {
    const lyr = data.layers.find(l => l.id === d.layer);
    const out = edges.filter(e => e.source.id === d.id && state.lenses.has(e.lens));
    const inc = edges.filter(e => e.target.id === d.id && state.lenses.has(e.lens));

    let html = `<h2>${d.name}</h2>
      <span class="layer-tag">${lyr.label}${d.region ? ' · ' + d.region : ''}</span>
      <p class="blurb">${d.blurb || ''}</p>`;

    if (d.metrics && Object.keys(d.metrics).length) {
      html += `<h3>metrics</h3><ul class="metrics">`;
      for (const k in d.metrics) {
        html += `<li><span class="k">${k}</span><span class="v">${d.metrics[k]}</span></li>`;
      }
      html += `</ul>`;
    }

    if (out.length) {
      html += `<h3>outgoing — ${out.length}</h3><ul class="edge-list">`;
      out.forEach(e => {
        html += `<li><span class="lens-${e.lens} arrow">→</span><div><span class="target" data-target="${e.target.id}">${e.target.name}</span><div class="weight">${e.label || ''}</div></div></li>`;
      });
      html += `</ul>`;
    }
    if (inc.length) {
      html += `<h3>incoming — ${inc.length}</h3><ul class="edge-list">`;
      inc.forEach(e => {
        html += `<li><span class="lens-${e.lens} arrow">←</span><div><span class="target" data-target="${e.source.id}">${e.source.name}</span><div class="weight">${e.label || ''}</div></div></li>`;
      });
      html += `</ul>`;
    }

    inspectEl.innerHTML = html;
    inspectEl.querySelectorAll('.target').forEach(el => {
      el.addEventListener('click', () => {
        const n = nodes.find(x => x.id === el.dataset.target);
        if (n) focusNode(n);
      });
    });
  }

  // ─── search ───
  searchEl.addEventListener('input', () => {
    const q = searchEl.value.trim().toLowerCase();
    if (!q) {
      if (!state.focused) {
        nodeSel.classed('dim', false).classed('focused', false);
        edgeSel.classed('focused', false).classed('dim', false);
      }
      return;
    }
    const matches = nodes.filter(n => n.name.toLowerCase().includes(q));
    if (matches.length === 1) {
      focusNode(matches[0]);
    } else {
      state.focused = null;
      nodeSel.classed('focused', n => n.name.toLowerCase().includes(q));
      nodeSel.classed('dim', n => !n.name.toLowerCase().includes(q));
      edgeSel.classed('focused', false).classed('dim', true);
    }
  });

  // clear focus on bg click
  svgEl.addEventListener('click', (ev) => {
    if (ev.target === svgEl) {
      state.focused = null;
      nodeSel.classed('focused', false).classed('dim', false);
      edgeSel.classed('focused', false).classed('dim', false);
      inspectEl.innerHTML = '<div class="empty">// click a node to inspect.</div>';
    }
  });

  // ─── resize ───
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const d = dims(); w = d.w; h = d.h;
      svgEl.setAttribute('viewBox', `0 0 ${w} ${h}`);
      sim.force('x', d3.forceX(w / 2).strength(0.03));
      sim.force('y', d3.forceY(node => layerY(node.layer)).strength(0.6));
      sim.alpha(0.4).restart();
    }, 120);
  });

  updateVisibility();
})();
