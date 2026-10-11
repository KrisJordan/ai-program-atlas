"""Synthetic change detection and bounded manual-content expectations."""
import copy
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters import ucsd_codeonly_science_reviews as review


@pytest.fixture
def synthetic(monkeypatch):
    html = '''<h1>Example Science</h1><h2>Courses</h2>
    <p>For course descriptions not found in the UC San Diego General Catalog 2026–27, contact the department.</p>
    <h3>Lower Division</h3><p class="course-name">EXSC 1. Test Methods (4)</p>
    <p>Construct and compare estimators. Prerequisites: EXSC 0 or instructor consent.</p>
    <h3>Upper Division</h3>'''
    soup = BeautifulSoup(html, 'html.parser')
    node = soup.select_one('.course-name')
    source = {'heading': 'Example Science', 'catalog_year': '2026–27', 'source_id': 'test-source', 'url': 'https://example.edu/catalog',
              'chapter_context_sha256': review.chapter_context_hash(soup),
              'heading_inventory_sha256': review.digest('EXSC 1. Test Methods (4)')}
    entries = [dict(id='test-1', code='EXSC 1', source_key='EXSC', heading='EXSC 1. Test Methods (4)', name='Test Methods',
                    description_hash=review.digest(review.following_text(node)), description='Compares estimators.', credits=4,
                    section_path=review.section_path(node), approved_for_integration=True, notes=[],
                    category_review={'status': 'reviewed'}, category='mathematics'),
               dict(id='test-2', code='EXSC 2', source_key='EXSC', heading=None, approved_for_integration=False)]
    monkeypatch.setattr(review, 'SPEC', dict(program_id='test-program', sources={'EXSC': source}, entries=entries))
    return html


def test_observations_are_not_manual_reviews(synthetic):
    result = review.parse_observations(synthetic, subject='EXSC')
    course, = result['courses']
    assert course['credits'] == 4
    assert course['prerequisites'] == 'EXSC 0 or instructor consent.'
    assert course['source_id'] == 'test-source'
    assert 'category' not in course and 'category_review' not in course
    assert not {'requirements', 'curriculum_audit', 'curriculum_status', 'checked_at', 'reviewed_at'} & result.keys()
    assert result['source_dispositions'][0]['code'] == 'EXSC 2'
    assert result['source_dispositions'][0]['status'] == 'no_current_heading'


@pytest.mark.parametrize('before,after', [
    ('Example Science', 'Wrong Department'),
    ('2026–27', '2025–26'),
    ('Construct and compare estimators.', 'Construct classifiers.'),
    ('EXSC 1. Test Methods (4)', 'EXSC 1/201. Test Methods (4)'),
    ('EXSC 0 or instructor consent.', 'EXSC 0 and instructor consent.'),
    ('<h3>Lower Division</h3>', '<h3>Lower Division</h3><p>Majors only.</p>'),
])
def test_changed_identity_edition_body_and_policy_require_review(synthetic, before, after):
    with pytest.raises(ValueError):
        review.parse_observations(synthetic.replace(before, after), subject='EXSC')


def test_missing_heading_appearance_needs_review(synthetic):
    with pytest.raises(ValueError, match='inventory'):
        review.parse_observations(synthetic + '<p class="course-name">EXSC 2. Newly Listed (4)</p><p>New content.</p>', subject='EXSC')


def test_duplicate_heading_rejected(synthetic):
    with pytest.raises(ValueError, match='inventory'):
        review.parse_observations(synthetic + '<p class="course-name">EXSC 1. Test Methods (4)</p>', subject='EXSC')


def test_section_move_is_not_same_course_context(synthetic):
    soup = BeautifulSoup(synthetic, 'html.parser')
    heading = soup.select_one('.course-name')
    body = heading.find_next_sibling('p')
    heading.extract(); body.extract()
    soup.append(heading); soup.append(body)
    # Same titles, introductions and complete body, but moved into upper division.
    with pytest.raises(ValueError, match='section'):
        review.parse_observations(str(soup), subject='EXSC')


def test_access_gate_rejected_even_with_copied_catalog_text(synthetic):
    with pytest.raises(ValueError, match='gate'):
        review.parse_observations(synthetic + '<input type="password">', subject='EXSC')


def test_exact_manual_scope_and_missingness():
    entries = review.SPEC['entries']
    current = {e['code']: e for e in entries if e['approved_for_integration']}
    missing = {e['code']: e for e in entries if not e['approved_for_integration']}
    assert len(entries) == 61 and len(current) == 54
    assert set(missing) == {'MAE 5', 'MAE 8', 'MAE 9', 'BILD 45GS', 'BILD 46GS', 'SIO 150', 'BIEB 100'}
    assert all(e['name'] is None and e['description'] is None and e['credits'] is None and 'category_review' not in e for e in missing.values())
    assert {e['credits'] for e in current.values()} == {4}
    assert sum(e['prerequisites'] is not None for e in current.values()) == 36
    assert len(review.SPEC['sources']) == 13
    assert all(e['category_review']['source_ids'] == [review.SPEC['sources'][e['source_key']]['source_id']] for e in current.values())


def test_content_distinctions_and_conditional_credit():
    e = {e['code']: e for e in review.SPEC['entries']}
    assert e['ASTR 10']['category'] == 'human_context'
    assert e['ASTR 18']['category'] == 'applications'
    assert e['BILD 62']['category'] == e['SE 9']['category'] == 'foundations'
    assert e['HDS 110']['category'] == 'applications'
    assert e['ECE 176']['category'] == 'ai_ml'
    assert e['BENG 100']['category'] == e['PSYC 60']['category'] == 'mathematics'
    assert e['ECE 140A']['category_review']['status'] == 'mixed'
    assert e['ECE 140B']['category_review']['candidate_categories'] == ['foundations', 'applications']
    assert e['ECE 109']['credits'] == 4
    assert 'Only one credit' in ' '.join(e['ECE 109']['notes'])
    assert 'C−' in ' '.join(e['CENG 15']['notes'])
    assert 'C−' not in ' '.join(e['NANO 15']['notes'])
    assert 'nonbiology majors only' in ' '.join(e['BILD 12']['notes'])
    assert 'concurrent enrollment in MATH 20A' in ' '.join(e['CHEM 6AH']['notes'])
    assert e['SIO 20R']['prerequisites'] == 'none.'
    assert e['ASTR 10']['prerequisites'] is None


PROVENANCE = Path('/tmp/ucsd-codeonly-science61-sources.json')
@pytest.mark.parametrize('chapter', sorted(review.SPEC['sources']))
def test_optional_actual_source_replay(chapter):
    if not PROVENANCE.exists():
        pytest.skip('Optional ignored source cache provenance absent')
    mapping = {s['source_key']: s for s in json.loads(PROVENANCE.read_text())}
    path = Path(mapping[chapter]['cache_path'])
    if not path.exists():
        pytest.skip('Optional ignored source body absent')
    result = review.SOURCE_PARSERS[mapping[chapter]['url']](path.read_text())
    expected = [e for e in review.SPEC['entries'] if e['source_key'] == chapter]
    assert {c['id'] for c in result['courses']} == {e['id'] for e in expected if e['approved_for_integration']}
    assert {d['code'] for d in result['source_dispositions']} == {e['code'] for e in expected if not e['approved_for_integration']}
    assert all('category_review' not in c and 'category' not in c for c in result['courses'])
