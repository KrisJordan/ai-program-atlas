import copy,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import northeastern_history_course_reviews as m
from atlas.adapters.northeastern_courseleaf import clean
PID='northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree'

def test_changed_historical_subject_cannot_reuse_manual_summary(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">HIST 3330. Synthetic historical inquiry. (4 Hours)</p><p class="cb_desc">Synthetic history of institutions.</p><p class="courseblockextra">Prerequisite(s): A or B with C</p></div>'
    e=copy.deepcopy(m.SPEC['courses']['HIST 3330']);e['block_digest']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser')).encode()).hexdigest();e['description_guard']='Synthetic history of institutions.';monkeypatch.setitem(m.SPEC['courses'],'HIST 3330',e)
    def page(b):return '<p>2026-2027 Edition</p><div id="site-title"><h1>'+m.SPEC['sources']['HIST']['heading']+'</h1></div><div id="textcontainer">'+b+'</div>'
    result=m.parse_subject(page(block),program_id=PID,subject='HIST',codes=['HIST 3330']);course=result['courses'][0]
    assert course['credits']==4 and course['prerequisites']=='A or B with C'
    assert 'category_review'not in course and result['requirements']==[]
    for bad in [block.replace('institutions','biology'),block.replace('4 Hours','3 Hours'),block.replace('with C','with B'),block+block,'']:
        with pytest.raises(ValueError):m.parse_subject(page(bad),program_id=PID,subject='HIST',codes=['HIST 3330'])
    with pytest.raises(ValueError):m.parse_subject(page(block).replace('2026-2027','2025-2026'),program_id=PID,subject='HIST',codes=['HIST 3330'])


def test_manual_scope_and_source_specific_interpretation():
    e=m.SPEC['courses'];assert len(e)==31 and sum(len(c['targets'])for c in e.values())==31
    assert all(c['category']=='human_context'and c['review']['status']=='reviewed' for c in e.values())
    assert 'not operational cybersecurity' in e['HIST 1389']['review']['rationale']
    assert 'not as technical computing instruction' in e['HIST 1390']['review']['rationale']
    assert 'not language proficiency' in e['HIST 1252']['review']['rationale']
    assert 'minimum grade of C' in e['HIST 3330']['prerequisites']
    assert all(c['prerequisites']is None for code,c in e.items()if code!='HIST 3330')
    assert 'no reciprocal identity group' in e['HIST 2303']['conditions'][0]['summary']


def test_optional_exact_chapter_replay():
    path=Path('.cache/research/degree-audit-northeastern/hist.html')
    if not path.exists():pytest.skip('Optional ignored history source capture absent')
    result=m.parse_subject(path.read_text(),program_id=PID,subject='HIST')
    assert len(result['courses'])==31 and result['requirements']==[]
    assert all('category_review'not in c for c in result['courses'])
