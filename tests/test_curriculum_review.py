"""A successful scrape cannot silently recertify a complete curriculum."""

from copy import deepcopy
from types import SimpleNamespace
from pathlib import Path

import pytest

from atlas import db
from atlas.http import FetchResult
from atlas.scrape import scrape_one
from tests.test_core_review import program


def reviewed_program():
    record = program()
    record["curriculum_status"] = "complete"
    record["courses"] = [
        {"id": "ai101", "code": "AI 101", "name": None, "source_id": "catalog", "credits": None}
    ]
    record["requirements"] = [
        {
            "id": "core",
            "title": "Core",
            "kind": "all",
            "source_id": "catalog",
            "course_ids": ["ai101"],
        }
    ]
    record["curriculum_audit"] = {
        "scope": "degree",
        "reviewed_at": "2026-10-10",
        "source_ids": ["catalog"],
        "sections": ["Core", "Degree-wide rules"],
        "unresolved_requirements": [],
        "metadata_gaps": ["Course description and prerequisites unverified"],
    }
    return record


@pytest.mark.parametrize(
    "fault", ["missing", "scope", "date", "source", "sections", "gap", "empty"]
)
def test_complete_requires_consistent_evidence_audit(fault):
    record = reviewed_program()
    if fault == "missing":
        del record["curriculum_audit"]
    elif fault == "scope":
        record["curriculum_audit"]["scope"] = "minor"
    elif fault == "date":
        record["curriculum_audit"]["reviewed_at"] = "not a date"
    elif fault == "source":
        record["curriculum_audit"]["source_ids"] = ["unregistered"]
    elif fault == "sections":
        record["curriculum_audit"]["sections"] = []
    elif fault == "gap":
        record["curriculum_audit"]["unresolved_requirements"] = ["Missing college rules"]
    else:
        record["requirements"] = []
    with pytest.raises(ValueError):
        db.validate_program(record)


def test_audit_relational_roundtrip_rerun_and_downgrade(tmp_path):
    conn = db.connect(tmp_path / "audit.sqlite")
    db.migrate(conn)
    record = reviewed_program()
    assert db.ingest_program(conn, record)
    assert not db.ingest_program(conn, record)
    assert conn.execute("SELECT count(*) FROM curriculum_reviews").fetchone()[0] == 1
    assert (
        conn.execute("SELECT source_id FROM curriculum_review_sources").fetchone()[0] == "catalog"
    )
    assert db.export_data(conn)["programs"][0]["curriculum_audit"] == record["curriculum_audit"]
    broken = deepcopy(record)
    broken["curriculum_audit"]["unresolved_requirements"] = ["New policy unresolved"]
    with pytest.raises(ValueError):
        db.ingest_program(conn, broken)
    assert db.export_data(conn)["programs"][0]["curriculum_status"] == "complete"
    broken["curriculum_status"] = "partial"
    assert db.ingest_program(conn, broken)
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()
    del broken["curriculum_audit"]
    assert db.ingest_program(conn, broken)
    assert conn.execute("SELECT count(*) FROM curriculum_review_sources").fetchone()[0] == 0
    conn.close()


@pytest.mark.parametrize(
    "certification", [{"curriculum_status": "complete"}, {"curriculum_audit": {}}]
)
def test_scraper_cannot_issue_reviewer_certification(tmp_path, certification):
    conn = db.connect(tmp_path / "scrape.sqlite")
    db.migrate(conn)
    record = reviewed_program()
    db.ingest_program(conn, record)

    class Fetch:
        def fetch(self, url, **kwargs):
            return FetchResult(url, "Source", "hash", "2026-10-10", 200, True)

    module = SimpleNamespace(
        SOURCES=[record["sources"][0]["url"]], parse=lambda _: {"id": record["id"], **certification}
    )
    result = scrape_one(conn, record["id"], module, Fetch())
    assert result["status"] == "partial"
    assert "cannot certify" in result["errors"][0]
    assert conn.execute("SELECT count(*) FROM extraction_candidates").fetchone()[0] == 0
    assert db.export_data(conn)["programs"][0]["curriculum_audit"] == record["curriculum_audit"]
    conn.close()


