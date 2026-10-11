"""Compile explicit research ledgers without mistaking unreviewed for audited."""
import json
import hashlib
from collections import Counter
from pathlib import Path

STATUSES = {"audited", "blocked", "in_progress", "pending"}
CHECKS = {"degree_identity", "required_and_choices", "elective_pools", "prerequisites",
          "credits_and_units", "classification", "family_composition", "degree_wide_requirements"}
CORE_DIMENSIONS = ("fixed_requirements", "choice_rules", "classification")
CORE_STATUSES = {"verified", "partial", "unverified"}


def core_review_fingerprint(program):
    """Pin a manual review to resolved facts, including unchanged-count choice edits.

    This detects stale evidence; generating a digest is never a source review.
    Optional public course-site links and refresh timestamps do not certify or
    invalidate curriculum judgments. Exact source identities and editions do.
    """
    course_keys = ("id", "code", "name", "description", "prerequisites", "credits",
                   "credit_unit", "category", "category_review", "source_id", "notes")
    content = {
        "id": program["id"], "catalog_year": program.get("catalog_year"),
        "requirements": program.get("requirements", []),
        "courses": [{k: c.get(k) for k in course_keys} for c in program.get("courses", [])],
        "course_identity_groups": program.get("course_identity_groups", []),
        "sources": [{k: s.get(k) for k in ("id", "url", "catalog_year", "locator")}
                    for s in program.get("sources", [])],
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def validate_core_review(review, pid):
    if review.get("program_id") != pid or not review.get("reviewer") or not review.get("reviewed_at"):
        raise ValueError(f"Core review needs program, reviewer and date: {pid}")
    dimensions = review.get("dimensions", {})
    if set(dimensions) != set(CORE_DIMENSIONS):
        raise ValueError(f"Core review needs three separate dimensions: {pid}")
    for dimension in dimensions.values():
        status = dimension.get("status")
        if status not in CORE_STATUSES or not dimension.get("summary"):
            raise ValueError(f"Invalid core review dimension: {pid}")
        if not isinstance(dimension.get("limitations"), list):
            raise ValueError(f"Core review needs explicit limitations: {pid}")
        if status != "verified" and not dimension["limitations"]:
            raise ValueError(f"Partial core review needs exact scope limitations: {pid}")
        if not dimension.get("evidence"):
            raise ValueError(f"Core review needs source evidence: {pid}")
        for source in dimension["evidence"]:
            if not source.get("url", "").startswith(("https://", "http://")) or not source.get("locator"):
                raise ValueError(f"Core review needs exact source locator: {pid}")
    fingerprint = review.get("reviewed_content_hash")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
        raise ValueError(f"Core review needs a pinned resolved-content digest: {pid}")


def check_expectations(expected, actual, pid, label):
    """Null category totals remain unverified; never silently compare them to zero."""
    for role in ("required", "options", "unresolved"):
        counts = expected.get(role)
        if counts is None:
            continue
        if counts.get("count") != actual[role]["count"]:
            raise ValueError(f"{label} profile is stale: {pid} {role}")
        if counts.get("categories") is not None:
            from .taxonomy import CATEGORIES
            if any(counts["categories"].get(c, 0) != actual[role]["categories"][c] for c in CATEGORIES):
                raise ValueError(f"{label} profile is stale: {pid} {role}")


def validate_ledger(entries, programs):
    degrees = {p["id"]: p for p in programs if p.get("program_kind") == "degree"}
    seen = set()
    for entry in entries:
        pid = entry.get("program_id")
        if pid not in degrees or pid in seen:
            raise ValueError(f"Unknown or duplicate degree audit program: {pid}")
        seen.add(pid)
        if entry.get("institution_id") != degrees[pid]["institution"]["id"]:
            raise ValueError(f"Degree audit institution mismatch: {pid}")
        status = entry.get("status")
        if status not in STATUSES:
            raise ValueError(f"Invalid degree audit status: {pid}")
        if entry.get("core_review") is not None:
            validate_core_review(entry["core_review"], pid)
        if status in {"audited", "blocked"}:
            checks = entry.get("checks", {})
            if any(not isinstance(checks.get(k), str) or not checks[k].strip() for k in CHECKS):
                raise ValueError(f"Degree audit needs every evidence check: {pid}")
            if not entry.get("sources"):
                raise ValueError(f"Degree audit needs exact sources: {pid}")
            for source in entry["sources"]:
                if not source.get("url", "").startswith(("https://", "http://")):
                    raise ValueError(f"Degree audit source needs HTTP URL: {pid}")
                if not source.get("locator") or not source.get("checked_at") or not source.get("access_status"):
                    raise ValueError(f"Degree audit source needs checked locator/access: {pid}")
            if status == "audited" and (entry.get("blockers") or not entry.get("expected_profile")):
                raise ValueError(f"Audited degree cannot have unresolved evidence or missing expected profile: {pid}")
            if status == "blocked" and not entry.get("blockers"):
                raise ValueError(f"Blocked degree needs exact missing evidence: {pid}")


def collect_ledgers(directory, programs):
    entries = []
    for path in sorted(Path(directory).glob("*.json")):
        data = json.loads(path.read_text())
        # Independent review has a separate schema; it must not replace primary audits.
        if path.name.startswith("independent-"):
            continue
        for original in data.get("programs", []):
            entry = {**original, "ledger": f"research/degree-audit/{path.name}",
                     "audit_date": data.get("audit_date"), "reviewer": data.get("reviewer")}
            entries.append(entry)
    lookup = {e["program_id"]: e for e in entries}
    reviewed = set()
    for path in sorted(Path(directory).glob("independent-core-*.json")):
        for original in json.loads(path.read_text()).get("programs", []):
            pid = original.get("program_id")
            if pid not in lookup or pid in reviewed:
                raise ValueError(f"Unknown or duplicate core review program: {pid}")
            reviewed.add(pid)
            lookup[pid]["core_review"] = {**original, "ledger": f"research/degree-audit/{path.name}"}
    validate_ledger(entries, programs)
    return {"audit_date": max((e.get("audit_date") or "" for e in entries), default="2026-10-11"),
            "programs": sorted(entries, key=lambda e: e["program_id"])}


def audit_summary(ledger, programs):
    entries = ledger.get("programs", [])
    validate_ledger(entries, programs)
    lookup = {e["program_id"]: e for e in entries}
    # The export supplies family-resolved programs. Compare independent manual
    # expectations to the exact graph being published, including partial scopes.
    from .curriculum_profile import requirement_profile
    for program in programs:
        entry = lookup.get(program["id"], {})
        expected = entry.get("expected_profile")
        review = entry.get("core_review")
        if not expected and not review:
            continue
        actual = requirement_profile(program, include_course_ids=bool(review))
        if expected:
            check_expectations(expected, actual, program["id"], "Independent degree audit")
        if review:
            if core_review_fingerprint(program) != review["reviewed_content_hash"]:
                raise ValueError(f"Core review resolved content is stale: {program['id']}")
            check_expectations(review.get("expected_profile") or {}, actual, program["id"], "Core review")
            for role, ids in (review.get("expected_course_ids") or {}).items():
                if ids is None:
                    continue
                if role not in actual["course_ids"] or len(ids) != len(set(ids)) or set(ids) != set(actual["course_ids"][role]):
                    raise ValueError(f"Core review exact identities are stale: {program['id']} {role}")
            subset = review.get("reviewed_option_subset")
            if subset is not None and not set(subset).issubset(actual["course_ids"]["options"]):
                raise ValueError(f"Core review option subset is stale: {program['id']}")
    degrees = [p for p in programs if p.get("program_kind") == "degree"]
    counts = Counter(lookup.get(p["id"], {}).get("status", "pending") for p in degrees)
    return {"audit_date": ledger.get("audit_date"), "scope_programs": len(degrees),
            **{k: counts[k] for k in ("audited", "blocked", "in_progress", "pending")},
            "second_pass_verified": sum(e.get("second_pass_status") == "verified" for e in entries),
            "core_review_dimensions": {
                key: dict(Counter(lookup.get(p["id"], {}).get("core_review", {}).get("dimensions", {}).get(key, {}).get("status", "not_reviewed") for p in degrees))
                for key in CORE_DIMENSIONS},
            "programs": entries}
