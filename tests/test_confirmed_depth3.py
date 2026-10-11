import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters import confirmed_depth3 as p
from atlas.db import validate_program

IDS = json.loads(Path('data/national-confirmed-depth-batch3-manifest.json').read_text())


def test_wpi_observes_course_changes_and_requires_formal_host():
    title = 'Artificial Intelligence Major with Concentration in Test'
    html = f'''<article class="node--type-degree"><h1>{title}</h1>
    <div class="field--name-field-degree-type"><div class="field__item">Concentration</div></div>
    <ul class="concentration-usage"><li>Artificial Intelligence Major</li></ul>
    <article class="node--type-class"><div class="col-3"><a href="/test">TEST 1000</a></div>
    <div class="col-7">Synthetic title</div><div class="field--name-field-credits">1/2</div></article></article>'''
    r = p.parse_wpi(html, 'test', title, 'https://wpi.cleancatalog.net/')
    assert r['courses'][0]['credits'] == .5
    assert r['courses'][0]['name'] == 'Synthetic title'
    assert r['requirements'][0]['kind'] == 'note'
    assert 'curriculum_audit' not in r
    with pytest.raises(ValueError):
        p.parse_wpi(html.replace('>Concentration<', '>Certificate<'), 'test', title, '')


def test_psu_numeric_degree_minimum_requires_explicit_award_statement():
    title = 'Artificial Intelligence Engineering, B.S.'
    html = f'<h1>{title}</h1><p>Plan Code: AIE_BS; University Park</p><div id="programrequirementstextcontainer">For the Bachelor of Science degree in Artificial Intelligence Engineering, a minimum of 129 credits is required</div>'
    r = p.parse_psu(html, 'test', title, 'AIE_BS')
    assert r['requirements'][0]['credits'] == 129
    with pytest.raises(ValueError):
        p.parse_psu(html.replace('Bachelor of Science', 'minor'), 'test', title, 'AIE_BS')


def test_delaware_does_not_promote_informal_interests():
    heading = 'BS Computer Science with Concentration in Artificial Intelligence and Robotics'
    html = '<h4>' + heading + '</h4><p>An official University credential appears on the student transcript.</p>'
    assert p.parse_delaware(html)['program_kind'] == 'concentration'
    with pytest.raises(ValueError):
        p.parse_delaware('<h4>' + heading + '</h4><p>Research interest.</p>')


def test_rit_immersion_requires_its_own_plan_not_minor_title():
    html = '<h1>AI in Society Immersion</h1><p>The plan code for AI in Society Immersion is AISTS-IM.</p>'
    assert p.parse_rit_immersion(html)['title'] == 'AI in Society Immersion'
    with pytest.raises(ValueError):
        p.parse_rit_immersion(html.replace('AISTS-IM', 'AISTS-MN'))


@pytest.mark.parametrize('pid', IDS)
def test_new_records_and_adapter_identity(pid):
    d = json.loads(Path('data/programs/' + pid + '.json').read_text())
    validate_program(d)
    assert d['curriculum_status'] in ['complete', 'partial', 'pending']
    if d['curriculum_status'] == 'complete':
        assert d['curriculum_audit']['unresolved_requirements'] == []
    assert d['first_offered'] is None
    spec = importlib.util.spec_from_file_location('candidate', 'atlas/adapters/' + pid + '/adapter.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert mod.PROGRAM_ID == pid
    assert mod.SOURCES[0] == d['sources'][0]['url']
    with pytest.raises(ValueError):
        mod.parse('<h1>Access denied</h1>')


def test_depth_ledger_keeps_campus_and_graduate_exclusions_explicit():
    rows = json.loads(Path('data/surveys/national-confirmed-depth-batch3.json').read_text())
    assert len(rows) == 6
    psu = next(r for r in rows if r['institution_id'] == 'pennsylvania-state-university')
    assert 'Harrisburg' in psu['note']
    assert not any('capital' in p or 'harrisburg' in p for p in IDS)
    rit = next(r for r in rows if r['institution_id'] == 'rochester-institute-of-technology')
    assert 'graduate' in rit['note']
