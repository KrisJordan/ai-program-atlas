"""Identity refresh must reject absent titles, navigation and access pages."""
import importlib
import json
from pathlib import Path

import pytest

from atlas.adapters.discovery_common import parse_identity
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'research/national-discovery-manifest.json').read_text())


def parse(html):
    return parse_identity(html, program_id='sample-ai-minor', title='Artificial Intelligence',
                          award='minor', kind='minor')


def test_identity_returns_only_observed_fields():
    assert parse('<main><h1>Artificial Intelligence</h1><p>Undergraduate minor</p></main>') == {
        'id': 'sample-ai-minor', 'title': 'Artificial Intelligence',
        'award_level': 'minor', 'program_kind': 'minor'}


@pytest.mark.parametrize('html', [
    '<main><h1>Computer Science</h1><p>Undergraduate minor</p></main>',
    '<nav><a>Artificial Intelligence minor</a></nav><main><h1>Welcome</h1></main>',
    '<main><h1>Log in</h1><h2>Artificial Intelligence minor</h2></main>',
    '<main><h1>Artificial Intelligence minor</h1><input type="password"></main>',
    '<main><h1>Artificial Intelligence</h1><p>Research laboratory</p></main>',
    '<main><h2>Artificial Intelligence</h2><p>Degree</p><h2>Biology</h2><p>minor</p></main>',
    '<main><p>Our Artificial Intelligence minor is mentioned in prose only.</p></main>',
])
def test_missing_or_nonprogram_evidence_rejected(html):
    with pytest.raises(ValueError):
        parse(html)


def test_award_must_be_in_same_directory_entry():
    html = '<main><ul><li><a>AI and Language</a> BA</li><li><a>AI and Biology</a> BS</li></ul></main>'
    with pytest.raises(ValueError):
        parse_identity(html, program_id='sample', title='AI and Language', award='BS', kind='degree')


@pytest.mark.parametrize('pid', MANIFEST)
def test_discovery_records_and_adapter_registration(pid):
    program = json.loads((ROOT / 'data/programs' / f'{pid}.json').read_text())
    validate_program(program)
    adapter = importlib.import_module(f'atlas.adapters.{pid}.adapter')
    assert adapter.PROGRAM_ID == pid
    assert adapter.SOURCES == (program['sources'][0]['url'],)
    assert program['curriculum_status'] == 'pending'
    assert not program['courses'] and not program['requirements']
    assert program['first_offered'] is None
    assert program['institution']['calendar'] == 'unknown'
    with pytest.raises(ValueError):
        adapter.parse('<main><h1>Unrelated course catalog</h1></main>')
    with pytest.raises(ValueError):
        adapter.parse('<main><h1>Sign in</h1><input type="password"></main>')


def test_survey_contains_every_national_cohort_institution_once():
    cohort = json.loads((ROOT / 'data/cohort.json').read_text())
    expected = {i['id'] for i in cohort['institutions']
                if any(r['category'] == 'National Universities' for r in i['rankings'])}
    survey = json.loads((ROOT / 'data/surveys/national.json').read_text())
    assert len(survey) == len(expected) == 108
    assert {r['institution_id'] for r in survey} == expected
    for row in survey:
        if row['status'] == 'confirmed':
            assert row['discoveries'] and row['sources'] and row['checked_at']
        if row['status'] == 'pending':
            assert row['checked_at'] is None
