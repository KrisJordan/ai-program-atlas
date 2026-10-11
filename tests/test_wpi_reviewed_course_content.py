import copy
import hashlib
import json
from pathlib import Path
import pytest
from atlas.adapters import wpi_reviewed_course_content as m
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def fixture(code,entry,desc='Synthetic prediction methods.',rec='Synthetic background',units='1/3'):
    r='' if rec is None else f'<div class="field--name-field-recommended"><div class="field__item">{rec}</div></div>'
    return f'<p>Undergraduate Catalog 2026-2027</p><main><h1>{code}: {entry["name"]}</h1><div class="field--name-field-description">{desc}</div><div class="field--name-field-credits"><div class="field__item">{units}</div></div>{r}</main>'


def test_changed_content_background_credits_version_rejected(monkeypatch):
    entry=copy.deepcopy(m.SPEC['DS 2010'])
    entry.pop('main_digest',None)
    entry['description_digest']=hashlib.sha256(b'Synthetic prediction methods.').hexdigest()
    entry['recommended_digest']=hashlib.sha256(b'Synthetic background').hexdigest()
    monkeypatch.setitem(m.SPEC,'DS 2010',entry)
    html=fixture('DS 2010',entry)
    out=m.parse(html,program_id='wpi-ai-bs',code='DS 2010')
    assert out['courses'][0]['category']=='ai_ml'
    assert out['courses'][0]['credits']==pytest.approx(1/3)
    assert 'not a mandatory prerequisite' in out['courses'][0]['prerequisites']
    assert 'category_review' not in out['courses'][0] and not out['requirements']
    for h in [html.replace('methods.','different.'),html.replace('Synthetic background','Different background'),html.replace('1/3','1/2'),html.replace('2026-2027','2025-2026')]:
        with pytest.raises(ValueError):m.parse(h,program_id='wpi-ai-bs',code='DS 2010')


def test_source_supported_categories_leave_roles_unchanged():
    for pid in ['wpi-ai-bs','wpi-business-analytics-applied-ai-bs']:
        p=json.loads(Path('data/programs',pid+'.json').read_text());validate_program(p)
        c={c['code']:c for c in p['courses']}
        assert c['FIN 2070']['name']=='Risk Analysis for Decision Making'
        assert c['FIN 2070']['category']=='applications'
        assert c['DS 2010']['category']=='ai_ml'
        assert c['DS 1010']['category_review']['status']=='mixed'
        profile=requirement_profile(p)
        assert profile['required']['count']==(6 if pid=='wpi-ai-bs' else 0)
        assert profile['options']['count']==(211 if pid=='wpi-ai-bs' else 47)
    assert profile['unresolved']['count']==2


def test_optional_actual_current_pages():
    root=Path('.cache/research/wpi-content-review')
    if not root.exists():pytest.skip('Ignored current source pages unavailable')
    for code,entry in m.SPEC.items():
        path=root/(code.lower().replace(' ','-').replace('/','_')+'.html')
        if not path.exists():pytest.skip('Optional source page absent')
        for pid in entry['program_ids']:
            first=m.parse(path.read_text(),program_id=pid,code=code)
            assert first==m.parse(path.read_text(),program_id=pid,code=code)


def test_business_complete_source_partition_and_hua_entry_rules():
    p=json.loads(Path('data/programs/wpi-business-analytics-applied-ai-bs.json').read_text())
    assert len(p['courses'])==49 and all(c['description'] for c in p['courses'])
    profile=requirement_profile(p)
    assert {k:v for k,v in profile['options']['categories'].items() if v} == {
        'foundations':4,'mathematics':11,'ai_ml':6,'systems':3,'human_context':3,'applications':17,'other':3}
    assert profile['unresolved']['categories']['human_context']==2
    courses={c['code']:c for c in p['courses']}
    assert 'Instructor consent' in courses['HU 3910']['prerequisites']
    assert 'at least two thematically related' in courses['HU 3900']['prerequisites']
    assert 'Suggested background (advisory)' in courses['OIE 4430']['prerequisites']
    assert any('OIE4430 and OIE4420' in n for n in p['notes'])
    assert not p.get('course_identity_groups')  # credit exclusions never imply alias identity


def test_complete_content_guard_covers_suggested_background(monkeypatch):
    from bs4 import BeautifulSoup
    from atlas.adapters.cmu_bs.common import text
    entry=copy.deepcopy(m.SPEC['OIE 4430'])
    entry['description_digest']=hashlib.sha256(b'Synthetic prediction methods.').hexdigest()
    entry['recommended_digest']=hashlib.sha256(b'Synthetic background').hexdigest()
    html=fixture('OIE 4430',entry).replace('</main>','<div class="field--name-field-suggested">Synthetic suggested condition</div></main>')
    entry['main_digest']=hashlib.sha256(text(BeautifulSoup(html,'html.parser').find('main')).encode()).hexdigest()
    monkeypatch.setitem(m.SPEC,'OIE 4430',entry)
    m.parse(html,program_id='wpi-business-analytics-applied-ai-bs',code='OIE 4430')
    with pytest.raises(ValueError):
        m.parse(html.replace('Synthetic suggested condition','Different condition'),program_id='wpi-business-analytics-applied-ai-bs',code='OIE 4430')


def test_ai_computing_mathematics_source_rules_preserve_option_scope():
    p=json.loads(Path('data/programs/wpi-ai-bs.json').read_text())
    courses={c['code']:c for c in p['courses']}
    assert courses['MA 1020']['credits']==pytest.approx(1/3)
    assert courses['MA 1120']['credits']==pytest.approx(1/3)
    assert courses['CS 2022/MA 2201']['category']=='mathematics'
    assert courses['CS 4032/MA 3257']['category']=='mathematics'
    assert courses['CS 2301']['category']=='systems'
    assert courses['CS 4344/DS 4344']['category']=='ai_ml'
    assert courses['CS 4445']['category_review']['status']=='mixed'
    assert courses['CS 4804']['category_review']['status']=='mixed'
    assert 'subsequently' in m.SPEC['CS 2301']['credit_restriction']
    assert 'Cannot satisfy' in m.SPEC['CS 3043/SS 3043']['eligibility_note']
    assert 'Suggested background (advisory)' in courses['MA 2210']['prerequisites']
    profile=requirement_profile(p)
    assert [profile[x]['count'] for x in ['required','options','unresolved']]==[6,211,2]
    assert sum('wpi-ai-bs' in e['program_ids'] for e in m.SPEC.values())==77
    assert not p.get('course_identity_groups')
