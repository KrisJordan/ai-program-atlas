"""Synthetic curriculum fixtures for the NJIT/Lehigh/Drexel degree batch."""

import importlib.util
import json
from pathlib import Path

import pytest

from atlas.db import validate_program
from atlas.requirements import validate_requirements

ROOT = Path(__file__).resolve().parents[1]
NJIT = "new-jersey-institute-of-technology-business-with-ai-bs-degree"


def load(pid):
    spec = importlib.util.spec_from_file_location(pid, ROOT / "atlas/adapters" / pid / "adapter.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_njit_observed_plan_preserves_zero_and_open_slots():
    html = '<h1>University Catalog</h1><h1>Business with AI</h1><p>(120 credit minimum)</p><table class="sc_plangrid"><tr class="plangridyear"><th>First Year</th></tr><tr class="plangridterm"><th>1st Semester</th></tr><tr><td class="codecol"><a class="code" href="/search/?P=FYS%20SEM">FYS SEM</a></td><td class="titlecol">Example Seminar</td><td class="hourscol">0</td></tr><tr><td class="codecol" colspan="2">Example GER</td><td class="hourscol">3</td></tr><tr class="plangridsum"><td>Term credits</td><td class="hourscol">3</td></tr></table>'
    d = load(NJIT).parse(html)
    assert d["courses"][0]["credits"] == 0
    assert d["requirements"][-1]["kind"] == "note"
    assert d["requirements"][-1]["credits"] == 3
    assert d["requirements"][-1]["parent_id"] == d["requirements"][1]["id"]
    assert "curriculum_audit" not in d and "last_verified" not in d
    with pytest.raises(ValueError, match="minimum"):
        load(NJIT).parse(html.replace("(120 credit minimum)", ""))
    with pytest.raises(ValueError, match="credit"):
        load(NJIT).parse(html.replace(">0</td>", ">unknown</td>"))


def test_reviewed_five_degree_records_validate():
    for pid in [
        NJIT,
        "lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree",
        "drexel-ai-ml-bs",
        "delaware-ai-engineering-major",
        "stevens-institute-of-technology-artificial-intelligence-bs-degree",
    ]:
        d = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
        validate_program(d)
        validate_requirements(d)
        if d.get("curriculum_audit"):
            assert d["curriculum_status"] == "partial"
            assert d["curriculum_audit"]["unresolved_requirements"]
