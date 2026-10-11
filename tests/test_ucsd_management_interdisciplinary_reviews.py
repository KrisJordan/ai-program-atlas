import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_management_interdisciplinary_reviews as review


def fixture(monkeypatch, code='MGT 164', body='Leadership. Prerequisites: upper-division standing.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]; key = entry['source_key']
    html = (f'<h1>{spec["sources"][key]["heading"]}</h1><h2>Courses</h2>'
            '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
            f'<h2>{entry["section"]}</h2><p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['sources'][key]['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'upper-division standing.' and c['category'] == 'applications'
    assert 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Leadership.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('upper-division standing.', 'graduate standing.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New credit limit.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Rady School of Management</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_duplicate_and_chapter_eligibility_change(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">MGT 164. Duplicate (4)</p>')
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Courses</h2>', '<h2>Courses</h2><p>New prerequisite policy.</p>'))


def test_section_membership_guard(monkeypatch):
    html = fixture(monkeypatch); extra = '<h2>MBA Approved Course List</h2>'; before = html + extra
    review.SPEC['sources']['MGT']['chapter_context_sha256'] = review.chapter_context_hash(before)
    start = before.index('<p class="course-name">'); target = before[start:before.index(extra)]
    moved = before[:start] + extra + target
    assert review.chapter_context_hash(moved) == review.chapter_context_hash(before)
    with pytest.raises(ValueError, match='section membership changed'):
        review.parse_observations(moved)


def test_complete_nested_and_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Leadership. Conditions apply. Prerequisites: approval.')
    html = html.replace('Leadership. Conditions apply. Prerequisites: approval.',
                        '<strong>Leadership.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_title_hold(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch, 'MGT 12'))
    assert out['courses'] == []
    assert out['source_dispositions'] == [dict(code='MGT 12', status='source_title_conflict', observed_name='Personal Financial Management')]


def test_hmnr_compound_heading_and_null_individual_rule(monkeypatch):
    html = fixture(monkeypatch, 'HMNR 100', 'Historical study of human rights.')
    out = review.parse_observations(html); c = out['courses'][0]
    assert c['code'] == 'HMNR 100' and c['prerequisites'] is None
    assert len(out['courses']) == 1 and 'course_identity_groups' not in out
    assert any('two stated audiences' in n for n in c['notes'])
    assert any('SOCI 174 or HITO 119' in n for n in c['notes'])
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('SOCI 174 or HITO 119', 'SOCI 174 and HITO 119'))


def test_manual_subject_and_eligibility_boundaries():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 19 and sum(e['approved_for_integration'] for e in by.values()) == 18
    assert by['CCS 123']['category'] == 'human_context'
    for code in ['INTL 190', 'INTL 190H', 'INTL 196H']:
        assert by[code]['category_review']['status'] == 'unclassified'
    for code in ['MGT 5', 'MGT 102', 'MGT 108R', 'MGT 164', 'MGT 167']:
        assert by[code]['category'] == 'applications'
    assert by['MGT 18']['category'] == by['MGT 18GS']['category'] == 'human_context'
    assert all(e['credits'] == 4 for e in by.values())
    assert any('sophomore' in n and 'Upper Division' in n for n in by['INTL 100']['notes'])
    assert any('C– or better' in n for n in by['INTL 190']['notes'])
    assert any('does not repeat the C– threshold' in n for n in by['INTL 190H']['notes'])
    assert any('distance education' in n for n in by['MGT 108R']['notes'])
    assert any('not thereby an AI-degree requirement' in n for n in by['LAWS 101']['notes'])
    assert any('repeated for credit up to four times' in n for n in by['CLAS 109']['notes'])


@pytest.mark.parametrize('subject,expected,dispositions', [('MGT',7,1),('INTL',4,0),('CLAS',3,0),('HMNR',2,0),('LAWS',1,0),('CCS',1,0)])
def test_exact_cached_chapter_replay(subject, expected, dispositions):
    source = review.SPEC['sources'][subject]; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == expected and len(out['source_dispositions']) == dispositions
    assert all(c['code'].split()[0] == subject for c in out['courses'])
