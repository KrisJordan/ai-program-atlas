import json,importlib
from pathlib import Path
import pytest
from atlas.adapters.rice_degree_courses import parse_descriptions,classify_observed
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program
PID='rice-university-artificial-intelligence-bs-degree'


def test_domain_psychology_observation_requires_actual_subject():
 html='<h1>Psychology (PSYC)</h1><div class="courseblock"><p class="courseblocktitle">PSYC 203 - INTRODUCTION TO COGNITIVE PSYCHOLOGY</p><span class="credits">Credit Hours: 3</span><p class="courseblockdesc">Description: An introduction to topics in cognitive psychology, including memory.</p></div>'
 html += '<div class=courseblock><p class=courseblocktitle>PSYC 430 - COMPUTATIONAL MODELING OF COGNITIVE PROCESSES</p><span class=credits>Credit Hours: 3</span><p class=courseblockdesc>Work modeling cognitive processes.</p></div><div class=courseblock><p class=courseblocktitle>PSYC 468 - HUMAN FACTORS IN ARTIFICIAL INTELLIGENCE</p><span class=credits>Credit Hours: 3</span><p class=courseblockdesc>Study societal impacts of AI.</p></div>'
 p=parse_descriptions(html,pid=PID,department='psyc')
 c=p['courses'][0]
 assert c['category']=='applications'and c['credits']==3 and c['prerequisites']is None
 assert 'category_review'not in c and 'curriculum_audit'not in p
 assert parse_descriptions(html.replace('Credit Hours: 3','Credit Hours: 4'),pid=PID,department='psyc')['courses'][0]['credits']==4
 with pytest.raises(ValueError,match='subject changed'):
  parse_descriptions(html.replace('topics in cognitive psychology','programming language design'),pid=PID,department='psyc')


def test_exact_source_spelling_and_systems_subject_are_preserved():
 rows=[dict(code='COMP 346',name='INTRODUCTION TO ARTIFICAL INTELLIGENCE',category='other'),dict(code='COMP 329',name='SYSTEMS FOR ARTIFICAL INTELLIGENCE',category='other')]
 classify_observed(rows)
 assert [c['category']for c in rows]==['ai_ml','systems']
 with pytest.raises(ValueError,match='title changed'):
  classify_observed([dict(code='COMP 346',name='Renamed subject',category='other')])


def test_manual_fixed_core_arithmetic_and_explicit_conflicts():
 p=json.loads(Path('data/programs',PID+'.json').read_text());validate_program(p)
 required=requirement_profile(p)['required']
 assert required['count']==13
 assert required['categories']==dict(foundations=3,mathematics=1,ai_ml=5,systems=2,human_context=1,applications=1,electives=0,other=0)
 ledger=json.loads(Path('research/degree-audit/rice.json').read_text())['programs'][0]
 assert ledger['status']=='blocked'and len(ledger['expected_course_ids']['required'])==13
 assert all(next(c for c in p['courses']if c['id']==cid)['category_review']['status']=='reviewed'for cid in ledger['expected_course_ids']['required'])
 notes={r['id']:r for r in p['requirements']}
 assert 'same academic year'in notes[PID+'-senior-design-sequence']['summary']
 assert 'reciprocal'in notes[PID+'-vision-conflict']['summary']
 assert 'Graduate level'in notes[PID+'-graduate-options']['summary']
 assert 'STAT315'in notes[PID+'-statistics-route']['summary']


