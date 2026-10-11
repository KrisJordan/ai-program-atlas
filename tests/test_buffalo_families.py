"""Preserve the university-described framework without inventing course equivalence."""

import json
from pathlib import Path
import pytest
from atlas import db
from atlas.families import resolve_program
from atlas.family_store import ingest_family

ROOT = Path(__file__).resolve().parents[1]
FID = "buffalo-ai-plus-x-degrees"
EXPECTED = {
    "university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree": "cd4281f19f4df28873efb40d4116110a476716ce284b601db4d91aa4b98e7ba3",
    "university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree": "fa05e54839152c1d58cf308485c989bd47848122cc9b055fcd7b96807b97a5a5",
    "university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree": "38a6fd5f700ec0d6e70ade70ca4a4a68dfabd7f27ef2d28d98aed3ec305b06c2",
    "university-at-buffalo-suny-ai-and-language-technology-bs-degree": "c714f05636c3c31f0f01fe52b4269e5d1514e01a61de5de894d920708b47bdc4",
    "university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree": "dcb5c671c145f93557fe81d4c3a2bb5fb90e1b56169f92de1797b84fc36f0a4f",
    "university-at-buffalo-suny-ai-and-policy-analysis-bs-degree": "a29c82e7b69c2315781e6ea0512199d03e0de24049aa6bc658c572200ff7af5b",
    "university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree": "ddf881c862acb6a25d9210fe09a5c75c515396747fce05635d9d5e4ea82bdedb",
    "university-at-buffalo-suny-ai-and-responsible-communication-bs-degree": "6cdbf33bee6e2c979eb86c686adf336a29f15aadf5a0c44abc6f6f7ba9ed2fc5",
}
ANNOTATIONS = {
    "origin",
    "component",
    "component_classification",
    "family_requirement_id",
    "family_source_id",
}


@pytest.mark.parametrize("pid", EXPECTED)
def test_buffalo_framework_preserves_exact_reviewed_graph_and_gaps(pid):
    family = json.loads((ROOT / "data/families" / f"{FID}.json").read_text())
    program = json.loads((ROOT / "data/programs" / f"{pid}.json").read_text())
    db.validate_program(program, family)
    resolved = resolve_program(program, family)
    rows = [{k: v for k, v in r.items() if k not in ANNOTATIONS} for r in resolved["requirements"] if not r["id"].startswith("buffalo-ubc-") and "-department-" not in r["id"]]
    assert db.digest(sorted(rows, key=lambda r: r["id"])) == EXPECTED[pid]
    assert len([r for r in resolved["requirements"] if r["origin"] == "family"]) == 5
    assert all(c["id"].startswith(("buffalo-ubc-", "buffalo-ai-qe-title-")) for c in resolved["courses"])
    # Independent general education additions do not change the original major framework.
    assert resolved["curriculum_status"] == "partial"
    assert resolved["curriculum_audit"]["unresolved_requirements"]
    assert resolved["family"]["relationship"] == "ai_plus_x"
    assert resolved["family"]["classification_kind"] == "source_stated"
    assert all(r["credits"] is None for r in family["shared_requirements"])


def test_buffalo_family_stores_only_five_framework_definitions(tmp_path):
    conn = db.connect(tmp_path / "atlas.sqlite")
    db.migrate(conn)
    family = json.loads((ROOT / "data/families" / f"{FID}.json").read_text())
    programs = {
        pid: json.loads((ROOT / "data/programs" / f"{pid}.json").read_text()) for pid in EXPECTED
    }
    for program in programs.values():
        db.upsert_institution(conn, program["institution"])
    assert ingest_family(conn, family, program_updates=programs)
    assert not ingest_family(conn, family, program_updates=programs)
    assert conn.execute("SELECT count(*) FROM family_requirement_groups").fetchone()[0] == 5
    assert conn.execute("SELECT count(*) FROM family_requirement_bindings").fetchone()[
        0
    ] == 5 * len(EXPECTED)
    data = db.export_data(conn)
    assert len(data["programs"]) == len(EXPECTED)
    assert data["families"][0]["shared_course_codes"] == []
    assert data["meta"]["curriculum_summary"]["pending"] == 0
    assert data["meta"]["curriculum_summary"]["complete"] == 0
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
