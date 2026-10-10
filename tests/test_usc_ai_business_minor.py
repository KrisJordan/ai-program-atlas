"""USC common minor rules stay distinct from an unverified course inventory."""
import importlib,json,hashlib
from pathlib import Path
import pytest
from atlas.db import validate_program
PID='university-of-southern-california-applied-ai-in-business-minor-minor'
a=importlib.import_module('atlas.adapters.'+PID+'.adapter')
ROOT=Path(__file__).resolve().parents[1]
# Synthetic reduction of applicable policy markers; not a saved source page.
POLICIES='''<main><h1>Marshall Minors</h1><a href="catalog">Applied AI in Business Minor</a>
<p>completion of 32-48 units, a declared major, and a minimum USC GPA of 2.75;
maximum of three Marshall courses prior to admission;
Applications to Marshall minors are accepted throughout the year;
all the necessary prerequisites for each course;
without pre-requisite waivers, course substitutions or exceptions;
minimum of 16 unique units outside of your home academic department;
Students admitted to a Marshall minor are admitted to the current Catalogue year;
with some exceptions depending on your specific program of study.</p></main>'''


def test_policy_observation_has_no_fabricated_courses_total_or_audit():
    result=a.parse_policies(POLICIES)
    assert len(result['requirements'])==6
    assert not {'courses','curriculum_status','curriculum_audit','last_verified'} & result.keys()
    assert all(g['kind']=='note' and g['credits'] is None for g in result['requirements'])


@pytest.mark.parametrize('old,new',[('Applied AI in Business Minor','Other Minor'),('GPA of 2.75','GPA of 3.0'),('16 unique units','12 unique units'),('without pre-requisite waivers','with pre-requisite waivers')])
def test_material_change_or_missing_applicability_fails(old,new):
    with pytest.raises(ValueError):a.parse_policies(POLICIES.replace(old,new))


def test_access_navigation_and_unrelated_pages_fail():
    for html in ('<main><h1>Other</h1></main>','<title>Sign in</title>'+POLICIES,'<nav>'+POLICIES.replace('<main>','').replace('</main>','')+'</nav><main><h1>Other</h1></main>'):
        with pytest.raises(ValueError):a.parse_policies(html)


def test_curated_seed_and_available_live_cache():
    data=json.loads((ROOT/'data/programs'/(PID+'.json')).read_text());validate_program(data)
    assert data['curriculum_status']=='partial' and not data['courses']
    assert data['first_offered']['value']=='Fall 2026' and data['first_offered']['uncertainty']
    for url in a.SOURCES:
        p=ROOT/'.cache/http'/(hashlib.sha256(url.encode()).hexdigest()+'.body')
        if p.exists():assert a.SOURCE_PARSERS[url](p.read_text())['id']==PID
