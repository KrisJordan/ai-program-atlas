"""Bounded independent expectations; empty graphs never verify curricula."""
import json
from pathlib import Path

import pytest

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint, validate_core_review, check_expectations
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / 'research/degree-audit/independent-core-central.json').read_text())
ENTRIES = {e['program_id']: e for e in LEDGER['programs']}
BUFFALO = sorted(pid for pid in ENTRIES if pid.startswith('university-at-buffalo'))


def load(pid):
    p = json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())
    if p.get('family'):
        family = json.loads((ROOT / 'data/families' / f"{p['family']['id']}.json").read_text())
        return resolve_program(p, family)
    return p


@pytest.mark.parametrize('pid', sorted(ENTRIES))
def test_pinned_bounded_review_and_counts(pid):
    p, e = load(pid), ENTRIES[pid]
    validate_core_review(e, pid)
    assert e['reviewed_content_hash'] == core_review_fingerprint(p)
    assert e['full_degree_verified'] is False
    result = requirement_profile(p)
    check_expectations(e['expected_profile'], result, pid, 'Independent central')
    ids = e['expected_course_ids']
    known = [set(value) for value in ids.values() if value is not None]
    assert sum(len(s) for s in known) == len(set().union(*known))
    for role, value in ids.items():
        if value is not None:
            assert len(value) == e['expected_profile'][role]['count']
            assert set(value) <= {c['id'] for c in p['courses']}
    assert all(d['limitations'] for d in e['dimensions'].values())


def test_scope_excludes_primary_authored_rit():
    assert len(ENTRIES) == 12 and len(BUFFALO) == 8
    assert not any(pid.startswith('rochester-institute') for pid in ENTRIES)


@pytest.mark.parametrize('pid', [pid for pid in BUFFALO if 'quantitative-economics' not in pid])
def test_buffalo_framework_and_dated_candidates_do_not_become_fixed_courses(pid):
    p, e = load(pid), ENTRIES[pid]
    assert e['dimensions']['fixed_requirements']['status'] == 'unverified'
    assert e['dimensions']['choice_rules']['status'] == 'partial'
    assert e['source_row_counts'] == {'pathway_rows': 830, 'distinct_pathway_code_titles': 308, 'university_context_records': 2}
    assert set(e['expected_course_ids']['unresolved']) == {c['id'] for c in p['courses']}
    assert all(r['kind'] == 'note' for r in p['requirements'])
    # Resolver metadata may expose a shared ID in origin instead; exact suffixes
    # independently identify the five source-bound family rules.
    inherited = [r for r in p['requirements'] if r['id'] in {pid + '-family-' + str(n) for n in range(1, 6)}]
    assert len(inherited) == 5 and not any(r['course_ids'] for r in inherited)
    society = next(r for r in inherited if r['title'] == 'Society Core')
    assert 'five three-credit' in society['summary']
    courses = {c['id']: c for c in p['courses']}
    assert courses['buffalo-ubc-eng-105']['category'] == 'human_context'
    assert courses['buffalo-ubc-ubc-399']['category_review']['status'] == 'unclassified'
    assert sum(c['category'] == 'other' for c in p['courses']) == 309


def test_delaware_two_sample_alternatives_are_context_not_a_student_load():
    p = load('delaware-ai-engineering-major')
    e = ENTRIES[p['id']]
    assert e['dimensions']['fixed_requirements']['status'] == 'unverified'
    requirements = {r['id']: r for r in p['requirements']}
    alternatives = [r for r in p['requirements'] if r['kind'] == 'alternative']
    assert {frozenset(r['course_ids']) for r in alternatives} == {
        frozenset({'delaware-eleg-405', 'delaware-eleg-625'}),
        frozenset({'delaware-eleg-397', 'delaware-eleg-398'}),
    }
    assert all(requirements[r['parent_id']]['kind'] == 'note' for r in alternatives)
    assert not {'delaware-phys-207', 'delaware-phys-227', 'delaware-phys-208', 'delaware-phys-228'} & {c['id'] for c in p['courses']}
    assert all(c['credits'] is None and c['prerequisites'] is None for c in p['courses'])
    courses = {c['code']: c for c in p['courses']}
    for code in ['MATH 219', 'CISC 210', 'ELEG 625', 'ELEG 401']:
        assert courses[code]['category'] == 'other'
    assert courses['CISC 220']['category'] == courses['CISC 320']['category'] == 'foundations'


