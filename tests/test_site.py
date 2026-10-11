"""Publishing tests use isolated synthetic records, never exported production data."""
from copy import deepcopy
import json

import pytest

from atlas.site import build, unique_courses


@pytest.fixture
def site_data():
    programs = []
    institutions = []
    for index in range(5):
        institution = {"id": f"test-{index}", "name": f"Test Institution {index}", "calendar": "quarter" if index else "semester", "aliases": [], "website": "https://example.edu"}
        institutions.append({**institution, "coverage_status": "pending", "rankings": [{"category": "National Liberal Arts Colleges" if index else "National Universities"}], "program_ids": [f"test-ai-{index}"]})
        course = {"id": f"course-{index}", "code": f"AI {index}01", "name": "Machine Learning", "category": "ai_ml", "credits": None, "credit_unit": "quarter_hours" if index else "semester_hours", "prerequisites": None, "url": "https://example.edu/course"}
        programs.append({"id": f"test-ai-{index}", "institution": institution, "title": f"Artificial Intelligence {index}", "award_level": "minor" if index else "BS", "program_kind": "minor" if index else "degree", "overview": "A test-only curriculum record.", "status": "active", "verification_status": "partial", "curriculum_status": "partial", "last_verified": "2026-10-10", "catalog_year": None, "courses": [course, deepcopy(course)], "requirements": [], "sources": [], "outcomes": [], "links": [{"kind": "catalog", "url": "https://example.edu/catalog", "label": "Catalog"}], "notes": []})
    programs[1]['curriculum_status'] = 'complete'
    programs[2].update(program_kind='additional_major', curriculum_status='pending', courses=[])
    programs[3].update(program_kind='concentration', curriculum_status='pending', courses=[])
    institutions[0]['rankings'][0].update(publisher='U.S. News', edition='2027', rank=20, source_url='https://example.edu/ranking', verification_status='primary_verified')
    programs[0]['institution']['rankings'] = institutions[0]['rankings']
    for index, theme in [(0, 'AI methods'), (1, 'Responsible AI and society')]:
        programs[index]['sources'] = [{'id': 'outcome-source', 'url': 'https://example.edu/outcome', 'title': 'Official evidence'}]
        programs[index]['outcomes'] = [{'text': theme, 'kind': 'inferred_taxonomy', 'source_id': 'outcome-source'}, {'text': 'Learn a documented skill.', 'kind': 'source_stated', 'source_id': 'outcome-source'}]
    programs[0]['outcomes'] += [dict(text=text, kind='source_stated', statement_type=kind, source_id='outcome-source') for kind, text in [('learning_outcome', 'Evaluate a model.'), ('program_aim', 'Connect computing and society.'), ('career_pathway', 'Careers in research and industry.')]]
    return {"meta": {"limitations": ["Test coverage is incomplete."]}, "programs": programs, "institutions": institutions, "csrankings": {"status": "not_imported"}}


def test_build_static_routes_and_unique_counts(tmp_path, site_data):
    build(site_data, tmp_path, "/nested/atlas/")
    assert len(unique_courses(site_data["programs"][0])) == 1
    index = (tmp_path / "index.html").read_text()
    assert 'href="/nested/atlas/programs/test-ai-0/"' in index
    assert 'src="/nested/atlas/assets/atlas.js?v=' in index
    detail = (tmp_path / "programs/test-ai-0/index.html").read_text()
    assert "1 course record is outside the fixed/option count profiles" in detail
    assert "1 of 1 course records have unknown credits" in detail
    assert "Unknown values are not zero" in detail
    assert (tmp_path / "coverage/index.html").exists()
    assert "not imported" in (tmp_path / "methodology/index.html").read_text()
    assert json.loads((tmp_path / "data.json").read_text())["programs"]


def test_source_text_escaped_and_unsafe_links_rejected(tmp_path, site_data):
    site_data["programs"][0]["title"] = '</script><script>alert("x")</script>'
    site_data["programs"][0]["links"][0]["url"] = 'javascript:alert("x")'
    build(site_data, tmp_path)
    detail = (tmp_path / "programs/test-ai-0/index.html").read_text()
    assert '<script>alert(' not in detail
    assert 'href="javascript:' not in detail
    assert '&lt;/script&gt;' in detail
    assert '\\u003c/script\\u003e' in (tmp_path / "index.html").read_text()


@pytest.mark.parametrize("path", ["../outside", "/a/../../b", '/"><script>/'])
def test_invalid_base_path(tmp_path, site_data, path):
    with pytest.raises(ValueError):
        build(site_data, tmp_path, path)


def test_invalid_program_path(tmp_path, site_data):
    site_data["programs"][0]["id"] = "../outside"
    with pytest.raises(ValueError):
        build(site_data, tmp_path)


def test_identity_counts_and_research_configuration(tmp_path, site_data):
    site_data['csrankings'] = {'methodology': {'year_start': 2016, 'year_end': 2025, 'fields': ['ai', 'vision'], 'geographic_filter': 'us', 'source_snapshot': 'pinned-test-snapshot', 'source_url': 'https://csrankings.org/faq', 'status': 'not_imported', 'method': 'A configured method with no computed values.'}, 'observations': [{'value': None, 'rank': None, 'missingness': 'permission_required'}]}
    build(site_data, tmp_path)
    coverage = (tmp_path / 'coverage/index.html').read_text()
    assert '2 records are identity-only' in coverage
    assert 'Counts include all documented records' in coverage
    methodology = (tmp_path / 'methodology/index.html').read_text()
    for text in ['2016–2025', 'Artificial intelligence (ai)', 'Computer vision (vision)', 'pinned-test-snapshot', 'permission_required', 'A configured method with no computed values.', 'additional majors']:
        assert text in methodology
    assert 'https://csrankings.org/faq.html' not in methodology
    index = (tmp_path / 'index.html').read_text()
    assert 'Additional major</span>' in index


