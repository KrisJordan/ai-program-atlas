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
    assert set(adapter.SOURCES) <= {s['url'] for s in program['sources']}
    if program['curriculum_status'] == 'pending':
        assert program['verification_status'] == 'partial'
        assert not program['courses'] and not program['requirements']
    else:
        assert program['requirements'] and program['curriculum_audit']
    if program['first_offered'] is not None:
        first = program['first_offered']
        assert first['value'] and first['precision']
        assert first['evidence_url'].startswith(('https://', 'http://'))
        assert first['evidence_url'] in {source['url'] for source in program['sources']}
    assert program['institution']['calendar'] in {'unknown','semester','quarter','other'}
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


def test_scoped_content_title_header_is_preserved_but_outer_header_is_rejected():
    config = dict(program_id='sample', title='Artificial Intelligence', award='minor',
                  kind='minor', heading='AI minor', claims=['Undergraduate AI minor'],
                  content_header_class='m-title')
    good = '<main><header class="m-title"><h1>AI minor</h1></header><p>Undergraduate AI minor</p></main>'
    assert parse_claims(good, **config)['award_level'] == 'minor'
    for html in (
        '<header class="m-title"><h1>AI minor</h1></header><main><p>Undergraduate AI minor</p></main>',
        '<main><header class="other"><h1>AI minor</h1></header><p>Undergraduate AI minor</p></main>',
        '<main><header class="m-title"><h1>AI minor</h1></header><p>Research news</p></main>',
    ):
        with pytest.raises(ValueError):
            parse_claims(html, **config)


def test_njit_requires_explicit_award_in_content():
    adapter = importlib.import_module('atlas.adapters.new-jersey-institute-of-technology-business-with-ai-bs-degree.adapter')
    heading = '<main><h3>What is Business with AI?</h3>'
    assert adapter.parse_award(heading + '<p>Bachelor of Science in Business with AI</p></main>')['award_level'] == 'BS'
    with pytest.raises(ValueError):
        adapter.parse_award(heading + '<a href="business-with-ai-bs/">Business with AI</a></main>')
    # The catalog observes the named plan but does not infer the award from its URL.
    plan = '<h1>Business with AI</h1><p>(120 credit minimum)</p><table class="sc_plangrid"><tr class="plangridyear"><th>First Year</th></tr><tr class="plangridterm"><th>1st Semester</th></tr><tr><td class="codecol"><a class="code" href="/search/?P=DS%20110">DS 110</a></td><td class="titlecol">Example AI Foundations</td><td class="hourscol">3</td></tr></table>'
    observed = adapter.parse(plan)
    assert observed['courses'][0]['code'] == 'DS 110'
    assert 'award_level' not in observed
    assert adapter.SOURCE_PARSERS[adapter.SOURCES[1]] is adapter.parse_award
