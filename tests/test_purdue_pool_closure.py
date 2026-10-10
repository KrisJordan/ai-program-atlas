"""Synthetic Purdue title-pool and college-policy structure tests."""

import hashlib
from pathlib import Path

import pytest

from atlas.adapters import purdue_college_pools as p


def pool():
    return """<h1>Comprehensive Culture Course List</h1><table id="example">
    <thead><tr><th>Subject</th><th>Number</th><th>Keyword/Title</th><th>UCORE/Civics Literacy Proficiency</th><th>Semester</th><th>Level</th></tr></thead>
    <tfoot><tr><th></th><th></th><th></th><th></th><th></th><th></th></tr></tfoot>
    <tr><td>TEST - Synthetic Subject</td><td>37100</td><td>Example One</td><td></td><td></td><td>3</td></tr>
    <tr><td>TEST - Synthetic Subject</td><td>37100</td><td>Example Two</td><td></td><td>Fall 2026</td><td>3</td></tr>
    <tr><td>TEST - Synthetic Subject</td><td>37100</td><td>Example One</td><td></td><td></td><td>3</td></tr></table>"""


def test_pools_preserve_repeatable_titles_and_deduplicate_exact_rows():
    result = p.parse_culture(pool())
    assert len(result["courses"]) == 2
    assert len({c["id"] for c in result["courses"]}) == 2
    assert all(c["credits"] is None for c in result["courses"])
    assert result["requirements"][0]["parent_id"].endswith("language-and-culture")
    gened = p.parse_gened(
        pool().replace(
            "Comprehensive Culture Course List", "Comprehensive General Education Elective List"
        )
    )
    assert [c["id"] for c in result["courses"]] == [c["id"] for c in gened["courses"]]
    assert "curriculum_audit" not in result and "last_verified" not in result


def test_changed_titles_are_observations_not_seed_replay():
    assert (
        p.parse_culture(pool().replace("Example Two", "Updated Title"))["courses"][1]["name"]
        == "Updated Title"
    )
    with pytest.raises(ValueError, match="column structure"):
        p.parse_culture(pool().replace("Number", "Credits"))


def test_overlap_applies_only_explicit_all_major_rows():
    html = """<h2>College of Science Not Recommended Course List</h2><p>Only one instance of an overlapping content course will apply toward graduation requirements</p>
    <table><tr><th>College Major / Subject</th><th>Course Area</th><th>Overlapping Courses</th></tr>
    <tr><td>All Majors</td><td>Synthetic physics</td><td>PHYS 11100, PHYS 22200 + 33300</td></tr>
    <tr><td>MA</td><td>Synthetic math</td><td>MA 11100, MA 22200</td></tr></table>"""
    rows = p.parse_overlap(html)["requirements"]
    assert len(rows) == 1 and "22200 + 33300" in rows[0]["summary"]
    assert not rows[0]["course_ids"] and rows[0]["kind"] == "note"


def test_experience_reads_source_numbers():
    html = """<h1>Language and Culture Experiential Guidelines</h1><p>Fall 2023 catalog terms and forward - maximum six credits of nine required credits. outside the United States; minimum eight (8) days containing a minimum 3-credit course.</p>"""
    assert "8 days" in p.parse_experience(html)["requirements"][0]["summary"]
    assert "9 days" in p.parse_experience(html.replace("(8)", "(9)"))["requirements"][0]["summary"]


@pytest.mark.parametrize(
    "url,parser,count", [(p.CULTURE_URL, p.parse_culture, 870), (p.GENED_URL, p.parse_gened, 1359)]
)
def test_optional_observed_cache(url, parser, count):
    path = Path(".cache/http") / (hashlib.sha256(url.encode()).hexdigest() + ".body")
    if not path.exists():
        pytest.skip("Optional ignored research cache unavailable")
    assert len(parser(path.read_text())["courses"]) == count
