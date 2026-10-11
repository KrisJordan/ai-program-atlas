import importlib.util
import json
from pathlib import Path
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile

def test_six_routes_keep_local_requirements_and_exact_exclusion_scope():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    for slug in ['communication','creative-writing','black-studies']:
        rule=r[slug+'-immersion'];assert rule['kind']=='choose_courses' and rule['count']==3 and rule['credits']==9
    assert '300' not in r['black-studies-immersion']['summary']
    assert 'creative writing concentration' in r['creative-writing-immersion']['summary']
    assert r['digital-literatures-and-comparative-media-immersion-group-1']['course_ids']==[PID+'-engl-215']
    assert r['digital-literatures-and-comparative-media-immersion-group-1']['kind']=='all'
    assert r['digital-literatures-and-comparative-media-immersion-group-2']['count']==2
    assert r['advertising-and-public-relations-immersion-group-1']['count']==1
    assert r['advertising-and-public-relations-immersion-group-2']['count']==2
    assert 'cannot also count' in r['advertising-and-public-relations-immersion-group-2']['summary']
    assert c['ENGL-376']['credits']==3 and c['ENGL-376']['category']=='human_context'
    assert any('instructor' in n for n in c['ENGL-389']['notes'])
    assert all(c[code]['category']=='applications' for code in ['COMM-223','COMM-322','COMM-421'])
    profile=requirement_profile(d)
    assert [profile[k]['count'] for k in ['required','options','unresolved']]==[23,770,17]
    assert len(c)==810 and sum(bool(x['description']) for x in c.values())==807
    spec=importlib.util.spec_from_file_location('rit_writing_integration',Path('atlas/adapters')/PID/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    assert set(a.SOURCES)<={s['url'] for s in d['sources']}
