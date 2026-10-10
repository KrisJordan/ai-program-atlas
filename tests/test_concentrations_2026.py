"""Synthetic changed-rule fixtures; no raw university HTML committed."""
import json
from pathlib import Path
import pytest
from atlas.adapters.concentrations_2026 import parse_emory, parse_emory_faq, parse_bc, EMORY_FAQ_QUESTIONS
from atlas.requirements import validate_requirements, validate_curriculum_audit


def emory_fixture(n=2):
 return '<main><h1>CS BS, AI Concentration</h1><table><tr><td>Requirement</td><td>Course Name</td></tr><tr><td>CS 170</td><td>Programming</td></tr><tr><td>One (1) course chosen from:</td><td><p>Any 300-level CS classroom course not taken above.</p><p>Math 346: Optimization</p></td></tr>'+f'<tr><td>Two({n}) courses chosen from:</td><td><p>CS 442: Vision</p><p>CS 444: Learning</p></td></tr>'+'<tr><td>One (1) course chosen from:</td><td>Any 400-level CS classroom course not taken above</td></tr></table><p>All courses require a letter grade and minimum GPA of 2.0.</p></main>'


def test_emory_changes_choice_and_preserves_open_alternative():
 p=parse_emory(emory_fixture(),'p','s','https://example.edu');validate_requirements(p)
 assert len(p['courses'])==4
 assert next(r for r in p['requirements'] if r['id']=='emory-ai-choice-1')['kind']=='alternative'
 assert next(r for r in p['requirements'] if r['id']=='emory-ai-choice-1-math')['course_ids']==['emory-math-346']
 q=parse_emory(emory_fixture(1),'p','s','https://example.edu')
 assert next(r for r in q['requirements'] if r['id']=='emory-ai-choice-2')['count']==1
 assert q['observed_policy_digest']!=p['observed_policy_digest']
 assert q['curriculum_status']=='partial' and 'curriculum_audit' not in q and 'last_verified' not in q
 with pytest.raises(ValueError):parse_emory('<h1>Other program</h1>','p','s','u')


def test_emory_faq_observes_changed_substitution_policy():
 def fixture(n):return ''.join(f'<button aria-controls="a{i}">{q}</button><div id="a{i}">Requires {n} research credits.</div>' for i,q in enumerate(EMORY_FAQ_QUESTIONS))
 p=parse_emory_faq(fixture(3),'p','s','u');q=parse_emory_faq(fixture(4),'p','s','u')
 assert p['observed_policy_digest']!=q['observed_policy_digest']
 assert '4 research credits' in q['requirements'][5]['summary']
 with pytest.raises(ValueError):parse_emory_faq('<h1>FAQ</h1>','p','s','u')


def test_emory_review_scope_and_conditional_research():
 p=json.loads((Path(__file__).parents[1]/'data/programs/emory-university-cs-bs-ai-concentration-concentration-concentration.json').read_text());validate_requirements(p);validate_curriculum_audit(p)
 assert p['curriculum_status']=='complete' and len(p['courses'])==23
 core=next(r for r in p['requirements'] if r['id']=='emory-ai-core')
 assert len(core['course_ids'])==14 and 'emory-cs-497r' not in core['course_ids']
 research=next(r for r in p['requirements'] if r['id']=='emory-ai-research')
 assert research['kind']=='note' and 'substitution' in research['summary']
 assert all(c['credits'] is None and c['prerequisites'] is None for c in p['courses'])
 assert p['first_offered'] is None and p['catalog_year'] is None


def test_bc_section_scope_and_changed_count():
 def fixture(n):return f'<button data-target="#ai">Artificial Intelligence Concentration</button><div id="ai"><p>Students take {n} courses.</p><ul><li>Two core courses: Machine Learning and Deep Learning</li><li>Two CS 3000-level applications courses.</li><li>An AI ethics course</li><li>Capstone (4 credits - seniors only)</li></ul></div><div>Unrelated software courses CSCI9999</div>'
 p=parse_bc(fixture(6),'p','s','u');q=parse_bc(fixture(7),'p','s','u')
 assert p['courses']==[] and p['requirements'][0]['count']==6 and q['requirements'][0]['count']==7
 assert p['observed_policy_digest']!=q['observed_policy_digest']
 assert next(r for r in p['requirements'] if r['id']=='bc-ai-group-3')['credits']==4
 assert all('9999' not in r['summary'] for r in p['requirements'])


def test_bc_metadata_exact_membership_deduplicates_sections():
 from atlas.adapters.concentrations_2026 import parse_bc_courses
 rows=[dict(dept_code='CSCI',title='Machine Learning',crs_number='3345',crs_desc='Learning methods.',prereq='CSCI1102',credits='3'),dict(dept_code='CSCI',title='Unapproved AI Topic',crs_number='9999',credits='3')]
 raw=json.dumps(dict(msg='OK',payload=rows+[rows[0]]));p=parse_bc_courses(raw,'p','s','u')
 assert len(p['courses'])==1 and p['courses'][0]['code']=='CSCI 3345'
 assert p['courses'][0]['prerequisites']=='CSCI1102' and p['courses'][0]['credits']==3
 assert p['courses'][0]['credit_unit']=='unknown'
 q=parse_bc_courses(raw.replace('CSCI1102','CSCI1103'),'p','s','u')
 assert q['courses'][0]['prerequisites']=='CSCI1103' and q['observed_policy_digest']!=p['observed_policy_digest']


