import json
from pathlib import Path
import pytest
from atlas.adapters.penn_bse.distributions import parse_distributions, parse_abroad
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]


def sec(n, title, body):
    return f'<div id="faq_{n}"><h4>{title}</h4>{body}</div>'


def ul(items):
    return "<ul>" + "".join("<li>" + s + "</li>" for s in items) + "</ul>"


def fixture():
    ns = (
        "<p>Freshman Seminar courses can not be used. Any course above 2000 pending approval by faculty committee. Only CIS Majors. CHEM 1012 or CHEM 1151, but not both.</p>"
        + ul(
            [
                "<strong>Subject "
                + str(i)
                + ":</strong> Any course"
                + ("<ul><li>Note: Course1111 is excluded.</li></ul>" if i == 0 else "")
                for i in range(17)
            ]
        )
    )
    math = (
        "<p>Each department decides which math courses it accepts. Freshman Seminars may not be used. MATH 2400 (discontinued as of Fall 2026)</p>"
        + ul(["<strong>STAT:</strong>4300,4310"])
        + ul(["STAT 4300 and ESE 3010"])
    )
    free = (
        "<p>Any undergraduate course unless it is in the No Credit list; students may not use courses on this list toward their degree.</p>"
        + ul(["EAS 5050 (use EAS 3010 for TBS)", "CIS (CSE) 100/101"])
    )
    eng = (
        "<p>all undergraduate and 5000-level graduate courses;2960,2970,2980;EAS courses below 0800;CIS 2620 counts as an Engineering course.</p>"
        + ul(["BE:5130"])
    )
    ssh = (
        "<p>any course numbered below 6000;All Departmental-based topics courses must be approved;must use the “SS” or “H” designations according to their cross-listed academic department</p><h3>Social Sciences</h3>"
        + ul(["COMM – Communications"])
        + ul(
            [
                "<strong>Finance (FNCE)</strong>1010",
                "<strong>History and Sociology of Science (HSSC)</strong>(taken prior to Fall 2004)",
            ]
        )
        + "<h3>Humanities</h3>"
        + ul(["PHIL except logic courses"])
        + ul(["<strong>CIS – Computer &amp; Information Science</strong>1060 (ANTH 2580)"])
        + "<h3>Courses From Academic Programs With All Multi-Listed Courses</h3>"
        + ul(["AFRC"])
        + "<h3>Writing Seminar Course</h3>"
    )
    sshpolicy = "<p>courses in the business discipline, military science;primarily a study of mathematics or a physical science;substitute up to two.</p>"
    tbs = (
        "<p>substitute up to two;may not be counted as engineering courses;EAS 2420 will no longer count as TBS starting in Spring 2025;OIDD 2340 (.5 cu) is for students in the M&amp;T program only.</p>"
        + ul(
            [
                "<strong>EAS:</strong>3010,5050",
                "<strong>OIDD</strong>:2340 (.5 cu),3990 (.5 cu)",
                "<strong>PFP Free</strong>(approved for entered Fall 2020 and later)",
            ]
        )
    )
    return (
        "<main><h1>Student Handbook</h1>"
        + "".join(
            [
                sec(39, "Natural Science Courses", ns),
                sec(36, "Mathematics Courses", math),
                sec(28, "Free Electives", free),
                sec(25, "Engineering Courses", eng),
                sec(54, "Social Sciences and Humanities Breadth", ssh),
                sec(53, "Social Science and Humanities Courses Requirement", sshpolicy),
                sec(59, "Technology in Business and Society Courses", tbs),
            ]
        )
        + "</main>"
    )


def test_classification_lists_not_extra_required_courses():
    r = parse_distributions(fixture())
    assert all(g["kind"] == "note" for g in r["requirements"])
    assert not {"last_verified", "curriculum_audit"} & r.keys()
    courses = {c["code"]: c for c in r["courses"]}
    assert courses["OIDD 2340"]["credits"] == 0.5 and courses["EAS 3010"]["credits"] is None
    assert all(c["name"] is None for c in courses.values())
    assert "HSSC 2004" not in courses and "CIS 2580" not in courses
    assert not any(c["code"].startswith("PFP") for c in courses.values())
    no_credit = next(g for g in r["requirements"] if g["id"].endswith("-no-credit-1"))
    assert "100/101" in no_credit["summary"] and not no_credit["course_ids"]


def test_actual_changed_pool_observed_and_missing_classification_rejected():
    r = parse_distributions(fixture().replace("3010,5050", "3010,5060"))
    assert any(c["code"] == "EAS 5060" for c in r["courses"])
    assert not any(c["code"] == "EAS 5050" for c in r["courses"])
    with pytest.raises(ValueError, match="classification missing"):
        parse_distributions(fixture().replace('id="faq_39"', 'id="other"'))
    with pytest.raises(ValueError, match="subject inventory changed"):
        parse_distributions(
            fixture().replace("<li><strong>Subject 16:</strong> Any course</li>", "")
        )


def test_abroad_approval_is_policy_not_blanket_course_credit():
    h = "<main><h1>Study Abroad</h1><p>minimum of 3.0 cumulative GPA;minimum of 7.0 CUs left;Seniors are not eligible;4.5 CUs;all courses taken abroad must be requested through XCAT;grades will be calculated into the cumulative GPA</p></main>"
    r = parse_abroad(h)
    assert not r["courses"] and len(r["requirements"]) == 3
    with pytest.raises(ValueError):
        parse_abroad(h.replace("3.0 cumulative GPA", "2.5 cumulative GPA"))


def test_curated_degree_preserves_program_college_conflicts():
    j = json.loads((ROOT / "data/programs/penn-bse-ai.json").read_text())
    validate_program(j)
    assert j["curriculum_status"] == "partial"
    assert any("EAS 5050" in gap for gap in j["curriculum_audit"]["unresolved_requirements"])
    assert any("ethics" in gap for gap in j["curriculum_audit"]["unresolved_requirements"])
