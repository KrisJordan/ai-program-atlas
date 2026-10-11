"""Explicit source-reviewed cross-listings; never infer aliases from names/codes."""
from datetime import date


def identity_map(program):
    result = {c["id"]: c["id"] for c in program.get("courses", [])}
    for group in program.get("course_identity_groups", []):
        for cid in group["course_ids"]:
            result[cid] = group["canonical_course_id"]
    return result


def validate_course_identities(program):
    courses = {c["id"]: c for c in program.get("courses", [])}
    sources = {s["id"] for s in program.get("sources", [])}
    used, gids = set(), set()
    for group in program.get("course_identity_groups", []):
        gid = group.get("id")
        if not isinstance(gid, str) or not gid.strip() or gid in gids:
            raise ValueError("Course identity groups need unique IDs")
        gids.add(gid)
        if group.get("relation") != "crosslisted":
            raise ValueError("Only source-proven cross-listings establish course identity")
        ids = group.get("course_ids")
        if (not isinstance(ids, list) or len(ids) < 2
                or any(not isinstance(cid, str) or cid not in courses for cid in ids)
                or len(set(ids)) != len(ids) or used.intersection(ids)):
            raise ValueError("Course identity groups need disjoint existing course IDs")
        used.update(ids)
        canonical = group.get("canonical_course_id")
        if canonical not in ids:
            raise ValueError("Canonical course must belong to its identity group")
        evidence = group.get("source_ids")
        if (not isinstance(evidence, list) or not evidence
                or any(not isinstance(sid, str) or sid not in sources for sid in evidence)
                or len(set(evidence)) != len(evidence)):
            raise ValueError("Course identity needs unique registered sources")
        for field in ("locator", "rationale"):
            if not isinstance(group.get(field), str) or not group[field].strip():
                raise ValueError(f"Course identity needs {field}")
        try:
            date.fromisoformat(group.get("reviewed_at", ""))
        except (ValueError, TypeError):
            raise ValueError("Course identity needs an ISO review date") from None
        reviewed = {courses[cid].get("category") for cid in ids
                    if (courses[cid].get("category_review") or {}).get("status") == "reviewed"}
        if len(reviewed) > 1 or (reviewed and courses[canonical].get("category") not in reviewed):
            raise ValueError("Cross-listed subject reviews conflict with canonical classification")
