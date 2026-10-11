import json
from pathlib import Path
from atlas.adapters.rit_writing_closure import PID
from atlas.db import validate_program
from atlas.curriculum_profile import requirement_profile


def test_whole_language_paths_credits_and_shared_identity_conditions_are_retained():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());validate_program(d)
    r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    for language in ['arabic','chinese','french','german','italian','japan','russian','spanish']:
        key=language+'-im-immersion'
        assert r[key]['kind']=='alternative' and r[key]['parent_id']==PID+'-immersion-observed-routes'
        assert r[key+'-three-language']['count']==3 and r[key+'-three-language']['credits'] is None
        assert r[key+'-culture-route']['kind']=='all'
        assert r[key+'-two-language']['count']==2 and r[key+'-culture']['count']==1
        assert r[key+'-two-language']['parent_id']==PID+'-'+key+'-culture-route'
    assert c['MLAR-201']['credits']==4 and c['MLAR-201']['category']=='human_context'
    assert '9 / 3' in r['chinese-im-immersion']['summary']
    assert 'Dubai' in r['arabic-im-immersion-culture']['summary']
    assert 'unresolved' in r['spanish-im-immersion-three-language']['summary']
    for code in ['HIST-130','HIST-135']:
        assert PID+'-'+code.lower() in r['spanish-im-immersion-three-language']['course_ids']
        assert PID+'-'+code.lower() in r['spanish-im-immersion-culture']['course_ids']
        assert sum(x['code']==code for x in d['courses'])==1
    assert c['ANTH-489']['category_review']['status']=='unclassified'
    assert c['ANTH-303']['category']=='mathematics' and c['ANTH-361']['category']=='human_context'
    assert c['ANTH-435']['category_review']['status']=='mixed'
    assert c['SOCI-235']['prerequisites'] is None
    assert r['cultural-anthropology-immersion']['count']==3
    first=r['cultural-anthropology-immersion-first-entry']
    assert first['kind']=='alternative' and first['count']==1
    assert set(first['course_ids'])=={PID+'-anth-'+n for n in ['102','104','105']}
    assert not(set(first['course_ids']) & set(r['cultural-anthropology-immersion']['course_ids']))
    p=requirement_profile(d)
    assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,591,15]
    assert d['curriculum_status']=='partial'
