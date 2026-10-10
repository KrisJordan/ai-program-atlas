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
    return {"meta": {"limitations": ["Test coverage is incomplete."]}, "programs": programs, "institutions": institutions, "csrankings": {"status": "not_imported"}}


def test_build_static_routes_and_unique_counts(tmp_path, site_data):
    build(site_data, tmp_path, "/nested/atlas/")
    assert len(unique_courses(site_data["programs"][0])) == 1
    index = (tmp_path / "index.html").read_text()
    assert 'href="/nested/atlas/programs/test-ai-0/"' in index
    assert 'src="/nested/atlas/assets/atlas.js"' in index
    detail = (tmp_path / "programs/test-ai-0/index.html").read_text()
    assert "1 unique documented course records" in detail
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
