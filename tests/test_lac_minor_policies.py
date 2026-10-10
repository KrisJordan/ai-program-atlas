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
