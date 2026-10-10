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


def test_content_header_is_evidence_but_global_navigation_is_not():
    assert parse('<main><header><h1>Artificial Intelligence Minor</h1></header></main>')['award_level'] == 'minor'
    with pytest.raises(ValueError):
        parse('<header><h1>Artificial Intelligence Minor</h1></header><main><h1>Welcome</h1></main>')


def test_article_header_survives_layout_cleanup():
    assert parse('<article><header><div><h1>New Artificial Intelligence Minor</h1></div></header></article>')['program_kind'] == 'minor'


def test_heading_context_crosses_wrappers_without_borrowing_peer_section():
    assert parse('<main><div><h1>Artificial Intelligence</h1></div><div><p>Undergraduate minor</p></div></main>')['award_level'] == 'minor'
    with pytest.raises(ValueError):
        parse('<main><div><h2>Artificial Intelligence</h2></div><div><h2>Biology</h2><p>minor</p></div></main>')


def test_plain_list_awards_and_bold_list_identity_are_local():
    assert parse('<main><ul><li>Minor in Artificial Intelligence</li></ul></main>')['award_level'] == 'minor'
    record = parse_identity('<main><ul><li><strong>Major in Artificial Intelligence</strong>: Bachelor of Arts and Bachelor of Science pathways.</li></ul></main>',
                            program_id='sample', title='Artificial Intelligence', award='BA', kind='degree')
    assert record['award_level'] == 'BA'
    with pytest.raises(ValueError):
        parse_identity('<main><ul><li><strong>Artificial Intelligence</strong> research</li><li>Biology BS</li></ul></main>',
                       program_id='sample', title='Artificial Intelligence', award='BS', kind='degree')


def test_directory_award_requires_immediately_preceding_section_heading():
    config = dict(program_id='sample', title='Artificial Intelligence and Biology, BS (Boston)',
                  aliases=('Artificial Intelligence and Biology (Boston)',), award='BS', kind='degree',
                  inherit_section_award=True)
    assert parse_identity('<main><h2>Bachelor of Science (BS)</h2><ul><li><a>Artificial Intelligence and Biology (Boston)</a></li></ul></main>', **config)['award_level'] == 'BS'
    with pytest.raises(ValueError):
        parse_identity('<main><h2>BS</h2><ul><li>Biology</li></ul><h2>Graduate Programs</h2><ul><li><a>Artificial Intelligence and Biology (Boston)</a></li></ul></main>', **config)


@pytest.mark.parametrize('scope,html,award', [
    ('courseleaf-title', '<header><div id="site-title"><h1>Artificial Intelligence Minor</h1></div></header><main>Requirements</main>', 'minor'),
    ('miami-title', '<div id="content-container"><div><h1>B.B.A. in Artificial Intelligence</h1><div id="content">Requirements</div></div></div>', 'other'),
    ('cornell-program-hero', '<div class="hero-banner--program-detail"><div class="hero-banner-content"><span>Minor</span><h1>Artificial Intelligence</h1></div></div><main>Requirements</main>', 'minor'),
    ('stevens-program-hero', '<main><div class="_slug__hero-wrapper__abc"><h1>Artificial Intelligence</h1><div><h3>Degree</h3><span>Bachelor of Science</span></div></div></main>', 'BS'),
])
def test_explicit_reviewed_page_identity_scopes(scope, html, award):
    record = parse_identity(html, program_id='sample', title='Artificial Intelligence', award=award,
                            kind='minor' if award == 'minor' else 'degree', identity_scopes=(scope,),
                            award_terms=('BBA',) if award == 'other' else ())
    assert record['award_level'] == award


def test_explicit_prose_scope_never_borrows_another_sentences_award():
    html = '<main><umd-element-pathway><div slot="text"><p>The Bachelor of Arts in Human-Centered AI starts this fall. The Bachelor of Science in Computer Science starts later.</p></div></umd-element-pathway></main>'
    config = dict(program_id='sample', title='Human-Centered AI', kind='degree', identity_scopes=('maryland-pathway-text',))
    assert parse_identity(html, award='BA', **config)['award_level'] == 'BA'
    with pytest.raises(ValueError):
        parse_identity(html, award='BS', **config)


def test_explicit_scope_cannot_restore_navigation_or_hidden_content():
    for wrapper in ('nav', 'aside'):
        html = f'<{wrapper}><div id="site-title"><h1>Artificial Intelligence Minor</h1></div></{wrapper}><main><h1>Welcome</h1></main>'
        with pytest.raises(ValueError):
            parse_identity(html, program_id='sample', title='Artificial Intelligence', award='minor', kind='minor', identity_scopes=('courseleaf-title',))
    with pytest.raises(ValueError):
        parse('<main><li aria-hidden="true">Artificial Intelligence Minor</li></main>')


def test_page_title_cannot_borrow_related_programs_award():
    with pytest.raises(ValueError):
        parse('<main><h1>Artificial Intelligence</h1><p>Research project</p><h2>Related Programs</h2><p>Biology minor</p></main>')


def test_outer_list_cannot_mix_child_program_identity_and_award():
    with pytest.raises(ValueError):
        parse('<main><ul><li>Programs<ul><li>Artificial Intelligence research</li><li>Biology minor</li></ul></li></ul></main>')
