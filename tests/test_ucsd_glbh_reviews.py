import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_glbh_reviews as review


def fixture(monkeypatch, code='GLBH 111', body='Clinic fieldwork. Recommended preparation: prior global-health coursework.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Global Health Program</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_metadata_only_missing_prerequisites_not_inferred_from_preparation(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['prerequisites'] is None
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['category'] == 'applications' and 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Clinic fieldwork', 'Historical policy analysis'), 'source changed'),
    (lambda s: s.replace('Recommended preparation', 'Prerequisites'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New enrollment restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Global Health Program</h1>', '<h1>Different chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_source_changes_fail_closed(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_complete_nested_and_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Fieldwork. Conditions apply. Prerequisites: approval.')
    html = html.replace('Fieldwork. Conditions apply. Prerequisites: approval.',
                        '<strong>Fieldwork.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_code_and_expanded_title_hold(monkeypatch):
    original = review.SPEC
    entry = next(e for e in original['entries'] if e['code'] == 'GLBH 131')
    monkeypatch.setattr(review, 'SPEC', {**original, 'entries': [entry]})
    html = '<h1>Global Health Program</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='GLBH 131', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">GLBH 131. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    out = review.parse_observations(fixture(monkeypatch, 'GLBH 107'))
    assert out['courses'] == [] and out['source_dispositions'][0]['status'] == 'source_title_conflict'


def test_content_boundaries_and_candidate_only_hold():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 26 and sum(e['approved_for_integration'] for e in by.values()) == 24
    assert {c for c, e in by.items() if e['category'] == 'applications'} == {'GLBH 111', 'GLBH 141'}
    assert {c for c, e in by.items() if e.get('category_review') and e['category_review']['status'] == 'mixed'} == {'GLBH 120', 'GLBH 121', 'GLBH 106', 'GLBH 146', 'GLBH 171R', 'GLBH 181'}
    for code in ['GLBH 130', 'GLBH 108S', 'GLBH 113', 'GLBH 139', 'GLBH 147', 'GLBH 148', 'GLBH 150']:
        assert by[code]['category'] == 'human_context'
    assert by['GLBH 150B']['category_review']['status'] == 'unclassified'
    assert not by['GLBH 107']['approved_for_integration']
    assert any('must not certify' in n for n in by['GLBH 107']['notes'])


def test_scope_of_preparation_fieldwork_and_coscheduling():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert by['GLBH 111']['observed_prerequisites'] is None
    assert any('US–Mexico border' in n for n in by['GLBH 111']['notes'])
    assert any('Application process' in n and 'does not waive' in n for n in by['GLBH 111']['notes'])
    assert any('recommended' in n and 'not stated as a mandatory' in n for n in by['GLBH 106']['notes'])
    assert any('graduate courses' in n for n in by['GLBH 139']['notes'])
    assert any('coscheduled' in n for n in by['GLBH 141']['notes'])
    assert any('no delivery format' in n for n in by['GLBH 171R']['notes'])
    assert by['GLBH 150B']['observed_prerequisites'] == 'GLBH 150A; department approval required.'
    assert by['GLBH 160']['observed_prerequisites'] == 'upper-division standing.'


def test_exact_cached_source_replay():
    source = review.SPEC['sources']['GLBH']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    assert len(out['courses']) == 24 and len(out['source_dispositions']) == 2
    assert all(c['credits'] == 4 for c in out['courses'])
    assert sum(c['prerequisites'] is None for c in out['courses']) == 22
