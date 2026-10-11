"""Local WPI selections are not extra electives or independent BS awards."""
import copy
import hashlib
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters import wpi_local_concentrations as local
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


def row(code):
    return f'<article class="node--type-class"><div class="col-3"><a href="/synthetic">{code}</a></div><div class="col-7">Synthetic title</div><span class="field--name-field-credits">1/3</span></article>'


def section(label, content):
    return '<div class="paragraph--type--degree-section"><div class="field--name-field-degree-section-description">'+label+'</div>'+content+'</div>'


def doc(key, content, extra=''):
    title, _ = local.identity('fixture', key)
    return '<main><article class="node--type-degree"><h1>'+title+'</h1><div class="field--name-field-degree-type"><div class="field__item">Concentration</div></div><div class="degree-class-details">Associated Degree <ul class="concentration-usage"><li>Artificial Intelligence Major</li></ul> 6 courses. '+extra+content+'</div></article></main>'


def test_fixed_courses_are_required_while_total_includes_them():
    html = doc('ece', section('Required (recommend to take first):', row('ECE 2010'))
               + section('Choose at least two foundational courses from:', row('ECE 2029')+row('ECE 2039'))
               + section('Choose remaining advanced courses from:', row('ECE 3012')))
    result = local.parse(html, 'test', 'ece')
    profile = requirement_profile(result)
    assert profile['required']['count'] == 1
    assert profile['options']['count'] == 3
    total = next(n for n in result['requirements'] if n['id']=='test-selection-total')
    assert total['count'] == 6 and 'including all fixed' in total['summary']
    assert total['credits'] is None
    assert 'curriculum_audit' not in result and 'last_verified' not in result
    changed = local.parse(html.replace('ECE 3012', 'ECE 3999'), 'test', 'ece')
    assert 'ECE 3999' in {c['code'] for c in changed['courses']}
    with pytest.raises(ValueError):
        local.parse(html.replace('>Concentration<', '>Certificate<'), 'test', 'ece')


def test_probability_bundle_is_choice_and_hidden_field_is_not_a_requirement():
    group = '<article class="node--type-elective-group">'+row('MA 2621')+row('MA 2631')+'</article>'
    subtotal = '<div class="hide-subtotal"><div class="degree-row-subtotal"><div class="col-2">1/3</div></div></div>'
    html = doc('optimization', section('Required Foundational Courses (must take both; 2/3 units):', group+row('MA 1024'))
               + section('Choose one course from:', row('MA 2073'))+subtotal,
               'beyond those taken to meet the core AI requirements')
    result = local.parse(html, 'test', 'optimization')
    assert requirement_profile(result)['required']['count'] == 1
    assert next(n for n in result['requirements'] if n['id'].endswith('required-alternative-0'))['count'] == 1
    assert any('not treated as a visible requirement' in n['summary'] for n in result['requirements'])
    with pytest.raises(ValueError):
        local.parse(html.replace('hide-subtotal','show-subtotal'), 'test', 'optimization')


def test_parent_requires_actual_mqp_overlap_and_adviser_clauses():
    html = '<main><h1>Artificial Intelligence Major</h1><div class="degree-class-details">one and only one concentration; 6 distinct courses; student\'s chosen concentration; sole advisor; co-advised; 10 units program requirements; at least 4/3 units</div></main>'
    result = local.parse_parent(html, 'test', 'ece')
    assert len(result['requirements']) == 3
    assert all(n['kind'] == 'note' for n in result['requirements'])
    assert 'not a second additional MQP' in result['requirements'][1]['summary']
    with pytest.raises(ValueError):
        local.parse_parent(html.replace('co-advised','advised'), 'test', 'ece')


@pytest.mark.parametrize('slug,key', local.KEYS.items())
def test_reviewed_local_seed_and_source_dispatch(slug, key):
    pid='wpi-ai-'+slug+'-concentration'
    program=json.loads(Path('data/programs',pid+'.json').read_text())
    validate_program(program)
    assert program['program_kind']=='concentration' and program['award_level']=='concentration'
    assert program['curriculum_status']==('partial' if key in local.GAPS else 'complete')
    assert bool(program['curriculum_audit']['unresolved_requirements'])==(key in local.GAPS)
    assert any(n['id'].endswith('-parent-mqp') for n in program['requirements'])
    assert any(n['id'].endswith('-policy-grading-credit') for n in program['requirements'])
    adapter=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    assert len(adapter.SOURCES)==(6 if key in ['experience','optimization'] else 5)
    assert set(adapter.SOURCES)==set(adapter.SOURCE_PARSERS)
    snapshot=copy.deepcopy(program)
    profile=requirement_profile(program)
    assert program==snapshot
    assert sum(profile[k]['count']for k in ['required','options','unresolved'])==len(program['courses'])
    expected={'environment':1,'ece':1,'biotechnology':3,'biochemistry':4,'optimization':1,'social-policy':2,'chemical':3}
    assert profile['required']['count']==expected.get(key,0)


@pytest.mark.parametrize('slug,key', local.KEYS.items())
def test_optional_inspected_source_snapshots_are_idempotent(slug,key):
    pid='wpi-ai-'+slug+'-concentration'
    adapter=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    for url,parse in adapter.SOURCE_PARSERS.items():
        path=Path('.cache/http',hashlib.sha256(url.encode()).hexdigest()+'.body')
        if not path.exists():pytest.skip('Optional ignored official-source cache unavailable')
        html=path.read_text()
        first=parse(html);second=parse(html)
        assert first==second
        assert 'curriculum_audit'not in first and 'last_verified'not in first


def test_linked_css_policy_requires_actual_hide_rule():
    css = '.hide-subtotal .degree-row-subtotal,.hide-subtotal .subtotal-row-wrapper{display:none !important}'
    assert local.parse_stylesheet(css, 'test')['requirements'][0]['kind']=='note'
    with pytest.raises(ValueError):
        local.parse_stylesheet(css.replace('display:none','display:block'), 'test')
