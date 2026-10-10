import json
from pathlib import Path
import pytest
from atlas.adapters.tufts_minor_paperwork import parse_paperwork
from atlas.db import validate_program

ROOT = Path(__file__).resolve().parents[1]
PID = "tufts-application-ai-minor"


def fixture():
    return '<main><h1>Instructions for Graduation Paperwork</h1><ul><li class="accordion-item"><h3>All Minors (SoE and A&amp;S)</h3><p>Fill out and sign. Use “IP” and “TBD”. Save Lastname Firstname CS minor checklist. The form is reviewed, signed, and returned to you via email for the rest of your graduation packet.</p><a href="https://tufts.app.box.com/f/public-form">CS minor Box folder</a></li><li class="accordion-item"><h3>SOE BSCS Majors</h3><p>Unrelated major-specific approval rule.</p></li></ul></main>'


def test_minors_procedure_excludes_other_program_rules_and_no_audit():
    result = parse_paperwork(fixture(), pid=PID)
    assert len(result["requirements"]) == 1
    assert "major-specific" not in result["requirements"][0]["summary"]
    assert result["observed_submission_url"] == "https://tufts.app.box.com/f/public-form"
    assert not {"last_verified", "curriculum_audit"} & result.keys()
    assert result["curriculum_status"] == "partial"


def test_wrong_scope_or_changed_required_procedure_rejected():
    with pytest.raises(ValueError, match="All-minors"):
        parse_paperwork(fixture().replace("All Minors (SoE and A&amp;S)", "All Majors"), pid=PID)
    with pytest.raises(ValueError, match="procedure changed"):
        parse_paperwork(fixture().replace("and sign.", "no signature."), pid=PID)


def test_checklist_evidence_completes_application_but_preserves_development_conflict():
    app = json.loads((ROOT / "data/programs/tufts-application-ai-minor.json").read_text())
    dev = json.loads((ROOT / "data/programs/tufts-ai-development-minor.json").read_text())
    for seed in [app, dev]:
        validate_program(seed)
        check = next(s for s in seed["sources"] if s["id"].endswith("-checklist"))
        assert check["source_date"] is None and check["catalog_year"] is None
        assert "pdf" in check["title"]
        assert any(r["id"].endswith("-checklist-overlap") for r in seed["requirements"])
    assert (
        app["curriculum_status"] == "complete"
        and not app["curriculum_audit"]["unresolved_requirements"]
    )
    assert (
        dev["curriculum_status"] == "partial"
        and len(dev["curriculum_audit"]["unresolved_requirements"]) == 1
    )
    # Preserve the department-published alternative; discrepancy cannot silently erase it.
    assert any(c["code"] == "EE 140/CS 128" for c in dev["courses"])
    assert any(r["id"].endswith("-checklist-ml-discrepancy") for r in dev["requirements"])
