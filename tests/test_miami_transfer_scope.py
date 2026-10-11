import json
from pathlib import Path
import pytest
from atlas.adapters import miami_transfer_scope as m


def actual():
    p=Path('.cache/research/miami-degree-audit/policy-transfer.html')
    if not p.exists():pytest.skip('Ignored current official source capture unavailable')
    return p.read_text()


def test_actual_scope_preserves_credit_exclusion_without_false_conflict():
    for pid in m.PROGRAMS:
        out=m.parse(actual(),pid=pid)
        assert len(out['requirements'])==2 and out['courses']==[]
        byid={r['id']:r for r in out['requirements']}
        p=json.loads(Path('data/programs',pid+'.json').read_text())
        for old in p['requirements']:
            if old['id']in byid:assert old['summary']==byid[old['id']]['summary']
        assert 'Session A' in m.SUMMER and 'Session B' in m.SUMMER
        assert 'does not grant transfer credit' in m.SUMMER
        assert 'reserves the right to reject' in m.PROCESS
        assert not any('inconsistent summer'in x for x in p['curriculum_audit']['unresolved_requirements'])
        assert p['curriculum_status']=='partial'


@pytest.mark.parametrize('old,new',[('Excluding the summer semester','Including the summer semester'),('a Session A course at UM and a Session B course elsewhere','a Session A course at UM and a Session A course elsewhere'),('reserves the right to reject','must accept')])
def test_changed_scope_or_discretion_requires_review(old,new):
    html=actual();assert old in html
    with pytest.raises(ValueError):m.parse(html.replace(old,new),pid=next(iter(m.PROGRAMS)))


def test_wrong_source_and_unreviewed_program_rejected():
    with pytest.raises(ValueError):m.parse('<h1>Other university policy</h1>',pid=next(iter(m.PROGRAMS)))
    with pytest.raises(ValueError):m.parse(actual(),pid='unrelated-degree')
