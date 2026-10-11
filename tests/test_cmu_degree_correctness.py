import json
from pathlib import Path
from atlas.adapters.cmu_bs.core_subjects import classify_observed
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def test_exact_systems_identity_and_renamed_subject():
 p={'courses':[dict(code='15-213',name='Introduction to Computer Systems',category='foundations')]}
 classify_observed(p)
 assert p['courses'][0]['category']=='systems'
 p['courses'][0]['name']='Changed title'
 classify_observed(p)
 assert p['courses'][0]['category']=='other'and 'category_review'not in p['courses'][0]


def test_independent_thirteen_course_core_and_explicit_unknowns():
 p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());validate_program(p)
 r=requirement_profile(p)['required']
 assert r['count']==13
 assert r['categories']==dict(foundations=4,mathematics=4,ai_ml=2,systems=1,human_context=1,applications=0,electives=0,other=1)
 fixed=['15-122','15-150','15-210','15-213','15-251','07-280','07-380','07-128','99-101','21-120','21-122','21-241','36-401']
 ledger=json.loads(Path('research/degree-audit/cmu.json').read_text())['programs'][0]
 assert {next(c['code']for c in p['courses']if c['id']==cid)for cid in ledger['expected_course_ids']['required']}==set(fixed)
 for code in ['07-128']:
  c=next(c for c in p['courses']if c['code']==code)
  assert c['category']=='other'and c['category_review']['status']=='unclassified'
 assert '15-112'not in fixed


def test_core_competency_description_and_changed_subject_guard():
 import pytest
 from atlas.adapters.cmu_bs.core_seminar import parse
 html='<h1>Carnegie Mellon University-Wide Studies Courses</h1><p>2026-2027 Catalog</p><dl class="courseblock"><dt>99-101 Core@CMU</dt><dd>Fall and Spring: 3 units<br>Collaboration and Teamwork; Communication and Presentation; Information and Data Literacy; Intercultural and Global Literacy.</dd></dl>'
 observed=parse(html)
 c=observed['courses'][0]
 assert c['category']=='human_context' and c['credits']==3 and c['prerequisites']is None
 assert 'category_review'not in c and 'curriculum_audit'not in observed
 changed=parse(html.replace('3 units','4 units'))
 assert changed['courses'][0]['credits']==4 and changed['observed_description_digests']!=observed['observed_description_digests']
 with pytest.raises(ValueError):parse(html.replace('Communication','Programming'))
 with pytest.raises(ValueError):parse(html.replace('99-101 Core@CMU','99-102 Core@CMU'))


def test_all_source_reviewed_roles_match_manual_sets_and_do_not_promote_preparation():
 p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());validate_program(p)
 ledger=json.loads(Path('research/degree-audit/cmu.json').read_text())['programs'][0]
 for kind in ['required','options','unresolved']:
  expected=ledger['expected_profile'][kind];actual=requirement_profile(p)[kind]
  assert actual['count']==expected['count'] and actual['categories']==expected['categories']
 assert ledger['expected_course_ids']['unresolved']==['cmu-15-112']
 assert {'cmu-70-100','cmu-19-440','cmu-17-416'}<=set(ledger['expected_course_ids']['options'])
 assert ledger['expected_profile']['options']['count']==259
 assert ledger['status']=='blocked' and ledger['remaining_work']==[]
