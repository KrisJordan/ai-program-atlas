"""Real course content and conditional eligibility are independently bounded."""
import hashlib
import importlib
import json
from pathlib import Path
import pytest
m=importlib.import_module('atlas.adapters.mit-ai-decision-making-bs.clinic_review')


def test_changed_clinic_content_withdraws_interpretation(monkeypatch):
    html='<main>Actual reviewed clinic example.</main>'
    monkeypatch.setitem(m.SPECS['news'],'content_digest',hashlib.sha256(b'Actual reviewed clinic example.').hexdigest())
    out=m.parse('news',html)
    assert out['courses'][0]['category']=='other'
    assert out['courses'][0]['prerequisites'] is None
    assert 'in-course condition' in out['requirements'][0]['summary']
    assert 'category_review' not in out['courses'][0]
    assert m.parse('news',html.replace('example','revision'))['courses']==[]
    with pytest.raises(ValueError):m.parse('news','<input type="password"><main>Login</main>')


@pytest.mark.parametrize('key,index',[('home',0),('news',2)])
def test_actual_clinic_source_replays_exact_read(key,index):
    p=Path(f'/tmp/mit-policy-followup-{index}.html')
    if not p.exists():pytest.skip('Optional public source capture absent')
    out=m.parse(key,p.read_text())
    assert len(out['courses'])==1 and out['requirements']
    assert not {'curriculum_status','curriculum_audit','last_verified'}&out.keys()


def test_clinic_seed_keeps_role_and_explicit_source_distinctions():
    d=json.loads(Path('data/programs/mit-ai-decision-making-bs.json').read_text())
    c=next(c for c in d['courses']if c['id']=='mit-ai-hass-urban-11-074')
    assert c['category_review']['status']=='mixed' and c['description']
    assert c['category']=='other' and c['credits'] is None and c['prerequisites'] is None
    assert c['source_id']=='mit-ai-decision-making-bs-hass-urban'
    assert c['public_site']==m.SPECS['home']['url']
    assert not any(x.startswith('Urban Studies lists')for x in d['curriculum_audit']['unresolved_requirements'])
    assert any('asterisk' in x for x in d['curriculum_audit']['metadata_gaps'])
    rules=[r for r in d['requirements']if r['id'].startswith('mit-ai-clinic-')]
    assert rules and all(r['kind']=='note'and r['parent_id']=='mit-ai-hass-urban'for r in rules)
