"""Evidence-reviewed subject taxonomy, separate from requirement role.

This module validates recorded human judgments; it does not infer categories from
titles, course prefixes, requirement pools, or the name of a degree.
"""
from datetime import date

CATEGORIES = (
    "foundations", "mathematics", "ai_ml", "systems", "human_context",
    "applications", "electives", "other",
)
REVIEW_STATUSES = ("reviewed", "mixed", "unclassified")


def classification_status(course):
    return (course.get("category_review") or {}).get("status", "unreviewed")


def validate_category_reviews(program):
    source_ids = {s["id"] for s in program.get("sources", [])}
    for course in program.get("courses", []):
        review = course.get("category_review")
        if review is None:
            continue
        if not isinstance(review, dict) or review.get("status") not in REVIEW_STATUSES:
            raise ValueError("Unknown course category review status")
        if review.get("taxonomy_version") != "1":
            raise ValueError("Unknown course taxonomy version")
        try:
            date.fromisoformat(review.get("reviewed_at", ""))
        except (TypeError, ValueError):
            raise ValueError("Course category review needs an ISO date") from None
        for field in ("locator", "rationale"):
            if not isinstance(review.get(field), str) or not review[field].strip():
                raise ValueError(f"Course category review needs {field}")
        evidence = review.get("source_ids")
        if (not isinstance(evidence, list) or not evidence
                or any(not isinstance(s, str) or s not in source_ids for s in evidence)
                or len(set(evidence)) != len(evidence)):
            raise ValueError("Course category review needs unique registered sources")
        category = course.get("category")
        candidates = review.get("candidate_categories", [])
        if (not isinstance(candidates, list)
                or any(c not in CATEGORIES or c in {"other", "electives"} for c in candidates)
                or len(set(candidates)) != len(candidates)):
            raise ValueError("Invalid course category review candidates")
        if review["status"] == "reviewed":
            if category not in CATEGORIES or category in {"other", "electives"}:
                raise ValueError("Reviewed course needs a supported subject category")
        elif category != "other":
            raise ValueError("Mixed or unclassified course must remain other")
        if review["status"] == "mixed" and len(candidates) < 2:
            raise ValueError("Mixed course needs at least two candidate categories")
