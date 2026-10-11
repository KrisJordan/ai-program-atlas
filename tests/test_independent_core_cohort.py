"""Independent source-transcribed core expectations, with explicit partial scopes."""
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint, validate_core_review, check_expectations
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = {e['program_id']: e for e in json.loads((ROOT / 'research/degree-audit/independent-core-cohort.json').read_text())['programs']}
RIT = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
RICE = 'rice-university-artificial-intelligence-bs-degree'
NW = 'northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'
BUS = 'wpi-business-analytics-applied-ai-bs'


def load(pid):
    p = json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())
    assert not p.get('family')
    return resolve_program(p)


@pytest.mark.parametrize('pid', sorted(ENTRIES))
def test_manual_fixed_identities_categories_and_pinned_scope(pid):
    p, e = load(pid), ENTRIES[pid]
    validate_core_review(e, pid)
    assert e['reviewed_content_hash'] == core_review_fingerprint(p)
    assert not e['full_degree_verified']
    actual = requirement_profile(p, include_course_ids=True)
    check_expectations(e['expected_profile'], actual, pid, 'Independent source core')
    for role, expected in e['expected_course_ids'].items():
        if expected is not None:
            assert set(expected) == set(actual['course_ids'][role])
    courses = {c['id']: c for c in p['courses']}
    for cid, category in e['manual_fixed_categories'].items():
        assert courses[cid]['category'] == category
    for cid, category in e.get('manual_option_categories', {}).items():
        assert courses[cid]['category'] == category
    assert set(e.get('reviewed_option_subset', [])) <= set(actual['course_ids']['options'])


def test_authorship_boundary_and_no_full_chart_inference():
    assert len(ENTRIES) == 10
    assert sum(len(e['manual_fixed_categories']) for e in ENTRIES.values()) == 98
    assert not any('northeastern' in pid for pid in ENTRIES)
    for pid, e in ENTRIES.items():
        assert e['dimensions']['fixed_requirements']['status'] == 'verified'
        if pid != RICE:
            assert e['expected_profile']['options'] is None
            assert e['expected_profile']['unresolved'] is None
            assert e['expected_course_ids']['options'] is None
            assert e['dimensions']['classification']['status'] == 'partial'
            assert e['dimensions']['choice_rules']['status'] == 'partial'


def test_cmu_probability_paths_are_complete_alternative_bundles():
    p = load('cmu-bs-ai'); r = {r['id']: r for r in p['requirements']}
    root = r['cmu-bs-ai-math-probability']
    assert (root['kind'], root['count']) == ('alternative', 1)
    expected = [
        {'cmu-36-218'}, {'cmu-15-259'}, {'cmu-21-325', 'cmu-36-226'},
        {'cmu-21-425', 'cmu-36-226'}, {'cmu-36-225', 'cmu-36-226'},
        {'cmu-36-235', 'cmu-36-236'},
    ]
    for i, ids in enumerate(expected, 1):
        child = r[f'cmu-bs-ai-math-probability-{i}']
        assert child['parent_id'] == root['id'] and child['kind'] == 'all'
        assert set(child['course_ids']) == ids
    assert r['cmu-bs-ai-programming-prerequisite']['kind'] == 'note'
    assert r['cmu-bs-ai-programming-prerequisite']['course_ids'] == ['cmu-15-112']


def test_penn_ai_core_and_optional_concentration_are_not_fixed():
    p = load('penn-bse-ai'); r = {r['id']: r for r in p['requirements']}
    children = [v for v in r.values() if v.get('parent_id') == 'penn-bse-ai-ai-core-6-cus']
    assert len(children) == 6
    assert all(v['kind'] == 'choose_credits' and v['credits'] == 1 for v in children)
    assert r['penn-bse-ai-optional-concentrations']['kind'] == 'note'
    for key in ['robotics', 'machine-learning', 'vision-language']:
        row = r['penn-bse-ai-optional-' + key]
        assert row['count'] == 4 and row['parent_id'] == 'penn-bse-ai-optional-concentrations'
    project = next(v for v in children if 'ai-project' in v['id'])
    assert '30%' in project['title']
    assert {'penn-ese-4210', 'penn-cis-5810', 'penn-cis-5300'} <= set(project['course_ids'])


def test_rit_fresh_table_six_pairs_and_nested_robotics():
    p = load(RIT); r = {r['id']: r for r in p['requirements']}
    expected = {0: ['gcis-123', 'csci-141'], 5: ['gcis-124', 'csci-142'], 8: ['math-190', 'math-200'], 14: ['comm-142', 'comm-201'], 24: ['iste-230', 'swen-344'], 25: ['ling-351', 'ling-581']}
    for index, suffixes in expected.items():
        row = r[f'{RIT}-sequence-{index}']
        assert row['kind'] == 'choose_courses' and row['count'] == 1
        assert set(row['course_ids']) == {RIT + '-' + s for s in suffixes}
    elective = r[RIT + '-ai-electives']
    assert (elective['kind'], elective['count'], elective['credits']) == ('choose_courses', 2, 6)
    children = [v for v in r.values() if v.get('parent_id') == elective['id']]
    robotics = next(v for v in children if RIT + '-eeee-485' in v.get('course_ids', []))
    assert set(robotics['course_ids']) == {RIT + '-eeee-485', RIT + '-csci-634'}
    assert robotics['kind'] in {'alternative', 'choose_courses'}
    courses = {c['code']: c for c in p['courses']}
    assert courses['IDAI-499']['credits'] == courses['YOPS-10']['credits'] == 0
    assert courses['IDAI-360']['category'] == 'mathematics'
    assert courses['IDAI-490']['category'] == 'foundations'
    assert len(ENTRIES[RIT]['reviewed_option_subset']) == 17


