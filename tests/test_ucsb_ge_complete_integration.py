import json
from pathlib import Path

import pytest

from atlas.adapters import ucsb_ge_catalog_pools as pools
from atlas.adapters import ucsb_ge_integrated_reviews as observer
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def seed():
    return json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())


def test_complete_reviewed_memberships_are_choices_and_keep_source_records():
    d = seed()
    validate_program(d)
    courses = {c['code']: c for c in d['courses']}
    rules = {r['id']: r for r in d['requirements']}
    assert len(d['courses']) == 940
    for area, count in [('D', 175), ('E', 299), ('F', 168), ('G', 273)]:
        r = rules['ucsb-ai-bs-policy-area-' + area.lower()]
        assert r['kind'] == 'choose_courses'
        expected = {courses[e['code'].strip()]['id'] for e in pools.SPEC['entries'] if area in e['general_areas']}
        assert set(r['course_ids']) == expected
        assert len(expected) == count
    profile = requirement_profile(d)
    assert [profile[k]['count'] for k in ('required', 'options', 'unresolved')] == [20, 827, 2]
    assert [profile[k]['source_record_count'] for k in ('required', 'options', 'unresolved')] == [21, 917, 2]


def test_reciprocal_identity_keeps_policies_and_does_not_merge_modality_or_wrong_codes():
    d = seed()
    groups = {g['id']: g for g in d['course_identity_groups']}
    courses = {c['id']: c for c in d['courses']}
    assert len(groups) == 82
    assert set(groups['ucsb-critical-ai-155']['course_ids']) == {'ucsb-c-lit-155', 'ucsb-ger-155', 'ucsb-engl-155ai'}
    assert set(groups['ucsb-ge-identity-045']['course_ids']) == {'ucsb-c-lit-186g', 'ucsb-slav-117g'}
    for code in ('ucsb-c-lit-186g', 'ucsb-slav-117g'):
        assert any('Repeat ceilings differ' in n for n in courses[code]['notes'])
    grouped = {i for g in groups.values() for i in g['course_ids']}
    assert not ({'ucsb-mus-175br', 'ucsb-eacs-5', 'ucsb-rg-st-4', 'ucsb-c-litw-40', 'ucsb-psy-w-1'} & grouped)
    assert groups['ucsb-ge-identity-098']['course_ids'] != groups['ucsb-ge-identity-099']['course_ids']


def test_source_ambiguities_and_unknown_prerequisites_remain_visible():
    courses = {c['code']: c for c in seed()['courses']}
    assert courses['ENGL 92RA']['credits'] is None
    assert courses['HIST 2CH']['credits'] == 1
    assert courses['HIST 2C']['credits'] == 5
    assert courses['MUS 3B']['prerequisites'] is None
    assert any('3A' in n and 'permission' in n for n in courses['MUS 3B']['notes'])
    assert courses['ENGL 155AI']['category'] == 'human_context'
    assert courses['LAIS 127']['category'] == courses['SPAN 127']['category'] == 'human_context'
    assert courses['CLASS 190']['category_review']['status'] == 'mixed'
    assert courses['FAMST 55AI']['category'] == 'human_context'
    assert courses['FAMST 56AI']['category_review']['status'] == 'mixed'


def test_complete_cached_observer_replays_without_manual_audit_or_identity_decisions():
    path = Path('.cache/research/ucsb-course-content/ge-defg-export.csv')
    if not path.exists():
        pytest.skip('Optional locally retained official export')
    result = observer.parse_csv(path.read_text())
    assert len(result['courses']) == 856
    assert len({c['id'] for c in result['courses']}) == 856
    assert not any('category_review' in c for c in result['courses'])
    assert 'course_identity_groups' not in result
    # Observation preserves the printed field; curated credit mode remains unknown.
    assert next(c for c in result['courses'] if c['code'] == 'ENGL 92RA')['credits'] == 5
    with pytest.raises(ValueError):
        observer.parse_csv(path.read_text().replace('Reading the Apocalypse', 'Changed course', 1))
