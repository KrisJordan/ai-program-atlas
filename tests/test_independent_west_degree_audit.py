"""Independent source-enumerated identities and conditional-load regressions.

No captured copyrighted page is embedded. The ledger contains manually transcribed
identifiers; subject examples are supported by independently reread descriptions.
"""
import json
from copy import deepcopy
from pathlib import Path

import pytest

from atlas import db
from atlas.course_identity import identity_map
from atlas.curriculum_profile import requirement_profile
from tests.test_core_review import conn  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / 'research/degree-audit/independent-west.json').read_text())
RIT = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
IST = 'penn-state-ai-methods-applications-ist-bs'
ENG = 'penn-state-ai-engineering-bs'


def load(pid):
    return json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())


def entry(pid):
    return next(p for p in LEDGER['programs'] if p['program_id'] == pid)


def reviewed_inventory(p, e):
    """Apply only an explicitly declared historical review boundary."""
    if e.get('expected_inventory_scope') != 'explicit_reviewed_course_subset':
        return p
    expected = set().union(*(set(ids) for ids in e['expected_course_ids'].values()))
    mapped = identity_map(p)
    assert expected <= set(mapped.values()), 'An independently reviewed course was removed'
    return {**p, 'courses': [c for c in p['courses'] if mapped[c['id']] in expected],
            'course_identity_groups': [g for g in p.get('course_identity_groups', [])
                                      if g['canonical_course_id'] in expected]}


@pytest.mark.parametrize('pid', [RIT, ENG, IST])
def test_declared_review_scope_matches_independently_transcribed_source_sets(pid):
    p = load(pid)
    before = deepcopy(p)
    e = entry(pid)
    scoped = reviewed_inventory(p, e)
    mapped = identity_map(scoped)
    result = requirement_profile(scoped)
    expected = e['expected_course_ids']
    assert set().union(*(set(ids) for ids in expected.values())) == set(mapped.values())
    for role, ids in expected.items():
        assert result[role]['count'] == len(ids) == e['expected_profile'][role]['count']
        # Keep all aliases of one identity together while isolating its role.
        for cid in ids:
            isolated = {**scoped, 'courses': [c for c in scoped['courses'] if mapped[c['id']] == cid],
                        'course_identity_groups': [g for g in p.get('course_identity_groups', [])
                                                   if g['canonical_course_id'] == cid]}
            single = requirement_profile(isolated)
            assert single[role]['count'] == 1
            assert sum(single[k]['count'] for k in expected) == 1
    assert p == before
    assert not e['full_degree_verified']
    assert e['second_pass_status'] == 'partial'


def test_rit_original_independent_card_partition_and_mixed_semantics():
    p = load(RIT)
    result = requirement_profile(reviewed_inventory(p, entry(RIT)))
    for role, expected in entry(RIT)['expected_profile'].items():
        assert result[role]['categories'] == expected['categories']
    courses = {c['code']: c for c in p['courses']}
    # Subject is derived from content, not the AI title or course-menu location.
    for code, subject in {'ISTE-230': 'systems', 'SWEN-344': 'foundations',
                          'SWEN-566': 'foundations', 'CSCI-634': 'ai_ml',
                          'PSYC-223': 'applications', 'GCIS-350': 'human_context'}.items():
        assert courses[code]['category'] == subject
        assert courses[code]['category_review']['status'] == 'reviewed'
    for code in ['ISTE-476', 'LING-351', 'EEEE-485']:
        assert courses[code]['category'] == 'other'
        assert courses[code]['category_review']['status'] == 'mixed'
    for code in ['YOPS-10', 'IDAI-499']:
        assert courses[code]['category_review']['status'] == 'unclassified'
    assert 'EEEE-346' in courses['EEEE-485']['prerequisites']
    assert 'EEEE-346' not in courses  # Conditional option preparation is not universal.
    assert 'instructor approval' in courses['LING-581']['prerequisites']


