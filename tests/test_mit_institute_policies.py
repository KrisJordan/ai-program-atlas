"""Scope and version boundaries for the linked MIT institute/department sources."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
from atlas.requirements import validate_requirements

ROOT = Path(__file__).resolve().parents[1]
POLICIES = importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.policies')

def fixture(name):
    return (ROOT/'tests/fixtures/mit_ncsu'/name).read_text()


def test_science_choices_and_metadata_missingness():
    d = POLICIES.parse_gir(fixture('mit-gir.html'))
    validate_requirements(d)
    choices = [r for r in d['requirements'] if r['kind'] == 'choose_courses']
    assert len(choices) == 6 and all(r['count'] == 1 for r in choices)
    assert all(c['name'] is None and c['credits'] == 12 for c in d['courses'])
    # The bare GIR table has no content review; science is not computing foundations.
    assert all(c['category'] == 'other' for c in d['courses'])
    assert {c['code'] for c in d['courses']} == {'7.012', '3.091', '18.01', '18.02', '8.01', '8.02'}
    assert not {'curriculum_status', 'curriculum_audit', 'last_verified'} & d.keys()


def test_transfer_pe_and_open_hass_criteria_are_policies_not_extra_course_pools():
    rules = {r['id']: r for r in POLICIES.parse_gir(fixture('mit-gir.html'))['requirements']}
    pe = rules['mit-ai-institute-pe']
    assert 'eight points' in pe['summary'] and 'four points' in pe['summary']
    assert 'not academic units' in pe['summary']
    assert rules['mit-ai-institute-hass-distribution']['kind'] == 'note'
    assert not rules['mit-ai-institute-hass-distribution']['course_ids']
    assert 'not invent a fixed course list' in rules['mit-ai-institute-hass-distribution']['summary']
    with pytest.raises(ValueError):
        POLICIES.parse_gir(fixture('mit-gir.html').replace('four points (two courses)', 'six points (three courses)'))


def test_institute_pane_guard_prevents_navigation_or_wrong_section_evidence():
    html = fixture('mit-gir.html').replace('id="sciencerequirementtextcontainer"', 'id="unrelated"')
    with pytest.raises(ValueError):
        POLICIES.parse_gir(html)


def test_versioned_cim2_is_scoped_and_does_not_infer_credit_totals_or_launch_date():
    d = POLICIES.parse_versioned(fixture('mit-versioned.html'))
    validate_requirements(d)
    assert {c['code'] for c in d['courses']} == {'6.3930', '6.4300'}
    assert all(c['credits'] is None for c in d['courses'])
    assert d['courses'][1]['prerequisites'] == 'Prereqs/[Coreqs]: [synthetic corequisite]'
    assert 'first_offered' not in d and 'catalog_year' not in d
    rules = {r['id']: r for r in d['requirements']}
    assert 'at most one required subject slot' in rules['mit-ai-version-reuse']['summary']
    assert rules['mit-ai-version-math']['course_ids'] == []
    assert 'non-calculus' in rules['mit-ai-version-math']['summary']
    assert 'not a fabricated finite list' in rules['mit-ai-version-math']['summary']


@pytest.mark.parametrize('old,new', [('Fall 2025 or later', 'Fall 2026 or later'), ('name="CIM2"', 'name="Other"'), ('non-calculus', 'any calculus')])
def test_version_or_eligibility_changes_require_review(old, new):
    with pytest.raises(ValueError):
        POLICIES.parse_versioned(fixture('mit-versioned.html').replace(old, new))


def test_cap_standing_is_not_universal_graduation_gpa_and_ie_is_distinct():
    html = '<main><h1>Academic Performance and Grades</h1><p>Synthetic rules: does not establish rigid standards; at least 36 units of credit; term rating above 3.0; individual basis. D: Minimally acceptable performance; may retake the prerequisite. P means performance at the level A, B, or C. First-Year Pass/No Record. All grades of Incomplete must be resolved prior to graduation. No grade of I can be assigned in the final term. IE does not carry credit but need not be resolved.</p></main>'
    d = POLICIES.parse_grades(html)
    assert 'rather than an automatic graduation GPA cutoff' in d['requirements'][0]['summary']
    assert 'separate financial-aid rule' in d['requirements'][0]['summary']
    assert 'IE notation carries no credit' in d['requirements'][2]['summary']


def test_curated_scope_audit_exposes_version_reconciliation():
    d = json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    validate_program(d)
    assert d['curriculum_status'] == 'partial' and d['catalog_year'] is None
    assert d['first_offered'] is None
    assert any('6-4_2025' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
    assert next(c for c in d['courses'] if c['code'] == '6.4300')['credits'] is None
    assert d['outcomes'][0]['statement_type'] == 'program_aim'
