"""Synthetic regression tests for data preservation and HTTP policy boundaries."""

from copy import deepcopy
from types import SimpleNamespace

import httpx
import pytest

from atlas import db
from atlas.http import Fetcher, FetchError, FetchResult
from atlas.scrape import scrape_one


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "review.sqlite")
    db.migrate(c)
    yield c
    c.close()


def program():
    return {
        "id": "review-ai-bs",
        "institution": {
            "id": "review-university",
            "name": "Review University",
            "calendar": "unknown",
        },
        "title": "Artificial Intelligence BS",
        "award_level": "BS",
        "program_kind": "degree",
        "status": "active",
        "verification_status": "confirmed",
        "curriculum_status": "partial",
        "last_verified": "2026-10-10",
        "sources": [
            {"id": "catalog", "url": "https://catalog.example.edu/ai", "title": "AI catalog"}
        ],
        "courses": [],
        "requirements": [],
        "outcomes": [],
    }


def test_nonempty_courses_ingest_atomically_and_idempotently(conn):
    record = program()
    record["courses"] = [
        {
            "id": "cs101",
            "code": "CS101",
            "name": "Introduction",
            "credits": 3,
            "credit_unit": "semester_hours",
            "source_id": "catalog",
        }
    ]
    assert db.ingest_program(conn, record)
    assert not db.ingest_program(conn, record)
    assert conn.execute("SELECT count(*) FROM courses").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM program_revisions").fetchone()[0] == 1


def test_invalid_replacement_preserves_reviewed_program_and_override(conn):
    record = program()
    db.ingest_program(conn, record)
    db.set_override(
        conn,
        record["id"],
        "overview",
        "Reviewed correction",
        "Official update",
        "https://catalog.example.edu/correction",
    )
    replacement = deepcopy(record)
    replacement["status"] = "invalid-status"
    with pytest.raises(Exception):
        db.ingest_program(conn, replacement)
    exported = db.export_data(conn)["programs"][0]
    assert exported["status"] == "active"
    assert exported["overview"] == "Reviewed correction"
    assert conn.execute("SELECT count(*) FROM program_revisions").fetchone()[0] == 1


def test_failed_fetch_preserves_reviewed_data(conn):
    record = program()
    db.ingest_program(conn, record)
    before = db.export_data(conn)["programs"]

    class FailedFetcher:
        def fetch(self, *_args, **_kwargs):
            raise FetchError("Robots disallows fetch")

    module = SimpleNamespace(SOURCES=["https://catalog.example.edu/ai"], parse=lambda _: {})
    result = scrape_one(conn, record["id"], module, FailedFetcher())
    assert result["status"] == "failed"
    assert db.export_data(conn)["programs"] == before
    assert conn.execute("SELECT count(*) FROM extraction_candidates").fetchone()[0] == 0


def test_same_observation_is_not_duplicated(conn):
    record = program()
    db.ingest_program(conn, record)

    class StableFetcher:
        def fetch(self, url, **_kwargs):
            return FetchResult(
                url, "<h1>Artificial Intelligence</h1>", "same", "2026-10-10", 200, True
            )

    module = SimpleNamespace(
        SOURCES=["https://catalog.example.edu/ai"],
        parse=lambda _: {"id": record["id"], "title": record["title"]},
    )
    first = scrape_one(conn, record["id"], module, StableFetcher())
    second = scrape_one(conn, record["id"], module, StableFetcher())
    assert first["new_candidates"] == 1
    assert second["new_candidates"] == 0
    assert db.export_data(conn)["programs"][0]["last_verified"] == "2026-10-10"


def test_long_robots_delay_stays_blocked_on_repeated_request(tmp_path):
    requests = []

    def handler(request):
        requests.append(str(request.url))
        text = (
            "User-agent: *\nCrawl-delay: 3600\nAllow: /"
            if request.url.path == "/robots.txt"
            else "secret target"
        )
        return httpx.Response(200, text=text)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0, sleep=lambda _: None)
        for _ in range(2):
            with pytest.raises(FetchError, match="crawl delay"):
                fetcher.fetch("https://catalog.example.edu/ai")
    assert all(url.endswith("/robots.txt") for url in requests)


