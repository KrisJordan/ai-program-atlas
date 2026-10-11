import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.rit_general_education import SPECS,parse_page
ROOT=Path(__file__).resolve().parents[1]
PID='rochester-institute-of-technology-artificial-intelligence-bs-degree'

@pytest.mark.parametrize('url',SPECS)
def test_source_body_and_identity_are_observed(url):
    title,headings=SPECS[url]
    html='<h1>'+title+'</h1><main>'+''.join('<h2>'+h+'</h2>' for h in headings)+'<p>'+'Published requirement body with nine credits and approval. '*4+'</p></main>'
    a=parse_page(html,pid=PID,url=url);b=parse_page(html.replace('nine','twelve'),pid=PID,url=url)
    assert a['observed_source_content_sha256']!=b['observed_source_content_sha256']
    assert a['requirements']==[] and a['curriculum_status']=='partial'
    assert not {'last_verified','first_offered','status','curriculum_audit'} & a.keys()
    with pytest.raises(ValueError,match='identity'):parse_page(html.replace('<h1>'+title,'<h1>Other source'),pid=PID,url=url)
    with pytest.raises(ValueError,match='body'):parse_page('<h1>'+title+'</h1>',pid=PID,url=url)


def test_curated_scope_separates_planned_start_from_verified_instruction():
    from atlas.db import validate_program
    d=json.loads((ROOT/'data/programs'/f'{PID}.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial' and d['status']=='announced'
    assert d['first_offered']['value']=='Fall 2026'
    assert 'not independently confirmed' in d['first_offered']['uncertainty']
    assert any('prohibits' in x and 'Immersion 3' in x for x in d['curriculum_audit']['unresolved_requirements'])
    assert any('robots' in x for x in d['curriculum_audit']['unresolved_requirements'])
    assert any(r['title']=='BS general education distribution' and r['credits']==60 and 'not 60 additional' in r['summary'] for r in d['requirements'])
    assert any('Club and intramural' in r['summary'] for r in d['requirements'])
    assert all(o['statement_type']=='program_aim' for o in d['outcomes'] if o['source_id']=='rit-ai-bs-launch')
    spec=importlib.util.spec_from_file_location(PID,ROOT/'atlas/adapters'/PID/'adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert all(u in m.SOURCES and u in m.SOURCE_PARSERS for u in SPECS)

@pytest.mark.parametrize('url',SPECS)
def test_optional_public_source_cache(url):
    p=Path('/tmp/rit-general')/(url.rstrip('/').split('/')[-1]+'.html')
    if not p.exists():pytest.skip('Optional public source cache unavailable')
    assert parse_page(p.read_text(),pid=PID,url=url)['observed_source_content_sha256']
