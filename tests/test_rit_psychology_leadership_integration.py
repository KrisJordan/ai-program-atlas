import json
from pathlib import Path
from atlas.adapters.rit_writing_closure import PID
from atlas.curriculum_profile import requirement_profile

def test_nested_pairs_preparation_and_ai_overlap_remain_distinct():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    prep=r['psychology-immersion-preparation'];assert prep['kind']=='note' and prep['parent_id'] is None
    assert r['psychology-immersion-preparation-or']['course_ids']==[PID+'-psyc-101',PID+'-psyc-101h']
    electives=r['psychology-immersion-electives'];assert electives['count']==3 and PID+'-psyc-223' not in electives['course_ids']
    assert r['psychology-immersion-electives-or-1']['course_ids']==[PID+'-psyc-221',PID+'-psyc-221h']
    assert r['psychology-immersion-electives-or-2']['course_ids']==[PID+'-psyc-224',PID+'-psyc-224h']
    assert 'No 300-level minimum' in r['psychology-immersion']['summary']
    assert 'broader overview criterion remains open' in r['psychology-immersion']['summary']
    diversity=r['diversity-inclusion-and-dialogue-immersion-group-2'];assert diversity['count']==1 and diversity['course_ids']==[PID+'-lead-304']
    pairs=[x for x in r.values() if x['parent_id']==diversity['id']];assert len(pairs)==5 and all(x['kind']=='alternative' and x['count']==1 for x in pairs)
    assert 'at least two distinct disciplines' in r['religious-studies-immersion']['summary']
    assert 'may not all come from the same discipline' in r['legal-studies-immersion']['summary']
    assert c['PSYC-101H']['prerequisites'] is None and c['PSYC-255']['credits']==3
    assert c['CRIM-510']['category']=='human_context'
    profile=requirement_profile(d);assert [profile[k]['count'] for k in ['required','options','unresolved']]==[23,641,15]
    assert len(c)==679 and sum(bool(x['description']) for x in c.values())==676
