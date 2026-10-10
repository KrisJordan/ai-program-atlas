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
