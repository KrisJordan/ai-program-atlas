"""Independent manual source judgments, never parser-produced certification."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint, validate_core_review, check_expectations
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
REVIEW = json.loads((ROOT / 'research/degree-audit/independent-core-east.json').read_text())
FAMILY = json.loads((ROOT / 'data/families/northeastern-ai-combined-degrees.json').read_text())
ENTRIES = REVIEW['programs']


def program(pid):
    p = json.loads((ROOT / 'data/programs' / (pid + '.json')).read_text())
    return resolve_program(p, FAMILY if p.get('family') else None)


def test_scope_and_explicit_unreviewed_dimensions():
    assert len(ENTRIES) == 26
    assert len({e['program_id'] for e in ENTRIES}) == 26
    ne = [e for e in ENTRIES if e['program_id'].startswith('northeastern')]
    assert len(ne) == 24
    assert sum(len(e['expected_course_ids']['required']) for e in ENTRIES) == 581
    assert len(REVIEW['course_content_checks']) == 219
    for e in ne:
        assert e['expected_profile']['options'] is None
        assert e['expected_profile']['unresolved'] is None
        assert e['expected_course_ids']['options'] is None
        assert e['dimensions']['classification']['status'] == 'partial'
        assert e['dimensions']['choice_rules']['limitations']
    assert {e['dimensions']['fixed_requirements']['status'] for e in ENTRIES} == {'verified'}


@pytest.mark.parametrize('entry', ENTRIES, ids=lambda e: e['program_id'])
def test_source_enumerated_fixed_identities_and_categories_match_resolved_graph(entry):
    p = program(entry['program_id'])
    validate_core_review(entry, p['id'])
    assert entry['reviewed_content_hash'] == core_review_fingerprint(p)
    profile = requirement_profile(p, include_course_ids=True)
    for role, expected in entry['expected_course_ids'].items():
        if expected is not None:
            assert set(expected) == set(profile['course_ids'][role])
    check_expectations(entry['expected_profile'], profile, p['id'], 'Independent source reread')
    assert set(entry.get('reviewed_option_subset', [])) <= set(profile['course_ids']['options'])
    byid = {c['id']: c for c in p['courses']}
    assert {byid[c]['code'] for c in entry['expected_course_ids']['required']} == set(entry['manual_fixed_codes'])


def test_manual_computing_categories_are_content_based_and_variant_specific():
    checks = {(c['institution_id'], c['code']): c for c in REVIEW['course_content_checks']}
    for code in ['CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'DS 3500']:
        assert checks['northeastern-university', code]['category'] == 'foundations'
    assert checks['northeastern-university', 'DS 3000']['category'] == 'mathematics'
    assert checks['northeastern-university', 'DS 4300']['category'] == 'systems'
    assert checks['northeastern-university', 'DS 4200']['category'] == 'other'
    math = next(e for e in ENTRIES if '-and-mathematics-' in e['program_id'])
    assert 'MATH 1365' in math['manual_fixed_codes']
    bio = next(e for e in ENTRIES if '-and-biology-' in e['program_id'])
    assert 'MATH 1365' not in bio['manual_fixed_codes']
    comm = next(e for e in ENTRIES if '-and-communication-studies-' in e['program_id'])
    assert 'CS 4120' not in comm['manual_fixed_codes']  # no solving the explicit eight-credit pool
    ling = next(e for e in ENTRIES if '-and-linguistics-' in e['program_id'])
    assert 'CS 4120' in ling['manual_fixed_codes']


def test_research_method_corrections_preserve_ids_and_mixed_semantics():
    for fragment, code in [('criminal-justice', 'CRIM 3600'), ('international-affairs', 'INTL 2718')]:
        e = next(e for e in ENTRIES if fragment in e['program_id'])
        p = program(e['program_id'])
        c = next(c for c in p['courses'] if c['code'] == code)
        assert c['id'] in e['expected_course_ids']['required']
        assert c['category'] == 'other'
        assert c['category_review']['status'] == 'mixed'
        assert set(c['category_review']['candidate_categories']) == {'applications', 'human_context'}


def test_psu_programming_and_capstone_bundles_are_not_all_fixed():
    eng = next(e for e in ENTRIES if e['program_id'] == 'penn-state-ai-engineering-bs')
    assert eng['expected_profile']['required']['count'] == 17
    assert eng['expected_profile']['options']['count'] == 13
    assert eng['expected_profile']['required']['categories']['foundations'] == 1
    assert eng['expected_profile']['options']['categories']['foundations'] == 5
    p = program(eng['program_id'])
    ids = {c['code']: c['id'] for c in p['courses']}
    route = next(n for n in p['requirements'] if set(n['course_ids']) == {ids['CMPSC 121'], ids['DS 120']})
    parent = next(n for n in p['requirements'] if n['id'] == route['parent_id'])
    assert route['kind'] == 'all' and parent['kind'] == 'alternative'
    ist = next(e for e in ENTRIES if e['program_id'] == 'penn-state-ai-methods-applications-ist-bs')
    assert ist['expected_profile']['required']['count'] == 9
    assert ist['expected_profile']['required']['categories']['foundations'] == 2
    assert ist['expected_profile']['options'] is None
    assert len(ist['reviewed_option_subset']) == 13


def test_optional_actual_course_blocks_pin_all_independently_read_content():
    """Ignored source captures are optional in CI; changed content invalidates this proof."""
    paths = {c['evidence']['source_path'] for c in REVIEW['course_content_checks']}
    if not all((ROOT / p).exists() for p in paths):
        pytest.skip('Ignored official source captures unavailable')
    soups = {p: BeautifulSoup((ROOT / p).read_text(), 'html.parser') for p in paths}
    for check in REVIEW['course_content_checks']:
        evidence = check['evidence']
        code = re.sub(r'\s+', '', check['code'])
        matches = []
        for block in soups[evidence['source_path']].select('.courseblock'):
            text = ' '.join(block.get_text(' ', strip=True).split())
            prefix = re.sub(r'\s+', '', re.split(r'[:.]', text, maxsplit=1)[0])
            if prefix == code:
                matches.append(text)
        assert len(matches) == 1, check['code']
        assert hashlib.sha256(matches[0].encode()).hexdigest() == evidence['block_sha256'], check['code']


def test_optional_actual_variant_source_hashes():
    for entry in ENTRIES:
        if not entry['program_id'].startswith('northeastern'):
            continue
        path = ROOT / '.cache/research/degree-audit-northeastern' / (entry['program_id'] + '.html')
        if not path.exists():
            pytest.skip('Ignored official table captures unavailable')
        assert hashlib.sha256(path.read_text().encode()).hexdigest() == entry['source_snapshot']['sha256']
