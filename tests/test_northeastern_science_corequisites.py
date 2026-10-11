import json
from pathlib import Path
from copy import deepcopy
from importlib import import_module
import pytest
from atlas.adapters.northeastern_science_corequisites import guard_degree, observe_subject
from atlas.families import resolve_program
from atlas.curriculum_profile import requirement_profile
ROOT=Path(__file__).resolve().parents[1]
PROFILE=('chem-2315-chem-2316',['CHEM 2315','CHEM 2316'],'organic-chemistry-course-choice','alternative','options',['CHEM 2324'])

def page():
    return '''<div id="site-title"><h1>Chemistry and Chemical Biology (CHEM)</h1></div><div id="textcontainer">
    <div class="courseblock"><p class="courseblocktitle">CHEM 2315. Organic Chemistry 1 for Chemistry Majors. (4 Hours)</p><p class="cb_desc">Organic reactions.</p><p class="courseblockextra">Corequisite(s): CHEM 2316 , CHEM 2324</p></div>
    <div class="courseblock"><p class="courseblocktitle">CHEM 2324. Recitation for CHEM 2315. (0 Hours)</p><p class="cb_desc">Accompanies CHEM 2315 and CHEM 2316.</p><p class="courseblockextra">Corequisite(s): CHEM 2315 , CHEM 2316</p></div></div>'''


def test_science_observation_retains_zero_hours_and_exact_branch_parent():
    result=observe_subject(page(),'test','CHEM',[PROFILE],lambda html:dict(courses=[],requirements=[],notes=[]))
    assert result['courses'][0]['credits']==0
    assert 'category_review' not in result['courses'][0]
    node=result['requirements'][0]
    assert node['parent_id']=='test-req-chem-2315-chem-2316'
    assert node['kind']=='all' and node['course_ids']==['test-chem-2324']
    for before,after in [('Corequisite(s): CHEM 2316 , CHEM 2324','Prerequisite(s): CHEM 2316 , CHEM 2324'),
                         ('(0 Hours)','(1 Hour)'),('Recitation for CHEM 2315','Different Course'),
                         ('Chemistry and Chemical Biology (CHEM)','Computer Science (CS)')]:
        with pytest.raises(ValueError):observe_subject(page().replace(before,after),'test','CHEM',[PROFILE],lambda html:dict(courses=[],requirements=[],notes=[]))


def test_degree_guard_does_not_promote_optional_or_contextual_science():
    policy='<div id="programrequirementstextcontainer">Also complete any corequisite labs, recitations, clinicals, or tools courses where specified</div>'
    groups=[dict(id='root',parent_id=None,kind='all',course_ids=[]),dict(id='test-req-organic-chemistry-course-choice',parent_id='root',kind='alternative',course_ids=[]),dict(id='test-req-chem-2315-chem-2316',parent_id='test-req-organic-chemistry-course-choice',kind='all',course_ids=['test-chem-2315','test-chem-2316'])]
    assert guard_degree(lambda html:dict(requirements=groups),'test',[PROFILE])(policy)
    for index,kind in [(0,'note'),(1,'all')]:
        changed=deepcopy(groups);changed[index]['kind']=kind
        with pytest.raises(ValueError):guard_degree(lambda html:dict(requirements=changed),'test',[PROFILE])(policy)
    with pytest.raises(ValueError):guard_degree(lambda html:dict(requirements=groups),'test',[PROFILE])(policy.replace('Also complete','Optionally take'))


# Independently transcribed from the four degree branches and exact subject
# statements. These expected sets are not generated from the parser profile.
EXPECTED={
 'biology':{'chem-1161-chem-1162':(['CHEM 1163'],'required'),'phys-1151':(['PHYS 1152','PHYS 1153'],'options'),'phys-1161':(['PHYS 1162','PHYS 1163'],'options')},
 'biochemistry':{'chem-1161-chem-1162':(['CHEM 1163'],'required')},
 'chemistry':{'chem-2161-chem-2162':(['CHEM 2163'],'required'),'chem-2321-chem-2322':(['CHEM 2323'],'required'),'chem-2315-chem-2316':(['CHEM 2324'],'options'),'chem-2317-chem-2318':(['CHEM 2325'],'options')},
 'ecology-and-evolutionary-biology':{'phys-1161-phys-1162':(['PHYS 1163'],'options')},
}

@pytest.mark.parametrize('partner',EXPECTED)
def test_four_reviewed_degree_additions_have_independent_expected_roles_and_deltas(partner):
    pid='northeastern-university-artificial-intelligence-and-'+partner+'-bs-boston-bs-degree'
    seed=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());family=json.loads((ROOT/'data/families/northeastern-ai-combined-degrees.json').read_text());p=resolve_program(seed,family);groups={r['id']:r for r in p['requirements']};newids=set();delta={'required':0,'options':0,'unresolved':0}
    for anchor,(codes,expected_role) in EXPECTED[partner].items():
        node=groups[pid+'-req-'+anchor+'-concurrent'];ids={pid+'-'+c.lower().replace(' ','-') for c in codes}
        assert set(node['course_ids'])==ids and node['parent_id']==pid+'-req-'+anchor
        newids |= ids;delta[expected_role]+=len(codes)
        kinds=[]
        while node:
            kinds.append(node['kind']);node=groups.get(node['parent_id']) if node.get('parent_id') else None
        assert 'note' not in kinds
        assert ('options' if 'alternative' in kinds else 'required')==expected_role
    old=deepcopy(p);old['requirements']=[r for r in old['requirements'] if not newids.intersection(r['course_ids'])];old['courses']=[c for c in old['courses'] if c['id'] not in newids]
    before=requirement_profile(old);after=requirement_profile(p)
    assert {role:after[role]['count']-before[role]['count'] for role in delta}==delta
    for c in p['courses']:
        if c['id'] in newids:
            assert c['category']=='applications' and c['category_review']['status']=='reviewed'
            assert c['credits']==(1 if c['code'] in ['PHYS 1152','PHYS 1153','PHYS 1162'] else 0)


@pytest.mark.parametrize('partner',EXPECTED)
def test_optional_official_degree_and_subject_replay_preserves_exact_children(partner):
    cache=ROOT/'.cache/research/degree-audit-northeastern';pid='northeastern-university-artificial-intelligence-and-'+partner+'-bs-boston-bs-degree';file=cache/(pid+'.html')
    if not file.exists():pytest.skip('Optional actual-source cache')
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());m=import_module('atlas.adapters.'+pid+'.adapter');m.parse(file.read_text())
    for subject in {c.split()[0].lower() for targets,role in EXPECTED[partner].values() for c in targets}:
        if not (cache/(subject+'.html')).exists():pytest.skip('Optional subject cache')
        result=m.SOURCE_PARSERS[f'https://catalog.northeastern.edu/course-descriptions/{subject}/']((cache/(subject+'.html')).read_text())
        assert all(r in p['requirements'] for r in result['requirements'])
        for c in result['courses']:
            if any(c['id'] in r['course_ids'] for r in result['requirements']):
                reviewed=next(x for x in p['courses'] if x['id']==c['id'])
                assert c=={k:v for k,v in reviewed.items() if k!='category_review'}
