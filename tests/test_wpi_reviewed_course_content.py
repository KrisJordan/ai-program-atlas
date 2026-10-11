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
        path=root/(entry.get('heading_code',code).lower().replace(' ','-').replace('/','_')+'.html')
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
    assert sum('wpi-ai-bs' in e['program_ids'] for e in m.SPEC.values())==144
    assert not p.get('course_identity_groups')


def test_graduate_native_credit_and_qualified_prerequisite_guard(monkeypatch):
    from bs4 import BeautifulSoup
    from atlas.adapters.cmu_bs.common import text
    code='CS 542';entry=copy.deepcopy(m.SPEC[code])
    desc='Synthetic database internals.';pr='Synthetic preparation would be helpful.'
    html=f'<p>Graduate Catalog</p><main><h1>{code}: {entry["name"]}</h1><div class="field--name-field-description">{desc}</div><div class="field--name-field-credits"><div class="field__item">3</div></div><div class="field--name-field-pr"><div class="field__item">{pr}</div></div></main>'
    entry['main_digest']=hashlib.sha256(text(BeautifulSoup(html,'html.parser').find('main')).encode()).hexdigest()
    entry['description_digest']=hashlib.sha256(desc.encode()).hexdigest()
    entry['prerequisite_digest']=hashlib.sha256(pr.encode()).hexdigest()
    monkeypatch.setitem(m.SPEC,code,entry)
    course=m.parse(html,program_id='wpi-ai-bs',code=code)['courses'][0]
    assert course['credits']==3 and course['credit_unit']=='unknown'
    assert 'would be helpful' in course['prerequisites']
    assert entry['catalog_year'] is None and 'category_review' not in course
    for changed in [html.replace('would be helpful','is required'),html.replace('Graduate Catalog','Unidentified Catalog'),html.replace('>3<','>4<')]:
        with pytest.raises(ValueError):m.parse(changed,program_id='wpi-ai-bs',code=code)


def test_graduate_mixtures_and_source_version_limits():
    p=json.loads(Path('data/programs/wpi-ai-bs.json').read_text());c={x['code']:x for x in p['courses']}
    for code in ['CS 555/DS 555','CS 553/DS 553','CS 586/DS 504','CS 547/DS 547']:
        assert c[code]['category']=='other' and c[code]['category_review']['status']=='mixed'
    assert c['CS 509']['category']=='foundations'
    assert c['CS 585/DS 503']['category']=='systems'
    assert c['CS 551/DS 551']['category']=='ai_ml'
    grad=[e for e in m.SPEC.values() if e.get('catalog_heading')=='Graduate Catalog']
    assert len(grad)==20 and all(e['catalog_year'] is None and e['credit_unit']=='unknown' for e in grad)


def test_engineering_subjects_and_explicit_description_referral(monkeypatch):
    from bs4 import BeautifulSoup
    from atlas.adapters.cmu_bs.common import text
    p=json.loads(Path('data/programs/wpi-ai-bs.json').read_text());c={x['code']:x for x in p['courses']}
    assert c['RBE 2002']['category']=='applications'
    assert c['RBE 4744']['category']=='ai_ml'
    assert c['RBE 4601']['category']=='human_context'
    assert c['ECE 2311']['category']=='mathematics'
    assert c['ECE 4801']['category']=='systems'
    assert c['RBE 2020']['category_review']['status']=='mixed'
    code='ECE 545/CS 545';entry=copy.deepcopy(m.SPEC[code])
    assert entry['heading_code']=='CS 545/ECE 545'
    assert len(c[code]['category_review']['source_ids'])==2
    html='<main><h1>Synthetic referral</h1><p>See the named companion description.</p></main>'
    entry['referral_main_digest']=hashlib.sha256(text(BeautifulSoup(html,'html.parser').find('main')).encode()).hexdigest()
    monkeypatch.setitem(m.SPEC,code,entry)
    result=m.parse_referral(html,program_id='wpi-ai-bs',code=code)
    assert not result['courses'] and not result['requirements']
    with pytest.raises(ValueError):m.parse_referral(html.replace('companion','unrelated'),program_id='wpi-ai-bs',code=code)


def test_life_science_domain_content_and_scoped_credit_rules():
    p=json.loads(Path('data/programs/wpi-ai-bs.json').read_text());c={x['code']:x for x in p['courses']}
    for code in ['BB 3080','BB 3010/BCB 3010','BB 4001/BCB 4001','CH 4210']:
        assert c[code]['category']=='applications'
        assert c[code]['category_review']['status']=='reviewed'
    assert c['CH 3520']['category']=='mathematics'
    assert c['CHE 3501']['category']=='mathematics'
    for code in ['CHE 2011','CHE 2012','CHE 2013']:
        assert 'CHE distribution' in c[code]['prerequisites']
        assert c[code]['credits']==pytest.approx(1/3)
    assert 'general chemistry' in m.SPEC['CH 2310']['audience_note']
