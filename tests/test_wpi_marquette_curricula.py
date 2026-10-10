"""Synthetic fixtures exercise choices, unit boundaries and fail-closed source parsing."""

import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]


def load(pid):
    return importlib.import_module("atlas.adapters." + pid + ".adapter")


def row(code, title, credit="1/3"):
    return f'<article class="node--type-class"><div class="col-3"><a href="/course/{code}">{code}</a></div><div class="col-7">{title}</div><span class="field--name-field-credits">{credit}</span></article>'


def section(desc, courses=""):
    return f'<div class="paragraph--type--degree-section"><div class="field--name-field-degree-section-description">{desc}</div>{courses}</div>'


def wpi_fixture():
    return (
        '<main><h1>Artificial Intelligence Major with Concentration in Advanced AI Methods and Technologies</h1><div class="degree-class-details"><p>Associated Degree Artificial Intelligence Major</p><p>Students must take 6 courses beyond those taken to meet the core AI requirements.</p>'
        + section("Choose at least three courses from:", row("CS 4341", "AI"))
        + section("Choose remaining courses from:", row("CS 2301", "Systems"))
        + section(
            "Or choose remaining course from: Advanced undergraduate students can take graduate CS and DS courses from the Core AI Bins of the MS in AI degree."
        )
        + section("Note: Only one of CS 2301 or CS 2303 may be used for the degree requirements.")
        + "</div></main>"
    )


def test_wpi_local_choices_fraction_and_no_review_replay():
    m = load("wpi-ai-advanced-methods-concentration")
    r = m.parse(wpi_fixture())
    assert r["requirements"][0]["count"] == 6
    assert r["requirements"][1]["count"] == 3
    assert r["courses"][0]["credits"] == pytest.approx(1 / 3)
    assert r["courses"][0]["credit_unit"] == "units"
    assert (
        r["curriculum_status"] == "partial"
        and "curriculum_audit" not in r
        and "last_verified" not in r
    )
    assert m.parse(wpi_fixture().replace("CS 4341", "CS 4349"))["courses"][0]["code"] == "CS 4349"
    with pytest.raises(ValueError):
        m.parse(wpi_fixture().replace("Core AI Bins", "All courses"))


def test_wpi_grad_pool_restricts_disciplines_and_retains_units():
    html = (
        '<main><h1>M.S. in Artificial Intelligence</h1><div class="degree-class-details">'
        + section(
            "<h3>Core Courses:</h3>five core MS-AI bins",
            row("CS 534", "AI", "3")
            + row("RBE 550", "Robotics", "3")
            + row("ECE 556/CS 556/DS 556", "Deep Learning", "3"),
        )
        + "</div></main>"
    )
    r = load("wpi-ai-advanced-methods-concentration").parse_graduate(html)
    assert [c["code"] for c in r["courses"]] == ["CS 534", "ECE 556/CS 556/DS 556"]
    assert all(c["credit_unit"] == "unknown" and c["credits"] == 3 for c in r["courses"])


def mqrow(code, title, credit="", indent=False):
    return (
        f'<tr><td class="codecol">'
        + ('<div class="blockindent">' if indent else "")
        + f'<a href="/course/{code}">{code}</a>'
        + ("</div>" if indent else "")
        + f"</td><td>{title}</td><td>{credit}</td></tr>"
    )


def comment(label, credit=""):
    return f"<tr><td>{label}</td><td>{credit}</td></tr>"


def marquette_fixture():
    return (
        '<main><h1>Applied Artificial Intelligence in Business, Major</h1><div id="requirementstextcontainer">must pair this major with an additional primary major<table class="sc_courselist">'
        + comment("Upper Division Business Electives", "15")
        + mqrow("BUAD 2001", "Intro", "3")
        + comment("Complete requirements of the Disruptive Tech or Machine Learning Focus", "6")
        + comment("Complete two of the following electives:", "6")
        + mqrow("FINA 4031", "Finance", "", True)
        + mqrow("MARK 4065", "Marketing", "", True)
        + mqrow("OSCM 4065", "Supply", "", True)
        + mqrow("INSY 4180", "Ethics", "3")
        + '<tr class="listsum"><td>Total Credit Hours:</td><td>33</td></tr></table><table class="sc_courselist">'
        + comment("Choose one of the following focus areas:")
        + comment("Disruptive Tech")
        + mqrow("FINA 4075", "FinTech", "3")
        + mqrow("AIM 4410", "Opportunity", "3")
        + comment("Or")
        + comment("Machine Learning")
        + mqrow("BUAN 3065", "Predictive", "3")
        + mqrow("BUAN 3066", "Prescriptive", "3")
        + "</table></div></main>"
    )


def test_marquette_nested_focus_shared_total_and_unknown_option_credits():
    m = load("marquette-applied-ai-business-major")
    r = m.parse(marquette_fixture())
    rules = {x["id"].split(m.PROGRAM_ID + "-")[1]: x for x in r["requirements"]}
    assert rules["total"]["credits"] == 33 and rules["primary-shared"]["credits"] == 15
    assert rules["electives"]["count"] == 2 and len(rules["electives"]["course_ids"]) == 3
    assert rules["focus"]["kind"] == "alternative"
    assert len(rules["focus-machine-learning"]["course_ids"]) == 2
    assert next(c for c in r["courses"] if c["code"] == "MARK 4065")["credits"] is None
    assert "curriculum_audit" not in r
    assert (
        m.parse(marquette_fixture().replace("BUAN 3066", "BUAN 3069"))["courses"][-1]["code"]
        == "BUAN 3069"
    )
    with pytest.raises(ValueError):
        m.parse(marquette_fixture().replace("Complete two", "Complete three"))


def test_marquette_policy_change_requires_review():
    m = load("marquette-applied-ai-business-major")
    r = m.parse_policy("<main><h1>Grade Minimums</h1><p>grade of C or higher</p></main>", "grades")
    assert len(r["requirements"]) == 1
    with pytest.raises(ValueError):
        m.parse_policy("<main><h1>Grade Minimums</h1><p>grade of D or higher</p></main>", "grades")


@pytest.mark.parametrize(
    "pid", ["wpi-ai-advanced-methods-concentration", "marquette-applied-ai-business-major"]
)
def test_reviewed_local_inventory_scope(pid):
    d = json.loads((ROOT / "data/programs" / f"{pid}.json").read_text())
    validate_program(d)
    assert (
        d["curriculum_status"] == "complete" and d["curriculum_audit"]["scope"] == d["program_kind"]
    )
    assert not d["curriculum_audit"]["unresolved_requirements"]
