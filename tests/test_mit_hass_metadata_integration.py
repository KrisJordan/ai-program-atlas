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
    for code in ['17.811', '17.447J']:
        assert by[code]['category'] == 'other'
        assert by[code]['category_review']['status'] == 'unclassified'
        assert by[code]['description'] is None
    methods=by['17.835']
    assert methods['category_review']['status']=='mixed'
    assert set(methods['category_review']['candidate_categories'])=={'mathematics','ai_ml'}
    assert '6.100A' in methods['prerequisites'] and methods['credits']is None
    assert methods['syllabus']=='https://web.mit.edu/insong/www/pdf/syl-poldata.pdf'
    causal=by['17.C08J']
    assert causal['category']=='mathematics' and causal['description']
    assert 'mit-ai-hass-review-common-c08' in causal['category_review']['source_ids']
    assert 'or permission of instructor' in causal['prerequisites']
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
    assert by['mit-ai-hass-economics-14-15-j']['category_review']['status']=='reviewed'
    assert by['mit-ai-hass-economics-14-15-j']['category']=='mathematics'
    assert 'mit-ai-hass-review-ocw-14-15-networks-spring-2022' in by['mit-ai-hass-economics-14-15-j']['category_review']['source_ids']
    assert by['mit-ai-hass-economics-14-16']['description']
    assert by['mit-ai-hass-economics-14-16']['credits'] is None
    path=Path('/tmp/atlas-mit-hass-economics.html')
    if not path.exists():pytest.skip('Optional public source capture absent')
    fields=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.hass_departments')
    adapter=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.adapter')
    url=m.SPECS['mit-ai-hass-review-economics-titles']['url']
    actual=adapter.SOURCE_PARSERS[url](path.read_text())
    source_rows={c['id']:c for c in actual['courses']}
    assert source_rows['mit-ai-hass-economics-14-16']['description'] is None
    assert source_rows['mit-ai-hass-economics-14-15-j']['category']=='other'
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


def test_urban_historical_units_do_not_cross_course_title_versions():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    later=by['mit-ai-hass-urban-11-013-j']
    earlier=by['mit-ai-hass-american-studies-11-013j']
    assert later['name']=='American Urban History' and later['credits']==12
    assert earlier['name']=='American Urban History I' and earlier['credits'] is None
    assert 'spring-2025' in later['syllabus'] and 'spring-2010' in earlier['syllabus']
    for held in ['mit-ai-hass-urban-11-041','mit-ai-hass-urban-11-148','mit-ai-hass-urban-11-015-j']:
        assert by[held]['description'] is None
    # The separate current D-Lab page now explicitly prints 11.025; the old
    # EC.701-only OCW source still does not establish that correspondence.
    dlab=by['mit-ai-hass-urban-11-025-j']
    assert 'mit-ai-hass-review-dlab-development' in dlab['category_review']['source_ids']
    assert not any('ec-701j' in sid for sid in dlab['category_review']['source_ids'])
    law=by['mit-ai-hass-african-and-african-diaspora-studies-11-166']
    assert 'permission' in law['prerequisites'].lower()


def test_sts_exact_composites_and_homepage_resource_limits():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    nuclear=by['mit-ai-hass-ethics-sts-084j-22-04j']
    ethics=by['mit-ai-hass-ethics-sts-085j-6-4590j']
    assert nuclear['category_review']['status']=='mixed'
    assert set(nuclear['category_review']['candidate_categories'])=={'applications','human_context'}
    assert ethics['description'] and ethics['public_site'].endswith('/6-4590-foundations-of-information-policy-fall-2024/')
    assert ethics['syllabus'] is None
    assert not by['mit-ai-hass-sts-tier-2-sts-085j']['description']
    assert by['mit-ai-hass-sts-tier-2-sts-081j']['category']=='human_context'


