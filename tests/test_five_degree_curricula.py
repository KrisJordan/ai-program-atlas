"""Synthetic curriculum fixtures for the NJIT/Lehigh/Drexel degree batch."""

import importlib.util
import json
from pathlib import Path

import pytest

from atlas.db import validate_program
from atlas.requirements import validate_requirements

ROOT = Path(__file__).resolve().parents[1]
NJIT = "new-jersey-institute-of-technology-business-with-ai-bs-degree"


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / "atlas/adapters" / pid / "adapter.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_njit_observed_plan_preserves_zero_and_open_slots():
    html = '<h1>University Catalog</h1><h1>Business with AI</h1><p>(120 credit minimum)</p><table class="sc_plangrid"><tr class="plangridyear"><th>First Year</th></tr><tr class="plangridterm"><th>1st Semester</th></tr><tr><td class="codecol"><a class="code" href="/search/?P=FYS%20SEM">FYS SEM</a></td><td class="titlecol">Example Seminar</td><td class="hourscol">0</td></tr><tr><td class="codecol" colspan="2">Example GER</td><td class="hourscol">3</td></tr><tr class="plangridsum"><td>Term credits</td><td class="hourscol">3</td></tr></table>'
    d = load(NJIT).parse(html)
    assert d["courses"][0]["credits"] == 0
    assert d["requirements"][-1]["kind"] == "note"
    assert d["requirements"][-1]["credits"] == 3
    assert d["requirements"][-1]["parent_id"] == d["requirements"][1]["id"]
    assert "curriculum_audit" not in d and "last_verified" not in d
    with pytest.raises(ValueError, match="minimum"):
        load(NJIT).parse(html.replace("(120 credit minimum)", ""))
    with pytest.raises(ValueError, match="credit"):
        load(NJIT).parse(html.replace(">0</td>", ">unknown</td>"))


def test_reviewed_five_degree_records_validate():
    for pid in [
        NJIT,
        "lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree",
        "drexel-ai-ml-bs",
        "delaware-ai-engineering-major",
        "stevens-institute-of-technology-artificial-intelligence-bs-degree",
    ]:
        d = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
        validate_program(d)
        validate_requirements(d)
        if d.get("curriculum_audit"):
            assert d["curriculum_status"] == "partial"
            assert d["curriculum_audit"]["unresolved_requirements"]


def test_lehigh_group_credits_and_ambiguous_titles():
    pid = "lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree"

    def row(values):
        return "<tr>" + "".join("<td>" + v + "</td>" for v in values) + "</tr>"

    def table(label, rows, footer=""):
        return (
            '<table aria-label="'
            + label
            + '">'
            + footer
            + "<tbody>"
            + "".join(row(v) for v in rows)
            + "</tbody></table>"
        )

    html = "<p>Bachelor of Science (BS) in Artificial Intelligence, Machine Learning, and Data Science</p>"
    html += table(
        "Degree Requirements table",
        [
            ["Required Technical Courses"],
            ["CSE 252", "Computing Ethics (Does not count toward HSS)", "3"],
            ["AI, ML and DS Depth: At least 12 credits", "12"],
            ["AI, ML and DS Electives: At least 21 credits", "21"],
            ["Required Mathematics and Sciences"],
            ["MATH 205", "Example Linear Methods", "3-4"],
            ["or MATH 241", "Example Algebra", ""],
            ["or MATH 242", "Other Algebra", ""],
            ["PHY 011 & PHY 012", "Example Lecture and Example Lab", "5"],
            ["HSS"],
            ["ECO 001", "Introduction to Engineering Practice", "4"],
        ],
        "<tfoot><tr><td>Total Minimum Required Credits 130-131</td></tr></tfoot>",
    )
    html += table(
        "AI, ML, and DS Depth Approved Courses table", [["CSE 323", "Example Vision", "3"]]
    )
    html += table("Approved AI, ML, and DS Electives table", [["ISE 230", "Example Models", "3"]])
    d = load(pid).parse(html)
    assert all(c["credits"] is None for c in d["courses"] if c["code"].startswith(("MATH", "PHY")))
    assert all(c["code"] != "ECO 001" for c in d["courses"])
    assert any(r["kind"] == "alternative" and len(r["course_ids"]) == 3 for r in d["requirements"])
    with pytest.raises(ValueError, match="ambiguous HSS"):
        load(pid).parse(
            html.replace("Introduction to Engineering Practice", "Corrected Course Title")
        )
    with pytest.raises(ValueError, match="range changed"):
        load(pid).parse(html.replace("130-131", "132"))


