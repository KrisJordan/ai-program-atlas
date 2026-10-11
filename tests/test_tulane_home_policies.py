import hashlib
import pytest
from atlas.adapters import tulane_home_policies as a

@pytest.mark.parametrize('key',list(a.URLS))
def test_reviewer_and_html_paths_preserve_scope_and_reject_drift(monkeypatch,key):
    paras=[prefix+' reviewed fixture.' for prefix in a.PREFIXES[key]]
    value=' '.join(paras)
    monkeypatch.setitem(a.HASHES,key,hashlib.sha256(value.encode()).hexdigest())
    html='<h1>'+a.TITLES[key]+'</h1>'+''.join('<p>'+v+'</p>' for v in paras)
    result=a.parse_source(html,pid='tulane-fixture',key=key)
    assert result==a.parse_reviewed(value,pid='tulane-fixture',key=key)
    assert result['curriculum_status']=='partial' and 'curriculum_audit' not in result
    assert result['requirements'][0]['kind']=='note'
    with pytest.raises(ValueError,match='review required'):
        a.parse_source(html.replace('reviewed fixture','changed rule'),pid='tulane-fixture',key=key)
    with pytest.raises(ValueError,match='identity'):
        a.parse_source(html.replace(a.TITLES[key],'Other school'),pid='tulane-fixture',key=key)

def test_cross_unit_conflict_and_graduate_exclusion_stay_visible():
    assert 'remains unresolved' in a.POLICIES['business'][1]
    assert 'graduate' in a.POLICIES['public-health-tropical-medicine'][1]
    sources=[];parsers={};a.register('tulane-fixture',sources,parsers)
    assert set(sources)==set(parsers)==set(a.URLS.values())
