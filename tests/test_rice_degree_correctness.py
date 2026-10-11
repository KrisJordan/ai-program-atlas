import json,importlib
from pathlib import Path
import pytest
from atlas.adapters.rice_degree_courses import parse_descriptions,classify_observed
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program
PID='rice-university-artificial-intelligence-bs-degree'


def test_domain_psychology_observation_requires_actual_subject():
 html='<h1>Psychology (PSYC)</h1><div class="courseblock"><p class="courseblocktitle">PSYC 203 - INTRODUCTION TO COGNITIVE PSYCHOLOGY</p><span class="credits">Credit Hours: 3</span><p class="courseblockdesc">Description: An introduction to topics in cognitive psychology, including memory.</p></div>'
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
 assert ledger['status']=='in_progress'and len(ledger['expected_course_ids']['required'])==13
 assert all(next(c for c in p['courses']if c['id']==cid)['category_review']['status']=='reviewed'for cid in ledger['expected_course_ids']['required'])
 notes={r['id']:r for r in p['requirements']}
 assert 'same academic year'in notes[PID+'-senior-design-sequence']['summary']
 assert 'reciprocal'in notes[PID+'-vision-conflict']['summary']
 assert 'Graduate level'in notes[PID+'-graduate-options']['summary']
 assert 'STAT 315'in notes[PID+'-statistics-route']['summary']


@pytest.mark.parametrize('dep',['comp','phil','psyc'])
def test_optional_source_reread_and_restriction_change(dep):
 path=Path('/tmp/rice-audit-'+dep+'.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 text=path.read_text();p=parse_descriptions(text,pid=PID,department=dep)
 assert p['courses']and all('category_review'not in c for c in p['courses'])
 if dep=='comp':
  assert len(p['requirements'])==4
  with pytest.raises(ValueError,match='graduate-only'):
   parse_descriptions(text.replace('Enrollment is limited to Graduate level students','Enrollment is open to undergraduate students'),pid=PID,department=dep)
