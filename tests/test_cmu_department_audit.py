import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters.cmu_bs.reviewed_departments import observe,MANIFEST
from atlas.db import validate_program


def test_department_source_change_is_not_an_automatic_subject_review():
    desc='Human cognitive processes and experiments.'
    spec=dict(heading='Department of Psychology Courses',source_id='test-source',url='https://example.test/',subjects={'85-110':dict(name='Cognitive Psychology',category='applications',description_digest=hashlib.sha256(desc.encode()).hexdigest())},conditions={})
    html=f'<h1>{spec["heading"]}</h1><p>2026-2027 Catalog</p><dl class="courseblock"><dt>85-110 Cognitive Psychology</dt><dd>Fall: 9 units<br>{desc}<br>Prerequisite: 85-100</dd></dl>'
    a=observe(html,spec)
    assert a['courses'][0]['category']=='applications'and a['courses'][0]['credits']==9
    assert a['courses'][0]['prerequisites']=='85-100'
    changed=observe(html.replace(desc,'Different subject.'),spec)
    assert changed['courses'][0]['category']=='other'
    assert changed['observed_description_digests']!=a['observed_description_digests']
    assert not {'last_verified','curriculum_audit'}&a.keys()
    assert 'category_review'not in a['courses'][0]
    with pytest.raises(ValueError):observe(html.replace('85-110','85-111'),spec)


def test_science_policy_and_cognitive_ai_mixture_keep_their_subjects():
    p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());validate_program(p);by={c['code']:c for c in p['courses']}
    for code in ['85-110','85-170','03-118','09-101','33-104','33-228','88-255']:assert by[code]['category']=='applications'
    for code in ['19-403','19-411','67-348']:assert by[code]['category']=='human_context'
    assert by['85-213']['category_review']['status']=='mixed'and by['85-213']['category']=='other'
    assert by['85-370']['name']=='Cognitive Neuropsychology Research Methods'
    assert any('Cognitive Neuroscience Research Methods'in n for n in by['85-370']['notes'])
    conditions=[r for r in p['requirements']if r['id'].startswith('cmu-bs-ai-department-entry-')]
    assert len(conditions)>=5 and all(r['kind']=='note' and not r['course_ids']for r in conditions)
    assert {'85-110','19-403','03-206'}<={code for s in MANIFEST.values()for code in s['subjects']}
    assert {s['source_id']for s in MANIFEST.values()}<={s['id']for s in p['sources']}


def test_business_domain_communication_and_restrictions_are_distinct():
    p=json.loads(Path('data/programs/cmu-bs-ai.json').read_text());validate_program(p);by={c['code']:c for c in p['courses']}
    assert all(by[c]['category']=='applications'for c in ['70-100','70-311','70-443','73-104','73-230'])
    assert all(by[c]['category']=='human_context'for c in ['70-301','70-340','70-348','70-352','70-364'])
    assert by['70-341']['category_review']['status']=='mixed'
    assert by['70-352']['credits']==3 and by['70-352']['credit_unit']=='units'
    rules={r['id']:r for r in p['requirements']}
    for code in ['70-100','70-348','70-352','73-104']:
        r=rules['cmu-bs-ai-department-entry-'+code+'-0'];assert r['kind']=='note'and not r['course_ids']
    spec=next(s for s in MANIFEST.values()if '70-100'in s['subjects'])
    assert 'Declared Tepper BA students' in spec['conditions']['70-100'][0]['marker']
