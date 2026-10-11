"""Authored public-policy structure and changed-rule fixtures; no raw source archive."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.american_sandiego_policies import (
    AU_SECTIONS, USD_TABS, parse_american_regulations,
    parse_american_declaration, parse_usd_policy,
)
from atlas.db import validate_program

ROOT = Path(__file__).parents[1]
PIDS = ['american-cs-bs-ai-concentration', 'san-diego-cs-ba-data-science-ai-concentration', 'san-diego-cs-bs-data-science-ai-concentration']


def au_fixture(residence=18):
    texts = {name: 'A published condition applies.' for name in AU_SECTIONS}
    texts[AU_SECTIONS[0]] = 'A credit hour measures work over a fifteen-week semester.'
    texts['9.1. Minimum Requirements for Majors'] = f'9.1.1.e. At least {residence} credits in-residence; no elected Pass/Fail.'
    return '<h2>Undergraduate Academic Rules and Regulations</h2>'+''.join(f'<h3>{h}</h3><p>{v}</p>' for h,v in texts.items())


def usd_fixture(kind, value=None):
    page,label=USD_TABS[kind]
    panels={
        'credit': '<h2>Standard Undergraduate Courses</h2><p>One unit of credit measures work over one semester.</p>',
        'school': '<h2>Special Restrictions on the Use of the Pass/Fail Option</h2><p>No major-required electives.</p><h2>Residency Requirement</h2><p>Computer Science degrees require 15 units; Engineering programs require 24 units.</p>',
        'grading': '<h2>Transfer of Credit</h2><p>C- or better; major or minor approval; 18 units after enrollment; Covid exception.</p><h2>Pass/Fail Option</h2><p>No major preparation.</p><h2>Duplication of Credit</h2><p>No duplicate learning.</p>',
        'overlap': '<h2>Majors</h2><p>Department restrictions apply to sharing.</p><h2>Minors</h2><p>No major credit sharing.</p>',
        'declaration': '<p>Declare after April 15 using appropriate processes.</p>',
        'residence': f'<p>The final {value or 30} semester units are resident unless the dean waives.</p>',
        'major-grades': '<p>GPA 2.0 in upper-division courses in the major; C– or better in at least 24 units.</p><p>Unrelated degree course inventory.</p>',
    }
    return f'<main><h1>{page}</h1><button role="tab" aria-selected="true">{label}</button><section role="tabpanel">{panels[kind]}</section></main>'


def test_au_changed_policy_observed_and_credit_definition_explicit():
    old=parse_american_regulations(au_fixture(),'p','s')
    new=parse_american_regulations(au_fixture(21),'p','s')
    assert old['observed_credit_unit']=='semester_hours'
    assert old['observed_policy_digest'] != new['observed_policy_digest']
    assert '21 credits' in ' '.join(r['summary'] for r in new['requirements'])
    assert new['curriculum_status']=='partial' and 'curriculum_audit' not in new
    with pytest.raises(ValueError): parse_american_regulations(au_fixture().replace('fifteen-week semester','term'),'p','s')
    with pytest.raises(ValueError): parse_american_regulations(au_fixture().replace('9.1. Minimum Requirements for Majors','Other'),'p','s')


def test_cas_second_major_does_not_consume_dual_degree_clause():
    fixture='<h1>Declaring a Major, Minor, or Certificate</h1><p>After one semester with GPA 2.0, a student may declare.</p><h2>First Major</h2><ul><li>AU GPA 2.0</li></ul><h2>Second Major</h2><ul><li>AU GPA 2.0; first/primary major declared</li></ul><h2>Dual Degree</h2><p>24 unique credits.</p>'
    p=parse_american_declaration(fixture,'p','s')
    q=parse_american_declaration(fixture.replace('GPA 2.0','GPA 2.5'),'p','s')
    assert not any('24 unique' in r['summary'] for r in p['requirements'])
    assert q['observed_policy_digest']!=p['observed_policy_digest']


@pytest.mark.parametrize('kind',USD_TABS)
def test_usd_active_tab_parser_and_shell_guard(kind):
    p=parse_usd_policy(usd_fixture(kind),'p','s',kind)
    assert p['requirements'] and p['curriculum_status']=='partial'
    assert 'curriculum_audit' not in p and 'last_verified' not in p
    for html in ['<div>Loading</div>',usd_fixture(kind).replace('aria-selected="true"','aria-selected="false"')]:
        with pytest.raises(ValueError):parse_usd_policy(html,'p','s',kind)


def test_usd_changes_observed_without_normalizing_distinct_residence_or_grade_rules():
    a=parse_usd_policy(usd_fixture('residence'),'p','s','residence')
    b=parse_usd_policy(usd_fixture('residence',36),'p','s','residence')
    assert a['observed_policy_digest']!=b['observed_policy_digest']
    assert '36 semester units' in b['requirements'][0]['summary']
    school=parse_usd_policy(usd_fixture('school'),'p','s','school')
    assert '15 units; Engineering programs require 24 units' in school['requirements'][1]['summary']
    grade=parse_usd_policy(usd_fixture('major-grades'),'p','s','major-grades')
    assert 'at least 24 units' in grade['requirements'][0]['summary']
    assert 'Unrelated' not in grade['requirements'][0]['summary']
    with pytest.raises(ValueError,match='review required'):
        parse_usd_policy(usd_fixture('grading').replace('18 units','24 units'),'p','s','grading')
    assert parse_usd_policy(usd_fixture('credit'),'p','s','credit')['observed_credit_unit']=='semester_hours'


@pytest.mark.parametrize('pid',PIDS)
def test_curated_cross_source_units_policy_scope_and_remaining_conflicts(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    validate_program(p)
    assert len(p['requirements'])==14
    assert p['catalog_year']=='2026-2027' and p['first_offered'] is None
    assert all(c['credit_unit']=='semester_hours' for c in p['courses'])
    adapter=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    urls={s['url'] for s in p['sources']}
    assert set(adapter.SOURCE_PARSERS)<=urls
    assert len(adapter.SOURCE_PARSERS)==(2 if pid.startswith('american') else 7)
    if pid.startswith('american'):
        assert p['requirements'][1]['kind']=='choose_credits'
        assert p['requirements'][1]['credits']==12
        assert '2.50' in ' '.join(p['curriculum_audit']['unresolved_requirements'])
    else:
        assert sum(c['credits'] is None for c in p['courses'])==4
        assert len(p['curriculum_audit']['unresolved_requirements'])==1
        assert 'GENG 430' in p['curriculum_audit']['unresolved_requirements'][0]
        assert not any(c['code']=='COMP 430' for c in p['courses'])
        assert all(r['kind']=='note' for r in p['requirements'][4:])
