"""Independent, source-enumerated core identities with honest unchecked scopes."""
import json
from pathlib import Path

import pytest

from atlas.course_identity import identity_map
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / 'research/degree-audit/independent-core-other.json').read_text())


def program(pid):
    return resolve_program(json.loads((ROOT / 'data/programs' / (pid + '.json')).read_text()))


@pytest.mark.parametrize('review', LEDGER['programs'], ids=lambda e: e['program_id'])
def test_manual_core_sets_and_totals_match_pinned_resolved_graph(review):
    p = program(review['program_id'])
    validate_core_review(review, p['id'])
    assert core_review_fingerprint(p) == review['reviewed_content_hash']
    actual = requirement_profile(p, include_course_ids=True)
    check_expectations(review['expected_profile'], actual, p['id'], 'Independent core')
    for role, ids in review['expected_course_ids'].items():
        if ids is not None:
            assert len(ids) == len(set(ids))
            assert set(ids) == set(actual['course_ids'][role])
    if 'reviewed_option_subset' in review:
        assert len(review['reviewed_option_subset']) == 27
        assert set(review['reviewed_option_subset']) <= set(actual['course_ids']['options'])
    assert not review['full_degree_verified']


def test_unavailable_sources_are_not_certified_as_zero():
    by = {e['program_id']: e for e in LEDGER['programs']}
    for pid in ['uc-merced-ai-bs',
                'stevens-institute-of-technology-artificial-intelligence-bs-degree',
                'university-of-south-florida-artificial-intelligence-bs-degree']:
        e = by[pid]
        assert e['dimensions']['fixed_requirements']['status'] == 'unverified'
        assert e['expected_course_ids']['required'] is None
        assert e['expected_profile']['required'] is None
    # GE and other broad pools were deliberately not source-reviewed here.
    assert all(e['expected_course_ids']['unresolved'] is None for e in by.values())
    assert all(e['expected_profile']['options'] is None or
               e['expected_profile']['options']['categories'] is None for e in by.values())


def test_source_reported_classification_corrections_remain_visible():
    njit = program('new-jersey-institute-of-technology-business-with-ai-bs-degree')
    course = next(c for c in njit['courses'] if c['code'] == 'MGMT 422')
    assert course['category'] == 'other'
    assert course['category_review']['status'] == 'mixed'
    assert set(course['category_review']['candidate_categories']) == {'applications', 'human_context'}
    usf = program('university-of-south-florida-artificial-intelligence-bs-degree')
    course = next(c for c in usf['courses'] if c['code'] == 'PSY 2012')
    assert course['category'] == 'applications'
    assert course['category_review']['status'] == 'reviewed'


def test_conditional_routes_do_not_promote_named_options():
    by = {e['program_id']: e for e in LEDGER['programs']}
    checks = {
        'miami-data-science-ai-bs': ['MTH 309', 'MTH 230', 'CSC 410'],
        'miami-ai-technologies-business-bsba': ['ACC 211', 'ACC 221', 'BTE 413', 'MAS 548'],
        'university-of-maryland-college-park-human-centered-ai-ba-degree': ['GVPT170', 'HCAI490'],
        'drexel-ai-ml-bs': ['CS 171', 'ECE 105', 'CI 491', 'ECE 491'],
    }
    for pid, codes in checks.items():
        p = program(pid)
        mapping = identity_map(p)
        options = set(by[pid]['expected_course_ids']['options'])
        fixed = set(by[pid]['expected_course_ids']['required'])
        for code in codes:
            c = next(c for c in p['courses'] if c['code'] == code)
            assert mapping[c['id']] in options
            assert mapping[c['id']] not in fixed
