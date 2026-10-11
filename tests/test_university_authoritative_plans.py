"""New independent draft evidence must not become adopted-plan certification."""
import hashlib
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / 'research/university-core-followup-authoritative-plans.json').read_text())
ROWS = LEDGER['programs']


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['program_id'])
def test_proposals_match_exact_resolved_facts(row):
    program = resolve_program(json.loads((ROOT / 'data/programs' / (row['program_id'] + '.json')).read_text()))
    validate_core_review(row, program['id'])
    assert core_review_fingerprint(program) == row['reviewed_content_hash']
    profile = requirement_profile(program, include_course_ids=True)
    check_expectations(row['expected_profile'], profile, program['id'], 'Draft-bound proposal')
    for role, ids in row['expected_course_ids'].items():
        if ids is not None:
            assert set(ids) == set(profile['course_ids'][role])
    assert row['full_degree_verified'] is False


def test_stevens_draft_is_partial_with_named_scope_not_governing_authority():
    row = ROWS[0]
    fixed = row['dimensions']['fixed_requirements']
    assert fixed['status'] == 'partial'
    assert 'UNOFFICIAL DRAFT' in fixed['summary'] and 'Workday' in fixed['summary']
    assert row['adopted_plan_verified'] is False
    assert row['expected_profile']['required']['count'] == 24
    assert row['expected_profile']['required']['categories']['foundations'] == 6
    assert row['expected_course_ids']['options'] is None
    assert row['expected_profile']['options'] is None
    choices = row['checked_choice_subsets']
    assert choices['science_sequences'][4] == ['CH115', 'BIO181', ['CH117', 'BIO182']]
    assert len(choices['science_sequences']) == 6
    assert len(choices['technical_codes']) == 11
    assert choices['frontiers_named_pool'] is None
    assert choices['positive_named_option_identity_count'] == 22
    assert {'EN250', 'CE240', 'NANO200', 'MA503'} <= set(choices['science_math_excluded_codes'])
    assert choices['source_conflicts'][0]['resolution'] is None
    assert 'additional_science_math_codes' not in choices
    assert 'CPE558' not in choices['technical_codes']
    assert sum(choices['draft_term_credits']) == choices['draft_term_credit_sum'] == 125
    assert choices['normalized_credit_unit'] is None


@pytest.mark.parametrize('row', ROWS[1:], ids=lambda row: row['program_id'])
def test_unreadable_governing_inventory_keeps_null_roles(row):
    assert row['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert row['dimensions']['choice_rules']['status'] == 'unverified'
    assert all(value is None for value in row['expected_course_ids'].values())
    assert all(value is None for value in row['expected_profile'].values())


def test_optional_actual_new_pdf_and_browser_captures():
    captures = [c for c in ROWS[0]['source_captures'] if c.get('evidence_kind') in {
        'actual_public_pdf_unofficial_draft', 'actual_browser_screenshot',
        'actual_reader_extraction_not_pdf_bytes'}]
    assert len(captures) == 5
    for capture in captures:
        path = Path(capture['path'])
        if not path.exists():
            pytest.skip('Private actual source captures are optional')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == capture['sha256']
    pdf = next(c for c in captures if c['evidence_kind'] == 'actual_public_pdf_unofficial_draft')
    assert Path(pdf['path']).read_bytes().startswith(b'%PDF')


def test_catalog_membership_claim_preserves_explicit_draft_eligibility_conflict():
    pid = ROWS[0]['program_id']
    program = json.loads((ROOT / 'data/programs' / (pid + '.json')).read_text())
    disputed = {'stevens-en-250', 'stevens-ce-240', 'stevens-nano-200'}
    rules = {rule['id']: rule for rule in program['requirements']}
    catalog = rules[pid + '-math-science-electives']
    assert catalog['kind'] == 'choose_courses' and catalog['count'] == 2
    assert set(catalog['course_ids']) == disputed
    assert 'Catalog claim' in catalog['summary'] and 'eligibility is resolved' in catalog['summary']
    conflict = rules[pid + '-fall-2026-math-science-conflict']
    assert conflict['kind'] == 'note'
    assert conflict['source_id'] == pid + '-fall-2026-draft-advising-plan'
    assert set(conflict['course_ids']) == disputed
    assert 'instead excludes' in conflict['summary'] and 'UNOFFICIAL DRAFT' in conflict['summary']
    assert all(any('Eligibility source conflict' in note for note in course['notes'])
               for course in program['courses'] if course['id'] in disputed)
    source = next(source for source in program['sources'] if source['id'] == conflict['source_id'])
    assert 'advising only' in source['title'] and 'Workday' in source['locator']
