"""Validate requirement trees without inventing equivalence or degree totals."""

from datetime import date


def validate_curriculum_audit(program: dict) -> None:
    """Require an explicit evidence review before declaring an inventory complete."""
    status = program.get("curriculum_status", "pending")
    if status not in {"pending", "partial", "complete"}:
        raise ValueError("Unknown curriculum status")
    audit = program.get("curriculum_audit")
    if audit is None:
        if status == "complete":
            raise ValueError("Complete curriculum requires a review audit")
        return
    if not isinstance(audit, dict) or audit.get("scope") != program.get("program_kind"):
        raise ValueError("Curriculum audit scope must match the represented program")
    try:
        reviewed = audit["reviewed_at"]
        if date.fromisoformat(reviewed).isoformat() != reviewed:
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        raise ValueError("Curriculum audit needs an ISO review date") from None
    for field in ("source_ids", "sections", "unresolved_requirements", "metadata_gaps"):
        values = audit.get(field)
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"Curriculum audit {field} must be a list of nonempty strings")
    if not audit["source_ids"] or not audit["sections"]:
        raise ValueError("Curriculum audit needs sources and reviewed sections")
    if len(audit["source_ids"]) != len(set(audit["source_ids"])):
        raise ValueError("Duplicate curriculum audit source")
    registered = {source["id"] for source in program.get("sources", [])}
    if not set(audit["source_ids"]) <= registered:
        raise ValueError("Curriculum audit references an unknown source")
    if status == "complete":
        if audit["unresolved_requirements"]:
            raise ValueError("Complete curriculum cannot have unresolved requirements")
        if not program.get("requirements"):
            raise ValueError("Complete curriculum needs a requirement inventory")


def validate_requirements(program: dict) -> None:
    courses = {c["id"] for c in program.get("courses", [])}
    groups_list = program.get("requirements", [])
    groups = {g["id"]: g for g in groups_list}
    if len(groups) != len(groups_list):
        raise ValueError("Duplicate requirement IDs")
    for gid, group in groups.items():
        kind = group["kind"]
        if kind not in {"all", "choose_courses", "choose_credits", "alternative", "note"}:
            raise ValueError(f"Unknown requirement kind: {kind}")
        if kind == "choose_courses" and (
            not isinstance(group.get("count"), int) or group["count"] <= 0
        ):
            raise ValueError(f"{gid}: choose_courses requires positive integer count")
        if kind == "choose_credits" and (group.get("credits") is None or group["credits"] <= 0):
            raise ValueError(f"{gid}: choose_credits requires positive credits")
        if kind == "choose_credits" and group.get("credit_unit", "unknown") == "unknown":
            raise ValueError(f"{gid}: credit choice requires known unit")
        if len(group.get("course_ids", [])) != len(set(group.get("course_ids", []))):
            raise ValueError(f"{gid}: duplicate course membership")
        for cid in group.get("course_ids", []):
            if cid not in courses:
                raise ValueError(f"{gid}: missing course {cid}")
        visited = {gid}
        parent = group.get("parent_id")
        while parent:
            if parent not in groups:
                raise ValueError(f"{gid}: missing parent {parent}")
            if parent in visited:
                raise ValueError(f"{gid}: requirement cycle")
            visited.add(parent)
            parent = groups[parent].get("parent_id")


def describe_rule(group: dict) -> str:
    kind = group["kind"]
    if kind == "choose_courses":
        return f"Choose {group['count']} courses"
    if kind == "choose_credits":
        return f"Choose {group['credits']:g} {group['credit_unit'].replace('_', ' ')}"
    return {
        "all": "All listed requirements",
        "alternative": "Choose an alternative",
        "note": "See source rule",
    }[kind]


def observed_category_counts(program: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    seen = set()
    for course in program.get("courses", []):
        if course["id"] in seen:
            continue
        seen.add(course["id"])
        category = course.get("category", "other")
        counts[category] = counts.get(category, 0) + 1
    return counts