def test_rit_known_zero_obligations_round_trip_without_erasing_unknowns(conn):
    p = load(RIT)
    assert db.ingest_program(conn, p)
    assert not db.ingest_program(conn, p)
    saved = next(x for x in db.export_data(conn)['programs'] if x['id'] == RIT)
    courses = {c['code']: c for c in saved['courses']}
    for code in ['YOPS-10', 'IDAI-499']:
        assert courses[code]['credits'] == 0
        rows = [r for r in saved['requirements'] if courses[code]['id'] in r['course_ids']
                and r['kind'] == 'all']
        assert rows and all(r['credits'] == 0 for r in rows)
    preparation = next(r for r in saved['requirements'] if r['id'] == RIT + '-prep')
    assert preparation['credits'] == 0 and not preparation['course_ids']
    assert sum(c['code'] == 'IDAI-499' for c in saved['courses']) == 1
    # Unquantified policy notes stay unknown; the advising PDF gives LING-584 3 credits.
    policy = next(r for r in saved['requirements'] if r['id'] == RIT + '-policy-grading')
    assert policy['credits'] is None
    assert courses['LING-584']['credits'] == 3 and courses['LING-584']['description'] is None
    assert requirement_profile(saved)['required']['count'] == 23
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_psu_full_option_identity_union_retains_unproved_slash_pairs(conn):
    p = load(IST)
    e = entry(IST)
    raw = set(e['expected_source_course_ids']['options'])
    components = e['manual_option_components']
    independently_listed = set(components['core_choices'] + components['technical_named_pool'])
    independently_listed.update(x for pool in components['application_focus_named_pools'].values() for x in pool)
    assert raw == independently_listed and len(raw) == 160
    actual = {frozenset(g['course_ids']) for g in p['course_identity_groups']}
    assert actual == {frozenset(pair) for pair in e['verified_identity_pairs']}
    assert len(p['courses']) == 169
    assert requirement_profile(p)['identity'] == e['expected_identity']
    assert requirement_profile(p)['options']['source_record_count'] == 160
    for number in ['301', '302']:
        assert identity_map(p)['psu-ist-' + number] != identity_map(p)['psu-eti-' + number]
    codes = {c['code'] for c in p['courses']}
    assert not codes.intersection({'BA 241', 'BA 242', 'FIN 301', 'MGMT 301', 'MKTG 301', 'SCM 301'})
    assert db.ingest_program(conn, p)
    assert not db.ingest_program(conn, p)
    saved = db.export_data(conn)['programs'][0]
    assert saved['course_identity_groups'] == p['course_identity_groups']
    assert requirement_profile(saved)['identity'] == e['expected_identity']
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_psu_whole_programming_and_capstone_routes_stay_grouped():
    p = load(ENG)
    groups = {g['id']: g for g in p['requirements']}
    route = next(g for g in groups.values() if set(g['course_ids']) == {'psu-cmpsc-121', 'psu-ds-120'})
    assert route['kind'] == 'all'
    assert groups[route['parent_id']]['kind'] == 'alternative'
    siblings = [g for g in groups.values() if g['parent_id'] == route['parent_id']]
    assert {tuple(g['course_ids']) for g in siblings} == {('psu-cmpsc-131',), ('psu-cmpsc-121', 'psu-ds-120')}
    p = load(IST)
    groups = {g['id']: g for g in p['requirements']}
    route = next(g for g in groups.values() if set(g['course_ids']) == {'psu-aima-430', 'psu-aima-440'})
    assert route['kind'] == 'all'
    selection = groups[route['parent_id']]
    assert selection['kind'] == 'choose_credits' and selection['credits'] == 6
    assert selection['course_ids'] == ['psu-a-i-494']
    courses = {c['code']: c for c in p['courses']}
    assert 'AIMA 430' in courses['AIMA 440']['prerequisites']
    assert 'DS 305' in courses['A-I 370']['prerequisites']
    # A condition to enroll in a core course does not promote its candidate courses.
    assert 'psu-ds-305' in entry(IST)['expected_course_ids']['options']


def test_rice_registration_permission_does_not_certify_credit_or_whole_degree():
    e = entry('rice-university-artificial-intelligence-bs-degree')
    findings = {f['id']: f for f in e['policy_findings']}
    assert findings['statistics-prerequisite-routes']['classification'] == 'conditional_permission'
    vision = findings['vision-mutual-exclusion']
    assert vision['classification'] == 'conditional_permission'
    assert 'credit' in vision['unresolved_scope']
    assert 'not separate inventory blockers' in vision['unresolved_scope']
    assert len(e['blockers']) == 1
    assert 'https://registrar.rice.edu/students/common-errors' in vision['source_urls']
    assert 'https://registrar.rice.edu/students/reg_repeated_courses' in vision['source_urls']
    assert e['expected_profile'] is None  # A policy pass is not an all-course re-audit.
    assert e['second_pass_status'] == 'partial' and not e['full_degree_verified']


