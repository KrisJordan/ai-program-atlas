/* Static enhancement: URL state is the single source of truth. */
(() => {
  'use strict';
  const node = document.getElementById('atlas-data');
  if (!node) return;
  const {programs, institutions, families = [], base_path: base, categories} = JSON.parse(node.textContent);
  document.documentElement.classList.add('js');
  const keys = ['q', 'type', 'award', 'evidence', 'calendar', 'institution', 'cohort', 'category', 'discipline'];
  const familyMap = new Map(families.map(f => [f.id, f]));
  const cohortSections = [...document.querySelectorAll('[data-cohort-group]')];
  const pathState = Object.fromEntries(cohortSections.map(section => [section.dataset.cohortGroup, 'majors']));
  const awardState = Object.fromEntries(cohortSections.map(section => [section.dataset.cohortGroup, '']));
  const majorMatches = p => p.program_path !== 'majors' || !awardState[p.cohort_group] || p.major_awards.includes(awardState[p.cohort_group]);
  const pathForType = type => ({minor: 'minors', concentration: 'concentrations', degree: 'majors', additional_major: 'majors'}[type]);
  const familyPanels = [...document.querySelectorAll('[data-family-id]')];
  let expanded = [];
  let expansionSpecified = false;
  const institutionMap = new Map(institutions.map(i => [i.id, i]));
  const form = document.getElementById('filters');
  const filterPanel = document.getElementById('filter-panel');
  const controls = Object.fromEntries(keys.map(k => [k, form.elements.namedItem(k)]));
  const byId = new Map(programs.map(p => [p.id, p]));
  const cards = [...document.querySelectorAll('[data-program-id]')];
  let selected = [];
  let profileMode = 'required';
  const sortControl = document.getElementById('sort-order');
  const profileControl = document.getElementById('compare-profile');
  let timer;
  // Search text and course counts are projected once at build time.
  const searchIndex = new Map(programs.map(p => [p.id, p.search_text.toLocaleLowerCase()]));
  const pretty = x => String(x || 'unknown').replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
  const relationshipLabel = p => ({ai_plus_x: 'AI + another discipline', x_plus_ai: 'Another discipline + AI', integrated: 'Integrated program'}[p.family?.relationship] || 'Not recorded');
  const e = x => String(x ?? 'Unknown').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const urlSafe = u => /^https?:\/\//.test(u || '');
  const link = (url, label) => urlSafe(url) ? `<a href="${e(url)}" rel="noopener noreferrer">${e(label)} ↗</a>` : e(label);
  const rankLabel = r => r.rank != null ? `#${r.rank}` : r.rank_upper_bound != null ? `Top ${r.rank_upper_bound} · exact rank unverified` : 'Exact rank unverified';
  const requirementCount = (r, p) => { const noun = r.kind === 'alternative' ? 'alternative' : r.has_children ? 'selection' : 'course'; return `${r.count} ${noun}${r.count === 1 ? '' : 's'}`; };
  const announce = text => { document.getElementById('compare-status').textContent = text; };
  const requirementScope = p => {
    const scope = {concentration: 'Concentration requirements only; not the whole parent degree.', minor: 'Minor requirements only; not the whole degree.', additional_major: 'Additional-major requirements only; not the primary degree.', degree: 'Represented degree program at its recorded catalog year.'}[p.program_kind] || 'Represented program only.';
    const status = p.curriculum_status === 'complete' ? 'Complete requirement inventory. ' : p.curriculum_status === 'partial' ? 'Partial requirement inventory. ' : 'Requirement inventory not yet extracted. ';
    return e(status + scope) + '<small>Course metadata completeness is separate. Listed electives and alternatives are not all required.</small>';
  };
  const metadataCounts = p => {
    const profile = p.course_profile;
    return '<dl class="mini-counts">' + [['description', 'Descriptions'], ['prerequisites', 'Prerequisite statements'], ['credits', 'Credit amounts'], ['credit_unit', 'Known credit units']].map(([key, label]) => {
      const count = profile.metadata[key];
      return `<dt>${label}</dt><dd>${count} of ${profile.count}</dd>`;
    }).join('') + '</dl><small>Populated fields with recorded source URLs. Missing prerequisites do not mean none.</small>';
  };

  const selectionLabel = choice => {
    const parts = [];
    if (choice.count != null) {
      const noun = choice.kind === 'alternative' ? 'alternative' : choice.has_children ? 'selection' : 'course';
      parts.push(`Choose ${choice.count} ${noun}${choice.count === 1 ? '' : 's'}`);
    } else if (choice.kind === 'alternative') parts.push('Choose an alternative');
    if (choice.credits != null) parts.push(`${choice.credits} ${pretty(choice.credit_unit)} recorded`);
    return parts.join(' · ') || 'Selection amount not recorded';
  };
  const profileCell = p => {
    if (!p.course_profile.count) return '<div class="compare-profile-cell">Not yet extracted</div>';
    const profile = p.curriculum_profile;
    const group = profile[profileMode];
    const classification = group.classification || {reviewed:0, mixed:0, unclassified:0, unreviewed:group.count};
    const label = profileMode === 'required' ? 'fixed required course' : 'elective option';
    const note = profileMode === 'required' ? 'Mapped fixed course set; cohort, placement, waiver and substitution conditions in the sources still apply. Required choice blocks are separate below.' : 'Elective and required-choice candidates, not all compulsory. Fixed required courses are excluded.';
    const identityNote = profile.identity?.crosslisted_aliases ? `<p class="profile-identity">${group.count} mapped course identities from ${group.source_record_count ?? group.count} retained source-code records in this view. Only explicitly verified cross-lists are combined. The course table retains every source code and its evidence.</p>` : '';
    const countNoun = identityNote ? 'identities' : 'records';
    const roleNoun = identityNote ? 'course identities' : 'course records';
    const outsideNoun = profile.unresolved.count === 1 ? (identityNote ? 'course identity' : 'course record') : roleNoun;
    const empty = profileMode === 'required' ? 'A fixed required course set is not established; this does not mean there are no requirements.' : 'No option set is established by the structured rules.';
    return `<div class="compare-profile-cell"><p class="profile-total">${group.count} distinct ${label} ${countNoun}</p><p class="profile-denominator">${note}</p>${identityNote}<p class="profile-taxonomy">Taxonomy review: ${classification.reviewed} reviewed · ${classification.mixed} mixed · ${classification.unclassified} unclassified · ${classification.unreviewed} unreviewed, of ${group.count} mapped identities. Missing review is not verified classification. Requirement inventory completeness is separate.</p>${group.count ? '<dl class="mini-counts">' + Object.entries(categories).map(([key,name]) => `<dt>${e(name)}</dt><dd>${group.categories[key] || '0 mapped'}</dd>`).join('') + '</dl>' : '<p class="profile-unavailable">' + empty + '</p>'}<small>Distinct mapped course identities; not credit totals or degree shares. “0 mapped” means no mapped records classified here, not evidence that the curriculum lacks the subject. Partial requirement or taxonomy evidence can omit relevant courses.</small><p class="profile-uncertainty">${profile.unresolved.count} ${outsideNoun} ${profile.unresolved.count === 1 ? 'is' : 'are'} outside the fixed/option count profiles; see individual requirement rules for their context.${profile.overlap_count ? ' ' + profile.overlap_count + ' ' + roleNoun + ' appear in multiple groups and are counted once.' : ''}</p></div>`;
  };
  const profileChoices = p => {
    const choices = p.curriculum_profile.choices;
    if (!choices.length) return 'No structured selection rules recorded. Full requirements may contain unresolved notes.';
    const sources = new Map((p.sources || []).map(source => [source.id,source]));
    const contexts = {required:'Required selection',conditional:'Conditional selection',unresolved:'Selection context unresolved'};
    const origins = {family:'Shared family requirement',variant:'Local variant requirement',replacement:'Variant replacement'};
    return `<details class="profile-choices"><summary>${choices.length} documented selection rules</summary><ul>${choices.map(choice => `<li><strong>${e(choice.title)}</strong><div class="profile-choice-rule">${e(selectionLabel(choice))}</div><small>${e(contexts[choice.context] || contexts.unresolved)}${origins[choice.origin] ? ' · ' + e(origins[choice.origin]) : ''}</small><small>${link(sources.get(choice.source_id)?.url,'Source')} · <a href="${base}programs/${e(p.id)}/#requirement-${e(choice.id)}">Full requirement</a></small></li>`).join('')}</ul></details><small>Nested quantities are not summed. Course counts and credit units remain distinct; no pathway is selected.</small>`;
  };

  function readState() {
    const params = new URLSearchParams(location.search);
    sortControl.value = params.get('sort') === 'name' ? 'name' : 'rank';
    keys.forEach(key => {
      const value = params.get(key) || '';
      controls[key].value = value;
      if (key !== 'q' && ![...controls[key].options].some(o => o.value === value)) controls[key].value = '';
    });
    cohortSections.forEach(section => {
      const group = section.dataset.cohortGroup;
      const value = params.get('path_' + group);
      const award = params.get('award_' + group);
      awardState[group] = ['BS','BSE','BA','second_major','other'].includes(award) ? award : '';
      if (controls.type.value === 'additional_major' && awardState[group] === 'other') awardState[group] = '';
      section.querySelector('[data-major-award]').value = awardState[group];
      pathState[group] = pathForType(controls.type.value) || (['majors', 'concentrations', 'minors'].includes(value) ? value : pathForType(controls.award.value) || 'majors');
    });
    profileMode = params.get('profile') === 'options' ? 'options' : 'required';
    profileControl.value = profileMode;
    selected = [...new Set((params.get('compare') || '').split(','))].filter(id => byId.has(id)).slice(0, 4);
    expansionSpecified = params.has('expand');
    expanded = [...new Set((params.get('expand') || '').split(','))].filter(id => familyMap.has(id));
    if (!params.has('expand') && controls.discipline.value) programs.filter(p => (p.family?.disciplines || []).includes(controls.discipline.value)).forEach(p => { if (!expanded.includes(p.family.id)) expanded.push(p.family.id); });
    if (!params.has('expand')) selected.forEach(id => { const family = byId.get(id)?.family?.id; if (family && !expanded.includes(family)) expanded.push(family); });
  }

  function writeState() {
    const params = new URLSearchParams();
    if (sortControl.value === 'name') params.set('sort', 'name');
    keys.forEach(key => { if (controls[key].value) params.set(key, controls[key].value); });
    if (selected.length) params.set('compare', selected.join(','));
    if (profileMode === 'options') params.set('profile', 'options');
    Object.entries(pathState).forEach(([group,path]) => { if (path !== 'majors') params.set('path_' + group, path); });
    Object.entries(awardState).forEach(([group,award]) => { if (award) params.set('award_' + group, award); });
    if (expanded.length || expansionSpecified) params.set('expand', expanded.join(','));
    const next = base + (params.size ? '?' + params.toString() : '') + location.hash;
    if (next !== location.pathname + location.search + location.hash) history.pushState(null, '', next);
    render();
  }

  function matches(p) {
    const query = controls.q.value.trim().toLocaleLowerCase();
    const searchable = searchIndex.get(p.id);
    return (!query || query.split(/\s+/).every(term => searchable.includes(term))) &&
      (!controls.type.value || p.program_kind === controls.type.value) &&
      (!controls.evidence.value || p.curriculum_status === controls.evidence.value) &&
      (!controls.award.value || p.award_level === controls.award.value || p.award_options.some(option => option.normalized === controls.award.value)) &&
      (!controls.calendar.value || (p.institution?.calendar || 'unknown') === controls.calendar.value) &&
      (!controls.institution.value || p.institution?.id === controls.institution.value) &&
      (!controls.cohort.value || (institutionMap.get(p.institution?.id)?.rankings || []).some(r => r.category === controls.cohort.value)) &&
      (!controls.category.value || p.course_profile.categories[controls.category.value] > 0) &&
      (!controls.discipline.value || (p.family?.disciplines || []).includes(controls.discipline.value));
  }

  function outcomeList(p, kind) {
    const items = (p.outcomes || []).filter(o => o.kind === kind);
    const sources = new Map((p.sources || []).map(s => [s.id, s]));
    const statementTypes = {learning_outcome: 'Learning outcome', program_aim: 'Program aim', career_pathway: 'Career pathway'};
    return items.length ? '<ul>' + items.map(o => {
      const labels = statementTypes[o.statement_type] ? [statementTypes[o.statement_type]] : [];
      if (kind === 'inferred_taxonomy') labels.push('Documented inference');
      else if (!labels.length) labels.push('Source statement');
      return `<li><span class="badge statement-type">${e(labels.join(' · '))}</span><p class="statement-text">${e(o.text)}</p><small>${link(sources.get(o.source_id)?.url, 'Source')}</small></li>`;
    }).join('') + '</ul>' : '<span class="muted">Not recorded</span>';
  }

  function researchComparison(items) {
    const contexts = items.map(p => p.research_context);
    const context = contexts.find(Boolean);
    if (!context) return '';
    const fields = context.rows;
    const cell = (p, field) => {
      const row = p.research_context?.rows.find(row => row.field === field);
      if (!row) return '<span class="muted">Source observation unavailable</span>';
      return `<strong>${e(row.score_text)}</strong><small>U.S. research rank: ${e(row.rank_text)}</small>${field !== 'aggregate' ? '<small>Adjusted publications: ' + e(row.adjusted_count_text) + '</small>' : ''}<small>${e(row.status_label)}</small>`;
    };
    return `<section class="research-comparison" aria-labelledby="research-comparison-title"><h3 id="research-comparison-title">Institution publication research context</h3><p class="section-note">CSRankings · ${e(context.year_start)}–${e(context.year_end)} · United States. These are institution-level publication measures, not undergraduate teaching or program quality. Programs at the same institution repeat the same context. U.S. ranks were computed before joining this Atlas cohort.</p><div class="table-scroll" role="region" aria-label="Institution research comparison" tabindex="0"><table class="compare-table research-table"><caption>Displayed research scores, U.S. ranks and adjusted publication counts</caption><thead><tr><th scope="col">Research selection</th>${items.map(p => `<th scope="col">${e(p.institution?.name)}<small>${e(p.title)}</small></th>`).join('')}</tr></thead><tbody>${fields.map(row => `<tr data-research-field="${e(row.field)}"><th scope="row">${e(row.label)}</th>${items.map(p => '<td>' + cell(p, row.field) + '</td>').join('')}</tr>`).join('')}</tbody></table></div><p class="section-note">Each field score is adjusted publications + 1. The five-field aggregate is their geometric mean, not an average rank. Scores use one decimal; adjusted counts here use three decimals. Missing observations stay unavailable and receive no zero score or last-place rank. <a href="${base}methodology/#research">Methodology, source snapshot &amp; reuse scope →</a></p></section>`;
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
      const changes = new Map((p.family?.requirement_overrides || []).map(change => [change.shared_id, change]));
      return requirements.length ? '<details class="compare-requirements"><summary>' + requirements.length + ' shared requirement groups</summary><ul>' + requirements.map(r => `<li>${e(r.title)}${changes.has(r.id) ? '<small><strong>' + (changes.get(r.id).operation === 'exclude' ? 'Excluded for this variant' : 'Replaced for this variant') + '</strong></small>' : ''}<small>${r.summary ? e(r.summary) + ' · ' : ''}${link(sources.get(r.source_id)?.url, 'Requirement source')}</small></li>`).join('') + '</ul></details><small>Groups include containers and choices, not a course total.' + (changes.size ? ' Explicit variant changes are recorded below.' : '') + '</small>' : 'Shared requirement structure not recorded';
    };
    const variantRequirementList = p => {
      if (!p.family) return 'No family relationship recorded';
      const requirements = (p.requirements || []).filter(r => ['variant', 'replacement'].includes(r.origin));
      const sources = new Map((p.sources || []).map(source => [source.id, source]));
      const shared = new Map((familyMap.get(p.family.id)?.shared_requirements || []).map(r => [r.id, r]));
      const changes = (p.family.requirement_overrides || []).map(change => `<li><strong>${e(pretty(change.operation))}: ${e(shared.get(change.shared_id)?.title || change.shared_id)}</strong><small>${e(change.reason || 'Reason not recorded')}</small><small>${link(sources.get(change.source_id)?.url, 'Change source')}</small></li>`).join('');
      return requirements.length || changes ? (changes ? '<ul>' + changes + '</ul>' : '') + '<details class="compare-requirements"><summary>' + requirements.length + ' local requirement groups</summary><ul>' + requirements.map(r => `<li>${e(r.title)}<small>${r.origin === 'replacement' ? 'Replaces a shared requirement' : 'Local variant requirement'}${r.component && r.component !== 'other' ? ' · ' + e(pretty(r.component)) : ''}${r.summary ? ' · ' + e(r.summary) : ''}</small><small>${link(sources.get(r.source_id)?.url, 'Requirement source')}</small></li>`).join('') + '</ul></details><small>Local requirements outside the recorded shared set; not every item necessarily differs from other variants.</small>' : 'Variant differences not yet recorded';
    };
    const rows = [
      ['Program family', p => p.family ? e(familyMap.get(p.family.id)?.name || p.family.id) + '<small>' + e(pretty(familyMap.get(p.family.id)?.classification_kind)) + '</small>' : 'No family relationship recorded'],
      ['Concrete variant / disciplines', p => p.family ? e(p.family.variant_label || p.title) + '<small>' + e((p.family.disciplines || []).join(', ') || 'Disciplines not recorded') + '</small><small>Relationship: ' + e(relationshipLabel(p)) + '</small><small>Membership evidence: ' + e(pretty(p.family.classification_kind)) + '</small>' : e(p.title)],
      ['Shared family requirements', familyRequirementList],
      ['Variant requirements / changes', variantRequirementList],
      ['Award / type', p => e(p.major_awards.includes('second_major') ? 'No separate award' : p.award_level) + '<small>' + e(pretty(p.program_kind)) + '</small>' + (p.award_options.length ? '<small>Offered awards: ' + p.award_options.map(option => e(option.label)).join(' · ') + '</small>' : '')],
      ['Parent program / award', p => p.parent_context_html || 'Not applicable to this program type'],
      ['Second-major eligibility', p => p.major_context_html || 'No second-major-only relationship recorded'],
      ['U.S. News cohort context', p => { const ranks = institutionMap.get(p.institution?.id)?.rankings || p.institution?.rankings || []; return ranks.length ? ranks.map(r => link(r.source_url, `${r.publisher || 'U.S. News'} ${r.edition || 'Edition unknown'} · ${r.category || 'Category unknown'} · ${rankLabel(r)}`) + '<small>Membership evidence: ' + e(pretty(r.verification_status)) + '</small>').join('<br>') + '<small>Institution context, not teaching quality. Different categories are not comparable.</small>' : 'Ranking provenance not recorded'; }],
      ['Calendar', p => e(pretty(p.institution?.calendar))],
      ['Catalog year', p => e(p.catalog_year)],
      ['Last verified', p => e(p.last_verified || 'Not recorded')],
      ['Evidence status', p => e(pretty(p.verification_status)) + '<small>Curriculum: ' + e(pretty(p.curriculum_status)) + '</small>'],
      ['Requirement coverage', requirementScope],
      ['Course metadata availability', metadataCounts],
      ['Course records', p => `${p.course_profile.count} unique records<small>${p.course_profile.unknown_credits} with unknown credits; not a degree total</small>`],
      ['Credit units', p => { const units = p.course_profile.credit_units.map(pretty); return e(units.join(', ') || 'Unknown') + '<small>No cross-calendar conversion</small>'; }],
      ['Requirement structure', p => { const roots = (p.requirements || []).filter(r => r.is_root); return roots.length ? '<ul>' + roots.map(r => `<li>${e(r.title)}<small>${e(pretty(r.kind))}${r.count != null ? ' · ' + e(requirementCount(r, p)) : ''}${r.credits != null ? ' · ' + e(r.credits) + ' ' + e(pretty(r.credit_unit)) : ''}</small></li>`).join('') + '</ul><small>Nested choices and full evidence on program page.</small>' : 'Not yet extracted'; }],

      ['Program aims &amp; outcomes', p => outcomeList(p, 'source_stated')],
      ['Inferred taxonomy', p => outcomeList(p, 'inferred_taxonomy') + '<small>Editorial interpretation</small>'],
      ['Official evidence', p => (p.links || []).map(l => link(l.url, l.label || pretty(l.kind))).join('<br>') || 'Not recorded'],
    ];
    if (!items.some(p => p.family)) rows.splice(0, 4);
    rows.unshift(['Curriculum profile', profileCell], ['Documented selection rules', profileChoices]);
    const themes = [...new Set(items.flatMap(p => (p.outcomes || []).filter(o => o.kind === 'inferred_taxonomy').map(o => o.text)))].sort((a, b) => a.localeCompare(b));
    const themeCell = (p, theme) => {
      const matches = (p.outcomes || []).filter(o => o.kind === 'inferred_taxonomy' && o.text === theme);
      if (!matches.length) return '<span class="muted">Not recorded</span>';
      const sources = new Map((p.sources || []).map(s => [s.id, s]));
      return '<span class="badge">Documented inference</span>' + matches.map(o => '<small>' + link(sources.get(o.source_id)?.url, 'Supporting source') + '</small>').join('');
    };
    const themeMatrix = `<section class="theme-comparison" aria-labelledby="theme-title"><h3 id="theme-title">Recorded inferred themes</h3><p class="section-note">These are the exact inferred taxonomy labels stored in the records, shown as editorial interpretations with supporting sources. “Not recorded” is missing evidence, not proof that a program lacks a theme. Source statements about program aims and outcomes remain separate below.</p>${themes.length ? `<div class="table-scroll" role="region" aria-label="Recorded inferred theme matrix" tabindex="0"><table class="theme-table"><caption class="sr-only">Recorded inferred themes by program</caption><thead><tr><th scope="col">Theme</th>${items.map(p => `<th scope="col">${e(p.institution?.name)}<small>${e(p.title)}</small></th>`).join('')}</tr></thead><tbody>${themes.map(theme => `<tr><th scope="row">${e(theme)}</th>${items.map(p => '<td>' + themeCell(p, theme) + '</td>').join('')}</tr>`).join('')}</tbody></table></div>` : '<p class="notice">No inferred themes have been recorded for the selected programs.</p>'}</section>`;
    target.innerHTML = `<div class="table-scroll" role="region" aria-label="Program comparison" tabindex="0"><table class="compare-table"><caption class="sr-only">Comparison of ${items.length} selected programs. Credit units remain distinct and unknown values are not zero.</caption><thead><tr><th scope="col">Program context</th>${items.map(p => `<th scope="col"><small>${e(p.institution?.name)}</small><a href="${base}programs/${e(p.id)}/">${e(p.title)}</a><button type="button" class="text-button remove" data-remove="${e(p.id)}" aria-label="Remove ${e(p.title)} at ${e(p.institution?.name)}">Remove</button></th>`).join('')}</tr></thead><tbody>${rows.map(([title, content]) => `<tr><th scope="row">${title}</th>${items.map(p => '<td>' + content(p) + '</td>').join('')}</tr>`).join('')}</tbody></table></div>` + researchComparison(items) + themeMatrix;
    target.querySelectorAll('[data-remove]').forEach(button => button.addEventListener('click', () => {
      selected = selected.filter(id => id !== button.dataset.remove);
      writeState();
      announce(`${selected.length} of 4 programs selected.`);
      document.getElementById('compare-title').setAttribute('tabindex', '-1');
      document.getElementById('compare-title').focus({preventScroll: true});
    }));
  }

  function sortDirectory() {
    const compareText = (a, b) => a < b ? -1 : a > b ? 1 : 0;
    const compare = (a, b) => {
      if (sortControl.value === 'rank') {
        const rankA = a.dataset.sortRank ? Number(a.dataset.sortRank) : Infinity;
        const rankB = b.dataset.sortRank ? Number(b.dataset.sortRank) : Infinity;
        if (rankA !== rankB) return rankA < rankB ? -1 : 1;
      }
      for (const key of ['sortInstitution', 'sortTitle', 'sortId']) {
        const order = compareText(a.dataset[key] || '', b.dataset[key] || '');
        if (order) return order;
      }
      return 0;
    };
    document.querySelectorAll('.program-grid, .family-variants').forEach(container => {
      const entries = [...container.children];
      const ordered = [...entries].sort(compare);
      if (ordered.some((entry, index) => entry !== entries[index])) ordered.forEach(entry => container.append(entry));
    });
  }

  function render() {
    const filterLabels = {q:'Search',type:'Program type',award:'Award',evidence:'Evidence',calendar:'Calendar',institution:'Institution',cohort:'Category',category:'Course category',discipline:'Discipline'};
    const activeFilters = keys.filter(key => controls[key].value.trim()).map(key => `${filterLabels[key]}: ${key === 'q' ? controls[key].value.trim() : controls[key].selectedOptions[0]?.textContent || controls[key].value}`);
    const filterSummary = document.getElementById('active-filter-summary');
    filterSummary.textContent = activeFilters.length ? `${activeFilters.length} active ${activeFilters.length === 1 ? 'filter' : 'filters'} · ${activeFilters.slice(0,2).map(text => text.length > 64 ? text.slice(0,61) + '…' : text).join(' · ')}${activeFilters.length > 2 ? ` · +${activeFilters.length - 2} more` : ''}` : 'No search filters active';
    filterSummary.title = activeFilters.join(' · ');
    sortDirectory();
    let count = 0;
    cards.forEach(card => {
      const program = byId.get(card.dataset.programId);
      const show = matches(program) && majorMatches(program) && pathState[program.cohort_group] === program.program_path;
      card.hidden = !show;
      if (show) count++;
    });
    cohortSections.forEach(section => {
      const group = section.dataset.cohortGroup;
      const allCandidates = programs.filter(p => p.cohort_group === group && matches(p));
      const candidates = allCandidates.filter(majorMatches);
      const awardControl = section.querySelector('[data-major-award]');
      awardControl.value = awardState[group];
      const awardLabels = {'':'All awards',BS:'BS',BSE:'BSE',BA:'BA',second_major:'Second majors',other:'Other / unspecified'};
      [...awardControl.options].forEach(option => { const n = allCandidates.filter(p => p.program_path === 'majors' && (!option.value || p.major_awards.includes(option.value))).length; option.textContent = `${awardLabels[option.value]} (${n})`; });
      section.querySelectorAll('[role=tab]').forEach(tab => {
        const active = tab.dataset.path === pathState[group];
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
        tab.querySelector('.path-count').textContent = candidates.filter(p => p.program_path === tab.dataset.path).length;
      });
      section.querySelectorAll('[role=tabpanel]').forEach(panel => {
        panel.hidden = panel.dataset.path !== pathState[group];
        panel.querySelector('.cohort-empty').hidden = candidates.some(p => p.program_path === panel.dataset.path);
      });
      const activeCount = candidates.filter(p => p.program_path === pathState[group]).length;
      section.querySelector('.cohort-result-count').textContent = `${activeCount} ${activeCount === 1 ? 'program' : 'programs'} in active tab`;
      const labels = {nu: 'National Universities', lac: 'National Liberal Arts Colleges'};
      section.hidden = Boolean(controls.cohort.value && labels[group] !== controls.cohort.value);
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

  cohortSections.forEach(section => {
    const tabs = [...section.querySelectorAll('[role=tab]')];
    section.querySelector('[data-major-award]').addEventListener('change', event => { awardState[section.dataset.cohortGroup] = event.target.value; controls.award.value = ''; if ((event.target.value === 'second_major' && controls.type.value === 'degree') || (['BS','BSE','BA'].includes(event.target.value) && controls.type.value === 'additional_major')) controls.type.value = ''; clearTimeout(timer); writeState(); });
    const selectPath = tab => {
      pathState[section.dataset.cohortGroup] = tab.dataset.path;
      if (controls.type.value && pathForType(controls.type.value) !== tab.dataset.path) controls.type.value = '';
      clearTimeout(timer); writeState();
    };
    tabs.forEach((tab,index) => {
      tab.addEventListener('click', () => selectPath(tab));
      tab.addEventListener('keydown', event => {
        const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index + tabs.length - 1) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
        if (next !== null) { event.preventDefault(); selectPath(tabs[next]); tabs[next].focus(); }
      });
    });
  });
  familyPanels.forEach(panel => panel.querySelector(':scope > summary').addEventListener('click', event => {
    event.preventDefault();
    const id = panel.dataset.familyId;
    expansionSpecified = true;
    expanded = expanded.includes(id) ? expanded.filter(value => value !== id) : [...expanded, id];
    clearTimeout(timer);
    writeState();
  }));
  sortControl.addEventListener('change', () => { clearTimeout(timer); writeState(); });
  profileControl.addEventListener('change', () => { profileMode = profileControl.value; clearTimeout(timer); writeState(); announce(profileMode === 'required' ? 'Showing required curriculum profiles.' : 'Showing elective option profiles.'); });
  form.addEventListener('submit', event => { event.preventDefault(); clearTimeout(timer); writeState(); });
  controls.q.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(writeState, 220); });
  keys.filter(k => k !== 'q').forEach(key => controls[key].addEventListener('change', () => { clearTimeout(timer); if (key === 'award') { Object.keys(awardState).forEach(group => { awardState[group] = ''; }); const path = pathForType(controls.award.value) || (controls.award.value ? 'majors' : null); if (path) Object.keys(pathState).forEach(group => { pathState[group] = path; }); } if (key === 'type' && controls.type.value) Object.keys(pathState).forEach(group => { pathState[group] = pathForType(controls.type.value); awardState[group] = ''; }); if (key === 'discipline' && controls.discipline.value) programs.filter(p => (p.family?.disciplines || []).includes(controls.discipline.value)).forEach(p => { if (!expanded.includes(p.family.id)) expanded.push(p.family.id); }); writeState(); }));
  const reset = () => { clearTimeout(timer); sortControl.value = 'rank'; keys.forEach(key => { controls[key].value = ''; }); Object.keys(pathState).forEach(group => { pathState[group] = 'majors'; awardState[group] = ''; }); writeState(); };
  document.getElementById('reset-filters').addEventListener('click', reset);
  document.getElementById('empty-reset').addEventListener('click', () => { reset(); filterPanel.open = true; controls.q.focus(); });
  document.getElementById('clear-comparison').addEventListener('click', () => {
    selected = [];
    writeState();
    announce('Comparison cleared.');
    document.getElementById('compare-title').setAttribute('tabindex', '-1');
    document.getElementById('compare-title').focus({preventScroll: true});
  });
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