def test_rice_all_represented_choices_and_reciprocal_identities():
    p = load(RICE); r = {r['id']: r for r in p['requirements']}
    assert r['rice-ai-r14']['kind'] == 'alternative'
    assert set(r['rice-ai-r15']['course_ids']) == {'rice-ai-stat-310', 'rice-ai-stat-314'}
    assert set(r['rice-ai-r16']['course_ids']) == {'rice-ai-stat-311', 'rice-ai-stat-314'}
    assert r['rice-ai-r15']['parent_id'] == r['rice-ai-r16']['parent_id'] == 'rice-ai-r14'
    expected = {
        frozenset({'rice-ai-stat-315', 'rice-ai-dsci-301'}),
        frozenset({'rice-ai-comp-447', 'rice-ai-elec-447'}),
        frozenset({'rice-ai-comp-450', 'rice-ai-elec-450', 'rice-ai-mech-450'}),
    }
    assert {frozenset(g['course_ids']) for g in p['course_identity_groups']} == expected
    assert len(p['courses']) == 43
    assert ENTRIES[RICE]['expected_profile']['options']['count'] == 26
    assert ENTRIES[RICE]['expected_profile']['options']['categories'] == {'mathematics': 14, 'foundations': 3, 'applications': 1, 'human_context': 1, 'ai_ml': 5, 'other': 2}


def test_mit_versioned_fixed_math_and_complete_programming_bundles():
    p = load('mit-ai-decision-making-bs'); r = {r['id']: r for r in p['requirements']}
    bundles = [v for v in r.values() if v.get('parent_id') == 'mit-ai-v2025-programming']
    expected = [['6-1000'], ['6-100a', '16-c20'], ['6-100a', '18-c20'], ['6-100a', '6-100b'], ['6-100a', '9-c20']]
    assert {frozenset(v['course_ids']) for v in bundles} == {frozenset('mit-ai-v2025-' + c for c in row) for row in expected}
    assert r['mit-ai-v2025-centers']['count'] == 5
    for names in [('6-c01', '6-c011'), ('6-c51', '6-c511')]:
        assert any(v.get('parent_id') == 'mit-ai-v2025-centers' and set(v['course_ids']) == {'mit-ai-v2025-' + c for c in names} for v in r.values())
    assert ENTRIES[p['id']]['manual_fixed_categories']['mit-ai-v2025-6-1200'] == 'mathematics'


def test_northwestern_breadth_is_five_domains_not_all_six():
    p = load(NW); r = {r['id']: r for r in p['requirements']}
    assert r['nw-bse-r17']['kind'] == 'choose_courses' and r['nw-bse-r17']['count'] == 5
    children = [v for v in r.values() if v.get('parent_id') == 'nw-bse-r17']
    assert len(children) == 6 and all(v['kind'] == 'alternative' for v in children)
    fixed = set(ENTRIES[NW]['expected_course_ids']['required'])
    assert 'nw-bse-math-228-1' not in fixed and 'nw-bse-physics-135-1' not in fixed
    assert {'nw-bse-dsgn-106-1', 'nw-bse-dsgn-106-2', 'nw-bse-english-106-1', 'nw-bse-english-106-2'} <= fixed


@pytest.mark.parametrize('award', ['ba', 'bs'])
def test_case_intro_python_or_complete_java_python_pair(award):
    pid = f'case-western-reserve-university-artificial-intelligence-{award}-degree'
    p = load(pid); rows = p['requirements']; prefix = 'case-' + award
    pair = next(r for r in rows if set(r['course_ids']) == {prefix + '-csds-132', prefix + '-csds-237'})
    single = next(r for r in rows if r['course_ids'] == [prefix + '-csds-134'])
    assert pair['kind'] == single['kind'] == 'all' and pair['parent_id'] == single['parent_id']
    parent = next(r for r in rows if r['id'] == pair['parent_id'])
    assert parent['kind'] == 'alternative'
    assert not set(pair['course_ids'] + single['course_ids']) & set(ENTRIES[pid]['expected_course_ids']['required'])


def test_wpi_manual_closed_ds_sequence_and_open_business_equivalents_differ():
    p = load('wpi-ai-bs'); r = {r['id']: r for r in p['requirements']}
    ds = r['wpi-ai-bs-core-ai-foundations']
    assert ds['kind'] == 'all' and set(ds['course_ids']) == {'wpi-ds-1010', 'wpi-ds-2010', 'wpi-ds-3010'}
    assert r['wpi-ai-bs-core-selection-total']['credits'] == pytest.approx(8 / 3)
    p = load(BUS); r = {r['id']: r for r in p['requirements']}
    account = r[BUS + '-business-2']
    assert account['kind'] == 'choose_courses' and account['course_ids'] == ['wpi-acc-2060']
    assert 'equivalent' in account['summary'].lower()
    assert ENTRIES[BUS]['expected_course_ids']['required'] == []
    assert r[BUS + '-electives']['count'] == 6
