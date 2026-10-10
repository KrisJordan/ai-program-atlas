import importlib.util
import json
from pathlib import Path
import pytest
from atlas.adapters.case_minor_courses import APPLIED, TECHNICAL, BASE, POOLS, parse_department

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/case_minor_courses'

@pytest.mark.parametrize('pid,department',[(pid,dept) for pid,pool in POOLS.items() for dept in pool])
def test_registered_source_observes_exact_existing_course_ids(pid,department):
    spec=importlib.util.spec_from_file_location('case_minor',ROOT/'atlas/adapters'/pid/'adapter.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    url=BASE+department+'/'
    assert url in adapter.SOURCES
    observed=adapter.SOURCE_PARSERS[url]((FIX/(department+'.html')).read_text())
    reviewed=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text())
    actual={c['id']:c for c in reviewed['courses']}
    assert len(observed['courses'])==len(POOLS[pid][department])
    for c in observed['courses']:
        assert c['id'] in actual
        assert (c['code'],c['credits'],c['prerequisites'])==(actual[c['id']]['code'],actual[c['id']]['credits'],actual[c['id']]['prerequisites'])
        assert c['description'] is None and c['credit_unit']=='semester_hours'
        assert c['public_site'] is None and c['syllabus'] is None
    assert observed['curriculum_status']=='partial'
    assert not {'curriculum_audit','last_verified'} & observed.keys()


def test_amount_restriction_and_description_changes_are_observed():
    html=(FIX/'scmg.html').read_text()
    baseline=parse_department(html,pid=APPLIED,department='scmg')
    changed=parse_department(html.replace('1.5 Unit.','2 Units.',1).replace('SCMG 433 and SCMG 492','SCMG 433'),pid=APPLIED,department='scmg')
    assert changed['courses'][0]['credits']==2
    assert 'SCMG 492' not in changed['courses'][0]['prerequisites']
    assert 'Master of Supply Chain Management' in baseline['courses'][0]['prerequisites']
    assert changed['observed_description_digests']!=baseline['observed_description_digests']
    changed=parse_department(html.replace('Synthetic course description','Changed prose'),pid=APPLIED,department='scmg')
    assert changed['observed_description_digests']!=baseline['observed_description_digests']


@pytest.mark.parametrize('mutation',[
    lambda h:h.replace('(SCMG)','(CSDS)'),
    lambda h:h.replace('SCMG 462.','SCMG 999.'),
    lambda h:h.replace('1.5 Unit.','1-3 Units.'),
    lambda h:h+h[h.index('<div class="courseblock">'):],
])
def test_wrong_missing_ambiguous_or_variable_course_structure_rejected(mutation):
    with pytest.raises(ValueError):parse_department(mutation((FIX/'scmg.html').read_text()),pid=APPLIED,department='scmg')


def test_cross_list_and_null_prerequisite_are_not_invented():
    html=(FIX/'cogs.html').read_text()
    observed=parse_department(html,pid=APPLIED,department='cogs')
    assert all(c['prerequisites'] is None for c in observed['courses'])
    with pytest.raises(ValueError):parse_department(html.replace('RLGN 250','RLGN 251'),pid=APPLIED,department='cogs')


def test_reviewed_course_coverage_and_policy_conflicts():
    from atlas.db import validate_program
    for pid,descriptions,prerequisites in [(APPLIED,25,18),(TECHNICAL,7,4)]:
        d=json.loads((ROOT/'data/programs'/f'{pid}.json').read_text());validate_program(d)
        assert sum(c['description'] is not None for c in d['courses'])==descriptions
        assert sum(c['prerequisites'] is not None for c in d['courses'])==prerequisites
    d=json.loads((ROOT/'data/programs'/f'{APPLIED}.json').read_text())
    assert d['status']=='unknown' and d['first_offered'] is None
    assert d['curriculum_status']=='partial' and d['curriculum_audit']['unresolved_requirements']
    assert sum(c['credits']==1.5 for c in d['courses'])==6
    assert 'In Approval' in ' '.join(d['notes'])
    note=next(r for r in d['requirements'] if r['id'].endswith('graduate-elective-restrictions'))
    assert len(note['course_ids'])==3 and 'No undergraduate exception was verified' in note['summary']
    assert any(r['count']==2 and r['credits']==6 for r in d['requirements'])
