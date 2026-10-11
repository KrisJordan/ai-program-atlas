"""Bounded local credential review; manual expected sets are separate evidence."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.additional_major_audit import validate_ledger, review_fingerprint
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program
from atlas.adapters import northwestern_second_major_metadata as metadata

ROUTES=('mccormick','non-mccormick')

def seed(route):return json.loads(Path('data/programs/northwestern-ai-second-major-'+route+'.json').read_text())
def ledger():return json.loads(Path('research/additional-major-review-northwestern.json').read_text())


def test_manual_exact_sets_and_category_counts():
    rows=ledger();programs=[seed(route)for route in ROUTES];validate_ledger(rows,programs)
    for p,row,option_count in zip(programs,rows['programs'],[99,105]):
        validate_program(p);profile=requirement_profile(p,include_course_ids=True)
        assert profile['required']['count']==5 and profile['options']['count']==option_count
        for role in ('required','options','unresolved'):
            assert set(profile['course_ids'][role])==set(row['expected_course_ids'][role])
            assert {k:profile[role][k]for k in ('count','categories')}==row['expected_profile'][role]
        assert len(p['course_identity_groups'])==1
        assert all(c.get('category_review')for c in p['courses'])
        assert p['program_kind']=='additional_major' and p['award_level']=='other'
        assert p['curriculum_audit']['scope']=='additional_major' and p['curriculum_status']=='partial'
        assert row['eligibility_review']['status']=='partial' and row['second_pass_status']
        bycode={c['code']:c for c in p['courses']}
        assert bycode['COMP_SCI 211-0']['category']=='foundations'
        assert bycode['COMP_SCI 212-0']['category']=='mathematics'
        assert bycode['COMP_SCI 301-0']['category_review']['status']=='mixed'
        assert bycode['COMP_SCI 353-0']['category']=='other'
        assert bycode['COMP_ENG 368-0']['credits']==1 and 'May not receive credit' in bycode['COMP_ENG 368-0']['prerequisites']
        assert all(r['count']==1 for r in p['requirements']if r['kind']=='alternative')
    for title in ('title','major_relationship','award_level'):
        changed=copy.deepcopy(programs[0]);changed[title]='Changed'if title!='major_relationship'else {'changed':True}
        assert review_fingerprint(changed)!=rows['programs'][0]['reviewed_content_hash']


def test_open_choices_bundles_and_exact_policy_conflicts():
    mc,non=[seed(route)for route in ROUTES]
    technical=lambda p:next(r for r in p['requirements']if r['title']=='Technical electives: displayed additional pool')
    for p in (mc,non):
        assert technical(p)['kind']=='choose_courses' and technical(p)['count']==6
        assert 'not the full open universe' in technical(p)['summary']
        note=next(r for r in p['requirements']if r['title']=='Six technical electives with open eligibility')
        assert note['kind']=='note' and note['count']is None
    advanced=next(r for r in mc['requirements']if r['title']=='Four advanced electives')
    assert advanced['kind']=='choose_courses' and advanced['count']==4 and len(advanced['course_ids'])==14
    assert any(len(r['course_ids'])==3 and r['kind']=='all' for r in non['requirements'])
    assert all('only one of' in c['prerequisites']for c in non['courses']if c['code']in ['COMP_SCI 150-0','GEN_ENG 150-0'])
    assert any('MATH 230-2' in x and 'excludes' in x for x in mc['curriculum_audit']['unresolved_requirements'])
    assert any('MATH 228-1' in x and 'McCormick students only' in x for x in non['curriculum_audit']['unresolved_requirements'])
    primary=next(r for r in mc['requirements']if r['title']=='Primary McCormick major uniqueness')
    assert primary['credits']==11 and primary['kind']=='note'
    credit=next(c for c in mc['courses']if c['code']=='COMP_SCI 1CA')
    assert credit['credits']is None and credit['description']is None and credit['category_review']['status']=='unclassified'


def test_description_guard_and_manual_review_non_emission(monkeypatch):
    body='Matrix factorizations and eigenvalues. Prerequisite: permission.'
    row=dict(code='MATH 900-0',department='math',url='https://example.edu/math/',title='Synthetic methods',program_title='Synthetic methods',description_sha256=hashlib.sha256(body.encode()).hexdigest(),description='Matrix methods.',category='mathematics',topic_specific=False,program_ids=['sample'])
    monkeypatch.setattr(metadata,'MANIFEST',dict(headings={'math':['Mathematics']},reviews={'math-900-0':row}))
    html='<h1>Mathematics</h1><div class="courseblock"><p class="courseblocktitle">MATH 900-0 Synthetic methods (1 Unit)</p><p class="courseblockdesc">'+body+'</p></div>'
    obs=metadata.parse_descriptions(html,pid='sample',department='math');c=obs['courses'][0]
    assert c['id']=='sample-math-900-0' and c['description']=='Matrix methods.' and c['prerequisites']=='Prerequisite: permission.'
    assert 'category_review'not in c and 'curriculum_audit'not in obs
    changed=metadata.parse_descriptions(html.replace('eigenvalues','political institutions'),pid='sample',department='math')['courses'][0]
    assert changed['description']is None and changed['category']=='other'
    row['topic_specific']=True
    assert metadata.parse_descriptions(html,pid='sample',department='math')['courses'][0]['description']is None
    with pytest.raises(ValueError,match='title changed'):
        metadata.parse_descriptions(html.replace('Synthetic methods','Another title'),pid='sample',department='math')


@pytest.mark.parametrize('route',ROUTES)
def test_actual_permitted_source_observations(route):
    directory=Path('/tmp/nw-second-review');pid='northwestern-ai-second-major-'+route
    if not (directory/(pid+'-catalog.html')).exists():pytest.skip('Ignored actual source captures unavailable')
    module=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    obs=module.parse((directory/(pid+'-catalog.html')).read_text())
    assert next(r for r in obs['requirements']if r['title']=='Technical electives: displayed additional pool')['count']==6
    assert all(r['count']==1 for r in obs['requirements']if r['kind']=='alternative')
    p=seed(route);seen=set()
    for dep in {r['department']for r in metadata.MANIFEST['reviews'].values()if pid in r['program_ids']}:
        if dep=='stat':continue # independently read web-tool paragraph, no full HTML capture
        data=metadata.parse_descriptions((directory/(dep+'.html')).read_text(),pid=pid,department=dep)
        assert not data['notes'] and 'curriculum_audit'not in data
        assert all('category_review'not in c for c in data['courses'])
        assert {c['id']for c in data['courses']}<={c['id']for c in p['courses']}
        seen.update(c['id']for c in data['courses'])
    assert len(seen)==len(p['courses'])-(1 if route=='mccormick'else 1)
    if route=='mccormick':
        policy=module.SOURCE_PARSERS[module.SOURCES[1]]((directory/(pid+'-college.html')).read_text())
        assert any(r['title']=='Primary McCormick major uniqueness'and r['credits']==11 for r in policy['requirements'])
