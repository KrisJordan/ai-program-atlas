import importlib.util,json
from pathlib import Path
import pytest
from atlas.db import validate_program
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('binghamton',ROOT/'atlas/adapters/binghamton-cs-ai-track/adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def fixture():
 def widget(n):return f'<ul data-acalog-course-prefix="CS" data-acalog-course-code="{n}"><li>Loading Course Info...</li></ul>'
 return '<h1>BSCS with Artificial Intelligence Track</h1><div id="content1"><p>four of the BSCS electives; two are required, and two are electives</p><h3>Required courses</h3>'+widget('436')+widget('465')+'<h3>Electives</h3>'+widget('417')+'<p>CS 481E - Test special topic</p><h3>For more information</h3><p>CS 999 - Not eligible</p></div>'
def test_widgets_and_inline_scope():
 p=m.parse(fixture());assert {c['code'] for c in p['courses']}=={'CS 436','CS 465','CS 417','CS 481E'}
 assert p['requirements'][0]['kind']=='all' and p['requirements'][1]['count']==2
 assert 'last_verified' not in p and 'curriculum_audit' not in p
 assert next(c for c in p['courses'] if c['code']=='CS 436')['name'] is None
 assert next(c for c in p['courses'] if c['code']=='CS 481E')['name']=='Test special topic'
def test_changed_option_observed():
 p=m.parse(fixture().replace('"417"','"498"'));assert 'CS 498' in {c['code'] for c in p['courses']}
@pytest.mark.parametrize('old,new',[('content1','wrong'),('two are required','three are required'),('Required courses','Other courses'),('Electives</h3>','Other</h3>'),('data-acalog-course-prefix="CS"','data-acalog-course-prefix="OTHER"')])
def test_partial_failure_refuses_destructive_candidate(old,new):
 with pytest.raises(ValueError):m.parse(fixture().replace(old,new))
def test_reviewed_seed():
 p=json.loads((ROOT/'data/programs/binghamton-cs-ai-track.json').read_text());validate_program(p)
 assert p['curriculum_status']=='partial' and p['first_offered'] is None
 assert len(p['courses'])==13 and sum(c['prerequisites'] is not None for c in p['courses'])==11
 assert sum(c['credits'] is not None for c in p['courses'])==1
 assert any('CS 417' in s for s in p['curriculum_audit']['unresolved_requirements'])