def test_redirect_cannot_introduce_credentials(tmp_path):
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.path == "/start":
            return httpx.Response(
                302, headers={"Location": "https://user:password@other.example.edu/ai"}
            )
        return httpx.Response(200, text="private content")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0)
        with pytest.raises(FetchError, match="credential|Unsafe|public"):
            fetcher.fetch("https://catalog.example.edu/start")
    assert all(request.url.host != "other.example.edu" for request in requests)


def test_bad_first_offered_override_cannot_break_export_shape(conn):
    record = program()
    db.ingest_program(conn, record)
    with pytest.raises(ValueError, match="first_offered|date|object"):
        db.set_override(
            conn,
            record["id"],
            "first_offered",
            "2020",
            "Launch date",
            "https://catalog.example.edu/launch",
        )
    assert db.export_data(conn)["programs"][0].get("first_offered") is None


def test_failed_migration_rolls_back_ddl_and_version(tmp_path, monkeypatch):
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    (migration_dir / "001_broken.sql").write_text(
        "CREATE TABLE partial_install(id INTEGER);\nINSERT INTO missing_table VALUES (1);"
    )
    monkeypatch.setattr(db, "__file__", str(tmp_path / "db.py"))
    conn = db.connect(tmp_path / "migration.sqlite")
    try:
        with pytest.raises(Exception):
            db.migrate(conn)
        assert (
            conn.execute("SELECT name FROM sqlite_master WHERE name='partial_install'").fetchone()
            is None
        )
        assert conn.execute("SELECT count(*) FROM schema_migrations").fetchone()[0] == 0
    finally:
        conn.close()


def test_known_curriculum_fact_requires_registered_source(conn):
    record = program()
    record["courses"] = [
        {
            "id": "cs101",
            "code": "CS101",
            "name": "Introduction",
            "credits": 3,
            "credit_unit": "semester_hours",
        }
    ]
    with pytest.raises(ValueError, match="source|evidence"):
        db.ingest_program(conn, record)


def test_redirect_cannot_fetch_loopback_service(tmp_path):
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.path == "/start":
            return httpx.Response(302, headers={"Location": "http://127.0.0.1:8080/internal"})
        return httpx.Response(200, text="local service data")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0)
        with pytest.raises(FetchError, match="public|local|private|Unsafe"):
            fetcher.fetch("https://catalog.example.edu/start")
    assert all(request.url.host != "127.0.0.1" for request in requests)


def test_reviewed_discovery_classification_updates_and_preserves_history(conn):
    record = program()
    db.ingest_program(conn, record)
    db.set_override(
        conn,
        record["id"],
        "overview",
        "Reviewed correction",
        "Official evidence",
        "https://catalog.example.edu/correction",
    )
    survey = {
        "institution_id": "review-university",
        "status": "confirmed",
        "checked_at": "2026-10-10",
        "note": "Initial directory observation",
        "sources": [{"url": "https://catalog.example.edu/program"}],
        "discoveries": [
            {
                "title": "Artificial Intelligence",
                "kind": "degree",
                "award_level": "BS",
                "url": "https://catalog.example.edu/program",
            }
        ],
    }
    db.ingest_survey(conn, [survey])
    corrected = deepcopy(survey)
    corrected["note"] = "Catalog review verifies an additional major, not a standalone award"
    corrected["discoveries"][0].update(kind="additional_major", award_level="other")
    db.ingest_survey(conn, [corrected])
    db.ingest_survey(conn, [corrected])
    discoveries = [dict(r) for r in conn.execute("SELECT kind,award_level FROM discoveries")]
    assert discoveries == [{"kind": "additional_major", "award_level": "other"}]
    assert conn.execute("SELECT count(*) FROM coverage_events").fetchone()[0] == 2
    assert db.export_data(conn)["programs"][0]["overview"] == "Reviewed correction"
    # An identity-only later observation cannot erase reviewed classifications.
    partial = deepcopy(corrected)
    partial["discoveries"][0].pop("kind")
    partial["discoveries"][0].pop("award_level")
    db.ingest_survey(conn, [partial])
    assert [
        dict(r) for r in conn.execute("SELECT kind,award_level FROM discoveries")
    ] == discoveries
