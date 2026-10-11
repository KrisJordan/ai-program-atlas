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


def group(label, codes, credit="1/3"):
    return (
        '<article class="node--type-elective-group"><button><span>'
        + label
        + '</span></button><span class="field--name-field-elective-credits">'
        + credit
        + "</span>"
        + "".join(row(code, "Course " + code) for code in codes)
        + "</article>"
    )


def ai_degree_fixture():
    parts = [
        section(
            "<h3>Degree Distribution Requirements for the Artificial Intelligence Major</h3>one and only one concentration; at least 4/3 units"
        ),
        section(
            "<h4>Computer Science Foundation</h4>no more than 1/3 unit at the 1000 level",
            row("CS 2223", "Algorithms")
            + section("CS 1004 or CS 1005", row("CS 1004", "Intro"))
            + section("CS 1101 or CS 1102", row("CS 1101", "Intro"))
            + section("CS 2102, CS 2103, or CS 2119", row("CS 2119", "Apps")),
        ),
        section(
            "<h4>Mathematical Sciences Foundation</h4>",
            group("Both MA 2611 and MA 2612", ["MA 2611", "MA 2612"], "2/3")
            + group("One linear algebra", ["MA 2071"])
            + group("Calculus", [], "2/3").replace(
                "</article>",
                section("MA 1020 or MA 1021", row("MA 1021", "Calc1"))
                + section("MA 1022 or MA 1120", row("MA 1022", "Calc2"))
                + "</article>",
            ),
        ),
        section(
            "<h4>AI Core Courses</h4>Choose 8/3 units; at least 2/3 units at the 4000-level",
            group("AI Foundations: Three of DS 1010, DS 2010, DS 3010", ["DS 1010", "DS 2010", "DS 3010"])
            + group("AI Overview: One of", ["CS 4341"])
            + group("Machine Learning: At least one", ["CS 4342"])
            + group("Interaction and Reasoning: At least one", ["CS 3041"]),
        ),
        section("<h4>AI Ethics and Social Implications</h4>", row("CS 3043", "Ethics")),
        section("<h4>Natural or Engineering Science</h4>10 units program requirements"),
        section("<h4>Concentration</h4>6 distinct courses"),
        section("<h4>Disciplinary AI Electives</h4>"),
        section("<h4>Major Qualifying Project (MQP)</h4>"),
    ]
    return (
        '<main><h1>Artificial Intelligence Major</h1><div class="degree-class-details">'
        + "".join(parts)
        + "</div></main>"
    )


def test_wpi_ai_keeps_calculus_pairs_and_core_choice_bins():
    m = load("wpi-ai-bs")
    r = m.parse(ai_degree_fixture())
    rules = {x["id"]: x for x in r["requirements"]}
    assert rules["wpi-ai-bs-intro"]["count"] == 2
    calc = [x for x in r["requirements"] if x["parent_id"] == "wpi-ai-bs-math-3"]
    assert len(calc) == 2 and all(x["count"] == 1 for x in calc)
    assert rules["wpi-ai-bs-core"]["credits"] == pytest.approx(8 / 3)
    assert m.parse(ai_degree_fixture().replace("CS 4342", "CS 4349"))["courses"] != r["courses"]
    with pytest.raises(ValueError):
        m.parse(ai_degree_fixture().replace("AI Core Courses", "Research Core"))


def test_wpi_closed_foundation_sequence_needs_exact_source_rule_and_membership():
    m = load("wpi-ai-bs")
    rules = {x["id"]: x for x in m.parse(ai_degree_fixture())["requirements"]}
    fixed = rules["wpi-ai-bs-core-ai-foundations"]
    assert fixed["kind"] == "all"
    assert set(fixed["course_ids"]) == {"wpi-ds-1010", "wpi-ds-2010", "wpi-ds-3010"}
    # A changed selection rule cannot reuse the earlier manual closed-set judgment.
    with pytest.raises(ValueError, match="Closed required"):
        m.parse(ai_degree_fixture().replace("Three of DS", "Two of DS"))
    with pytest.raises(ValueError, match="Closed required"):
        m.parse(ai_degree_fixture().replace("DS 3010", "DS 3999"))


