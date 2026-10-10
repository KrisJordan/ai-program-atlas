"""Synthetic documents model official markup without storing source-page copies."""

import importlib
import json
from pathlib import Path

import pytest

NAMES = ["cmu_bs", "cmu_minor", "cmu_additional", "penn_bse", "penn_business", "penn_cs"]


def adapter(name):
    return importlib.import_module("atlas.adapters." + name + ".adapter")


def row(code="07-280", name="Synthetic AI core", credits="12", other=False):
    return f'<tr{" class=orclass" if other else ""}><td class="codecol"><a href="/search/?P={code}">{code}</a></td><td>{name}</td><td class="hourscol">{credits}</td></tr>'


def table(rows, label="All of the following:"):
    return f'<table class="sc_courselist"><td>{label}</td><tbody>{rows}</tbody></table>'


def cmu_fixture(name):
    if name == "cmu_minor":
        return minor_fixture()
    if name == "cmu_additional":
        return additional_fixture()
    headings = {
        "cmu_bs": (
            "Artificial Intelligence, B.S.",
            ["Computer Science", "Artificial Intelligence", "Ethics Course"],
        ),
        "cmu_minor": (
            "Artificial Intelligence, Minor",
            ["Required Core Courses", "Technical Electives", "Societal Aspects of AI"],
        ),
        "cmu_additional": (
            "Artificial Intelligence, Additional Major",
            [
                "Computer Science Core",
                "Artificial Intelligence Core",
                "AI Cluster Electives",
                "Ethics and Human Cognition",
            ],
        ),
    }
    title, sections = headings[name]
    return (
        "<div>2030-2031 Catalog</div><main><h1>"
        + title
        + "</h1>"
        + "".join("<h4>" + s + "</h4>" + table(row()) for s in sections)
        + "</main>"
    )


def block(title, body):
    return f'<div class="accordion-item"><h2><button>{title}</button></h2><div class="accordion-body">{body}</div></div>'


def penn_bse_fixture():
    return (
        "<h1>B.S.E. in AI Curriculum</h1>"
        + block("Computing (5 CUs)", "<ul><li>CIS 1200: Synthetic computing</li></ul>")
        + block(
            "AI Core (6 CUs)",
            "<p>Students choose at least one course unit from each of the following six categories:</p>"
            + "".join(
                f"<h5>Area {i}</h5><ul><li>CIS {4200 + i}: Synthetic AI {i}</li></ul>"
                for i in range(6)
            ),
        )
        + block("AI Electives (6 CUs)", "<ul><li>ESE 5000: Synthetic elective</li></ul>")
    )


def business_fixture():
    return "<h1>Artificial Intelligence for Business Joint Concentration</h1><h3>Requirements for Concentration</h3><p>The concentration in Artificial Intelligence for Business requires a total of 4 CU.</p><ul><li>Courses taken on a pass/fail basis cannot be counted.</li><li>A maximum of 1 CU of an Independent Study Project requires faculty advisor approval.</li><li>A maximum of 1 CU outside of Wharton requires faculty advisor approval.</li></ul><h4>Pillar F</h4><p>STAT 4230: Synthetic foundations (1 CU)</p><h4>Pillar I</h4><p>LGST 2420: Synthetic ethics (0.5 CU)</p><h4>Pillar F – Complete an additional 1 CU:</h4><p>STAT 4990: Synthetic elective</p><h4>Pillar I – Complete an additional 1.5 CU:</h4><p>MGMT/OIDD 3130: Synthetic crosslist</p>"


def minor_fixture():
    comments = lambda label: (
        '<tr><td><span class="courselistcomment">' + label + "</span></td></tr>"
    )
    pre = (
        row("15-121")
        + row("15-122", other=True)
        + row("21-112")
        + row("21-120", other=True)
        + row("21-127")
        + row("21-240")
    )
    core = (
        row("15-259", "Synthetic probability", "9-12")
        + row("36-218", "Alternative probability", "", True)
        + row()
        + row("07-380")
    )
    tech = "".join(
        comments(label) + row(code)
        for label, code in [
            ("Cognition and Action Cluster", "15-386"),
            ("Machine Learning Cluster", "10-403"),
            ("Perception and Language Cluster", "11-411"),
        ]
    )
    societal = (
        comments("Human-AI Interaction Cluster")
        + row("05-317")
        + comments("AI and Humanity Cluster")
        + row("16-161")
    )
    return (
        '<div>2030-2031 Catalog</div><main><h1>Artificial Intelligence, Minor</h1><p>The minor consists of six courses and is not available to SCS students. Admission requires a "C" average in all prerequisite coursework and a statement (maximum one page), no later than the semester before they intend to graduate.</p><h4>Prerequisites</h4>'
        + table(pre)
        + "<h4>Required Core Courses</h4>"
        + table(core)
        + "<h4>Technical Electives</h4><p>Choose from two of the following three cluster areas. Each course must be a minimum of 9 units.</p>"
        + table(tech)
        + "<h4>Societal Aspects of AI</h4><p>Choose from one of the following two cluster areas. Two mini courses can be combined to form one 9 unit course.</p>"
        + table(societal)
        + "<h4>Double Counting</h4><p>Double count at most two courses total, not counting the prerequisite courses, toward all other majors and minors.</p></main>"
    )


