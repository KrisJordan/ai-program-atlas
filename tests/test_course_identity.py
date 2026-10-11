from copy import deepcopy
import sqlite3
import pytest
from atlas import db
from atlas.curriculum_profile import requirement_profile
from tests.test_core_review import conn, program  # noqa: F401


def record():
    p = program()
    p["courses"] = [dict(id=cid, code=cid.upper(), name="Source-stated course alias",
        source_id="catalog", category="ai_ml") for cid in ("ds-410", "cs-410", "unrelated")]
    p["requirements"] = [dict(id="options", parent_id=None, title="Choose one", kind="choose_courses",
        count=1, course_ids=["ds-410", "cs-410", "unrelated"], source_id="catalog")]
    p["course_identity_groups"] = [dict(id="crosslist-410", relation="crosslisted",
        canonical_course_id="ds-410", course_ids=["ds-410", "cs-410"], source_ids=["catalog"],
        reviewed_at="2026-10-11", locator="Both course blocks, Cross-listed with",
        rationale="Reciprocal official statements identify one course under two codes.")]
    return p


def test_verified_alias_counts_once_but_preserves_sources_and_selection_rule(conn):
    p = record();before = deepcopy(p)
    assert db.ingest_program(conn, p)
    assert not db.ingest_program(conn, p)
    exported = db.export_data(conn)["programs"][0]
    assert exported["courses"] == p["courses"]
    assert exported["course_identity_groups"] == p["course_identity_groups"]
    r = requirement_profile(exported)
    assert r["options"]["count"] == r["options"]["categories"]["ai_ml"] == 2
    assert r["options"]["source_record_count"] == 3
    assert r["choices"][0]["count"] == 1
    assert r["identity"] == dict(source_records=3,mapped_identities=2,crosslisted_aliases=1,reviewed_groups=1)
    assert p == before
    assert conn.execute("SELECT count(*) FROM course_identity_members").fetchone()[0] == 2
    assert db.revision_record(conn.execute("SELECT * FROM program_revisions").fetchone())["course_identity_groups"] == p["course_identity_groups"]
    p.pop("course_identity_groups")
    assert db.ingest_program(conn, p)
    assert conn.execute("SELECT count(*) FROM course_identity_groups").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM course_identity_sources").fetchone()[0] == 0
    assert requirement_profile(p)["options"]["count"] == 3  # Same names never imply identity.
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()


def test_fixed_alias_wins_across_choices_and_unknown_context():
    p = record()
    p["requirements"] += [dict(id="fixed",kind="all",course_ids=["cs-410"]),
                           dict(id="context",kind="note",course_ids=["ds-410"])]
    r = requirement_profile(p)
    assert [r[x]["count"] for x in ("required","options","unresolved")] == [1,1,0]
    assert r["required"]["source_record_count"] == 2
    assert sum(r[x]["source_record_count"] for x in ("required","options","unresolved")) == 3


@pytest.mark.parametrize("change", [
    {"relation":"credit_exclusion"}, {"relation":"similar_title"},
    {"canonical_course_id":"unrelated"}, {"course_ids":["ds-410"]},
    {"course_ids":["ds-410","missing"]}, {"source_ids":["missing"]},
    {"source_ids":[]}, {"rationale":""}, {"reviewed_at":"unknown"},
])
def test_unproven_identity_cannot_replace_reviewed_data(conn, change):
    p=record();db.ingest_program(conn,p)
    p["course_identity_groups"][0].update(change)
    with pytest.raises(ValueError):db.ingest_program(conn,p)
    assert db.export_data(conn)["programs"][0]["course_identity_groups"] == record()["course_identity_groups"]


def test_overlapping_groups_and_conflicting_reviewed_subjects_are_rejected():
    p=record();p["course_identity_groups"].append({**p["course_identity_groups"][0],"id":"duplicate"})
    with pytest.raises(ValueError,match="disjoint"):db.validate_program(p)
    p=record()
    # Identity validation is independently callable; taxonomy details validated elsewhere.
    from atlas.course_identity import validate_course_identities
    p["courses"][1].update(category="foundations",category_review={"status":"reviewed"})
    with pytest.raises(ValueError,match="conflict"):validate_course_identities(p)


def test_relational_alias_membership_requires_existing_course(conn):
    p=record();db.ingest_program(conn,p)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO course_identity_members VALUES (?,?,?)",(p["id"],"crosslist-410","missing"))
