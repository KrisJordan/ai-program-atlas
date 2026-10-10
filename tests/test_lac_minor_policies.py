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
    assert sum(c['name'] is not None for c in courses.values()) == 21
    assert courses['STAT-142']['credits'] == 1
    assert courses['STAT-141']['credits'] == 4
    assert courses['CS-372']['credits'] is None
    assert courses['CS-372']['name'] is None
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
