import hashlib
from pathlib import Path

import pytest

from atlas.adapters import ucsd_cse_remaining_reviews as review

EXAMPLE = dict(review.SPEC['entries'][1])

def fixture(monkeypatch, body='Studies computing. Prerequisites: CSE 11 or CSE 8B and MATH 20C; instructor approval.'):
    entry = dict(EXAMPLE)
    entry['description_hash'] = hashlib.sha256(body.encode()).hexdigest()
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [entry]})
    return ('<h1>Computer Science and Engineering (CSE)</h1>'
            f'<p class="course-name">{entry["heading"]}</p>'
            f'<p class="course-descriptions">{body}</p>')


def test_observation_retains_unsolved_prerequisite_expression(monkeypatch):
    data = review.parse_observations(fixture(monkeypatch))
    assert data['courses'][0]['prerequisites'] == 'CSE 11 or CSE 8B and MATH 20C; instructor approval.'
    assert 'category_review' not in data['courses'][0]
    assert 'requirements' not in data
    assert 'course_identity_groups' not in data


def test_changed_prerequisite_invalidates_whole_review(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='source changed'):
        review.parse_observations(html.replace('instructor approval', 'no instructor approval'))


def test_unmatched_code_appearing_requires_review(monkeypatch):
    missing = dict(review.SPEC['entries'][0])
    monkeypatch.setattr(review, 'SPEC', {**review.SPEC, 'entries': [missing]})
    html = '<h1>Computer Science and Engineering (CSE)</h1>'
    assert review.parse_observations(html)['courses'] == []
    with pytest.raises(ValueError, match='identifier appeared'):
        review.parse_observations(html + '<p class="course-name">CSE 8B. New content (4)</p>')


def test_missing_prerequisites_differ_from_explicit_none(monkeypatch):
    assert review.parse_observations(fixture(monkeypatch, 'Studies computing.'))['courses'][0]['prerequisites'] is None
    assert review.parse_observations(fixture(monkeypatch, 'Studies computing. Prerequisites: none.'))['courses'][0]['prerequisites'] == 'none.'


def test_duplicate_identity_fails(monkeypatch):
    html = fixture(monkeypatch)
    with pytest.raises(ValueError, match='Duplicate'):
        review.parse_observations(html + html)


def test_review_manifest_is_complete_and_bounded():
    entries = review.SPEC['entries']
    assert len(entries) == len({e['id'] for e in entries}) == 88
    missing = {e['code'] for e in entries if e['heading'] is None}
    assert missing == {'CSE 8B', 'CSE 154', 'CSE 157', 'CSE 176B', 'CSE 186', 'CSE 5A'}
    by_code = {e['code']: e for e in entries}
    assert by_code['CSE 20']['category'] == 'mathematics'
    assert by_code['CSE 105']['category'] == 'foundations'
    assert by_code['CSE 127']['category'] == 'systems'
    assert by_code['CSE 151B']['category'] == 'ai_ml'
    assert by_code['CSE 194']['category'] == 'human_context'
    assert by_code['CSE 193']['category_review']['status'] == 'unclassified'
    assert by_code['CSE 5']['category_review']['candidate_categories'] == ['ai_ml', 'human_context']
    assert by_code['CSE 180']['id'] != by_code['CSE 180R']['id']


def test_private_source_replay():
    cache = Path('.cache/http/02421735947aad7739f42482f2448cb91ce18e810264063f4b601113ac4d93d4.body')
    if not cache.exists():
        pytest.skip('optional private copyrighted source cache is not redistributed')
    courses = {c['code']: c for c in review.parse_observations(cache.read_text())['courses']}
    assert len(courses) == 82
    assert courses['CSE 15L']['credits'] == 2
    assert courses['CSE 170']['credits'] == 5
    assert courses['CSE 90']['prerequisites'] is None
    assert 'CSE-PACE' in courses['CSE 89']['prerequisites']
    assert 'Concurrent tutor' in courses['CSE 95']['prerequisites']
    assert 'Not for students who plan to study AI' in courses['CSE 5']['prerequisites']
    assert 'two units of credit' in courses['CSE 29']['prerequisites']
