"""Compile explicit research ledgers without mistaking unreviewed for audited."""
import json
from collections import Counter
from pathlib import Path

STATUSES = {"audited", "blocked", "in_progress", "pending"}
CHECKS = {"degree_identity", "required_and_choices", "elective_pools", "prerequisites",
          "credits_and_units", "classification", "family_composition", "degree_wide_requirements"}


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
        if path.name == "independent-review.json":
            continue
        for original in data.get("programs", []):
            entry = {**original, "ledger": f"research/degree-audit/{path.name}",
                     "audit_date": data.get("audit_date"), "reviewer": data.get("reviewer")}
            entries.append(entry)
    validate_ledger(entries, programs)
    return {"audit_date": max((e.get("audit_date") or "" for e in entries), default="2026-10-11"),
            "programs": sorted(entries, key=lambda e: e["program_id"])}


def audit_summary(ledger, programs):
    entries = ledger.get("programs", [])
    validate_ledger(entries, programs)
    lookup = {e["program_id"]: e for e in entries}
    degrees = [p for p in programs if p.get("program_kind") == "degree"]
    counts = Counter(lookup.get(p["id"], {}).get("status", "pending") for p in degrees)
    return {"audit_date": ledger.get("audit_date"), "scope_programs": len(degrees),
            **{k: counts[k] for k in ("audited", "blocked", "in_progress", "pending")},
            "second_pass_verified": sum(e.get("second_pass_status") == "verified" for e in entries),
            "programs": entries}
