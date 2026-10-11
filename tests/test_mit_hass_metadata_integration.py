"""Approved departmental evidence enriches rows without new review certification."""
import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_metadata')


def test_changed_actual_panel_cannot_replay_saved_metadata(monkeypatch):
    html = '''<h1>Classes</h1><div class="expcol-wrap">
    <div class="field--name-field-subject-number">4.123</div>
    <div class="faux-full-title">Test Studio</div>
    <div class="field--name-field-subject-description">Original studio work.</div>
    </div>'''
    observation = m.observer.observe_architecture(html)[0]
    url = 'https://architecture.mit.edu/example'
    review = dict(source_url=url, source_id='actual', approved_for_integration=True,
                  observation_digest=m.observer.observation_digest(observation),
                  category='applications', description_summary='Studio practice.',
                  prerequisites=None, credits=None, restrictions=[], catalog_year=None)
    monkeypatch.setattr(m, 'MANIFEST', {'courses': {'row': dict(
        listed_code='4.123', listed_name='Test Studio', listed_source_id='pool',
        review_status='reviewed', observations=[review])}})
    monkeypatch.setattr(m, 'INTEGRATED', {'course_ids': ['row']})
    monkeypatch.setattr(m, 'SPECS', {'actual': {'url': url, 'parser': 'architecture'}})
    parsed = m.parse(html, url)
    assert parsed['courses'][0]['id'] == 'row'
    assert parsed['courses'][0]['description'] == 'Studio practice.'
    assert parsed['courses'][0]['credits'] is None
    assert 'category_review' not in parsed['courses'][0]
    assert 'curriculum_audit' not in parsed
    assert m.parse(html.replace('Original studio work.', 'Changed studio scope.'), url)['courses'] == []


def test_integrated_evidence_preserves_term_rules_and_withholds_conflicts():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by = {c['id']: c for c in p['courses']}
    integrated = [by[cid] for cid in m.INTEGRATED['course_ids']]
    assert len(integrated) >= 70
    assert all(c.get('category_review') for c in integrated)
    assert sum(bool(c.get('description')) for c in integrated) >= 139
    limited = [c for c in integrated if any(o.get('evidence_basis') == 'official_title_only'
               and o['approved_for_integration'] for o in m.MANIFEST['courses'][c['id']]['observations'])]
    assert limited
    for c in limited:
        if c['description'] is None:
            assert 'Limited official-title-only' in c['category_review']['rationale']
        else:
            # A separately sourced content review can supersede the initial title disposition.
            evidence=[o for o in m.MANIFEST['courses'][c['id']]['observations']
                      if o['approved_for_integration'] and o.get('description_summary')==c['description']
                      and o['source_id'] in c['category_review']['source_ids']]
            assert evidence or 'mit-ai-clinic-review-news' in c['category_review']['source_ids']
    assert {s['url'] for s in m.SPECS.values()} <= {s['url'] for s in p['sources']}
    greek = [c for c in integrated if c['code'] in {'21L.607', '21L.608'}]
    assert greek and all(c['credits'] == 6 for c in greek)
    assert any(r['id'] == 'mit-ai-hass-reviewed-language-bundles' and r['kind'] == 'note'
               for r in p['requirements'])
    undergraduate = next(c for c in integrated if c['code'] == '4.603')
    assert undergraduate['prerequisites'] is None
    held = {cid for cid, row in m.MANIFEST['courses'].items()
            if row['review_status'] in {'identity_review_needed', 'source_conflict'}}
    assert held.isdisjoint(m.INTEGRATED['course_ids'])


def test_actual_integrated_source_replay_has_exact_approved_identity_scope():
    paths = {sid: Path(m.INTEGRATED.get('cache_paths', {}).get(sid,
                str(Path('/tmp/mit-hass-subjects') / m.INTEGRATED.get('cache_names', {}).get(
                sid, sid.removeprefix('mit-ai-hass-review-') + '.html'))))
             for sid in m.SPECS}
    if not all(p.exists() for p in paths.values()):
        pytest.skip('Optional ignored official source captures absent')
    rows = [c for sid, path in paths.items()
            for c in m.parse(path.read_text(), m.SPECS[sid]['url'])['courses']]
    assert {c['id'] for c in rows} == set(m.INTEGRATED['course_ids'])
    assert all('category_review' not in c for c in rows)


def test_current_cmsw_capture_does_not_certify_archived_term_records():
    path = Path('/tmp/mit-hass-subjects/cmsw-visible.html')
    if not path.exists():
        pytest.skip('Optional ordinary-browser visible source capture absent')
    url = m.SPECS['mit-ai-hass-review-cmsw-fall2026']['url']
    rows = m.parse(path.read_text(), url)['courses']
    assert rows
    assert all(c['source_id'] == 'mit-ai-hass-review-cmsw-fall2026' for c in rows)
    archived = {cid for cid in m.INTEGRATED['course_ids']
                if any(o['approved_for_integration'] and o['source_id'].endswith('cmsw-fall2025')
                       for o in m.MANIFEST['courses'][cid]['observations'])}
    assert archived and archived.isdisjoint({c['id'] for c in rows})


def test_same_source_metadata_composition_preserves_eligibility_and_known_units():
    original = lambda _: {'id': 'program', 'courses': [dict(id='c', credits=12, notes=['eligibility'])],
                          'requirements': [dict(id='field-plan', kind='choose_courses', count=3)]}
    metadata = lambda _: {'id': 'program', 'courses': [dict(id='c', credits=None, category='other', notes=['title only'])],
                          'requirements': [], 'observed_hass_description_digests': {'c': 'guard'}}
    out = m.with_metadata(original, metadata)('source')
    assert out['requirements'] == original('source')['requirements']
    assert len(out['courses']) == 1 and out['courses'][0]['credits'] == 12
    assert out['courses'][0]['category'] == 'other'
    assert out['courses'][0]['notes'] == ['eligibility', 'title only']