def test_historical_language_registration_is_not_a_current_general_prerequisite():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    regular=by['mit-ai-hass-asian-and-asian-diaspora-studies-21g-101']
    streamlined=by['mit-ai-hass-asian-and-asian-diaspora-studies-21g-107']
    calligraphy=by['mit-ai-hass-asian-and-asian-diaspora-studies-21g-111']
    assert 'no prior background' in regular['prerequisites']
    assert any('capped at16' in n and 'auditors' in n for n in regular['notes'])
    assert any('21G.171 requires concurrent21G.076' in n and 'not silently applied' in n for n in regular['notes'])
    assert streamlined['prerequisites'] is None
    assert any('audience/placement context' in n for n in streamlined['notes'])
    assert calligraphy['category']=='other' and calligraphy['category_review']['status']=='mixed'
    assert calligraphy['syllabus'].endswith('/pages/syllabus/')


def test_browser_selected_semester_cannot_be_replayed_by_default_html():
    sid='mit-ai-hass-review-music-visible-spring-2026'
    captured=Path(m.INTEGRATED['cache_paths'][sid])
    default=Path('/tmp/mit-hass-subjects/music-schedule.html')
    if not captured.exists()or not default.exists():pytest.skip('Optional ignored browser and HTTP captures absent')
    url=m.SPECS[sid]['url']
    rows=m.parse(captured.read_text(),url)['courses']
    assert len(rows)==4 and all(c['source_id']==sid for c in rows)
    assert all(c['public_site']is None and c['syllabus']is None for c in rows)
    assert not any(c['source_id']==sid for c in m.parse(default.read_text(),url)['courses'])
    changed=json.loads(captured.read_text());changed['semester']='Spring 2025'
    assert m.parse(json.dumps(changed),url)['courses']==[]


def test_visible_theater_exact_code_and_formal_none_are_preserved():
    sid='mit-ai-hass-review-theater-visible-spring-2025'
    path=Path(m.INTEGRATED['cache_paths'][sid])
    if not path.exists():pytest.skip('Optional ignored visible theater capture absent')
    rows=m.parse(path.read_text(),m.SPECS[sid]['url'])['courses']
    assert len(rows)==1 and rows[0]['code']=='21T.248'
    assert rows[0]['credits']==12 and rows[0]['prerequisites']=='None'
    assert rows[0]['public_site']is None and rows[0]['syllabus']is None


def test_archaeology_and_steam_descriptions_stay_with_exact_source_versions():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    approved=by['mit-ai-hass-archaeology-and-archaeological-science-3-987']
    held=by['mit-ai-hass-ancient-and-medieval-studies-3-987']
    assert approved['description'] and approved['category_review']['status']=='mixed'
    assert held['description'] is None
    assert approved['credits'] is None and approved['prerequisites'] is None
    assert approved['public_site'].endswith('/3-987-human-origins-and-evolution-spring-2006/')
    assert approved['syllabus'] is None  # The metadata observer reads this homepage only.
    target=by['mit-ai-hass-cmsw-education-cms-s61-5e6c537a']
    assert target['category']=='applications' and 'educational' in target['description'].lower()
    assert 'spring-2024' in target['syllabus']
    for cid in ['mit-ai-hass-cmsw-education-cms-s61-23d0f187',
                'mit-ai-hass-cmsw-education-cms-s61-a0a026fc',
                'mit-ai-hass-cmsw-pool-cms-cms-s61']:
        assert by[cid]['description'] != target['description']


def test_concourse_corequisite_preference_and_unknown_fields_stay_distinct():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    limited=by['mit-ai-hass-ethics-cc-110']
    preference=by['mit-ai-hass-ethics-cc-117j-17-05j']
    unprinted=by['mit-ai-hass-ethics-cc-111j-17-04j']
    assert limited['prerequisites']=='None. Coreq: CC.010 or CC.A10'
    assert limited['credits']==12
    assert any('Limited to students in Concourse' in n for n in limited['notes'])
    assert preference['prerequisites']=='None' and preference['credits']==12
    assert any('not an exclusive enrollment restriction' in n for n in preference['notes'])
    assert unprinted['prerequisites'] is None and unprinted['credits'] is None
    assert any('Spring2013' in n and 'not imported' in n for n in unprinted['notes'])
    for c in [limited,preference,unprinted]:
        assert c['public_site'] is None and c['syllabus'] is None


