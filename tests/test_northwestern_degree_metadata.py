import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import northwestern_degree_metadata as m
from atlas.adapters.northwestern_degree_policies import PID, parse_college, parse_theme, THEME_URL
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def seed(): return json.loads(Path('data/programs',PID+'.json').read_text())


def test_manual_roles_identity_and_unknowns():
    p=seed(); validate_program(p); bycode={c['code']:c for c in p['courses']}
    profile=requirement_profile(p)
    audit=json.loads(Path('research/degree-audit/northwestern.json').read_text())['programs'][0]
    for role in ['required','options','unresolved']:
        assert audit['expected_profile'][role]=={k:profile[role][k]for k in ['count','categories']}
    assert [profile[x]['count']for x in ['required','options','unresolved']]==[13,175,1]
    assert len(p['courses'])==190 and all(c.get('category_review')for c in p['courses'])
    assert profile['identity']['crosslisted_aliases']==1
    assert bycode['COMP_SCI 336-0']['category']=='foundations'
    assert bycode['COMP_SCI 265-0']['category']=='human_context'
    assert bycode['COMP_SCI 353-0']['category_review']['candidate_categories']==['ai_ml','applications']
    assert bycode['COMP_ENG 368-0']['credits']==1 and 'May not receive credit' in bycode['COMP_ENG 368-0']['prerequisites']
    assert bycode['CHEM 141-0']['credits']==0.34 and bycode['CHEM 141-0']['credit_unit']=='units'
    assert 'Must be taken concurrently' in bycode['CHEM 141-0']['prerequisites']
    assert 'permission of instructor' in bycode['COMP_SCI 469-0']['prerequisites']
    assert 'Not open to students in the McCormick' in bycode['MATH 230-2']['prerequisites']
    for code in ['COMP_SCI 1CA','GEOG 240','GEOG 312','GEOG 313','GEOG 328']:
        assert bycode[code]['credits'] is None and bycode[code]['description'] is None
        assert bycode[code]['category_review']['status']=='unclassified'
    assert sum(c['description'] is None for c in p['courses'])==21


def test_exact_observations_reject_stale_editorial_content(monkeypatch):
    body='Synthetic course uses matrix transformations. Prerequisite: permission.'
    review=dict(code='MATH 900-0',title='Synthetic methods',program_title='Synthetic methods',department='math',url='https://example.edu/math/',category='mathematics',description='An original summary.',description_sha256=hashlib.sha256(body.encode()).hexdigest(),topic_specific=False)
    monkeypatch.setattr(m,'MANIFEST',{'headings':{'math':['Mathematics']}})
    monkeypatch.setattr(m,'REVIEWS',{'synthetic':review})
    html='<h1>Mathematics</h1><div class="courseblock"><p class="courseblocktitle">MATH 900-0 Synthetic methods (0.34 Unit)</p><p class="courseblockdesc">'+body+'</p></div>'
    d=m.parse_descriptions(html,pid=PID,department='math'); c=d['courses'][0]
    assert c['description']=='An original summary.' and c['credits']==0.34
    assert c['prerequisites']=='Prerequisite: permission.'
    assert 'category_review'not in c and 'curriculum_audit'not in d
    changed=m.parse_descriptions(html.replace('matrix transformations','historical analysis'),pid=PID,department='math')['courses'][0]
    assert changed['description']is None and changed['category']=='other'
    review['topic_specific']=True
    assert m.parse_descriptions(html,pid=PID,department='math')['courses'][0]['category']=='other'
    with pytest.raises(ValueError,match='title changed'):
        m.parse_descriptions(html.replace('Synthetic methods','New title'),pid=PID,department='math')


def test_optional_actual_all_metadata_and_role_sources():
    if not Path('/tmp/nw-full-audit/fetch-index.json').exists():pytest.skip('Ignored actual source captures absent')
    module=importlib.import_module('atlas.adapters.'+PID+'.adapter')
    seen=set()
    for dep in m.MANIFEST['headings']:
        path=Path('/tmp/nw-full-audit',dep+'.html')
        data=m.parse_descriptions(path.read_text(),pid=PID,department=dep)
        assert not any(n.startswith('Changed bodies')for n in data['notes'])
        assert all('category_review'not in c for c in data['courses'])
        seen.update(c['id']for c in data['courses'])
        assert next(r['url']for r in m.REVIEWS.values()if r['department']==dep)in module.SOURCE_PARSERS
    assert seen==set(m.REVIEWS)
    major=module.parse(Path('/tmp/nw-audit-major.html').read_text())
    assert next(r for r in major['requirements']if r['id']=='nw-bse-r4')['kind']=='note'
    advanced=next(r for r in major['requirements']if r['id'].endswith('policy-advanced-intro'))
    assert advanced['kind']=='choose_courses' and advanced['count']==4 and len(advanced['course_ids'])==14
    college=parse_college(Path('/tmp/nw-audit-college.html').read_text())
    honors=next(r for r in college['requirements']if r['id'].endswith('policy-honors-calculus'))
    assert honors['course_ids']==['nw-bse-math-228-1','nw-bse-es-appm-252-1'] and honors['count']==1
    theme=parse_theme(Path('.cache/http',hashlib.sha256(THEME_URL.encode()).hexdigest()+'.body').read_text())
    assert len(theme['courses'])==13
    assert not any('1xx'in c['code'] or c['code'].startswith('PRDV')for c in theme['courses'])
    assert theme['requirements'][-1]['credits']==7 and theme['requirements'][-1]['kind']=='choose_credits'
