import importlib,json
from pathlib import Path
import pytest
from atlas.db import validate_program
adapter=importlib.import_module('atlas.adapters.umich-artificial-intelligence-minor.adapter')


def fixture():
    return '''<main><h1>New AI minor launches for students across disciplines</h1><p>In Winter 2026, University of Michigan Engineering established a new minor in artificial intelligence; skills to build custom AI solutions tailored to their disciplines.</p><p>Students majoring in engineering, information, music, pharmacy, business, art &amp; design, and architecture can currently enroll.</p><p>A sophomore in biomedical engineering who is pursuing the AI minor.</p></main>'''


def test_identity_is_distinct_and_dated_news_is_not_curriculum():
    d=adapter.parse(fixture())
    assert d['id']=='umich-artificial-intelligence-minor'
    assert d['program_kind']=='minor' and d['outcomes'][0]['statement_type']=='program_aim'
    assert 'dated news' in d['requirements'][0]['summary']
    assert not {'first_offered','last_verified','status','curriculum_status','curriculum_audit','courses'} & d.keys()
    for old,new in [('Winter 2026','Fall 2025'),('pharmacy','public policy'),('minor in artificial intelligence','AI course')]:
        with pytest.raises(ValueError):adapter.parse(fixture().replace(old,new))
    with pytest.raises(ValueError):adapter.parse('<h1>Access denied</h1>'+fixture())


def test_seed_keeps_unknown_first_instruction_and_requirement_inventory():
    root=Path(__file__).resolve().parents[1]
    d=json.loads((root/'data/programs/umich-artificial-intelligence-minor.json').read_text())
    validate_program(d)
    assert d['curriculum_status']=='pending' and d['courses']==[] and d['first_offered'] is None
    assert len(d['requirements'])==1 and d['requirements'][0]['kind']=='note'
    assert d['sources'][0]['source_date']=='2026-04-09'
    hcai=json.loads((root/'data/programs/university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor.json').read_text())
    assert hcai['id']!=d['id'] and hcai['title']!=d['title']
