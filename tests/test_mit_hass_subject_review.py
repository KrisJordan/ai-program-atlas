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
