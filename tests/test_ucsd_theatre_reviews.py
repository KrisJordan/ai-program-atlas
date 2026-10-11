import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_theatre_reviews as review


def fixture(monkeypatch, code='TDGE 40', body='Social movement. Prerequisites: none.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]
    html = ('<h1>Theatre and Dance</h1><h2>Courses</h2>'
            '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
            f'<h2>{entry["section"]}</h2><p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['sources']['THEA']['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only_explicit_none(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'none.' and c['category'] == 'human_context'
    assert 'category_review' not in c and c['source_id'].endswith('-theatre-courses')


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Social movement.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('Prerequisites: none.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New repeat limit.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Theatre and Dance</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_source_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_duplicate_and_section_policy_changes(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">TDGE 40. Duplicate (4)</p>')
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>TDGE—Theatre General</h2>', '<h2>TDGE—Theatre General</h2><p>New restriction.</p>'))


def test_section_membership_guard_independent_of_text_hash(monkeypatch):
    html = fixture(monkeypatch)
    # Keep the heading/context sequence unchanged while moving the target across sections.
    extra = '<h2>TDAC—Theatre Acting</h2>'
    before = html + extra
    review.SPEC['sources']['THEA']['chapter_context_sha256'] = review.chapter_context_hash(before)
    assert review.parse_observations(before)['courses']
    start = before.index('<p class="course-name">')
    target = before[start:before.index(extra)]
    moved = before[:start] + extra + target
    assert review.chapter_context_hash(moved) == review.chapter_context_hash(before)
    with pytest.raises(ValueError, match='section membership changed'):
        review.parse_observations(moved)


def test_complete_nested_and_unwrapped_course_text(monkeypatch):
    html = fixture(monkeypatch, body='Performance. Conditions apply. Prerequisites: approval.')
    html = html.replace('Performance. Conditions apply. Prerequisites: approval.',
                        '<strong>Performance.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_heading_title_hold_and_changed_range_heading(monkeypatch):
    original = review.SPEC
    missing = next(e for e in original['entries'] if e['code'] == 'TDMV 143')
    html = fixture(monkeypatch, 'TDGE 131')
    assert review.parse_observations(html)['source_dispositions'][0]['status'] == 'source_title_conflict'
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [missing]})
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='TDMV 143', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">TDMV 143. New course (4)</p>')
    monkeypatch.setattr(review, 'SPEC', original)
    html = fixture(monkeypatch, 'TDAC 104')
    with pytest.raises(ValueError, match='section membership changed|source changed'):
        review.parse_observations(html.replace('TDAC 104.', 'TDAC 104–106.'))


def test_range_credit_and_concurrent_rule(monkeypatch):
    c = review.parse_observations(fixture(monkeypatch, 'TDPF 163', 'Dance. Prerequisites: concurrent enrollment in TDPF 160.'))['courses'][0]
    assert c['credits'] is None
    assert c['prerequisites'] == 'concurrent enrollment in TDPF 160.'
    assert any('2–6 quarter units' in n for n in c['notes'])


def test_manual_classification_and_scope():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 37 and sum(e['approved_for_integration'] for e in by.values()) == 35
    assert by['TDAC 104']['category'] == 'human_context'
    assert by['TDAC 106']['category'] == 'applications'
    for code in ['TDAC 120', 'TDAC 105', 'TDMV 140', 'TDMV 141', 'TDMV 142', 'TDMV 144', 'TDMV 146', 'TDPF 163']:
        assert by[code]['category_review']['status'] == 'mixed'
        assert set(by[code]['category_review']['candidate_categories']) == {'applications', 'human_context'}
    for code in ['TDGE 196A', 'TDGE 196B']:
        assert by[code]['category_review']['status'] == 'unclassified'
    assert any('explicitly identifies an online' in n for n in by['TDGE 131R']['notes'])
    assert any('not always mandatory' in n for n in by['TDAC 120']['notes'])
    assert any('whichever is met first' in n for n in by['TDDE 132']['notes'])
    assert any('shared major-applicability cap' in n for n in by['TDDE 190']['notes'])
    assert any('department’s major requirements' in n for n in by['TDPR 104']['notes'])
    assert any('rather than merely recommended' in n for n in by['TDPF 161']['notes'])
    assert '3.5 GPA in major' in by['TDGE 196A']['observed_prerequisites']


def test_exact_cached_chapter_replay():
    source = review.SPEC['sources']['THEA']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == 35 and len(out['source_dispositions']) == 2
    assert sum(c['credits'] is None for c in out['courses']) == 10
    assert all(c['prerequisites'] is not None for c in out['courses'])
    assert all(c['code'].split()[0] in source['subjects'] for c in out['courses'])
