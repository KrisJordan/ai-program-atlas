import json
from pathlib import Path
import pytest
from atlas.adapters.rit_open_related_immersions import parse_global
from atlas.adapters.rit_writing_closure import PID


def fixture():
    return '<main><h1>Global Experience Immersion</h1><h2>Curriculum for 2026-2027 for Global Experience Immersion</h2><p>Global Experience immersions are approved by RIT Global and the RIT General Education Committee. All nine credits must contain a substantial global or study away experiential component and all must be GE Electives or Perspectives to qualify.</p></main>'


def test_open_criterion_observed_without_invented_finite_pool_or_fresh_audit():
    a=parse_global(fixture());b=parse_global(fixture().replace('All nine','All twelve'))
    assert a['observed_credits']==9 and b['observed_credits']==12
    assert a['courses']==a['requirements']==[] and a['observed_credit_unit']=='unknown'
    assert 'curriculum_audit' not in a
    for before,after in [('2026-2027','2025-2026'),('General Education Committee','Unidentified Committee'),('All nine credits must contain','No criterion')]:
        with pytest.raises(ValueError):parse_global(fixture().replace(before,after))


def test_manual_open_rule_and_untagged_language_partition_remain_explicit():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']}
    g=r['global-experience-immersion']
    assert g['kind']=='choose_credits' and g['credits']==9 and g['course_ids']==[]
    assert 'RIT General Education Committee' in g['summary'] and 'GE Electives or Perspectives' in g['summary']
    assert 'no finite' in g['summary'] and g['parent_id']==PID+'-immersion-observed-routes'
    latin=r['latino-latina-latin-american-studies-immersion']
    assert latin['kind']=='choose_courses' and latin['count']==3 and latin['credits'] is None
    assert 'no automatic partition' in latin['summary']
    assert r['american-indian-and-indigenous-studies-immersion-required']['course_ids']==[PID+'-anth-260']
    assert 'North America' in r['american-indian-and-indigenous-studies-immersion-electives']['summary']
    assert 'No 300-level minimum' in r['urban-studies-immersion']['summary']
    assert d['curriculum_status']=='partial'
