import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_anar_reviews as m


def test_anar_preserves_topic_conditions_and_distinct_repeat_routes():
    d=json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['ANAR 117']['credits']==8 and cs['ANAR 135']['credits']==8
    assert cs['ANAR 100']['category_review']['status']=='unclassified'
    assert any('Latin American' in n and 'unresolved' in n for n in cs['ANAR 100']['notes'])
    assert cs['ANAR 155']['credits']==cs['ANAR 155S']['credits']==4
    assert cs['ANAR 155']['prerequisites']!=cs['ANAR 155S']['prerequisites']
    assert cs['ANAR 155']['category_review']['status']=='mixed'
    assert cs['ANAR 155S']['category']=='human_context'
    assert 'ANTH 3' not in cs['ANAR 182']['prerequisites']
    assert cs['ANAR 135S']['category_review']['status']=='unclassified'


def test_shared_anthropology_url_composes_prior_records_without_overwrite():
    s=m.SPEC['sources']['ANAR'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional cached Anthropology source')
    a=importlib.import_module('atlas.adapters.'+m.SPEC['program_id']+'.adapter')
    assert a.SOURCES.count(s['url'])==1
    out=a.SOURCE_PARSERS[s['url']](p.read_text())
    assert len(out['courses'])==115 and len({c['id']for c in out['courses']})==115
    assert {'ANAR 117','ANSC 138','ANTH 128A'}<={c['code']for c in out['courses']}
    d=json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text());cs={c['id']:c for c in d['courses']}
    assert all(cs[c['id']][k]==v for c in out['courses']for k,v in c.items()if k!='notes')
