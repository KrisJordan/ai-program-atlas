"""Course identity, offering terms and catalog metadata are independently verified."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters.cmu_bs.course_resources import RESOURCES,parse_resource
from atlas.adapters.cmu_bs.course_metadata import parse_metadata
from tests.test_cmu_penn import metadata_fixture


def test_catalog_description_change_is_observed_without_copying_prose():
 h=metadata_fixture();p=parse_metadata(h,pid='cmu-bs-ai',codes=('07-280',))
 # Add a description between the units and prerequisites, preserving catalog fields.
 q=parse_metadata(h.replace('Prerequisites:', 'Newly documented topic.<br>Prerequisites:'),pid='cmu-bs-ai',codes=('07-280',))
 assert p['observed_description_digests']!=q['observed_description_digests']
 assert p['courses'][0]['description'] is None and q['courses'][0]['description'] is None
 assert p['courses'][0]['prerequisites']==q['courses'][0]['prerequisites']


@pytest.mark.parametrize('url',list(RESOURCES))
def test_course_resource_requires_exact_course_and_recorded_term(url):
 config=RESOURCES[url];html=f'<title>Course resource</title><h1>{config["code"]} {config["name"]}</h1><p>{config["term"]}</p><h2>Syllabus</h2><p>Course policies</p>'
 p=parse_resource(html,pid='cmu-bs-ai',url=url)
 assert p['curriculum_status']=='partial' and 'last_verified' not in p and 'curriculum_audit' not in p
 assert p['courses'][0]['credits'] is None and p['courses'][0]['prerequisites'] is None
 with pytest.raises(ValueError):parse_resource(html.replace(config['code'],'99-999'),pid='cmu-bs-ai',url=url)
 with pytest.raises(ValueError):parse_resource(html.replace(config['term'],'Fall 2035'),pid='cmu-bs-ai',url=url)
 with pytest.raises(ValueError):parse_resource('<title>Sign in</title>'+html,pid='cmu-bs-ai',url=url)
 q=parse_resource(html.replace('Course policies','Changed course policies'),pid='cmu-bs-ai',url=url)
 assert p['observed_resource_digest']!=q['observed_resource_digest']


@pytest.mark.parametrize('pid,adapter',[('cmu-bs-ai','cmu_bs'),('cmu-minor-ai','cmu_minor'),('cmu-additional-ai','cmu_additional')])
def test_reviewed_cmu_core_metadata_and_historical_provenance(pid,adapter):
 p=json.loads((Path(__file__).parents[1]/'data/programs'/f'{pid}.json').read_text());courses={c['code']:c for c in p['courses']};sources={s['id']:s for s in p['sources']}
 for code in ['07-280','07-380','11-411','16-385']:
  c=courses[code];assert c['description'] and c['prerequisites'] and c['credits']==12 and c['credit_unit']=='units'
  assert c['public_site'] and c['source_id']==pid+'-course-directory'
 assert '21-122' in courses['07-380']['prerequisites']
 assert 'Spring 2020' in sources['cmu-16385-spring-2020-site']['title']
 assert 'Spring 2026' in sources['cmu-11411-spring-2026-syllabus']['title']
 assert courses['11-411']['syllabus'].endswith('/syllabus')
 assert 'discrepancy' in ' '.join(p['notes'])
 statements=[o for o in p['outcomes'] if o['kind']=='source_stated']
 assert all(o['statement_type']=='learning_outcome' for o in statements)
 assert all('statement_type' not in o for o in p['outcomes'] if o['kind']=='inferred_taxonomy')
 module=importlib.import_module('atlas.adapters.'+adapter+'.adapter')
 assert set(RESOURCES)<=set(module.SOURCES) and set(RESOURCES)<=set(module.SOURCE_PARSERS)
