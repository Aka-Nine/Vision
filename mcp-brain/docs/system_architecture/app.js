// ── Navigation ──────────────────────────────────────────────────────
function showSection(id, el) {
  document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (el) el.classList.add('active');
}

// ── Tab Switching ────────────────────────────────────────────────────
function switchTab(tabId, btn, groupId) {
  const group = document.getElementById(groupId);
  group.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  group.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');
}

// ── Pipeline Steps ──────────────────────────────────────────────────
function toggleStep(el) {
  const detail = el.querySelector('.step-detail');
  const isOpen = detail.classList.contains('open');
  document.querySelectorAll('.step-detail').forEach(d => d.classList.remove('open'));
  document.querySelectorAll('.pipeline-step').forEach(s => s.classList.remove('open'));
  if (!isOpen) {
    detail.classList.add('open');
    el.classList.add('open');
  }
}

// ── Failure Cards ───────────────────────────────────────────────────
function toggleFailure(el) {
  const body = el.querySelector('.failure-body');
  const isOpen = body.classList.contains('open');
  document.querySelectorAll('.failure-body').forEach(b => b.classList.remove('open'));
  if (!isOpen) body.classList.add('open');
}

// ── Component Explorer ──────────────────────────────────────────────
function renderComponentGrid() {
  const grid = document.getElementById('comp-grid');
  if (!grid) return;
  grid.innerHTML = window.COMPONENTS.map(c => `
    <button class="comp-btn" onclick="selectComponent('${c.id}')" id="btn-${c.id}">
      <div class="comp-file">${c.file}</div>
      <div class="comp-name">${c.name}</div>
      <span class="comp-tag tag-${c.tag}">${c.layer}</span>
    </button>
  `).join('');
  // auto-select first
  selectComponent(window.COMPONENTS[0].id);
}

function selectComponent(id) {
  document.querySelectorAll('.comp-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('btn-' + id);
  if (btn) btn.classList.add('active');

  const c = window.COMPONENTS.find(x => x.id === id);
  if (!c) return;

  const det = document.getElementById('comp-detail');
  det.classList.add('active');

  det.innerHTML = `
    <div class="comp-detail-header">
      <div class="comp-detail-meta">
        <span class="comp-tag tag-${c.tag}" style="margin-bottom:0.5rem;display:inline-block">${c.layer}</span>
        <h2 style="margin-top:0.4rem">${c.name}</h2>
        <code style="font-size:0.9rem">${c.file}</code>
      </div>
    </div>

    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('t-why','this','comp-tabs')">Why It Exists</button>
      <button class="tab-btn" onclick="switchTab('t-what','this','comp-tabs')">What It Does</button>
      <button class="tab-btn" onclick="switchTab('t-io','this','comp-tabs')">I/O & Methods</button>
      <button class="tab-btn" onclick="switchTab('t-flow','this','comp-tabs')">Data Flow</button>
      <button class="tab-btn" onclick="switchTab('t-future','this','comp-tabs')">Future Growth</button>
      <button class="tab-btn" onclick="switchTab('t-alt','this','comp-tabs')">Alternatives</button>
    </div>

    <div id="comp-tabs">
      <div class="tab-panel active" id="t-why">
        <div class="insight"><strong>Role in the System</strong>${c.why}</div>
      </div>

      <div class="tab-panel" id="t-what">
        <p>${c.what}</p>
        ${c.failures ? `<div class="insight warn"><strong>Failure Handling</strong>${c.failures}</div>` : ''}
      </div>

      <div class="tab-panel" id="t-io">
        <h3>Inputs</h3>
        <div>${c.inputs.map(i => `<span class="data-badge badge-in">${i}</span>`).join('')}</div>
        <h3>Outputs</h3>
        <div>${c.outputs.map(o => `<span class="data-badge badge-out">${o}</span>`).join('')}</div>
        <h3>Key Methods</h3>
        <div>${c.methods.map(m => `<span class="data-badge badge-dep">${m}</span>`).join('')}</div>
        <h3>Dependencies</h3>
        <div>${c.deps.map(d => `<span class="data-badge badge-dep">${d}</span>`).join('')}</div>
      </div>

      <div class="tab-panel" id="t-flow">
        <pre>${c.dataFlow}</pre>
      </div>

      <div class="tab-panel" id="t-future">
        <div class="insight future"><strong>Growth Roadmap</strong>${c.future}</div>
      </div>

      <div class="tab-panel" id="t-alt">
        <div class="insight alt"><strong>Alternative Approaches</strong>${c.alternatives}</div>
      </div>
    </div>
  `;

  // Fix tab buttons inside dynamic content
  det.querySelectorAll('.tab-btn').forEach((btn, i) => {
    const panels = ['t-why','t-what','t-io','t-flow','t-future','t-alt'];
    btn.onclick = () => switchTab(panels[i], btn, 'comp-tabs');
  });
}

// ── Init ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderComponentGrid();

  // start on hld
  const firstNav = document.querySelector('nav a');
  if (firstNav) firstNav.classList.add('active');
  document.getElementById('hld').classList.add('active');
});
