"""Exact-code descriptions stay separate from particular topics and role rules."""
import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import maryland_full_course_reviews as m
from atlas.adapters import maryland_catalog_subjects as title_subjects


def test_changed_missing_duplicate_and_wrong_chapter_fail_without_certification(monkeypatch):
    block='<div class="courseblock"><p class="courseblocktitle">TEST101 Example methods (3 Credits)</p><p class="courseblockdesc">An invented description.</p><p class="courseblockextra"><strong>Recommended:</strong> Prior experience.</p></div>'
    from bs4 import BeautifulSoup
    from atlas.adapters.national_curriculum_common import clean
    digest=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
    monkeypatch.setattr(m,'SPEC',{'TEST101':dict(digest=digest,category='foundations',description='An original test summary.')})
    html='<h1>TEST - Test subjects</h1>'+block
    result=m.parse(html,pid='example',prefix='test',codes=['TEST101'])
    assert result['courses'][0]['prerequisites']=='Recommended: Prior experience.'
    assert 'category_review' not in result['courses'][0]
    assert 'curriculum_audit' not in result
    for bad,match in [(html.replace('invented','changed'),'block changed'),('<h1>TEST - Test subjects</h1>','courses missing'),(html+block,'Duplicate'),(html.replace('TEST -','WRONG -'),'heading changed')]:
        with pytest.raises(ValueError,match=match):m.parse(bad,pid='example',prefix='test',codes=['TEST101'])


def test_exact_topics_and_missing_blocks_never_inherit_generic_content():
    programs=[json.loads(p.read_text()) for p in Path('data/programs').glob('*maryland*degree.json')]
    assert len(m.SPEC)==148
    assert not {'CMSC498','GEOG398','IMDM498'} & m.SPEC.keys()
    counts=[]
    for p in programs:
        mapped={code for codes in m.TARGETS[p['id']].values() for code in codes}
        for c in p['courses']:
            if c['id']=='umd-'+c['code'].lower() and c['code'] in mapped:
                assert c['category_review']['status'] in {'reviewed','mixed'}
                assert c['description']==m.SPEC[c['code']]['description']
            elif c['code'] in title_subjects.SPEC and c['name']==title_subjects.SPEC[c['code']]['name']:
                assert c['category']==title_subjects.SPEC[c['code']]['category']
                assert c['category_review']['status']=='reviewed'
                assert c['description'] is None
                assert 'Moderate-confidence' in c['category_review']['rationale']
            else:
                assert c['category']=='other'
                assert c['category_review']['status']=='unclassified'
        counts.append(sum(c['category_review']['status']!='unclassified' for c in p['courses']))
    assert sorted(counts)==[65,99]
    assert all('no description paragraph' in m.SPEC[c]['description'] for c in ['LATN101','LATN102','LATN201'])


def test_subject_decisions_are_about_content_not_degree_prefixes():
    assert m.SPEC['PHIL370']['category']=='mathematics'
    assert m.SPEC['CMSC454']['category']=='foundations'
    assert m.SPEC['CMSC474']['category']=='mathematics'
    assert m.SPEC['SOCY216']['category']=='human_context'
    assert m.SPEC['INST366']['category']=='human_context'
    assert m.SPEC['PSYC431']['category']=='applications'
    assert m.SPEC['STAT426']['category']=='other'
    assert set(m.SPEC['STAT426']['candidate_categories'])=={'mathematics','ai_ml'}
