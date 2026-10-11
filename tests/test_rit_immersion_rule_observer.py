import json
from pathlib import Path
import pytest
from atlas.adapters.rit_immersion_rule_observer import parse

TITLE = 'Example Immersion'
def fixture(rows):
    return '<main><h1>Example Immersion</h1><h2>Curriculum for 2026-2027 for Example Immersion</h2><table class="sc_courselist"><tbody>'+rows+'</tbody></table></main>'


def test_observes_credit_rules_and_repeated_identity_without_seed_replay():
    html = fixture('<tr><td colspan="3">At least 3 credits</td></tr><tr><td><a class="code_bubble">ITDL-511</a></td><td>Project</td><td>1-3</td></tr><tr><td colspan="3">Six more credits</td></tr><tr><td><a class="code_bubble">ITDL-511</a></td><td>Project</td><td>1-3</td></tr>')
    r = parse(html, title=TITLE)
    assert r['observed_tables'][0]['rows'][1]['course_codes'] == ['ITDL-511']
    assert r['observed_tables'][0]['rows'][3]['course_codes'] == ['ITDL-511']
    assert r['requirements'] == r['courses'] == []
    assert 'audit' not in r and 'category_review' not in r
    changed = parse(html.replace('At least 3 credits', 'At least 6 credits'), title=TITLE)
    assert changed['observed_tables'][0]['rows'][0]['cells'] == ['At least 6 credits']


def test_rejects_access_shell_wrong_identity_and_year():
    valid = fixture('<tr><td>Choose three</td></tr>')
    for html in [valid.replace('2026-2027','2025-2026'),valid.replace('<h1>Example','<h1>Other'),valid.replace('<tbody>','<tbody><input type="password">'),'<main><h1>Example Immersion</h1></main>']:
        with pytest.raises(ValueError):parse(html,title=TITLE)


def test_reviewed_stem_inventory_preserves_roles_conditions_and_unknowns():
    data = json.loads(Path('research/rit-immersion-routes-stem.json').read_text())
    rows = {r['id']:r for r in data['routes']}
    assert len(rows) == 15
    assert sum(len({c for g in r['groups'] for c in g['course_codes']}) for r in rows.values()) == 156
    assert len({c for r in rows.values() for g in r['groups'] for c in g['course_codes']}) == 132
    chem = rows['chemistry-immersion']
    assert chem['groups'][0]['role'] == 'preparation_alternative'
    assert len(chem['groups'][0]['course_codes']) == 5
    assert rows['biology-cellular-and-molecular-immersion']['total_hours'] == 10
    vip = rows['vertically-integrated-projects-immersion']
    assert vip['plan_code'] is None and vip['groups'][0]['role'] == 'required_credits'
    assert vip['groups'][0]['published_hours'] == 'at least 3'
    assert rows['principles-computing-immersion']['unresolved_source_questions']
    assert rows['free-culture-and-free-and-open-source-computing-immersion']['unresolved_source_questions']
    for r in rows.values():
        assert r['course_metadata_reviewed'] == 0
        assert all('category_review' not in g for g in r['groups'])