def additional_fixture():
    comment = lambda label: '<tr><td><span class="courselistcomment">' + label + "</span></td></tr>"
    pair = lambda a, b: (
        '<tr><td class="codecol"><a href="/a">'
        + a
        + '</a> &amp; <a href="/b">'
        + b
        + '</a></td><td>Synthetic probability<br/>and Synthetic inference</td><td class="hourscol">18</td></tr>'
    )
    math = (
        row("21-112")
        + row("21-120", other=True)
        + row("21-127")
        + row("21-128", other=True)
        + row("15-151", other=True)
        + row("21-122")
        + row("21-241")
    )
    math += (
        comment("Probability and Statistics (one of)")
        + row("36-218")
        + row("15-259", "Synthetic computing (if taken Sp24 or later)")
    )
    math += (
        pair("21-325", "36-226")
        + pair("21-425", "36-226")
        + pair("36-225", "36-226")
        + pair("36-235", "36-236")
        + comment("Modern Regression Course")
        + row("36-401")
    )
    clusters = "".join(
        comment(label + " (1 course)") + row(code)
        for label, code in [
            ("Cognition and Action Cluster", "15-386"),
            ("Machine Learning Cluster", "36-402"),
            ("Perception and Language Cluster", "11-411"),
            ("Human-AI Interaction Cluster", "05-317"),
        ]
    )
    ethics = (
        comment("Ethics (1 course)")
        + row("16-161")
        + comment("Human Cognition (1 course)")
        + row("85-110")
    )
    return (
        '<div>2030-2031 Catalog</div><main><h1>Artificial Intelligence, Additional Major</h1><p>Consult the Program Administrator. Students must complete 21-112 or 21-120, 15-122, 15-150, one of 15-210, 15-213, or 15-251, as well as 07-280 with a "B" average.</p>'
        + "<h4>Prerequisites</h4>"
        + table(row("15-112"))
        + "<h4>Math and Statistics Core</h4>"
        + table(math)
        + "<h4>Computer Science Core</h4>"
        + table("".join(row(c) for c in ["15-122", "15-150", "15-210", "15-213", "15-251"]))
        + "<h4>Artificial Intelligence Core</h4>"
        + table(row() + row("07-380"))
        + "<h4>AI Cluster Electives</h4>"
        + table(clusters)
        + "<h4>Ethics and Human Cognition</h4>"
        + table(ethics)
        + "<p>07-180 is encouraged before 07-280 and not required for additional majors. Double count at most five courses total across all other majors and minors. Math, ethics and human cognition double count without restriction except for 36-402.</p></main>"
    )


def cs_fixture():
    return (
        "<h1>Degree Concentrations for CSCI Students</h1>"
        + "<p>Available only for students pursuing a CSCI degree; concentrations are optional, with one concentration per degree.</p>"
        + block(
            "Artificial Intelligence",
            "<p>4 CUs</p><p>Required:</p><p>1) CIS4210/5210</p><p>2) either CIS4190/5190 or CIS5200</p><p>Pick the remaining two CUs from:</p><p>MEAM5100</p><p>CIS5300</p>",
        )
        + block("Other discipline", "<p>CIS9999</p>")
    )


@pytest.mark.parametrize("name", NAMES)
def test_heading_alone_never_refreshes_seed(name):
    with pytest.raises(ValueError):
        adapter(name).parse("<h1>Artificial Intelligence, B.S.</h1>")


@pytest.mark.parametrize("name", ["cmu_bs", "cmu_minor", "cmu_additional"])
def test_cmu_reads_edition_and_actual_rows(name):
    parsed = adapter(name).parse(cmu_fixture(name))
    assert parsed["catalog_year"] == "2030-2031"
    assert parsed["courses"][0]["name"] == "Synthetic AI core"
    assert parsed["courses"][0]["credits"] == 12
    assert parsed["curriculum_status"] == "partial"
    assert "last_verified" not in parsed
    assert "verification_status" not in parsed
    changed = adapter(name).parse(cmu_fixture(name).replace("Synthetic AI core", "Changed course"))
    assert changed["courses"][0]["name"] == "Changed course"


