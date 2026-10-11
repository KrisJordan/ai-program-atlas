"""Reviewed curricular relationships, independent of a program's award."""
import re
from datetime import date

RELATIONSHIPS = {"concentration", "track", "specialization", "emphasis", "immersion"}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _evidence(item, sources):
    ids = item.get("source_ids")
    if not isinstance(ids, list) or not ids or any(not _text(s) for s in ids) or len(set(ids)) != len(ids) or not set(ids) <= sources:
        raise ValueError("Program relationship needs registered, distinct evidence sources")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", item.get("reviewed_at", "")):
        raise ValueError("Program relationship needs a review date")
    date.fromisoformat(item["reviewed_at"])


def validate_program_relationships(program):
    sources = {s["id"] for s in program.get("sources", [])}
    major = program.get("major_relationship")
    if major is not None:
        if not isinstance(major, dict) or major.get("kind") != "second_major_only":
            raise ValueError("Unknown major relationship")
        if program.get("program_kind") != "additional_major":
            raise ValueError("Second-major-only relationship requires an additional-major record")
        _evidence(major, sources)
        if any(not _text(major.get(k)) for k in ("official_term", "eligibility", "locator")):
            raise ValueError("Second-major relationship needs official terminology and eligibility evidence")
    parents = program.get("parent_programs", [])
    review = program.get("parent_program_review")
    if not isinstance(parents, list):
        raise ValueError("parent_programs must be a list")
    if (parents or review is not None) and program.get("program_kind") != "concentration":
        raise ValueError("Parent relationships describe formal concentration/track records")
    if parents and review is None:
        raise ValueError("Parent relationships need an explicit review")
    seen = set()
    for parent in parents:
        if not isinstance(parent, dict) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", parent.get("id", "")):
            raise ValueError("Parent relationship needs a stable local ID")
        if parent["id"] in seen:
            raise ValueError("Duplicate parent relationship ID")
        seen.add(parent["id"])
        if parent.get("relationship") not in RELATIONSHIPS:
            raise ValueError("Unknown concentration relationship")
        if any(not _text(parent.get(k)) for k in ("title", "locator")):
            raise ValueError("Parent relationship needs official title and evidence locator")
        for key in ("award_level", "award_label", "eligibility", "parent_program_id"):
            if parent.get(key) is not None and not _text(parent[key]):
                raise ValueError(f"Parent {key} must be text or null")
        if parent.get("parent_program_id") == program["id"]:
            raise ValueError("Concentration cannot be its own parent")
        _evidence(parent, sources)
    if review is not None:
        if not isinstance(review, dict) or review.get("status") not in {"verified", "partial", "unknown"}:
            raise ValueError("Unknown parent review status")
        _evidence(review, sources)
        if not isinstance(review.get("notes"), list) or any(not _text(n) for n in review["notes"]):
            raise ValueError("Parent review notes must be a list of text")
        if review["status"] == "unknown" and parents:
            raise ValueError("Unknown parent review cannot claim a verified parent")
        if review["status"] == "verified" and (not parents or any(not p.get("award_level") for p in parents)):
            raise ValueError("Verified parent review needs an explicit parent and award")


def ingest_relationships(conn, program):
    # Historical migration fixtures may intentionally load an older schema.
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE name='program_parents'").fetchone():
        return
    pid = program["id"]
    for table in ("program_major_relationships", "program_parent_reviews", "program_parents"):
        conn.execute(f"DELETE FROM {table} WHERE program_id=?", (pid,))
    major = program.get("major_relationship")
    if major:
        conn.execute("INSERT INTO program_major_relationships VALUES (?,?,?,?,?,?)",
                     (pid, major["kind"], major["official_term"], major["eligibility"], major["locator"], major["reviewed_at"]))
        conn.executemany("INSERT INTO program_major_relationship_sources VALUES (?,?)", [(pid, s) for s in major["source_ids"]])
    review = program.get("parent_program_review")
    if review:
        from .db import canonical
        conn.execute("INSERT INTO program_parent_reviews VALUES (?,?,?,?)", (pid, review["status"], review["reviewed_at"], canonical(review["notes"])))
        conn.executemany("INSERT INTO program_parent_review_sources VALUES (?,?)", [(pid, s) for s in review["source_ids"]])
    for ordinal, parent in enumerate(program.get("parent_programs", [])):
        conn.execute("INSERT INTO program_parents VALUES (?,?,?,?,?,?,?,?,?,?,?)", (pid, parent["id"], ordinal,
            parent["title"], parent.get("award_level"), parent.get("award_label"), parent["relationship"],
            parent.get("parent_program_id"), parent.get("eligibility"), parent["locator"], parent["reviewed_at"]))
        conn.executemany("INSERT INTO program_parent_sources VALUES (?,?,?)", [(pid, parent["id"], s) for s in parent["source_ids"]])
