import importlib.util,json
from pathlib import Path
import pytest
from atlas.adapters.stevens_public_policies import parse_policy,TABS
ROOT=Path(__file__).resolve().parents[1]

def load(pid):
    spec=importlib.util.spec_from_file_location('adapter',ROOT/'atlas/adapters'/pid/'adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

@pytest.mark.parametrize('tab',TABS)
def test_stevens_rendered_tab_identity_and_change(tab):
    title,anchor=TABS[tab]
    html=f'<h1>Catalog</h1><article><h1>{title}</h1><p>{anchor}. Synthetic policy text for structural checks.</p></article>'
    x=parse_policy(html,pid='test',tab=tab)
    y=parse_policy(html.replace('Synthetic','Changed'),pid='test',tab=tab)
    assert x['observed_policy_digest']!=y['observed_policy_digest']
    assert x['requirements']==[] and x['curriculum_status']=='partial'
    with pytest.raises(ValueError):parse_policy('<article><h1>Undergraduate Requirements and Procedures</h1></article>',pid='test',tab=tab)


def test_ursinus_exact_crosslist_observation_and_change():
    a=load('ursinus-ai-minor')
    html='<h1>Mathematics, Computer Science and Statistics Courses</h1><p class="course-number-name"><strong>CS/MUS-372. Digital Musical Audio Processing</strong></p><p class="course-text">Synthetic description. Prerequisite: MATH-106 or 111 or higher and CS-174 (or CS-173 with permission of the instructor). Three hours per week. Four semester hours.</p>'
    x=a.parse_audio_course(html);c=x['courses'][0]
    assert c['code']=='CS-372' and c['id']=='ursinus-cs-372' and c['credits']==4
    assert 'permission' in c['prerequisites'] and c['description'] is None
    y=a.parse_audio_course(html.replace('Four semester hours','Three semester hours').replace('CS-174','CS-175'))
    assert y['courses'][0]['credits']==3 and 'CS-175' in y['courses'][0]['prerequisites']
    assert y['observed_course_digest']!=x['observed_course_digest']
    with pytest.raises(ValueError):a.parse_audio_course(html.replace('CS/MUS-372','CS/MUS-373'))


def test_reviewed_conflicts_and_no_completion_promotion():
    from atlas.db import validate_program
    for pid in ['ursinus-ai-minor','stevens-institute-of-technology-artificial-intelligence-minor-minor','stevens-institute-of-technology-artificial-intelligence-bs-degree']:
        d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
        assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
    d=json.loads((ROOT/'data/programs/stevens-institute-of-technology-artificial-intelligence-bs-degree.json').read_text())
    assert d['catalog_year']=='2026-2027'
    assert any('School of Computing' in gap for gap in d['curriculum_audit']['unresolved_requirements'])
    assert any('1.75' in r['summary'] and '50 percent' in r['summary'] for r in d['requirements'])
