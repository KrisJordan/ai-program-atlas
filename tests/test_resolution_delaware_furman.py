"""Resolution proposals preserve evidence boundaries and manual missingness."""
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = json.loads((ROOT / 'research/degree-audit/independent-resolution-delaware-furman.json').read_text())
ROWS = {p['program_id']: p for p in PROPOSAL['programs']}


@pytest.mark.parametrize('pid', ['delaware-ai-engineering-major', 'furman-ai-bs'])
def test_complete_proposals_pin_current_graph_without_certifying_empty_core(pid):
    row = ROWS[pid]
    program = json.loads((ROOT / f'data/programs/{pid}.json').read_text())
    validate_core_review(row, pid)
    assert row['reviewed_content_hash'] == core_review_fingerprint(program)
    check_expectations(row['expected_profile'], requirement_profile(program), pid, 'Resolution proposal')
    assert row['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert not row['full_degree_verified']
    assert all(b['access_status'].endswith('_not_retried') for b in row['checked_boundaries'])
    assert PROPOSAL['proposal_only'] is True


def test_delaware_manual_categories_and_context_enumeration_are_exhaustive():
    row = ROWS['delaware-ai-engineering-major']
    sets = row['manual_category_course_ids']
    all_ids = [cid for values in sets.values() for cid in values]
    assert len(all_ids) == len(set(all_ids)) == 28
    assert set(all_ids) == set(row['expected_course_ids']['unresolved'])
    assert {category: len(ids) for category, ids in sets.items()} == {
        'foundations': 2, 'mathematics': 7, 'ai_ml': 3, 'human_context': 2, 'other': 14,
    }
    assert row['expected_course_ids']['required'] == row['expected_course_ids']['options'] == []
    assert any('2025' in s['url'] for s in row['sources'])
    assert 'cohort' in ' '.join(row['dimensions']['fixed_requirements']['limitations'])


def test_furman_introductory_ai_themes_do_not_establish_degree_obligations():
    row = ROWS['furman-ai-bs']
    assert row['manual_category_course_ids'] is None
    assert len(row['sources']) == 4
    assert any('introductory-courses' in s['url'] for s in row['sources'])
    for role in ['required', 'options', 'unresolved']:
        assert row['expected_course_ids'][role] == []
        assert row['expected_profile'][role] == {'count': 0, 'categories': None}
    assert all(d['status'] == 'unverified' for d in row['dimensions'].values())
