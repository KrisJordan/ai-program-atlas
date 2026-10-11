"""Independently enumerated science roles and consequential source conditions."""
import importlib.util
import json
from pathlib import Path
from atlas.adapters.rit_writing_closure import PID
from atlas.db import validate_program
from atlas.curriculum_profile import requirement_profile


def test_science_preparation_is_context_and_local_core_is_optional():
    d=json.loads(Path('data/programs/'+PID+'.json').read_text());validate_program(d)
    r={x['id'].removeprefix(PID+'-'):x for x in d['requirements']}
    c={x['code']:x for x in d['courses']}
    assert r['chemistry-preparation']['kind']=='note'
    assert set(r['chemistry-preparation']['course_ids'])=={PID+'-'+x.lower() for x in ['CHMG-131','CHMG-141','CHMG-142','CHMG-145','CHMG-146']}
    assert 'complete CHMG-141+145+142+146 sequence' in r['chemistry-preparation']['summary']
    assert 'OR CHMG-131' in r['chemistry-preparation']['summary']
    for route in ['cellular-biology','physics','astronomy','chemistry']:
        assert r[route+'-immersion']['parent_id']==PID+'-immersion-observed-routes'
    assert r['cellular-biology-electives']['count']==2 and r['cellular-biology-electives']['credits'] is None
    assert r['physics-electives']['count']==2 and r['physics-electives']['credits'] is None
    assert c['BIOL-216']['credits']==1 and c['BIOL-427']['credits']==4
    assert c['PHYS-330']['credits']==4 and c['PHYS-411']['credits']==4
    assert c['PHYS-320']['category']=='mathematics'
    assert 'PHYS-IM' in c['PHYS-315']['prerequisites']
    assert c['CHMG-131']['prerequisites'] is None
    assert 'CHMO-235' in c['CHMO-231']['prerequisites']
    assert PID+'-biol-575' not in r['cellular-biology-electives']['course_ids']
    assert PID+'-phys-251' not in r['physics-electives']['course_ids']
    p=requirement_profile(d)
    assert [p[k]['count'] for k in ['required','options','unresolved']]==[23,770,17]
    assert d['curriculum_status']=='partial'


def test_registered_science_sources_are_only_integrated_current_routes():
    path=Path('atlas/adapters')/PID/'adapter.py'
    spec=importlib.util.spec_from_file_location('rit_science_registration',path)
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    d=json.loads(Path('data/programs/'+PID+'.json').read_text())
    assert set(a.SOURCES)<={s['url'] for s in d['sources']}
    for slug in ['biology-cellular-and-molecular-immersion','physics-immersion','astronomy-immersion','chemistry-immersion']:
        assert 'https://www.rit.edu/study/'+slug in a.SOURCE_PARSERS
    assert 'https://www.rit.edu/study/climate-change-interdisciplinary-problem-immersion' in a.SOURCE_PARSERS
    assert 'https://www.rit.edu/study/biology-ecology-and-evolution-immersion' in a.SOURCE_PARSERS
