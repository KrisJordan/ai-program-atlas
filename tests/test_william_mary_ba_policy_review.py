import hashlib
import importlib.util
import json
from html import escape
from pathlib import Path

import pytest
from atlas import db
from atlas.adapters import william_mary_ba_policy_review as m
from atlas.curriculum_profile import requirement_profile


@pytest.mark.parametrize('key',list(m.SPECS))
def test_observer_requires_actual_material_policy_and_emits_no_audit(key):
    _,heading,rows=m.SPECS[key]
    html='<main><h1>'+heading+'</h1>'+''.join('<p>'+escape(p)+'</p>' for _,_,phrases,_ in rows for p in phrases)+'</main>'
    result=m.parse(html,key)
    assert len(result['requirements'])==len(rows)
    assert result['courses']==[]
    assert not {'curriculum_status','curriculum_audit','last_verified'} & result.keys()
    assert all(r['kind']=='note' and not r['course_ids'] for r in result['requirements'])
    for _,_,phrases,_ in rows:
        with pytest.raises(ValueError):
            m.parse(html.replace(escape(phrases[0]),'changed policy'),key)
    with pytest.raises(ValueError):
        m.parse('<h1>Sign in</h1>',key)


@pytest.mark.parametrize('key',list(m.SPECS))
def test_current_public_source_cache_when_available(key):
    url,_,rows=m.SPECS[key]
    path=Path('.cache/http',hashlib.sha256(url.encode()).hexdigest()+'.body')
    if not path.exists():pytest.skip('Ignored permitted public policy cache unavailable')
    spec=importlib.util.spec_from_file_location('wm_ba_adapter',Path('atlas/adapters',m.PID,'adapter.py'))
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    o=adapter.SOURCE_PARSERS[url](path.read_text())
    assert len(o['requirements'])==len(rows)
    assert 'curriculum_audit' not in o


def test_integrated_policies_preserve_unresolved_identity_and_partial_scope():
    p=json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    assert p['curriculum_status']=='partial' and len(p['courses'])==3
    assert all(c['credits'] is None for c in p['courses'])
    profile=requirement_profile(p)
    assert profile['required']['count']==3 and profile['options']['count']==0
    rules={r['id']:r for r in p['requirements']}
    assert 'CDSP' in rules[m.PID+'-public-passfail-eligibility']['summary']
    assert 'major/minor' in rules[m.PID+'-public-passfail-exclusions']['summary'].lower()
    assert 'not as an unconditional two-attempt cap' in rules[m.PID+'-public-repeat-current']['summary']
    ledger=json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())
    entry=next(r for r in ledger['programs'] if r['program_id']==m.PID)
    assert entry['status']=='in_progress'
    assert entry['expected_profile']['required']['count']==3
    assert any(s['url']=='https://catalog.wm.edu/' and s['access_status']=='inaccessible' for s in entry['sources'])
    assert any('DATA' in b['issue'] or 'identity' in b['issue'] for b in entry['blockers'])
