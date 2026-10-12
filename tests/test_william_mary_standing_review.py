import json
from html import escape
from pathlib import Path
import pytest
from atlas import db
from atlas.adapters import william_mary_standing_review as m


def fixture(key):
    _, heading, rows = m.SPECS[key]
    html = '<main><h1>'+heading+'</h1>'+''.join('<p>'+escape(p)+'</p>' for _,_,phrases,_ in rows for p in phrases)
    if key == 'continuance':
        html += '<table>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in m.CONTINUANCE)+'</table>'
    return html+'</main>'


@pytest.mark.parametrize('key', list(m.SPECS))
def test_source_policy_observation_requires_identity_and_material_text(key):
    html = fixture(key)
    observed = m.parse(html, key)
    assert len(observed['requirements']) == len(m.SPECS[key][2])
    assert observed['courses'] == []
    assert not {'curriculum_audit','curriculum_status','last_verified'} & observed.keys()
    for _,_,phrases,_ in m.SPECS[key][2]:
        with pytest.raises(ValueError):m.parse(html.replace(escape(phrases[0]), 'changed policy'), key)
    with pytest.raises(ValueError):m.parse('<main><h1>Sign in</h1></main>', key)


def test_changed_continuance_cell_not_certified_by_unchanged_prose():
    html = fixture('continuance')
    with pytest.raises(ValueError, match='table'):
        m.parse(html.replace('<td>1.85</td>','<td>1.95</td>'), 'continuance')
    with pytest.raises(ValueError, match='table'):
        m.parse(html.replace('<td>120</td>','<td>121</td>'), 'continuance')


@pytest.mark.parametrize('key', list(m.SPECS))
def test_actual_public_source_replay_when_available(key):
    path = Path('/tmp/atlas-wm-'+key+'.html')
    if not path.exists():pytest.skip('Local permitted public source capture unavailable')
    assert len(m.parse(path.read_text(), key)['requirements']) == len(m.SPECS[key][2])


def test_integrated_policy_preserves_conflicts_and_conditional_scope():
    p = json.loads(Path('data/programs',m.PID+'.json').read_text());db.validate_program(p)
    assert p['curriculum_status'] == 'partial'
    assert p['institution']['calendar'] == 'semester'
    assert next(c for c in p['courses'] if c['code']=='DATA 305')['credit_unit']=='unknown'
    rules = {r['id']: r for r in p['requirements']}
    assert '2.0 overall' in rules[m.PID+'-standing-continuance-degree']['summary']
    assert 'Only admitted or approved FlexTrack' in rules[m.PID+'-standing-flex-route']['summary']
    assert 'does not itself establish a ten-semester' in rules[m.PID+'-standing-continuance-thresholds']['summary']
    assert 'applicability remains unresolved' in rules[m.PID+'-standing-probation-qualification']['summary']
    ledger=json.loads(Path('research/degree-audit/national-degree-batch.json').read_text())
    e=next(x for x in ledger['programs'] if x['program_id']==m.PID)
    assert e['status']=='blocked' and e['expected_profile']['required']['count']==7
    assert 'full-degree and independent second pass remain incomplete' in e['correction_status']
