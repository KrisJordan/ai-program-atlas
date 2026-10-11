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
 assert r['categories']==dict(foundations=4,mathematics=4,ai_ml=2,systems=1,human_context=0,applications=0,electives=0,other=2)
 fixed=['15-122','15-150','15-210','15-213','15-251','07-280','07-380','07-128','99-101','21-120','21-122','21-241','36-401']
 ledger=json.loads(Path('research/degree-audit/cmu.json').read_text())['programs'][0]
 assert {next(c['code']for c in p['courses']if c['id']==cid)for cid in ledger['expected_course_ids']['required']}==set(fixed)
 for code in ['07-128','99-101']:
  c=next(c for c in p['courses']if c['code']==code)
  assert c['category']=='other'and c['category_review']['status']=='unclassified'
 assert '15-112'not in fixed
