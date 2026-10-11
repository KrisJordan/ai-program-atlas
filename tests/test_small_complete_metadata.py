"""Evidence review guards: absence is unknown; enrollment conflicts remain visible."""

import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import small_complete_metadata as m
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
IDS = [
    "smu-cs-ba-ai-ml-track",
    "smu-cs-bs-ai-ml-specialization",
    "villanova-ai-ml-minor",
    "texas-am-ai-business-minor",
    "ohio-state-ai-specialization",
    "denison-mlai-minor",
]


def tamu_fixture():
    return (
        "<main><h1>BUSN - Mays Business School</h1>"
        + "".join(
            f'<div class="courseblock"><h2 class="courseblocktitle">{code} Test title</h2>'
            f'<p class="courseblockdesc">Credits 3. {guard}. '
            + (
                "Prerequisites: Artificial Intelligence in Business minor; junior or senior classification."
                if int(code[-3:]) >= 400
                else ""
            )
            + "</p></div>"
            for code, (guard, _) in m.TAMU_SUMMARIES.items()
        )
        + "</main>"
    )


def osu_fixture():
    return (
        "<main><h1>Courses</h1>"
        + "".join(
            f'<details class="coe-accordion"><summary>{code}</summary><span class="title">Test title</span>'
            f'<p class="description">Description: {guard}. Prereq: 2331 or 5331; and Math 2568. Units: {4 if code.endswith("5914") else 3}.0</p></details>'
            for code, (guard, _) in m.OSU_SUMMARIES.items()
        )
        + "</main>"
    )


def test_tamu_absent_prerequisites_remain_null_and_restrictions_survive():
    result = m.parse_tamu_courses(tamu_fixture())
    courses = {c["code"]: c for c in result["courses"]}
    assert courses["BUSN 250"]["prerequisites"] is None
    assert courses["BUSN 255"]["prerequisites"] is None
    assert all(
        "junior or senior" in courses[code]["prerequisites"]
        for code in ["BUSN 460", "BUSN 465", "BUSN 470"]
    )
    assert (
        not {"curriculum_audit", "last_verified", "first_offered", "curriculum_status"}
        & result.keys()
    )
    with pytest.raises(ValueError):
        m.parse_tamu_courses(tamu_fixture().replace("BUSN 470", "BUSN 471"))
    with pytest.raises(ValueError):
        m.parse_tamu_courses(tamu_fixture().replace("Credits 3.", "Credits variable."))


def test_osu_directory_is_separate_observation_with_unknown_unit():
    result = m.parse_osu_courses(osu_fixture())
    assert len(result["courses"]) == 7
    assert all(c["credit_unit"] == "unknown" for c in result["courses"])
    assert next(c for c in result["courses"] if c["code"] == "CSE 5914")["credits"] == 4
    assert "5331" in result["courses"][0]["prerequisites"]
    assert (
        not {"curriculum_audit", "last_verified", "first_offered", "curriculum_status"}
        & result.keys()
    )
    with pytest.raises(ValueError):
        m.parse_osu_courses(osu_fixture().replace("Units:", "Unverified credits:"))
    with pytest.raises(ValueError):
        m.parse_osu_courses(osu_fixture().replace("CSE 5914", "CSE 5915"))


def test_denison_prerequisites_do_not_invent_parentheses():
    html = "<h1>Machine Learning &amp; AI (ML)</h1>" + "".join(
        f'<div class="courseblock"><p class="courseblocktitle">ML {code} - Test course</p>'
        '<p class="courseblockextra">Prerequisite(s): MATH 145 and CS 105 or CS 145.</p></div>'
        for code in [240, 310, 400]
    )
    result = m.parse_denison_prerequisites(html)
    assert all(c["prerequisites"] == "MATH 145 and CS 105 or CS 145." for c in result["courses"])
    assert "grouping remains unresolved" in result["notes"][0]
    with pytest.raises(ValueError):
        m.parse_denison_prerequisites(html.replace("Prerequisite(s):", "Former prerequisites:"))


def test_source_context_distinguishes_aim_and_career_not_assessed_outcome():
    result = m.parse_denison_home(
        "<h1>Machine Learning &amp; Artificial Intelligence</h1><h2>Communicate effectively</h2><p>technical and non-technical audiences</p><h2>Jobs as a machine learning &amp; artificial intelligence major</h2><p>advanced graduate study in artificial intelligence</p>"
    )
    assert [o["statement_type"] for o in result["outcomes"]] == ["program_aim", "career_pathway"]
    assert all(o["kind"] == "source_stated" for o in result["outcomes"])
    with pytest.raises(ValueError):
        m.parse_denison_home("<h1>Generic CS degree</h1>")


@pytest.mark.parametrize("pid", IDS)
def test_six_reviewed_records_validate_with_null_launch_and_no_guessed_links(pid):
    record = json.loads((ROOT / "data/programs" / f"{pid}.json").read_text())
    validate_program(record)
    assert record["first_offered"] is None
    assert all(
        c.get("public_site") is None and c.get("syllabus") is None for c in record["courses"]
    )
    module = importlib.import_module("atlas.adapters." + pid + ".adapter")
    assert set(module.SOURCES) <= {s["url"] for s in record["sources"]}
    if pid == "ohio-state-ai-specialization":
        assert record["curriculum_status"] == "partial"
        assert record["curriculum_audit"]["unresolved_requirements"]
        course = next(c for c in record["courses"] if c["code"] == "CSE 3521")
        assert (
            "Specialization table:" in course["prerequisites"]
            and "Course directory:" in course["prerequisites"]
        )
        assert "5221" in course["prerequisites"] and "5331" in course["prerequisites"]
    else:
        assert record["curriculum_status"] == "complete"
