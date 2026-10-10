import importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PID='case-applied-ai-minor'
def adapter():
 s=importlib.util.spec_from_file_location('case_applied',ROOT/'atlas/adapters'/PID/'adapter.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_applied_choices_and_observed_changes():
 html=(ROOT/'tests/fixtures/next_degrees/case-applied.html').read_text()
 d=adapter().parse(html)
 assert len(d['courses'])==25
 assert [r['count'] for r in d['requirements'][:3]]==[None,1,2]
 assert len(d['requirements'][2]['course_ids'])==19
 assert d['requirements'][2]['credits']==6
 changed=adapter().parse(html.replace('at least two','at least three'))
 assert changed['requirements'][2]['count']==3
 assert d['curriculum_status']=='partial' and 'curriculum_audit' not in d and 'last_verified' not in d
 with pytest.raises(ValueError):adapter().parse(html.replace('Choose one of the following:','Unrecognized choice'))
def test_case_review_preserves_approval_conflict_and_core_restrictions():
 from atlas.db import validate_program
 d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
 assert d['curriculum_status']=='complete' and d['status']=='unknown'
 assert d['first_offered'] is None
 assert len(d['courses'])==25 and len(d['requirements'])==9
 assert 'In Approval' in ' '.join(d['notes'])
 assert all('300-level CSDS' in c['prerequisites'] for c in d['courses'][:2])
 assert any('semester' in s['locator'] for s in d['sources'])
