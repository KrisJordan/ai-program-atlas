"""Independent core expectations from the Case 2026–2027 requirement tables."""
import importlib
import json
from pathlib import Path

import pytest
from atlas.adapters.case_degree_courses import classify_observed, parse_descriptions, BASE
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program

# Synthetic source blocks use the public structure, not a copied catalog document.
ROWS = [
 ('CSDS 132','Programming in Java','3','Algorithmic problem solving and object-oriented design.'),
 ('CSDS 134','Programming in Python','3','Introduction to computer science and programming; algorithmic problem solving.'),
 ('CSDS 233','Introduction to Data Structures','4','Different representations of data; asymptotic analysis. Prereq: CSDS 134.'),
 ('CSDS 237','The Python Programming Language','1','Programming in Python; object-oriented programming. Prereq: CSDS 132.'),
 ('CSDS 302','Discrete Mathematics','3','Discrete mathematics and mathematical induction. Prereq: MATH 122.'),
 ('CSDS 310','Algorithms','3','Algorithm design and analysis; dynamic programming. Prereq: CSDS 233 with a C or higher.'),
 ('CSDS 330','Introduction to Artificial Intelligence','3','Artificial intelligence and knowledge representation.'),
 ('CSDS 340','Introduction to Machine Learning','3','Algorithms for machine learning and their implementation.'),
 ('CSDS 395A','Senior Project in Artificial Intelligence','4','Artificial intelligence models for practical applications. Prereq: Senior standing.'),
]

def fixture():
 return '<h1>Computer and Data Sciences (CSDS)</h1>'+''.join(f'<div class="courseblock"><p class="courseblocktitle">{code}. {title}. {hours} Units.</p><p class="courseblockdesc">{desc}</p></div>' for code,title,hours,desc in ROWS)


def test_exact_course_observations_and_changed_metadata():
 d=parse_descriptions(fixture(),pid='test',award='BA',department='csds')
 c={c['code']:c for c in d['courses']}
 assert c['CSDS 233']['category']=='foundations'
 assert c['CSDS 302']['category']=='mathematics'
 assert c['CSDS 237']['credits']==1 and c['CSDS 237']['credit_unit']=='unknown'
 assert c['CSDS 132']['prerequisites'] is None
 changed=parse_descriptions(fixture().replace('Prer'+'eq: CSDS 134.', 'Prereq: CSDS 132.'),pid='test',award='BA',department='csds')
 assert next(c for c in changed['courses'] if c['code']=='CSDS 233')['prerequisites']=='Prereq: CSDS 132.'
 assert changed['observed_description_digests']!=d['observed_description_digests']
 assert 'curriculum_audit' not in d and all('category_review' not in c for c in d['courses'])


def test_changed_identity_or_subject_rejects_prior_classification():
 with pytest.raises(ValueError,match='title changed'):
  parse_descriptions(fixture().replace('Programming in Java','Topics in Java'),pid='test',award='BA',department='csds')
 with pytest.raises(ValueError,match='subject evidence'):
  parse_descriptions(fixture().replace('dynamic programming','historical biographies'),pid='test',award='BA',department='csds')
 unknown=[dict(code='CSDS 999',name='Synthetic computing elective',category='other')]
 assert classify_observed(unknown)[0]['category']=='other'


@pytest.mark.parametrize('award',['BA','BS'])
def test_reviewed_fixed_set_and_programming_bundle(award):
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 p=json.loads(Path('data/programs',pid+'.json').read_text());validate_program(p)
 # Manual official core list; programming alternatives are deliberately absent.
 expected=['MATH 121','MATH 307','CSDS 233','CSDS 302','CSDS 310','CSDS 330','CSDS 340','CSDS 395A']+(['ENGR 399'] if award=='BS' else [])
 rules={r['id']:r for r in p['requirements']}
 def fixed(r):
  if r['kind']!='all':return False
  return not r['parent_id'] or fixed(rules[r['parent_id']])
 fixed_ids={c for r in rules.values() if fixed(r) for c in r['course_ids']}
 byid={c['id']:c for c in p['courses']}
 assert {byid[c]['code'] for c in fixed_ids}==set(expected)
 categories={'foundations':2,'mathematics':3,'ai_ml':3,'systems':0,'human_context':int(award=='BS'),'applications':0,'electives':0,'other':0}
 profile=requirement_profile(p)
 assert profile['required']['count']==len(expected)
 assert profile['required']['categories']==categories
 assert profile['options']['categories']['foundations']==3
 assert all(byid[c]['category_review']['status']=='reviewed' for c in fixed_ids)
 bundle=next(r for r in p['requirements'] if r['course_ids']==[f'case-{award.lower()}-csds-132',f'case-{award.lower()}-csds-237'])
 assert bundle['kind']=='all' and rules[bundle['parent_id']]['kind']=='alternative'
 assert all('csds-'+x not in ' '.join(fixed_ids) for x in ['132','134','237'])
 # Course-level prerequisites must not silently create fixed degree obligations.
 assert next(c for c in p['courses'] if c['id']==f'case-{award.lower()}-csds-310')['prerequisites'].count('C or higher')==2
 audit=json.loads(Path('research/degree-audit/case-western.json').read_text())
 record=next(x for x in audit['programs'] if x['program_id']==pid)
 assert record['status']=='in_progress' and record['expected_profile'] is None
 assert set(record['expected_course_ids']['required'])==fixed_ids


@pytest.mark.parametrize('award',['BA','BS'])
def test_optional_reread_catalog(award):
 path=Path('/tmp/case-audit-'+award.lower()+'.html')
 if not path.exists():pytest.skip('Optional ignored source cache absent')
 pid=f'case-western-reserve-university-artificial-intelligence-{award.lower()}-degree'
 m=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 d=m.parse(path.read_text())
 assert next(c for c in d['courses'] if c['code']=='CSDS 233')['category']=='foundations'
 assert next(c for c in d['courses'] if c['code']=='CSDS 302')['category']=='mathematics'
 assert BASE+'csds/' in m.SOURCE_PARSERS
 assert all('category_review' not in c for c in d['courses'])