def test_cmu_core_choice_is_nested_not_all_required():
    html = cmu_fixture("cmu_bs").replace(
        "<h4>Artificial Intelligence</h4>" + table(row()),
        "<h4>Artificial Intelligence</h4>"
        + table(
            row()
            + '<tr><td><span class="courselistcomment">plus one of the following AI core courses:</span></td></tr>'
            + row("11-411", "Synthetic language")
            + row("16-385", "Synthetic vision")
        ),
    )
    parsed = adapter("cmu_bs").parse(html)
    choice = next(r for r in parsed["requirements"] if r["count"] == 1)
    assert choice["kind"] == "choose_courses"
    assert set(choice["course_ids"]) == {"cmu-11-411", "cmu-16-385"}
    assert choice["parent_id"] == "cmu-bs-ai-artificial-intelligence"


def test_cmu_unknown_credit_range_is_null():
    p = adapter("cmu_bs").parse(cmu_fixture("cmu_bs").replace(">12<", ">9-12<"))
    assert all(c["credits"] is None for c in p["courses"])


def test_cmu_missing_section_fails():
    with pytest.raises(ValueError, match="section missing"):
        adapter("cmu_bs").parse(cmu_fixture("cmu_bs").replace("Ethics Course", "Different section"))


def test_minor_probability_is_single_choice_and_missing_titles_not_injected():
    p = adapter("cmu_minor").parse(minor_fixture())
    choice = next(
        r for r in p["requirements"] if r["id"].endswith("required-core-courses-option-1")
    )
    assert choice["count"] == 1 and len(choice["course_ids"]) == 2
    assert set(choice["course_ids"]) == {"cmu-15-259", "cmu-36-218"}
    assert "curriculum_audit" not in p


def test_penn_bse_requires_six_core_areas_and_observes_changes():
    parsed = adapter("penn_bse").parse(penn_bse_fixture())
    children = [r for r in parsed["requirements"] if r["parent_id"]]
    assert len(children) == 6 and all(r["credits"] == 1 for r in children)
    assert all(c["credits"] is None for c in parsed["courses"])
    assert parsed["catalog_year"] is None and "last_verified" not in parsed
    changed = adapter("penn_bse").parse(
        penn_bse_fixture().replace("Synthetic elective", "Revised elective")
    )
    assert any(c["name"] == "Revised elective" for c in changed["courses"])
    with pytest.raises(ValueError, match="six"):
        adapter("penn_bse").parse(penn_bse_fixture().replace("<h5>Area 5</h5>", ""))


def test_penn_nested_intro_alternatives_keep_course_titles_separate():
    html = penn_bse_fixture().replace(
        "<li>CIS 4200: Synthetic AI 0</li>",
        "<li>CIS 2210: Synthetic intro<ul><li>Or CIS 5210 Synthetic alternative</li></ul></li>",
    )
    p = adapter("penn_bse").parse(html)
    courses = {c["code"]: c for c in p["courses"]}
    assert courses["CIS 2210"]["name"] == "Synthetic intro"
    assert courses["CIS 5210"]["name"] == "Synthetic alternative"
    area = next(r for r in p["requirements"] if r["title"] == "Area 0")
    assert len(area["course_ids"]) == 2


def test_wharton_units_crosslist_and_source_change():
    p = adapter("penn_business").parse(business_fixture())
    assert p["program_kind"] == "concentration" and p["award_level"] == "concentration"
    assert p["requirements"][0]["credits"] == 4
    assert [r["credits"] for r in p["requirements"][1:5]] == [1, 0.5, 1, 1.5]
    assert len(p["courses"]) == 4
    assert p["courses"][-1]["code"] == "MGMT/OIDD 3130"
    assert p["courses"][-1]["credits"] is None
    with pytest.raises(ValueError, match="total changed"):
        adapter("penn_business").parse(business_fixture().replace("total of 4 CU", "total of 5 CU"))


def test_cs_concentration_scope_and_unknown_titles():
    p = adapter("penn_cs").parse(cs_fixture())
    assert len(p["courses"]) == 7
    assert all(c["name"] is None and c["credits"] is None for c in p["courses"])
    assert not any(c["code"] == "CIS 9999" for c in p["courses"])
    assert len(p["requirements"][1]["course_ids"]) == 2
    assert len(p["requirements"][2]["course_ids"]) == 3
    assert p["requirements"][-2]["credits"] == 2


