"""Protect bounded replacement judgments against false role certification."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / 'research/degree-audit/independent-resolution-usf-wm.json').read_text())['programs']


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['program_id'])
def test_complete_proposed_core_rows_match_resolved_facts(row):
    p = resolve_program(json.loads((ROOT / 'data/programs' / (row['program_id'] + '.json')).read_text()))
    validate_core_review(row, p['id'])
    assert core_review_fingerprint(p) == row['reviewed_content_hash']
    actual = requirement_profile(p, include_course_ids=True)
    check_expectations(row['expected_profile'], actual, p['id'], 'Proposed bounded core')
    for role, ids in row['expected_course_ids'].items():
        if ids is not None:
            assert set(ids) == set(actual['course_ids'][role])
    subset = row['checked_subject_subset']
    courses = {c['id']: c for c in p['courses']}
    assert subset['count'] == len(set(subset['course_ids']))
    counts = Counter(courses[cid]['category'] for cid in subset['course_ids'])
    assert all(counts[category] == n for category, n in subset['categories'].items())
    assert not row['full_degree_verified']


def test_unreadable_usf_major_cannot_be_certified_by_readable_course_descriptions():
    row = ROWS[0]
    assert row['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert row['dimensions']['choice_rules']['status'] == 'unverified'
    assert all(value is None for value in row['expected_course_ids'].values())
    assert all(value is None for value in row['expected_profile'].values())
    assert row['checked_subject_subset']['role_membership_verified'] is False
    assert row['checked_subject_subset']['count'] == 29


def test_wm_conflicting_example_is_not_a_rename_or_fixed_pool():
    row = ROWS[1]
    assert row['dimensions']['fixed_requirements']['status'] == 'partial'
    assert row['expected_course_ids']['required'] == [
        'wm-applied-ai-data-201', 'wm-applied-ai-data-202', 'wm-applied-ai-data-305']
    limits = ' '.join(row['dimensions']['fixed_requirements']['limitations'])
    assert 'AAI301' in limits and 'PHIL150' in limits
    assert row['expected_course_ids']['options'] is None
    assert row['expected_profile']['required']['count'] == 3


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['program_id'])
def test_optional_actual_source_captures_match_recorded_hashes(row):
    captures = row['source_captures']
    if any(not (ROOT / capture['path']).exists() for capture in captures):
        pytest.skip('Private permitted source captures are optional')
    for capture in captures:
        assert hashlib.sha256((ROOT / capture['path']).read_bytes()).hexdigest() == capture['sha256']
