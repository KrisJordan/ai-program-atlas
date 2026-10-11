from importlib import import_module
from pathlib import Path
from copy import deepcopy
from collections import Counter
import hashlib,json
import pytest
PID='university-of-south-florida-artificial-intelligence-bs-degree'
m=import_module('atlas.adapters.'+PID+'.general_education_courses')
e=import_module('atlas.adapters.'+PID+'.ge_export')

def test_reviewed_pool_exact_membership_and_actual_subject_decisions():
    assert len(m.REVIEWS)==152 and len({r['code'] for r in m.REVIEWS})==152
    counts=Counter(a for r in m.REVIEWS for a in r['attributes'] if a in e.GE)
    assert counts=={'SGEC':1,'SGEH':6,'SGEM':4,'SGEN':12,'SGES':6,'UGEC':22,'UGEH':51,'UGEM':18,'UGEN':17,'UGES':21}
    by={r['code']:r for r in m.REVIEWS}
    assert by['CGS 2060']['category']=='foundations'
    assert by['ART 2602']['category']=='applications'
    assert by['PHI 2101']['category']=='mathematics'
    assert by['MAD 2470']['candidate_categories']==['mathematics','systems']
    assert by['MUN 1120']['category']=='applications'

@pytest.mark.parametrize('review',m.REVIEWS,ids=lambda r:r['code'])
def test_optional_actual_details_and_designation_guards(review):
    p=Path('.cache/research/usf-ge')/(review['code'].replace(' ','')+'.html')
    if not p.exists():pytest.skip('Optional private current course capture absent')
    html=p.read_text();out=m.parse_course(html,review)
    assert out['courses'][0]['id']==review['course_id']
    assert not {'curriculum_audit','last_verified','requirements'} & out.keys()
    assert 'category_review' not in out['courses'][0]
    with pytest.raises(ValueError):m.parse_course(html.replace('MainContent_lbltampacurr','changed'),review)

def test_full_seed_retains_context_roles_unknowns_and_conflicts():
    p=json.loads((Path('data/programs')/(PID+'.json')).read_text());by={c['code']:c for c in p['courses']}
    assert len(p['courses'])==170
    assert by['MUN 1120']['credits']==1 and by['FRE 1120']['credits']==4
    assert all(c['credit_unit']=='unknown' for c in by.values())
    assert 'Graduate Standing' in by['ENC 2251']['prerequisites'] and 'Exclude Graduate' in by['ENC 2251']['prerequisites']
    assert 'Majors Only,Non-Majors Only' in by['DAN 2100']['prerequisites']
    assert 'simultaneously' in by['PHY 2054']['prerequisites']
    groups=[r for r in p['requirements'] if r['id'].startswith('usf-ai-ge-pool-')]
    assert len(groups)==10 and all(r['kind']=='note' and r['count'] is None for r in groups)
    assert len({cid for r in groups for cid in r['course_ids']})==152
    from atlas.curriculum_profile import requirement_profile
    profile=requirement_profile(p)
    assert [profile[k]['count'] for k in ['required','options','unresolved']]==[24,5,141]
    assert p['curriculum_status']=='partial'

def test_optional_export_corroborates_every_current_attribute():
    path=Path('.cache/research/usf-ge/Course Inventory.xlsx')
    if not path.exists():pytest.skip('Optional private official export absent')
    rows=e.read_export(path);assert len(rows)==152
    for row,review in zip(rows,m.REVIEWS):
        assert row['code']==review['code'] and row['attributes']==review['attributes']

def export_fixture(path, records):
    import zipfile
    import xml.etree.ElementTree as ET
    ns=e.NS['s'];strings=[]
    sheet=ET.Element('{'+ns+'}worksheet');data=ET.SubElement(sheet,'{'+ns+'}sheetData')
    for rownum,row in enumerate([e.HEADERS,['','','','','','','One USF']]+records,1):
        node=ET.SubElement(data,'{'+ns+'}row',r=str(rownum))
        for col,value in zip('ABCDEFG',row):
            index=len(strings);strings.append(str(value));cell=ET.SubElement(node,'{'+ns+'}c',r=col+str(rownum),t='s');ET.SubElement(cell,'{'+ns+'}v').text=str(index)
    shared=ET.Element('{'+ns+'}sst')
    for value in strings:ET.SubElement(ET.SubElement(shared,'{'+ns+'}si'),'{'+ns+'}t').text=value
    with zipfile.ZipFile(path,'w') as z:z.writestr('xl/sharedStrings.xml',ET.tostring(shared));z.writestr('xl/worksheets/sheet1.xml',ET.tostring(sheet))
    return path


def test_export_preserves_overlapping_designations_and_nonstandard_credit_amount(tmp_path):
    path=export_fixture(tmp_path/'small.xlsx',[['Arts','Music','MUN','1120','Synthetic ensemble',1,'UGEH'],['Science','Biology','BSC','2085','Synthetic anatomy',3,'SGEN, UGEN']])
    rows=e.read_export(path)
    assert rows[0]['credits']==1 and rows[1]['attributes']==['SGEN','UGEN']
    assert len(rows)==2  # Multi-designation membership does not duplicate a course.

@pytest.mark.parametrize('records',[[],[['A','B','CS','1','Unrelated',3,'CAP']], [['A','B','AA','1','Example',3,'UGEC']]*2])
def test_invalid_export_never_turns_into_pool_deletion(tmp_path,records):
    with pytest.raises(ValueError):e.read_export(export_fixture(tmp_path/'invalid.xlsx',records))
