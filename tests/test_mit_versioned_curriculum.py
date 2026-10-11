"""Synthetic versioned requirements preserve bundles and source boundaries."""
from importlib import import_module
from pathlib import Path
import json
import pytest
from atlas.requirements import validate_requirements

ROOT = Path(__file__).resolve().parents[1]
adapter = import_module('atlas.adapters.mit-ai-decision-making-bs.versioned')


def html():
    return (ROOT/'tests/fixtures/mit_ncsu/mit-versioned-full.html').read_text()


def test_finite_routes_and_open_math_stay_separate():
    d = adapter.parse(html())
    validate_requirements(d)
    rules = {r['id']: r for r in d['requirements']}
    assert rules['mit-ai-v2025-elective-3']['kind'] == 'alternative'
    assert rules['mit-ai-v2025-math-open']['course_ids'] == []
    assert 'non-calculus' in rules['mit-ai-v2025-math-open']['summary']
    assert rules['mit-ai-v2025-elective-2-grad-ai-d-aus-1']['course_ids'] == ['mit-ai-v2025-6-7900']
    assert rules['mit-ai-v2025-elective-3-grad-aus2-1']['course_ids'] == ['mit-ai-v2025-6-s974-2027fa']


def test_bundles_remain_all_components_in_required_and_overlay_choices():
    d = adapter.parse(html())
    rules = {r['id']: r for r in d['requirements']}
    assert rules['mit-ai-v2025-programming-2']['course_ids'] == ['mit-ai-v2025-6-100a', 'mit-ai-v2025-6-100b']
    assert rules['mit-ai-v2025-overlay-ai-d-serc-1']['course_ids'] == ['mit-ai-v2025-6-c01', 'mit-ai-v2025-6-c011']
    assert rules['mit-ai-v2025-overlay-ai-d-serc']['kind'] == 'note'
    assert 'not additional required slots' in rules['mit-ai-v2025-overlay-ai-d-serc']['summary']
    assert rules['mit-ai-v2025-centers']['kind'] == 'choose_courses'
    assert rules['mit-ai-v2025-centers']['count'] == 5
    assert 'Select 5 printed option(s)' in rules['mit-ai-v2025-centers']['summary']
    assert rules['mit-ai-v2025-math-1']['kind']=='all'
    assert rules['mit-ai-v2025-math-2']['kind']=='alternative'
    assert rules['mit-ai-v2025-math-3']['kind']=='alternative'


def test_observations_have_distinct_ids_and_published_units_without_review():
    d = adapter.parse(html())
    assert all(c['id'].startswith('mit-ai-v2025-') for c in d['courses'])
    assert not any(c['code'] == '6.000' for c in d['courses'])
    assert all(c['credits'] == 12 for c in d['courses'])
    assert all(c['prerequisites'] == 'Prereqs: synthetic prerequisite' for c in d['courses'])
    assert not {'curriculum_audit', 'curriculum_status', 'last_verified', 'first_offered', 'catalog_year'} & d.keys()


@pytest.mark.parametrize('old,new', [
    ('Five <b>Center</b>', 'Four <b>Center</b>'),
    ('name="grad_II"', 'name="unreviewed"'),
    ('href="#grad_AUS2"', 'href="#new_pool"'),
    ('At least two of', 'At least three of'),
    (' &amp; ', ' or '),
])
def test_material_rule_changes_fail_closed(old, new):
    with pytest.raises(ValueError):
        adapter.parse(html().replace(old, new))


def test_seed_keeps_conditional_source_views_and_credit_conflict():
    d = json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    validate_requirements(d)
    rules = {r['id']: r for r in d['requirements']}
    assert rules['mit-ai-chart-reference']['kind'] == 'note'
    assert rules['mit-ai-version-required']['parent_id'] is None
    assert 'not cumulative' in rules['mit-ai-version-required']['summary']
    assert len([c for c in d['courses'] if c['code'] == '6.4300']) == 2
    assert next(c for c in d['courses'] if c['id']=='mit-ai-v2025-6-4300')['credits']==15
    assert next(c for c in d['courses'] if c['id']=='mit-ai-6-4300')['credits']is None
    assert d['curriculum_status'] == 'partial'
