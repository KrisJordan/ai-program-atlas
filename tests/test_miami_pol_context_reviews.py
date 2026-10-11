"""Political Science review distinguishes methods, practice and source conflicts."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_pol_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID='miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['POL 323','POL 398','POL 505','POL 585']}
    blocks=[]
    for code,entry in spec['courses'].items():
        credits='6' if code=='POL 323' else '1-9' if code=='POL 398' else '3'
        block=(f'<div class="courseblock"><p class="courseblocktitle">{code}. '
               f'{entry["name"]}. {credits} Credit Hours.</p>'
               '<p>Synthetic reviewed scope. Pre/Co-Requisite: TEST 101. Components: LEC.</p></div>')
        entry['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Political Science (POL)</h1>'+''.join(blocks)


def test_observations_preserve_credit_scope_and_do_not_certify_review(synthetic):
    result=module.parse(synthetic,pid=PID)
    records={c['code']:c for c in result['courses']}
    assert records['POL 323']['credits']==6
    assert records['POL 398']['credits'] is None
    assert result['observed_credit_ranges']['POL 398']['maximum']==9
    assert records['POL 505']['prerequisites']=='Pre/Co-Requisite: POL 202 .'
    assert 'PO L 211 and 212 or graduate standing' in records['POL 585']['prerequisites']
    assert 'Prerequisite: POL 202' in records['POL 585']['prerequisites']
    assert not {'curriculum_audit','last_verified','requirements'} & set(result)
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change',['missing','duplicate','subject','precorequisite','credit','heading','login'])
def test_changed_source_and_wrong_pages_fail(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    edited={
        'missing':synthetic.replace(first,''), 'duplicate':synthetic+first,
        'subject':synthetic.replace('Synthetic reviewed scope.','New content.',1),
        'precorequisite':synthetic.replace('Pre/Co-Requisite:','Prerequisite:',1),
        'credit':synthetic.replace('6 Credit Hours','3 Credit Hours',1),
        'heading':synthetic.replace('Political Science (POL)','Different chapter'),
        'login':'<h1>Sign in</h1><form>University credentials required</form>',
    }[change]
    with pytest.raises(ValueError):module.parse(edited,pid=PID)


def test_classifications_come_from_methods_and_practice_not_ai_word():
    entries=module.SPEC['courses']
    assert len(entries)==146
    assert Counter(e['category'] for e in entries.values())=={'human_context':118,'mathematics':4,'applications':8,'other':16}
    assert {c for c,e in entries.items() if e['category']=='mathematics'}=={'POL 306','POL 510','POL 517','POL 518'}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}=={'POL 394','POL 398','POL 499','POL 585','POL 595'}
    assert entries['POL 558']['category']=='other'
    assert entries['POL 558']['review']['candidate_categories']==['human_context','applications']
    assert entries['POL 512']['review']['candidate_categories']==['human_context','mathematics']
    assert 'Strongly Recommended' in entries['POL 569']['prerequisites']
    assert 'not stated as required' in entries['POL 569']['prerequisites']
    assert entries['POL 203']['prerequisites']=='Requisite: If took INS 101 , cannot take POL 203 .'
    assert 'repeat credit' in entries['POL 389']['description']
    assert 'camera' in entries['POL 532']['description']
    assert module.SPEC['sources']['pol']['catalog_year'] is None


def test_registration_preserves_old_response_and_is_idempotent(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'existing-rule'}]}
    before=deepcopy(old);sources=[];parsers={module.URL:lambda html:old}
    module.register(PID,sources,parsers);callback=parsers[module.URL]
    module.register(PID,sources,parsers)
    assert callback is parsers[module.URL] and sources==[module.URL]
    result=callback(synthetic)
    assert old==before and result['requirements']==old['requirements']
    assert len(result['courses'])==4
    with pytest.raises(ValueError):module.parse(synthetic,pid='unreviewed')


def test_optional_actual_replay_all_four_program_scopes():
    path=Path('.cache/research/miami-degree-audit/pol.html')
    if not path.exists():pytest.skip('Raw capture deliberately uncommitted')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==146
        for c in result['courses']:
            e=module.SPEC['courses'][c['code']]
            assert (c['name'],c['credits'],c['prerequisites'])==(e['name'],e['credits'],e['prerequisites'])
