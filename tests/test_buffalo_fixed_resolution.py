"""Binding department titles remain distinct from illustrative sibling curricula."""
import json
from pathlib import Path

import pytest

from atlas.adapters.buffalo_economics_titles import COMPONENTS, PROGRAM_ID, SOURCE_ID, parse, title_id
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import check_expectations, core_review_fingerprint, validate_core_review
from atlas.families import resolve_program

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / 'research/degree-audit/independent-resolution-buffalo.json').read_text())


def fixture():
    body = '<title>BS in AI and Quantitative Economics - Department of Economics</title><h2>Required Courses</h2>'
    for label, credits, fixed, choice in COMPONENTS:
        body += f'<h3>{label} ({credits} credits)</h3><ul>' + ''.join(f'<li>{t}</li>' for t in fixed) + '</ul>'
        if choice:
            body += '<p>' + choice[0] + '</p><ul>' + ''.join(f'<li>{t}</li>' for t in choice[2]) + '</ul>'
    return body + '<h2>Experiential learning</h2>'


def test_uncoded_binding_titles_preserve_fixed_and_choice_roles():
    p = parse(fixture())
    result = requirement_profile(p)
    assert (result['required']['count'], result['options']['count'], result['unresolved']['count']) == (19, 16, 0)
    assert all(c['code'] is None and c['credits'] is None and c['prerequisites'] is None for c in p['courses'])
    assert all(c['source_id'] == SOURCE_ID and 'category_review' not in c for c in p['courses'])
    assert {r['count'] for r in p['requirements'] if r['kind'] == 'choose_courses'} == {1, 2, 4}
    assert all(r['credit_unit'] == 'unknown' for r in p['requirements'])
    assert 'curriculum_audit' not in p and 'core_review' not in p
    assert title_id('Introduction to Computer Science I') != title_id('Introduction to Computer Science II')


@pytest.mark.parametrize('before,after', [
    ('Required Courses', 'Suggested Courses'),
    ('Precalculus', 'College Algebra'),
    ('Choose two of', 'Choose three of'),
    ('Math Core (8 credits)', 'Math Core (9 credits)'),
    ('BS in AI and Quantitative Economics', 'BA in Economics'),
    ('<li>Health Economics</li>', ''),
])
def test_changed_identity_membership_quantity_or_amount_requires_review(before, after):
    with pytest.raises(ValueError):
        parse(fixture().replace(before, after))


@pytest.mark.parametrize('entry', LEDGER['programs'], ids=lambda e: e['program_id'])
def test_resolution_proposal_pins_manual_mapped_sets(entry):
    p = json.loads((ROOT / 'data/programs' / (entry['program_id'] + '.json')).read_text())
    family = json.loads((ROOT / 'data/families/buffalo-ai-plus-x-degrees.json').read_text())
    p = resolve_program(p, family)
    validate_core_review(entry, p['id'])
    assert core_review_fingerprint(p) == entry['reviewed_content_hash']
    check_expectations(entry['expected_profile'], requirement_profile(p), p['id'], 'Buffalo resolution')
    known = {c['id'] for c in p['courses']}
    sets = [set(ids) for ids in entry['expected_course_ids'].values()]
    assert len(set.union(*sets)) == sum(map(len, sets)) == len(known)
    assert set.union(*sets) == known
    assert entry['resolution_outcome'] == 'exact_evidence_limit'
    assert entry['full_degree_verified'] is False
    fixed_status = entry['dimensions']['fixed_requirements']['status']
    assert fixed_status == ('partial' if p['id'] == PROGRAM_ID else 'unverified')


def test_economics_manual_inventory_retains_uncertainty_and_bounded_subject_review():
    entry = next(e for e in LEDGER['programs'] if e['program_id'] == PROGRAM_ID)
    inventory = entry['manual_uncoded_major_inventory']
    assert inventory['catalog_year'] is None and inventory['credit_unit'] == 'unknown'
    assert sum(map(len, inventory['fixed_titles_by_component'].values())) == 19
    assert [len(g['titles']) for g in inventory['choice_groups']] == [3, 3, 10]
    assert [g['count'] for g in inventory['choice_groups']] == [1, 2, 4]
    p = json.loads((ROOT / 'data/programs' / (PROGRAM_ID + '.json')).read_text())
    major = [c for c in p['courses'] if c['source_id'] == SOURCE_ID]
    assert len(major) == 35 and sum(c['category_review']['status'] == 'reviewed' for c in major) == 7
    assert sum(c['category_review']['status'] == 'unclassified' for c in major) == 28
    assert all(c['code'] is None and c['description'] is None for c in major)
