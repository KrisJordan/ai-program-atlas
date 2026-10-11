import hashlib,json
from collections import Counter
from pathlib import Path
import pytest
from atlas import db
from atlas.curriculum_profile import requirement_profile
from atlas.adapters import drexel_wi_course_review as m


def test_exact_subject_observer_guards_material_changes_and_missing_code(monkeypatch):
 title='TEST 101 [WI] Example communication 1.0-3.0 Credits'
 body='Audience-focused writing. Repeat Status: Can be repeated for credit Prerequisites: TEST 100 [Min Grade: C] Corequisite : EXAM 080'
 html='<main><h1>Example Subject</h1><div class="courseblock"><p class="courseblocktitle">'+title+'</p><p>'+body+'</p></div></main>'
 digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
 monkeypatch.setattr(m,'SPEC',{'pages':{'TEST':{'url':'https://example.edu/quarter/test/','heading':'Example Subject','source_id':'example','inventory_digest':digest(title),'auxiliary':{}}},'courses':{'TEST 101':{'id':'test-101','prefix':'TEST','digest':digest(title+' '+body),'description':'Writing for audiences.','category':'human_context'},'TEST 999':{'id':'test-999','prefix':'TEST','missing':True}}})
 o=m.parse(html,'TEST');c=o['courses'][0]
 assert c['credits'] is None and o['observed_credit_ranges']=={'TEST 101':'1.0-3.0'}
 assert o['observed_missing_courses']==['TEST 999']
 assert c['prerequisites']=='Prerequisites: TEST 100 [Min Grade: C]; Corequisites: EXAM 080'
 assert not {'requirements','curriculum_status','curriculum_audit'} & o.keys()
 assert 'category_review' not in c
 for bad in (html.replace('Audience-focused writing','Unrelated science'),html.replace('Grade: C','Grade: D'),html.replace('Example Subject','Another Subject'),html.replace('1.0-3.0','3.0'),html.replace('</main>','<input type="password"></main>'),html.replace('</main>','<div class="courseblock"><p class="courseblocktitle">TEST 999 New course 3.0 Credits</p></div></main>')):
  with pytest.raises(ValueError):m.parse(bad,'TEST')


@pytest.mark.parametrize('prefix',list(m.SPEC['pages']))
def test_actual_quarter_chapters_when_local_captures_present(prefix):
 f=Path('/tmp/drexel-wi-chapters',prefix+'.html')
 if not f.exists():pytest.skip('Local permitted public source unavailable')
 o=m.parse(f.read_text(),prefix)
 expected={code for code,e in m.SPEC['courses'].items() if e['prefix']==prefix and not e.get('missing')}
 assert {c['code'] for c in o['courses']}==expected
 assert all('category_review' not in c for c in o['courses'])


def test_source_enumerated_counts_and_nonobligatory_wi_scope():
 p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
 by={c['code']:c for c in p['courses']}
 assert len(m.SPEC['courses'])==198
 assert sum(bool(e.get('missing')) for e in m.SPEC['courses'].values())==2
 assert Counter(by[x]['category'] for x in m.SPEC['courses'])=={'human_context':108,'applications':67,'other':16,'mathematics':4,'foundations':3}
 assert by['NURS 422']['name']=='Leadership Concepts in Nursing' and by['NURS 422']['credits'] is None
 assert '0.0-3.0' in by['NURS 422']['description']
 assert by['ECON 350']['category']=='mathematics' and by['ARCH 431']['category']=='applications'
 assert by['BIO 473']['prerequisites'].startswith('Restrictions: Can enroll if major is BIO')
 assert 'BSN co-op' in by['NURS 423']['description']
 for code in ('BUSN 112','ENGL 340'):
  assert by[code]['description'] is None and by[code]['category_review']['status']=='unclassified'
 assert len(p['courses'])==281 and all(c.get('category_review') for c in p['courses'])
 e=next(x for x in json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())['programs'] if x['program_id']==m.PID)
 expected=e['expected_profile'];actual=requirement_profile(p)
 assert [expected[k]['count'] for k in ('required','options','unresolved')]==[11,72,198]
 for role in ('required','options','unresolved'):
  assert actual[role]['count']==expected[role]['count']
  assert {k:v for k,v in actual[role]['categories'].items() if v}==expected[role]['categories']
  assert actual[role]['classification']['unreviewed']==0
 assert e['status']=='blocked' and p['curriculum_status']=='partial'
 # The broad WI-only source remains a note; source review never turns it into198 obligations.
 assert next(r for r in p['requirements'] if r['id']==m.PID+'-policy-wi-options')['kind']=='note'
 assert len(set(e['expected_course_ids']['required'])|set(e['expected_course_ids']['options'])|set(e['expected_course_ids']['unresolved']))==281
 assert not p.get('course_identity_groups')
