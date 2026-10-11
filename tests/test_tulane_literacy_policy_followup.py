import json
from pathlib import Path
import pytest
from atlas.adapters.tulane_literacy_policy_followup import parse_declaration,parse_university
ROOT=Path(__file__).resolve().parents[1]
PID='tulane-ai-literacy-minor'

def test_declaration_observer_requires_actual_steps():
 html='<h1>Major or Minor Declarations</h1><div><button>Declaring All Other Programs</button><ol>'+''.join('<li>Step to obtain department approval and submit the signed declaration form for processing.</li>' for _ in range(3))+'</ol></div>'
 a=parse_declaration(html,PID);b=parse_declaration(html.replace('department approval','advisor approval'),PID)
 assert a['observed_policy_sha256']!=b['observed_policy_sha256']
 assert a['requirements']==[] and 'curriculum_audit' not in a
 with pytest.raises(ValueError):parse_declaration(html.replace('All Other','Some Other'),PID)

def test_university_policy_changed_text_queues_review():
 html='<h1>The University</h1>'+''.join('<h2>'+h+'</h2><p>'+'A semester credit policy with reviewed text and department approval. '*2+'</p>' for h in ['Credit-Hour','Curriculum Effective Date'])
 a=parse_university(html,PID);b=parse_university(html.replace('semester','quarter'),PID)
 assert a['observed_policy_sections']!=b['observed_policy_sections']
 assert a['curriculum_status']=='partial' and 'last_verified' not in a
 with pytest.raises(ValueError):parse_university(html.replace('Credit-Hour','Other Heading'),PID)

def test_curated_credit_conflict_stays_visible():
 from atlas.db import validate_program
 d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
 assert d['curriculum_status']=='partial' and any('CMPS 1500' in x for x in d['curriculum_audit']['unresolved_requirements'])
 assert all(x['credit_unit']=='semester_hours' for x in d['courses']+d['requirements'] if x['credits'] is not None)
 assert next(c for c in d['courses'] if c['code']=='CMPS 1500')['credits']==4
 assert next(r for r in d['requirements'] if r['title']=='Published minor credit total')['credits']==15
 assert any('College Advising' in r['summary'] for r in d['requirements'])
