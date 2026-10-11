"""Invented, bounded policy fixtures; no copyrighted page snapshots."""
import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import ucsb_policies as p
from atlas.db import validate_program


def fixture():
    return '''<h1>Undergraduate Requirements</h1><p>2018 forward. 35 of the final 45; 35 of the final 90; minimum of 12 units on campus; at least three terms; 6 or more units; at least two units but fewer than six; at least a 2.0; third quarter of matriculation; nine quarters or more; one four-unit course; one of these areas; P/NP basis.</p><p>Students must complete Writing 2 or 2E and one course from Writing 50, 109ST. NOTE: Test.</p><p>Area D: A minimum of 2 courses. Area E: A minimum of 2 courses. Area F: A minimum of 1 course. Area G: A minimum of 1 course. four designated courses; 1800 words; ENGR 101; Ethnicity Requirement (one course); World Cultures Requirement (one course)</p>'''


def test_policy_choices_changed_numbers_and_unknown_metadata():
    r = p.parse_requirements(fixture())
    assert {c['code'] for c in r['courses']} == {'WRIT 2', 'WRIT 2E', 'WRIT 50', 'WRIT 109ST'}
    assert all(c['name'] is None and c['credits'] is None for c in r['courses'])
    r2 = p.parse_requirements(fixture().replace('Writing 50, 109ST', 'Writing 51, 109ST').replace('Area D: A minimum of 2', 'Area D: A minimum of 3'))
    assert 'WRIT 51' in {c['code'] for c in r2['courses']}
    assert next(n for n in r2['requirements'] if n['id'].endswith('area-d'))['count'] == 3
    assert not any(n['id'].endswith('area-h') for n in r['requirements'])
    assert 'curriculum_audit' not in r and r['curriculum_status'] == 'partial'
    with pytest.raises(ValueError): p.parse_requirements(fixture().replace('35 of the final 45', 'changed rule'))


def test_current_catalog_awpe_guard_and_no_placement_bundle():
    html = '<h1>UC Entry Level Writing Requirement</h1><p>3 or higher on either of the English AP Exams; 30 or higher; 680 or higher; 5 or higher; 6 or higher; only accept AWPE results from students transferring from another UC campus; LING 12 with a C or better; C- or lower must repeat Writing 1; neither earns UC-transferable units</p>'
    r = p.parse_elwr(html)
    assert all(n['kind'] == 'note' and not n['course_ids'] for n in r['requirements'])
    with pytest.raises(ValueError): p.parse_elwr(html.replace('another UC campus', 'any campus'))


def test_reviewed_gear_values_keep_unresolved_conflicts():
    d = json.loads(Path('data/programs/ucsb-ai-bs.json').read_text())
    validate_program(d)
    nodes = {n['id']: n for n in d['requirements']}
    assert nodes['ucsb-ai-bs-science-list-a']['credits'] == 8
    assert nodes['ucsb-ai-bs-science-list-b']['credits'] == 12
    assert nodes['ucsb-ai-bs-upper']['credits'] == 36
    assert '72' in nodes['ucsb-ai-bs-upper']['summary']
    assert next(c for c in d['courses'] if c['code'] == 'CMPSC 41')['credits'] is None
    assert d['curriculum_status'] == 'partial'
    assert any('capstone' in s.lower() for s in d['curriculum_audit']['unresolved_requirements'])
    adapter = importlib.import_module('atlas.adapters.ucsb-ai-bs.adapter')
    assert p.GEAR_URL in adapter.SOURCES and p.GEAR_URL not in adapter.SOURCE_PARSERS
