import json

import pytest

from atlas.degree_audit import CHECKS, audit_summary, collect_ledgers, validate_ledger
from tests.test_core_review import program


def entry(status="blocked"):
    p = program()
    return dict(program_id=p["id"], institution_id=p["institution"]["id"], status=status,
                checks={k: "Reviewed the exact official source; remaining boundary recorded." for k in CHECKS},
                sources=[dict(url="https://catalog.example.edu/ai", catalog_year="2026-27",
                    locator="Requirements", checked_at="2026-10-11", access_status="accessible")],
                blockers=["Finite approved elective list requires authentication: https://catalog.example.edu/list"],
                expected_profile=None, second_pass_status="pending")


def test_missing_ledger_is_pending_not_audited_or_absent():
    p = program()
    summary = audit_summary({}, [p, {**p, "id": "minor-ai", "program_kind": "minor"}])
    assert summary["scope_programs"] == summary["pending"] == 1
    assert summary["audited"] == summary["blocked"] == summary["second_pass_verified"] == 0


def test_blocked_correction_does_not_certify_degree_audit():
    summary = audit_summary({"programs": [entry()]}, [program()])
    assert summary["blocked"] == 1
    assert summary["audited"] == summary["pending"] == 0


@pytest.mark.parametrize("change", [
    {"status": "audited"}, {"blockers": []}, {"checks": {}}, {"sources": []},
    {"program_id": "unknown-ai"}, {"institution_id": "other"}, {"status": "fetched"},
])
def test_incomplete_or_mismatched_evidence_is_rejected(change):
    with pytest.raises(ValueError):
        validate_ledger([{**entry(), **change}], [program()])


def test_duplicate_owner_cannot_silently_replace_audit():
    with pytest.raises(ValueError):
        validate_ledger([entry(), entry()], [program()])


def test_ledger_compilation_preserves_evidence_and_separates_second_pass(tmp_path):
    (tmp_path / "owner.json").write_text(json.dumps(dict(audit_date="2026-10-11",
        reviewer="researcher", programs=[entry()])))
    (tmp_path / "independent-review.json").write_text(json.dumps(dict(programs=[entry()])))
    report = collect_ledgers(tmp_path, [program()])
    assert len(report["programs"]) == 1
    assert report["programs"][0]["ledger"] == "research/degree-audit/owner.json"
    assert report["programs"][0]["sources"] == entry()["sources"]
