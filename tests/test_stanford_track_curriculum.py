"""Synthetic published-sheet and rendered-Bulletin fragments."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "stanford", ROOT / "atlas/adapters/stanford-ai-track/adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sheet():
    cells = [
        "Artificial Intelligence Track 2026-2027 Program Sheet",
        "Depth; Track and Electives (25 units and seven courses minimum)",
        "Track Requirement B : Two courses, each from a different area: Area I) AI Methods CS 224R, 229; Area II) Natural Language Processing: CS 124; Area III) Vision: CS 131; Area IV) Robotics: CS 123",
        "Track Requirement C : One additional course from the Track Requirement B list, or from the following: CS 157, 329 (any suffix, with advisor approval), ENGR 205",
        "Track Electives : At least three add'l courses selected from the Track Requirement B list, C list, the General CS Electives list, or the following: EE 263, 278; PHIL 152",
        "General CS Electives : 112, 157 (or PHIL 151), 166, 195 (max 4 units), 247 (any suffix), 248 (any suffix), 293 (for 3+ units), 348 (any suffix); CEE 342",
        "Students may replace one track elective with Eligible Humanities Electives.",
        "Any earlier General elective is eligible provided they were a matriculated student that year.",
        "There is no double counting. CS Core, Depth and Senior Project must be approved by the Computer Science office.",
        "Core (15 units minimum); AI Track Core, Depth, and Senior Project (43 units minimum); At least 3 units of 191.",
        "Submit no later than one month prior to the last quarter; edits initialed/dated by SSO.",
    ]
    return (
        '<table class="waffle">'
        + "".join("<tr><th>1</th><td>" + c + "</td></tr>" for c in cells)
        + "</table>"
    )


def test_sheet_observation_preserves_nested_choices_and_shorthand_department():
    data = load().parse_track_sheet(
        sheet().replace("CS 224R, 229", "CS 224R, 228").replace("(25 units", "(26 units")
    )
    ids = {c["code"] for c in data["courses"]}
    assert "CS 228" in ids and "CS 229" not in ids
    assert "PHIL 151" in ids and "CS 166" in ids and "PHIL 166" not in ids
    assert not ids.intersection({"CS 329", "CS 247", "CS 248", "CS 348"})
    assert data["requirements"][0]["credits"] == 26
    assert data["requirements"][2]["count"] == 2
    areas = [r for r in data["requirements"] if "-track-b-area-" in r["id"]]
    assert len(areas) == 4 and all(r["count"] == 1 for r in areas)
    assert all(c["credits"] is None and c["name"] is None for c in data["courses"])
    assert "curriculum_audit" not in data and data["curriculum_status"] == "partial"
    with pytest.raises(ValueError, match="choice or policy"):
        load().parse_track_sheet(
            sheet().replace("Two courses, each from a different area", "Two courses in any area")
        )
    with pytest.raises(ValueError):
        load().parse_track_sheet("<h1>Artificial Intelligence</h1>")


def test_rendered_bulletin_includes_unlinked_courses_and_fails_unresolved_ids():
    html = """<button id="human-header">Optional Humanities Elective Courses</button><div role="region" aria-labelledby="human-header"><p>Students may use up to one course. Cross-listed versions are acceptable.</p><ul><li><span><button>CS120: Example Safety</button></span></li><li><span>ARTSINST142: Example Art</span></li></ul></div>"""
    data = load().parse_bulletin(html)
    assert [c["code"] for c in data["courses"]] == ["CS 120", "ARTSINST 142"]
    assert data["courses"][1]["name"] == "Example Art"
    assert data["requirements"][0]["parent_id"] == "stanford-ai-track-track-electives"
    with pytest.raises(ValueError, match="unresolved"):
        load().parse_bulletin(
            html.replace("CS120: Example Safety", "1050000").replace(
                "ARTSINST142: Example Art", "1050001"
            )
        )


def test_stanford_curated_track_scope_complete_metadata_stays_missing():
    data = json.loads((ROOT / "data/programs/stanford-ai-track.json").read_text())
    validate_program(data)
    assert data["program_kind"] == "concentration" and data["award_level"] == "concentration"
    assert (
        data["curriculum_status"] == "complete"
        and data["curriculum_audit"]["unresolved_requirements"] == []
    )
    assert len(data["courses"]) == 217
    assert any(c["name"] is None for c in data["courses"])
    assert all(c["credits"] is None for c in data["courses"])
    pool = next(r for r in data["requirements"] if r["id"].endswith("-humanities-pool"))
    assert len(pool["course_ids"]) == 86
    assert not any("stanford-cs-329" == c["id"] for c in data["courses"])


def test_stanford_optional_actual_sheet_cache_replay():
    mod = load()
    path = (
        ROOT / ".cache/http" / (hashlib.sha256(mod.TRACK_SHEET_URL.encode()).hexdigest() + ".body")
    )
    if not path.exists():
        pytest.skip("Optional permitted local source cache unavailable")
    data = mod.parse_track_sheet(path.read_text())
    assert len(data["courses"]) == 135
    assert [len(r["course_ids"]) for r in data["requirements"] if "-track-b-area-" in r["id"]] == [
        6,
        4,
        3,
        4,
    ]