def business_fixture():
    parts = [
        section(
            "<h3>Mathematics and Science Requirements</h3>",
            group("Recommended: Calculus (2/3) - equivalents", ["MA 1021"], "2/3")
            + group("Recommended: Statistics (2/3) - equivalents", ["MA 2611"], "2/3")
            + group("Recommended: Linear Algebra (1/3) - equivalents", ["MA 2071"]),
        ),
        section("<h4>Computer Science</h4>", group("CS1004 or equivalent", ["CS 1004"])),
        section("<h4>Basic Science</h4>BB, CH, GE, PH"),
    ]
    for heading, count in [
        ("Business Foundation", 5),
        ("Technical and AI Foundation", 4),
        ("Analytics Foundation", 4),
    ]:
        parts.append(
            section(
                "<h4>" + heading + "</h4>",
                "".join(
                    group(str(i + 1) + ". Choose course", ["BUS " + str(1000 + i)])
                    for i in range(count)
                ),
            )
        )
    parts.extend(
        [
            section(
                "<h4>Business Analytics and Applied AI Electives</h4>Select a total of six electives"
            ),
            section(
                "Business Analytics Applications (Select at least 3)",
                row("FIN 3330", "Finance") + "<div>Minimum Units 12/3</div>",
            ),
            section(
                "Computing Technologies, Data and Mathematical Sciences (Maximum 3)",
                row("CS 2119", "Apps"),
            ),
            section("Business and Entrepreneurship (Maximum 2):", row("ETR 1100", "Enterprise")),
            section("<h4>MQP</h4>"),
            section(
                "<h4>Additional Notes:</h4>Each course may only count in one slot; may not double major in Marketing Analytics"
            ),
            section(
                "<h3>BS/MS Rules for Graduate Business Degree</h3>accepted into a graduate business program"
            ),
            section("<h3>Transfer Students and Transfer Credit</h3>prior written permission"),
        ]
    )
    return (
        '<main><h1>Business Analytics and Applied AI Major</h1><div class="degree-class-details">'
        + "".join(parts)
        + "</div></main>"
    )


def test_business_does_not_use_pool_sum_as_required_credit():
    m = load("wpi-business-analytics-applied-ai-bs")
    r = m.parse(business_fixture())
    rules = {x["id"]: x for x in r["requirements"]}
    assert rules[m.PROGRAM_ID + "-electives"]["count"] == 6
    apps = rules[m.PROGRAM_ID + "-electives-applications"]
    assert apps["count"] == 3 and apps["credits"] is None
    assert rules[m.PROGRAM_ID + "-electives-computing"]["kind"] == "note"
    assert rules[m.PROGRAM_ID + "-science"]["credits"] is None
    assert rules[m.PROGRAM_ID + "-math-0"]["kind"] == "choose_credits"
    with pytest.raises(ValueError):
        m.parse(business_fixture().replace("Select a total of six electives", "Select electives"))


def test_course_page_observes_advisory_background_and_unknown_credits():
    m = importlib.import_module("atlas.adapters.wpi-ai-bs.course_metadata")
    html = '<main><h1>CS 4342: Machine Learning</h1><span class="field--name-field-credits"><span class="field__item">1/3</span></span><div class="field--name-field-recommended"><div class="field__item">CS 2223</div></div></main>'
    r = m.parse_course(html, "wpi-ai-bs", "CS 4342", "Artificial Intelligence", "BS", "degree")
    c = r["courses"][0]
    assert "not a mandatory prerequisite" in c["prerequisites"] and c["description"] is None
    assert (
        m.parse_course(
            html.replace("1/3", "Variable"),
            "wpi-ai-bs",
            "CS 4342",
            "Artificial Intelligence",
            "BS",
            "degree",
        )["courses"][0]["credits"]
        is None
    )
    with pytest.raises(ValueError):
        m.parse_course(html, "wpi-ai-bs", "CS 4341", "Artificial Intelligence", "BS", "degree")


@pytest.mark.parametrize("pid", ["wpi-ai-bs", "wpi-business-analytics-applied-ai-bs"])
def test_wpi_degrees_keep_linked_requirements_unresolved(pid):
    d = json.loads((ROOT / "data/programs" / f"{pid}.json").read_text())
    validate_program(d)
    assert d["curriculum_status"] == "partial" and d["curriculum_audit"]["unresolved_requirements"]
