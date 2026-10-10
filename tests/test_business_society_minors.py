"""Guard course choices and honest limits in five reviewed minor records."""
import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ('university-of-notre-dame-ai-analytics-in-business-minor-minor','nd',22),
 ('notre-dame-ai-essentials-business-minor','nd-essentials',12),
 ('university-of-miami-artificial-intelligence-for-business-technology-minor-minor','miami',15),
 ('rochester-institute-of-technology-artificial-intelligence-minor-minor','rit',17),
 ('rit-ai-society-minor','rit-society',16)]

def load(pid):
 spec=importlib.util.spec_from_file_location('adapter',ROOT/'atlas/adapters'/pid/'adapter.py')
 a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);return a

@pytest.mark.parametrize('pid,key,count',CASES)
def test_extracts_source_courses_without_certifying(pid,key,count):
 a=load(pid);html=(ROOT/'tests/fixtures/business_society_minors'/(key+'.html')).read_text();x=a.parse(html)
 assert len(x['courses'])==count
 assert x['curriculum_status']=='partial'
 assert 'curriculum_audit' not in x and 'last_verified' not in x
 assert all(c['description'] is None for c in x['courses'])
 with pytest.raises(ValueError):a.parse('<h1>Other Minor</h1>'+html.split('</h1>',1)[1])

@pytest.mark.parametrize('pid,key,count',CASES)
def test_reviewed_data_valid_and_remaining_gaps_explicit(pid,key,count):
 d=json.loads((ROOT/'data/programs'/(pid+'.json')).read_text());validate_program(d)
 assert d['curriculum_status']==('complete' if key.startswith('rit') else 'partial')
 assert bool(d['curriculum_audit']['unresolved_requirements']) == (not key.startswith('rit'))
 assert len(d['courses']) == (38 if key == 'nd' else count)


def test_nd_dedup_preserves_distinct_codes_and_fractional_choices():
 a=load(CASES[0][0]);x=a.parse((ROOT/'tests/fixtures/business_society_minors/nd.html').read_text())
 codes=[c['code'] for c in x['courses']]
 assert codes.count('ITAO 30660')==1
 assert 'MARK 30120' in codes and 'MARK 30130' in codes
 y=load(CASES[1][0]).parse((ROOT/'tests/fixtures/business_society_minors/nd-essentials.html').read_text())
 assert y['requirements'][1]['credits']==7.5
 assert y['requirements'][1]['kind']=='note' # no guessed normalized unit
 assert [c for c in y['courses'] if c['code']=='FIN 40260 / 40262']


def test_miami_prerequisite_choice_is_separate_from_twelve_credits():
 x=load(CASES[2][0]).parse((ROOT/'tests/fixtures/business_society_minors/miami.html').read_text())
 req=x['requirements'];assert [r['count'] for r in req]==[1,None,2,1]
 assert [r['credits'] for r in req]==[None,3,6,3]
 assert all(c['credits'] is None for c in x['courses'])


def test_rit_changed_choice_and_course_name_are_observed():
 a=load(CASES[3][0]);html=(ROOT/'tests/fixtures/business_society_minors/rit.html').read_text()
 x=a.parse(html.replace('Select five','Select four').replace('AI for Programmers','New AI Course'))
 assert x['requirements'][1]['count']==4
 assert x['courses'][0]['name']=='New AI Course'
 assert x['requirements'][0]['credits']==1
 assert x['courses'][0]['credits'] is None # group amount is not a course-level inference


def test_rit_rejects_degree_heading_and_unrecognized_choice():
 a=load(CASES[3][0]);html=(ROOT/'tests/fixtures/business_society_minors/rit.html').read_text()
 with pytest.raises(ValueError):a.parse(html.replace('<h1>Artificial Intelligence Minor</h1>','<h1>Artificial Intelligence</h1>'))
 with pytest.raises(ValueError):a.parse(html.replace('Select five','Select an advisor-approved set'))


def test_nd_current_linked_page_expansion_remains_observation_only():
    a = load(CASES[0][0])
    x = a.parse((ROOT/'tests/fixtures/business_society_minors/nd-current.html').read_text())
    assert a.SOURCES[0].endswith('/ai-analytics-in-business-minor/')
    assert len(x['courses']) == 36
    assert len(x['requirements'][1]['course_ids']) == 34
    assert 'curriculum_audit' not in x
    assert all(c['credit_unit'] == 'unknown' for c in x['courses'])
    # Credit normalization belongs to the separate academic-code review, not this HTML parser.
    assert [c for c in x['courses'] if c['code'] == 'FIN 40262']
