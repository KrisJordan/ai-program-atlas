import copy
import hashlib
from collections import Counter
from pathlib import Path

import pytest

from atlas.adapters import ucsd_cogs_remaining_reviews as review


def fixture(monkeypatch, code='COGS 120', body='Interaction design. Prerequisites: COGS 108.'):
    spec = copy.deepcopy(review.SPEC)
    entry = next(e for e in spec['entries'] if e['code'] == code)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    spec['entries'] = [entry]
    html = ('<h1>Cognitive Science</h1><h2>Courses</h2>'
            '<p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>'
            f'<h2>{entry["section"]}</h2><p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')
    spec['sources']['COGS']['chapter_context_sha256'] = review.chapter_context_hash(html)
    monkeypatch.setattr(review, 'SPEC', spec)
    return html


def test_metadata_only_no_inherited_insufficiency_label(monkeypatch):
    out = review.parse_observations(fixture(monkeypatch)); c = out['courses'][0]
    assert set(out) == {'id', 'courses', 'source_dispositions'}
    assert c['name'] == 'Interaction Design'
    assert c['credits'] == 5 and c['credit_unit'] == 'quarter_hours'
    assert c['prerequisites'] == 'COGS 108.' and c['category'] == 'applications'
    assert 'category_review' not in c


@pytest.mark.parametrize('transform,match', [
    (lambda s: s.replace('Interaction design.', 'Unrelated research.'), 'source changed'),
    (lambda s: s.replace('Prerequisites: COGS 108.', 'Prerequisites: approval.'), 'source changed'),
    (lambda s: s.replace('(5)', '(4)'), 'source changed'),
    (lambda s: s + '<p>New credit exclusion.</p>', 'source changed'),
    (lambda s: s.replace('2026–27', '2027–28'), 'edition changed'),
    (lambda s: s.replace('<h1>Cognitive Science</h1>', '<h1>Other chapter</h1>'), 'Expected one'),
    (lambda s: s + '<input type="password">', 'Access page'),
])
def test_material_source_guards(monkeypatch, transform, match):
    with pytest.raises(ValueError, match=match):
        review.parse_observations(transform(fixture(monkeypatch)))


def test_duplicate_changed_range_and_missing_exact_code(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + '<p class="course-name">COGS 120. Duplicate (5)</p>')
    for altered in ['COGS 120–121.', 'COGS 121.']:
        with pytest.raises(ValueError, match='section membership changed|source changed'):
            review.parse_observations(html.replace('COGS 120.', altered))


def test_chapter_policy_and_independent_section_membership(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='chapter context changed'):
        review.parse_observations(html.replace('<h2>Courses</h2>', '<h2>Courses</h2><p>New prerequisite policy.</p>'))
    extra = '<h2>Graduate</h2>'; before = html + extra
    review.SPEC['sources']['COGS']['chapter_context_sha256'] = review.chapter_context_hash(before)
    start = before.index('<p class="course-name">'); target = before[start:before.index(extra)]
    moved = before[:start] + extra + target
    assert review.chapter_context_hash(moved) == review.chapter_context_hash(before)
    with pytest.raises(ValueError, match='section membership changed'):
        review.parse_observations(moved)


def test_complete_nested_and_unwrapped_text(monkeypatch):
    html = fixture(monkeypatch, body='Design. Conditions apply. Prerequisites: approval.')
    html = html.replace('Design. Conditions apply. Prerequisites: approval.',
                        '<strong>Design.</strong></p>Conditions apply.<div><p>Prerequisites: approval.</p></div><p>')
    assert review.parse_observations(html)['courses'][0]['prerequisites'] == 'approval.'
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('Conditions apply.', ''))


def test_recommendation_not_formal_prerequisite(monkeypatch):
    c = review.parse_observations(fixture(monkeypatch, 'COGS 18', 'Python. Recommended preparation: COGS 3.'))['courses'][0]
    assert c['prerequisites'] is None
    assert any('not a stated prerequisite' in n for n in c['notes'])


def test_exact_recommendation_suffix_and_source_spelling(monkeypatch):
    c = review.parse_observations(fixture(monkeypatch, 'COGS 101B', 'Learning. Prerequisites: COGS 1. Recommended: COGS 101A.'))['courses'][0]
    assert c['prerequisites'] == 'COGS 1. Recommended: COGS 101A.'
    assert any('not promoted' in n for n in c['notes'])


def test_manual_ai_neuroscience_design_and_mixed_boundaries():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert len(by) == 64 and all(e['approved_for_integration'] for e in by.values())
    assert not {'COGS 2', 'COGS 190A', 'COGS 194'} & by.keys()
    assert Counter(e['category'] for e in by.values()) == {'applications':44,'ai_ml':7,'other':6,'human_context':3,'foundations':2,'mathematics':2}
    assert all(e['listed_name'] is None for e in by.values())
    assert all(e['category_review']['status'] in ['reviewed','mixed'] for e in by.values())
    for code in ['COGS 118C','COGS 189','COGS 107B','COGS 124','COGS 152','COGS 164','COGS 178']:
        assert by[code]['category'] == 'applications'
    for code in ['COGS 118A','COGS 118B','COGS 181','COGS 182','COGS 185','COGS 186','COGS 188']:
        assert by[code]['category'] == 'ai_ml'
    assert by['COGS 14B']['category'] == 'mathematics'
    assert by['COGS 20']['category_review']['status'] == 'mixed'
    assert by['COGS 8']['category_review']['candidate_categories'] == ['foundations','applications']
    assert by['COGS 120']['credits'] == 5
    assert sum(e['credits'] == 4 for e in by.values()) == 63


def test_exact_conditions_and_identity_boundaries():
    by = {e['code']: e for e in review.SPEC['entries']}
    assert any('either order' in n for n in by['COGS 118A']['notes'])
    assert any('repeated CSE 11' in n for n in by['COGS 118B']['notes'])
    assert any('not a mandatory prerequisite' in n for n in by['COGS 120']['notes'])
    assert any('renumbered from HDP 121' in n for n in by['COGS 110']['notes'])
    assert any('three-code exclusion' in n for n in by['COGS 20']['notes'])
    assert any('by petition' in n for n in by['COGS 17']['notes'])
    assert any('not converted into a required course list' in n for n in by['COGS 156']['notes'])
    assert any('should have experience' in n for n in by['COGS 157']['notes'])
    assert any('formal prerequisite' in n for n in by['COGS 164']['notes'])
    assert any('not an enrollment prohibition' in n for n in by['COGS 15']['notes'])
    assert 'freshman and sophomore standing' in by['COGS 8']['observed_prerequisites']


def test_exact_cached_chapter_replay():
    source = review.SPEC['sources']['COGS']; path = Path(source['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored current chapter absent')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['source_hash']
    out = review.SOURCE_PARSERS[source['url']](raw.decode())
    assert len(out['courses']) == 64 and out['source_dispositions'] == []
    assert sum(c['prerequisites'] is None for c in out['courses']) == 12
    assert all(c['code'].startswith('COGS ') for c in out['courses'])
