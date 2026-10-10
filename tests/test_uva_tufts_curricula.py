"""Synthetic layouts expose variant leakage, topic collapse and alternative errors."""

import importlib.util
import json
from pathlib import Path
import pytest
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
PIDS = [
    "uva-bscs-ai-concentration",
    "uva-bacs-ai-concentration",
    "tufts-application-ai-minor",
    "tufts-ai-development-minor",
]


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / "atlas/adapters" / pid / "adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def linked_course(code, name, topics=()):
    return (
        '<li><a href="https://example.edu/catalog">'
        + code
        + " - "
        + name
        + "</a> — 3 credits"
        + (
            "<ul>" + "".join("<li>Approved Topic: " + t + "</li>" for t in topics) + "</ul>"
            if topics
            else ""
        )
        + "</li>"
    )


def uva_fixture():
    s = "<main><h1>Artificial Intelligence Concentration</h1><p>Concentrations under the BA and BS in Computer Science degree programs, effective Fall 2026. Recorded on the transcript, but not on their diploma. Courses can also count for any other major or minor requirement.</p><h2>Declaring the AI Concentration</h2><ul><li>BSCS Majors: Submit a change of major form to the SEAS office</li><li>BACS Majors: Choose the concentration via AirTable (when available - coming soon).</li></ul>"
    core = linked_course("CS 4710", "Synthetic AI") + linked_course("CS 4774", "Synthetic ML")
    s += (
        "<h2>BSCS AI Concentration</h2><p>four courses (12 credits)</p><h3>Required Courses</h3><p>Complete two.</p><ul>"
        + core
        + "</ul>"
    )
    s += (
        "<h3>AI Techniques Elective (3 credits)</h3><p>Students must complete one of the following.</p><ul>"
        + linked_course("CS 4501", "Special Topics", ("Synthetic Vision", "Synthetic Robotics"))
        + "</ul>"
    )
    s += (
        "<h3>AI Applications &amp; Impacts Elective (3 credits)</h3><p>Students must complete one of the following.</p><ul>"
        + linked_course("MDST 3510", "Media Topics", ("Synthetic Policy",))
        + "</ul>"
    )
    s += (
        "<h2>BACS AI Concentration</h2><p>four courses (12 credits). Each course also satisfies a major requirement for the BACS; core courses also satisfy the CS Restricted Electives.</p><h3>AI Concentration Core</h3><p>Complete two.</p><ul>"
        + core
        + "</ul>"
    )
    s += (
        "<h3>AI Concentration Electives</h3><p>Students must also complete two courses from the list.</p><ul>"
        + linked_course("MDST 3510", "Media Topics")
        + "</ul><h4>Special Topics Courses</h4><p>These courses will require manual override.</p><ul><li>CS 4501: Synthetic Law</li><li>CS 4501: Synthetic Agents</li></ul></main>"
    )
    return s


def accordion(title, rows):
    return (
        '<li class="accordion-item"><h3>'
        + title
        + "</h3><div><ul>"
        + "".join("<li>" + r + "</li>" for r in rows)
        + "</ul></div></li>"
    )


def tufts_fixture(development):
    title = "Minor in AI Development" if development else "Minor in the Application of AI"
    s = (
        "<main><h1>"
        + title
        + "</h1><p>The minor requires five courses and at least 15 credits.</p>"
    )
    if development:
        s += "<p>open to all undergraduate students in Arts and Sciences and Engineering, including majors in Computer Science, Data Science, and Electrical and Computer Engineering; grade of C- or better.</p>"
        core = [
            "<strong>CS15 - Synthetic Structures</strong> (4 credits, requires prior completion of CS10)",
            "<strong>CS61 - Synthetic Math</strong> (3 credits, recommends Math 32) or <strong>Math 65 - Synthetic Bridge</strong> (3 credits)",
            "<strong>CS131 - Synthetic AI</strong> (3 credits, requires prior completion of CS15)",
            "<strong>CS135 - Synthetic ML</strong> (3 credits, requires Math70) or <strong>EE140/CS128 - Synthetic Sequential</strong> (3 credits)",
        ]
        electives = [
            "CS150 - Synthetic Topic A",
            "CS150 - Synthetic Topic B",
            "CS168/EE109 - Synthetic Optimization or EE159 - Synthetic Advanced Optimization",
        ]
    else:
        s += "<p>Open except those pursuing a B.S. in Computer Science, Data Science, or Computer Engineering in the School of Engineering or a B.A. or B.S. in Computer Science in the School of Arts and Sciences.</p>"
        core = [
            "<strong>CS10 - Synthetic Programming</strong> (4 credits, no enrollment requirements) <strong>or ES2 Synthetic Computing</strong> (4 credits, no enrollment requirements)",
            "<strong>CS31 - Synthetic AI</strong> (3 credits, requires CS10)",
            "<strong>CS35 - Synthetic ML</strong> (3 credits, requires ES2)",
        ]
        electives = [
            "CEE132/DS143/ME173 - Synthetic Sustainability",
            "CHEM194 Special Topics: Synthetic Drug Design",
            "Directed study, research, and thesis courses involving AI, as approved by the minor director",
        ]
        s += "<p>Changes to the disciplinary elective list are made in consultation with members of the AI Council.</p>"
    s += (
        "<ul>"
        + accordion(
            "Core Courses (Four Required)" if development else "Core Courses (Three Required)", core
        )
        + accordion(
            "Elective Courses (Select One)"
            if development
            else "Disciplinary Electives (Select Two)",
            electives,
        )
        + "</ul></main>"
    )
    return s


