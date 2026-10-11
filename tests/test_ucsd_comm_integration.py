import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsd_comm_reviews as m
from atlas.curriculum_profile import requirement_profile


def test_comm_keeps_held_titles_and_explicit_none_distinct_from_unknown():
    d=json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text());cs={c['code']:c for c in d['courses']}
    assert cs['COMM 102D']['prerequisites']=='none.'
    assert cs['COMM 102D']['credits']==6
    assert cs['COMM 102C']['name']=='MMPP: Media and the Design of Social Learning NOTE: Course crosslisting with HDP 115 ended Summer 2015'
    assert cs['COMM 102C']['category_review']['status']=='unclassified'
    assert cs['COMM 120P']['category_review']['status']=='unclassified'
    assert cs['COMM 120P']['name']=='Digital Media Pedagogy'
    assert cs['COMM 124A']['category_review']['status']=='mixed'
    assert cs['COMM 194']['category_review']['status']=='unclassified'
    assert cs['COMM 194']['credits']==4
    assert [requirement_profile(d)[k]['count']for k in ['required','options','unresolved']]==[8,119,2241]


def test_comm_registered_current_source_replays_only_approved_observations():
    s=m.SPEC['sources']['COMM'];p=Path(s['cache_path'])
    if not p.exists():pytest.skip('Optional current Communication chapter')
    a=importlib.import_module('atlas.adapters.'+m.SPEC['program_id']+'.adapter');out=a.SOURCE_PARSERS[s['url']](p.read_text())
    assert len(out['courses'])==39 and len(out['source_dispositions'])==6
    cs={c['id']:c for c in json.loads(Path('data/programs',m.SPEC['program_id']+'.json').read_text())['courses']}
    assert all(cs[c['id']][key]==v for c in out['courses']for key,v in c.items()if key!='notes')