def test_curated_pilot_references_and_credential_distinctions():
    root = Path(__file__).resolve().parents[1] / "data" / "programs"
    records = [
        json.loads((root / (adapter(name).PROGRAM_ID + ".json")).read_text()) for name in NAMES
    ]
    assert len(records) == 6
    for p in records:
        ids = {c["id"] for c in p["courses"]}
        sources = {s["id"] for s in p["sources"]}
        reqids = {r["id"] for r in p["requirements"]}
        assert len(ids) == len(p["courses"])
        assert len(reqids) == len(p["requirements"])
        assert all(
            r["source_id"] in sources and set(r["course_ids"]) <= ids for r in p["requirements"]
        )
        assert all(r["parent_id"] is None or r["parent_id"] in reqids for r in p["requirements"])
        assert all(c["source_id"] in sources for c in p["courses"])
        assert p["curriculum_status"] in ("complete", "partial")
        if p["curriculum_status"] == "complete":
            assert not p["curriculum_audit"]["unresolved_requirements"]
    byid = {p["id"]: p for p in records}
    assert byid["cmu-additional-ai"]["program_kind"] == "additional_major"
    assert byid["penn-concentration-ai-business"]["award_level"] == "concentration"
    assert byid["cmu-minor-ai"]["first_offered"] is None
    assert byid["penn-bse-ai"]["first_offered"]["value"] == "Fall 2024"


def test_wharton_does_not_turn_missing_credits_into_zero():
    with pytest.raises(ValueError, match="credits missing"):
        adapter("penn_business").parse(business_fixture().replace(" (0.5 CU)", ""))


@pytest.mark.parametrize(
    "old,new",
    [
        ("at most two courses total", "at most three courses total"),
        ("two of the following three cluster areas", "two courses from any cluster"),
        ("not available to SCS students", "available to all students"),
        ("<h4>Double Counting</h4>", "<h4>Other Requirements</h4>"),
    ],
)
def test_minor_policy_changes_require_review(old, new):
    with pytest.raises(ValueError):
        adapter("cmu_minor").parse(minor_fixture().replace(old, new))


def test_minor_prerequisite_alternatives_and_distinct_cluster_choices():
    p = adapter("cmu_minor").parse(minor_fixture())
    prereqs = [r for r in p["requirements"] if r["parent_id"] == "cmu-minor-ai-prerequisites"]
    assert len(prereqs) == 4
    assert prereqs[0]["course_ids"] == ["cmu-15-121", "cmu-15-122"]
    technical = next(r for r in p["requirements"] if r["title"] == "Technical Electives")
    children = [r for r in p["requirements"] if r["parent_id"] == technical["id"]]
    assert technical["count"] == 2 and len(children) == 3
    assert all(r["kind"] == "choose_courses" and r["count"] == 1 for r in children)
    assert p["curriculum_status"] == "partial" and "curriculum_audit" not in p


def test_wharton_approval_caps_are_observed_and_never_minimum_requirements():
    p = adapter("penn_business").parse(
        business_fixture().replace("maximum of 1 CU", "maximum of 0.5 CU")
    )
    caps = [r for r in p["requirements"] if r["title"].endswith("allowance")]
    assert len(caps) == 2
    assert all(
        r["kind"] == "note" and r["credits"] is None and "0.5 CU" in r["summary"] for r in caps
    )
    with pytest.raises(ValueError, match="approval/cap"):
        adapter("penn_business").parse(
            business_fixture().replace("faculty advisor approval", "automatic approval")
        )


def test_cs_parent_degree_eligibility_cannot_be_assumed_from_title():
    with pytest.raises(ValueError, match="eligibility"):
        adapter("penn_cs").parse(
            cs_fixture().replace(
                "one concentration per degree", "multiple concentrations per degree"
            )
        )


def test_additional_probability_sequences_are_and_options_with_combined_units():
    p = adapter("cmu_additional").parse(additional_fixture())
    probability = next(r for r in p["requirements"] if r["id"].endswith("-probability"))
    choices = [r for r in p["requirements"] if r["parent_id"] == probability["id"]]
    assert probability["kind"] == "alternative" and probability["count"] == 1
    assert len(choices) == 6
    pair = next(r for r in choices if r["course_ids"] == ["cmu-21-325", "cmu-36-226"])
    assert pair["kind"] == "all" and pair["credits"] == 18
    courses = {c["id"]: c for c in p["courses"]}
    assert courses["cmu-21-325"]["credits"] is None
    assert courses["cmu-36-226"]["credits"] is None
    assert "curriculum_audit" not in p and p["curriculum_status"] == "partial"


@pytest.mark.parametrize(
    "old,new",
    [
        ("Sp24 or later", "Sp25 or later"),
        ("at most five courses total", "at most six courses total"),
        ("one of 15-210", "all of 15-210"),
    ],
)
def test_additional_policy_changes_require_review(old, new):
    with pytest.raises(ValueError):
        adapter("cmu_additional").parse(additional_fixture().replace(old, new))