@pytest.mark.parametrize("pid", PIDS)
def test_real_structure_and_manual_partial_audit(pid):
    f = uva_fixture() if pid.startswith("uva-") else tufts_fixture("development" in pid)
    mod = load(pid)
    result = mod.parse(f)
    assert result["courses"] and result["requirements"]
    assert result["curriculum_status"] == "partial"
    assert not {"curriculum_audit", "last_verified"} & result.keys()
    seed = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
    validate_program(seed)
    assert (
        seed["curriculum_status"] == "partial"
        and seed["curriculum_audit"]["unresolved_requirements"]
    )
    with pytest.raises(ValueError):
        mod.parse("<main><h1>Unrelated curriculum</h1></main>")


def test_uva_variants_do_not_leak_topics_or_restrict_ba_mdst():
    bs = load(PIDS[0]).parse(uva_fixture())
    ba = load(PIDS[1]).parse(uva_fixture())
    assert any("Synthetic Vision" in c["name"] for c in bs["courses"])
    assert not any("Synthetic Vision" in c["name"] for c in ba["courses"])
    mdst = next(c for c in ba["courses"] if c["code"] == "MDST 3510")
    assert mdst["name"] == "Media Topics"
    topics = [c for c in ba["courses"] if c["code"] == "CS 4501"]
    assert len(topics) == 2 and all(c["credits"] is None for c in topics)
    rule = next(r for r in ba["requirements"] if r["id"].endswith("-manual-topics"))
    assert rule["kind"] == "note" and "manual override" in rule["summary"]


def test_uva_changed_choice_count_observed_and_missing_list_rejected():
    r = load(PIDS[1]).parse(uva_fixture().replace("complete two courses", "complete three courses"))
    assert next(x for x in r["requirements"] if x["id"].endswith("-electives"))["count"] == 3
    broken = uva_fixture().replace(
        "<ul>"
        + linked_course("CS 4710", "Synthetic AI")
        + linked_course("CS 4774", "Synthetic ML")
        + "</ul>",
        "",
        1,
    )
    with pytest.raises(ValueError, match="Course list missing"):
        load(PIDS[0]).parse(broken)


def test_tufts_core_choices_and_crosslisted_option_counts():
    r = load(PIDS[2]).parse(tufts_fixture(False))
    slot = next(x for x in r["requirements"] if x["id"].endswith("core-slot-1"))
    assert slot["kind"] == "choose_courses" and slot["count"] == 1 and len(slot["course_ids"]) == 2
    assert len([c for c in r["courses"] if c["code"] == "CEE 132/DS 143/ME 173"]) == 1
    elective = next(x for x in r["requirements"] if x["id"].endswith("-electives"))
    assert elective["count"] == 2
    assert any(x["id"].endswith("-approved-independent-work") for x in r["requirements"])


def test_tufts_topics_not_collapsed_and_alternative_course_separate():
    r = load(PIDS[3]).parse(tufts_fixture(True))
    topics = [c for c in r["courses"] if c["code"] == "CS 150"]
    assert len(topics) == 2 and topics[0]["id"] != topics[1]["id"]
    assert any(c["code"] == "EE 159" for c in r["courses"])
    assert next(c for c in r["courses"] if c["code"] == "CS 61")["prerequisites"].startswith(
        "recommends"
    )
    with pytest.raises(ValueError, match="minimum-grade"):
        load(PIDS[3]).parse(tufts_fixture(True).replace("C- or better", "D or better"))
