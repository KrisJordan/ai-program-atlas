import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.miami_policies import SPECS,parse_policy
ROOT=Path(__file__).resolve().parents[1]
PIDS=[p.stem for p in (ROOT/'data/programs').glob('*miami*')]

@pytest.mark.parametrize('code',SPECS)
def test_observations_depend_on_real_policy_body(code):
    _,title,headings=SPECS[code]
    body=''.join('<h2>'+h+'</h2><p>Reviewed policy content has a minimum nine credits and requires department approval.</p>' for h in headings)
    if not headings:body='<p>The applicable undergraduate policy requires department approval and at least nine credits in this synthetic fixture.</p>'
    html='<h1>'+title+'</h1><div id="content">'+body+'</div>'
    old=parse_policy(html,pid='miami-test',code=code)
    new=parse_policy(html.replace('nine credits','twelve credits'),pid='miami-test',code=code)
    assert old['observed_policy_sections']!=new['observed_policy_sections']
    assert old['courses']==old['requirements']==[] and old['curriculum_status']=='partial'
    assert not {'last_verified','curriculum_audit','catalog_year'} & old.keys()
    with pytest.raises(ValueError,match='identity'):parse_policy(html.replace('<h1>'+title,'<h1>Other identity'),pid='miami-test',code=code)
    if headings:
        with pytest.raises(ValueError,match='section'):parse_policy(html.replace('<h2>'+headings[0],'<h2>Other section'),pid='miami-test',code=code)

@pytest.mark.parametrize('pid',PIDS)
def test_scoped_sources_units_and_conflicts(pid):
    from atlas.db import validate_program
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
    spec=importlib.util.spec_from_file_location(pid,ROOT/'atlas/adapters'/pid/'adapter.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    codes=['transfer','grades','courses']+(['business'] if 'business' in pid else ['arts'])
    if d['program_kind']=='degree':codes+=['graduation','general','writing','undergraduate']
    assert all(SPECS[k][0] in module.SOURCE_PARSERS and SPECS[k][0] in module.SOURCES for k in codes)
    assert d['curriculum_status']=='partial'
    assert any('inconsistent summer' in x for x in d['curriculum_audit']['unresolved_requirements'])
    assert all(x['credit_unit']=='semester_hours' for x in d['courses']+d['requirements'] if x['credits'] is not None)
    assert any('second grade' in r['summary'] and 'lower' in r['summary'] for r in d['requirements'])
    if d['program_kind']=='minor':
        assert not any(r['title']=='University graduation minimum and residence' for r in d['requirements'])
    if pid=='miami-data-science-ai-bs':
        assert any('nine-credit' in x for x in d['curriculum_audit']['unresolved_requirements'])
        assert d['status']=='unknown'

@pytest.mark.parametrize('code',SPECS)
def test_optional_fetched_policy_pages(code):
    url=SPECS[code][0];key='undergraduate' if code=='undergraduate' else url.rstrip('/').split('/')[-1]
    path=Path('/tmp/miami-policies')/(key+'.html')
    if not path.exists():pytest.skip('Optional public source cache not present')
    assert parse_policy(path.read_text(),pid='miami-test',code=code)['observed_policy_sections']
