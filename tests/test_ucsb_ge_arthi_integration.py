import json
from pathlib import Path
from atlas.adapters import ucsb_ge_arthi_reviews as m
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def test_completed_art_history_batch_maps_choices_without_inferred_prerequisites():
    d = json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    validate_program(d)
    courses = {c['code']: c for c in d['courses']}
    for entry in m.SPEC['entries']:
        c = courses[entry['code']]
        assert c['category_review'] == entry['category_review']
        assert c['prerequisites'] is None
    assert courses['ARTHI 136W']['category'] == 'applications'
    assert courses['ARTHI 5B']['category_review']['status'] == 'mixed'
    assert courses['ARTHI 136O']['category'] == 'human_context'
    assert courses['ARTHIW 6R']['category'] == 'human_context'
    assert any('113A' in n for n in courses['ARTHI 113B']['notes'])
    assert any('same course' in n.lower() for n in courses['ARTHIW 6F']['notes'])
    assert courses['ARTHIW 6F']['id'] != courses['ARTHI 6F']['id']
    profile = requirement_profile(d)
    assert [profile[k]['count'] for k in ('required', 'options', 'unresolved')] == [20, 133, 2]
    assert profile['options']['source_record_count'] == 135
    assert len(d['course_identity_groups']) == 3
    r = {r['id']: r for r in d['requirements']}
    assert 'ucsb-arthiw-6r' in r['ucsb-ai-bs-policy-area-e']['course_ids']
    assert 'ucsb-arthiw-6r' in r['ucsb-ai-bs-policy-area-f']['course_ids']
    assert r['ucsb-ai-bs-policy-area-f']['count'] == 1
