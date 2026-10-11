"""Synthetic evidence tests for locally scoped concentration curricula."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug, ROOT / "atlas/adapters" / slug / "adapter.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ohio_fixture():
    def table(caption, rows):
        return (
            "<table><caption>"
            + caption
            + "</caption>"
            + "".join(
                "<tr>" + "".join("<td>" + str(x) + "</td>" for x in row) + "</tr>" for row in rows
            )
            + "</table>"
        )

    return (
        "<h1>BSCSE and BSCIS Specializations</h1><p>All CSE and BSCIS majors are required to take a specialization. Starred courses are only available to undergraduates by petition. Select at the time of application to the major. To change specializations, please contact your academic advisor.</p><details><summary>Artificial Intelligence</summary>"
        + table("Required Courses", [("CSE 3521", "Example AI", 3, "Example 100 or 200")])
        + table(
            "Pick Two of the Following Courses",
            [
                ("CSE 5523", "Example Learning", 3, "Example 300"),
                ("CSE 5914", "Example Project", 4, "Example 400"),
            ],
        )
        + "</details><details><summary>Other Track</summary>"
        + table("Required Courses", [("CSE 9999", "Wrong Track", 9, "")])
        + "</details>"
    )


def test_ohio_actual_credits_prerequisites_and_optional_capstone():
    d = load("ohio-state-ai-specialization").parse(ohio_fixture())
    assert len(d["courses"]) == 3
    assert d["courses"][-1]["credits"] == 4
    assert d["courses"][0]["prerequisites"] == "Example 100 or 200"
    assert "ohio-state-cse-5914" in d["requirements"][2]["course_ids"]
    assert d["requirements"][0]["credits"] is None
    assert d["requirements"][2]["count"] == 2
    with pytest.raises(ValueError, match="selection rule"):
        load("ohio-state-ai-specialization").parse(ohio_fixture().replace("Pick Two", "Pick Three"))
    with pytest.raises(ValueError, match="format"):
        load("ohio-state-ai-specialization").parse(ohio_fixture().replace("CSE 5914", "CSE 5914*"))


def test_ohio_parent_cis_ai_exception_and_observed_total():
    html = "<p>All BS CIS students must choose a specialization option. Overall, each student must have 16 credit hours of technical elective coursework, of which 9 hours must be in CSE. Linear Algebra is still required for the AI specialization as it is a prerequisite for CSE 3521.</p>"
    d = load("ohio-state-ai-specialization").parse_cis(html.replace("16 credit", "18 credit"))
    assert "18 technical-elective" in d["requirements"][0]["summary"]
    assert len(d["requirements"]) == 2
    assert all(r["parent_id"] is None for r in d["requirements"])


def rochester_fixture():
    return '<h2>BS in Computer Science</h2><p>BS students can complete a concentration. Complete five advanced four-credit courses numbered 200 or higher with at least three of these courses in the chosen concentration area. This does not include core or math courses listed above. No more than two core or major electives may be completed at other institutions unless they are taken as part of the University program.</p><details id="artificial-intelligence"><summary>Artificial Intelligence</summary><p>Approved courses for AI concentration:</p><ul><li>CSC 239: Example Learning</li><li>CSC 290: Example Systems</li></ul></details>'


def test_rochester_at_least_rule_is_not_five_ai_only():
    d = load("rochester-ai-concentration").parse(rochester_fixture())
    assert [r["count"] for r in d["requirements"][:3]] == [5, 3, 2]
    assert d["requirements"][2]["course_ids"] == []
    assert all(c["credits"] is None for c in d["courses"])
    assert "unused AI" in d["requirements"][1]["summary"]
    with pytest.raises(ValueError, match="exclusions changed"):
        load("rochester-ai-concentration").parse(
            rochester_fixture().replace("at least three", "at least four")
        )


def georgia_fixture():
    links = "".join(
        f'<a href="https://bulletin.uga.edu/example/{i}">{code} - Example {i}</a><br/>'
        for i, code in enumerate(
            [
                "CSCI 3360",
                "CSCI 4360/6360",
                "CSCI(PHIL) 4550/6550",
                "CSCI 4900/6900",
                "CSCI 4380/6380",
            ]
        )
    )
    return (
        "<h1>Artificial Intelligence Area of Emphasis</h1><p>Students will also earn a bachelor's degree in Computer Science; the degree will not be accredited by ABET.</p><h4>Specific Requirements:</h4><p>Students complete the following three courses: minimum of 2 courses from the following: "
        + links
        + " Subject to prior approval; the special topic must be related to artificial intelligence.</p><h4>Special considerations:</h4><p>These are NOT required: CSCI 4720 - Example Architecture CSCI 4050/4370 - Example Application CSCI 4730/4760 - Example Systems The student must still fulfill all other major requirements. Electives count toward the student's 12 hours of major electives.</p>"
    )


def test_georgia_combined_numbers_and_conditional_parent_waivers():
    d = load("georgia-ai-emphasis").parse(georgia_fixture().replace("minimum of 2", "minimum of 3"))
    assert (
        len(d["courses"]) == 5
    )  # paired levels are source-listed options, not two required courses
    assert d["requirements"][1]["count"] == 3
    assert d["requirements"][2]["count"] == 3 and "3" in d["requirements"][2]["title"]
    assert "CSCI 4720" in d["requirements"][4]["summary"]
    assert all(c["credits"] is None for c in d["courses"])
    with pytest.raises(ValueError, match="exceptions changed"):
        load("georgia-ai-emphasis").parse(georgia_fixture().replace("NOT required", "required"))


def test_concentration_complete_audits_and_unresolved_discoveries():
    from atlas.db import validate_program

    for slug in [
        "indiana-cs-ai-specialization",
        "ohio-state-ai-specialization",
        "rochester-ai-concentration",
        "georgia-ai-emphasis",
    ]:
        d = json.loads((ROOT / "data/programs" / f"{slug}.json").read_text())
        validate_program(d)
        assert d["curriculum_status"] == ("partial" if slug == "ohio-state-ai-specialization" else "complete")
        assert d["curriculum_audit"]["scope"] == "concentration"
        assert bool(d["curriculum_audit"]["unresolved_requirements"]) == (slug == "ohio-state-ai-specialization")
        assert d["curriculum_audit"]["metadata_gaps"]
    for slug in ["stony-brook-ai-data-science-specialization"]:
        d = json.loads((ROOT / "data/programs" / f"{slug}.json").read_text())
        validate_program(d)
        assert d["curriculum_status"] == "pending" and not d["courses"]
