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
