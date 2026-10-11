import hashlib
import pytest
from atlas.adapters import nd_home_policies as a

@pytest.mark.parametrize('key',list(a.URLS))
def test_scoped_observations_fail_on_changed_policy(monkeypatch,key):
    html='<h1>'+a.TITLES[key]+'</h1>'+''.join('<'+tag+'>'+prefix+' reviewed fixture</'+tag+'>' for tag,prefix in a.PREFIXES[key])
    monkeypatch.setitem(a.HASHES,key,hashlib.sha256(a.observed_text(html,key).encode()).hexdigest())
    result=a.parse_source(html,pid='nd-fixture',key=key)
    assert result['curriculum_status']=='partial' and 'curriculum_audit' not in result
    assert all(r['kind']=='note' and r['source_id']=='nd-fixture-home-'+key for r in result['requirements'])
    with pytest.raises(ValueError,match='review required'):
        a.parse_source(html.replace('reviewed fixture','changed rule'),pid='nd-fixture',key=key)
    with pytest.raises(ValueError,match='identity'):
        a.parse_source(html.replace(a.TITLES[key],'Wrong college'),pid='nd-fixture',key=key)

def test_home_colleges_remain_conditional_and_conflict_visible():
    assert 'not applied' in a.POLICIES['engineering'][0][2]
    assert 'do not explain' in a.POLICIES['arts-letters'][0][2]
    assert '50% unique' in a.POLICIES['science'][1][2]
    sources=[];parsers={};a.register('nd-fixture',sources,parsers)
    assert set(sources)==set(parsers)==set(a.URLS.values())
