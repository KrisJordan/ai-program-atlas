import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest

from atlas.adapters import ucsd_computing_design_remaining_reviews as review


def fixture(monkeypatch, code='DSC 10', body='Data inference. Prerequisites: none.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]; key = entry['source_key']; source = spec['sources'][key]
    html = (f'<h1>{source["heading"]}</h1><h2>Courses</h2>'
            f'<p>For course descriptions not found in the UC San Diego General Catalog {source["catalog_year"]}, contact the department.</p>'
            f'<h2>{entry["section"]}</h2><p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    source['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_shared_heading_metadata_only(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['code'] == 'DSC 10' and len(out['courses']) == 1
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'none.' and c['category'] == 'mathematics'
    assert 'category_review' not in c and 'course_identity_groups' not in out


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Data inference.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('Prerequisites: none.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New major restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Data Science</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_shared_heading_duplicate_and_context_change(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('DSC 10/R.', 'DSC 10.'))
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">DSC 10. Other version (4)</p>')
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Courses</h2>', '<h2>Courses</h2><p>New policy.</p>'))


def test_independent_section_membership(monkeypatch):
    html = fixture(monkeypatch); extra = '<h2>Upper Division</h2>'; before = html + extra
    review.SPEC['sources']['DSC']['chapter_context_sha256'] = review.chapter_context_hash(before)
    start = before.index('<p class="course-name">'); target = before[start:before.index(extra)]
    moved = before[:start] + extra + target
    assert review.chapter_context_hash(moved) == review.chapter_context_hash(before)
    with pytest.raises(ValueError, match='section membership changed'):
        review.parse_observations(moved)


def test_complete_nested_and_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Data. Conditions apply. Prerequisites: approval.')
    html = html.replace('Data. Conditions apply. Prerequisites: approval.',
                        '<strong>Data.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_css_older_edition_and_conjunction(monkeypatch):
    html = fixture(monkeypatch, 'CSS 2', 'Research. Prerequisites: CSS 1 and choose one of COGS 14B, MATH 11.')
    c = review.parse_observations(html)['courses'][0]
    assert 'and choose one' in c['prerequisites']
    assert any('2023–24' in n and 'remain unconfirmed' in n for n in c['notes'])
    with pytest.raises(ValueError, match='edition changed'):
        review.parse_observations(html.replace('2023–24', '2026–27'))


def test_film_real_code_in_cinematic_chapter_and_two_unit_omission(monkeypatch):
    original = review.SPEC
    c = review.parse_observations(fixture(monkeypatch, 'FILM 71'))['courses'][0]
    assert c['code'] == 'FILM 71' and c['source_id'].endswith('-cin-courses')
    monkeypatch.setattr(review, 'SPEC', original)
    c = review.parse_observations(fixture(monkeypatch, 'ENG 15', 'Study skills.'))['courses'][0]
    assert c['credits'] == 2 and c['prerequisites'] is None


def test_missing_dsc_appearance_guard(monkeypatch):
    entries = [e for e in review.SPEC['entries'] if e['code'] in ['DSC 131','DSC 185']]
    html = fixture(monkeypatch)
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': entries})
    assert len(review.parse_observations(html)['source_dispositions']) == 2
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">DSC 131. New course (4)</p>')


def test_manual_method_and_eligibility_boundaries():
    by = {e['code']: e for e in review.SPEC['entries']}
    approved = [e for e in by.values() if e['approved_for_integration']]
    assert len(by) == 22 and len(approved) == 20
    assert Counter(e['category'] for e in approved) == {'applications':12,'mathematics':3,'ai_ml':3,'systems':1,'other':1}
    assert all(e['listed_name'] is None for e in by.values())
    assert by['DSC 102']['category'] == 'systems'
    assert by['DSC 155']['category'] == 'mathematics'
    assert by['CSS 2']['category_review']['candidate_categories'] == ['applications','human_context']
    assert any('strongly recommended, not a formal prerequisite' in n for n in by['DSC 140A']['notes'])
    assert any('does not separately print upper-division' in n for n in by['DSC 140B']['notes'])
    assert any('encouraged but explicitly not required' in n for n in by['DSC 155']['notes'])
    assert any('No DS25 restriction is printed' in n for n in by['DSC 161']['notes'])
    assert any('open to all undergraduates' in n for n in by['ENG 100D']['notes'])


@pytest.mark.parametrize('subject,expected,dispositions', [('ENG',4,0),('DSGN',3,0),('CIN',3,0),('DSC',9,2),('CSS',1,0)])
def test_exact_cached_chapter_replay(subject, expected, dispositions):
    source = review.SPEC['sources'][subject]; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == expected and len(out['source_dispositions']) == dispositions
    assert all(c['code'].split()[0] in source['subjects'] for c in out['courses'])
