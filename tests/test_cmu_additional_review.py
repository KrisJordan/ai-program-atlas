import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from atlas.adapters.cmu_additional.adapter import parse
from atlas.adapters.cmu_additional import course_review
from atlas.additional_major_audit import review_fingerprint, validate_ledger
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program
from test_cmu_penn import additional_fixture


def test_source_fixed_rows_and_nested_sequence_choices():
    p = parse(additional_fixture())
    rows = {r['id'].removeprefix('cmu-additional-ai-'): r for r in p['requirements']}
    for key, code in [('pre-group-1', '15-112'), ('math-group-3', '21-122'),
                      ('math-group-4', '21-241'), ('math-group-5', '36-401')]:
        assert (rows[key]['kind'], rows[key]['count'], rows[key]['course_ids']) == ('all', None, ['cmu-' + code])
    assert rows['math-group-1']['kind'] == rows['math-group-2']['kind'] == 'choose_courses'
    assert rows['probability']['kind'] == 'alternative'
    pairs = [r for r in rows.values() if r['parent_id'] == rows['probability']['id'] and len(r['course_ids']) == 2]
    assert len(pairs) == 4 and all(r['kind'] == 'all' and r['credits'] == 18 for r in pairs)
    assert p['curriculum_status'] == 'partial' and 'curriculum_audit' not in p
    assert all(c['category'] == 'other' and 'category_review' not in c for c in p['courses'])


@pytest.mark.parametrize('old,new', [
    ('following courses are required', 'following courses are suggested'),
    ('21-241', '21-242'), ('36-401', '36-402'), ('15-112', '15-113'),
])
def test_fixed_role_guard_rejects_changed_directive_or_identity(old, new):
    with pytest.raises(ValueError, match='all-of directive|fixed row'):
        parse(additional_fixture().replace(old, new))


def test_description_observer_does_not_replay_independent_review(monkeypatch):
    url = 'https://example.edu/courses/'
    desc = 'Synthetic system storage and execution.'
    digest = hashlib.sha256(desc.encode()).hexdigest()
    monkeypatch.setattr(course_review, 'REVIEWS', {'15-213': dict(name='Synthetic systems',
        category='systems', catalog_year='2026-2027', description_digest=digest,
        source_id='synthetic', url=url)})
    monkeypatch.setattr(course_review, 'DIRECTORIES', {url: 'Synthetic Courses'})
    html = '<h1>Synthetic Courses</h1><p>2026-2027 Catalog</p><dl class="courseblock"><dt>15-213 Synthetic systems</dt><dd>Fall: 12 units<br/>' + desc + '<br/>Prerequisite: 15-122 Min. grade C</dd></dl>'
    result = course_review.parse(html, url)
    assert result['courses'][0]['category'] == 'systems'
    assert result['courses'][0]['credits'] == 12
    assert result['courses'][0]['prerequisites'] == '15-122 Min. grade C'
    assert 'category_review' not in result['courses'][0]
    assert course_review.parse(html.replace(desc, 'Synthetic neural learning.'), url)['courses'][0]['category'] == 'other'
    assert course_review.parse(html.replace('2026-2027', '2027-2028'), url)['courses'][0]['category'] == 'other'
    with pytest.raises(ValueError, match='inventory changed'):
        course_review.parse(html.replace('15-213', '15-214'), url)
    course_review.REVIEWS['15-213']['course_entry_note'] = 'Synthetic restriction.'
    with pytest.raises(ValueError, match='course-entry evidence changed'):
        course_review.parse(html.replace(desc, 'Synthetic altered entry.'), url)


def test_manual_expected_sets_categories_and_stronger_digest():
    p = json.loads(Path('data/programs/cmu-additional-ai.json').read_text())
    ledger = json.loads(Path('research/additional-major-review-cmu.json').read_text())
    row = ledger['programs'][0]
    validate_program(p)
    validate_ledger(ledger, [p])
    actual = requirement_profile(p, include_course_ids=True)
    assert set(row['expected_course_ids']['required']) == {'cmu-' + c for c in
        '15-112 15-122 15-150 15-210 15-213 15-251 07-280 07-380 21-122 21-241 36-401'.split()}
    assert [actual[r]['count'] for r in ['required', 'options', 'unresolved']] == [11, 50, 0]
    assert actual['required']['categories']['systems'] == 1
    assert actual['options']['classification'] == {'reviewed': 41, 'mixed': 9, 'unclassified': 0, 'unreviewed': 0}
    assert all(c['description'] and c['category_review'] for c in p['courses'])
    changed = deepcopy(p)
    changed['major_relationship']['eligibility'] += ' Changed scope.'
    assert review_fingerprint(changed) != row['reviewed_content_hash']
    with pytest.raises(ValueError, match='resolved content is stale'):
        validate_ledger(ledger, [changed])
