import json
from pathlib import Path
import pytest
from atlas.adapters.penn_bse.subjects import classify_observed
from atlas.adapters.penn_bse.core_resources import parse_resource
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def test_subject_does_not_follow_ai_pool_or_ambiguous_short_title():
 p={'courses':[dict(code='CIS 3500',name='Software Engineering',category='ai_ml'),dict(code='CIS 4500',name='Databases',category='ai_ml'),dict(code='ESE 6050',name='Modern Convex Optimization',category='ai_ml'),dict(code='ESE 2000',name='Data, Systems, Decisions',category='ai_ml')]}
 classify_observed(p)
 assert [c['category'] for c in p['courses']]==['foundations','systems','mathematics','other']
 p['courses'][0]['name']='New subject';classify_observed(p)
 assert p['courses'][0]['category']=='other'
 assert all('category_review' not in c for c in p['courses'])


def test_public_offering_scope_identity_and_subject_guard():
 html='<h1>CIS 2450, Spring 2026</h1><p>This course covers fundamentals of scaling computation across nodes.</p>'
 d=parse_resource(html,'cis2450');c=d['courses'][0]
 assert c['category']=='systems' and c['credits'] is None and c['prerequisites'] is None
 assert d['observed_offering']=='Spring 2026'
 assert 'category_review' not in c and 'curriculum_audit' not in d
 for old,new in [('Spring 2026','Spring 2030'),('CIS 2450','CIS 2451'),('fundamentals of scaling computation','introductory calculus')]:
  with pytest.raises(ValueError):parse_resource(html.replace(old,new),'cis2450')


def test_actual_prerequisite_observation_changes_without_certification():
 html='<h1>CIS 1210 Fall 2026 Data Structures and Algorithms</h1><p>Prerequisites: CIS 1200 and CIS 1600; must be completed. Grading: synthetic.</p>'
 a=parse_resource(html,'cis1210');b=parse_resource(html.replace('and CIS 1600','or CIS 1600'),'cis1210')
 assert 'and CIS 1600' in a['courses'][0]['prerequisites']
 assert 'or CIS 1600' in b['courses'][0]['prerequisites']
 assert a['observed_description_digests']!=b['observed_description_digests']
 assert not {'last_verified','curriculum_audit'} & a.keys()


def test_primary_fixed_core_independently_reviewed():
 p=json.loads(Path('data/programs/penn-bse-ai.json').read_text());validate_program(p)
 actual=requirement_profile(p)['required']
 assert actual['count']==10
 assert actual['categories']==dict(foundations=4,mathematics=5,ai_ml=0,systems=1,human_context=0,applications=0,electives=0,other=0)
 expected={'CIS 1100','CIS 1200','CIS 1210','CIS 3200','CIS 2450','MATH 1400','MATH 1410','CIS 1600','ESE 2030','ESE 4020'}
 assert all(c['category_review']['status']=='reviewed'for c in p['courses']if c['code'] in expected)
 assert next(c for c in p['courses']if c['code']=='CIS 2450')['prerequisites'] is None
 assert next(c for c in p['courses']if c['code']=='CIS 1100')['credits'] is None
 assert len([c for c in p['courses']if c.get('category_review')])==552


def test_independent_full_source_role_sets_and_unknown_evidence():
 p=json.loads(Path('data/programs/penn-bse-ai.json').read_text())
 e=json.loads(Path('research/degree-audit/penn.json').read_text())['programs'][0]
 observed=requirement_profile(p)
 assert e['status']=='blocked' and not e['remaining_work']
 for role in ['required','options','unresolved']:
  assert observed[role]['count']==len(e['expected_course_ids'][role])==e['expected_profile'][role]['count']
  assert observed[role]['categories']==e['expected_profile'][role]['categories']
 assert [observed[r]['count']for r in ['required','options','unresolved']]==[10,372,170]
 assert all(c['category']=='other' and c['category_review']['status']=='unclassified'for c in p['courses']if c['name'] is None)
 assert next(c for c in p['courses']if c['code']=='WRIT 1380')['category']=='other'
 assert next(c for c in p['courses']if c['code']=='ECON 2300')['category']=='mathematics'
 assert next(c for c in p['courses']if c['code']=='CIS 5190')['category']=='ai_ml'


def test_unapproved_inventory_row_supplies_title_without_eligibility():
 from atlas.adapters.penn_bse.inventory_titles import parse_inventory_with_titles
 rows=[dict(course4d='CIS 3500',title='Software Engineering',status='yes'),dict(course4d='EAS 2030',title='Engineering Ethics',status='no'),dict(course4d='ZZZ 1234',title='Unrelated title',status='no')]
 d=classify_observed(parse_inventory_with_titles(json.dumps(rows)))
 by={c['code']:c for c in d['courses']}
 assert set(by)=={'CIS 3500','EAS 2030'}
 assert by['EAS 2030']['name']=='Engineering Ethics' and by['EAS 2030']['category']=='human_context'
 assert not any(by['EAS 2030']['id']in r['course_ids'] for r in d['requirements'])
 rows[1]['title']='Changed ambiguous subject'
 changed=classify_observed(parse_inventory_with_titles(json.dumps(rows)))
 assert next(c for c in changed['courses']if c['code']=='EAS 2030')['category']=='other'
 rows[1]['status']='ask'
 conditional=parse_inventory_with_titles(json.dumps(rows))
 assert len([c for c in conditional['courses']if c['code']=='EAS 2030'])==1
 assert any(r['kind']=='note' and by['EAS 2030']['id']in r['course_ids']for r in conditional['requirements'])
 assert not any('category_review'in c for c in conditional['courses'])
