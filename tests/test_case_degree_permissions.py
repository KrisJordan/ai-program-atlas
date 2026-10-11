import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import case_degree_permissions as m


def fixture():
 return '<h1>Permissions</h1><h2>Requisites Have Not Been Met</h2><p>Prerequisites, corequisites and other requirement conditions: registration not allowed unless a Requisites Not Met permission is granted.</p><h2>There is a Career Restriction</h2><p>No registration without receiving permission from registrar or dean.</p>'


def test_permission_process_is_conditional_not_automatic():
 d=m.parse_permissions(fixture(),'test')
 assert 'not guaranteed enrollment or blanket waiver' in d['requirements'][0]['summary']
 assert 'curriculum_audit' not in d and d['curriculum_status']=='partial'
 with pytest.raises(ValueError,match='authority'):m.parse_permissions(fixture().replace('registrar or dean','instructor alone'),'test')
 with pytest.raises(ValueError,match='condition'):m.parse_permissions(fixture().replace('other requirement conditions','closed courses'),'test')


@pytest.mark.parametrize('a',['ba','bs'])
def test_published_restrictions_preserved_with_documented_request_route(a):
 p=json.loads(Path('data/programs',f'case-western-reserve-university-artificial-intelligence-{a}-degree.json').read_text())
 assert {m.PERMISSIONS_URL,m.FACULTY_URL}<={s['url'] for s in p['sources']}
 assert p['curriculum_status']=='complete' and not p['curriculum_audit']['unresolved_requirements']
 if a=='ba':
  for c in [c for c in p['courses'] if c['code'] in ['SCMG 462','SCMG 463']]:
   assert 'Master of Supply Chain Management program' in c['prerequisites']
 ledger=json.loads(Path('research/degree-audit/case-western.json').read_text())
 entry=next(e for e in ledger['programs'] if e['program_id']==p['id'])
 assert entry['status']=='in_progress' and not entry['blockers']


@pytest.mark.parametrize('url,parser',[(m.PERMISSIONS_URL,m.parse_permissions),(m.FACULTY_URL,m.parse_faculty)])
def test_optional_actual_permission_pages(url,parser):
 path=Path('.cache/http',hashlib.sha256(url.encode()).hexdigest()+'.body')
 if not path.exists():pytest.skip('Ignored actual source cache absent')
 assert parser(path.read_text(),'test')['requirements']
