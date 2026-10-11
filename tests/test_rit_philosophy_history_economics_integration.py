import json
from pathlib import Path
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def test_economics_preparation_and_explicit_ethics_whole_routes_remain_separate():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());validate_program(d)
    r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    econ=r['economics-immersion'];prep=r['economics-immersion-preparation']
    assert econ['kind']=='choose_courses' and econ['count']==3 and econ['credits']==9 and len(econ['course_ids'])==22
    assert prep['kind']=='note' and prep['course_ids']==[PID+'-econ-101'] and prep['credits']==3
    assert not(set(prep['course_ids']) & set(econ['course_ids']))
    assert r['ethics-immersion']['kind']=='alternative'
    assert r['ethics-immersion-foundation-pair']['kind']=='all'
    assert set(r['ethics-immersion-foundation-pair']['course_ids'])=={PID+'-phil-202',PID+'-phil-415'}
    assert r['ethics-immersion-two-electives']['count']==2 and r['ethics-immersion-one-elective']['count']==1
    assert len(r['ethics-immersion-two-electives']['course_ids'])==13
    assert 'two courses' in r['ethics-immersion']['summary']
    assert 'topic includes ethical issues' in r['ethics-immersion']['summary']
    assert len(r['history-immersion']['course_ids'])==54 and len(r['philosophy-immersion']['course_ids'])==37
    assert c['ECON-408']['category']==c['ECON-411']['category']=='applications'
    assert c['HIST-326']['category']==c['PHIL-320']['category']=='human_context'
    assert c['PHIL-205']['category']=='mathematics'
    p=requirement_profile(d)
    assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,411,14]
    assert d['curriculum_status']=='partial'
