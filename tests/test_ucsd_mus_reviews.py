import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_mus_reviews as review


def fixture(monkeypatch, code='MUS 199', body='Individual research. Prerequisites: instructor consent.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Music</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_metadata_only_variable_units_and_unknown_content(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch))
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    c = out['courses'][0]
    assert c['credits'] is None and c['credit_unit'] == 'quarter_hours'
    assert c['category'] == 'other'
    assert c['prerequisites'] == 'instructor consent.'
    assert 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Individual research', 'Practical orchestration'), 'source changed'),
    (lambda s: s.replace('instructor consent', 'department approval'), 'source changed'),
    (lambda s: s.replace('(1–4)', '(4)'), 'source changed'),
    (lambda s: s + '<p>Additional enrollment condition.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Music</h1>', '<h1>Other chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_complete_material_changes_require_review(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_complete_body_includes_nested_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Research. Conditions apply. Prerequisites: consent.')
    html = html.replace('Research. Conditions apply. Prerequisites: consent.',
                        '<strong>Research.</strong></p>Conditions apply.<div><p>Prerequisites: consent.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'consent.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_r_code_not_substituted_from_unsuffixed(monkeypatch):
    entry = next(e for e in review.SPEC['entries'] if e['code'] == 'MUS 19R')
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    html = ('<h1>Music</h1><p class="course-disclaimer">General Catalog 2026–27</p>'
            '<p class="course-name">MUS 19. Blacktronika: Afrofuturism in Electronic Music (4)</p>')
    out = review.parse_observations(html)
    assert out['courses'] == []
    assert out['source_dispositions'] == [dict(code='MUS 19R', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">MUS 19R. New course (4)</p>')


def test_actual_music_practice_history_and_project_boundaries():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 33 and sum(e['approved_for_integration'] for e in by.values()) == 27
    assert {c for c, e in by.items() if e['category'] == 'applications'} == {'MUS 132R', 'MUS 103A', 'MUS 137A', 'MUS 137B', 'MUS 137C'}
    assert {c for c, e in by.items() if e.get('category_review') and e['category_review']['status'] == 'unclassified'} == {'MUS 160B', 'MUS 137D', 'MUS 137E', 'MUS 137F', 'MUS 199'}
    for code in ['MUS 17', 'MUS 107', 'MUS 150', 'MUS 112', 'MUS 113', 'MUS 116', 'MUS 120A', 'MUS 120B', 'MUS 120C']:
        assert by[code]['category'] == 'human_context'
    assert any('no online-delivery inference' in n for n in by['MUS 132R']['notes'])


def test_restrictions_recommendations_and_sequence_not_flattened():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert by['MUS 199']['printed_credits'] == '1–4'
    assert 'Pass/Not Pass grade only' in by['MUS 199']['observed_prerequisites']
    assert 'music and ICAM majors only' in by['MUS 160B']['observed_prerequisites']
    assert any('Two production-course limitation' in n and 'not explained' in n for n in by['MUS 160B']['notes'])
    assert any('Welcome Week' in n for n in by['MUS 132R']['notes'])
    assert any('recommended' in n and 'not a required corequisite' in n for n in by['MUS 120A']['notes'])
    assert 'MUS 137A or consent' in by['MUS 137B']['observed_prerequisites']
    assert 'MUS 137E and department approval' in by['MUS 137F']['observed_prerequisites']
    assert any('five times' in n for n in by['MUS 112']['notes'])
    assert any('twice' in n for n in by['MUS 150']['notes'])


def test_cached_full_source_replay_and_missing_set():
    source = review.SPEC['sources']['MUS']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode())
    assert len(out['courses']) == 27 and len(out['source_dispositions']) == 6
    assert {d['code'] for d in out['source_dispositions']} == {'MUS 8GS', 'MUS 19R', 'MUS 20R', 'MUS 126R', 'MUS 150GS', 'MUS 13AS'}
    assert sum(c['credits'] == 4 for c in out['courses']) == 26
    assert all(c['prerequisites'] for c in out['courses'])
    by = {c['code']: c for c in out['courses']}
    assert by['MUS 150']['prerequisites'] == 'MUS 126/ETHN 178, or MUS 127/ETHN 179, or consent of instructor.'
    assert by['MUS 132R']['prerequisites'] == 'by audition only; MUS 132. Department approval required.'