def test_empty_curriculum_profile_and_rank_provenance(tmp_path, site_data):
    build(site_data, tmp_path)
    pending = (tmp_path / 'programs/test-ai-2/index.html').read_text()
    assert 'Curriculum profile not yet extracted' in pending
    assert 'class="category-row"' not in pending
    documented = (tmp_path / 'programs/test-ai-0/index.html').read_text()
    assert 'U.S. News 2027 · National Universities · #20' in documented
    assert 'href="https://example.edu/ranking"' in documented
    assert 'not a measure of this program or undergraduate teaching quality' in documented


def test_program_statements_use_explicit_types_only(tmp_path, site_data):
    from bs4 import BeautifulSoup
    program = site_data['programs'][0]
    program['outcomes'].append(dict(text='Graduates will learn another skill.', kind='source_stated', statement_type='unspecified', source_id='outcome-source'))
    build(site_data, tmp_path)
    soup = BeautifulSoup((tmp_path / 'programs/test-ai-0/index.html').read_text(), 'html.parser')
    section = soup.find(id='outcomes')
    assert section.find('h2').get_text() == 'Program aims & outcomes'
    source_items = section.find(class_='outcomes').find_all('li')
    labels = {item.find(class_='statement-text').get_text(): item.find(class_='statement-type').get_text() for item in source_items}
    assert labels['Learn a documented skill.'] == 'Source statement'
    assert labels['Graduates will learn another skill.'] == 'Source statement'
    assert labels['Evaluate a model.'] == 'Learning outcome'
    assert labels['Connect computing and society.'] == 'Program aim'
    assert labels['Careers in research and industry.'] == 'Career pathway'
    inference = section.find_all(class_='outcomes')[1]
    assert inference.find(class_='statement-type').get_text() == 'Documented inference'
    assert inference.find('a')['href'] == 'https://example.edu/outcome'
    assert '03 / LEARNING OUTCOMES' not in str(section)


def test_statement_type_does_not_change_inference_provenance():
    from atlas.site import outcomes
    html = outcomes({'outcomes': [{'text': 'A recorded editorial interpretation.', 'kind': 'inferred_taxonomy', 'statement_type': 'program_aim'}]}, 'inferred_taxonomy')
    assert 'Program aim · Documented inference' in html
    assert 'Source statement' not in html


def test_directory_static_rank_order_keeps_category_and_evidence(site_data, tmp_path):
    """No-JS baseline uses research ranks while retaining U.S. News provenance."""
    from bs4 import BeautifulSoup
    site_data['meta']['cohort'] = {'edition': '2027'}
    for index, (name, rank, status) in enumerate([
        ('Zulu', 2, 'primary_verified'), ('Alpha', 10, 'enumerated_secondary'),
        ('Beta', 1, 'primary_edition_inferred'), ('Gamma', None, 'primary_verified'),
        ('Omega', 2, 'secondary_reported'),
    ]):
        institution = site_data['institutions'][index]
        institution['name'] = name
        institution['rankings'] = [dict(publisher='U.S. News', edition='2027', category='National Universities', rank=rank, rank_upper_bound=100, source_url='https://example.edu/rank-' + str(index), verification_status=status)]
        site_data['programs'][index]['institution'] = deepcopy(institution)
        site_data['programs'][index].update(program_kind='degree', award_level='BS')
    site_data['csrankings'] = dict(methodology=dict(status='available'), observations=[
        dict(institution_id=site_data['institutions'][i]['id'], field='aggregate',
             missingness='observed', value=5.0, rank=rank) for i, rank in [(0,2),(1,10),(4,2)]])
    original = deepcopy(site_data)
    build(site_data, tmp_path)
    assert site_data == original
    soup = BeautifulSoup((tmp_path / 'index.html').read_text(), 'html.parser')
    grid = soup.find(id='cohort-nu-majors').find(class_='program-grid')
    cards = grid.find_all('article', recursive=False)
    assert [c['data-program-id'] for c in cards] == ['test-ai-4', 'test-ai-0', 'test-ai-1', 'test-ai-2', 'test-ai-3']
    assert [c['data-sort-rank'] for c in cards] == ['2', '2', '10', '', '']
    assert 'reported #1 is not used for sorting' in cards[3].get_text()
    assert 'Enumerated secondary' in cards[2].get_text()
    assert cards[2].find(class_='card-ranking').find('a')['href'] == 'https://example.edu/rank-1'
    assert '2027' in cards[2].find(class_='card-ranking').get_text()
    assert soup.find(id='sort-order').find('option')['value'] == 'csrankings'
    assert 'five-field aggregate' in soup.find(class_='directory-method-note').get_text()
    rows = soup.select('#cohort-nu-majors .directory-table tbody tr')
    assert [r['data-row-id'] for r in rows] == [c['data-program-id'] for c in cards]
    assert soup.find('dialog', id='filter-panel')
    assert not soup.select('.inventory-counts, .edition-note, .coverage-strip')
