import importlib
import json
from pathlib import Path

import pytest

m = importlib.import_module("atlas.adapters.case-applied-ai-minor.adapter")


def test_permission_process_does_not_waive_minor_restrictions():
    html = """<h1>Permissions</h1><h2>Requisites Have Not Been Met</h2><p>Conditions need Requisites Not Met approval.</p><h2>There is a Career Restriction</h2><p>Permission from a registrar or dean is needed.</p>"""
    d = m.parse_permissions(html)
    assert d["curriculum_status"] == "partial"
    assert "not evidence of a blanket" in d["requirements"][0]["summary"]
    with pytest.raises(ValueError, match="authority"):
        m.parse_permissions(html.replace("registrar or dean", "classmate"))


def test_case_minor_retains_specific_unresolved_access_conflict():
    d = json.loads(Path("data/programs/case-applied-ai-minor.json").read_text())
    assert d["curriculum_status"] == "partial" and d["status"] == "unknown"
    gap = " ".join(d["curriculum_audit"]["unresolved_requirements"])
    assert "BUAI 446" in gap and "SCMG 462/463" in gap
    assert {m.PERMISSIONS_URL, m.FACULTY_PERMISSIONS_URL} <= {s["url"] for s in d["sources"]}
