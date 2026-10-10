"""Validate requirement trees without inventing equivalence or degree totals."""


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
