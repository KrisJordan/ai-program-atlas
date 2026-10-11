import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_phil_econ_reviews as m
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program

PID=m.SPEC['program_id']


def test_integrated_metadata_preserves_roles_and_source_conflict():
    d=json.loads(Path('data/programs',PID+'.json').read_text());validate_program(d)
    c={x['code']:x for x in d['courses']};profile=requirement_profile(d)
    assert [profile[k]['count']for k in ['required','options','unresolved']]==[8,119,2240]
    assert c['PHIL 12']['category']=='mathematics'
    assert c['PHIL 123']['category']=='human_context'
    assert c['ECON 165T']['credits']==2
    assert c['ECON 185']['name']=='Educational Equity and Development Across the Lifespan'
    assert c['ECON 185']['category_review']['status']=='unclassified'
    assert 'and MATH 181B' in c['ECON 185']['prerequisites']
    assert any('current catalog title is Detecting Discrimination' in n for n in d['notes'])
    assert all(c[x]['category_review']['status']=='unclassified'for x in ['ECON 163','PHIL 28GS'])
    assert 'philosophy majors' in c['PHIL 115']['prerequisites'].lower()
    assert any('PHIL 185' in n and 'repeat' in n.lower()for n in d['notes'])


def test_current_source_observers_registered_without_manual_review_replay():
    adapter=importlib.import_module('atlas.adapters.'+PID+'.adapter')
    d=json.loads(Path('data/programs',PID+'.json').read_text());courses={c['id']:c for c in d['courses']}
    for subject,source in m.SPEC['sources'].items():
        assert source['url']in adapter.SOURCES
        cache=Path(source['cache_path'])
        if not cache.exists():pytest.skip('Optional ignored current course chapter')
        result=adapter.SOURCE_PARSERS[source['url']](cache.read_text())
        assert all('category_review'not in c for c in result['courses'])
        for c in result['courses']:
            assert all(courses[c['id']][k]==v for k,v in c.items()if k!='notes')
        assert all(c['code']!='ECON 185'for c in result['courses'])
