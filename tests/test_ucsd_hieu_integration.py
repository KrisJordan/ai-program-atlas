import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hieu_reviews as m
from atlas.curriculum_profile import requirement_profile

PID=m.SPEC['program_id']


def test_hieu_preserves_title_hold_missing_units_and_conditional_study():
    d=json.loads(Path('data/programs',PID+'.json').read_text());c={x['code']:x for x in d['courses']}
    assert c['HIEU 124']['credits'] is None
    assert c['HIEU 198']['credits'] is None
    assert '2.95' in c['HIEU 198']['prerequisites']
    assert c['HIEU 122']['name']=='Ancient Greece from the Bronze Age to the Peloponnesian War'
    assert c['HIEU 122']['category_review']['status']=='unclassified'
    assert c['HIEU 124']['prerequisites'] is None
    assert any('not transferred' in n for n in c['HIEU 124']['notes'])
    assert c['HIEU 145']['category_review']['status']=='mixed'
    assert [requirement_profile(d)[k]['count']for k in ('required','options','unresolved')]==[8,119,2241]


def test_hieu_registered_bounded_history_observer_matches_curated_observations():
    s=m.SPEC['sources']['HIEU'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional official current history chapter')
    a=importlib.import_module('atlas.adapters.'+PID+'.adapter');r=a.SOURCE_PARSERS[s['url']](p.read_text())
    assert len(r['courses'])==265 and len(r['source_dispositions'])==20
    saved={c['id']:c for c in json.loads(Path('data/programs',PID+'.json').read_text())['courses']}
    for c in r['courses']:
        assert 'category_review'not in c
        assert all(saved[c['id']][k]==v for k,v in c.items()if k!='notes')
