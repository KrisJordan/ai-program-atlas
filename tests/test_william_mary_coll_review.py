import hashlib
import json
from html import escape
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas import db
from atlas.adapters import william_mary_coll_review as m
from atlas.adapters.national_curriculum_common import clean


@pytest.mark.parametrize('key',list(m.SPECS))
def test_material_coll_rules_are_guarded_and_open_criteria(key,monkeypatch):
    _,heading,rows=m.SPECS[key]
    html='<main><h1>'+heading+'</h1>'+''.join('<p>'+escape(v)+'</p>' for _,_,phrases,_ in rows for v in phrases)
    if key=='transfer':
        tables=''.join('<table><tr><td>Invented distinct pathway '+str(i)+'</td></tr></table>' for i in range(6))
        soup=BeautifulSoup(tables,'html.parser')
        digest=hashlib.sha256('\n'.join(clean(t.get_text(' ',strip=True)) for t in soup.find_all('table')).encode()).hexdigest()
        monkeypatch.setattr(m,'TRANSFER_TABLE_DIGEST',digest)
        html+=tables
    html+='</main>'
    o=m.parse(html,key)
    assert len(o['requirements'])==len(rows) and o['courses']==[]
    assert all(r['kind']=='note' and r['credit_unit']=='unknown' for r in o['requirements'])
    assert not {'curriculum_audit','curriculum_status','last_verified'} & o.keys()
    for _,_,phrases,_ in rows:
        with pytest.raises(ValueError):m.parse(html.replace(escape(phrases[0]),'altered condition'),key)
    if key=='transfer':
        with pytest.raises(ValueError,match='tables changed'):
            m.parse(html.replace('Invented distinct pathway 3','Changed exemption'),key)


@pytest.mark.parametrize('key',list(m.SPECS))
def test_actual_coll_source_cache_when_available(key):
    url,_,rows=m.SPECS[key];p=Path('.cache/http',hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not p.exists():pytest.skip('Ignored permitted source cache unavailable')
    assert len(m.parse(p.read_text(),key)['requirements'])==len(rows)


def test_integrated_coll_does_not_invent_named_courses_or_complete_degree():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    assert p['curriculum_status']=='partial' and len(p['courses'])==3
    rules={r['id']:r for r in p['requirements']}
    pathway=rules[m.PID+'-coll-transfer-pathways']['summary']
    assert 'Passport retains all three' in pathway
    assert 'retain one in-residence' in pathway
    assert 'retain two in-residence' in pathway
    assert 'cannot fill both' in rules[m.PID+'-coll-guide-proficiencies']['summary']
    assert all(r['course_ids']==[] for r in rules.values() if '-coll-' in r['id'])
    assert any('three or four' in x for x in p['curriculum_audit']['unresolved_requirements'])
