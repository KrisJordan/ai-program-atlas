"""Synthetic layouts exercise observed policies; no downloaded catalog fixtures."""

import importlib.util
import json
from pathlib import Path

import pytest

from atlas.adapters.tulane_policies import parse_ntc, parse_sse
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
PID = "tulane-ai-literacy-minor"


def load():
    spec = importlib.util.spec_from_file_location(
        "literacy", ROOT / "atlas/adapters" / PID / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fixture():
    def head(label, count, credit):
        return f'<tr class="areaheader"><td><span class="courselistcomment">{label}</span><sup>{count}</sup></td><td class="hourscol">{credit}</td></tr>'

    def course(code, alt=False):
        return f'<tr class="{"orclass" if alt else ""}"><td><a class="code" href="/example">{code}</a></td><td>Test {code}</td><td class="hourscol"></td></tr>'

    equivalent = "<tr><td>Other equivalent course, approval of the AI Literacy Minor Faculty Steering Committee</td></tr>"
    return (
        '<h1>Artificial Intelligence (AI) Literacy Minor</h1><h2>2026-2027 Edition</h2><div id="requirementstextcontainer"><p>requires 15 credit hours with minimum 2.000 grade point average. Only three credit hours can overlap a major; no minor and a certificate overlap.</p><table class="sc_courselist">'
        + head("Foundational Requirement", "1 course, 3 credit hours", 3)
        + course("DATA 2350")
        + head("AI and Society Electives", "Choose two (2) of the following:", 6)
        + course("BUSG 4360")
        + course("ENGP 3460", True)
        + course("DATA 4030")
        + equivalent
        + head("Problem Solving with AI Electives", "Choose two (2) of the following:", 6)
        + course("CMPS 1100")
        + course("CMPS 1500", True)
        + course("DATA 2150")
        + equivalent
        + "</table></div>"
    )


def test_literacy_or_pairs_and_blanks():
    data = load().parse(fixture().replace("Test DATA 2350", "Changed title"))
    assert data["courses"][0]["name"] == "Changed title"
    assert all(c["credits"] is None for c in data["courses"])
    alts = [r for r in data["requirements"] if r["kind"] == "alternative"]
    assert len(alts) == 2 and all(len(r["course_ids"]) == 2 for r in alts)
    assert [r["count"] for r in data["requirements"] if r["kind"] == "choose_courses"] == [2, 2]
    assert data["curriculum_status"] == "partial" and "curriculum_audit" not in data
    with pytest.raises(ValueError, match="Unrecognized literacy option"):
        load().parse(
            fixture().replace(
                "Other equivalent course, approval of the AI Literacy Minor Faculty Steering Committee",
                "Other courses",
            )
        )
    with pytest.raises(ValueError, match="heading"):
        load().parse(
            fixture().replace(
                "Artificial Intelligence (AI) Literacy Minor", "Artificial Intelligence Minor"
            )
        )


def test_tulane_policies_require_evidence_and_respect_scope():
    ntc = """<h1>Newcomb-Tulane College</h1><h3>Minor Component</h3><p>grade-point average of at least 2.000 in courses counting toward that minor. No courses counting toward the student's first minor count in the second. Students may not count the same course(s) toward a minor and a certificate. The S/U option may not be employed for major or minor requirements. Credit Expiration: ten years from most recent admission or readmission; continuously enrolled exception. Transfer: prior approval, official transcript, C or better; Grades are not transferred.</p>"""
    data = parse_ntc(ntc.replace("at least 2.000", "at least 2.500"), PID)
    assert "2.500" in data["requirements"][0]["summary"]
    assert len(data["requirements"]) == 5
    with pytest.raises(ValueError):
        parse_ntc(ntc.replace("ten years", "unlimited"), PID)
    sse = """<h1>School of Science and Engineering</h1><p>Major/Minor Declaration Form, Department Chair approval, Newcomb-Tulane advisor. Students may have one or two minors; 24 credits of the major separate, 2.000 GPA; second minor or towards a certificate cannot overlap.</p>"""
    data = parse_sse(sse, PID)
    assert len(data["requirements"]) == 2
    assert "24 major credits" in data["requirements"][1]["summary"]
    assert all("half" not in r["summary"] for r in data["requirements"])
    assert len(load().parse_school(sse)["requirements"]) == 1  # NTC minor not declared through SSE


def test_curated_minor_identity_and_honest_status():
    data = json.loads((ROOT / "data/programs" / f"{PID}.json").read_text())
    validate_program(data)
    assert data["curriculum_status"] == "partial"
    assert data["institution"]["id"] == "tulane-university-of-louisiana"
    assert len(data["courses"]) == 14 and data["first_offered"] is None
    c = next(c for c in data["courses"] if c["code"] == "CMPS 1500")
    assert c["credits"] == 4 and "1501" in c["prerequisites"]
    assert any("four-credit" in x for x in data["curriculum_audit"]["unresolved_requirements"])
