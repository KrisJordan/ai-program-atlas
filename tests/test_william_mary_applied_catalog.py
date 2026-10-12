"""Source table extraction, current graph roles and static rendered evidence."""
import importlib
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from atlas.adapters.william_mary_applied_catalog import CATALOG, SID, parse
from atlas.curriculum_profile import requirement_profile
from atlas.degree_audit import core_review_fingerprint
from atlas.db import validate_program
from atlas.site import build

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/william_mary/ba_catalog.html'
FIXED = {'wm-applied-ai-' + code for code in (
    'aai-101', 'aai-301', 'aai-302', 'data-201', 'data-210', 'data-303', 'data-405')}


def test_catalog_preserves_fixed_choice_capstone_open_elective_and_distinct_totals():
    p = parse(FIXTURE.read_text())
    profile = requirement_profile(p, include_course_ids=True)
    assert set(profile['course_ids']['required']) == FIXED
    assert set(profile['course_ids']['options']) == {'wm-applied-ai-data-202', 'wm-applied-ai-phil-150'}
    choices = [r for r in p['requirements'] if r['kind'] == 'choose_courses']
    assert len(choices) == 1 and choices[0]['count'] == 1 and choices[0]['credits'] is None
    electives = next(r for r in p['requirements'] if r['kind'] == 'choose_credits')
    assert electives['credits'] == 6 and electives['count'] is None and electives['course_ids'] == []
    assert 'advisor' in electives['summary'] and 'Applied AI attribute' in electives['summary']
    assert [r['credits'] for r in p['requirements'][:2]] == [30, 120]
    assert p['requirements'][1]['kind'] == 'note'
    assert {c['code']: c['credits'] for c in p['courses']}['PHIL 150'] == 4
    assert not {'curriculum_audit', 'curriculum_status', 'last_verified'} & p.keys()
    adapter = importlib.import_module('atlas.adapters.william-mary-applied-ai-ba.adapter')
    assert CATALOG in adapter.SOURCES and adapter.SOURCE_PARSERS[CATALOG] is parse


@pytest.mark.parametrize('old,new', [
    ('2026-2027 Edition', '2025-2026 Edition'),
    ('id="requirementstext"', 'id="overviewtext"'),
    ('or <a', 'and <a'),
    ('Total Hours</th><td>30', 'Total Hours</th><td>31'),
    ('Capstone:', 'Recommended capstone:'),
    ('Applied AI attribute', 'Any attribute'),
    ('Core Courses:', 'Sample courses:'),
])
def test_unreviewed_edition_operator_and_structure_changes_fail(old, new):
    with pytest.raises(ValueError):
        parse(FIXTURE.read_text().replace(old, new))


def test_new_courses_and_credit_changes_are_observed_not_static_replays():
    result = parse(FIXTURE.read_text().replace('DATA%20210', 'DATA%20211').replace('DATA 210', 'DATA 211'))
    assert 'DATA 211' in {c['code'] for c in result['courses']}
    assert 'DATA 210' not in {c['code'] for c in result['courses']}
    result = parse(FIXTURE.read_text().replace('Technology (4)', 'Technology (5)'))
    assert next(c for c in result['courses'] if c['code'] == 'PHIL 150')['credits'] == 5


def test_curated_graph_keeps_faq_and_section_prerequisites_out_of_catalog_fixed_set():
    p = json.loads((ROOT / 'data/programs/william-mary-applied-ai-ba.json').read_text())
    validate_program(p)
    profile = requirement_profile(p, include_course_ids=True)
    assert set(profile['course_ids']['required']) == FIXED
    assert set(profile['course_ids']['options']) == {'wm-applied-ai-data-202', 'wm-applied-ai-phil-150'}
    assert profile['course_ids']['unresolved'] == ['wm-applied-ai-data-305']
    assert p['curriculum_status'] == 'partial'
    assert not p.get('course_identity_groups')
    assert sum(c['category_review']['status'] == 'unclassified' for c in p['courses']) == 7
    review = next(r for r in json.loads((ROOT / 'research/degree-audit/independent-core-other.json').read_text())['programs'] if r['program_id'] == p['id'])
    assert review['reviewed_content_hash'] == core_review_fingerprint(p)
    assert review['expected_profile']['required']['count'] == 7
    assert all(d['status'] == 'partial' for d in review['dimensions'].values())


def test_static_program_page_preserves_catalog_links_and_all_choice_labels(tmp_path):
    p = json.loads((ROOT / 'data/programs/william-mary-applied-ai-ba.json').read_text())
    build({'meta': {}, 'institutions': [{**p['institution'], 'program_ids': [p['id']]}], 'programs': [p], 'rankings': []}, tmp_path, base_path='/review/atlas/')
    page = BeautifulSoup((tmp_path / 'programs' / p['id'] / 'index.html').read_text(), 'html.parser')
    text = page.get_text(' ', strip=True)
    for phrase in ['AAI 301', 'PHIL 150', 'Agentic Coordination', 'Applied AI or advisor-approved electives', '2026-2027', '31']:
        assert phrase in text
    assert page.find('a', href=CATALOG + '#requirementstext')
    assert page.find('a', href='/review/atlas/')
    assert page.find(id='course-wm-applied-ai-data-305')
