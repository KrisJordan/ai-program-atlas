"""Synthetic local-scope curriculum structures; no copied catalog descriptions."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
IDS = {'mit': 'mit-ai-decision-making-bs', 'ncsu': 'ncsu-cs-ai-concentration'}

def adapter(key):
    return importlib.import_module('atlas.adapters.' + IDS[key] + '.adapter')

def fixture(key):
    return (ROOT / 'tests/fixtures/mit_ncsu' / (key + '.html')).read_text()

@pytest.mark.parametrize('key', IDS)
def test_source_guard_and_review_separation(key):
    observed = adapter(key).parse(fixture(key))
    assert observed['courses'] and observed['requirements']
    assert not {'last_verified', 'curriculum_status', 'curriculum_audit'} & observed.keys()
    with pytest.raises(ValueError):
        adapter(key).parse('<main>Unrelated program</main>')
    with pytest.raises(ValueError):
        adapter(key).parse('<title>Access denied</title>' + fixture(key))


def test_ncsu_only_concentration_pools_not_parent_degree_or_general_csc_pool():
    observed = adapter('ncsu').parse(fixture('ncsu'))
    courses = {course['code']: course for course in observed['courses']}
    assert set(courses) == {'CSC 411', 'CSC 422', 'BUS 351', 'DSA 405', 'CSC 440', 'CSC 442'}
    assert courses['DSA 405']['credits'] == 1
    assert all(c['credit_unit'] == 'unknown' for c in courses.values())
    rules = {r['id']: r for r in observed['requirements']}
    assert rules['ncsu-ai-csc-electives']['credits'] == 6
    assert rules['ncsu-ai-electives']['credits'] == 9
    assert rules['ncsu-ai-electives']['kind'] == 'note'
    assert 'Select 9 published credit hours' in rules['ncsu-ai-electives']['summary']
    assert set(rules['ncsu-ai-csc-electives']['course_ids']) <= set(rules['ncsu-ai-electives']['course_ids'])
    assert 'At most 3' in rules['ncsu-ai-csc-cap']['summary']
    assert 'unresolved source discrepancy' in rules['ncsu-ai-grade']['summary']
    assert observed['outcomes'][0]['statement_type'] == 'program_aim'


def test_ncsu_policy_changes_require_review():
    for old, new in [('only 3 hours', 'only 6 hours'), ('<sup>2</sup>', '<sup>1</sup>'), ('21 credit hours', '24 credit hours')]:
        with pytest.raises(ValueError):
            adapter('ncsu').parse(fixture('ncsu').replace(old, new))


def test_mit_bundles_one_option_and_shared_course_not_duplicated():
    observed = adapter('mit').parse(fixture('mit'))
    courses = {course['code']: course for course in observed['courses']}
    assert courses['6.100A']['credits'] is None
    assert courses['6.C011']['credits'] is None
    bundle = next(r for r in observed['requirements'] if set(r['course_ids']) == {'mit-ai-6-100a', 'mit-ai-6-100b'})
    parent = next(r for r in observed['requirements'] if r['id'] == bundle['parent_id'])
    assert bundle['kind'] == 'all' and parent['kind'] == 'alternative'
    assert parent['credits'] == 12
    assert len([c for c in observed['courses'] if c['code'] == '6.4110']) == 1
    assert len([r for r in observed['requirements'] if 'mit-ai-6-4110' in r['course_ids']]) == 2
    assert not any(r['credits'] in (168, 177, 180, 189) for r in observed['requirements'])
    assert any('180–189' in r['summary'] for r in observed['requirements'])
    assert any('overlay' in r['summary'] for r in observed['requirements'])


def test_mit_policy_or_option_heading_changes_require_review():
    for old, new in [('Select five subjects', 'Select four subjects'), ('6-unit disciplinary module', '3-unit disciplinary module'), ('Human-centric', 'Humanities')]:
        with pytest.raises(ValueError):
            adapter('mit').parse(fixture('mit').replace(old, new))


def test_mit_linked_reference_is_not_certified_cim2_pool():
    html = '<main><div id="cimtextcontainer"><h2>Communication-Intensive in the Major Subjects</h2><table class="sc_courselist"><tr><td class="codecol"><a class="code" href="/subject">6.4300</a></td><td>Synthetic vision subject</td><td class="hourscol">12</td></tr></table></div></main>'
    d = adapter('mit').parse_cim_reference(html)
    assert d['courses'][0]['credits'] == 12
    assert d['requirements'][0]['kind'] == 'note'
    assert 'not a verified set' in d['requirements'][0]['summary']

@pytest.mark.parametrize('key', IDS)
def test_partial_audits_register_exact_remaining_scope(key):
    d = json.loads((ROOT/'data/programs'/(IDS[key]+'.json')).read_text())
    validate_program(d)
    assert d['curriculum_status'] == 'partial'
    assert d['curriculum_audit']['unresolved_requirements']
    assert d['curriculum_audit']['scope'] == d['program_kind']
    assert set(adapter(key).SOURCES) <= {s['url'] for s in d['sources']}
    assert d['first_offered'] is None


def test_mit_conflicting_vision_credits_remain_unknown_in_reviewed_seed():
    d = json.loads((ROOT/'data/programs/mit-ai-decision-making-bs.json').read_text())
    vision = next(c for c in d['courses'] if c['code'] == '6.4300')
    assert vision['credits'] is None
    assert any('15' in gap and '12' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
