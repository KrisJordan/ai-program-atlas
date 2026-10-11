"""Reviewed metadata boundaries and substantive course-access conflicts."""

import importlib
import json
from pathlib import Path
import pytest
from atlas.adapters import small_complete_metadata_batch2 as m
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
IDS = list(dict.fromkeys(c["pid"] for c in m.CONFIG.values()))


def test_uga_undergraduate_pre_corequisite_and_variable_credit():
    key = "georgia-csci-4170-6170"
    spec = m.CONFIG[key]["courses"][0]
    html = f"""<h1>CSCI 4170/6170</h1><li class="credit-number">4 hours</li>
    <p class="large-mws">Course Description</p><p>{spec["guard"]}</p>
    <p class="large-mws">Undergraduate Pre or Corequisite</p><p>CSCI 2720 or CSCI 2725</p>
    <p class="large-mws">Graduate Prerequisite</p><p>Department permission</p>"""
    row = m.parse_metadata(html, key)["courses"][0]
    assert row["prerequisites"] == "Prerequisite or corequisite: CSCI 2720 or CSCI 2725"
    assert row["credits"] == 4 and row["credit_unit"] == "unknown"
    variable = m.parse_metadata(
        html.replace("4 hours", "1-4 hours. Repeatable for maximum 14 hours credit."), key
    )["courses"][0]
    assert "credits" not in variable  # never mistake repeat maximum for course amount
    with pytest.raises(ValueError):
        m.parse_metadata(html.replace(spec["guard"], "Different content"), key)
    with pytest.raises(ValueError):
        m.parse_metadata(html.replace("CSCI 4170/6170", "CSCI 4180"), key)


def msu_version(effective, description, prerequisite, restriction):
    fields = {
        "Effective Dates:": effective,
        "Description:": description,
        "Credits:": "Total Credits: Credits: 1",
        "Prerequisite:": prerequisite,
        "Restrictions:": restriction,
    }
    return "<h3>CSE 300 Test title</h3>" + "".join(
        f'<div><div class="col-md-3">{k}</div><div class="col-md-7">{v}</div></div>'
        for k, v in fields.items()
    )


def test_msu_selects_reviewed_open_version_not_first_historical_version():
    key = "msu-300"
    cfg = m.CONFIG[key]
    guard = cfg["courses"][0]["guard"]
    old = msu_version("FS20 - FS23", "Old description", "Old prerequisite", "Old restriction")
    current = msu_version(
        cfg["effective"], guard, "CSE 232", "Open to Computer Science Major only."
    )
    row = m.parse_metadata(old + current, key)["courses"][0]
    assert (
        row["prerequisites"]
        == "CSE 232. Enrollment restrictions: Open to Computer Science Major only."
    )
    assert "Old" not in row["prerequisites"]
    with pytest.raises(ValueError):
        m.parse_metadata(old, key)
    with pytest.raises(ValueError):
        m.parse_metadata(current + current, key)
    with pytest.raises(ValueError):
        m.parse_metadata(current.replace(cfg["effective"], "FS27 - Open"), key)


def test_rochester_schedule_does_not_invent_credit_or_prerequisite():
    key = "rochester-spring"
    cfg = m.CONFIG[key]
    html = (
        "<h2>Spring Term Schedule</h2><h3>Spring 2026</h3><table>"
        + "".join(
            f"<tr><td>{s['code']}-01</td></tr><tr><td>{s['guard']}</td></tr>"
            for s in cfg["courses"]
        )
        + "</table>"
    )
    observed = m.parse_metadata(html, key)
    assert len(observed["courses"]) == 2
    assert all("credits" not in c and "prerequisites" not in c for c in observed["courses"])
    assert (
        not {"first_offered", "curriculum_audit", "curriculum_status", "last_verified"}
        & observed.keys()
    )
    with pytest.raises(ValueError):
        m.parse_metadata(html.replace("Spring 2026", "Spring 2027"), key)


def test_lc_explicit_none_and_semester_credits():
    key = "lc-phil"
    s = m.CONFIG[key]["courses"][0]
    html = f'<div class="courseblock"><p class="courseblocktitle">PHIL 241 Test title</p><p class="courseblockdesc">{s["guard"]} Prerequisites: None. Usually offered: Annually. Semester credits: 4.</p></div>'
    row = m.parse_metadata(html, key)["courses"][0]
    assert (
        row["prerequisites"] == "None."
        and row["credit_unit"] == "semester_hours"
        and row["credits"] == 4
    )
    with pytest.raises(ValueError):
        m.parse_metadata(html.replace("Semester credits:", "Unclassified credits:"), key)


def test_indiana_recommendations_not_promoted_to_prerequisites():
    key = "indiana-cs-ai-specialization-source-4"
    # Each guard begins with the real identity, followed by its reviewed course context.
    html = "".join(
        f'<li class="nobullet"><span class="ctitle">{s["code"]} Test title (3 cr.)</span>{s["guard"]} Programming recommended.</li>'
        for s in m.CONFIG[key]["courses"]
    )
    rows = m.parse_metadata(html, key)["courses"]
    assert len(rows) == 11 and all("prerequisites" not in r for r in rows)
    assert not any(c["code"] == "CSCI-B 490" for c in rows)


def test_villanova_inconsistent_ai_description_stays_unknown():
    key = "villanova-mgt-3180"
    s = m.CONFIG[key]["courses"][0]
    html = f'<main><h1>MGT 3180: Advance Data Mining &amp; AI</h1><div class="body-text-wrapper">{s["guard"]} Junior or senior standing</div><div class="field--name-field-credits"><div class="field__item">3</div></div><div class="field--name-field-pr"><div class="field__item">MGT 3170:Y</div></div></main>'
    row = m.parse_metadata(html, key)["courses"][0]
    assert "description" not in row
    assert row["prerequisites"] == "MGT 3170:Y; Junior or senior standing."


def test_aims_are_not_learning_outcomes_or_launch_evidence():
    observed = m.parse_aim("<p>overall aim: Developers, Deployers and Integrators</p>", "georgia")
    assert observed["outcomes"][0]["statement_type"] == "program_aim"
    assert "first_offered" not in observed
    with pytest.raises(ValueError):
        m.parse_aim("<p>AI options</p>", "georgia")


@pytest.mark.parametrize("pid", IDS)
def test_six_records_validate_and_register_source_routes(pid):
    d = json.loads((ROOT / "data/programs" / f"{pid}.json").read_text())
    validate_program(d)
    module = importlib.import_module("atlas.adapters." + pid + ".adapter")
    assert all(v["url"] in module.SOURCE_PARSERS for v in m.CONFIG.values() if v["pid"] == pid)
    if pid.startswith("michigan-state"):
        assert d["curriculum_status"] == "partial"
        assert "CSE 300" in d["curriculum_audit"]["unresolved_requirements"][0]
        assert d["outcomes"][0]["statement_type"] == "program_aim"
    else:
        assert d["curriculum_status"] == "complete"
    if pid == "georgia-ai-emphasis":
        assert d["first_offered"]["value"] == "Fall 2026"
    else:
        assert d["first_offered"] is None
    assert all(c["syllabus"] is None and c["public_site"] is None for c in d["courses"])
