"""Synthetic catalog layouts; no downloaded university pages in fixtures."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MSU = "michigan-state-university-artificial-intelligence-minor-minor"
TULANE = "tulane-university-of-louisiana-artificial-intelligence-minor-minor"


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug, ROOT / "atlas/adapters" / slug / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def msu_fixture():
    return """<span id="MainContent_lblProg">Minor in Artificial Intelligence</span>
    <div id="MainContent_divDesc">
    <p>Complete a minimum of 22 credits. Admission requires completion of Computer Science and Engineering 231 and 260 with a minimum grade in each of those two courses of 3.0.</p>
    <p>Available other than the Bachelor of Science Degree in Computer Science; Bachelor of Science Degree in Computer Engineering; Bachelor of Science Degree in Computational Data Science; Bachelor of Science Degree in Data Science; not available to students with a Minor in Computer Science.</p>
    <p>With the approval of the department and college courses may also be used to satisfy degree requirements. Students must apply to the Department of Computer Science and Engineering. Enrollment may be limited. Calculus I is an implied component.</p>
    <table><tr><td>All of the following courses (19 credits)</td></tr>
    <tr><td></td><td>CSE</td><td>231</td><td>Example Programming</td><td>4</td></tr>
    <tr><td>One of the following courses (3 credits)</td></tr>
    <tr><td></td><td>CSE</td><td>440</td><td>Example AI</td><td>3</td></tr></table></div>"""


def test_msu_reads_table_values_and_entrance_grade():
    data = load(MSU).parse(
        msu_fixture().replace("of 3.0", "of 3.5").replace("Example AI", "New AI")
    )
    assert data["courses"][-1]["name"] == "New AI"
    assert data["requirements"][2]["count"] == 1
    assert "3.5" in data["requirements"][3]["summary"]
    assert data["requirements"][0]["credits"] == 22
    assert data["curriculum_status"] == "partial"  # only reviewer certifies complete
    with pytest.raises(ValueError, match="rules changed"):
        load(MSU).parse(
            msu_fixture().replace("Calculus I is an implied component", "No preparation")
        )


def test_msu_general_policy_requires_actual_rules():
    html = """<div id="s261"><h5>Selecting a Minor</h5><p>Awards are awarded in conjunction with the primary undergraduate degree; exclude the same name represented by the minor. The minimum number of credits for a minor is 15. Unique credits do not count for a course taken to satisfy another university, college, or major requirement.</p></div>"""
    result = load(MSU).parse_policy(html.replace("is 15", "is 18"))
    assert "18" in result["requirements"][0]["summary"]
    assert result["requirements"][0]["parent_id"] is None
    with pytest.raises(ValueError):
        load(MSU).parse_policy("<h5>Selecting a Minor</h5>")


def tulane_fixture():
    def group(title, credits):
        return f'<tr class="areaheader"><td><span class="courselistcomment">{title}</span></td><td class="hourscol">{credits}</td></tr>'

    def row(code, credits):
        return f'<tr><td><a class="code" href="/example">{code}</a></td><td>Example Course</td><td class="hourscol">{credits}</td></tr>'

    return (
        '<h1>University Catalog 2026-2027</h1><h1>Artificial Intelligence Minor</h1><h2>2026-2027 Edition</h2><div id="requirementstextcontainer"><p>The minor comprises of 5 courses, requiring 16 credits.</p><table class="sc_courselist">'
        + group("Algorithms", 4)
        + row("CMPS 2200", 4)
        + group("AI/ML Foundations", 6)
        + row("CMPS 3140", 3)
        + row("CMPS 3240", 3)
        + group("AI/ML Electives (choose two)", 6)
        + row("CMPS 3160", "")
        + "</table><p>6000-level sections for these courses are allowed.</p><h3>Academic Prerequisites</h3><ul><li>CMPS 1500 Example First (4 c.h.) or CMPS 1100 Example Alternative (3 c.h.)</li><li>CMPS 1600 Example Second (4 c.h.)</li><li>CMPS/MATH 2170 Example Discrete (3 c.h.)</li></ul>"
        + "<p>Complete these before declaring the minor; cumulative GPA of 2.5 or above. CS majors: only one course may overlap (CMPS 2200); 4 (12 CR) extra courses. A reused course may not fulfill the AI/Algorithms requirement. Get advisor's and the departmental chair's signatures, then submitted to the Advising Office.</p></div>"
    )


def test_tulane_preserves_prerequisite_alternatives_and_unknown_elective_credit():
    data = load(TULANE).parse(tulane_fixture())
    courses = {c["code"]: c for c in data["courses"]}
    assert courses["CMPS 3160"]["credits"] is None
    assert courses["CMPS 1100"]["credits"] == 3
    assert courses["CMPS 1500"]["credits"] == 4
    assert courses["CMPS/MATH 2170"]["credits"] == 3
    prereq = next(r for r in data["requirements"] if r["id"].endswith("-prerequisites"))
    assert prereq["parent_id"] is None  # never add preparation to 16-credit total
    choice = next(r for r in data["requirements"] if r["kind"] == "alternative")
    assert choice["count"] == 1 and len(choice["course_ids"]) == 2
    assert data["catalog_year"] == "2026-2027"
    with pytest.raises(ValueError, match="policy changed"):
        load(TULANE).parse(
            tulane_fixture().replace("only one course may overlap", "two courses may overlap")
        )


def test_reviewed_batch_status_and_evidence():
    from atlas.db import validate_program

    for slug, status in [
        (MSU, "partial"),
        (TULANE, "complete"),
        ("stanford-ai-track", "complete"),
    ]:
        data = json.loads((ROOT / "data/programs" / f"{slug}.json").read_text())
        validate_program(data)
        assert data["curriculum_status"] == status
        assert bool(data["curriculum_audit"]["unresolved_requirements"]) == (status != "complete")


def test_stanford_policy_observation_never_implies_course_inventory():
    html = """<h1>BS | Program Sheets</h1><h3>Artificial Intelligence (AI)</h3>
    <p>Use the year they matriculated; not allowed to mix requirements; there is no double-counting.
    A letter grade except Spring 2019-20 and Autumn 2020-21 through Summer 2020-21.
    Submit at least one quarter prior, with approved program sheets. Students must meet all the requirements for one CS track and may petition for exceptions or deviations.</p>"""
    result = load("stanford-ai-track").parse_sheets(html)
    assert result["curriculum_status"] == "partial"
    assert "courses" not in result and "curriculum_audit" not in result
    assert len(result["requirements"]) == 6
    with pytest.raises(ValueError, match="policies changed"):
        load("stanford-ai-track").parse_sheets(
            html.replace("there is no double-counting", "double-counting allowed")
        )
    degree = "<h1>BS | Degree Requirements</h1><p>minimum 2.0 GPA across all Engineering Fundamentals, CS Core, Depth, and Senior Project courses combined. Depth section has strict minimum requirements for both the number of courses and units.</p>"
    observed = load("stanford-ai-track").parse_degree_policies(degree.replace("2.0 GPA", "2.5 GPA"))
    assert "2.5 GPA" in observed["requirements"][0]["summary"]
