import hashlib
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import miami_supplemental_policies as a
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]
PIDS=['miami-data-science-ai-bs','university-of-miami-data-science-and-artificial-intelligence-ba-degree','miami-ai-technologies-business-bsba','university-of-miami-artificial-intelligence-technologies-for-business-other-degree']

@pytest.mark.parametrize('key',['cognates','individualized'])
def test_source_changes_are_rejected(key,monkeypatch):
 html='<main><h1>'+a.TITLES[key]+'</h1><p>Synthetic reviewed policy</p></main>'
 monkeypatch.setitem(a.HASHES,key,hashlib.sha256(a.observed_text(html,key).encode()).hexdigest())
 obs=a.parse_source(html,pid='test',key=key)
 assert len(obs['requirements'])==1
 assert not {'curriculum_status','curriculum_audit','last_verified'} & obs.keys()
 for changed in [html.replace('Synthetic','Changed'),'<h1>Access denied</h1>']:
  with pytest.raises(ValueError):a.parse_source(changed,pid='test',key=key)


def test_heritage_courses_are_conditional_and_guarded(monkeypatch):
 html='<main><h1>Modern Languages and Literatures</h1><h2>Placement Guidelines for MLL Courses</h2><p>synthetic rules</p><h2>Advanced Writing and Communication Requirement</h2>'
 html+=''.join('<div class="courseblock">SPA '+n+'. Synthetic title '+n+'. 3 Credit Hours.</div>' for n in ['107','207','208','307'])+'</main>'
 monkeypatch.setitem(a.HASHES,'languages',hashlib.sha256(a.observed_text(html,'languages').encode()).hexdigest())
 d=a.parse_source(html,pid='test',key='languages')
 assert len(d['courses'])==4 and len(d['requirements'])==3
 assert all(r['kind']=='note' for r in d['requirements'])
 assert 'does not meet' in d['requirements'][1]['summary']
 assert next(c for c in d['courses'] if c['code']=='SPA 307')['prerequisites'].startswith('SPA 208')
 assert all(c['credits']==3 and c['credit_unit']=='semester_hours' for c in d['courses'])
 with pytest.raises(ValueError):a.parse_source(html.replace('3 Credit Hours','4 Credit Hours',1),pid='test',key='languages')
 with pytest.raises(ValueError):a.parse_source(html.replace('SPA 107','SPA 108'),pid='test',key='languages')

@pytest.mark.parametrize('pid',PIDS)
def test_seed_applicability_and_remaining_conflicts(pid):
 d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
 m=importlib.import_module('atlas.adapters.'+pid+'.adapter')
 assert a.COGNATES in m.SOURCE_PARSERS and a.INDIVIDUALIZED in m.SOURCE_PARSERS
 assert (a.LANGUAGES in m.SOURCE_PARSERS)==('data-science' in pid)
 assert d['curriculum_status']=='partial' and any('inconsistent summer' in x for x in d['curriculum_audit']['unresolved_requirements'])
 assert any('open route' in x for x in d['curriculum_audit']['unresolved_requirements'])
 assert len([c for c in d['courses'] if c['source_id']==a.SOURCE_IDS['languages']])==(4 if 'data-science' in pid else 0)

@pytest.mark.parametrize('key',['cognates','individualized','languages'])
def test_optional_public_cache(key):
 p=Path('/tmp/miami-supplement')/(key+'.html')
 if not p.exists():pytest.skip('Optional raw source cache is not committed')
 assert a.parse_source(p.read_text(),pid='test',key=key)['requirements']