def duke_fixture(n=3):
 def section(i,text):return f'<div id="collapse-accordion-1385-{i}">{text}</div>'
 return '<main><h1>BS Concentration in AI and Machine Learning</h1><p>Fall 2026. At least 15 required units.</p>'+section(1,'<p>Prerequisites (4 units)</p><ol><li>COMPSCI 101L OR COMPSCI 102L OR equivalent</li><li>MATH 111L &amp; MATH 112L OR MATH 21 &amp; MATH 22</li><li>Statistics<ul><li>STA231/MATH 340</li><li>STA 240L</li></ul></li></ol>')+section(2,'<p>Core (5 units)</p><ol><li>COMPSCI 201</li><li>COMPSCI 230 OR COMPSCI 231D</li><li>COMPSCI 210D OR COMPSCI 250D</li><li>COMPSCI 270 OR two courses:<ul><li>one of MATH 202, MATH 212</li><li>AND one of MATH 216, MATH 218</li></ul></li><li>COMPSCI 330</li></ol>')+section(3,'<p>Systems (1 unit)</p><ul><li>COMPSCI 310 OR COMPSCI 510</li></ul>')+section(4,'<p>AI (1 unit)</p><ul><li>COMPSCI 370</li><li>COMPSCI 570</li></ul>')+section(5,'<p>ML (1 unit)</p><ul><li>COMPSCI 571 (cross STA 561, ECE 682)</li></ul>')+section(6,f'<p>Concentration Electives ({n} units)</p><p>{n} COMPSCI courses 200-level.</p><ul><li>COMPSCI 590 Topics<ul><li>Robot Learning</li><li>Deep Learning</li></ul></li><li>COMPSCI 575 - NLP, renumbered from COMPSCI 572 in Fall 2026</li><li>STA 332 - Inference (cross MATH 343), renumbered from STA 432 in Fall 2025 OR ECE 480 - Probability</li><li>one independent study</li></ul><p>Stellic</p>')+section(7,'Academic Plan Change')+section(8,'DUS approval')+'</main>'


def test_duke_nested_alternative_crosslists_topics_and_changed_rule():
 from atlas.adapters.concentrations_2026 import parse_duke_concentration
 p=parse_duke_concentration(duke_fixture(),'p','s','u');validate_requirements(p)
 assert next(r for r in p['requirements'] if r['id']=='duke-ai-core-3')['kind']=='alternative'
 pair=next(r for r in p['requirements'] if r['id']=='duke-ai-core-3-pair')
 assert pair['kind']=='all' and len([r for r in p['requirements'] if r['parent_id']==pair['id']])==2
 assert len([c for c in p['courses'] if c['code']=='COMPSCI 590'])==2
 assert sum(c['code']=='COMPSCI 571 / STA 561 / ECE 682' for c in p['courses'])==1
 assert not any(c['code'] in ['COMPSCI 572','STA 432','ECE 480'] for c in p['courses'])
 elective=next(r for r in p['requirements'] if r['id']=='duke-ai-group-6')
 ml=next(c for c in p['courses'] if c['code'].startswith('COMPSCI 571'))
 assert ml['id'] in elective['course_ids'] and elective['count']==3
 q=parse_duke_concentration(duke_fixture(4),'p','s','u')
 assert next(r for r in q['requirements'] if r['id']=='duke-ai-group-6')['count']==4
 assert q['observed_policy_digest']!=p['observed_policy_digest'] and 'curriculum_audit' not in q
 with pytest.raises(ValueError):parse_duke_concentration(duke_fixture().replace('collapse-accordion-1385-8','missing'),'p','s','u')


@pytest.mark.parametrize('pid,count',[
 ('boston-college-artificial-intelligence-concentration-concentration-concentration',1),
 ('duke-university-ai-and-machine-learning-concentration-concentration',87),
])
def test_partial_concentrations_keep_inventory_gaps_separate_from_metadata(pid,count):
 import importlib
 p=json.loads((Path(__file__).parents[1]/'data/programs'/f'{pid}.json').read_text());validate_requirements(p);validate_curriculum_audit(p)
 assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
 assert len(p['courses'])==count and p['first_offered'] is None
 adapter=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 assert set(adapter.SOURCE_PARSERS)==set(adapter.SOURCES[1:])
 if pid.startswith('duke'):
  assert all(c['credits'] is None and c['prerequisites'] is None for c in p['courses'])
  assert 'Stellic' in ' '.join(p['curriculum_audit']['unresolved_requirements'])
