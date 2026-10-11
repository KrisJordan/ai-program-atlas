import json
from pathlib import Path
import pytest
from atlas.adapters.rit_ecology_gender_integration import parse_ecology,parse_rules
from atlas.adapters.rit_writing_closure import PID


def fixture():
    title='Biology: Ecology and Evolution Immersion'
    return f'<main><h1>{title}</h1><h2>Curriculum for 2026-2027 for {title}</h2><table class="sc_courselist"><tbody><tr><td><a class="code_bubble">BIOL-240</a></td><td>Ecology</td><td>3-4</td></tr><tr><td><a class="code_bubble">MEDS-250</a></td><td>Anatomy</td><td></td></tr></tbody></table></main>'+''.join('<div class="courseblock"><span class="detail-code">'+code+'</span><span class="detail-title">Synthetic '+code+'</span><span class="detail-hours_html">(4 Credits)</span><div class="courseblockextra">Observed domain investigation.</div></div>' for code in ['BIOL-240','MEDS-250'])


def test_composed_actual_panels_have_correct_sources_without_manual_reviews():
    o=parse_ecology(fixture());c={x['code']:x for x in o['courses']}
    assert c['BIOL-240']['source_id']=='rit-biology-ecology-course-cards-2026-2027'
    assert c['MEDS-250']['source_id']=='rit-applied-science-ecology-cards-2026-2027'
    assert all(x['credits']==4 and x['category']=='other' and 'category_review' not in x for x in c.values())
    assert o['requirements']==[] and 'curriculum_audit' not in o
    with pytest.raises(ValueError):parse_ecology(fixture().replace('MEDS-250','MEDS-999'))
    with pytest.raises(ValueError):parse_ecology(fixture().replace('2026-2027','2025-2026'))


def test_exact_required_choice_overlap_and_gender_conditions_stay_local():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']};c={x['code']:x for x in d['courses']}
    a=r['biology-ecology-and-evolution-immersion-required'];b=r['biology-ecology-and-evolution-immersion-electives']
    assert a['kind']=='alternative' and a['count']==1 and a['credits'] is None
    assert b['kind']=='choose_courses' and b['count']==2 and b['credits'] is None
    assert set(a['course_ids'])<set(b['course_ids']) and len(b['course_ids'])==11
    assert c['BIOL-240']['credits']==4 and c['MEDS-250']['credits']==4
    assert 'RIT Global' in c['ENVS-310']['prerequisites']
    assert 'MEDS-250' not in c['MEDS-251']['prerequisites']
    assert 'Only one' in r['gender-and-stem-studies-immersion']['summary']
    assert 'relevant' in r['gender-art-and-media-immersion']['summary']
    assert '300' in r['queer-and-transgender-studies-immersion-group-1']['summary']
    assert r['queer-and-transgender-studies-immersion-group-0']['kind']=='all'
    assert r['womens-and-gender-studies-immersion']['credits'] is None
    assert r['womens-and-gender-studies-immersion-group-0']['credits']==9
    assert c['WGST-380']['name']=='Gender and Political Thought'
    assert c['WGST-399']['category_review']['status']=='unclassified'
    assert d['curriculum_status']=='partial'


def test_rules_only_observer_does_not_duplicate_or_manufacture_course_metadata():
    o=parse_rules(fixture(),title="Biology: Ecology and Evolution Immersion")
    assert o["courses"]==[] and o["requirements"]==[]
    assert o["observed_catalog_year"]=="2026-2027" and "curriculum_audit" not in o
