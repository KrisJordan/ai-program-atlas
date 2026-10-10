"""Integration coverage for audited requirements and reproducible database builds."""

import copy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from atlas import db
from atlas.cli import ingest_all
from atlas.http import FetchError, Fetcher, FetchResult
from atlas.requirements import describe_rule, observed_category_counts, validate_requirements
from atlas.scrape import scrape_one
from atlas.site import build
from tests.test_core_review import program


def test_nested_requirement_integrity_and_choice_rules():
    p = program()
    p["courses"] = [{"id": "a"}, {"id": "b"}]
    p["requirements"] = [
        {"id": "root", "kind": "all", "course_ids": []},
        {
            "id": "choice",
            "parent_id": "root",
            "kind": "choose_courses",
            "count": 1,
            "course_ids": ["a", "b"],
        },
    ]
    validate_requirements(p)
    assert describe_rule(p["requirements"][1]) == "Choose 1 courses"
    assert observed_category_counts(
        {"courses": [{"id": "a", "category": "ai_ml"}, {"id": "a", "category": "ai_ml"}]}
    ) == {"ai_ml": 1}
    for bad in ("cycle", "orphan", "missing_course", "invalid_count"):
        invalid = copy.deepcopy(p)
        if bad == "cycle":
            invalid["requirements"][0]["parent_id"] = "choice"
        if bad == "orphan":
            invalid["requirements"][1]["parent_id"] = "missing"
        if bad == "missing_course":
            invalid["requirements"][1]["course_ids"] = ["c"]
        if bad == "invalid_count":
            invalid["requirements"][1]["count"] = 0
        with pytest.raises(ValueError):
            validate_requirements(invalid)


def test_credit_choices_preserve_units():
    for unit in ("course_units", "quarter_hours", "semester_hours", "units"):
        rule = {"id": "choice", "kind": "choose_credits", "credits": 6, "credit_unit": unit}
        validate_requirements({"requirements": [rule]})
        assert describe_rule(rule) == f"Choose 6 {unit.replace('_', ' ')}"
    with pytest.raises(ValueError):
        validate_requirements(
            {
                "requirements": [
                    {
                        "id": "choice",
                        "kind": "choose_credits",
                        "credits": 6,
                        "credit_unit": "unknown",
                    }
                ]
            }
        )


def test_retry_policy_cache_and_robots_restrictions(tmp_path):
    hits = []

    def handler(request):
        hits.append(request.url.path)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /blocked")
        if request.url.path == "/forbidden":
            return httpx.Response(403)
        if request.url.path == "/temporary" and hits.count("/temporary") < 3:
            return httpx.Response(503)
        return httpx.Response(200, text="<h1>Artificial Intelligence</h1>")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0, sleep=lambda _: None)
        fetched = fetcher.fetch("https://catalog.example.edu/temporary")
        assert hits.count("/temporary") == 3
        assert fetched.cached is False
        assert fetcher.fetch("https://catalog.example.edu/temporary").cached is True
        assert hits.count("/temporary") == 3
        with pytest.raises(FetchError, match="Robots disallows"):
            fetcher.fetch("https://catalog.example.edu/blocked")
        assert "/blocked" not in hits
        with pytest.raises(FetchError, match="HTTP 403"):
            fetcher.fetch("https://catalog.example.edu/forbidden")
        assert hits.count("/forbidden") == 1


def test_changed_requirements_queue_without_erasing_reviewed_record(tmp_path):
    conn = db.connect(tmp_path / "atlas.sqlite")
    db.migrate(conn)
    p = program()
    db.ingest_program(conn, p)
    module = SimpleNamespace(
        SOURCES=["https://catalog.example.edu/ai"],
        parse=lambda body: {"id": p["id"], "notes": [body]},
    )

    class Fake:
        text = "Old rule"

        def fetch(self, url, **kwargs):
            return FetchResult(url, self.text, self.text, "2026-10-10", 200, False)

    fetcher = Fake()
    assert scrape_one(conn, p["id"], module, fetcher)["source_changes"] == 0
    fetcher.text = "New rule"
    result = scrape_one(conn, p["id"], module, fetcher)
    assert result["source_changes"] == 1 and result["new_candidates"] == 1
    assert conn.execute("SELECT count(*) FROM extraction_candidates").fetchone()[0] == 2
    assert db.export_data(conn)["programs"][0]["title"] == p["title"]
    assert conn.execute("SELECT count(*) FROM program_revisions").fetchone()[0] == 1
    conn.close()


def test_complete_reviewed_inventory_rebuild_is_deterministic(tmp_path):
    root = Path(__file__).resolve().parents[1]
    conn = db.connect(tmp_path / "one.sqlite")
    db.migrate(conn)
    changed = ingest_all(conn, root / "data")
    assert changed == len(list((root / "data/programs").glob("*.json")))
    first = db.canonical(db.export_data(conn))
    assert ingest_all(conn, root / "data") == 0
    assert db.canonical(db.export_data(conn)) == first
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()
    conn2 = db.connect(tmp_path / "two.sqlite")
    db.migrate(conn2)
    ingest_all(conn2, root / "data")
    assert db.canonical(db.export_data(conn2)) == first
    build(db.export_data(conn), tmp_path / "site1")
    build(db.export_data(conn2), tmp_path / "site2")
    files1 = {
        p.relative_to(tmp_path / "site1"): p.read_bytes()
        for p in (tmp_path / "site1").rglob("*")
        if p.is_file()
    }
    files2 = {
        p.relative_to(tmp_path / "site2"): p.read_bytes()
        for p in (tmp_path / "site2").rglob("*")
        if p.is_file()
    }
    assert files1 == files2
    conn.close()
    conn2.close()


def test_compressed_response_is_decoded_once(tmp_path):
    import gzip

    def handler(request):
        text = (
            "User-agent: *\nAllow: /"
            if request.url.path == "/robots.txt"
            else "<h1>Artificial Intelligence</h1>"
        )
        return httpx.Response(
            200,
            content=gzip.compress(text.encode()),
            headers={
                "Content-Encoding": "gzip",
                "Content-Type": "text/html" if request.url.path != "/robots.txt" else "text/plain",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0)
        assert (
            fetcher.fetch("https://catalog.example.edu/ai").text
            == "<h1>Artificial Intelligence</h1>"
        )


def test_long_retry_after_is_deferred_not_truncated(tmp_path):
    requests = []

    def handler(request):
        requests.append(request.url.path)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(429, headers={"Retry-After": "3600"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        fetcher = Fetcher(tmp_path, client=client, delay=0)
        with pytest.raises(FetchError, match="later run"):
            fetcher.fetch("https://catalog.example.edu/ai")
    assert requests.count("/ai") == 1
