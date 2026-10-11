"""Synthetic source layouts test alternatives, actual observations and policy loss."""

import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program
from atlas.adapters.villanova_curriculum import parse_course

ROOT = Path(__file__).resolve().parents[1]
PIDS = ["villanova-ai-ml-minor", "villanova-analytics-ai-minor", "villanova-analytics-ai-co-major"]


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / "atlas/adapters" / pid / "adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row(code, name="Synthetic course", credits=3):
    return f'<article class="node--type-class"><div class="col-3"><a href="/course">{code}</a></div><div class="col-7">{name}</div><span class="field--name-field-credits">{credits}</span></article>'


def fixture(pid):
    ai = pid == PIDS[0]
    co = pid == PIDS[2]
    title = (
        "Artificial Intelligence and Machine Learning Minor"
        if ai
        else "Analytics &amp; Artificial Intelligence " + ("Co-Major" if co else "Minor")
    )
    core = ["MIS 3300", "MIS 2020", "MIS 3080"] if ai else ["MGT 3170", "MGT 4170"]
    s = (
        f'<main><h1>{title}</h1><div class="paragraph--type--degree-section"><h2>Course Requirements for {title} ({15 if co else 9} Credits)</h2>'
        + "".join(row(c) for c in core)
        + "</div>"
    )
    if not ai:
        s += (
            '<div class="paragraph--type--degree-section"><div class="field--name-field-degree-section-description">Plus '
            + ("Three (3)" if co else "one (1)")
            + " elective courses</div>"
            + "".join(row(c) for c in ["MIS 2030", "MIS 3050", "MIS 3060"])
            + "</div>"
        )
        s += "<p>For students pursuing both Analytics &amp; Artificial Intelligence and Master of Science in Business Analytics and Artificial Intelligence. MSA 8105 (R and Python) may fulfill an Analytics &amp; Artificial Intelligence elective. In addition, one of the following: MSA 8110 (Data Models), MSA 8240 (Business Intelligence).</p><p>up to nine credits; permission of the department, graduate programs, and undergraduate programs; cannot apply to undergraduate degree requirements retroactively.</p>"
        if co:
            s += "<p>must be taken in conjunction with a major in Accounting, Economics, Finance, Management, Management Information Systems, Marketing, or Real Estate.</p><p>Only one course may fulfill another VSB major. MIS 3050 or MIS 2030. Other Approved Electives. CSC 4480 (Database Systems).</p>"
        else:
            s += "<p>three (3) unique business courses; may also fulfill the free elective requirements. CSC 4480 may not fulfill an Analytics &amp; Artificial Intelligence requirement.</p>"
    else:
        s += "<p>three (3) unique MIS courses; open to all VSB students; may also fulfill the free elective requirements. CSC 1052 (Data Structures) may fulfill MIS 2020 only if not fulfilling the core Arts and Sciences requirement. Applied Quantitative Finance Concentration students may not also minor.</p>"
    if co:
        s += '<div class="modal"><h5 class="modal-title">Other Approved Electives</h5><div class="modal-body"><span>Total Credits</span></div></div>'
    return s + "</main>"


@pytest.mark.parametrize("pid", PIDS)
def test_fresh_curriculum_and_manual_audit_are_separate(pid):
    mod = load(pid)
    observed = mod.parse(fixture(pid))
    seed = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
    validate_program(seed)
    assert observed["courses"] and observed["requirements"]
    assert observed["curriculum_status"] == "partial"
    assert not {"curriculum_audit", "last_verified"} & observed.keys()
    assert seed["curriculum_audit"]["unresolved_requirements"] == (
        []
        if pid != PIDS[2]
        else ["Empty Other Approved Electives entry has no verified inventory or approval rule."]
    )
    assert (
        next(
            c
            for c in observed["courses"]
            if c["code"].endswith("3300" if pid == PIDS[0] else "3170")
        )["name"]
        == "Synthetic course"
    )
    with pytest.raises(ValueError):
        mod.parse(fixture(pid).replace("Course Requirements for ", "Changed section "))


def test_elective_count_and_numeric_course_credit_are_observed():
    mod = load(PIDS[1])
    html = fixture(PIDS[1]).replace("one (1)", "one (2)").replace(">3</span>", ">4</span>")
    r = mod.parse(html)
    assert next(x for x in r["requirements"] if x["id"].endswith("-electives"))["count"] == 2
    assert next(c for c in r["courses"] if c["code"] == "MGT 3170")["credits"] == 4


def test_conditional_course_is_not_unrestricted_elective_and_minor_excludes_csc():
    r = load(PIDS[1]).parse(fixture(PIDS[1]))
    elective = next(x for x in r["requirements"] if x["id"].endswith("-electives"))
    assert not any("msa-" in c for c in elective["course_ids"])
    assert not any(c["code"] == "CSC 4480" for c in r["courses"])
    with pytest.raises(ValueError, match="excluded-course"):
        load(PIDS[1]).parse(fixture(PIDS[1]).replace("may not fulfill", "may fulfill"))


def test_co_major_keeps_exclusive_slot_and_unresolved_open_entry():
    r = load(PIDS[2]).parse(fixture(PIDS[2]))
    rules = {x["id"].split(PIDS[2] + "-")[1]: x for x in r["requirements"]}
    assert rules["database-alternative"]["course_ids"] == [
        "villanova-mis-3050",
        "villanova-mis-2030",
    ]
    assert rules["other-approved-electives"]["kind"] == "note"
    assert "villanova-csc-4480" in rules["graduate-substitutions"]["course_ids"]


def test_course_metadata_is_scoped_and_missing_prerequisite_unknown():
    html = '<main><h1>MIS 3300: Test AI</h1><span class="field--name-field-credits"><span class="field__item">3</span></span><div class="field--name-field-description">A changed description.</div></main>'
    result = parse_course(html, pid=PIDS[0], code="MIS 3300", url="https://example.edu/course")
    assert result["courses"][0]["prerequisites"] is None
    assert result["courses"][0]["description"] is None
    assert result["observed_description_digest"]
    with pytest.raises(ValueError):
        parse_course(html, pid=PIDS[0], code="MIS 3080", url="https://example.edu/course")
