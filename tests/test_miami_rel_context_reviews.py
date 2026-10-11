"""Religion review does not turn medical/cognitive words into AI classifications."""
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path

from bs4 import BeautifulSoup
import pytest
from atlas.adapters import miami_rel_context_reviews as module
from atlas.adapters.business_society_minors import clean

PID='miami-data-science-ai-bs'


@pytest.fixture
def synthetic(monkeypatch):
    spec=deepcopy(module.SPEC)
    spec['courses']={c:spec['courses'][c] for c in ['REL 119','REL 332','REL 348','REL 530']}
    blocks=[]
    for code,entry in spec['courses'].items():
        credits='1-4' if code=='REL 119' else '1-3' if code=='REL 530' else '3'
        block=(f'<div class="courseblock"><p class="courseblocktitle">{code}. '
               f'{entry["name"]}. {credits} Credit Hours.</p>'
               '<p>Synthetic religious interpretation. Credit limitation applies. Components: LEC.</p></div>')
        entry['block_hash']=hashlib.sha256(clean(BeautifulSoup(block,'html.parser').get_text(' ',strip=True)).encode()).hexdigest()
        blocks.append(block)
    monkeypatch.setattr(module,'SPEC',spec)
    return '<h1>Religious Studies (REL)</h1>'+''.join(blocks)


def test_ranges_and_explicit_negative_prerequisite_are_preserved(synthetic):
    result=module.parse(synthetic,pid=PID);records={c['code']:c for c in result['courses']}
    assert records['REL 119']['credits'] is None and records['REL 530']['credits'] is None
    assert result['observed_credit_ranges']['REL 119']['maximum']==4
    assert result['observed_credit_ranges']['REL 530']['maximum']==3
    assert records['REL 332']['prerequisites']=='May be taken without having had REL 331.'
    assert 'only one department' in records['REL 348']['prerequisites']
    assert not {'course_identity_groups','requirements','curriculum_audit','last_verified'} & set(result)
    assert all('category_review' not in c for c in records.values())


@pytest.mark.parametrize('change',['missing','duplicate','content','restriction','credits','heading','login'])
def test_changed_source_and_wrong_pages_fail_closed(synthetic,change):
    first=str(BeautifulSoup(synthetic,'html.parser').select_one('.courseblock'))
    edited={
        'missing':synthetic.replace(first,''),'duplicate':synthetic+first,
        'content':synthetic.replace('Synthetic religious interpretation.','New subject.',1),
        'restriction':synthetic.replace('Credit limitation applies.','No credit limitation.',1),
        'credits':synthetic.replace('1-4 Credit Hours','4 Credit Hours',1),
        'heading':synthetic.replace('Religious Studies (REL)','Wrong chapter'),
        'login':'<h1>University Login</h1><form>Account required</form>',
    }[change]
    with pytest.raises(ValueError):module.parse(edited,pid=PID)


def test_reviewed_subjects_and_unknown_external_courses_remain_distinct():
    entries=module.SPEC['courses']
    unknown={f'REL {n}' for n in [119,139,159,219,239,259,319,339,359,419,439,459]}
    assert len(entries)==113
    assert Counter(e['category'] for e in entries.values())=={'human_context':97,'applications':2,'other':14}
    assert {c for c,e in entries.items() if e['review']['status']=='unclassified'}==unknown
    assert {c for c,e in entries.items() if e['category']=='applications'}=={'REL 253','REL 450'}
    assert {c for c,e in entries.items() if e['review']['status']=='mixed'}=={'REL 365','REL 378'}
    assert entries['REL 161']['category']==entries['REL 451']['category']=='human_context'
    assert entries['REL 271']['prerequisites']=='The source explicitly assumes no prior knowledge.'
    assert sum(e['credit_range'] is not None for e in entries.values())==14
    assert module.SPEC['sources']['rel']['catalog_year'] is None


def test_safe_composition_and_unknown_program_rejection(synthetic):
    old={'id':PID,'courses':[],'requirements':[{'id':'existing-rule'}]}
    before=deepcopy(old);sources=[];parsers={module.URL:lambda html:old}
    module.register(PID,sources,parsers);callback=parsers[module.URL]
    module.register(PID,sources,parsers)
    result=callback(synthetic)
    assert callback is parsers[module.URL] and sources==[module.URL]
    assert old==before and result['requirements']==old['requirements']
    assert len(result['courses'])==4
    with pytest.raises(ValueError):module.parse(synthetic,pid='unreviewed-program')


def test_optional_actual_replay_all_four_scopes():
    path=Path('.cache/research/miami-degree-audit/rel.html')
    if not path.exists():pytest.skip('Raw official capture deliberately uncommitted')
    pids={p for e in module.SPEC['courses'].values() for p in e['program_ids']}
    assert len(pids)==4
    for pid in pids:
        result=module.parse(path.read_text(),pid=pid)
        assert len(result['courses'])==113
        for c in result['courses']:
            e=module.SPEC['courses'][c['code']]
            assert (c['name'],c['credits'],c['prerequisites'])==(e['name'],e['credits'],e['prerequisites'])