def test_actual_language_registration_keeps_preexisting_field_rules():
    path = Path('/tmp/atlas-mit-hass-rest-chinese.html')
    if not path.exists():
        pytest.skip('Optional ignored official source capture absent')
    adapter = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.adapter')
    fields = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_languages')
    url = 'https://languages.mit.edu/areas-of-study/chinese-studies/'
    before = fields.SOURCE_PARSERS[url](path.read_text())
    after = adapter.SOURCE_PARSERS[url](path.read_text())
    assert before['requirements'] == after['requirements']
    assert after['observed_hass_description_digests']
    assert len(adapter.SOURCES) == len(set(adapter.SOURCES))


def test_political_titles_do_not_inherit_pool_category_and_keep_explicit_credit():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    rows = [c for c in p['courses'] if c['id'].startswith('mit-ai-hass-political-subfields-')]
    by = {c['code']: c for c in rows}
    for code in ['17.835', '17.C08J', '17.811', '17.447J']:
        assert by[code]['category'] == 'other'
        assert by[code]['category_review']['status'] == 'unclassified'
        assert by[code]['description'] is None
    assert by['17.567']['credits'] == 9
    assert any('MISTI' in n for n in by['17.567']['notes'])


def test_explicit_cms_alias_content_keeps_sts_source_identity_and_mixed_scope():
    p = json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    rows = [c for c in p['courses'] if c['id'] in m.INTEGRATED['course_ids'] and c['code'] == 'STS.024']
    assert rows and all(c['description'] and c['category'] == 'other' for c in rows)
    assert all(c['category_review']['status'] == 'mixed' for c in rows)
    assert all(c['source_id'] != 'mit-ai-hass-review-cmsw-spring2026' for c in rows)
    merged = {cid for g in p.get('course_identity_groups', []) for cid in g['course_ids']}
    assert set(c['id'] for c in rows)<=merged
    group=next(g for g in p['course_identity_groups']if g['id']=='mit-ai-hass-cms524-sts024-spring2026')
    assert 'mit-ai-hass-review-cmsw-spring2026' in group['source_ids']


def test_economics_limited_title_review_preserves_printed_prerequisites_and_rules():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    assert by['mit-ai-hass-economics-14-16']['prerequisites']=='14.03/14.04'
    assert by['mit-ai-hass-economics-14-27']['prerequisites']=='14.30 or 6.041'
    assert by['mit-ai-hass-economics-14-15-j']['category_review']['status']=='unclassified'
    assert by['mit-ai-hass-economics-14-16']['description'] is None
    assert by['mit-ai-hass-economics-14-16']['credits'] is None
    path=Path('/tmp/atlas-mit-hass-economics.html')
    if not path.exists():pytest.skip('Optional public source capture absent')
    fields=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments')
    adapter=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.adapter')
    url=m.SPECS['mit-ai-hass-review-economics-titles']['url']
    actual=adapter.SOURCE_PARSERS[url](path.read_text())
    assert actual['requirements']==fields.parse_economics(path.read_text())['requirements']
    assert actual['observed_hass_description_digests']


def test_same_french_url_observes_both_titles_and_term_specific_prose():
    path=Path('/tmp/atlas-mit-hass-rest-french.html')
    if not path.exists():pytest.skip('Optional public source capture absent')
    url=m.SPECS['mit-ai-hass-review-french-spotlights']['url']
    rows=m.parse(path.read_text(),url)['courses']
    prose=[c for c in rows if c['source_id']=='mit-ai-hass-review-french-spotlights']
    assert {c['code']for c in prose}=={'21G.312','21G.346'}
    assert all(c['name'] is None and c['description'] for c in prose)
    assert all(any('Spring 2027' in n for n in c['notes'])for c in prose)
    assert any(c['source_id']!='mit-ai-hass-review-french-spotlights'for c in rows)
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    unknown=[c for c in p['courses']if c['id']in {'mit-ai-hass-language-placement-21g-342','mit-ai-hass-language-placement-21g-347','mit-ai-hass-music-21m-223j'}]
    assert len(unknown)==3
    assert all(c['category_review']['status']=='unclassified'and c['category']=='other'for c in unknown)
    assert all(c['name'] is None and c['description'] is None and c['credits'] is None for c in unknown)
    assert all(any('code-only observation' in n for n in c['notes'])for c in unknown)


def test_literature_term_upgrade_preserves_bundle_and_preparation_limits():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    first=by['mit-ai-hass-ancient-and-medieval-studies-21l-611']
    second=by['mit-ai-hass-ancient-and-medieval-studies-21l-612']
    assert first['credits']==second['credits']==6
    assert second['prerequisites']=='21L.611 or permission of instructor'
    assert any('petition after both' in n for n in first['notes'])
    writing=by['mit-ai-hass-african-and-african-diaspora-studies-21l-504j']
    assert writing['category']=='human_context'and writing['prerequisites']=='Permission of instructor'
    narrative=by['mit-ai-hass-computing-21l-489-j']
    assert narrative['prerequisites']=='none'
    assert any('helpful, not a prerequisite' in n for n in narrative['notes'])
    current=[c for c in p['courses']if c['code']=='21L.707'and c['name']and 'AI'in c['name']]
    assert all(not c.get('description')or 'Art of War and Peace'not in c['description']for c in current)
