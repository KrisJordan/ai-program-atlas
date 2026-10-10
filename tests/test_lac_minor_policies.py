"""Reviewed minor choices and policies remain distinct from metadata completeness."""
import json
from pathlib import Path
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]

def record(slug):
    data = json.loads((ROOT / 'data/programs' / (slug + '.json')).read_text())
    validate_program(data)
    return data

def test_lake_forest_track_choice_and_nonduplicated_course_inventory():
    d = record('lake-forest-ai-minor')
    assert d['curriculum_status'] == 'complete'
    assert d['curriculum_audit']['scope'] == 'minor'
    assert not d['curriculum_audit']['unresolved_requirements']
    courses = {c['id']: c for c in d['courses']}
    assert len(courses) == 28
    req = {r['id'].removeprefix('lake-forest-ai-minor-'): r for r in d['requirements']}
    assert req['track']['kind'] == 'alternative' and req['track']['count'] == 1
    assert req['studies']['parent_id'] == req['track']['id']
    assert req['governance']['parent_id'] == req['track']['id']
    assert req['studies-humanities']['count'] == 2
    assert len(req['studies-humanities']['course_ids']) == 15
    assert len(req['governance-second']['course_ids']) == 20
    assert req['governance-second']['count'] == 1
    assert 'only if not used for ethics' in req['overlap']['summary']
    assert '50%' in req['residence']['summary']
    assert 'four that do not double count' in req['minor-policy']['summary']
    capstone = next(c for c in courses.values() if c['code'] == 'CSCI320')
    assert capstone['prerequisites'] == 'MATH 150 or permission of instructor.'
    assert all(c['credits'] is None for c in courses.values())
    assert all(o['statement_type'] == 'learning_outcome' for o in d['outcomes'])

def test_ursinus_credit_exclusions_aliases_and_partial_policy_audit():
    d = record('ursinus-ai-minor')
    assert d['curriculum_status'] == 'partial'
    assert d['catalog_year'] == '2026-2027'
    courses = {c['code']: c for c in d['courses']}
    assert len(courses) == 22
    assert sum(c['name'] is not None for c in courses.values()) == 22
    assert courses['STAT-142']['credits'] == 1
    assert courses['STAT-141']['credits'] == 4
    assert courses['CS-372']['credits'] == 4
    assert courses['CS-372']['name'] == 'Digital Musical Audio Processing'
    assert courses['PHIL/CS-243']['name'] == 'Technology and Ethics'
    assert courses['STAT-244']['prerequisites'] == 'None (explicitly stated).'
    assert courses['PHIL-274']['prerequisites'] is None
    req = {r['id'].removeprefix('ursinus-ai-minor-'): r for r in d['requirements']}
    assert req['total']['credits'] == 24
    assert req['total']['credit_unit'] == 'semester_hours'
    assert len(req['required']['course_ids']) == 5
    assert len(req['electives']['course_ids']) == 17
    assert 'both STAT-242W and STAT-243W' in req['statistics-credit']['summary']
    assert 'director' in req['grading']['summary']
    assert any('overlap' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
    assert d['outcomes'][0]['statement_type'] == 'program_aim'
    assert d['outcomes'][1]['kind'] == 'inferred_taxonomy'

def test_nd_source_pools_credit_definition_and_unresolved_rules():
    d = record('university-of-notre-dame-ai-analytics-in-business-minor-minor')
    e = record('notre-dame-ai-essentials-business-minor')
    assert len(d['courses']) == 38 and len(e['courses']) == 12
    for data in (d, e):
        assert data['curriculum_status'] == 'partial'
        assert all(c['credit_unit'] == 'semester_hours' for c in data['courses'])
        assert all(c['credits'] is not None for c in data['courses'])
        assert data['curriculum_audit']['unresolved_requirements']
        assert data['outcomes'][0]['statement_type'] == 'program_aim'
        assert any('5.4.2' in s['locator'] for s in data['sources'])
    req = {r['id'].removeprefix(d['id']+'-'):r for r in d['requirements']}
    assert len(req['electives']['course_ids']) == 34
    assert req['electives']['credits'] == 9
    assert req['electives']['kind'] == 'choose_credits'
    assert len(req['catalog-elective-conflict']['course_ids']) == 30
    assert req['catalog-elective-conflict']['kind'] == 'note'
    assert len(set(req['electives']['course_ids'])-set(req['catalog-elective-conflict']['course_ids'])) == 6
    assert len(set(req['catalog-elective-conflict']['course_ids'])-set(req['electives']['course_ids'])) == 2
    codes = {c['code']: c for c in d['courses']}
    assert 'ITAO 50840' not in codes and 'ITAO 30530' not in codes
    assert codes['MARK 30120']['name'] != codes['MARK 30130']['name']
    assert 'recommended' in codes['ITAO 40530']['prerequisites']
    assert 'Business Analytics' in codes['ITAO 50850']['prerequisites']
