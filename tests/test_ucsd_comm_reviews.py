import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_comm_reviews as review


def fixture(monkeypatch, code='COMM 102D', body='Supervised community education. Prerequisites: none.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Communication</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_observed_units_exact_none_and_no_manual_certifications(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch))
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert out['id'] == 'university-of-california-san-diego-artificial-intelligence-bs-degree'
    course = out['courses'][0]
    assert course['credits'] == 6 and course['credit_unit'] == 'quarter_hours'
    assert course['prerequisites'] == 'none.'
    assert course['category'] == 'applications'
    assert 'category_review' not in course


def test_no_prerequisite_statement_remains_unknown(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch, 'COMM 10', 'Communication history and theory.'))
    assert out['courses'][0]['prerequisites'] is None


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Supervised community', 'Independent commercial'), 'source changed'),
    (lambda s: s.replace('Prerequisites: none.', 'Prerequisites: instructor approval.'), 'source changed'),
    (lambda s: s.replace('(6)', '(4)'), 'source changed'),
    (lambda s: s + '<p>Additional registration restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Communication</h1>', '<h1>Another subject</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_all_material_source_changes_fail_closed(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_complete_block_includes_unwrapped_text_and_second_paragraph(monkeypatch):
    html = fixture(monkeypatch, body='Fieldwork. Extra restriction. Prerequisites: approval.')
    html = html.replace('Fieldwork. Extra restriction. Prerequisites: approval.',
                        'Fieldwork.</p>Extra restriction.<p>Prerequisites: approval.')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Extra restriction.', ''))


def test_missing_exact_suffix_and_title_holds(monkeypatch):
    original = review.SPEC
    entry = next(e for e in original['entries'] if e['code'] == 'COMM 140GS')
    monkeypatch.setattr(review, 'SPEC', {**original, 'entries': [entry]})
    html = '<h1>Communication</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    html += '<p class="course-name">COMM 140. Cinema in Latin America (4)</p>'
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='COMM 140GS', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">COMM 140GS. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    out = review.parse_observations(fixture(monkeypatch, 'COMM 102C'))
    assert out['courses'] == []
    assert out['source_dispositions'][0]['status'] == 'source_title_conflict'


def test_manual_content_decisions_and_no_assumed_technical_training():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 45 and sum(e['approved_for_integration'] for e in by.values()) == 39
    assert {c for c, e in by.items() if e['heading'] is None} == {'COMM 140GS', 'COMM 114M', 'COMM 106E', 'COMM 117GS'}
    assert {c for c, e in by.items() if e['disposition'] == 'source_title_conflict'} == {'COMM 102C', 'COMM 120P'}
    assert {c for c, e in by.items() if e['approved_for_integration'] and e['category'] == 'applications'} == {'COMM 101E', 'COMM 102D', 'COMM 102M', 'COMM 102P'}
    assert by['COMM 124A']['category_review']['status'] == 'mixed'
    assert set(by['COMM 124A']['category_review']['candidate_categories']) == {'human_context', 'applications'}
    for code in ['COMM 146', 'COMM 190', 'COMM 194']:
        assert by[code]['category_review']['status'] == 'unclassified'
    for code in ['COMM 114D', 'COMM 114I', 'COMM 114J', 'COMM 30', 'COMM 40', 'COMM 50']:
        assert by[code]['category'] == 'human_context'


def test_practice_scope_credit_exclusions_and_companion_internship():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert by['COMM 194']['credits'] == 4
    assert any('separate six-unit' in n for n in by['COMM 194']['notes'])
    assert any('POLI 194' in n for n in by['COMM 194']['notes'])
    assert any('thirty' in n for n in by['COMM 190']['notes'])
    assert any('off-campus' in n for n in by['COMM 135']['notes'])
    assert any('three hours' in n.lower() for n in by['COMM 120P']['notes'])
    assert any('Summer 2015' in n for n in by['COMM 102C']['notes'])
    assert any('COMM 100CR' in n for n in by['COMM 100C']['notes'])


def test_actual_cached_chapter_replay():
    source = review.SPEC['sources']['COMM']
    path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    by = {c['code']: c for c in out['courses']}
    assert len(by) == 39 and len(out['source_dispositions']) == 6
    assert sum(c['credits'] == 6 for c in by.values()) == 3
    assert by['COMM 102D']['prerequisites'] == 'none.'
    assert by['COMM 102M']['prerequisites'] == 'COMM 10 and COMM 101 or VIS 70N.'
    assert by['COMM 194']['prerequisites'] == 'participation in UCDC program.'
    assert by['COMM 111B']['prerequisites'] is None
