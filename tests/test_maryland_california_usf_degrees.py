"""Small invented fixtures verify choice semantics, provenance and honest refresh scope."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

MD_BA='university-of-maryland-college-park-human-centered-ai-ba-degree'
MD_BS='university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
UCSD='university-of-california-san-diego-artificial-intelligence-bs-degree'
USF='university-of-south-florida-artificial-intelligence-bs-degree'
PIDS=[MD_BA,MD_BS,UCSD,'ucsb-ai-bs',USF]
ROOT=Path(__file__).resolve().parents[1]

def module(pid):return importlib.import_module('atlas.adapters.'+pid+'.adapter')
def row(code, name='Invented test title', credit='', indent=False, alternative=False):
 return f'<tr class="{"orclass" if alternative else ""}"><td class="codecol">'+ ('<div class="blockindent">' if indent else '')+('or ' if alternative else '')+code+('</div>' if indent else '')+f'</td><td>{name}</td><td class="hourscol">{credit}</td></tr>'
def comment(label):return f'<tr><td><span class="courselistcomment">{label}</span></td><td class="hourscol"></td></tr>'
def md_doc(title, tables, extra=''):
 return f'<main><h1>{title} Major</h1><div id="requirementstextcontainer">{extra}'+''.join(f'<h3>Track {i}</h3><table class="sc_courselist">{t}</table>' for i,t in enumerate(tables))+'</div></main>'

def test_maryland_or_rows_ranges_and_topics_are_not_flattened():
 tables=[comment('Core Requirements')+row('MATH140',credit='3-4')+row('MATH340',alternative=True)]
 tables+=[comment('Required Courses:')+row('CSAI473',credit='3')+comment('Electives (take two of the following):')+row('CMSC498','Topics (CMSC498E Invented)',indent=True)+row('CMSC498','Topics (CMSC498Y Different)',indent=True) for _ in range(5)]
 r=module(MD_BS).parse(md_doc('Artificial Intelligence: Computational Structures for AI Systems',tables))
 choice=next(n for n in r['requirements'] if 'umd-math140' in n['course_ids'])
 assert choice['kind']=='choose_courses' and choice['count']==1 and len(choice['course_ids'])==2
 assert next(c for c in r['courses'] if c['code']=='MATH140')['credits'] is None
 assert {c['id'] for c in r['courses'] if c['code']=='CMSC498'}=={'umd-cmsc498-cmsc498e','umd-cmsc498-cmsc498y'}
 assert all(n['count']==2 for n in r['requirements'] if n['title'].startswith('Electives'))
 assert r['curriculum_status']=='partial' and 'curriculum_audit' not in r
 with pytest.raises(ValueError):module(MD_BS).parse(md_doc('Artificial Intelligence: Computational Structures for AI Systems',tables[:-1]))

def test_maryland_ba_extra_required_course_and_approved_topics():
 rows=row('HCAI490','Example capstone')+comment('Specializations (students will choose 6 courses from one of the following specialization areas)')+comment('Law, Policy, and Governance Specialization (GVPT170 is required along with 6 other courses)')+row('GVPT170',indent=True)+row('PHIL438','Topics (PHIL438L Invented)<sup>1</sup>',indent=True)
 html=md_doc('Human-Centered Artificial Intelligence',[rows],'<p>MATH115; at least 2 courses must be from LING. Final semester capstone seminar. Students may replace this course with an internship.</p>')
 r=module(MD_BA).parse(html);pool=next(n for n in r['requirements'] if n['count']==6)
 assert 'umd-gvpt170' not in pool['course_ids']
 assert any(n['course_ids']==['umd-gvpt170'] and n['kind']=='all' for n in r['requirements'])
 assert any(n['title'].startswith('Approved content') for n in r['requirements'])
 changed=module(MD_BA).parse(html.replace('PHIL438','PHIL439'))
 assert any(c['code']=='PHIL439' for c in changed['courses'])
 assert not any(c['code']=='PHIL438' for c in changed['courses'])

def test_ucsd_range_expansion_excludes_broad_eligibility_ranges():
 codes=module(UCSD).codes
 assert codes('MATH 20A-B; COGS 118A-C; COGS 120–127')==['MATH 20A','MATH 20B','COGS 118A','COGS 118B','COGS 118C']+['COGS '+str(x) for x in range(120,128)]
 assert codes('CSE 100–194')==[]

def ucsb_fixture():
 return '<main><h1>Curriculum</h1><h2>Bachelor of Science in Artificial Intelligence</h2><h2>Core Areas</h2><p>CMPSC 165A: Invented AI title</p><h2>Degree Requirements</h2><p>180 total units. Major electives: 36 Science electives: 20 General Education and University requirements: 32</p><table><tr><th>Course Code</th><th>Name</th><th>Units</th></tr><tr><td>Math 3A</td><td>Invented math title</td><td>4</td></tr></table><h3>Sample 4-Year Plan</h3><table><tr><td>CMPSC 999</td></tr></table></main>'

def test_ucsb_excludes_sample_plan_and_reextracts_changes():
 r=module('ucsb-ai-bs').parse(ucsb_fixture())
 assert {c['code'] for c in r['courses']}=={'MATH 3A','CMPSC 165A'}
 assert 'curriculum_audit' not in r and 'last_verified' not in r
 r=module('ucsb-ai-bs').parse(ucsb_fixture().replace('Math 3A','Math 3B'))
 assert 'MATH 3B' in {c['code'] for c in r['courses']}
 with pytest.raises(ValueError):module('ucsb-ai-bs').parse(ucsb_fixture().replace('180 total units','Unknown units'))

@pytest.mark.parametrize('pid',PIDS)
def test_seeds_validate_and_sources_registered(pid):
 d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
 assert set(module(pid).SOURCES)<={s['url'] for s in d['sources']}
 assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
 with pytest.raises(ValueError):module(pid).parse('<main><h1>Unrelated program</h1></main>')

def test_usf_html_identity_does_not_refresh_brochure_requirements():
 r=module(USF).parse('<main><h1>Bachelor of Science in Artificial Intelligence</h1></main>')
 assert r['award_level']=='BSAI'
 assert not {'courses','requirements','curriculum_status','curriculum_audit','last_verified'}&r.keys()

def test_ucsd_seed_mathematical_substitutions_are_choices():
 d=json.loads((ROOT/'data/programs'/f'{UCSD}.json').read_text())
 for cid in ['ucsd-math-20c','ucsd-math-18']:
  n=next(n for n in d['requirements'] if cid in n['course_ids'])
  assert n['kind']=='choose_courses' and n['count']==1 and len(n['course_ids'])==2

def test_ucsd_metadata_requires_actual_course_blocks_and_preserves_logic():
 m=importlib.import_module('atlas.adapters.'+UCSD+'.course_metadata')
 html=''.join(f'<p class="course-name">{code}. Synthetic title (4)</p><p>Synthetic description. Prerequisites: CSE 12 and CSE 25 or CSE 29; major restriction.</p>' for code in sorted(m.CODES))
 r=m.parse(html)
 assert len(r['courses'])==8
 assert all(c['credits']==4 and c['prerequisites']=='CSE 12 and CSE 25 or CSE 29' for c in r['courses'])
 assert 'curriculum_audit' not in r
 with pytest.raises(ValueError):m.parse(html.replace('CSE 55.','CSE 56.'))
