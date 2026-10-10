"""Synthetic fixtures exercise changed rules and program-section isolation."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters.vt_duke_minors import parse_vt, parse_duke_ml, parse_duke_apps, policy_observation
from atlas.requirements import validate_requirements, validate_curriculum_audit


def ml_fixture(n=2):
 def section(title,body):return '<li class="accordion"><h3>'+title+'</h3><div class="accordion__text">'+body+'</div></li>'
 return '<section><h2>Other minor</h2><p>ECE 999 Unrelated</p></section><section><h2><a name="ml"></a>Minor in Machine Learning &amp; Artificial Intelligence</h2><p>A minimum of five (5) technical courses.</p><ul>'+section('Fundamental Courses','<ul><li>ECE 480 Probability</li><li>ECE 580 Machine learning</li><li>Choose one<ul><li>ECE 682D/CS 571D/Stat 561D</li><li>ECE 687D/CS 671D/STA 671D</li></ul></li></ul>')+section('Upper-Level Focus Courses',f'<h4>Choose ({n})</h4><ul><li>ECE 585: Test course</li><li>Approved topics<ul><li>ME 555: Robot Learning</li><li>ME 555: Dynamic Systems</li></ul></li></ul>')+section('Note on Prerequisites','<p>Course prerequisites must be satisfied.</p>')+section('Notes on Course Counting','<ul><li>No major overlap.</li></ul>')+'</ul></section>'


def test_ml_scope_crosslists_topics_changed_count():
 p=parse_duke_ml(ml_fixture(),'test','s','https://example.edu')
 validate_requirements(p)
 assert len(p['courses'])==7
 assert not any(c['code']=='ECE 999' for c in p['courses'])
 assert len([c for c in p['courses'] if c['code']=='ME 555'])==2
 assert next(c for c in p['courses'] if c['code'].startswith('ECE 682'))['name'] is None
 q=parse_duke_ml(ml_fixture(3),'test','s','https://example.edu')
 assert next(r for r in q['requirements'] if r['id']=='duke-ml-focus')['count']==3
 assert p['observed_policy_digest']!=q['observed_policy_digest']
 assert 'curriculum_audit' not in q and 'last_verified' not in q


def apps_fixture(units=1):
 return '<main><p>Students may not receive more than one minor. Computer Science majors have restrictions.</p><div><h4>Minor in Artificial Intelligence: Applications and Implications</h4><h5>Prerequisites (5 Units)</h5><ol><li>COMPSCI 230 - Discrete math OR 231D - Proofs OR 232 - Math</li><li>MATH 230/STA 230 - Probability</li></ol><h5>Core (3 units)</h5><ol><li>COMPSCI 201</li><li>COMPSCI 370D OR COMPSCI 570</li></ol>'+f'<h5>Minor Elective ({units} unit)</h5><p>COMPSCI course OUTSIDE COMPSCI.</p><ul><li>BME 502, BME 503</li><li>PUBPOL 255 (cross COMPSCI 255)</li></ul><h5>Free Elective (1 unit)</h5><p>Approved concentration elective OR independent study</p></div></main>'


def test_apps_choices_crosslists_and_changed_units():
 p=parse_duke_apps(apps_fixture(),'test','s','https://example.edu');validate_requirements(p)
 assert any(c['code']=='COMPSCI 231D' and c['name']=='Proofs' for c in p['courses'])
 assert sum(c['code']=='MATH 230 / STA 230' for c in p['courses'])==1
 assert sum(c['code']=='PUBPOL 255 / COMPSCI 255' for c in p['courses'])==1
 assert any('OUTSIDE' in r['summary'] for r in p['requirements'])
 q=parse_duke_apps(apps_fixture(2),'test','s','https://example.edu')
 assert next(r for r in q['requirements'] if r['id']=='duke-apps-group-2')['credits']==2
 assert all(c['credits'] is None and c['prerequisites'] is None for c in p['courses'])


def test_vt_observes_changed_declaration_without_inventing_curriculum():
 h='<main><h1>Artificial Intelligence (AI) Minor</h1><h3>Who should pursue this minor</h3><p>Any undergraduate.</p><h3>How to pursue the minor</h3><p>Declare August 2026.</p></main>'
 p=parse_vt(h,'test','s','https://example.edu');q=parse_vt(h.replace('2026','2027'),'test','s','https://example.edu')
 assert p['courses']==[] and p['curriculum_status']=='partial'
 assert '2027' in q['requirements'][1]['summary'] and p['observed_policy_digest']!=q['observed_policy_digest']
 with pytest.raises(ValueError):parse_vt('<h1>Other minor</h1>','test','s','https://example.edu')


@pytest.mark.parametrize('pid,n',[
 ('virginia-tech-artificial-intelligence-ai-minor-minor',0),
 ('duke-university-machine-learning-artificial-intelligence-minor-minor',25),
 ('duke-university-artificial-intelligence-applications-and-implications-minor-minor',47),
])
def test_reviewed_partial_records_keep_gaps_explicit(pid,n):
 p=json.loads((Path(__file__).resolve().parents[1]/'data/programs'/f'{pid}.json').read_text())
 validate_requirements(p);validate_curriculum_audit(p)
 assert p['curriculum_status']=='partial' and p['curriculum_audit']['unresolved_requirements']
 assert len(p['courses'])==n and len({c['id'] for c in p['courses']})==n
 assert p['first_offered'] is None
 m=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 assert set(m.SOURCE_PARSERS)==set(m.SOURCES[1:])
