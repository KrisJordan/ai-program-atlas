"""Disjoint MIT HASS contribution: source identities and withheld decisions matter."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'atlas/adapters/mit-ai-decision-making-bs'
SPEC = importlib.util.spec_from_file_location('mit_hass_review', ADAPTER / 'reviewed_hass_subjects.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)
MANIFEST = json.loads((ADAPTER / 'reviewed_hass_subjects.json').read_text())
SEED = json.loads((ROOT / 'data/programs/mit-ai-decision-making-bs.json').read_text())


def entry(code):
    return next(r for r in MANIFEST['courses'].values() if r['listed_code'] == code)


def test_scope_is_exact_and_unread_records_are_not_certified():
    hass = {c['id'] for c in SEED['courses'] if c['id'].startswith('mit-ai-hass-')}
    assert set(MANIFEST['courses']) == hass
    assert len(hass) == 845
    assert MANIFEST['full_audit_status'] == 'partial'
    for row in MANIFEST['courses'].values():
        if row['review_status'] == 'pending':
            assert row['observations'] == []
        for evidence in row['observations']:
            if evidence.get('evidence_basis') == 'official_title_only':
                assert evidence['description_digest'] is None
                assert evidence['description_summary'] is None
                assert evidence['prerequisites'] is None
                if evidence['credits'] is not None:
                    assert evidence['units_text']=='9 unit IAP version' and evidence['credits']==9
                assert 'title' in evidence['rationale']
            else:
                assert evidence['description_digest']
                assert evidence['description_summary']
            assert evidence['source_id'] in MANIFEST['source_specs']


def test_probability_literature_is_not_math_and_music_is_not_automatic_ai():
    assert entry('21L.017')['observations'][0]['category'] == 'human_context'
    music = entry('21M.080')['observations'][0]
    assert music['category'] == 'applications'
    assert music['credits'] == 12
    assert music['unit_rule_source_url'] == 'https://catalog.mit.edu/subjects/'


def test_half_term_subjects_preserve_hass_bundle_and_permission():
    greek = entry('21L.608')['observations'][0]
    assert greek['credits'] == 6
    assert greek['prerequisites'] == '21L.607 or permission of instructor'
    assert any('oneHASS-H' in text for text in greek['restrictions'])
    assert entry('21L.614')['observations'][0]['credits'] == 6


def test_graduate_prerequisite_not_transferred_to_undergraduate():
    observation = entry('4.603')['observations'][0]
    assert observation['prerequisites'] is None
    assert observation['observed_prerequisite_field'] == '4.604: permission of instructor'
    assert any('graduate4.604 only' in text for text in observation['restrictions'])


def test_conflicting_and_changed_identity_evidence_is_withheld():
    for row in MANIFEST['courses'].values():
        if row['review_status'] in {'identity_review_needed', 'source_conflict'}:
            assert not any(o['approved_for_integration'] for o in row['observations'])
    writing = [r for r in MANIFEST['courses'].values() if any(o['observed_code'] == 'WGS.231' for o in r['observations'])]
    assert writing and all(r['review_status'] == 'source_conflict' for r in writing)


def test_review_reuse_is_guarded_by_source_context_and_entire_observation():
    obs = dict(code='21L.017', name='The Art of the Probable', description='Literary history.', term='Fall 2026', prerequisites='none')
    course = dict(id='test', code='21L.017', name='The Art of the Probable', source_id='listed-source')
    evidence = dict(approved_for_integration=True, source_url='https://lit.mit.edu/example', observation_digest=review.observation_digest(obs))
    manifest = {'courses': {'test': dict(listed_code=course['code'], listed_name=course['name'], listed_source_id=course['source_id'], review_status='reviewed', observations=[evidence])}}
    assert review.matched_review(course, obs, evidence['source_url'], manifest) == evidence
    for field in ['description', 'name', 'term', 'prerequisites']:
        changed = copy.deepcopy(obs); changed[field] = 'changed'
        assert review.matched_review(course, changed, evidence['source_url'], manifest) is None
    assert review.matched_review(course, obs, 'https://example.org/other', manifest) is None
    assert review.matched_review({**course, 'source_id': 'another-version'}, obs, evidence['source_url'], manifest) is None


def test_triplets_need_actual_notation_rule_and_unknown_remains_null():
    html = '<p>The total unit credit for a subject is obtained by adding together all the units shown.</p>'
    assert review.unit_total('3-0-3; second half of term', html) == 6
    assert review.unit_total('0-0-0', html) == 0
    assert review.unit_total('Units arranged', html) is None
    with pytest.raises(ValueError, match='convention'):
        review.unit_total('3-0-9', html.replace('adding', 'averaging'))


@pytest.mark.parametrize('key,parser', [('architecture',review.observe_architecture), ('literature',review.observe_literature), ('music-schedule',review.observe_performing_arts), ('theater-schedule',review.observe_performing_arts)])
def test_actual_source_cache_reviews_reproduce_when_cache_available(key, parser):
    path = Path('/tmp/mit-hass-subjects') / (key + '.html')
    if not path.exists():
        pytest.skip('Optional ignored official source capture')
    observations = parser(path.read_text())
    source_specs = {s['url'] for s in MANIFEST['source_specs'].values() if s.get('parser') in {'architecture','literature','performing_arts'}}
    matched = []
    for course in SEED['courses']:
        for obs in observations:
            for url in source_specs:
                hit = review.matched_review(course, obs, url, MANIFEST)
                if hit:matched.append(hit)
    assert matched
    assert all(hit['approved_for_integration'] for hit in matched)


def test_cmsw_visible_term_parser_keeps_alias_and_meeting_distinct():
    html = '''<section id="mit-subject-list"><h2>Fall 2026</h2>
    <li class="academic_term_tier__subject">
    <a class="academic_term_tier__subject-course-number">CMS.611[J]</a>
    <span class="academic_term_tier__subject-course-title">Creating Video Games</span>
    <div class="academic-term-tier__subject-description"><ul>
    <li><strong>Same subject as:</strong> 6.4570[J]</li>
    <li><strong>Meets with:</strong> CMS.900</li><li><strong>Units:</strong> 3-3-6</li>
    </ul><p>Teams combine game programming and art production.</p></div></li></section>'''
    row = review.observe_cmsw(html)[0]
    assert row['term'] == 'Fall 2026'
    assert row['same_subject_as'] == '6.4570[J]'
    assert row['meets_with'] == 'CMS.900'
    assert row['prerequisites'] is None
    assert row['description'] == 'Teams combine game programming and art production.'
    with pytest.raises(ValueError, match='term label'):
        review.observe_cmsw(html.replace('Fall 2026', 'Unknown'))
    with pytest.raises(ValueError, match='paired'):
        review.observe_cmsw(html.replace('academic-term-tier__subject-description', 'changed'))


def test_cmsw_manual_subject_and_identity_judgments():
    observations = [o for r in MANIFEST['courses'].values() for o in r['observations']
                    if o['source_id'] == 'mit-ai-hass-review-cmsw-fall2026']
    by_code = {o['observed_code']: o for o in observations}
    assert by_code['CMS.401']['category'] == 'human_context'
    assert by_code['CMS.611[J]']['status'] == 'mixed'
    assert by_code['CMS.611[J]']['candidate_categories'] == ['foundations', 'applications']
    assert by_code['CMS.591[J]']['prerequisites'] == 'Permission of instructor. Coreq: CMS.586'
    assert by_code['CMS.357[J]']['prerequisites'] is None
    assert by_code['CMS.357[J]']['credits'] == 12
    malformed = [r for r in MANIFEST['courses'].values() if '.WGS.' in r['listed_code']]
    assert malformed and all(r['review_status'] == 'identity_review_needed' for r in malformed)


def test_cmsw_actual_visible_capture_replays_approved_observations():
    path = Path('/tmp/mit-hass-subjects/cmsw-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public visible-DOM capture')
    rows = review.observe_cmsw(path.read_text())
    hashes = {review.observation_digest(row) for row in rows}
    observations = [o for r in MANIFEST['courses'].values() for o in r['observations']
                    if o['source_id'] == 'mit-ai-hass-review-cmsw-fall2026']
    assert len(observations) == 33
    assert all(o['observation_digest'] in hashes for o in observations)


def test_cmsw_archived_term_credits_and_missing_description_are_not_imputed():
    rows=[r for r in MANIFEST['courses'].values() if any(o['source_id']=='mit-ai-hass-review-cmsw-spring2026' for o in r['observations'])]
    obs={o['observed_code']:o for r in rows for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-spring2026'}
    assert obs['CMS.305[J]']['credits']==9
    assert obs['CMS.C35[J]']['credits']==15
    assert obs['CMS.C35[J]']['status']=='mixed'
    assert obs['CMS.702']['category']=='human_context'
    assert obs['CMS.593[J]']['prerequisites']=='CMS.592'
    assert all(o['catalog_year']=='Spring 2026' for o in obs.values())
    hamilton=[r for r in MANIFEST['courses'].values() if r['listed_code'].startswith('CMS.427')]
    assert hamilton and all(r['review_status']=='pending' and not r['observations'] for r in hamilton)
    assert all(any('no description' in x for x in r['missingness']) for r in hamilton)
    changed=next(r for r in rows if r['listed_name']=='Intersectionality, Neurodiversity, and Disability')
    assert changed['review_status']=='identity_review_needed'


def test_cmsw_spring_visible_capture_replays_without_assuming_latest_term():
    path=Path('/tmp/mit-hass-subjects/cmsw-spring2026-visible.html')
    if not path.exists():
        pytest.skip('Optional ignored public archived-term capture')
    source=review.observe_cmsw(path.read_text())
    assert {o['term'] for o in source}=={'Spring 2026'}
    assert next(o for o in source if o['code']=='CMS.427[J]')['description'] is None
    hashes={review.observation_digest(o) for o in source}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-spring2026']
    assert len(saved)==31 and all(o['observation_digest'] in hashes for o in saved)


def test_cmsw_2025_interactive_writing_does_not_force_a_programming_path():
    records=[r for r in MANIFEST['courses'].values() if any(o['source_id']=='mit-ai-hass-review-cmsw-fall2025' for o in r['observations'])]
    obs={o['observed_code']:o for r in records for o in r['observations'] if o['source_id']=='mit-ai-hass-review-cmsw-fall2025'}
    assert obs['CMS.618[J]']['category']=='human_context'
    assert any('OR structuring text' in x for x in obs['CMS.618[J]']['restrictions'])
    assert obs['CMS.560']['category']=='human_context'
    assert obs['CMS.560']['prerequisites'] is None
    changed=[r for r in MANIFEST['courses'].values() if r['listed_code']=='CMS.400']
    assert changed and all(r['review_status']=='identity_review_needed' for r in changed)


@pytest.mark.parametrize('term',['fall2025','spring2025'])
def test_cmsw_2025_visible_capture_replays_exact_dated_observations(term):
    path=Path('/tmp/mit-hass-subjects')/f'cmsw-{term}-visible.html'
    if not path.exists():
        pytest.skip('Optional ignored public archived-term capture')
    hashes={review.observation_digest(o) for o in review.observe_cmsw(path.read_text())}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-cmsw-{term}']
    assert saved and all(o['observation_digest'] in hashes for o in saved)


def test_official_language_title_reviews_do_not_invent_description_or_identity():
    assert MANIFEST['evidence_counts']['description_reviewed_records']==139
    assert MANIFEST['evidence_counts']['title_only_reviewed_records']>=45
    for code in ['21G.715','21G.111','21H.186']:
        o=entry(code)['observations'][-1]
        assert o['evidence_basis']=='official_title_only'
        assert o['status']=='unclassified' and o['category']=='other'
        assert o['description_summary'] is o['description_digest'] is o['credits'] is None
    assert entry('21G.901')['observations'][-1]['category']=='human_context'
    for code in ['21G.094','21G.612','21G.613','21G.614']:
        assert entry(code)['review_status']=='identity_review_needed'
        assert not entry(code)['observations'][-1]['approved_for_integration']


@pytest.mark.parametrize('language',['french','spanish','chinese','japanese','korean','portuguese','russian'])
def test_actual_language_schedule_title_observations_replay(language):
    path=Path('/tmp')/f'atlas-mit-hass-rest-{language}.html'
    if not path.exists():
        pytest.skip('Optional ignored official language page capture')
    observations=review.observe_language_titles(path.read_text())
    hashes={review.observation_digest(o) for o in observations}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']==f'mit-ai-hass-review-language-titles-{language}']
    assert saved and all(o['observation_digest'] in hashes for o in saved)
    assert all(o['description'] is o['prerequisites'] is o['units'] is None for o in observations)


def test_language_observer_uses_printed_code_not_a_conflicting_link():
    html='''<main><h1>French &amp; Francophone Studies</h1><div class="value">Fall 2026</div>
    <div><div class="credit-section-wrap"><div class="value">21G</div>
    <div class="semester-section-titile"><div class="value">333</div></div>
    <a href="https://example.edu/#21G.304">catalog link</a></div>
    <div><div class="value">French IV</div></div></div></main>'''
    o=review.observe_language_titles(html)[0]
    assert o['code']=='21G.333' and o['name']=='French IV'
    assert o['linked_urls']==['https://example.edu/#21G.304']
    assert o['description'] is None
    with pytest.raises(ValueError,match='identity/term'):
        review.observe_language_titles(html.replace('Fall 2026','Term unknown'))


def test_political_pool_membership_does_not_classify_computing_or_methods():
    rows=[r for r in MANIFEST['courses'].values() if r['listed_source_id']=='mit-ai-decision-making-bs-hass-political-subfields']
    bycode={r['listed_code']:r for r in rows}
    for code in ['17.835','17.C08J','17.811','17.447J','17.803']:
        o=bycode[code]['observations'][-1]
        assert o['category']=='other' and o['status']=='unclassified'
        assert o['evidence_basis']=='official_title_only'
        assert o['description_digest'] is None
    assert bycode['17.055']['observations'][-1]['category']=='human_context'
    assert bycode['17.567']['observations'][-1]['credits']==9
    assert 'Washington Summer Internship' in bycode['17.307']['observations'][-1]['restrictions'][0]
    assert 'current IAP offering' in bycode['17.567']['observations'][-1]['restrictions'][0]


def test_actual_political_pdf_title_review_replays_with_source_guards():
    path=Path('/tmp/atlas-mit-political-subfields.txt')
    if not path.exists():
        pytest.skip('Optional ignored official PDF extraction')
    text=path.read_text();rows=review.observe_political_pdf_titles(text)
    hashes={review.observation_digest(o) for o in rows}
    saved=[o for r in MANIFEST['courses'].values() for o in r['observations'] if o['source_id']=='mit-ai-hass-review-political-pdf-titles']
    assert len(rows)==66 and len(saved)==65
    assert all(o['observation_digest'] in hashes for o in saved)
    with pytest.raises(ValueError,match='Unrecognized PDF line'):
        review.observe_political_pdf_titles(text.replace('Models and Methods','Changed heading'))
