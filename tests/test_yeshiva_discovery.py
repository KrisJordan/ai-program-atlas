import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'atlas/adapters/yeshiva-cs-ai-concentration/adapter.py'
spec=importlib.util.spec_from_file_location('yeshiva_discovery',P)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def fixture():
    return '''<nav>Artificial Intelligence Concentration Requirements (99 credits)</nav>
    <main id="main"><h1>Computer Science, BS</h1><div id="degreeRequirements">
    <h2>Overview</h2><p>The Computer Science major includes concentrations in Artificial Intelligence and Distributed Systems.</p>
    <h2>Degree Requirements</h2><p>BS requirements <a href="/en/current/university-catalog/undergraduate-programs/general-education-and-jewish-studies-requirements/yeshiva-college-bs">Yeshiva College</a></p>
    <h2>Artificial Intelligence Concentration Requirements (7 credits)</h2><h3></h3>
    <table><tbody><tr><td><a href="/en/current/university-catalog/courses-by-subject-area/com-computer-science-um-gr/3000/com-3760">COM 3760</a></td><td>Artificial Intelligence</td><td>3</td></tr>
    <tr><td><a href="/en/current/university-catalog/courses-by-subject-area/mat-mathematics-um-gr/1000/mat-1412">MAT 1412</a></td><td>Calculus I</td><td>4</td></tr></tbody></table>
    <h2>Distributed Systems Concentration Requirements (3 credits)</h2><table><tr><td>COM 4580</td><td>Cybersecurity</td><td>3</td></tr></table>
    </div></main>'''

def test_only_ai_table_and_unknown_units():
    r=mod.parse(fixture())
    assert [c['code'] for c in r['courses']]==['COM 3760','MAT 1412']
    assert all(c['credit_unit']=='unknown' and c['prerequisites'] is None for c in r['courses'])
    assert r['curriculum_status']=='partial'
    assert 'curriculum_audit' not in r and 'last_verified' not in r

def test_live_input_changes_are_extracted():
    html=fixture().replace('7 credits','8 credits').replace('<td>3</td></tr>','<td>4</td></tr>',1).replace('COM 3760','COM 3920').replace('Artificial Intelligence</td>','Machine Learning</td>')
    r=mod.parse(html)
    assert r['courses'][0]['code']=='COM 3920'
    assert r['courses'][0]['name']=='Machine Learning'
    assert r['requirements'][0]['credits']==8

@pytest.mark.parametrize('before,after',[
    ('Computer Science, BS','Computer Science, MS'),
    ('The Computer Science major includes concentrations in Artificial Intelligence and Distributed Systems.','Artificial Intelligence is a course.'),
    ('/yeshiva-college-bs','/stern-college-ba'),
    ('7 credits','9 credits'),
    ('<td>4</td>','<td>3 or 4</td>'),
    ('<h3></h3>','<h3>Choose one course</h3>'),
    ('<table><tbody>','<p>Complete two options.</p><table><tbody>'),
    ('/en/current/university-catalog/courses-by-subject-area/com-computer-science-um-gr/3000/com-3760','https://example.com/course'),
])
def test_changed_or_ambiguous_scope_fails(before,after):
    with pytest.raises(ValueError):mod.parse(fixture().replace(before,after))

def test_navigation_alone_does_not_establish_award():
    with pytest.raises(ValueError):mod.parse('<nav>'+fixture()+'</nav>')

def test_reviewed_seed_scope_and_live_replay_if_available():
    from atlas.db import validate_program
    seed=json.loads((ROOT/'data/programs/yeshiva-cs-ai-concentration.json').read_text())
    validate_program(seed)
    assert seed['award_level']=='concentration' and seed['hosting_unit']=='Yeshiva College'
    assert len(seed['courses'])==22 and seed['curriculum_status']=='partial'
    assert seed['first_offered'] is None and seed['catalog_year']=='2026-2027'
    assert all(o['statement_type']!='learning_outcome' for o in seed['outcomes'])
    cache=ROOT/'.cache/research/yeshiva-cs-ai.html'
    if cache.exists():
        result=mod.parse(cache.read_text())
        assert [(c['id'],c['code'],c['name'],c['credits']) for c in result['courses']]==[(c['id'],c['code'],c['name'],c['credits']) for c in seed['courses']]
        assert {k:v for k,v in result['requirements'][0].items() if k!='credit_unit'}=={k:v for k,v in seed['requirements'][0].items() if k!='credit_unit'}
        assert seed['requirements'][0]['credit_unit']=='semester'