def test_wgs_dated_topic_does_not_resolve_other_term_conflict_or_create_resources():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    digital=by['mit-ai-hass-computing-wgs-243']
    assert digital['category_review']['status']=='mixed'
    assert set(digital['category_review']['candidate_categories'])=={'foundations','human_context'}
    assert digital['credits']==12 and digital['prerequisites'] is None
    assert any('helpful but not required' in n for n in digital['notes'])
    assert any('Feminist Geographies' in n for n in digital['notes'])
    assert digital['public_site'] is None and digital['syllabus'] is None
    conflicts=[c for c in p['courses'] if c['code']=='21W.742J [WGS.231]']
    assert len(conflicts)==2 and all(c['description'] is None for c in conflicts)


def test_wgs_historical_year_change_withdraws_saved_review():
    sid='mit-ai-hass-review-wgs-archive-wgs243-sp26'
    path=Path(m.INTEGRATED['cache_paths'][sid])
    if not path.exists():pytest.skip('Optional ignored WGS capture absent')
    html=path.read_text();url=m.SPECS[sid]['url']
    rows=m.parse(html,url)['courses']
    assert len(rows)==1 and rows[0]['source_id']==sid
    assert m.parse(html.replace('2025-2026','2026-2027'),url)['courses']==[]


def test_dlab_current_page_does_not_make_historical_travel_a_current_requirement():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    c=next(c for c in p['courses'] if c['id']=='mit-ai-hass-urban-11-025-j')
    assert c['credits']==12 and c['prerequisites'].startswith('None.')
    assert 'first class session' in c['prerequisites']
    assert set(c['category_review']['candidate_categories'])=={'applications','human_context'}
    assert c['category']=='other'
    assert any('2022' in n and 'does not promise or require present travel' in n for n in c['notes'])
    assert c['public_site'] is None and c['syllabus'] is None


def test_dated_project_site_and_new_department_metadata_keep_resource_scopes():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    project=by['mit-ai-hass-urban-11-154']
    assert project['description'] and project['category_review']['status']=='unclassified'
    assert project['public_site']=='https://bigdatavis.mit.edu/' and project['syllabus']is None
    assert any('Fall2021' in note for note in project['notes'])
    assert project['credits']is None and project['prerequisites']is None
    communication=by['mit-ai-hass-sts-tier-2-sts-034']
    assert communication['credits']==12
    assert communication['category_review']['status']=='mixed'
    assert set(communication['category_review']['candidate_categories'])=={'applications','human_context'}
    assert 'fall-2011' in communication['syllabus']
    assert any('Spring 2025' in note for note in communication['notes'])
    specific=by['mit-ai-hass-computing-24-s00-9b7fdfac']
    assert specific['category_review']['status']=='mixed'
    assert set(specific['category_review']['candidate_categories'])=={'mathematics','ai_ml'}
    assert specific['prerequisites']is None and specific['public_site']is None


def test_dated_sts_admission_and_pe_points_do_not_become_degree_credit():
    p=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    by={c['id']:c for c in p['courses']}
    embodied=by['mit-ai-hass-sts-tier-1-sts-014']
    assert embodied['credits']==12 and embodied['prerequisites']=='None'
    assert any('PE&W' in n and 'separate' in n for n in embodied['notes'])
    assert set(embodied['category_review']['candidate_categories'])=={'applications','human_context'}
    exercise=by['mit-ai-hass-sts-tier-1-sts-041']
    assert exercise['credits']is None and exercise['prerequisites']is None
    self=by['mit-ai-hass-sts-tier-2-sts-044']
    assert self['credits']==9 and self['prerequisites']=='None'
    assert any('15' in n and 'first class' in n for n in self['notes'])
    assert any('graduate students do extra' in n for n in self['notes'])
    political=by['mit-ai-hass-political-subfields-17-831']
    assert set(political['category_review']['candidate_categories'])=={'mathematics','human_context'}
    assert political['credits']is None and political['prerequisites']is None
    assert political['public_site']is None and political['syllabus']is None
