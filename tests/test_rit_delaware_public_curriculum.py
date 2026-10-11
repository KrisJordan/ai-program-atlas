"""Dynamic public rendering and bounded catalog-access evidence."""

import importlib
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
RIT = importlib.import_module("atlas.adapters.rit-ai-society-immersion.adapter")
UD = importlib.import_module("atlas.adapters.delaware-cs-ai-robotics-concentration.adapter")
CODES = [
    "STSO-320",
    "STSO-140",
    "STSO-201",
    "STSO-240",
    "STSO-340",
    "STSO-350",
    "STSO-360",
    "STSO-425",
    "STSO-441",
    "DHSS-101",
    "DHSS-103",
    "PHIL-307",
    "POLS-280",
    "VISL-234",
]


def identity():
    return "<h1>AI in Society Immersion</h1><p>The plan code for AI in Society Immersion is AISTS-IM.</p><h2>Curriculum for 2026-2027 for AI in Society Immersion</h2>"


def rendered():
    def course(code, amount=""):
        return f'<tr><td><span data-code-bubble="{code}">{code}</span></td><td>Observed {code} title</td><td>{amount}</td></tr>'

    return (
        identity()
        + """<p>historical, social, cultural, ethical, policy, and environmental perspectives. Immersions may not overlap with program requirements.</p><div id="curriculumContainer"><table class="sc_courselist"><tr><td>Required Course</td></tr>"""
        + course(CODES[0], "3")
        + "<tr><td>Electives</td></tr><tr><td>Select two of the following:</td><td>6</td></tr>"
        + "".join(course(c) for c in CODES[1:])
        + "<tr><td>Total Hours</td><td>9</td></tr></table></div>"
    )


def test_missing_dynamic_content_does_not_become_empty_curriculum():
    result = RIT.parse(
        identity() + '<div id="overviewContainer"></div><div id="curriculumContainer"></div>'
    )
    assert (
        not {"courses", "requirements", "outcomes", "curriculum_audit", "curriculum_status"}
        & result.keys()
    )
    assert "rendered" in result["notes"][0]


def test_exact_immersion_pool_and_unknown_elective_amounts():
    result = RIT.parse(rendered())
    assert len(result["courses"]) == 14
    assert result["courses"][0]["credits"] == 3
    assert all(c["credits"] is None for c in result["courses"][1:])
    elective = result["requirements"][2]
    assert elective["count"] == 2 and elective["credits"] == 6 and len(elective["course_ids"]) == 13
    assert result["outcomes"][0]["statement_type"] == "program_aim"
    assert (
        not {"curriculum_status", "curriculum_audit", "last_verified", "first_offered"}
        & result.keys()
    )
    assert all(c["code"] not in ("DHSS-488", "PHIL-320") for c in result["courses"])
    assert result["courses"][0]["name"] == "Observed STSO-320 title"


@pytest.mark.parametrize(
    "old,new",
    [
        ("AISTS-IM", "AISTS-MN"),
        ("2026-2027", "2027-2028"),
        ("Select two", "Select three"),
        ("Total Hours</td><td>9", "Total Hours</td><td>12"),
        ("POLS-280", "PHIL-320"),
        ("may not overlap", "may overlap"),
    ],
)
def test_rit_changed_identity_pool_or_policy_requires_review(old, new):
    with pytest.raises(ValueError):
        RIT.parse(rendered().replace(old, new))


@pytest.mark.parametrize("key", list(RIT.POLICIES))
def test_rit_policy_guards_and_no_automatic_audit(key):
    _, title, guards, rules = RIT.POLICIES[key]
    html = f"<h1>{title}</h1><p>" + " ".join(guards) + "</p>"
    result = RIT.parse_policy(html, key)
    assert len(result["requirements"]) == len(rules)
    assert not {"curriculum_status", "curriculum_audit", "last_verified"} & result.keys()
    with pytest.raises(ValueError):
        RIT.parse_policy(html.replace(guards[-1], "Changed policy"), key)


def test_delaware_rules_do_not_invent_course_pool_or_apply_focus_area_permission():
    html = """<h1>Student FAQ</h1><p>no such approval is required to select a concentration; second semester of your second (Sophomore) year; Can independent study be used as a concentration course? No, but it can be used as an elective. pass/fail cannot be used to satisfy any major or minor requirement. permission must be obtained from the department. you must look up the program description for your catalog year.</p>"""
    result = UD.parse_faq(html)
    assert len(result["requirements"]) == 5 and "courses" not in result
    assert "cannot be used" in result["requirements"][1]["summary"]
    assert "No advisor approval" in result["requirements"][0]["summary"]
    with pytest.raises(ValueError):
        UD.parse_faq(html.replace("No, but it can be used", "Yes"))


def test_curated_review_states_and_identity_limits():
    rit = json.loads((ROOT / "data/programs/rit-ai-society-immersion.json").read_text())
    ud = json.loads((ROOT / "data/programs/delaware-cs-ai-robotics-concentration.json").read_text())
    for record in [rit, ud]:
        validate_program(record)
        assert record["first_offered"] is None
    assert (
        rit["curriculum_status"] == "complete"
        and rit["curriculum_audit"]["scope"] == "concentration"
    )
    assert len(rit["courses"]) == 14 and len(rit["requirements"]) == 12
    assert sum(c["credits"] is not None for c in rit["courses"]) == 1
    assert "Transcript recognition is unverified" in rit["overview"]
    assert (
        ud["curriculum_status"] == "partial"
        and ud["courses"] == []
        and len(ud["requirements"]) == 5
    )
    assert ud["curriculum_audit"]["unresolved_requirements"]
    assert "transcript-recognized" in ud["overview"]
    assert all(r["kind"] == "note" for r in ud["requirements"])
