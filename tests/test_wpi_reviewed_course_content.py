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
        path=root/(code.lower().replace(' ','-')+'.html')
        if not path.exists():pytest.skip('Optional source page absent')
        for pid in entry['program_ids']:
            first=m.parse(path.read_text(),program_id=pid,code=code)
            assert first==m.parse(path.read_text(),program_id=pid,code=code)
