"""Preserve honest planning-source applicability and bounded review ownership."""
import hashlib
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = json.loads((ROOT / 'research/university-core-followup-plan-conflicts.json').read_text())
ROWS = {row['program_id']: row for row in PROPOSAL['programs']}


@pytest.mark.parametrize('pid', sorted(ROWS))
def test_complete_rows_pin_resolved_facts_and_preserve_prior_bounded_sets(pid):
    row = ROWS[pid]
    program = resolve_program(json.loads((ROOT / f'data/programs/{pid}.json').read_text()))
    prior = next(p for p in json.loads((ROOT / row['prior_review_file']).read_text())['programs']
                 if p['program_id'] == pid)
    validate_core_review(row, pid)
    assert core_review_fingerprint(program) == row['reviewed_content_hash']
    actual = requirement_profile(program, include_course_ids=True)
    check_expectations(row['expected_profile'], actual, pid, 'Plan-conflict proposal')
    for role, ids in row['expected_course_ids'].items():
        if ids is not None:
            assert set(ids) == set(actual['course_ids'][role])
    assert row['expected_course_ids'] == prior['expected_course_ids']
    assert row['expected_profile'] == prior['expected_profile']
    assert {k: d['status'] for k, d in row['dimensions'].items()} == {
        k: d['status'] for k, d in prior['dimensions'].items()}
    assert not row['full_degree_verified']
    assert not row['hierarchy_and_version']['governing_inventory_verified']
    assert PROPOSAL['proposal_only']


def test_new_governance_and_blank_form_do_not_certify_wm_course_equivalence():
    row = ROWS['william-mary-applied-ai-ba']
    assert row['dimensions']['fixed_requirements']['status'] == 'partial'
    assert 'AAI301' in row['hierarchy_and_version']['not_established']
    assert 'PHIL150' in row['hierarchy_and_version']['not_established']
    assert any(s['new_to_followup'] and 'bylaws' in s['url'] for s in row['followup_sources'])
    assert any('blank' in s['finding'] for s in row['followup_sources'] if s['url'].endswith('.pdf'))


def test_delaware_sample_and_purdue_aggregate_do_not_become_complete_cores():
    delaware = ROWS['delaware-ai-engineering-major']
    assert delaware['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert delaware['expected_course_ids']['required'] == []
    assert len(delaware['expected_course_ids']['unresolved']) == 28
    purdue = ROWS['purdue-ai-ba']
    assert purdue['dimensions']['fixed_requirements']['status'] == 'partial'
    assert len(purdue['expected_course_ids']['required']) == 5
    assert not any(s['new_to_followup'] for s in purdue['followup_sources'])


@pytest.mark.parametrize('pid', sorted(ROWS))
def test_optional_actual_followup_captures_match_hashes(pid):
    captures = ROWS[pid]['followup_sources']
    if not all((ROOT / c['saved_source_path']).exists() for c in captures):
        pytest.skip('Optional ignored public-source captures unavailable')
    for capture in captures:
        assert hashlib.sha256((ROOT / capture['saved_source_path']).read_bytes()).hexdigest() == capture['saved_source_sha256']