def test_rice_statistics_route_preparation_is_not_promoted_to_fixed_requirement():
    p = load('rice-university-artificial-intelligence-bs-degree')
    courses = {c['code']: c for c in p['courses']}
    for code in ['STAT 310', 'STAT 311', 'STAT 314', 'STAT 315']:
        isolated = {**p, 'courses': [courses[code]], 'course_identity_groups': []}
        profile = requirement_profile(isolated)
        assert profile['required']['count'] == 0
        assert profile['options']['count'] == 1
    for code in ['COMP 345', 'COMP 346']:
        assert 'STAT 315' in courses[code]['prerequisites']
    assert 'STAT 310' in courses['STAT 314']['prerequisites']
    # Credit exclusion is neither reciprocal cross-list proof nor a waiver.
    assert not any({courses['COMP 345']['id'], courses['COMP 447']['id']} <= set(g['course_ids'])
                   for g in p['course_identity_groups'])


def test_rice_residence_scope_is_not_rewritten_as_a_transfer_only_exception():
    e = entry('rice-university-artificial-intelligence-bs-degree')
    finding = next(f for f in e['policy_findings'] if f['id'] == 'summer-residence')
    assert finding['classification'] == 'unresolved_source_conflict'
    assert 'not a distinct stricter transfer-only policy' in finding['conclusion']
    assert len(finding['source_urls']) == 5
    assert any('/graduation-requirements/' in u for u in finding['source_urls'])
    assert any('/transfer-credit/' in u for u in finding['source_urls'])


def test_ne_mathematics_all34_source_roles_categories_and_credit_units():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree'
    p = load(pid)
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    before = deepcopy(p)
    resolved = resolve_program(p, family)
    e = entry(pid)
    decisions = e['manual_course_decisions']
    courses = {c['code']: c for c in resolved['courses']}
    assert set(decisions) == set(courses) and len(courses) == 34
    profile = requirement_profile(resolved)
    for role in ['required', 'options', 'unresolved']:
        assert profile[role]['count'] == e['expected_profile'][role]['count']
        assert profile[role]['categories'] == e['expected_profile'][role]['categories']
    for code, expected in decisions.items():
        course = courses[code]
        assert course['category'] == expected['category']
        assert course['credits'] == expected['credits']
        assert course['credit_unit'] == 'semester_hours'
        isolated = {**resolved, 'courses': [course]}
        assert requirement_profile(isolated)[expected['role']]['count'] == 1
    assert p == before
    assert 'CS 1800' not in courses and 'CS 1802' not in courses
    assert 'MATH 1341' in courses['MATH 1342']['prerequisites']
    for code in ['MATH 2321', 'MATH 2341']:
        assert courses[code]['prerequisites'] is None
    assert not e['full_degree_verified'] and e['second_pass_status'] == 'partial'


def test_ne_mathematics_source_loads_are_not_summed_as_a_student_schedule():
    pid = 'northeastern-university-artificial-intelligence-and-mathematics-bs-boston-bs-degree'
    rules = entry(pid)['source_load_rules']
    assert (rules['published_degree_hours'], rules['general_elective_hours']) == (130, 24)
    assert (rules['math_elective_count'], rules['math_elective_hours']) == (4, 16)
    assert rules['khoury_elective_hours'] == 12
    assert 'neither a source contradiction nor a corrected total' in rules['scope']


def test_ne_physics_all49_independent_course_decisions():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree'
    p = load(pid)
    before = deepcopy(p)
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    resolved = resolve_program(p, family)
    e = entry(pid)
    courses = {c['code']: c for c in resolved['courses']}
    assert set(courses) == set(e['manual_course_decisions']) and len(courses) == 49
    profile = requirement_profile(resolved)
    for role, expected in e['expected_profile'].items():
        assert profile[role]['count'] == expected['count']
        assert profile[role]['categories'] == expected['categories']
    for code, decision in e['manual_course_decisions'].items():
        course = courses[code]
        assert course['category'] == decision['category']
        assert course['credits'] == decision['credits']
        assert course['credit_unit'] == 'semester_hours'
        assert requirement_profile({**resolved, 'courses': [course]})[decision['role']]['count'] == 1
    assert not {'CS 1800', 'CS 1802', 'DS 4420'} & set(courses)
    assert p == before
    assert not e['full_degree_verified'] and e['second_pass_status'] == 'partial'


