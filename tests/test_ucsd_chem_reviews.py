import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_chem_reviews as review


def fixture(monkeypatch, code='CHEM 117', body='Health disparities. Prerequisites: CHEM 40B, 40CH, or 41C.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]
    html = ('<h1>Chemistry and Biochemistry</h1><h2>Courses</h2>'
            '<p class="course-disclaimer">General Catalog 2026–27</p>'
            '<h2>Upper Division</h2>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only_alternative_prerequisites(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'CHEM 40B, 40CH, or 41C.'
    assert c['category'] == 'other' and 'category_review' not in c
    assert c['source_id'].endswith('-chem-courses')


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Health disparities.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('or 41C.', 'and 41C.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New credit exclusion.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Chemistry and Biochemistry</h1>', '<h1>Other chapter</h1>'), 'identity changed'),
    (lambda s: s + s, 'Duplicate'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_source_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_section_policy_addition_requires_review(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Upper Division</h2>', '<h2>Upper Division</h2><p>Enrollment restricted.</p>'))


def test_complete_nested_and_unwrapped_course_text(monkeypatch):
    html = fixture(monkeypatch, body='Chemistry. Conditions apply. Prerequisites: approval.')
    html = html.replace('Chemistry. Conditions apply. Prerequisites: approval.',
                        '<strong>Chemistry.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_missing_heading_and_appearance_hold(monkeypatch):
    entry = next(e for e in review.SPEC['entries'] if e['code'] == 'CHEM 15')
    html = fixture(monkeypatch)
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    out = review.parse_observations(html)
    assert out['courses'] == []
    assert out['source_dispositions'] == [dict(code='CHEM 15', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">CHEM 15. New course (4)</p>')


def test_manual_content_boundaries_and_credit_direction():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 14 and sum(e['approved_for_integration'] for e in by.values()) == 13
    assert by['CHEM 117']['category_review']['status'] == 'mixed'
    assert set(by['CHEM 117']['category_review']['candidate_categories']) == {'human_context', 'applications'}
    assert by['CHEM 151']['category'] == 'applications'
    assert all(e['credits'] == 4 for e in by.values() if e['approved_for_integration'])
    assert any('directional' in n for n in by['CHEM 6C']['notes'])
    assert any('after CHEM 6C' in n and 'not subsequently' in n for n in by['CHEM 6CH']['notes'])
    assert by['CHEM 6CH']['observed_prerequisites'] == 'CHEM 6BH and MATH 20B.'
    assert any('recommended' in n and 'not promoted' in n for n in by['CHEM 172']['notes'])
    assert any('first-year and sophomore' in n for n in by['CHEM 4']['notes'])
    assert any('unless space is available' in n for n in by['CHEM 143C']['notes'])
    assert any('SIO 141' in n and 'no exact' in n for n in by['CHEM 174']['notes'])


def test_omitted_prerequisites_stay_null(monkeypatch):
    c = review.parse_observations(fixture(monkeypatch, 'CHEM 4', 'Chemical models. Recommended: concurrent MATH 3C.'))['courses'][0]
    assert c['prerequisites'] is None
    assert any('not absence' in n for n in c['notes'])


def test_exact_cached_chapter_replay():
    source = review.SPEC['sources']['CHEM']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == 13 and len(out['source_dispositions']) == 1
    assert sum(c['prerequisites'] is None for c in out['courses']) == 2
    assert all(c['credits'] == 4 for c in out['courses'])
