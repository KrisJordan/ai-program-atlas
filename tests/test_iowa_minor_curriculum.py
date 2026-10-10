"""Hand-authored miniature catalog fragments; no downloaded HTML is committed."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.requirements import validate_requirements, validate_curriculum_audit

adapter = importlib.import_module('atlas.adapters.university-of-iowa-artificial-intelligence-theory-methods-and-applications-minor-minor.adapter')


def fixture():
    html = '<h1 class="page-title">Artificial Intelligence: Theory, Methods, and Applications, Minor</h1><p>2026-2027 Edition</p>'
    html += '<p>applications requires 15 s.h.; grade-point average of at least 2.00; pass/nonpass prohibited; maximum of 3 s.h. of transfer. Enrollment: undergraduate degree-seeking.</p>'
    html += '<p>complete at least 12 s.h. in elective selections; at least two of the three categories. Replacement: ECE numbered 5000–5999. Approval: maximum of one AI-related course; AI ethics may qualify.</p>'
    for condition in ('computer programming', 'matrix algebra', 'probability'):
        html += f'<p>For a major that does not require a {condition} course, apply conditional eligibility.</p>'
    for section,code in [('Required Course','ENGR:3110'),('Theory','ECE:5200'),('Methods','ECE:5215'),('Applications','ECE:5230'),('Support','ECE:5320')]:
        html += f'<h3>{section}</h3><table class="sc_courselist"><tr><td>{code}</td><td>Test course</td><td>3</td></tr></table>'
    for code in ('ENGR:1300','MATH:2550','MATH:2700','ECE:3995','STAT:2020','STAT:3120'):
        html += f'<span class="sc_courseinline"><a>{code}</a>Test conditional course</span>'
    return html


def test_iowa_choices_conditions_and_null_metadata():
    p = adapter.parse(fixture())
    validate_requirements(p)
    assert len(p['courses']) == 11
    assert len({c['id'] for c in p['courses']}) == 11
    assert p['curriculum_status'] == 'partial' and 'curriculum_audit' not in p
    assert all(c['prerequisites'] is None for c in p['courses'])
    assert next(c for c in p['courses'] if c['code']=='ENGR:1300')['credits'] is None
    groups = {r['id']:r for r in p['requirements']}
    assert groups['iowa-required']['kind']=='alternative'
    assert len(groups['iowa-substitution']['course_ids'])==3
    assert groups['iowa-electives']['credits']==12
    assert 'at least two' in groups['iowa-electives']['summary']
    assert 'only for' in groups['iowa-conditional-probability']['summary']
    assert 'one' in groups['iowa-approvals']['summary']


def test_iowa_changed_numeric_rules_are_observed_not_recertified():
    original = adapter.parse(fixture())
    changed = adapter.parse(fixture().replace('requires 15 s.h.', 'requires 18 s.h.').replace('at least 12 s.h.', 'at least 15 s.h.').replace('at least 2.00', 'at least 2.50'))
    assert changed['requirements'][0]['credits']==18
    assert next(r for r in changed['requirements'] if r['id']=='iowa-electives')['credits']==15
    assert '2.50' in changed['requirements'][-1]['summary']
    assert changed['observed_policy_digest']!=original['observed_policy_digest']
    assert changed['curriculum_status']=='partial' and 'last_verified' not in changed


def test_iowa_unrecognized_approval_change_requires_review():
    with pytest.raises(ValueError, match='needs review'):
        adapter.parse(fixture().replace('maximum of one AI-related', 'maximum of two AI-related'))


def test_iowa_reviewed_inventory_is_complete_only_with_audit():
    p=json.loads((Path(__file__).resolve().parents[1]/'data/programs'/f'{adapter.PROGRAM_ID}.json').read_text())
    validate_requirements(p);validate_curriculum_audit(p)
    assert p['curriculum_status']=='complete'
    assert p['curriculum_audit']['scope']=='minor'
    assert len(p['courses'])==20
    assert len(p['requirements'])==15
