import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_anar_reviews as review


def fixture(monkeypatch, code='ANAR 117', body='Hands-on field methods. Prerequisites: upper-division standing or consent of instructor.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Anthropology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_metadata_only_exact_eight_units_and_prerequisites(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch))
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert out['id'] == review.SPEC['program_id']
    course = out['courses'][0]
    assert course['credits'] == 8 and course['credit_unit'] == 'quarter_hours'
    assert course['prerequisites'] == 'upper-division standing or consent of instructor.'
    assert course['category'] == 'applications'
    assert 'category_review' not in course


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Hands-on field', 'Historical interpretive'), 'source changed'),
    (lambda s: s.replace(' or consent of instructor', ''), 'source changed'),
    (lambda s: s.replace('(8)', '(4)'), 'source changed'),
    (lambda s: s + '<p>New eligibility restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Anthropology</h1>', '<h1>Different chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_changes_require_full_review(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_complete_block_includes_unwrapped_and_unclassed_text(monkeypatch):
    html = fixture(monkeypatch, body='Fieldwork. Conditions apply. Prerequisites: approval.')
    html = html.replace('Fieldwork. Conditions apply. Prerequisites: approval.',
                        'Fieldwork.</p>Conditions apply.<p>Prerequisites: approval.')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_suffix_is_not_inferred_from_unsuffixed_course(monkeypatch):
    entry = next(e for e in review.SPEC['entries'] if e['code'] == 'ANAR 135S')
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    html = ('<h1>Anthropology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            '<p class="course-name">ANAR 135. Ancient Mediterranean Civilization (8)</p>')
    out = review.parse_observations(html)
    assert out['courses'] == []
    assert out['source_dispositions'] == [dict(code='ANAR 135S', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">ANAR 135S. New course (4)</p>')


def test_science_methods_history_and_variable_topic_decisions():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 36 and sum(e['approved_for_integration'] for e in by.values()) == 28
    assert {c for c, e in by.items() if e['category'] == 'applications'} == {'ANAR 114', 'ANAR 115', 'ANAR 116', 'ANAR 117', 'ANAR 119S', 'ANAR 120', 'ANAR 146'}
    for code in ['ANAR 113', 'ANAR 118', 'ANAR 135', 'ANAR 143', 'ANAR 160', 'ANAR 165', 'ANAR 182']:
        assert by[code]['category'] == 'human_context'
    assert by['ANAR 155']['category_review']['status'] == 'mixed'
    assert by['ANAR 155S']['category'] == 'human_context'
    assert by['ANAR 100']['category_review']['status'] == 'unclassified'
    assert any('Latin American' in n and 'unresolved' in n for n in by['ANAR 100']['notes'])


def test_exact_credit_repeat_preparation_and_enrollment_scopes():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert {c for c, e in by.items() if e['credits'] == 8} == {'ANAR 117', 'ANAR 119S', 'ANAR 135'}
    assert 'ANTH 3' not in by['ANAR 182']['observed_prerequisites']
    assert any('recommended preparation' in n for n in by['ANAR 182']['notes'])
    assert 'Graduate students' in by['ANAR 160']['observed_prerequisites']
    assert by['ANAR 145S']['observed_prerequisites'] == 'consent of instructor only.'
    assert by['ANAR 155S']['observed_prerequisites'] != by['ANAR 155']['observed_prerequisites']
    assert any('combined maximum of twelve' in n for n in by['ANAR 155']['notes'])
    assert any('credit four times' in n for n in by['ANAR 100']['notes'])
    assert any('ANAR 146R' in n for n in by['ANAR 146']['notes'])
    assert any('summer study abroad' in n for n in by['ANAR 157S']['notes'])


def test_cached_chapter_hash_and_all_observations():
    source = review.SPEC['sources']['ANAR']
    path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    assert len(out['courses']) == 28 and len(out['source_dispositions']) == 8
    assert {d['code'] for d in out['source_dispositions']} == {'ANAR 103', 'ANAR 105', 'ANAR 125', 'ANAR 135S', 'ANAR 141', 'ANAR 142', 'ANAR 190', 'ANAR 191'}
    assert sum(c['credits'] == 4 for c in out['courses']) == 25
    assert all(c['prerequisites'] for c in out['courses'])
