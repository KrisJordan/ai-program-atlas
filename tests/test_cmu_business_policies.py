from importlib import import_module
from pathlib import Path
import json
import pytest
from atlas.db import validate_program
from atlas.requirements import validate_requirements
m=import_module('atlas.adapters.cmu-ai-business-concentration.policies')
ROOT=Path(__file__).resolve().parents[1]


def test_observed_metadata_is_extracted_and_missing_prerequisite_is_unknown():
    blocks=[]
    for i,code in enumerate(sorted(m.CODES['business'])):
        blocks.append('<dl class="courseblock"><dt>'+code+' Synthetic '+str(i)+'</dt><dd>Fall: '+str(9+i)+' units<br>Short fixture description.'+('<br>Prerequisites: 70-122' if i==0 else '')+'</dd></dl>')
    html='<h1>Undergraduate Business Administration Courses</h1>'+''.join(blocks)
    d=m.parse_courses('business',html)
    assert sorted(c['credits'] for c in d['courses'])==list(range(9,17))
    assert sum(c['prerequisites'] is not None for c in d['courses'])==1
    assert all(c['description'] is None for c in d['courses'])
    assert 'curriculum_audit' not in d and 'curriculum_status' not in d
    with pytest.raises(ValueError):m.parse_courses('business',html.replace('70-445','70-446'))
    with pytest.raises(ValueError):m.parse_courses('business',html.replace('Fall: 9 units','Fall: variable units'))


def test_additional_major_waiver_does_not_award_concentration():
    html='<h1>Business Administration, B.S.</h1><p>For students electing to complete an additional major, the concentration requirement is waived; students must complete 27 units of business elective courses as part of the waived concentration requirement.</p>'
    d=m.parse_host_context(html)
    assert d['requirements'][0]['kind']=='note'
    assert 'does not award the named AI and Business concentration' in d['requirements'][0]['summary']
    assert 'courses' not in d
    with pytest.raises(ValueError):m.parse_host_context(html.replace('27 units','18 units'))


def test_declaration_is_recommended_not_an_admission_deadline():
    html='<h1>Business Administration</h1><p>AI and Business. For students in the Business major, a concentration is available. Students are encouraged to declare their concentration by the end of their sophomore year. Courses taken to meet concentration requirements are not allowed to double count.</p>'
    d=m.parse_site(html)
    assert 'recommendation, not a published eligibility deadline' in d['requirements'][0]['summary']
    with pytest.raises(ValueError):m.parse_site(html.replace('encouraged','required'))


@pytest.mark.parametrize('key,fn',[('cmu-tepper',m.parse_tepper),('cmu-regulations',m.parse_regulations),('cmu-business-site',m.parse_site),('cmu-advising',m.parse_advising)])
def test_optional_policy_sources_and_material_drift(key,fn):
    p=Path('/tmp/atlas-local-'+key+'.html')
    if not p.exists():pytest.skip('Optional reviewed official source cache')
    html=p.read_text();d=fn(html)
    assert d['requirements'] and 'curriculum_audit' not in d
    if key=='cmu-tepper':
        assert any('one external course' in r['summary'] for r in d['requirements'])
        with pytest.raises(ValueError):fn(html.replace('Only 1 course can transfer between','Only 2 courses can transfer between'))


def test_local_complete_audit_has_finite_four_course_load_and_no_host_degree_claim():
    d=json.loads((ROOT/'data/programs/cmu-ai-business-concentration.json').read_text())
    validate_program(d);validate_requirements(d)
    assert d['curriculum_status']=='complete'
    assert d['curriculum_audit']['scope']=='concentration'
    assert d['curriculum_audit']['unresolved_requirements']==[]
    by={c['id']:c for c in d['courses']}
    groups=[r for r in d['requirements'] if r['id'].startswith(d['id']+'-group-')]
    assert len(groups)==4 and [r['kind'] for r in groups]==['all','choose_courses','choose_courses','choose_courses']
    assert all(by[c]['credits']==9 and by[c]['credit_unit']=='units' for r in groups for c in r['course_ids'])
    assert 9*(len(groups[0]['course_ids'])+sum(r['count'] for r in groups[1:]))==36
    assert any('does not certify' in r['summary'] for r in d['requirements'])
