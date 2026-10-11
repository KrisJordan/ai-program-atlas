"""Reviewed classifications must survive storage and remain separate from roles."""
from copy import deepcopy
import sqlite3

import pytest

from atlas import db
from atlas.curriculum_profile import requirement_profile
from tests.test_core_review import conn, program  # noqa: F401


def reviewed_course(cid="data-structures", status="reviewed", category="foundations"):
    return {
        "id": cid, "code": "CS 200", "name": "Data Structures", "source_id": "catalog",
        "category": category,
        "category_review": {"status": status, "taxonomy_version": "1",
            "reviewed_at": "2026-10-11", "source_ids": ["catalog"],
            "locator": "CS 200 description", "rationale": "Data representation and algorithms.",
            "candidate_categories": []},
    }


def test_review_survives_relational_storage_revisions_replacement_and_reruns(conn):
    p = program()
    p["courses"] = [reviewed_course()]
    before = deepcopy(p)
    assert db.ingest_program(conn, p)
    assert not db.ingest_program(conn, p)
    assert p == before
    assert db.export_data(conn)["programs"][0]["courses"] == p["courses"]
    assert db.revision_record(conn.execute("SELECT * FROM program_revisions").fetchone())["courses"] == p["courses"]
    assert dict(conn.execute("SELECT * FROM course_category_reviews").fetchone())["status"] == "reviewed"
    assert conn.execute("SELECT source_id FROM course_category_review_sources").fetchone()[0] == "catalog"
    p["courses"][0].pop("category_review")
    assert db.ingest_program(conn, p)
    assert conn.execute("SELECT count(*) FROM course_category_reviews").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM course_category_review_sources").fetchone()[0] == 0
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()


@pytest.mark.parametrize("change", [
    {"status": "automatic"}, {"taxonomy_version": "2"}, {"reviewed_at": "yesterday"},
    {"source_ids": []}, {"source_ids": ["missing"]}, {"source_ids": ["catalog", "catalog"]},
    {"locator": ""}, {"rationale": " "}, {"candidate_categories": ["electives"]},
    {"status": "mixed", "candidate_categories": ["foundations", "systems"]},
])
def test_invalid_review_does_not_replace_curated_data(conn, change):
    p = program()
    db.ingest_program(conn, p)
    p["courses"] = [reviewed_course()]
    p["courses"][0]["category_review"].update(change)
    with pytest.raises(ValueError):
        db.ingest_program(conn, p)
    assert not db.export_data(conn)["programs"][0]["courses"]


def test_unknown_and_mixed_content_are_explicit_in_each_role():
    fixed = reviewed_course()
    mixed = reviewed_course("mixed", "mixed", "other")
    mixed["category_review"]["candidate_categories"] = ["foundations", "human_context"]
    unknown = reviewed_course("unknown", "unclassified", "other")
    legacy = {"id": "legacy", "category": "ai_ml"}
    p = {"courses": [fixed, mixed, unknown, legacy], "requirements": [
        {"id": "fixed", "kind": "all", "course_ids": [fixed["id"], mixed["id"]]},
        {"id": "options", "kind": "choose_courses", "count": 1,
         "course_ids": [fixed["id"], legacy["id"]]},
    ]}
    result = requirement_profile(p)
    assert result["required"]["classification"] == dict(reviewed=1, mixed=1, unclassified=0, unreviewed=0)
    assert result["options"]["classification"] == dict(reviewed=0, mixed=0, unclassified=0, unreviewed=1)
    assert result["unresolved"]["classification"] == dict(reviewed=0, mixed=0, unclassified=1, unreviewed=0)
    assert result["required"]["categories"]["foundations"] == 1
    assert result["required"]["categories"]["other"] == 1
    for role in ("required", "options", "unresolved"):
        assert sum(result[role]["classification"].values()) == result[role]["count"]


def test_review_evidence_cannot_reference_another_programs_source(conn):
    p = program()
    p["courses"] = [reviewed_course()]
    db.ingest_program(conn, p)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO course_category_review_sources VALUES (?,?,?)",
                     (p["id"], p["courses"][0]["id"], "missing"))


@pytest.mark.parametrize("category,status,candidates", [
    ("other", "reviewed", []), ("electives", "reviewed", []),
    ("other", "mixed", ["mathematics"]),
])
def test_reviewed_does_not_certify_unknown_or_requirement_role(category,status,candidates):
    p = program()
    p["courses"] = [reviewed_course(status=status, category=category)]
    p["courses"][0]["category_review"]["candidate_categories"] = candidates
    with pytest.raises(ValueError):
        db.validate_program(p)