def test_ne_physics_whole_routes_zero_recitations_and_undergraduate_permission():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree'
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    p = resolve_program(load(pid), family)
    courses = {c['code']: c for c in p['courses']}
    groups = {g['id']: g for g in p['requirements']}
    for numbers in [('1161', '1162', '1163'), ('1191', '1192', '1193')]:
        ids = {courses['PHYS ' + n]['id'] for n in numbers}
        bundle = next(g for g in groups.values() if set(g['course_ids']) == ids)
        assert bundle['kind'] == 'all'
        assert groups[bundle['parent_id']]['kind'] == 'alternative'
        assert sum(courses['PHYS ' + n]['credits'] for n in numbers) == 5
    for code, role in [('PHYS 1163', 'options'), ('PHYS 1193', 'options'), ('PHYS 1167', 'required')]:
        assert courses[code]['credits'] == 0
        assert requirement_profile({**p, 'courses': [courses[code]]})[role]['count'] == 1
    for code, category, role in [('PHYS 5116', 'mathematics', 'options'),
                                  ('PHYS 5318', 'applications', 'required')]:
        assert courses[code]['category'] == category
        assert 'PHYS 2303' in courses[code]['prerequisites']
        assert 'or graduate program admission' in courses[code]['prerequisites']
        assert requirement_profile({**p, 'courses': [courses[code]]})[role]['count'] == 1
    for code in ['MATH 1365', 'MATH 1465']:
        assert requirement_profile({**p, 'courses': [courses[code]]})['options']['count'] == 1


def test_ne_physics_resolved_storage_preserves_reviewed_roles_and_known_zeros(conn):
    from atlas.family_store import ingest_family
    pid = 'northeastern-university-artificial-intelligence-and-physics-bs-boston-bs-degree'
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    with conn:
        db.upsert_institution(conn, load(pid)['institution'])
    ingest_family(conn, family)
    assert db.ingest_program(conn, load(pid))
    assert not db.ingest_program(conn, load(pid))
    saved = next(p for p in db.export_data(conn)['programs'] if p['id'] == pid)
    profile = requirement_profile(saved)
    assert (profile['required']['count'], profile['options']['count']) == (25, 24)
    courses = {c['code']: c for c in saved['courses']}
    assert all(courses[code]['credits'] == 0 for code in ['PHYS 1163', 'PHYS 1193', 'PHYS 1167'])
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_ne_linguistics_all45_independent_course_decisions_and_nonreuse():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree'
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    raw = load(pid)
    before = deepcopy(raw)
    p = resolve_program(raw, family)
    courses = {c['code']: c for c in p['courses']}
    e = entry(pid)
    assert set(courses) == set(e['manual_course_decisions']) and len(courses) == 45
    for role, expected in e['expected_profile'].items():
        actual = requirement_profile(p)[role]
        assert (actual['count'], actual['categories']) == (expected['count'], expected['categories'])
    for code, decision in e['manual_course_decisions'].items():
        course = courses[code]
        assert (course['category'], course['credits'], course['credit_unit']) == (
            decision['category'], decision['credits'], 'semester_hours')
        assert requirement_profile({**p, 'courses': [course]})[decision['role']]['count'] == 1
    group = next(g for g in p['requirements'] if g['id'].endswith('-req-linguistics-electives-course-choice'))
    assert group['kind'] == 'choose_courses' and group['count'] == 2
    assert 'not used to fulfill other degree requirements' in group['summary']
    assert e['source_load_rules']['linguistics_elective_nonreuse'] is True
    assert raw == before


def test_ne_linguistics_optional_preparation_and_variable_research_subjects():
    pid = 'northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree'
    p = load(pid)
    courses = {c['code']: c for c in p['courses']}
    for code in ['PSYC 4610', 'PSYC 4658']:
        assert 'PSYC 3464' in courses[code]['prerequisites']
        assert 'PSYC 3466' in courses[code]['prerequisites']
    assert 'AMSL 1102' in courses['DEAF 2700']['prerequisites']
    assert not {'AMSL 1102', 'PSYC 3464', 'PSYC 3466'} & set(courses)
    assert 'permission of instructor' in courses['LING 4654']['prerequisites']
    for code in ['LING 4654', 'LING 4891', 'LING 4991']:
        assert courses[code]['category'] == 'other'
        assert courses[code]['category_review']['status'] == 'unclassified'
    assert courses['PSYC 2320']['category'] == 'mathematics'
    assert courses['LING 3412']['category'] == 'human_context'
    assert courses['CS 4120']['category'] == 'ai_ml'
    assert not entry(pid)['full_degree_verified']


