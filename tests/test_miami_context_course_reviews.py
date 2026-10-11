from copy import deepcopy
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_context_course_reviews as m
from atlas.adapters.business_society_minors import clean


@pytest.fixture
def synthetic(monkeypatch):
    html='<h1>Example (XYZ)</h1><div class="courseblock"><p class="courseblocktitle">XYZ 100. Example context. 1-3 Credit Hours.</p><p>Source content. Requisite: Nonbusiness students. Components: LEC.</p></div>'
    block=BeautifulSoup(html,'html.parser').select_one('.courseblock')
    item=dict(key='xyz',name='Example context',program_ids=['example'],url='https://example.edu/xyz/',block_hash=hashlib.sha256(clean(block.get_text(' ',strip=True)).encode()).hexdigest(),description='Original concise summary.',prerequisites='Requisite: Nonbusiness students.',category='applications')
    monkeypatch.setattr(m,'SPEC',dict(sources={'xyz':dict(heading='Example (XYZ)')},courses={'XYZ 100':item}))
    return html


def test_observation_does_not_certify_review_or_promote_context(synthetic):
    result=m.parse(synthetic,pid='example',key='xyz');c=result['courses'][0]
    assert c['credits'] is None and c['credit_unit']=='semester_hours'
    assert c['prerequisites']=='Requisite: Nonbusiness students.'
    assert 'category_review'not in c and 'requirements'not in result
    previous=lambda _:dict(id='example',courses=[dict(c)],requirements=[{'id':'existing-context','kind':'note'}])
    composed=m._compose(previous,synthetic,pid='example',key='xyz')
    assert len(composed['courses'])==1 and composed['requirements']==previous('')['requirements']


@pytest.mark.parametrize('old,new',[('Example (XYZ)','Wrong (XYZ)'),('Source content.','Changed description.'),('Nonbusiness students.','All students.'),('1-3 Credit','3 Credit')])
def test_changed_identity_content_eligibility_or_credit_requires_review(synthetic,old,new):
    with pytest.raises(ValueError):m.parse(synthetic.replace(old,new),pid='example',key='xyz')


def test_missing_duplicate_and_unreviewed_scope_rejected(synthetic):
    block=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    for html in ['<h1>Example (XYZ)</h1>',synthetic+block]:
        with pytest.raises(ValueError):m.parse(html,pid='example',key='xyz')
    with pytest.raises(ValueError):m.parse(synthetic,pid='unrelated',key='xyz')


def test_actual_reviewed_blocks_and_seed_provenance():
    observations=0
    for key,source in m.SPEC['sources'].items():
        cache=Path('.cache/http')/(hashlib.sha256(source['url'].encode()).hexdigest()+'.body')
        if not cache.exists():pytest.skip('Ignored actual official source capture unavailable')
        for pid in {pid for x in m.SPEC['courses'].values()if x['key']==key for pid in x['program_ids']}:
            result=m.parse(cache.read_text(),pid=pid,key=key)
            seed=json.loads(Path('data/programs',pid+'.json').read_text());bycode={c['code']:c for c in seed['courses']}
            for c in result['courses']:
                assert 'category_review'not in c
                assert {k:bycode[c['code']][k]for k in c}==c
                assert bycode[c['code']]['category_review']['source_ids']==[c['source_id']]
                observations+=1
    assert observations==sum(len(x['program_ids'])for x in m.SPEC['courses'].values())


def test_business_credit_exclusions_and_existing_concurrent_route_retained():
    assert 'no credit for business' in m.SPEC['courses']['FIN 300']['prerequisites']
    assert 'no credit toward any business' in m.SPEC['courses']['BUS 201']['prerequisites']
    assert 'Non Business Majors' in m.SPEC['courses']['BUS 200']['prerequisites']
    assert 'Or Corequisites:' in m.SPEC['courses']['MAS 311']['prerequisites']
    # Similar titles and credit exclusions are not identity-group evidence.
    assert m.SPEC['courses']['ECO 301']['name']==m.SPEC['courses']['ECO 303']['name']
    assert m.SPEC['courses']['ECO 301']['block_hash']!=m.SPEC['courses']['ECO 303']['block_hash']
