"""Concentration alternatives and linked policy boundaries, using invented small fixtures."""

import importlib
import pytest

c = importlib.import_module("atlas.adapters.wpi-ai-bs.concentrations")
p = importlib.import_module("atlas.adapters.wpi-ai-bs.degree_policies")


def row(code, name="Synthetic course", credits="1/3"):
    return f'<article class="node--type-class"><div class="col-3"><a href="/course">{code}</a></div><div class="col-7">{name}</div><span class="field--name-field-credits">{credits}</span></article>'


def section(label, content):
    return (
        '<div class="paragraph--type--degree-section"><div class="field--name-field-degree-section-description">'
        + label
        + "</div>"
        + content
        + "</div>"
    )


def doc(key, content, extra=""):
    return (
        "<main><h1>Artificial Intelligence Major with Concentration in "
        + c.CONCENTRATIONS[key][0]
        + '</h1><div class="degree-class-details">Associated Degree Artificial Intelligence Major. 6 courses. '
        + extra
        + content
        + "</div></main>"
    )


def group(label, content):
    return (
        '<article class="node--type-elective-group"><button><span>'
        + label
        + "</span></button>"
        + content
        + "</article>"
    )


def test_optimization_required_probability_is_one_alternative_not_both():
    html = doc(
        "optimization",
        section(
            "Required Foundational Courses (must take both; 2/3 units):",
            row("MA 1024") + group("Either MA 2621 or MA 2631", row("MA 2621") + row("MA 2631")),
        )
        + section("Choose one course from:", row("MA 2073")),
        "beyond those taken to meet the core AI requirements",
    )
    r = c.parse(html, "optimization")
    required = next(x for x in r["requirements"] if x["kind"] == "all")
    assert required["course_ids"] == ["wpi-ma-1024"]
    alt = next(x for x in r["requirements"] if x["parent_id"] == required["id"])
    assert alt["count"] == 1 and len(alt["course_ids"]) == 2
    assert (
        c.parse(html.replace("MA 2073", "MA 2079"), "optimization")["courses"][-1]["code"]
        == "MA 2079"
    )


def test_experience_design_includes_named_graduate_wrappers_and_level_floor():
    grad = group(
        "IMGD 5100: Synthetic design",
        '<span class="field--name-field-elective-credits">1/2</span><p>See Graduate Catalog</p>',
    )
    html = doc(
        "experience",
        section("Choose three courses in Experience Design from:", row("CS 3041") + grad),
        "At least 2 courses must be at the 3000-level or higher",
    )
    r = c.parse(html, "experience")
    g = next(x for x in r["courses"] if x["code"] == "IMGD 5100")
    assert g["credits"] == 0.5 and g["credit_unit"] == "units"
    assert any(x["id"].endswith("-advanced") for x in r["requirements"])
    with pytest.raises(ValueError):
        c.parse(html.replace("At least 2", "At least 3"), "experience")


def test_special_topics_extend_minimum_pool_conditionally_and_keep_unknown_credit():
    html = doc(
        "social-policy",
        section("Required (must take both):", row("PSY 1500") + row("PSY 2503"))
        + section("Choose at least three from:", row("PSY 1400"))
        + section(
            "Including from Special Topics Course, when relevant to BS-AI degree:",
            row("ENV 4800", credits=""),
        ),
        "At least one course must be at the 4000 level",
    )
    r = c.parse(html, "social-policy")
    minimum = next(x for x in r["requirements"] if x["count"] == 3)
    assert "wpi-env-4800" in minimum["course_ids"] and "relevant" in minimum["summary"]
    assert next(x for x in r["courses"] if x["code"] == "ENV 4800")["credits"] is None


def test_robotics_open_pool_preserves_exclusion_without_inventing_course_inventory():
    html = doc(
        "robotics",
        section("Choose one course in Controls:", row("ES 3011"))
        + section(
            "Choose one course from:",
            "An RBE course at the 3000-level or above, including graduate courses. RBE 3100 does not count towards this requirement.",
        ),
    )
    r = c.parse(html, "robotics")
    assert len(r["courses"]) == 1
    assert any("except RBE3100" in x["summary"] for x in r["requirements"])
    with pytest.raises(ValueError):
        c.parse(html.replace("RBE 3100 does not count", "RBE 3100 counts"), "robotics")


def test_policy_conversion_is_source_gated_and_remains_partial():
    html = "<main><h1>Graduate Courses</h1><p>1 graduate credit = 1/6 undergraduate unit</p></main>"
    r = p.parse(html, "wpi-ai-bs", "Artificial Intelligence", "graduate")
    assert r["curriculum_status"] == "partial" and "curriculum_audit" not in r
    with pytest.raises(ValueError):
        p.parse(html.replace("1/6", "1/5"), "wpi-ai-bs", "Artificial Intelligence", "graduate")


def test_degree_options_extract_actual_business_prohibited_combinations():
    html = "<main><h1>Degree Options</h1><p>two units of integrated academic study plus an MQP; must not overlap with credit earned for another additional degree designation by more than one unit; No student shall complete more than two undergraduate majors; One interdisciplinary project of at least 4/3 units; a single project bearing at least one unit credit</p><ul><li>Business Analytics &amp; Applied AI and Test Discipline</li></ul></main>"
    r = p.parse(
        html, "wpi-business-analytics-applied-ai-bs", "Business Analytics & Applied AI", "options"
    )
    assert "Test Discipline" in r["requirements"][-1]["summary"]
    assert (
        "Test Discipline"
        not in p.parse(
            html.replace("Test Discipline", "New Discipline"),
            "wpi-business-analytics-applied-ai-bs",
            "Business Analytics & Applied AI",
            "options",
        )["requirements"][-1]["summary"]
    )
