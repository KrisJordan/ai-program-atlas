"""General policy evidence must not certify inaccessible W&M curricula."""
import json
from pathlib import Path
import pytest
from atlas.adapters.william_mary_public_policies import parse_advising, parse_reviewed_declaration_text
from atlas.db import validate_program
ROOT=Path(__file__).resolve().parents[1]

def test_advising_observation_scopes_and_detects_changes():
    html='<main><h1>Academic Forms &amp; Processes</h1><h2>Form Categories</h2><p>'+('Synthetic committee description. '*5)+'</p><h2>Registrar Forms</h2><p>'+('Synthetic major and minor declaration procedure. '*5)+'</p><h2>Unrelated</h2><p>Extra</p></main>'
    a=parse_advising(html,'test')
    assert a==parse_advising(html.replace('Extra','New extra'),'test')
    assert a!=parse_advising(html.replace('Synthetic committee','Updated committee'),'test')
    assert a['requirements']==[] and 'curriculum_audit' not in a
    with pytest.raises(ValueError):parse_advising(html.replace('Registrar Forms','Other'),'test')

@pytest.mark.parametrize('minor',[True,False])
def test_pdf_text_is_manual_observation_not_curated_policy(minor):
    marker='DECLARATION OF ACADEMIC MINOR Signature of Department Chair or Program Director' if minor else 'DECLARATION/CHANGE OF MAJOR To Declare a Major SINGLE VS. DOUBLE MAJORS'
    text=marker+' Synthetic form policy sentence.'*20
    a=parse_reviewed_declaration_text(text,'test',minor=minor)
    assert a['requirements']==[] and 'curriculum_audit' not in a
    assert a!=parse_reviewed_declaration_text(text+' Changed residency.','test',minor=minor)
    with pytest.raises(ValueError):parse_reviewed_declaration_text(b'%PDF-1.4','test',minor=minor)
    with pytest.raises(ValueError):parse_reviewed_declaration_text('Unrelated policy '*50,'test',minor=minor)

@pytest.mark.parametrize('pid',['william-mary-ai-minor','william-mary-cs-ai-ml-concentration','william-mary-data-science-ai-specialization','william-mary-applied-ai-ba'])
def test_catalog_barrier_and_source_conditions_stay_visible(pid):
    d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
    assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
    src=next(s for s in d['sources'] if s['id'].startswith('wm-registrar-'))
    assert src['source_date'] is None and 'revision' in src['locator']
    if d['program_kind']=='minor':
        by={r['id']:r for r in d['requirements']}
        assert 'unless' in by[pid+'-residence']['summary']
        assert 'two majors may not' in by[pid+'-major-relationship']['summary']
        assert '2.00' in by[pid+'-grades']['summary']
    else:
        assert 'in-progress credits do not count' in next(r for r in d['requirements'] if r['id'].endswith('-earned-credits'))['summary']
        assert not any('Self-Designed' in r['summary'] for r in d['requirements'])
