import copy
import json
from pathlib import Path
import pytest
from atlas.adapters import miami_policy_closure as pc
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import validate_ledger

ROOT=Path(__file__).resolve().parents[1]
MANUAL=json.loads((ROOT/'research/miami-manual-role-sets.json').read_text())['programs']


def test_manual_source_sets_match_graph_and_actual_categories():
    programs=[]
    for pid,e in MANUAL.items():
        p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());programs.append(p)
        bycode={c['code']:c for c in p['courses']};profile=requirement_profile(p)
        assert len(e['required_codes'])==len(set(e['required_codes']))
        assert not set(e['required_codes']) & set(e['option_codes'])
        assert {bycode[c]['id']for c in e['required_codes']}==set(e['expected_course_ids']['required'])
        assert {bycode[c]['id']for c in e['option_codes']}==set(e['expected_course_ids']['options'])
        for role,v in e['expected_profile'].items():
            assert profile[role]['count']==v['count']
            assert {k:n for k,n in profile[role]['categories'].items()if n}==v['categories']
            assert profile[role]['classification']['unreviewed']==0
        assert profile['identity']['crosslisted_aliases']==2
        assert all(c.get('category_review')for c in p['courses'])
    ledger=json.loads((ROOT/'research/degree-audit/national-degree-batch.json').read_text())
    rows=[e for e in ledger['programs']if e['program_id']in MANUAL]
    validate_ledger(rows,programs)
    for e in rows:
        assert e['status']=='blocked' and len(e['blockers'])==1
        assert 'C-minus' in e['blockers'][0]['issue']
        assert len(e['blockers'][0]['related_urls'])==1
        assert e['expected_profile']==MANUAL[e['program_id']]['expected_profile']
        assert e['expected_course_ids']==MANUAL[e['program_id']]['expected_course_ids']


def test_degree_specific_choices_do_not_become_fixed():
    bs=MANUAL['miami-data-science-ai-bs'];ba=MANUAL['university-of-miami-data-science-and-artificial-intelligence-ba-degree']
    assert 'CSC 410' in bs['option_codes'] and 'CSC 410' in ba['option_codes']
    assert 'CSC 315' in bs['required_codes'] and 'CSC 315' in ba['option_codes']
    assert 'CSC 506' in bs['option_codes'] and 'CSC 506' not in ba['option_codes']
    bsba=MANUAL['miami-ai-technologies-business-bsba'];bba=MANUAL['university-of-miami-artificial-intelligence-technologies-for-business-other-degree']
    assert 'ACC 211' in bsba['option_codes'] and 'ACC 211' in bba['required_codes']
    assert 'BTE 271' in bsba['option_codes'] and 'BTE 271' in bba['required_codes']
    assert 'MTH 161' in bsba['required_codes'] and 'MTH 161' in bba['option_codes']


@pytest.mark.parametrize('key',['grades','business','arts'])
def test_optional_actual_completion_policy_observations(key):
    path=ROOT/'.cache/research/miami-degree-audit'/f'policy-{key}.html'
    if not path.exists():pytest.skip('Ignored actual policy capture')
    pid='miami-ai-technologies-business-bsba' if key=='business' else 'miami-data-science-ai-bs'
    html=path.read_text();out=pc.parse(html,pid=pid,key=key)
    assert all(r['kind']=='note'and not r['course_ids'] for r in out['requirements'])
    assert 'curriculum_audit'not in out and not out['courses']
    changed=html.replace('</h1>',' changed</h1>',1)
    with pytest.raises(ValueError):pc.parse(changed,pid=pid,key=key)
    with pytest.raises(ValueError):pc.parse(html,pid='unrelated',key=key)
    if key=='business':
        summary=out['requirements'][1]['summary']
        assert 'readmission' in summary and 'at least C' in summary and 'continuously enrolled' in summary
        with pytest.raises(ValueError):pc.parse(html,pid='miami-data-science-ai-bs',key=key)
    if key=='grades':
        text=out['requirements'][1]['summary']
        assert 'C average or better' in text and 'C-minus' in text
        assert 'free elective' in text and 'Neither' in text
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(html,'html.parser')
        threshold=next(t for t in soup.select_one('#content').find_all(string=True) if 'average or better' in t)
        assert 'C' in threshold
        threshold.replace_with(str(threshold).replace('C','D'))
        with pytest.raises(ValueError):pc.parse(str(soup),pid=pid,key=key)