def drexel_fixture():
    def area(name):
        return '<tr class="areaheader"><td>' + name + "</td></tr>"

    def comment(label, credit=""):
        return '<tr><td colspan="2">' + label + '</td><td class="hourscol">' + credit + "</td></tr>"

    def course(codes, names, credit="", other=False):
        return (
            "<tr"
            + (' class="orclass"' if other else "")
            + '><td class="codecol">'
            + "<br/> &amp; ".join(
                '<a href="/search/?P=' + c.replace(" ", "%20") + '">' + c + "</a>" for c in codes
            )
            + "</td><td>"
            + "<br/>and ".join(names)
            + '</td><td class="hourscol">'
            + credit
            + "</td></tr>"
        )

    rows = (
        area("Core Requirements")
        + course(["CS 171"], ["Example Programming"], "3.0")
        + course(["ENGR 131"], ["Example Alternative"], other=True)
    )
    rows += (
        area("Elective Requirements")
        + comment(
            "Select 8 courses from the list below. For sequences, each course may count separately provided that it is not already used to satisfy another degree requirement.",
            "24.0",
        )
        + course(["CS 281", "CS 283"], ["Example Architecture", "Example Systems"])
        + course(["CS 417"], ["Example Learning"])
        + course(["ECE 417"], ["Example Learning"], other=True)
    )
    rows += (
        area("Project Requirements")
        + comment("Select one of the following sequences:", "6.0")
        + course(
            ["CI 101", "CI 102", "CI 103"],
            ["Example Design A", "Example Design B", "Example Design C"],
        )
    )
    rows += (
        area("Mathematics Requirements")
        + comment("Select one of the following sequences:", "11.0-14.0")
        + course(
            ["MATH 121", "MATH 122", "MATH 200"],
            ["Example Calculus A", "Example Calculus B", "Example Calculus C"],
        )
        + course(["MATH 201"], ["Example Algebra"], "3.0-4.0")
        + course(["ECE 231"], ["Other Algebra"], other=True)
    )
    rows += (
        area("Science Requirements")
        + comment("Select from the following 100-400 level courses:", "20.0")
        + comment("Any BIO (Bioscience)")
    )
    rows += (
        area("Arts & Humanities Requirements")
        + course(["PHIL 311"], ["Example Ethics"], "3.0")
        + area("University Requirements")
        + course(["CIVC 101"], ["Example Civic"], "1.0")
        + area("Free Electives")
        + comment("Select any unrestricted 099-499 courses", "46.0-50.0")
        + comment("Total Credits", "180.0")
    )
    policies = "<p>Only one of the two High Performance Computing sequences may be selected. MATH 200 can use any other MATH course not used elsewhere. Pass three writing-intensive courses after their freshman year. Two writing-intensive courses must be in a student’s major. Transfer students need to meet with an academic advisor.</p>"
    return (
        '<h1>Artificial Intelligence &amp; Machine Learning</h1><p>Degree Awarded: Bachelor of Science (BS)</p><div id="degreerequirementstextcontainer"><table class="sc_courselist">'
        + rows
        + "</table>"
        + policies
        + "</div>"
    )


def test_drexel_nested_sequences_and_alternatives():
    d = load("drexel-ai-ml-bs").parse(drexel_fixture())
    pool = next(r for r in d["requirements"] if r["kind"] == "choose_courses")
    assert pool["count"] == 8 and len(pool["course_ids"]) == 4
    design = next(
        r for r in d["requirements"] if r["title"] == "Project Requirements sequence choice"
    )
    sequence = next(r for r in d["requirements"] if r["parent_id"] == design["id"])
    assert design["kind"] == "alternative" and sequence["kind"] == "all"
    assert all(c["credits"] is None for c in d["courses"] if c["code"].startswith("CI "))
    algebra = next(r for r in d["requirements"] if "drexel-math-201" in r["course_ids"])
    assert "3.0-4.0" in algebra["summary"]
    with pytest.raises(ValueError, match="policy changed"):
        load("drexel-ai-ml-bs").parse(drexel_fixture().replace("not already used", "already used"))
    with pytest.raises(ValueError, match="180-credit"):
        load("drexel-ai-ml-bs").parse(drexel_fixture().replace("180.0", "181.0"))


def delaware_fixture():
    html = "<h1>Artificial Intelligence Engineering BS</h1><h2>Sample Plan of Study</h2>"
    rows = [
        "CISC 106 – Example Computing",
        "PHYS 207 & 227 – Example Physics &amp; Lab",
        "ELEG 405 or 625 – Example Learning or Example Data",
        "ELEG 499 – Example Design",
    ]
    for year, row in zip(["First Year", "Second Year", "Third Year", "Fourth Year"], rows):
        html += (
            '<div class="et_pb_toggle"><h5>'
            + year
            + "</h5><ul><li>"
            + row
            + "</li><li>Example Elective</li></ul></div>"
        )
    return html


def test_delaware_sample_is_not_full_degree_inventory():
    d = load("delaware-ai-engineering-major").parse(delaware_fixture())
    assert d["award_level"] == "BS" and d["curriculum_status"] == "partial"
    assert len(d["courses"]) == 4
    assert all(c["credits"] is None for c in d["courses"])
    assert any(r["kind"] == "alternative" for r in d["requirements"])
    assert "sample" in d["requirements"][0]["title"]
    with pytest.raises(ValueError, match="BS heading"):
        load("delaware-ai-engineering-major").parse(
            delaware_fixture().replace("Engineering BS", "Engineering MS")
        )