def test_existing_database_migrates_and_retains_rank_evidence(tmp_path):
    conn = db.connect(tmp_path / "old.sqlite")
    schema = Path(db.__file__).parent / "migrations/001_initial.sql"
    conn.executescript(schema.read_text())
    conn.execute("INSERT INTO schema_migrations VALUES (1,'2026-10-09')")
    conn.execute("INSERT INTO institutions(id,name) VALUES ('example','Example')")
    conn.execute(
        "INSERT INTO rankings(institution_id,publisher,edition,category,rank,source_url) "
        "VALUES ('example','U.S. News','2027','National Universities',20,'https://example.edu/ranks')"
    )
    conn.commit()
    db.migrate(conn)
    assert conn.execute("SELECT rank FROM rankings").fetchone()[0] == 20
    cohort = {
        "complete": False,
        "sources": [{"url": "https://example.edu/ranks", "fetched_at": "2026-10-10"}],
        "institutions": [
            {
                "id": "example",
                "name": "Example",
                "rankings": [
                    {
                        "edition": "2027",
                        "category": "National Universities",
                        "rank": 20,
                        "source_url": "https://example.edu/ranks",
                        "source_date": "2026-09-22",
                        "locator": "Overall national table",
                        "verification_status": "primary_verified",
                    }
                ],
            }
        ],
    }
    db.ingest_cohort(conn, cohort)
    db.ingest_cohort(conn, cohort)
    exported = db.export_data(conn)
    rank = exported["institutions"][0]["rankings"][0]
    assert rank["source_date"] == "2026-09-22"
    assert rank["fetched_at"] == "2026-10-10"
    assert rank["locator"] == "Overall national table"
    assert len(exported["rankings"]) == 1
    assert exported["meta"]["cohort"]["complete"] is False
    conn.close()


def test_progress_separates_requirement_scope_from_unknown_course_metadata(tmp_path):
    conn = db.connect(tmp_path / "progress.sqlite")
    db.migrate(conn)
    db.ingest_program(conn, reviewed_program())
    summary = db.export_data(conn)["meta"]["curriculum_summary"]
    assert (summary["complete"], summary["partial"], summary["pending"]) == (1, 0, 0)
    assert summary["program_course_records"] == 1
    assert summary["requirement_nodes"] == 1
    assert summary["course_metadata"]["prerequisites"] == 0
    assert summary["credit_amount_and_unit"] == 0
    conn.close()


def test_membership_bound_does_not_invent_exact_rank(tmp_path):
    from atlas.site import ranking_label
    import sqlite3

    conn = db.connect(tmp_path / "membership.sqlite")
    db.migrate(conn)
    rank = {
        "edition": "2027",
        "category": "National Liberal Arts Colleges",
        "rank": None,
        "rank_upper_bound": 100,
        "verification_status": "primary_membership_verified",
        "source_url": "https://example.edu/top-100",
    }
    cohort = {
        "complete": False,
        "institutions": [{"id": "example", "name": "Example", "rankings": [rank]}],
    }
    db.ingest_cohort(conn, cohort)
    result = db.export_data(conn)["institutions"][0]["rankings"][0]
    assert result["rank"] is None
    assert result["rank_upper_bound"] == 100
    assert ranking_label(result) == "Top 100 · exact rank unverified"
    rank["rank"] = 101
    with pytest.raises(sqlite3.IntegrityError):
        db.ingest_cohort(conn, cohort)
    assert db.export_data(conn)["institutions"][0]["rankings"][0]["rank"] is None
    rank["rank"] = 97
    db.ingest_cohort(conn, cohort)
    assert ranking_label(db.export_data(conn)["institutions"][0]["rankings"][0]) == "#97"
    conn.close()