def test_ne_health_all52_independent_course_decisions():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree'
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    p = resolve_program(load(pid), family)
    courses = {c['code']: c for c in p['courses']}
    e = entry(pid)
    assert set(courses) == set(e['manual_course_decisions']) and len(courses) == 52
    for role, expected in e['expected_profile'].items():
        actual = requirement_profile(p)[role]
        assert (actual['count'], actual['categories']) == (expected['count'], expected['categories'])
    for code, decision in e['manual_course_decisions'].items():
        c = courses[code]
        assert (c['category'], c['credits'], c['credit_unit']) == (
            decision['category'], decision['credits'], 'semester_hours')
        assert requirement_profile({**p, 'courses': [c]})[decision['role']]['count'] == 1
    assert not e['full_degree_verified']


def test_ne_health_whole_statistics_route_recommendations_and_grade_scope():
    from atlas.families import resolve_program
    pid = 'northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree'
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    p = resolve_program(load(pid), family)
    courses = {c['code']: c for c in p['courses']}
    groups = {g['id']: g for g in p['requirements']}
    ids = {courses[code]['id'] for code in ['ENVR 2500', 'ENVR 2501', 'ENVR 2502']}
    route = next(g for g in groups.values() if set(g['course_ids']) == ids)
    assert route['kind'] == 'all' and groups[route['parent_id']]['kind'] == 'alternative'
    assert sum(courses[code]['credits'] for code in ['ENVR 2500', 'ENVR 2501', 'ENVR 2502']) == 5
    assert courses['ENVR 2502']['credits'] == 0 and courses['CHEM 1163']['credits'] == 0
    assert courses['PHTH 2350']['prerequisites'] is None
    assert 'PHTH 2300' not in courses['PHTH 4540']['prerequisites']
    assert 'ENGW 3302' in courses['PHTH 4540']['prerequisites']
    # The synopsis need not repeat every recommendation; required-prerequisite
    # metadata must not promote it into an enrollment obligation.
    grade = groups[pid+'-req-health-sciences-major-requirement-policy']['summary']
    assert 'PHTH core, statistics, and science requirements' in grade
    assert 'HSCI 1000 and HSCI 2000' in grade
    concurrent = groups[pid+'-req-cs-1802-concurrent']
    assert concurrent['course_ids'] == [courses['CS 1802']['id']]
    assert courses['CS 1800']['id'] in groups[concurrent['parent_id']]['course_ids']


def test_ne_health_fresh_export_and_render_match_manual_profile(conn, tmp_path):
    from bs4 import BeautifulSoup
    from atlas.family_store import ingest_family
    from atlas.site import build
    pid = 'northeastern-university-artificial-intelligence-and-health-science-bs-boston-bs-degree'
    raw = load(pid)
    family = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
    with conn:
        db.upsert_institution(conn, raw['institution'])
    ingest_family(conn, family)
    assert db.ingest_program(conn, raw)
    assert not db.ingest_program(conn, raw)
    data = db.export_data(conn)
    p = next(x for x in data['programs'] if x['id'] == pid)
    expected = entry(pid)['expected_profile']
    for role, manual in expected.items():
        actual = requirement_profile(p)[role]
        assert (actual['count'], actual['categories']) == (manual['count'], manual['categories'])
    build(data, tmp_path/'site', base_path='/ai-program-atlas/')
    html = (tmp_path/'site'/'programs'/pid/'index.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')
    for role in ['required', 'options']:
        panel = soup.select_one(f'.profile-panel[data-profile="{role}"]')
        assert panel.select_one('.profile-denominator' if role == 'required' else '.profile-total').get_text().startswith('26 distinct')
        for category, count in expected[role]['categories'].items():
            label = panel.select_one(f'.category-row[data-category="{category}"] strong').get_text()
            assert int(label.split()[0]) == count
    assert '/ai-program-atlas/assets/' in html
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_rit_later_immersion_additions_do_not_receive_independent_certification():
    p = load(RIT); e = entry(RIT)
    reviewed = reviewed_inventory(p,e)
    old_ids = {c['id'] for c in reviewed['courses']}
    new = [c for c in p['courses'] if c['id'] not in old_ids]
    assert len(old_ids)==43 and new
    assert e['second_pass_status']=='partial' and not e['full_degree_verified']
    assert 'outside this independent content review' in e['verified_scope']
    assert requirement_profile(p)['required']['count']==23
    assert requirement_profile({**p,'courses':new,'course_identity_groups':[]})['required']['count']==0
    missing = {**p,'courses':[c for c in p['courses'] if c['id'] != e['expected_course_ids']['required'][0]]}
    with pytest.raises(AssertionError,match='independently reviewed course was removed'):
        reviewed_inventory(missing,e)
