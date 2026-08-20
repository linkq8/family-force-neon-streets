(() => {
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const panels = [...document.querySelectorAll('[role="tabpanel"]')];
  const storageKey = 'family-force-commercial-guide-v1';
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch (_) { stored = {}; }

  function openTab(id, focus = false) {
    tabs.forEach(tab => {
      const selected = tab.dataset.tab === id;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && focus) tab.focus();
    });
    panels.forEach(panel => {
      const selected = panel.id === id;
      panel.hidden = !selected;
      panel.classList.toggle('active', selected);
    });
    history.replaceState(null, '', `#${id}`);
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => openTab(tab.dataset.tab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
        : (index + (event.key === 'ArrowLeft' ? 1 : -1) + tabs.length) % tabs.length;
      openTab(tabs[next].dataset.tab, true);
    });
  });
  document.querySelectorAll('[data-goto]').forEach(button => button.addEventListener('click', () => openTab(button.dataset.goto, true)));
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));

  const checks = [...document.querySelectorAll('input[type="checkbox"]')];
  checks.forEach((input, index) => {
    input.dataset.checkId = `${input.closest('[data-check-group]')?.dataset.checkGroup || 'misc'}-${index}`;
    input.checked = Boolean(stored[input.dataset.checkId]);
    input.addEventListener('change', saveChecks);
  });
  function saveChecks() {
    const value = {};
    checks.forEach(input => { if (input.checked) value[input.dataset.checkId] = true; });
    localStorage.setItem(storageKey, JSON.stringify(value));
    updateQa();
  }
  document.querySelectorAll('[data-reset]').forEach(button => button.addEventListener('click', () => {
    const group = button.dataset.reset;
    checks.forEach(input => {
      if (group === 'all' || input.dataset.checkId.startsWith(`${group}-`)) input.checked = false;
    });
    saveChecks();
  }));

  const form = document.getElementById('order-form');
  const output = document.getElementById('estimate-output');
  const bands = { base: [8, 14], hero: [4, 10], weapon: [2, 5], stage: [20, 45], enemy: [8, 18] };
  function estimate() {
    const data = new FormData(form);
    const heroes = Math.max(0, Number(data.get('heroes')) || 0);
    const weapons = Math.max(0, Number(data.get('weapons')) || 0);
    const stages = Math.max(0, Number(data.get('stages')) || 0);
    const enemies = Math.max(0, Number(data.get('enemies')) || 0);
    const low = bands.base[0] + heroes * bands.hero[0] + weapons * bands.weapon[0] + stages * bands.stage[0] + enemies * bands.enemy[0];
    const high = bands.base[1] + heroes * bands.hero[1] + weapons * bands.weapon[1] + stages * bands.stage[1] + enemies * bands.enemy[1];
    const rate = Math.max(0, Number(data.get('rate')) || 0);
    output.innerHTML = `<div><dt>ساعات تقديرية</dt><dd>${low}–${high}</dd></div>` +
      `<div><dt>نقاط اعتماد</dt><dd>${2 + heroes + stages}</dd></div>` +
      `<div><dt>سعر تقديري</dt><dd>${rate ? `${(low * rate).toLocaleString()}–${(high * rate).toLocaleString()}` : 'أدخل سعر الساعة'}</dd></div>`;
  }
  form.addEventListener('input', estimate);

  function updateQa() {
    const qa = checks.filter(input => input.dataset.checkId.startsWith('qa-'));
    const done = qa.filter(input => input.checked).length;
    const percent = qa.length ? Math.round(done / qa.length * 100) : 0;
    document.getElementById('qa-progress').textContent = `${percent}%`;
    const verdict = document.getElementById('qa-verdict');
    verdict.textContent = percent === 100 ? 'جاهز بعد اعتماد المسؤول' : 'غير جاهز للتسليم';
    verdict.closest('.release-gate').classList.toggle('ready', percent === 100);
  }

  const initial = location.hash.slice(1);
  openTab(panels.some(panel => panel.id === initial) ? initial : 'overview');
  estimate();
  updateQa();
})();
