import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.rit_policies import SPECS,parse_policy
ROOT=Path(__file__).resolve().parents[1]
PIDS=['rochester-institute-of-technology-artificial-intelligence-minor-minor','rit-ai-society-minor','rochester-institute-of-technology-artificial-intelligence-bs-degree']

@pytest.mark.parametrize('code',SPECS)
def test_policy_source_and_section_changes_are_observed(code):
    html=(ROOT/'tests/fixtures/rit_policies'/f'{code}.html').read_text()
    old=parse_policy(html,pid=PIDS[0],code=code)
    new=parse_policy(html.replace('Minimum nine','Minimum twelve'),pid=PIDS[0],code=code)
    assert old['observed_policy_sections']!=new['observed_policy_sections']
    assert old['curriculum_status']=='partial' and old['requirements']==[]
    assert not {'curriculum_audit','last_verified'} & old.keys()
    with pytest.raises(ValueError):parse_policy(html.replace(SPECS[code][0],'Other policy'),pid=PIDS[0],code=code)
    with pytest.raises(ValueError):parse_policy(html.replace('<h2>','<h3>').replace('</h2>','</h3>'),pid=PIDS[0],code=code)

@pytest.mark.parametrize('pid',PIDS)
def test_registered_sources_and_scoped_audits(pid):
    spec=importlib.util.spec_from_file_location('rit',ROOT/'atlas/adapters'/pid/'adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    from atlas.db import validate_program
    validate_program(d)
    for code in (['d011','d020','d050','d120'] if d['program_kind']=='minor' else ['d020','d050','d120','d015']):
        url='https://www.rit.edu/policies/'+code
        assert url in adapter.SOURCES and url in adapter.SOURCE_PARSERS
    if d['program_kind']=='minor':
        assert d['curriculum_status']=='complete' and d['curriculum_audit']['unresolved_requirements']==[]
        assert any('nine' in r['summary'] and 'X-graded' in r['summary'] for r in d['requirements'])
        assert any('Pass/No Pass' in r['summary'] and 'minor' in r['summary'] for r in d['requirements'])
    else:
        assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
        assert all(c['credit_unit']=='semester_hours' for c in d['courses'] if c['credits'] is not None)
        assert any('25 percent' in r['summary'] for r in d['requirements'])
