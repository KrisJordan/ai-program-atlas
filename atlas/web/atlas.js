/* Static enhancement: URL state is the single source of truth. */
(() => {
  'use strict';
  const node = document.getElementById('atlas-data');
  if (!node) return;
  const {programs, institutions, base_path: base, categories} = JSON.parse(node.textContent);
  document.documentElement.classList.add('js');
  const keys = ['q', 'award', 'calendar', 'institution', 'cohort', 'category'];
  const institutionMap = new Map(institutions.map(i => [i.id, i]));
  const form = document.getElementById('filters');
  const controls = Object.fromEntries(keys.map(k => [k, form.elements.namedItem(k)]));
  const byId = new Map(programs.map(p => [p.id, p]));
  const cards = [...document.querySelectorAll('[data-program-id]')];
  let selected = [];
  let timer;
  const courses = p => [...new Map((p.courses || []).map(c => [c.id, c])).values()];
  const pretty = x => String(x || 'unknown').replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
  const e = x => String(x ?? 'Unknown').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const urlSafe = u => /^https?:\/\//.test(u || '');
  const link = (url, label) => urlSafe(url) ? `<a href="${e(url)}" rel="noopener noreferrer">${e(label)} ↗</a>` : e(label);
  const announce = text => { document.getElementById('compare-status').textContent = text; };

  function readState() {
    const params = new URLSearchParams(location.search);
    keys.forEach(key => {
      const value = params.get(key) || '';
      controls[key].value = value;
      if (key !== 'q' && ![...controls[key].options].some(o => o.value === value)) controls[key].value = '';
    });
    selected = [...new Set((params.get('compare') || '').split(','))].filter(id => byId.has(id)).slice(0, 4);
  }

  function writeState() {
    const params = new URLSearchParams();
    keys.forEach(key => { if (controls[key].value) params.set(key, controls[key].value); });
    if (selected.length) params.set('compare', selected.join(','));
    const next = base + (params.size ? '?' + params.toString() : '') + location.hash;
    if (next !== location.pathname + location.search + location.hash) history.pushState(null, '', next);
    render();
  }

  function matches(p) {
    const query = controls.q.value.trim().toLocaleLowerCase();
    const allCourses = courses(p);
    const searchable = [p.title, p.overview, p.hosting_unit, p.institution?.name, ...(p.institution?.aliases || []), ...allCourses.flatMap(c => [c.name, c.code])].join(' ').toLocaleLowerCase();
    return (!query || query.split(/\s+/).every(term => searchable.includes(term))) &&
      (!controls.award.value || p.award_level === controls.award.value) &&
      (!controls.calendar.value || (p.institution?.calendar || 'unknown') === controls.calendar.value) &&
      (!controls.institution.value || p.institution?.id === controls.institution.value) &&
      (!controls.cohort.value || (institutionMap.get(p.institution?.id)?.rankings || []).some(r => r.category === controls.cohort.value)) &&
      (!controls.category.value || allCourses.some(c => (categories[c.category] ? c.category : 'other') === controls.category.value));
  }

  function outcomeList(p, kind) {
    const items = (p.outcomes || []).filter(o => o.kind === kind);
    const sources = new Map((p.sources || []).map(s => [s.id, s]));
    return items.length ? '<ul>' + items.map(o => `<li>${e(o.text)}<small>${link(sources.get(o.source_id)?.url, 'Source')}</small></li>`).join('') + '</ul>' : '<span class="muted">Not recorded</span>';
  }

  function renderComparison() {
    const target = document.getElementById('comparison-content');
    document.getElementById('compare-tray').hidden = selected.length === 0;
    document.getElementById('tray-count').textContent = `${selected.length} of 4 selected`;
    document.getElementById('clear-comparison').hidden = selected.length === 0;
    if (!selected.length) {
      target.innerHTML = '<p class="comparison-placeholder">Select “Compare” on a program to begin.</p>';
      return;
    }
    const items = selected.map(id => byId.get(id));
    const rows = [
      ['Award / type', p => e(p.award_level) + '<small>' + e(pretty(p.program_kind)) + '</small>'],
      ['Calendar', p => e(pretty(p.institution?.calendar))],
      ['Catalog year', p => e(p.catalog_year)],
      ['Last verified', p => e(p.last_verified || 'Not recorded')],
      ['Evidence status', p => e(pretty(p.verification_status)) + '<small>Curriculum: ' + e(pretty(p.curriculum_status)) + '</small>'],
      ['Course records', p => `${courses(p).length} unique records<small>${courses(p).filter(c => c.credits == null).length} with unknown credits; not a degree total</small>`],
      ['Credit units', p => { const units = [...new Set(courses(p).map(c => pretty(c.credit_unit)))]; return e(units.join(', ') || 'Unknown') + '<small>No cross-calendar conversion</small>'; }],
      ['Requirement structure', p => { const roots = (p.requirements || []).filter(r => !r.parent_id); return roots.length ? '<ul>' + roots.map(r => `<li>${e(r.title)}<small>${e(pretty(r.kind))}${r.count != null ? ' · ' + e(r.count) + ' courses' : ''}${r.credits != null ? ' · ' + e(r.credits) + ' ' + e(pretty(r.credit_unit)) : ''}</small></li>`).join('') + '</ul><small>Nested choices and full evidence on program page.</small>' : 'Not yet extracted'; }],
      ['Course categories', p => '<dl class="mini-counts">' + Object.entries(categories).map(([key, label]) => `<dt>${e(label)}</dt><dd>${courses(p).filter(c => (categories[c.category] ? c.category : 'other') === key).length}</dd>`).join('') + '</dl><small>Observed course counts; incomplete curricula may omit categories.</small>'],
      ['Source-stated outcomes', p => outcomeList(p, 'source_stated')],
      ['Inferred taxonomy', p => outcomeList(p, 'inferred_taxonomy') + '<small>Editorial interpretation</small>'],
      ['Official evidence', p => (p.links || []).map(l => link(l.url, l.label || pretty(l.kind))).join('<br>') || 'Not recorded'],
    ];
    target.innerHTML = `<div class="table-scroll" role="region" aria-label="Program comparison" tabindex="0"><table class="compare-table"><caption class="sr-only">Comparison of ${items.length} selected programs. Credit units remain distinct and unknown values are not zero.</caption><thead><tr><th scope="col">Program context</th>${items.map(p => `<th scope="col"><small>${e(p.institution?.name)}</small><a href="${base}programs/${e(p.id)}/">${e(p.title)}</a><button type="button" class="text-button remove" data-remove="${e(p.id)}" aria-label="Remove ${e(p.title)} at ${e(p.institution?.name)}">Remove</button></th>`).join('')}</tr></thead><tbody>${rows.map(([title, content]) => `<tr><th scope="row">${title}</th>${items.map(p => '<td>' + content(p) + '</td>').join('')}</tr>`).join('')}</tbody></table></div>`;
    target.querySelectorAll('[data-remove]').forEach(button => button.addEventListener('click', () => {
      selected = selected.filter(id => id !== button.dataset.remove);
      writeState();
      announce(`${selected.length} of 4 programs selected.`);
      document.getElementById('compare-title').setAttribute('tabindex', '-1');
      document.getElementById('compare-title').focus({preventScroll: true});
    }));
  }

  function render() {
    let count = 0;
    cards.forEach(card => {
      const show = matches(byId.get(card.dataset.programId));
      card.hidden = !show;
      if (show) count++;
    });
    document.getElementById('result-count').textContent = `${count} ${count === 1 ? 'program' : 'programs'}${count !== programs.length ? ' of ' + programs.length : ''}`;
    document.getElementById('empty-state').hidden = count > 0;
    document.querySelectorAll('[data-compare]').forEach(input => { input.checked = selected.includes(input.dataset.compare); });
    renderComparison();
  }

  form.addEventListener('submit', event => { event.preventDefault(); clearTimeout(timer); writeState(); });
  controls.q.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(writeState, 220); });
  keys.filter(k => k !== 'q').forEach(key => controls[key].addEventListener('change', () => { clearTimeout(timer); writeState(); }));
  const reset = () => { clearTimeout(timer); keys.forEach(key => { controls[key].value = ''; }); writeState(); };
  document.getElementById('reset-filters').addEventListener('click', reset);
  document.getElementById('empty-reset').addEventListener('click', () => { reset(); controls.q.focus(); });
  document.getElementById('clear-comparison').addEventListener('click', () => { selected = []; writeState(); announce('Comparison cleared.'); });
  document.querySelectorAll('[data-compare]').forEach(input => input.addEventListener('change', () => {
    const id = input.dataset.compare;
    if (input.checked && selected.length === 4) { input.checked = false; announce('Choose up to four programs. Remove a selection to add another.'); return; }
    selected = input.checked ? [...selected, id] : selected.filter(value => value !== id);
    clearTimeout(timer);
    writeState();
    announce(`${selected.length} of 4 programs selected. Comparison updated below.`);
  }));
  window.addEventListener('popstate', () => { clearTimeout(timer); readState(); render(); announce(selected.length ? `${selected.length} of 4 programs selected.` : ''); });
  readState();
  render();
})();
