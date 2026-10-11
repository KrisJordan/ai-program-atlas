"""College/cohort requirements must not become universal AI-major courses."""
import json
from pathlib import Path

import pytest

from atlas.adapters import ucsd_eighth_pools as eighth
from atlas.adapters import ucsd_marshall_pools as marshall
from atlas.adapters import ucsd_revelle_pools as revelle
from atlas.adapters.ucsd_college_context import (
    COLLEGE_SOURCE_PREFIXES, PID, college_parent, requirement,
)
from atlas.curriculum_profile import requirement_profile
from atlas.db import validate_program


@pytest.mark.parametrize('college,prefixes', COLLEGE_SOURCE_PREFIXES.items())
def test_college_rules_inherit_existing_conditional_pathway(college, prefixes):
    for prefix in prefixes:
        source = PID + '-' + prefix + 'fixture'
        row = requirement(PID, 'fixture', 'Synthetic selection', source,
                          kind='choose_courses', count=2, credits=8)
        assert row['parent_id'] == PID + '-policy-college-' + college
        assert row['count'] == 2 and row['credits'] == 8
        nested = requirement(PID, 'nested', 'Synthetic nested rule', source,
                             parent=PID + '-fixture')
        assert nested['parent_id'] == PID + '-fixture'
    assert college_parent(PID + '-catalog') is None
    assert college_parent('another-program-revelle-fixture') is None


def test_revelle_first_year_sequence_remains_conditional_in_parser():
    html = '<h1>Humanities Requirements</h1><p>D grade or better; regardless of transfer type; first year at UC San Diego; HUM-001 or -002; Entry Level Writing Requirement</p><table>'
    for number in [1, 2, 3, 4, 5, 100]:
        html += f'<tr><td>Humanities {number}:</td><td>Synthetic course 4 units, letter graded</td></tr>'
    result = revelle.parse_humanities(html + '</table>')
    first = next(n for n in result['requirements'] if n['kind'] == 'all')
    assert first['parent_id'] == PID + '-policy-college-revelle-college'
    assert len(first['course_ids']) == 5
    assert requirement_profile(result)['required']['count'] == 0


def test_marshall_first_year_and_new_transfer_are_not_universal():
    html = '<h1>General Education Requirements for First-Year Students</h1><p>Option A: Option B: Option C: two different academic disciplines; four 4-unit; no exceptions; before enrolling in DOC 2 and DOC 3</p>'
    html += ''.join(f'<h3>DOC-{n}: Synthetic course (4 units)</h3>' for n in [1, 2, 3])
    first = marshall.parse_first(html)
    transfer = marshall.parse_transfer('<h1>General Education Requirements for Transfer Students</h1><p>Cal-GETC; Fall 2026 term and forward; DOC-170; Winter 2027; one or two missing IGETC; D grade or better; Letter of GE Completion; course-by-course basis</p>')
    for result in [first, transfer]:
        assert requirement_profile(result)['required']['count'] == 0
        assert all(n['parent_id'] == PID + '-policy-college-thurgood-marshall-college'
                   for n in result['requirements'] if n['kind'] == 'all')
    rule = next(n for n in transfer['requirements'] if n['kind'] == 'all')
    assert 'Fall 2026 onward' in rule['summary']


def test_eighth_transfer_parser_preserves_sequence_and_applicability():
    result = eighth.parse_transfer('<h1>Degree Requirements for Transfer Students</h1><p>CCE-110 (4 units); CCE-120 (4 units); Two Additional College Level Writing Courses; Starting in Fall 2026; six quarters; Official Letter of Reciprocity</p>')
    rule = next(n for n in result['requirements'] if n['kind'] == 'all')
    assert rule['parent_id'] == PID + '-policy-college-eighth-college'
    assert len(rule['course_ids']) == 2
    assert 'Fall2026' in rule['summary']
    assert requirement_profile(result)['required']['count'] == 0


def test_curated_college_graph_has_only_eight_fixed_major_courses():
    program = json.loads(Path('data/programs', PID + '.json').read_text())
    validate_program(program)
    groups = {r['id']: r for r in program['requirements']}
    for row in groups.values():
        expected = college_parent(row['source_id'])
        if expected is None:
            continue
        ancestors = set()
        parent = row['parent_id']
        while parent:
            assert parent not in ancestors
            ancestors.add(parent)
            parent = groups[parent]['parent_id']
        assert expected in ancestors
        assert groups[expected]['kind'] == 'note'
    profile = requirement_profile(program)
    assert profile['required']['count'] == 8
    assert profile['required']['categories']['human_context'] == 0
    conditional_ids = {
        'revelle-humanities-first', 'marshall-core-doc-1', 'marshall-core-doc-2',
        'marshall-core-doc-3', 'marshall-transfer-doc170', 'eighth-transfer-cce',
    }
    assert sum(len(groups[PID + '-' + key]['course_ids']) for key in conditional_ids) == 11
    for choice in profile['choices']:
        if college_parent(choice['source_id']):
            assert choice['context'] == 'unresolved'
    assert program['curriculum_status'] == 'partial'
