"""Guards and source decisions for the assigned code-only performance queue."""
import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_performance_remaining_reviews as review


def fixture(monkeypatch, code='TDDE 1', body='Studio and historical study. No prerequisite field.'):
    entry = copy.deepcopy(next(e for e in review.SPEC['entries'] if e['code'] == code))
    key = entry['source_key']
    spec = copy.deepcopy(review.SPEC)
    spec['entries'] = [entry]
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    source = spec['sources'][key]
    html = (f'<h1>{source["heading"]}</h1><h2>Courses</h2>'
            '<p class="course-disclaimer">For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
            f'<h3>{entry["section"]}</h3><p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    source['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html, key


def test_runtime_observations_do_not_certify_reviews_or_roles(monkeypatch):
    html, key = fixture(monkeypatch)
    out = review.parse_observations(html, subject=key)
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    course = out['courses'][0]
    assert course['prerequisites'] is None
    assert course['credits'] == 4 and course['credit_unit'] == 'quarter_hours'
    assert course['category'] == 'other'
    assert 'category_review' not in course
    assert 'requirements' not in out and 'course_identity_groups' not in out


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Studio and historical study', 'Programming instruction'), 'source changed'),
    (lambda s: s + '<div><p>Enrollment limited to majors.</p></div>', 'source changed'),
    (lambda s: s.replace('(4)', '(2)'), 'source changed'),
    (lambda s: s.replace('TDDE 1.', 'TDDE 2.'), 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Theatre and Dance</h1>', '<h1>Unrelated</h1>'), 'identity changed'),
    (lambda s: s.replace('<h3>', '<p>Major-only registration.</p><h3>'), 'context changed'),
    (lambda s: s.replace('TDDE—Theatre Design', 'Graduate'), 'context changed'),
    (lambda s: s + '<input type="password">', 'Access page'),
    (lambda s: s + s, 'edition changed'),
])
def test_changes_to_actual_source_require_new_review(monkeypatch, transform, match):
    html, key = fixture(monkeypatch)
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(html), subject=key)


def test_nested_or_unwrapped_conditions_are_in_full_block_guard(monkeypatch):
    html, key = fixture(monkeypatch, body='Studio. Conditions apply. Prerequisites: consent.')
    html = html.replace('Studio. Conditions apply. Prerequisites: consent.',
                        '<strong>Studio.</strong></p>Conditions apply.<div><p>Prerequisites: consent.</p></div><p>')
    assert review.parse_observations(html, subject=key)['courses'][0]['prerequisites'] == 'consent.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''), subject=key)


def test_shared_music_sequence_is_three_explicit_members_not_a_credit_range(monkeypatch):
    body = 'Pitch and notation practice. Prerequisites: examination or consent. Must be taken in sequence.'
    html, key = fixture(monkeypatch, code='MUS 2A', body=body)
    spec = copy.deepcopy(review.SPEC)
    original = __import__('json').loads(Path(review.__file__).with_suffix('.json').read_text())
    entries = [copy.deepcopy(e) for e in original['entries'] if e['code'] in {'MUS 2A', 'MUS 2B', 'MUS 2C'}]
    for entry in entries:
        entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = entries
    monkeypatch.setattr(review, 'SPEC', spec)
    result = review.parse_observations(html, subject=key)['courses']
    assert {c['code'] for c in result} == {'MUS 2A', 'MUS 2B', 'MUS 2C'}
    assert all(c['credits'] == 4 for c in result)
    assert len({c['id'] for c in result}) == 3
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('4-4-4', '4-2-4'), subject=key)


def test_missing_music10_is_not_filled_from_music101_or_title_similarity(monkeypatch):
    html, key = fixture(monkeypatch, 'MUS 80', 'Changing music topics. Prerequisites: consent.')
    source = review.SPEC['sources']['MUS']
    original = __import__('json').loads(Path(review.__file__).with_suffix('.json').read_text())
    entry = next(e for e in original['entries'] if e['code'] == 'MUS 10')
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    result = review.parse_observations(html, subject=key)
    assert result['courses'] == []
    assert result['source_dispositions'] == [{'code': 'MUS 10', 'status': 'no_current_heading'}]
    assert entry['category_review'] is None
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">MUS 10. Newly listed subject (4)</p><p>New content.</p>', subject=key)


def test_specific_content_decisions_do_not_follow_prefixes_or_technology_words():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 103 and sum(e['approved_for_integration'] for e in by.values()) == 102
    for code in ['MUS 6', 'MUS 7', 'MUS 127', 'VIS 7', 'VIS 10', 'VIS 31', 'VIS 159', 'TDGE 126', 'TDTR 120']:
        assert by[code]['category'] == 'human_context'
    for code in ['MUS 1A', 'MUS 5', 'MUS 20', 'VIS 9', 'VIS 32', 'VIS 41', 'TDAC 1', 'TDDR 101', 'TDTR 115']:
        assert by[code]['category'] == 'applications'
    for code in ['VIS 2', 'VIS 8', 'VIS 30', 'VIS 70N', 'VIS 80', 'TDDE 1', 'TDDM 5', 'TDHT 119', 'TDMV 43', 'TDMV 148', 'TDMV 149']:
        assert by[code]['category_review']['status'] == 'mixed'
        assert by[code]['category'] == 'other'
    assert by['MUS 80']['category_review']['status'] == 'unclassified'
    assert by['MUS 80']['credits'] is None and by['MUS 80']['printed_credits'] == '1–4'


def test_restrictions_are_not_cancelled_by_none_or_pool_membership():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert 'Art history majors only' in by['VIS 23']['observed_prerequisites']
    assert 'within a year' in by['VIS 23']['observed_prerequisites']
    assert 'Open to visual arts majors and minors' in by['VIS 60']['observed_prerequisites']
    assert 'cinematic arts majors and minors' in by['VIS 70N']['observed_prerequisites']
    assert any('residence' in n for n in by['VIS 80']['notes'])
    assert by['TDDR 101']['observed_prerequisites'] is None
    assert any('recommended' in n and 'not stated prerequisites' in n for n in by['TDDR 101']['notes'])
    assert by['TDHT 119']['observed_prerequisites'] == 'interview required.'
    assert by['TDMV 148']['observed_prerequisites'] == 'TDMV 138.'
    assert 'TDMV 138 or consent' in by['TDMV 149']['observed_prerequisites']
    assert any('TDGE 11' in n and 'topic-specific' in n for n in by['TDGE 12']['notes'])
    for code in ['MUS 2A', 'MUS 2B', 'MUS 2C']:
        assert 'concurrently enrolled' in by[code]['observed_prerequisites']
        assert 'Music majors' in by[code]['observed_prerequisites']


@pytest.mark.parametrize('key,count', [('MUS', 22), ('VIS', 27), ('THEA', 53)])
def test_full_cached_source_replay(key, count):
    source = review.SPEC['sources'][key]
    path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored actual UCSD chapter unavailable')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.parse_observations(raw.decode(), subject=key)
    assert len(out['courses']) == count
    assert len(out['source_dispositions']) == (1 if key == 'MUS' else 0)
    assert all('category_review' not in c for c in out['courses'])
    expected = {e['id']: e for e in review.SPEC['entries'] if e['source_key'] == key and e['approved_for_integration']}
    for course in out['courses']:
        entry = expected[course['id']]
        assert course['prerequisites'] == entry['observed_prerequisites']
        assert course['name'] and course['description']
