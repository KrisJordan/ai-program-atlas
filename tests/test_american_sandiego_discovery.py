"""Authored structural/changed-rule fixtures, not archived university pages."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.american_sandiego_concentrations import parse_american, parse_sandiego
from atlas.db import validate_program
from atlas.requirements import validate_requirements

ROOT = Path(__file__).parents[1]
PIDS = ['american-cs-bs-ai-concentration', 'san-diego-cs-ba-data-science-ai-concentration', 'san-diego-cs-bs-data-science-ai-concentration']


def american_fixture(credits=12, grade='C'):
    courses = ''.join(f'<a class="acalog-program-core-course-link" href="https://catalog.american.edu/course/{i}">CSC-{i} Example topic {i} (3)</a>' for i in range(400, 405))
    return '<h1 class="acalog-program-name">Computer Science (BS)</h1>'+f'<div class="acalog-program-core"><h3>Concentration ({credits} credit hours)</h3><div class="acalog-program-cores"><div class="acalog-program-core"><h4>Artificial Intelligence</h4><div class="acalog-program-core-description">Complete {credits} credit hours from the following if not taken to fulfill Breadth of Knowledge:</div>{courses}</div></div></div>'+''.join(f'<div class="acalog-program-core"><h2 class="acalog-program-core-name">{label}</h2><div class="acalog-program-core-description">{value}</div></div>' for label,value in [('Admission to the Program','Departmental approval and GPA 2.00.'),('Major Requirements',f'Courses require {grade} or better.')])


def usd_fixture(award='BA', option_units=3, code='GENG 430'):
    rows = [('Concentration in Data Science and Artificial Intelligence',''),('COMP 351','Example AI','3'),('COMP 352','Example Data Science','3'),('One of the following courses:',str(option_units)),('COMP 333','Example human-centered data',''),(code,'Example bioinformatics',''),('Total Units',str(6+option_units))]
    table = '<table>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in r)+'</tr>' for r in rows)+'</table>'
    return '<header><h1>University of San Diego</h1></header><main><h1>Computer Science '+award+'</h1><h3>Concentrations in Computer Science (9 - 9.5 units)</h3><p>Courses taken toward a concentration may also apply to the major. Concentrations are optional. Cyber security approval is separate.</p>'+table+'</main>'


def test_american_changed_rule_and_policy_observed_without_certification():
    old = parse_american(american_fixture(), 'p', 's', 'https://example.edu')
    new = parse_american(american_fixture(15,'B'), 'p', 's', 'https://example.edu')
    validate_requirements(new)
    choice = new['requirements'][1]
    assert choice['kind']=='note' and choice['credits']==15
    assert len(choice['course_ids'])==5 and 'Breadth of Knowledge' in choice['summary']
    assert 'B or better' in new['requirements'][-1]['summary']
    assert old['observed_policy_digest'] != new['observed_policy_digest']
    assert new['curriculum_status']=='partial' and 'curriculum_audit' not in new and 'last_verified' not in new
    assert all(c['credit_unit']=='unknown' and c['prerequisites'] is None for c in new['courses'])


@pytest.mark.parametrize('change', [lambda h:h.replace('Computer Science (BS)','Computer Science (BA)'), lambda h:h.replace('Concentration (12 credit hours)','Electives (12 credit hours)'), lambda h:h.replace('if not taken to fulfill Breadth of Knowledge:','without restrictions:'), lambda h:h.replace('Admission to the Program','Other policy')])
def test_american_rejects_wrong_award_elective_bucket_or_missing_rule(change):
    with pytest.raises(ValueError): parse_american(change(american_fixture()),'p','s','u')


def test_usd_preserves_concrete_award_choice_and_unknown_course_units():
    p = parse_sandiego(usd_fixture(),'p','s','u','BA')
    q = parse_sandiego(usd_fixture(option_units=4),'p','s','u','BA')
    validate_requirements(p)
    assert p['requirements'][1]['kind']=='all' and len(p['requirements'][1]['course_ids'])==2
    assert p['requirements'][2]['kind']=='choose_courses' and p['requirements'][2]['count']==1
    assert q['requirements'][2]['credits']==4 and q['requirements'][0]['credits']==10
    assert p['observed_policy_digest']!=q['observed_policy_digest']
    assert 'BA' in p['requirements'][0]['title']
    assert p['courses'][-1]['code']=='GENG 430' and p['courses'][-1]['credits'] is None
    assert all(c['prerequisites'] is None for c in p['courses'])
    assert 'curriculum_audit' not in p


@pytest.mark.parametrize('change', [lambda h:h.replace('Computer Science BA','Computer Science BS'), lambda h:h.replace('Concentrations are optional','Concentrations are mandatory'), lambda h:h.replace('Total Units','Other Units'), lambda h:h.replace('<td>9</td>','<td>12</td>'), lambda h:h.replace('One of the following courses:','Two of the following courses:')])
def test_usd_rejects_incompatible_identity_structure_and_total(change):
    with pytest.raises(ValueError): parse_sandiego(change(usd_fixture()),'p','s','u','BA')


@pytest.mark.parametrize('pid', PIDS)
def test_curated_new_records_and_adapter_sources(pid):
    p=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    validate_program(p)
    a=importlib.import_module('atlas.adapters.'+pid+'.adapter')
    assert a.SOURCES[0]==p['sources'][0]['url']
    assert p['program_kind']=='concentration' and p['curriculum_status']=='partial'
    assert p['first_offered'] is None and p['catalog_year']=='2026-2027'
    assert p['curriculum_audit']['unresolved_requirements'] and p['curriculum_audit']['metadata_gaps']
    assert not p['outcomes']
    with pytest.raises(ValueError): a.parse('<div id="app">Loading catalog</div>')
    if pid.startswith('american'):
        assert len(p['courses'])==7 and p['requirements'][1]['credits']==12
    else:
        assert len(p['courses'])==6 and p['requirements'][0]['credits']==9
        assert 'GENG 430' in ' '.join(p['curriculum_audit']['unresolved_requirements'])
        assert not any(c['code']=='COMP 430' for c in p['courses'])
        assert sum(c['credits'] is None for c in p['courses'])==4


def test_five_institution_depth_ledger_and_discoveries():
    ledger=json.loads((ROOT/'data/surveys/national-five-depth-2026-10-11.json').read_text())
    assert {r['institution_id'] for r in ledger}=={'american-university','creighton-university','fordham-university','university-of-san-diego','rutgers-university-camden'}
    assert {p['program_id'] for r in ledger for p in r['discoveries']}==set(PIDS)
    assert all(r['status']=='inspected' and r['remaining_work'] and r['sources'] for r in ledger)
    rutgers=next(r for r in ledger if r['institution_id']=='rutgers-university-camden')
    assert rutgers['discoveries']==[] and any('certificate' in s.lower() for s in rutgers['nonqualifying_observations'])
    assert not any(r.get('absence_claim') for r in ledger)