def test_purdue_named_choices_and_nested_nlp_transcription():
    p = load('purdue-ai-bs');e = ENTRIES[p['id']]
    r = {r['id']: r for r in p['requirements']}
    assert set(r['purdue-ai-bs-core']['course_ids']) == set(e['expected_course_ids']['required'])
    select = r['purdue-ai-bs-cs-selective-i']
    nlp = r['purdue-ai-bs-nlp-alternative']
    assert (select['kind'], select['count'], select['credits']) == ('choose_courses', 2, 6)
    assert nlp['kind'] == 'alternative' and nlp['parent_id'] == select['id']
    assert set(nlp['course_ids']) == {'purdue-cs-47700', 'purdue-cs-57700'}
    assert set(select['course_ids'] + nlp['course_ids']) == set(e['manual_option_components']['selective_1'])
    assert r['purdue-ai-bs-cs-selective-ii']['count'] == 1
    assert r['purdue-ai-bs-philosophy-selective']['count'] == 1
    cap = r['purdue-ai-bs-capstone']
    children = [q for q in p['requirements'] if q['parent_id'] == cap['id']]
    assert cap['count'] == 1 and cap['credits'] == 3 and len(children) == 4
    assert sum(bool(q['course_ids']) for q in children) == 1
    assert all(q['credits'] == 3 for q in children)
    union = set().union(*(set(v) for v in e['manual_option_components'].values()))
    # The earlier mapped college/core options stay in the graph, but the new
    # independent pass certifies only its named department subset.
    assert union == set(e['reviewed_option_subset']) and len(union) == 33
    assert union <= set(requirement_profile(p, include_course_ids=True)['course_ids']['options'])
    assert e['expected_course_ids']['options'] is None
    assert len(e['reviewed_option_subset']) == 33
    assert set(e['reviewed_option_subset']) <= union
    for key, rid in [('UCC01', 'purdue-ai-bs-college-core-written-communication'), ('UCC08', 'purdue-ai-bs-college-core-science-technology-and-society')]:
        assert len(r[rid]['course_ids']) == {'UCC01': 10, 'UCC08': 94}[key]
        assert r[rid]['kind'] == 'choose_courses' and r[rid]['count'] == 1
    courses = {c['id']: c for c in p['courses']}
    assert courses['purdue-ma-26100']['credits'] == 4
    assert courses['purdue-ma-27101']['credits'] == 5
    assert r['purdue-ai-bs-core-ma-26100']['credits'] is None
    assert r['purdue-ai-bs-core']['credits'] is None


def test_purdue_content_checks_have_explicit_dated_and_unreviewed_boundaries():
    p = load('purdue-ai-bs');e = ENTRIES[p['id']]
    assert e['expected_profile']['options'] is None
    assert e['expected_profile']['unresolved'] is None
    assert e['expected_course_ids']['unresolved'] is None
    courses = {c['id']: c for c in p['courses']}
    for number, category in {'18000': 'foundations', '18200': 'other', '34800': 'systems', '37300': 'ai_ml', '38100': 'foundations', '44800': 'systems', '47100': 'ai_ml', '48300': 'foundations', '52300': 'human_context', '57700': 'ai_ml'}.items():
        assert courses['purdue-cs-' + number]['category'] == category
    assert courses['purdue-cs-18200']['category_review']['status'] == 'mixed'
    assert 'historic outline does not imply current-term' in courses['purdue-cs-47100']['category_review']['rationale']
    assert e['dimensions']['classification']['status'] == 'partial'


def test_purdue_ba_unknown_philosophy_menu_is_not_a_verified_empty_pool():
    p = load('purdue-ai-ba');e = ENTRIES[p['id']]
    requirements = {r['id']: r for r in p['requirements']}
    philosophy = requirements['purdue-ai-ba-philosophy']
    assert philosophy['count'] == 8 and philosophy['credits'] == 24
    assert not philosophy['course_ids']
    assert e['dimensions']['choice_rules']['status'] == 'partial'
    assert set(requirements['purdue-ai-ba-cs']['course_ids']) == set(e['expected_course_ids']['required'])
    assert requirements['purdue-ai-ba-cs']['credits'] == 15
    assert all(c['credits'] is None for c in p['courses'])


def test_furman_zero_graph_is_not_zero_verified_curriculum():
    p = load('furman-ai-bs');e = ENTRIES[p['id']]
    assert not p['courses'] and not p['requirements']
    assert {d['status'] for d in e['dimensions'].values()} == {'unverified'}
    assert all(e['expected_profile'][role]['categories'] is None for role in ['required', 'options', 'unresolved'])
    assert 'Empty mapped graph only' in e['expected_profile_scope']
