import json
from pathlib import Path
import pytest
from atlas.adapters.njit_science_options import PID, SOURCES_BY_KIND, RELATIONSHIPS, parse_science


def fixture(kind):
    _, heading, codes = SOURCES_BY_KIND[kind]
    blocks=[]
    for code in codes:
        phrases=RELATIONSHIPS.get(code,([],[],''))[1]
        desc='. '.join(phrases)+'.' if phrases else 'Survey of the subject.'
        blocks.append(f'<div class="courseblock"><p class="courseblocktitle">{code}. Example {code}. 1 credit, 2 contact hours (0;2;0).</p><p class="courseblockdesc">{desc}</p></div>')
    return '<h1>'+heading+'</h1>'+''.join(blocks)


@pytest.mark.parametrize('kind,ncourses,nrules',[('physics',12,6),('chemistry',6,2),('biology',1,1)])
def test_options_are_conditional_and_extract_actual_rows(kind,ncourses,nrules):
    result=parse_science(fixture(kind),kind)
    assert len(result['courses'])==ncourses and len(result['requirements'])==nrules
    assert all(r['kind']=='note' for r in result['requirements'])
    assert all(c['credits']==1 for c in result['courses'])
    assert not {'curriculum_audit','last_verified'} & result.keys()
    changed=parse_science(fixture(kind).replace('1 credit,','2 credits,',1),kind)
    assert changed['courses'][0]['credits']==2


def test_alternatives_do_not_expand_ger_pool_or_impose_both_lectures():
    result=parse_science(fixture('physics'),'physics')
    assert 'PHYS 122' not in {c['code'] for c in result['courses']}
    r=next(r for r in result['requirements'] if 'phys-121a' in r['id'])
    assert r['course_ids']==['njit-phys-121a','njit-phys-121']
    result=parse_science(fixture('chemistry'),'chemistry')
    c=next(c for c in result['courses'] if c['code']=='CHEM 125A')
    assert c['prerequisites']=='Corequisites: CHEM 125 or CHEM 121'
    c=next(c for c in result['courses'] if c['code']=='CHEM 121')
    assert c['prerequisites'] is None


def test_changed_relationship_and_duplicate_or_missing_option_fail():
    html=fixture('physics')
    with pytest.raises(ValueError,match='condition changed'):
        parse_science(html.replace('Corequisite: PHYS 102','Corequisite: PHYS 103',1),'physics')
    with pytest.raises(ValueError,match='Missing reviewed'):
        parse_science(html.replace('PHYS 202. Example','PHYS 299. Example'),'physics')
    with pytest.raises(ValueError,match='duplicate'):
        parse_science(html+html,'physics')
    with pytest.raises(ValueError,match='condition changed'):
        parse_science(fixture('biology').replace('This laboratory course','Lecture-only course'),'biology')


def test_seed_preserves_pool_and_outstanding_scope():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text())
    c={c['code']:c for c in d['courses']};r={r['id']:r for r in d['requirements']}
    assert len(r[PID+'-njit-natural']['course_ids'])==36
    assert c['R216 206']['credits']==3 and 'PHYS 122' not in c
    assert c['PHYS 202']['prerequisites'] is None
    assert c['PHYS 203']['prerequisites']=='Prerequisite: None'
    assert len([r for r in d['requirements'] if '-science-option-' in r['id']])==9
    assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
