"""Conservative course-set profiles from an already resolved requirement graph.

These are distinct record counts, never degree proportions or credit-load estimates.
A fixed course has an explicit all-only path. Prose conditions, note containers,
open pools and alternative bundles prevent inferring a student's selected path.
"""

from collections import Counter
from .taxonomy import CATEGORIES, classification_status
CHOICES = {"choose_courses", "choose_credits", "alternative"}


def requirement_profile(program: dict) -> dict:
    """Partition documented course IDs without changing or resolving the input.

    Call after ``families.resolve_program`` (as public database export does).
    A separate fixed occurrence wins over choice/contextual occurrences. Notes
    cannot establish an obligation, even when their descendants have all/choice
    kinds. Unbound records remain unresolved. Choice quantities retain their
    individual source units and conditional context and are never added together.
    """
    courses = {course["id"]: course for course in program.get("courses", [])}
    groups = {group["id"]: group for group in program.get("requirements", [])}
    contexts = {}

    def context(gid, visiting=frozenset()):
        if gid in contexts:
            return contexts[gid]
        if gid not in groups or gid in visiting:
            return "unresolved"
        group = groups[gid]
        parent = group.get("parent_id")
        above = context(parent, visiting | {gid}) if parent else "required"
        if above == "unresolved" or group.get("kind") == "note":
            value = "unresolved"
        elif above == "conditional" or group.get("kind") in CHOICES:
            value = "conditional"
        elif group.get("kind") == "all":
            value = "required"
        else:
            value = "unresolved"
        contexts[gid] = value
        return value

    fixed, options = set(), set()
    memberships = Counter()
    choices = []
    unresolved_groups = 0
    for gid, group in groups.items():
        state = context(gid)
        ids = set(group.get("course_ids", [])) & courses.keys()
        memberships.update(ids)
        if state == "required":
            fixed.update(ids)
        elif state == "conditional":
            options.update(ids)
        else:
            unresolved_groups += 1
        if group.get("kind") in CHOICES:
            parent = group.get("parent_id")
            choices.append({
                "id": gid,
                "title": group.get("title", gid),
                "kind": group["kind"],
                "count": group.get("count"),
                "credits": group.get("credits"),
                "credit_unit": group.get("credit_unit", "unknown"),
                "source_id": group.get("source_id"),
                "parent_id": parent,
                "origin": group.get("origin"),
                "summary": group.get("summary"),
                "context": context(parent) if parent else "required",
            })
    options -= fixed
    unresolved = courses.keys() - fixed - options

    def profile(ids):
        categories = dict.fromkeys(CATEGORIES, 0)
        classification = dict.fromkeys(("reviewed", "mixed", "unclassified", "unreviewed"), 0)
        for cid in ids:
            category = courses[cid].get("category")
            categories[category if category in categories else "other"] += 1
            classification[classification_status(courses[cid])] += 1
        return {"count": len(ids), "categories": categories, "classification": classification}

    return {
        "required": profile(fixed),
        "options": profile(options),
        "unresolved": profile(unresolved),
        "choices": choices,
        "choice_count": len(choices),
        "unresolved_group_count": unresolved_groups,
        # Counts repeated identities, not extra workload or equivalent courses.
        "overlap_count": sum(count > 1 for count in memberships.values()),
    }
