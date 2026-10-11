import copy
import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_final_science_reviews as review


def fixture(monkeypatch, code='DSC 20', body='Programming. Prerequisites: DSC 10/R.'):
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


def test_joint_heading_metadata_only(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['code'] == 'DSC 20' and len(out['courses']) == 1
    assert c['credits'] == 4 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'DSC 10/R.' and c['category'] == 'foundations'
    assert 'category_review' not in c and 'course_identity_groups' not in out


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Programming.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('Prerequisites: DSC 10/R.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(4)', '(6)'), 'source changed'),
    (lambda s: s + '<p>New restriction.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Data Science</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_shared_heading_changes_and_duplicate_identifier(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('DSC 20/R.', 'DSC 20.'))
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">DSC 20. Separate version (4)</p>')
    with pytest.raises(ValueError, match='section membership changed|source changed'):
        review.parse_observations(html.replace('DSC 20/R.', 'DSC 20R.'))


def test_chapter_policy_and_independent_section_membership(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Courses</h2>', '<h2>Courses</h2><p>Changed policy.</p>'))
    extra = '<h2>Upper Division</h2>'; before = html + extra
    review.SPEC['sources']['DSC']['chapter_context_sha256'] = review.chapter_context_hash(before)
    start = before.index('<p class="course-name">'); target = before[start:before.index(extra)]
    moved = before[:start] + extra + target
    assert review.chapter_context_hash(moved) == review.chapter_context_hash(before)
    with pytest.raises(ValueError, match='section membership changed'):
        review.parse_observations(moved)


def test_complete_nested_and_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Programming. Conditions apply. Prerequisites: approval.')
    html = html.replace('Programming. Conditions apply. Prerequisites: approval.',
                        '<strong>Programming.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_css_older_explicit_edition_and_prerequisite_omission(monkeypatch):
    html = fixture(monkeypatch, 'CSS 1', 'Python programming.')
    c = review.parse_observations(html)['courses'][0]
    assert c['prerequisites'] is None and c['category'] == 'foundations'
    assert any('2023–24' in n and 'current degree membership' in n for n in c['notes'])
    with pytest.raises(ValueError, match='edition changed'):
        review.parse_observations(html.replace('2023–24', '2026–27'))


def test_missing_cogs_heading(monkeypatch):
    entry = next(e for e in review.SPEC['entries'] if e['code'] == 'COGS 194')
    html = fixture(monkeypatch, 'COGS 2')
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    assert review.parse_observations(html)['source_dispositions'] == [dict(code='COGS 194', status='no_current_heading')]
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">COGS 194. New course (4)</p>')


def test_manual_subjects_and_restriction_scopes():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 19 and sum(e['approved_for_integration'] for e in by.values()) == 18
    assert all(e['credits'] == 4 for e in by.values() if e['approved_for_integration'])
    for code in ['DSC 180A', 'DSC 180B', 'COGS 190A']:
        assert by[code]['category_review']['status'] == 'unclassified'
    for code in ['ANBI 131', 'ANBI 132', 'ANBI 121', 'DSC 160']:
        assert by[code]['category_review']['status'] == 'mixed'
    assert by['ANBI 174']['category'] == by['MATH 163']['category'] == 'human_context'
    assert by['ANBI 130']['category'] == 'applications'
    assert any('no space-available exception' in n for n in by['DSC 180B']['notes'])
    assert any('all others may enroll as space permits' in n for n in by['DSC 160']['notes'])
    assert any('discussion section' in n for n in by['DSC 180B']['notes'])
    assert any('repeated CSE 151A' in n for n in by['DSC 180A']['notes'])
    assert any('should be taken' in n and 'not changed' in n for n in by['COGS 190A']['notes'])
    assert any('equivalent or higher-level' in n for n in by['MATH 20E']['notes'])
    assert any('does not print an instructor-consent' in n for n in by['MATH 20E']['notes'])


@pytest.mark.parametrize('subject,expected,dispositions', [('ANTH',6,0),('DSC',5,0),('MATH',4,0),('COGS',2,1),('CSS',1,0)])
def test_exact_cached_chapter_replay(subject, expected, dispositions):
    source = review.SPEC['sources'][subject]; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == expected and len(out['source_dispositions']) == dispositions
    assert all(c['code'].split()[0] in source['subjects'] for c in out['courses'])
