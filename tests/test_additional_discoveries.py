import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug, ROOT / "atlas" / "adapters" / slug / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def columbia_fixture():
    def row(code, title, alternative=False):
        return f'<tr class="{"orclass" if alternative else "regular"}"><td class="codecol">{code}</td><td>{title}</td><td class="hourscol"></td></tr>'

    def table(rows):
        return "<table>" + "".join(rows) + "</table>"

    choice = "<tr><td>Choose one:</td></tr>"
    return (
        "<h3>\u200bMinor in Artificial Intelligence</h3><p>The minor consists of 6 courses.</p>"
        + table(
            [
                row("MATH UN2015", "Example Math"),
                row("COMS W2132", "Example Coding"),
                row("IEOR E2000", "Example Data", True),
                row("IEOR E2000", "Example Data"),
            ]
        )
        + "<h4>AI Requirement:</h4>"
        + table([row("COMS W4701", "Example AI")])
        + "<h4>Ethics Requirement:</h4>"
        + table([choice, row("COMS W4710", "Example Ethics")])
        + "<h4>AI Elective:</h4>"
        + table(
            [
                choice,
                "<tr><td>Any COMS 47XX course</td></tr>",
                "<tr><td>Relevant COMS 4995/6998 course</td></tr>",
                row("STAT GU4243", ""),
            ]
        )
        + "<p>MATH UN2015 allows a separate linear algebra course and a separate probability course.</p>"
        + "<p>Students in majors offered solely or jointly by CS are not eligible.</p>"
    )


def test_columbia_preserves_duplicate_ambiguity_and_blank_points():
    parse = load("columbia-ai-minor").parse
    data = parse(columbia_fixture())
    assert data["program_kind"] == "minor" and data["curriculum_status"] == "partial"
    assert len([c for c in data["courses"] if c["code"] == "IEOR E2000"]) == 1
    assert all(c["credits"] is None for c in data["courses"])
    assert next(c for c in data["courses"] if c["code"] == "STAT GU4243")["name"].endswith(
        "(title not supplied)"
    )
    assert any(r["id"].endswith("duplicate-source-row") for r in data["requirements"])
    assert any(r["id"].endswith("broad-electives") for r in data["requirements"])
    assert "curriculum_audit" not in data and "last_verified" not in data
    assert (
        parse(columbia_fixture().replace("6 courses", "7 courses"))["requirements"][0]["count"] == 7
    )
    with pytest.raises(ValueError):
        parse("<h3>Minor in Artificial Intelligence</h3><p>Six courses.</p>")
    with pytest.raises(ValueError, match="Broad elective"):
        parse(columbia_fixture().replace("47XX", "48XX"))


def test_stanford_formal_concentration_not_standalone_bs():
    parse = load("stanford-ai-track").parse
    row = parse(
        "<main><h3>Artificial Intelligence</h3><p>Topics in the AI concentration include reasoning.</p></main>"
    )
    assert row["award_level"] == row["program_kind"] == "concentration"
    assert row["title"].endswith("(CS BS track)")
    assert "last_verified" not in row
    with pytest.raises(ValueError):
        parse("<main><h3>Artificial Intelligence</h3><p>An optional area of interest.</p></main>")


def test_additional_survey_integrity():
    rows = json.loads((ROOT / "data/surveys/national-additional.json").read_text())
    cohort = {i["id"] for i in json.loads((ROOT / "data/cohort.json").read_text())["institutions"]}
    assert len(rows) == len({r["institution_id"] for r in rows}) == 25
    assert all(r["institution_id"] in cohort and r["sources"] for r in rows)
    assert all(r["status"] != "no_qualifying_program_found" for r in rows)
    confirmed = {r["institution_id"]: r for r in rows if r["status"] == "confirmed"}
    assert {
        "stanford-university", "columbia-university",
        "university-of-virginia", "villanova-university",
    } <= set(confirmed)
    assert all(r["discoveries"] and r["checked_at"] and r["sources"] for r in confirmed.values())
    for pid in ["columbia-ai-minor", "stanford-ai-track"]:
        p = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
        assert p["curriculum_status"] == "partial"
        assert p["curriculum_audit"]["unresolved_requirements"]
        from atlas.db import validate_program

        validate_program(p)
