import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug, ROOT / "atlas" / "adapters" / slug / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_columbia_minor_requires_local_minor_context():
    parse = load("columbia-ai-minor").parse
    assert (
        parse("<main><h2>Minor in Artificial Intelligence</h2><p>Six courses.</p></main>")[
            "program_kind"
        ]
        == "minor"
    )
    with pytest.raises(ValueError):
        parse("<main><h2>Artificial Intelligence</h2><p>Research only.</p></main>")


def test_stanford_formal_concentration_not_standalone_bs():
    parse = load("stanford-ai-track").parse
    row = parse(
        "<main><h3>Artificial Intelligence</h3><p>Topics in the AI concentration include reasoning.</p></main>"
    )
    assert row["award_level"] == row["program_kind"] == "concentration"
    assert row["title"].endswith("(CS BS track)")
    assert "last_verified" not in row
    with pytest.raises(ValueError):
        parse("<main><h3>Artificial Intelligence</h3><p>An optional area of interest.</p></main>")


def test_additional_survey_integrity():
    rows = json.loads((ROOT / "data/surveys/national-additional.json").read_text())
    cohort = {i["id"] for i in json.loads((ROOT / "data/cohort.json").read_text())["institutions"]}
    assert len(rows) == len({r["institution_id"] for r in rows}) == 25
    assert all(r["institution_id"] in cohort and r["sources"] for r in rows)
    assert all(r["status"] != "no_qualifying_program_found" for r in rows)
    assert sum(r["status"] == "confirmed" for r in rows) == 2
    for pid in ["columbia-ai-minor", "stanford-ai-track"]:
        p = json.loads((ROOT / "data/programs" / (pid + ".json")).read_text())
        assert p["curriculum_status"] == "pending"
        assert not p["courses"] and not p["requirements"]
