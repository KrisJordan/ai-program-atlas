"""Synthetic, deliberately non-catalog fixtures for Buffalo source boundaries."""

import importlib.util
import json
from pathlib import Path

import pytest

from atlas.adapters.buffalo_overview import parse_degree, parse_family, parse_minor
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "university-at-buffalo-suny-"


def test_family_is_explicit_not_title_inference():
    html = "<h2>All AI+X degrees consist of the following components</h2><ul><li>Mathematical prerequisites vary.</li><li>Society Core: five three-credit courses.</li><li>Technology Component: four-credit courses.</li><li>Integrative Courses in the partner field.</li><li>Capstone Experience with other students.</li></ul><p>AI and Example</p>"
    d = parse_family(html, "example", "AI and Example")
    assert len(d["requirements"]) == 5
    assert all(r["kind"] == "note" and r["credits"] is None for r in d["requirements"])
    assert d["curriculum_status"] == "partial"
    with pytest.raises(ValueError, match="rule changed"):
        parse_family(
            html.replace("five three-credit", "six three-credit"), "example", "AI and Example"
        )
    with pytest.raises(ValueError, match="member missing"):
        parse_family(html, "example", "AI and Different")
    assert "last_verified" not in d and "curriculum_audit" not in d


def test_program_observes_roles_and_capstone():
    html = "<h1>AI and Example</h1><h2>What will I learn?</h2><p>Complete an applied capstone.</p><h2>What can I do with an AI and Example degree?</h2><ul><li>Example analyst.</li><li>Example developer.</li></ul><h2>Another section</h2><ul><li>Not a career.</li></ul>"
    d = parse_degree(html, "example", "AI and Example", "https://www.buffalo.edu/example")
    assert [o["text"] for o in d["outcomes"]] == ["Example analyst", "Example developer"]
    assert len(d["requirements"]) == 1
    assert "courses" not in d
    with pytest.raises(ValueError, match="heading"):
        parse_degree(html, "example", "Wrong Name", "unused")


def test_minor_approximation_stays_non_numeric():
    d = parse_minor(
        "<h1>Minor in AI Ethics</h1><p>requires approximately 24 credits</p>", "ethics", "AI Ethics"
    )
    assert "24 credits" in d["requirements"][0]["summary"]
    assert d["requirements"][0]["credits"] is None
    with pytest.raises(ValueError, match="Approximate"):
        parse_minor("<h1>Minor in AI Ethics</h1>", "ethics", "AI Ethics")
    d = parse_minor(
        "<h1>Minor in Artificial Intelligence, Crime and Society</h1><p>CAS Major/Minor Change Request</p>",
        "crime",
        "Artificial Intelligence, Crime and Society",
    )
    assert d["requirements"][0]["id"] == "crime-declaration"


def test_reviewed_buffalo_records_preserve_gaps():
    for path in (ROOT / "data/programs").glob(PREFIX + "*.json"):
        d = json.loads(path.read_text())
        if not d.get("curriculum_audit"):
            continue
        family = (
            json.loads((ROOT / "data/families" / (d["family"]["id"] + ".json")).read_text())
            if d.get("family")
            else None
        )
        validate_program(d, family)
        assert d["curriculum_status"] == "partial"
        assert d["courses"] == []
        assert d["curriculum_audit"]["unresolved_requirements"]
        spec = importlib.util.spec_from_file_location(
            d["id"], ROOT / "atlas/adapters" / d["id"] / "adapter.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.PROGRAM_ID == d["id"]
        if d["program_kind"] == "degree":
            assert len(module.SOURCE_PARSERS) == 2


def test_program_specific_language_and_internship_rules():
    title = "AI and Language and Intercultural Competence"
    html = (
        "<h1>"
        + title
        + "</h1><h2>What will I learn?</h2><p>A capstone. You can choose from Example Language, Other Language—as you take advanced courses.</p><h2>What can I do with an "
        + title
        + " degree?</h2><p>Several paths.</p>"
    )
    d = parse_degree(html, "language", title, "unused")
    assert "Example Language, Other Language" in d["requirements"][-1]["summary"]
    with pytest.raises(ValueError, match="options"):
        parse_degree(html.replace("choose from", "consider"), "language", title, "unused")
    title = "AI and Logic and Ontology"
    html = (
        "<h1>"
        + title
        + "</h1><h2>What will I learn?</h2><p>An internship and capstone.</p><h2>What can I do with an "
        + title
        + " degree?</h2><p>Several paths.</p>"
    )
    assert (
        parse_degree(html, "logic", title, "unused")["requirements"][-1]["id"] == "logic-internship"
    )
    with pytest.raises(ValueError, match="Internship"):
        parse_degree(html.replace("internship", "project"), "logic", title, "unused")
