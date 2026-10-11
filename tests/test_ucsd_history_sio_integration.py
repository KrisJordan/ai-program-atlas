import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_hila_reviews as hila, ucsd_sio_reviews as sio, ucsd_eds_reviews as eds, ucsd_cgs_reviews as cgs, ucsd_mus_reviews as mus
from atlas.curriculum_profile import requirement_profile

PID=hila.SPEC['program_id']

def test_history_sio_integration_preserves_held_identity_and_roles():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['HILA 119']['credits'] is None
    assert 'EASY' in ' '.join(cs['HILA 167']['notes'])
    assert cs['HIUS 120']['name']=='Race and Oral History in San Diego (cross-listed with ETHN 120) (4 or 6)'
    assert cs['HIUS 120']['category_review']['status']=='unclassified'
    assert cs['HIUS 120D']['category_review']['status']=='mixed'
    assert 'strongly recommended' in ' '.join(cs['HIUS 120D']['notes'])
    for code in ['SIO 105','SIO 113']:
        assert cs[code]['category_review']['status']=='unclassified'
        assert cs[code]['category']=='other'
    assert cs['SIO 105']['name']=='Conservation Solutions'
    assert cs['SIO 194']['credits']==4
    assert 'six-to-eight-unit' in ' '.join(cs['SIO 194']['notes'])
    assert cs['SIO 109']['category_review']['status']=='mixed'
    assert cs['POLI 117']['category_review']['status']=='unclassified'
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2241]

@pytest.mark.parametrize('module,subject,count,dispositions',[(hila,'HILA',187,13),(sio,'SIO',35,6),(eds,'EDS',31,1),(cgs,'CGS',24,0),(mus,'MUS',27,6)])
def test_composed_source_replays_approved_metadata_only(module,subject,count,dispositions):
    s=module.SPEC['sources'][subject];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional ignored official chapter capture')
    a=importlib.import_module('atlas.adapters.'+PID+'.adapter')
    assert a.SOURCES.count(s['url'])==1
    r=a.SOURCE_PARSERS[s['url']](p.read_text())
    assert len(r['courses'])==count and len(r['source_dispositions'])==dispositions
    assert len({c['id']for c in r['courses']})==count
    saved={c['id']:c for c in json.loads(Path('data/programs',PID+'.json').read_text())['courses']}
    for c in r['courses']:
        assert 'category_review'not in c
        assert all(saved[c['id']][k]==v for k,v in c.items()if k!='notes')
        assert set(c['notes'])<=set(saved[c['id']]['notes'])


def test_music_study_and_cultural_ai_remain_conditional_content():
    d=json.loads(Path('data/programs',PID+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['CGS 108']['category']=='human_context'
    assert cs['MUS 132R']['name']=='Recital Preparation'
    assert 'audition' in cs['MUS 132R']['prerequisites']
    assert cs['MUS 199']['credits']is None
    assert cs['MUS 160B']['category_review']['status']=='unclassified'
    assert 'music and ICAM majors only' in cs['MUS 160B']['prerequisites']
    assert any('Two production-course limitation' in n for n in cs['MUS 160B']['notes'])
    for code in ['MUS 8GS','MUS 19R','MUS 20R','MUS 126R','MUS 150GS','MUS 13AS']:
        assert cs[code]['category_review']['status']=='unclassified'
