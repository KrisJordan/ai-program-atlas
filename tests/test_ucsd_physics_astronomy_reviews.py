import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_physics_astronomy_reviews as review


def fixture(monkeypatch, code='PHYS 1A', body='Mechanics. Prerequisites: MATH 20A.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]
    subject = code.split()[0]
    html = (f'<h1>{spec["sources"][subject]["heading"]}</h1><h2>Courses</h2>'
            '<p class="course-disclaimer">General Catalog 2026–27</p>'
            '<p>Enrollment rules apply.</p><h2>Lower Division</h2><p>Intended audiences vary.</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['physics_preamble_sha256'] = review.physics_preamble_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only_source_routing_and_three_unit_lecture(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 3 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'MATH 20A.'
    assert c['source_id'].endswith('-phys-courses')
    assert 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Mechanics.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('MATH 20A.', 'MATH 20B.'), 'source changed'),
    (lambda s: s.replace('(3)', '(4)'), 'source changed'),
    (lambda s: s + '<p>New credit exclusion.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Physics</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_body_and_edition_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_chapter_wide_policy_changes_fail_closed(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='chapter-wide policies changed'):
        review.parse_observations(html.replace('Enrollment rules apply.', 'Enrollment rules waived.'))
    with pytest.raises(ValueError, match='chapter-wide policies changed'):
        review.parse_observations(html.replace('<p>Intended audiences vary.</p>', ''))


def test_complete_nested_and_unwrapped_course_text(monkeypatch):
    html = fixture(monkeypatch, body='Physics. Conditions apply. Prerequisites: approval.')
    html = html.replace('Physics. Conditions apply. Prerequisites: approval.',
                        '<strong>Physics.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_physics_code_and_astronomy_title_hold(monkeypatch):
    original = review.SPEC
    entry = next(e for e in original['entries'] if e['code'] == 'PHYS 13')
    html = fixture(monkeypatch)
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='PHYS 13', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">PHYS 13. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    out = review.parse_observations(fixture(monkeypatch, 'ASTR 150'))
    assert out['courses'] == [] and out['source_dispositions'][0]['status'] == 'source_title_conflict'


def test_content_boundaries_and_exact_units():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 26 and sum(e['approved_for_integration'] for e in by.values()) == 24
    assert by['ASTR 60']['category'] == 'human_context'
    assert by['ASTR 154']['category_review']['status'] == 'mixed'
    assert set(by['ASTR 154']['category_review']['candidate_categories']) == {'mathematics', 'ai_ml'}
    for code in ['ASTR 15', 'ASTR 4', 'PHYS 124', 'PHYS 133', 'PHYS 4E']:
        assert by[code]['category'] == 'applications'
    assert by['ASTR 154']['credits'] == 5
    assert not by['ASTR 150']['approved_for_integration']
    assert all(by[c]['credits'] == 3 for c in ['PHYS 1A', 'PHYS 1B', 'PHYS 1C'])


def test_recommended_corequisite_and_major_scopes():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert 'Corequisites: MATH 10B or 20B.' in by['PHYS 11']['observed_prerequisites']
    assert any('separate terms' in n for n in by['PHYS 1B']['notes'])
    assert any('strongly recommended' in n and 'not in' in n for n in by['PHYS 2C']['notes'])
    assert 'Recommended preparation: prior or concurrent enrollment in MATH 20E.' in by['PHYS 2D']['observed_prerequisites']
    assert any('PY26' in n and 'PY35' in n for n in by['PHYS 133']['notes'])
    assert any('formerly' in n.lower() and 'PHYS 120B' in n for n in by['PHYS 124']['notes'])
    assert any('not added as an AI-degree obligation' in n for n in by['PHYS 4E']['notes'])


@pytest.mark.parametrize('subject', ['PHYS', 'ASTR'])
def test_exact_cached_chapter_replay(subject):
    source = review.SPEC['sources'][subject]; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == (14 if subject == 'PHYS' else 10)
    assert len(out['source_dispositions']) == 1
    assert all(c['code'].startswith(subject + ' ') for c in out['courses'])
