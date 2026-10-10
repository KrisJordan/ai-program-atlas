/* Static enhancement: URL state is the single source of truth. */
(() => {
  'use strict';
  const node = document.getElementById('atlas-data');
  if (!node) return;
  const {programs, institutions, families = [], base_path: base, categories} = JSON.parse(node.textContent);
  document.documentElement.classList.add('js');
  const keys = ['q', 'type', 'award', 'evidence', 'calendar', 'institution', 'cohort', 'category', 'discipline'];
  const familyMap = new Map(families.map(f => [f.id, f]));
  const familyPanels = [...document.querySelectorAll('[data-family-id]')];
  let expanded = [];
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
  const rankLabel = r => r.rank != null ? `#${r.rank}` : r.rank_upper_bound != null ? `Top ${r.rank_upper_bound} · exact rank unverified` : 'Exact rank unverified';
  const requirementCount = (r, p) => { const noun = r.kind === 'alternative' ? 'alternative' : (p.requirements || []).some(child => child.parent_id === r.id) ? 'selection' : 'course'; return `${r.count} ${noun}${r.count === 1 ? '' : 's'}`; };
  const announce = text => { document.getElementById('compare-status').textContent = text; };
  const requirementScope = p => {
    const scope = {concentration: 'Concentration requirements only; not the whole parent degree.', minor: 'Minor requirements only; not the whole degree.', additional_major: 'Additional-major requirements only; not the primary degree.', degree: 'Represented degree program at its recorded catalog year.'}[p.program_kind] || 'Represented program only.';
    const status = p.curriculum_status === 'complete' ? 'Complete requirement inventory. ' : p.curriculum_status === 'partial' ? 'Partial requirement inventory. ' : 'Requirement inventory not yet extracted. ';
    return e(status + scope) + '<small>Course metadata completeness is separate. Listed electives and alternatives are not all required.</small>';
  };
  const metadataCounts = p => {
    const items = courses(p), sources = new Map((p.sources || []).map(s => [s.id, s]));
    return '<dl class="mini-counts">' + [['description', 'Descriptions'], ['prerequisites', 'Prerequisite statements'], ['credits', 'Credit amounts'], ['credit_unit', 'Known credit units']].map(([key, label]) => {
      const count = items.filter(c => (urlSafe(c.url) || urlSafe(sources.get(c.source_id)?.url)) && c[key] != null && c[key] !== '' && (key !== 'credit_unit' || c[key] !== 'unknown')).length;
      return `<dt>${label}</dt><dd>${count} of ${items.length}</dd>`;
    }).join('') + '</dl><small>Populated fields with recorded source URLs. Missing prerequisites do not mean none.</small>';
  };

  function readState() {
    const params = new URLSearchParams(location.search);
    keys.forEach(key => {
      const value = params.get(key) || '';
      controls[key].value = value;
      if (key !== 'q' && ![...controls[key].options].some(o => o.value === value)) controls[key].value = '';
    });
    selected = [...new Set((params.get('compare') || '').split(','))].filter(id => byId.has(id)).slice(0, 4);
    expanded = [...new Set((params.get('expand') || '').split(','))].filter(id => familyMap.has(id));
    if (!params.has('expand') && controls.discipline.value) programs.filter(p => (p.family?.disciplines || []).includes(controls.discipline.value)).forEach(p => { if (!expanded.includes(p.family.id)) expanded.push(p.family.id); });
    if (!params.has('expand')) selected.forEach(id => { const family = byId.get(id)?.family?.id; if (family && !expanded.includes(family)) expanded.push(family); });
  }

  function writeState() {
    const params = new URLSearchParams();
    keys.forEach(key => { if (controls[key].value) params.set(key, controls[key].value); });
    if (selected.length) params.set('compare', selected.join(','));
    if (expanded.length) params.set('expand', expanded.join(','));
    const next = base + (params.size ? '?' + params.toString() : '') + location.hash;
    if (next !== location.pathname + location.search + location.hash) history.pushState(null, '', next);
    render();
  }

  function matches(p) {
    const query = controls.q.value.trim().toLocaleLowerCase();
    const allCourses = courses(p);
    const searchable = [p.title, p.overview, p.hosting_unit, p.institution?.name, p.family?.variant_label, familyMap.get(p.family?.id)?.name, ...(p.family?.disciplines || []), ...(p.institution?.aliases || []), ...allCourses.flatMap(c => [c.name, c.code])].join(' ').toLocaleLowerCase();
    return (!query || query.split(/\s+/).every(term => searchable.includes(term))) &&
      (!controls.type.value || p.program_kind === controls.type.value) &&
      (!controls.evidence.value || p.curriculum_status === controls.evidence.value) &&
      (!controls.award.value || p.award_level === controls.award.value) &&
      (!controls.calendar.value || (p.institution?.calendar || 'unknown') === controls.calendar.value) &&
      (!controls.institution.value || p.institution?.id === controls.institution.value) &&
      (!controls.cohort.value || (institutionMap.get(p.institution?.id)?.rankings || []).some(r => r.category === controls.cohort.value)) &&
      (!controls.category.value || allCourses.some(c => (categories[c.category] ? c.category : 'other') === controls.category.value)) &&
      (!controls.discipline.value || (p.family?.disciplines || []).includes(controls.discipline.value));
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
    const familyRequirementList = p => {
      const family = familyMap.get(p.family?.id);
      if (!family) return 'No family relationship recorded';
      const requirements = family.shared_requirements || [];
      const sources = new Map([...(family.sources || []), ...(p.sources || [])].map(source => [source.id, source]));
      return requirements.length ? '<ul>' + requirements.map(r => `<li>${e(r.title)}<small>${r.summary ? e(r.summary) + ' · ' : ''}${link(sources.get(r.source_id)?.url, 'Requirement source')}</small></li>`).join('') + '</ul><small>Shared requirement groups include containers and choices; not a course total. Follow variant replacements below.</small>' : 'Shared requirement structure not recorded';
    };
    const variantRequirementList = p => {
      if (!p.family) return 'No family relationship recorded';
      const requirements = (p.requirements || []).filter(r => ['variant', 'replacement'].includes(r.origin));
      const sources = new Map((p.sources || []).map(source => [source.id, source]));
      return requirements.length ? '<ul>' + requirements.map(r => `<li>${e(r.title)}<small>${r.origin === 'replacement' ? 'Replaces a shared requirement' : 'Variant-specific'}${r.component && r.component !== 'other' ? ' · ' + e(pretty(r.component)) : ''}${r.summary ? ' · ' + e(r.summary) : ''}</small><small>${link(sources.get(r.source_id)?.url, 'Requirement source')}</small></li>`).join('') + '</ul>' : 'Variant differences not yet recorded';
    };
    const rows = [
      ['Program family', p => p.family ? e(familyMap.get(p.family.id)?.name || p.family.id) + '<small>' + e(pretty(p.family.classification_kind)) + '</small>' : 'No family relationship recorded'],
      ['Concrete variant / disciplines', p => p.family ? e(p.family.variant_label || p.title) + '<small>' + e((p.family.disciplines || []).join(', ') || 'Disciplines not recorded') + '</small>' : e(p.title)],
      ['Shared family requirements', familyRequirementList],
      ['Variant-specific requirements', variantRequirementList],
      ['Award / type', p => e(p.award_level) + '<small>' + e(pretty(p.program_kind)) + '</small>'],
      ['U.S. News cohort context', p => { const ranks = institutionMap.get(p.institution?.id)?.rankings || p.institution?.rankings || []; return ranks.length ? ranks.map(r => link(r.source_url, `${r.publisher || 'U.S. News'} ${r.edition || 'Edition unknown'} · ${r.category || 'Category unknown'} · ${rankLabel(r)}`) + '<small>Membership evidence: ' + e(pretty(r.verification_status)) + '</small>').join('<br>') + '<small>Institution context, not teaching quality. Different categories are not comparable.</small>' : 'Ranking provenance not recorded'; }],
      ['Calendar', p => e(pretty(p.institution?.calendar))],
      ['Catalog year', p => e(p.catalog_year)],
      ['Last verified', p => e(p.last_verified || 'Not recorded')],
      ['Evidence status', p => e(pretty(p.verification_status)) + '<small>Curriculum: ' + e(pretty(p.curriculum_status)) + '</small>'],
      ['Requirement coverage', requirementScope],
      ['Course metadata availability', metadataCounts],
      ['Course records', p => `${courses(p).length} unique records<small>${courses(p).filter(c => c.credits == null).length} with unknown credits; not a degree total</small>`],
      ['Credit units', p => { const units = [...new Set(courses(p).map(c => pretty(c.credit_unit)))]; return e(units.join(', ') || 'Unknown') + '<small>No cross-calendar conversion</small>'; }],
      ['Requirement structure', p => { const roots = (p.requirements || []).filter(r => !r.parent_id); return roots.length ? '<ul>' + roots.map(r => `<li>${e(r.title)}<small>${e(pretty(r.kind))}${r.count != null ? ' · ' + e(requirementCount(r, p)) : ''}${r.credits != null ? ' · ' + e(r.credits) + ' ' + e(pretty(r.credit_unit)) : ''}</small></li>`).join('') + '</ul><small>Nested choices and full evidence on program page.</small>' : 'Not yet extracted'; }],
      ['Course categories', p => courses(p).length ? '<dl class="mini-counts">' + Object.entries(categories).map(([key, label]) => `<dt>${e(label)}</dt><dd>${courses(p).filter(c => (categories[c.category] ? c.category : 'other') === key).length}</dd>`).join('') + '</dl><small>Observed course counts; incomplete curricula may omit categories.</small>' : 'Not yet extracted'],
      ['Source-stated outcomes', p => outcomeList(p, 'source_stated')],
      ['Inferred taxonomy', p => outcomeList(p, 'inferred_taxonomy') + '<small>Editorial interpretation</small>'],
      ['Official evidence', p => (p.links || []).map(l => link(l.url, l.label || pretty(l.kind))).join('<br>') || 'Not recorded'],
    ];
    if (!items.some(p => p.family)) rows.splice(0, 4);
    const themes = [...new Set(items.flatMap(p => (p.outcomes || []).filter(o => o.kind === 'inferred_taxonomy').map(o => o.text)))].sort((a, b) => a.localeCompare(b));
    const themeCell = (p, theme) => {
      const matches = (p.outcomes || []).filter(o => o.kind === 'inferred_taxonomy' && o.text === theme);
      if (!matches.length) return '<span class="muted">Not recorded</span>';
      const sources = new Map((p.sources || []).map(s => [s.id, s]));
      return '<span class="badge">Documented inference</span>' + matches.map(o => '<small>' + link(sources.get(o.source_id)?.url, 'Supporting source') + '</small>').join('');
    };
    const themeMatrix = `<section class="theme-comparison" aria-labelledby="theme-title"><h3 id="theme-title">Recorded outcome themes</h3><p class="section-note">These are the exact inferred taxonomy labels stored in the records, shown as editorial interpretations with supporting sources. “Not recorded” is missing evidence, not an absent learning outcome. Source-stated outcomes remain separate below.</p>${themes.length ? `<div class="table-scroll" role="region" aria-label="Recorded outcome theme matrix" tabindex="0"><table class="theme-table"><caption class="sr-only">Recorded inferred outcome themes by program</caption><thead><tr><th scope="col">Theme</th>${items.map(p => `<th scope="col">${e(p.institution?.name)}<small>${e(p.title)}</small></th>`).join('')}</tr></thead><tbody>${themes.map(theme => `<tr><th scope="row">${e(theme)}</th>${items.map(p => '<td>' + themeCell(p, theme) + '</td>').join('')}</tr>`).join('')}</tbody></table></div>` : '<p class="notice">No inferred outcome themes have been recorded for the selected programs.</p>'}</section>`;
    target.innerHTML = themeMatrix + `<div class="table-scroll" role="region" aria-label="Program comparison" tabindex="0"><table class="compare-table"><caption class="sr-only">Comparison of ${items.length} selected programs. Credit units remain distinct and unknown values are not zero.</caption><thead><tr><th scope="col">Program context</th>${items.map(p => `<th scope="col"><small>${e(p.institution?.name)}</small><a href="${base}programs/${e(p.id)}/">${e(p.title)}</a><button type="button" class="text-button remove" data-remove="${e(p.id)}" aria-label="Remove ${e(p.title)} at ${e(p.institution?.name)}">Remove</button></th>`).join('')}</tr></thead><tbody>${rows.map(([title, content]) => `<tr><th scope="row">${title}</th>${items.map(p => '<td>' + content(p) + '</td>').join('')}</tr>`).join('')}</tbody></table></div>`;
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
    let visibleFamilies = 0;
    familyPanels.forEach(panel => {
      const visible = [...panel.querySelectorAll('[data-program-id]')].filter(card => !card.hidden).length;
      panel.hidden = visible === 0;
      panel.open = expanded.includes(panel.dataset.familyId);
      if (visible) visibleFamilies++;
      panel.querySelector('.family-match-count').textContent = `${visible} matching ${visible === 1 ? 'variant' : 'variants'}`;
      panel.querySelector('.family-toggle').textContent = panel.open ? 'Hide variants' : 'View variants';
    });
    document.getElementById('result-count').textContent = `${count} ${count === 1 ? 'program' : 'programs'}${count !== programs.length ? ' of ' + programs.length : ''}${visibleFamilies ? ' · ' + visibleFamilies + ' program ' + (visibleFamilies === 1 ? 'family' : 'families') : ''}`;
    document.getElementById('empty-state').hidden = count > 0;
    document.querySelectorAll('[data-compare]').forEach(input => { input.checked = selected.includes(input.dataset.compare); });
    renderComparison();
  }

  familyPanels.forEach(panel => panel.querySelector(':scope > summary').addEventListener('click', event => {
    event.preventDefault();
    const id = panel.dataset.familyId;
    expanded = expanded.includes(id) ? expanded.filter(value => value !== id) : [...expanded, id];
    clearTimeout(timer);
    writeState();
  }));
  form.addEventListener('submit', event => { event.preventDefault(); clearTimeout(timer); writeState(); });
  controls.q.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(writeState, 220); });
  keys.filter(k => k !== 'q').forEach(key => controls[key].addEventListener('change', () => { clearTimeout(timer); if (key === 'discipline' && controls.discipline.value) programs.filter(p => (p.family?.disciplines || []).includes(controls.discipline.value)).forEach(p => { if (!expanded.includes(p.family.id)) expanded.push(p.family.id); }); writeState(); }));
  const reset = () => { clearTimeout(timer); keys.forEach(key => { controls[key].value = ''; }); writeState(); };
  document.getElementById('reset-filters').addEventListener('click', reset);
  document.getElementById('empty-reset').addEventListener('click', () => { reset(); controls.q.focus(); });
  document.getElementById('clear-comparison').addEventListener('click', () => { selected = []; writeState(); announce('Comparison cleared.'); });
  document.querySelectorAll('[data-compare]').forEach(input => input.addEventListener('change', () => {
    const id = input.dataset.compare;
    if (input.checked && selected.length === 4) { input.checked = false; announce('Choose up to four programs. Remove a selection to add another.'); return; }
    selected = input.checked ? [...selected, id] : selected.filter(value => value !== id);
    const family = byId.get(id)?.family?.id;
    if (input.checked && family && !expanded.includes(family)) expanded.push(family);
    clearTimeout(timer);
    writeState();
    announce(`${selected.length} of 4 programs selected. Comparison updated below.`);
  }));
  window.addEventListener('popstate', () => { clearTimeout(timer); readState(); render(); announce(selected.length ? `${selected.length} of 4 programs selected.` : ''); });
  readState();
  render();
})();
