"""Public-document extraction preserves conditional routes and unknown values."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import umich_hcai as adapter
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]


def fixture():
    codes=['SI 326','SI 376','SI 212','SI 310','SI 311','SI 332','SI 346','SI 405','SI 410','SI 411','SI 434','SI 465','PUBPOL 240','LING 321','PHIL 340','COMM 349','ARCH 411','TO 433','TO 438','EECS 449','EECS 492','AMCULT/DIGITAL 202','COGSCI 446','COMM 362','COMM 425']
    rows=[]
    for code in codes:
        credit={'PHIL 340':'2-4','COMM 349':'3-4','TO 438':'1.5','SI 311':'1.5'}.get(code,'3')
        rows.append(f'* {code}: Synthetic course ({credit} credits)')
    return '## **Human-Centered Artificial Intelligence**\n'+'\n'.join(rows)+'\n## **Frequently Asked Questions**'


def test_whole_conditional_routes_and_variable_credits(monkeypatch):
    raw=fixture();monkeypatch.setattr(adapter,'HANDBOOK_HASH',hashlib.sha256(raw.encode()).hexdigest())
    d=adapter.parse_handbook(raw)
    assert len(d['courses'])==25 and len(d['outcomes'])==5
    groups={r['id']:r for r in d['requirements']}
    assert groups['umich-hcai-routes']['kind']=='alternative'
    assert groups['umich-hcai-standard']['credits']==9
    assert groups['umich-hcai-bsi-electives']['credits']==6
    assert groups['umich-hcai-bsi-route']['course_ids']==['umich-hcai-si-310']
    assert 'umich-hcai-si-310' not in groups['umich-hcai-bsi-electives']['course_ids']
    assert len(groups['umich-hcai-standard']['course_ids'])==23
    assert next(c for c in d['courses'] if c['code']=='PHIL 340')['credits'] is None
    assert next(c for c in d['courses'] if c['code']=='TO 438')['credits']==1.5
    assert 'si-311-' in next(c for c in d['courses'] if c['code']=='SI 311')['id']
    assert not {'last_verified','curriculum_audit','curriculum_status'} & d.keys()
    with pytest.raises(ValueError):adapter.parse_handbook(raw.replace('3 credits','4 credits',1))


@pytest.mark.parametrize('raw',['<h1>Sign in</h1>','<h1>Access denied</h1>','Human-Centered Artificial Intelligence minor'])
def test_shells_and_partial_documents_rejected(raw):
    with pytest.raises(ValueError):adapter.parse_handbook(raw)
    with pytest.raises(ValueError):adapter.parse_table(raw)


def test_course_table_changes_and_advisory_prerequisites(monkeypatch):
    cells=['SI','465','Synthetic ML (ML)','','','Enforced preparation','Advisory preparation','Synthetic description','4']
    monkeypatch.setattr(adapter,'ROW_HASHES',{'465':hashlib.sha256(json.dumps(cells,ensure_ascii=False).encode()).hexdigest()})
    html='<table><tr>'+''.join('<td>'+s+'</td>' for s in cells)+'</tr></table>'
    d=adapter.parse_table(html);c=d['courses'][0]
    assert c['name']=='Synthetic ML' and c['credits']==4
    assert 'Advisory' in c['prerequisites'] and 'Winter 2026' in c['prerequisites']
    with pytest.raises(ValueError):adapter.parse_table(html.replace('Enforced preparation','Changed preparation'))
    with pytest.raises(ValueError):adapter.parse_table(html+html)


def test_seed_has_explicit_remaining_gaps_and_sources():
    d=json.loads((ROOT/'data/programs'/f'{adapter.PROGRAM_ID}.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
    assert d['first_offered']['value']=='Fall 2025'
    assert len(d['courses'])==25 and len(d['requirements'])==37
    assert sum(bool(c['description']) for c in d['courses'])==10
    assert sum(bool(c['prerequisites']) for c in d['courses'])==4
    assert all(c['syllabus'] is None for c in d['courses'])
    mod=importlib.import_module('atlas.adapters.'+adapter.PROGRAM_ID+'.adapter')
    assert set(mod.SOURCES)<={s['url'] for s in d['sources']}


def test_topics_do_not_transfer_graduate_metadata_to_undergraduate():
    row=['Winter','SI','311','151','','12345','Generative AI & UX','','','','','']
    html='<table><tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr></table>'
    d=adapter.parse_topics(html)
    assert 'courses' not in d and 'graduate' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):adapter.parse_topics(html.replace('>311<','>511<'))
    with pytest.raises(ValueError):adapter.parse_topics(html.replace('>Winter<','>Fall<'))


def test_lsa_home_rules_are_scoped_and_fail_closed(monkeypatch):
    text='Synthetic reviewed LSA minor policies'
    monkeypatch.setattr(adapter,'LSA_REVIEWED_HASH',hashlib.sha256(adapter.clean(text).encode()).hexdigest())
    d=adapter.parse_lsa_reviewed(text)
    assert len(d['requirements'])==6
    assert all(r['title'].startswith('LSA students:') for r in d['requirements'])
    assert all(r['parent_id']=='umich-hcai-root' for r in d['requirements'])
    overlap=next(r for r in d['requirements'] if r['id'].endswith('-overlap'))
    assert 'each major' in overlap['summary']
    assert not {'last_verified','curriculum_audit','curriculum_status'} & d.keys()
    with pytest.raises(ValueError):adapter.parse_lsa_reviewed(text+' changed')
    with pytest.raises(ValueError):adapter.parse_lsa_reviewed('<h1>Access denied</h1>')
