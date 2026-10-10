"""Final survey identities must remain evidence-backed and explicitly partial."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.final_discovery_common import parse_claims
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'research/national-final-manifest.json').read_text())


def parse(html):
    return parse_claims(html, program_id='sample', title='Artificial Intelligence',
                        award='concentration', kind='concentration',
                        heading='Computer Science BS',
                        claims=['Artificial Intelligence concentration',
                                'Students must select a concentration'])


def test_refresh_returns_only_identity_observations():
    result = parse('<main><h1>Computer Science BS</h1>'
                   '<p>Artificial Intelligence concentration.</p>'
                   '<p>Students must select a concentration.</p></main>')
    assert result == {'id': 'sample', 'title': 'Artificial Intelligence',
                      'award_level': 'concentration', 'program_kind': 'concentration'}


@pytest.mark.parametrize('html', [
    '<main><h1>Computer Science BS</h1><p>Artificial Intelligence concentration</p></main>',
    '<main><h1>Computer Science BS</h1><p>Students must select a concentration</p></main>',
    '<main><h1>Unrelated</h1><p>Artificial Intelligence concentration. Students must select a concentration.</p></main>',
    '<nav><h1>Computer Science BS</h1><p>Artificial Intelligence concentration. Students must select a concentration.</p></nav><main><h1>Welcome</h1></main>',
    '<aside><p>Artificial Intelligence concentration. Students must select a concentration.</p></aside><main><h1>Computer Science BS</h1></main>',
    '<main><h1>Sign in</h1><h2>Computer Science BS</h2><p>Artificial Intelligence concentration. Students must select a concentration.</p></main>',
    '<main><h1>Computer Science BS</h1><input type="password"><p>Artificial Intelligence concentration. Students must select a concentration.</p></main>',
])
def test_incomplete_navigation_or_access_evidence_rejected(html):
    with pytest.raises(ValueError):
        parse(html)


@pytest.mark.parametrize('pid', MANIFEST)
def test_new_records_validate_and_reject_unrelated_refresh(pid):
    program = json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())
    validate_program(program)
    adapter = importlib.import_module(f'atlas.adapters.{pid}.adapter')
    assert adapter.PROGRAM_ID == pid
    assert adapter.SOURCES == (program['sources'][0]['url'],)
    assert program['curriculum_status'] == 'pending'
    assert program['verification_status'] == 'partial'
    assert not program['courses'] and not program['requirements']
    assert program['first_offered'] is None
    assert program['institution']['calendar'] == 'unknown'
    for html in ('<main><h1>Unrelated catalog</h1></main>',
                 '<main><h1>Sign in</h1><input type="password"></main>'):
        with pytest.raises(ValueError):
            adapter.parse(html)


def test_final_survey_has_actual_attempts_and_no_absence_claims():
    survey = json.loads((ROOT / 'data/surveys/national-final.json').read_text())
    assert len(survey) == len({r['institution_id'] for r in survey}) == 16
    assert all(r['sources'] and r['checked_at'] == '2026-10-10' for r in survey)
    assert all(r['status'] in {'confirmed', 'inspected', 'inaccessible'} for r in survey)
    assert sum(len(r['discoveries']) for r in survey) == len(MANIFEST) == 12
    assert sum(r['status'] == 'confirmed' for r in survey) == 9
