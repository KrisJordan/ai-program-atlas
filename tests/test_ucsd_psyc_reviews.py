import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_psyc_reviews as review


def fixture(monkeypatch, code='PSYC 111B', body='Applied research methods. Prerequisites: previous course and approval.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Psychology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_metadata_only_six_units_and_exact_suffix(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 6 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'previous course and approval.'
    assert c['category'] == 'applications' and 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Applied research', 'Unrelated theoretical'), 'source changed'),
    (lambda s: s.replace(' and approval', ''), 'source changed'),
    (lambda s: s.replace('(6)', '(4)'), 'source changed'),
    (lambda s: s + '<p>New major exclusion.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Psychology</h1>', '<h1>Other chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_changed_complete_source_fails_closed(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_nested_and_unwrapped_conditions_guarded(monkeypatch):
    html = fixture(monkeypatch, body='Research. Majors only. Prerequisites: approval.')
    html = html.replace('Research. Majors only. Prerequisites: approval.',
                        '<strong>Research.</strong></p>Majors only.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Majors only.', ''))


def test_missing_heading_and_substantive_title_hold(monkeypatch):
    original = review.SPEC
    entry = next(e for e in original['entries'] if e['code'] == 'PSYC 139')
    monkeypatch.setattr(review, 'SPEC', {**original, 'entries': [entry]})
    html = '<h1>Psychology</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='PSYC 139', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">PSYC 139. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    out = review.parse_observations(fixture(monkeypatch, 'PSYC 162'))
    assert out['courses'] == [] and out['source_dispositions'][0]['status'] == 'source_title_conflict'


def test_content_boundaries_and_old_identity_not_certified():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 16 and sum(e['approved_for_integration'] for e in by.values()) == 14
    assert {c for c, e in by.items() if e['category'] == 'applications'} == {'PSYC 116C', 'PSYC 117', 'PSYC 2', 'PSYC 141', 'PSYC 168', 'PSYC 111B', 'PSYC 115B'}
    for code in ['PSYC 127', 'PSYC 131', 'PSYC 42', 'PSYC 185', 'PSYC 164']:
        assert by[code]['category'] == 'human_context'
    for code in ['PSYC 193L', 'PSYC 194A']:
        assert by[code]['category_review']['status'] == 'unclassified'
    assert not by['PSYC 162']['approved_for_integration']
    assert any('must not certify' in n for n in by['PSYC 162']['notes'])


def test_exact_boolean_major_and_grade_scope():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert by['PSYC 117']['observed_prerequisites'] == 'upper-division standing, PSYC 60 or COGS 14B and PSYC 70 or COGS 14A. Instructor approval.'
    assert by['PSYC 193L']['observed_prerequisites'] == 'upper-division standing, department approval, and PSYC 60 or COGS 14B or MATH 11 and PSYC 70 or COGS 14A.'
    assert any('PC25' in n and 'PC35' in n for n in by['PSYC 127']['notes'])
    assert any('CG32' in n and 'PC25' not in n and 'PC35' not in n for n in by['PSYC 117']['notes'])
    assert any('for the Psychology Honors Program' in n for n in by['PSYC 111B']['notes'])
    assert any('recommended preparation' in n for n in by['PSYC 162']['notes'])
    assert by['PSYC 2']['observed_prerequisites'] is None
    assert by['PSYC 42']['observed_prerequisites'] is None


def test_actual_cached_replay():
    source = review.SPEC['sources']['PSYC']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    assert len(out['courses']) == 14 and len(out['source_dispositions']) == 2
    assert sum(c['credits'] == 6 for c in out['courses']) == 1
    assert sum(c['credits'] == 4 for c in out['courses']) == 13
    assert sum(c['prerequisites'] is None for c in out['courses']) == 2
