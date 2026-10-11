"""Collect adapter observations in a review queue; never overwrite curated records."""

from __future__ import annotations

import importlib
from pathlib import Path

from .db import canonical, digest, now
from .http import Fetcher
from .requirements import validate_requirements


def adapters():
    result = {}
    for path in sorted((Path(__file__).parent / "adapters").glob("*/adapter.py")):
        module = importlib.import_module(f"atlas.adapters.{path.parent.name}.adapter")
        pid = getattr(module, "PROGRAM_ID", getattr(module, "PID", path.parent.name))
        if pid in result:
            raise ValueError(f"Duplicate adapter for {pid}")
        result[pid] = module
    return result


def scrape_one(conn, pid, module, fetcher, *, force=False):
    if not conn.execute("SELECT 1 FROM programs WHERE id=?", (pid,)).fetchone():
        raise ValueError(f"Ingest reviewed program before scraping: {pid}")
    with conn:
        cursor = conn.execute(
            "INSERT INTO scrape_runs(adapter,started_at,status) VALUES (?,?,?)",
            (pid, now(), "running"),
        )
        run_id = cursor.lastrowid
    errors = []
    candidates = 0
    changes = 0
    for index, source in enumerate(module.SOURCES):
        url = source if isinstance(source, str) else source["url"]
        try:
            fetched = fetcher.fetch(url, force=force)
            previous = conn.execute(
                "SELECT content_hash FROM source_snapshots WHERE program_id=? AND url=? ORDER BY id DESC LIMIT 1",
                (pid, url),
            ).fetchone()
            changed = bool(previous and previous[0] != fetched.content_hash)
            changes += int(changed)
            with conn:
                conn.execute(
                    "INSERT INTO source_snapshots(run_id,program_id,url,fetched_at,content_hash,http_status,cached,changed) VALUES (?,?,?,?,?,?,?,?)",
                    (
                        run_id,
                        pid,
                        url,
                        fetched.fetched_at,
                        fetched.content_hash,
                        fetched.status,
                        int(fetched.cached),
                        int(changed),
                    ),
                )
            parsers = getattr(module, "SOURCE_PARSERS", {})
            parser = parsers.get(url) or (module.parse if index == 0 else None)
            if parser is None:
                continue
            observed = parser(fetched.text)
            if observed.get("id") != pid:
                raise ValueError(f"Adapter ID mismatch: {observed.get('id')} versus {pid}")
            if "last_verified" in observed:
                raise ValueError(
                    "Adapter observations must not replay a curated verification timestamp"
                )
            if "curriculum_audit" in observed or observed.get("curriculum_status") == "complete":
                raise ValueError("Scrapers cannot certify reviewed curriculum completeness")
            if any("category_review" in course for course in observed.get("courses", [])):
                raise ValueError("Scrapers cannot certify independent course taxonomy reviews")
            if "course_identity_groups" in observed:
                raise ValueError("Scrapers cannot certify independent course identity reviews")
            validate_requirements(observed)
            fingerprint = digest(observed)
            with conn:
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO extraction_candidates(program_id,run_id,source_url,payload_json,content_hash,created_at) VALUES (?,?,?,?,?,?)",
                    (pid, run_id, url, canonical(observed), fingerprint, now()),
                )
                candidates += cursor.rowcount
        except Exception as exc:
            errors.append(f"{url}: {type(exc).__name__}: {exc}")
    snapshot_count = conn.execute(
        "SELECT count(*) FROM source_snapshots WHERE run_id=?", (run_id,)
    ).fetchone()[0]
    status = ("partial" if snapshot_count else "failed") if errors else "success"
    if not module.SOURCES:
        status, errors = "failed", ["Adapter has no source URLs"]
    with conn:
        conn.execute(
            "UPDATE scrape_runs SET finished_at=?,status=?,error=? WHERE id=?",
            (now(), status, "\n".join(errors) or None, run_id),
        )
    return {
        "run_id": run_id,
        "program_id": pid,
        "status": status,
        "new_candidates": candidates,
        "source_changes": changes,
        "errors": errors,
    }


def scrape_all(conn, ids=None, *, force=False, fetcher=None):
    available = adapters()
    chosen = ids or sorted(available)
    unknown = set(chosen) - available.keys()
    if unknown:
        raise ValueError(f"Unknown adapters: {sorted(unknown)}")
    owned = fetcher is None
    fetcher = fetcher or Fetcher()
    results = []
    try:
        for pid in chosen:
            results.append(scrape_one(conn, pid, available[pid], fetcher, force=force))
    finally:
        if owned:
            fetcher.close()
    return results
