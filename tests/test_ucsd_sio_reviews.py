import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_sio_reviews as review


def fixture(monkeypatch, code='SIO 50', body='Geology with laboratory and fieldwork. Prerequisites: none.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Scripps Institution of Oceanography</h1>'
            '<p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_metadata_only_exact_credits_and_explicit_no_prerequisites(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch))
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    course = out['courses'][0]
    assert course['credits'] == 6 and course['credit_unit'] == 'quarter_hours'
    assert course['prerequisites'] == 'none.'
    assert course['category'] == 'applications'
    assert 'category_review' not in course


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Geology with', 'Public policy with'), 'source changed'),
    (lambda s: s.replace('Prerequisites: none.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(6)', '(4)'), 'source changed'),
    (lambda s: s + '<p>New eligibility restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Scripps Institution of Oceanography</h1>', '<h1>Other chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_complete_source_changes_require_new_review(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_nested_unwrapped_and_unclassed_block_text_is_guarded(monkeypatch):
    html = fixture(monkeypatch, body='Fieldwork. Conditions apply. Prerequisites: approval.')
    html = html.replace('Fieldwork. Conditions apply. Prerequisites: approval.',
                        '<strong>Fieldwork.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_exact_identifier_and_title_hold(monkeypatch):
    original = review.SPEC
    entry = next(e for e in original['entries'] if e['code'] == 'SIO 104')
    monkeypatch.setattr(review, 'SPEC', {**original, 'entries': [entry]})
    html = '<h1>Scripps Institution of Oceanography</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='SIO 104', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">SIO 104. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    out = review.parse_observations(fixture(monkeypatch, 'SIO 105'))
    assert out['courses'] == []
    assert out['source_dispositions'][0]['status'] == 'source_title_conflict'


def test_actual_content_boundaries_and_held_candidate_review():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 41 and sum(e['approved_for_integration'] for e in by.values()) == 35
    assert {c for c, e in by.items() if e['heading'] is None} == {'SIO 104', 'SIO 140', 'SIO 141', 'SIO 142GS'}
    assert {c for c, e in by.items() if e['disposition'] == 'source_title_conflict'} == {'SIO 105', 'SIO 113'}
    for code in ['SIO 25', 'SIO 114', 'SIO 109', 'SIO 109R']:
        assert by[code]['category_review']['status'] == 'mixed'
        assert set(by[code]['category_review']['candidate_categories']) == {'human_context', 'applications'}
    for code in ['SIO 101', 'SIO 110', 'SIO 116', 'SIO 116GS', 'SIO 147', 'SIO 166', 'SIO 167']:
        assert by[code]['category'] == 'applications'
    for code in ['SIO 194', 'SIO 196']:
        assert by[code]['category_review']['status'] == 'unclassified'
    assert by['SIO 113']['category'] == 'foundations' and not by['SIO 113']['approved_for_integration']
    assert any('not transferred' in n for n in by['SIO 113']['notes'])


def test_internship_honors_preparation_and_program_scopes():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert by['SIO 194']['credits'] == 4
    assert any('six-to-eight-unit' in n for n in by['SIO 194']['notes'])
    assert 'department approval' in by['SIO 194']['observed_prerequisites']
    assert all(x in by['SIO 196']['observed_prerequisites'] for x in ['ninety', 'twelve', '3.3', '3.5', 'Department stamp'])
    assert 'SIO 50' not in by['SIO 167']['observed_prerequisites']
    assert any('Recommended preparation' in n for n in by['SIO 167']['notes'])
    assert 'Global Seminars' in by['SIO 116GS']['observed_prerequisites']
    assert 'Global Seminars' not in by['SIO 116']['observed_prerequisites']
    assert by['SIO 109']['observed_prerequisites'] is None
    assert by['SIO 109R']['observed_prerequisites'] is None


def test_cached_full_chapter_replay():
    source = review.SPEC['sources']['SIO']
    path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    assert len(out['courses']) == 35 and len(out['source_dispositions']) == 6
    assert sum(c['credits'] == 6 for c in out['courses']) == 3
    assert sum(c['credits'] == 4 for c in out['courses']) == 32
    assert sum(c['prerequisites'] is None for c in out['courses']) == 2
    by = {c['code']: c for c in out['courses']}
    assert by['SIO 102']['prerequisites'] == 'SIO 50 and CHEM 6A-B-C or CHEM 6AH-6BH-6CH, or consent of instructor.'
    assert by['SIO 3']['prerequisites'] == 'none.'
