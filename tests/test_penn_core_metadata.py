"""Exact Penn core identity and term handling; no raw course pages in fixtures."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters.penn_cs.course_metadata import RESOURCE_SPECS,WHARTON,parse_resource,parse_wharton


def test_applied_ml_observes_prerequisite_change_and_separate_course_numbers():
 url=next(iter(RESOURCE_SPECS))
 h='<title>CIS 4190/5190 Applied Machine Learning Fall 2026</title><p>syllabus</p><p><b>Prerequisites:</b> Probability and linear algebra.</p>'
 p=parse_resource(h,pid='p',url=url)
 assert [c['code'] for c in p['courses']]==['CIS 4190','CIS 5190']
 assert all(c['credits'] is None and c['syllabus']==url for c in p['courses'])
 q=parse_resource(h.replace('Probability','Statistics'),pid='p',url=url)
 assert q['courses'][0]['prerequisites']=='Statistics and linear algebra.'
 assert q['observed_resource_digest']!=p['observed_resource_digest']
 assert 'last_verified' not in q and 'curriculum_audit' not in q
 with pytest.raises(ValueError):parse_resource(h.replace('Fall 2026','Fall 2030'),pid='p',url=url)
 with pytest.raises(ValueError):parse_resource(h.replace('4190/5190','4200/5200'),pid='p',url=url)
 with pytest.raises(ValueError):parse_resource('<title>Sign in</title>'+h,pid='p',url=url)


def test_summer_ai_syllabus_preserves_distinct_prerequisite_context():
 url=next(u for u in RESOURCE_SPECS if u.endswith('/syllabus/'))
 h='<title>Syllabus cis5210-26su</title><dl><dt>Course number</dt><dd>CIS 5210 - Artificial Intelligence</dd><dt>Prerequisites &amp; recommended background knowledge</dt><dd>CIS 1210 and programming experience</dd><dt>Instructor</dt><dd>Faculty</dd></dl>'
 p=parse_resource(h,pid='p',url=url)
 assert p['courses'][0]['prerequisites']=='CIS 1210 and programming experience'
 assert p['courses'][0]['syllabus']==url and p['courses'][0]['public_site'] is None


def test_historical_ml_example_never_promotes_prerequisites():
 url='https://machine-learning-upenn.github.io/'
 h='<h1>CIS 5200 Machine Learning Spring 2023</h1><h2>Prerequisites</h2><p>Historical prerequisites</p>'
 p=parse_resource(h,pid='p',url=url)
 assert p['courses'][0]['public_site']==url and p['courses'][0]['prerequisites'] is None
 assert 'Spring 2023' in p['notes'][0]


def wharton_fixture(code,prerequisite='STAT 1020 OR STAT 1120'):
 return f'<div class="wfpCourseDescriptions-course"><h3>{code} - Named core <a href="https://example.edu/unvisited">(Course Syllabus)</a></h3><p>Course description. This course may be taken concurrently with the prerequisite with instructor permission.</p>'+(f'<p><strong>Prerequisites:</strong> {prerequisite}</p>' if prerequisite else '')+'</div><div class="wfpCourseDescriptions-course"><h3>STAT9999 - Not this course</h3><p>Unrelated.</p></div>'


def test_wharton_exact_block_change_and_unvisited_syllabus():
 url=next(iter(WHARTON));p=parse_wharton(wharton_fixture('STAT4230'),pid='p',url=url)
 c=p['courses'][0]
 assert c['name']=='Named core' and c['code']=='STAT 4230'
 assert c['prerequisites']=='STAT 1020 OR STAT 1120; may be taken concurrently with instructor permission.'
 assert c['syllabus'] is None and c['public_site'] is None and c['credits'] is None and c['description'] is None
 q=parse_wharton(wharton_fixture('STAT4230','STAT 4310'),pid='p',url=url)
 assert q['courses'][0]['prerequisites'].startswith('STAT 4310') and q['observed_description_digest']!=p['observed_description_digest']
 with pytest.raises(ValueError):parse_wharton(wharton_fixture('STAT4231'),pid='p',url=url)
 lgst=list(WHARTON)[1]
 assert parse_wharton(wharton_fixture('LGST2420',None),pid='p',url=lgst)['courses'][0]['prerequisites'] is None


@pytest.mark.parametrize('pid,adapter,n,descriptions,prereqs',[
 ('penn-concentration-ai-cs','penn_cs',12,5,3),('penn-concentration-ai-business','penn_business',28,2,1)])
def test_reviewed_penn_metadata_preserves_inventory_and_missingness(pid,adapter,n,descriptions,prereqs):
 from atlas.db import validate_program
 p=json.loads((Path(__file__).parents[1]/'data/programs'/f'{pid}.json').read_text());validate_program(p)
 assert len(p['courses'])==n and p['curriculum_status']=='complete'
 assert sum(bool(c['description']) for c in p['courses'])==descriptions
 assert sum(bool(c['prerequisites']) for c in p['courses'])==prereqs
 codes={c['code']:c for c in p['courses']}
 if adapter=='penn_cs':
  assert all(c['credits'] is None for c in p['courses'])
  assert codes['CIS 4210']['prerequisites'] is None and 'Fall 2022' in codes['CIS 4210']['description']
  assert codes['CIS 5200']['prerequisites'] is None and 'Spring 2023' in codes['CIS 5200']['description']
  assert 'Fall 2026' in codes['CIS 4190']['prerequisites']
  assert sum(bool(c['syllabus']) for c in p['courses'])==3
 else:
  assert codes['STAT 4230']['credits']==1 and codes['LGST 2420']['credits']==0.5
  assert codes['LGST 2420']['prerequisites'] is None
  assert not any(c['syllabus'] or c['public_site'] for c in p['courses'])
 module=importlib.import_module('atlas.adapters.'+adapter+'.adapter')
 assert set(module.SOURCES[1:])==set(module.SOURCE_PARSERS)
