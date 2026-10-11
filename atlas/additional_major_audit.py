"""Independent additional-major reviews, separate from whole-degree audits."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from .curriculum_profile import requirement_profile
from .degree_audit import (CORE_DIMENSIONS, CORE_STATUSES, check_expectations,
                           core_review_fingerprint, validate_core_review)


def review_fingerprint(program):
    content = {
        "core": core_review_fingerprint(program),
        **{key: program.get(key) for key in
           ("title", "award_level", "program_kind", "major_relationship")},
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def validate_ledger(ledger, programs):
    lookup = {p["id"]: p for p in programs if p.get("program_kind") == "additional_major"}
    seen = set()
    for row in ledger.get("programs", []):
        pid = row.get("program_id")
        if pid not in lookup or pid in seen:
            raise ValueError(f"Unknown or duplicate additional-major review: {pid}")
        seen.add(pid)
        if row.get("scope") != "additional_major" or not row.get("scope_summary"):
            raise ValueError(f"Additional-major review needs explicit credential scope: {pid}")
        validate_core_review(row, pid)
        eligibility = row.get("eligibility_review", {})
        status = eligibility.get("status")
        if status not in CORE_STATUSES or not eligibility.get("summary"):
            raise ValueError(f"Additional-major review needs eligibility judgment: {pid}")
        if not isinstance(eligibility.get("limitations"), list) or (
                status != "verified" and not eligibility["limitations"]):
            raise ValueError(f"Additional-major eligibility needs exact limitations: {pid}")
        if not eligibility.get("evidence"):
            raise ValueError(f"Additional-major eligibility needs source evidence: {pid}")
        for evidence in eligibility["evidence"]:
            if not evidence.get("url", "").startswith(("https://", "http://")) or not evidence.get("locator"):
                raise ValueError(f"Additional-major eligibility needs exact source locator: {pid}")
        program = lookup[pid]
        if review_fingerprint(program) != row["reviewed_content_hash"]:
            raise ValueError(f"Additional-major review resolved content is stale: {pid}")
        actual = requirement_profile(program, include_course_ids=True)
        check_expectations(row.get("expected_profile") or {}, actual, pid, "Additional-major review")
        for role, ids in (row.get("expected_course_ids") or {}).items():
            if ids is None:
                continue
            if role not in actual["course_ids"] or len(ids) != len(set(ids)) or set(ids) != set(actual["course_ids"][role]):
                raise ValueError(f"Additional-major review exact identities are stale: {pid} {role}")
        subset = row.get("reviewed_option_subset")
        if subset is not None and not set(subset).issubset(actual["course_ids"]["options"]):
            raise ValueError(f"Additional-major review option subset is stale: {pid}")


def collect_ledgers(directory, programs):
    rows = []
    for path in sorted(Path(directory).glob("additional-major-review-*.json")):
        for row in json.loads(path.read_text()).get("programs", []):
            rows.append({**row, "ledger": f"research/{path.name}"})
    result = {"programs": sorted(rows, key=lambda row: row["program_id"])}
    validate_ledger(result, programs)
    return result


def audit_summary(ledger, programs):
    validate_ledger(ledger, programs)
    rows = ledger.get("programs", [])
    lookup = {row["program_id"]: row for row in rows}
    scoped = [p for p in programs if p.get("program_kind") == "additional_major"]
    dimensions = {}
    for key in (*CORE_DIMENSIONS, "eligibility"):
        counts = Counter()
        for program in scoped:
            row = lookup.get(program["id"], {})
            dimension = row.get("eligibility_review", {}) if key == "eligibility" else row.get("dimensions", {}).get(key, {})
            counts[dimension.get("status", "not_reviewed")] += 1
        dimensions[key] = dict(counts)
    return {"scope_programs": len(scoped), "reviewed_programs": len(rows),
            "dimensions": dimensions, "programs": rows}