@pytest.mark.parametrize('dep',['comp','phil','psyc'])
def test_optional_source_reread_and_restriction_change(dep):
 path=Path('/tmp/rice-audit-'+dep+'.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 text=path.read_text();p=parse_descriptions(text,pid=PID,department=dep)
 assert p['courses']and all('category_review'not in c for c in p['courses'])
 if dep=='comp':
  assert {PID+'-'+suffix for suffix in ['vision-conflict','graduate-options','statistics-route','senior-design-sequence']} <= {r['id'] for r in p['requirements']}
  with pytest.raises(ValueError,match='graduate-only'):
   parse_descriptions(text.replace('Enrollment is limited to Graduate level students','Enrollment is open to undergraduate students'),pid=PID,department=dep)



def test_statistics_blocker_requires_actual_exclusion_not_merely_missing_core():
 p=json.loads(Path('data/programs',PID+'.json').read_text())
 note=next(r for r in p['requirements'] if r['id']==PID+'-statistics-route')
 assert note['kind']=='note' and 'excludes prior STAT310/311 credit' in note['summary']
 assert not note.get('course_ids')
 assert 'STAT 310 / STAT 311' in next(r['summary'] for r in p['requirements'] if r['id'].endswith('course-entry-stat-315'))
 ledger=json.loads(Path('research/degree-audit/rice.json').read_text())['programs'][0]
 assert 'rice-ai-stat-315' not in ledger['expected_course_ids']['required']
 assert not any('Graduate level' in b['issue'] for b in ledger['blockers'])


def test_all_manual_course_sets_and_subject_totals_match_graph():
 p=json.loads(Path('data/programs',PID+'.json').read_text())
 ledger=json.loads(Path('research/degree-audit/rice.json').read_text())['programs'][0]
 observed=requirement_profile(p)
 for role in ['required','options','unresolved']:
  assert observed[role]['count']==ledger['expected_profile'][role]['count']
  assert observed[role]['categories']==ledger['expected_profile'][role]['categories']
 assert len(p['courses'])==43
 assert all(c['category_review']['status'] in ['reviewed','mixed'] for c in p['courses'])
 canonical={g['canonical_course_id'] for g in p['course_identity_groups']}
 aliases={cid for g in p['course_identity_groups'] for cid in g['course_ids']} - canonical
 assert {c['id'] for c in p['courses']} - aliases==set(ledger['expected_course_ids']['required']+ledger['expected_course_ids']['options'])
 assert observed['options']['source_record_count']==30 and observed['options']['count']==26
 assert len(p['course_identity_groups'])==3
 assert {c['code'] for c in p['courses'] if c['category_review']['status']=='mixed'}=={'COMP 631','COMP 462'}
 assert all(c['credit_unit']=='semester_hours' for c in p['courses'])


def test_statistics_recommendation_is_not_formal_prerequisite():
 from atlas.adapters.rice_degree_courses import IDENTITIES
 blocks=[]
 for code in ['STAT 310','STAT 311','STAT 314','STAT 315']:
  title,_,marker=IDENTITIES[code]
  blocks.append(f'<div class=courseblock><p class=courseblocktitle>{code} - {title}</p><span class=credits>Credit Hour: 1</span><p class=courseblockdesc>{marker}</p><p class=courseblockextra>Recommended Prerequisite(s): MATH 212.</p></div>')
 observation=parse_descriptions('<h1>Statistics (STAT)</h1>'+''.join(blocks),pid=PID,department='stat')
 assert all(c['prerequisites'] is None for c in observation['courses'])
 assert all('Recommended' in r['summary'] for r in observation['requirements'])
 changed=''.join(blocks).replace('Recommended Prerequisite(s):','Prerequisite(s):')
 observation=parse_descriptions('<h1>Statistics (STAT)</h1>'+changed,pid=PID,department='stat')
 assert all(c['prerequisites']=='Prerequisite(s): MATH 212.' for c in observation['courses'])
 assert all('category_review' not in c for c in observation['courses'])


def test_embedded_crosslist_recommendation_and_exclusion_are_observed():
 html='<h1>Data Science (DSCI)</h1><div class=courseblock><p class=courseblocktitle>DSCI 301 - PROBABILITY AND STATISTICS FOR DATA SCIENCE</p><span class=credits>Credit Hours: 4</span><p class=courseblockdesc>mathematical statistics and computation. Cross-list: STAT 315. Recommended Prerequisite(s): MATH 212. Mutually Exclusive: Cannot register for DSCI 301 if student has credit for STAT 310.</p></div>'
 d=parse_descriptions(html,pid=PID,department='dsci')
 assert d['courses'][0]['prerequisites'] is None
 summary=d['requirements'][0]['summary']
 assert 'Cross-list: STAT 315' in summary and 'Recommended Prerequisite(s): MATH 212' in summary
 assert 'Cannot register' in summary and 'STAT 310' in summary
 changed=parse_descriptions(html.replace('STAT 310','STAT 311'),pid=PID,department='dsci')
 assert changed['requirements'][0]['summary']!=summary
 assert changed['observed_description_digests']!=d['observed_description_digests']
