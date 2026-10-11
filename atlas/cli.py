"""Local research database, rerunnable observations and deterministic static builds."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from . import db


def ingest_all(conn, data_dir):
    from .family_store import ingest_family

    files = sorted((data_dir / "programs").glob("*.json"))
    records = {path: json.loads(path.read_text()) for path in files}
    updates = {record["id"]: record for record in records.values()}
    if len(updates) != len(records):
        raise ValueError("Duplicate program IDs in input files")
    hashes = dict(conn.execute("SELECT id,content_hash FROM programs"))
    changed = sum(hashes.get(p["id"]) != db.digest(p) for p in records.values())
    with db.atomic(conn):
        cohort = data_dir / "cohort.json"
        if cohort.exists():
            db.ingest_cohort(conn, json.loads(cohort.read_text()))
        for record in records.values():
            db.upsert_institution(conn, record["institution"])
        for path in sorted((data_dir / "families").glob("*.json")):
            ingest_family(conn, json.loads(path.read_text()), program_updates=updates)
        for path, record in records.items():
            try:
                db.ingest_program(conn, record)
            except Exception as exc:
                raise ValueError(f"{path}: {exc}") from exc
        for path in sorted((data_dir / "surveys").glob("*.json")):
            content = json.loads(path.read_text())
            db.ingest_survey(
                conn, content if isinstance(content, list) else content["institutions"]
            )
        db.initialize_csrankings(conn)
        db.refresh_inspection_dates(conn)
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("data/atlas.sqlite"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    ingest = sub.add_parser("ingest", help="Ingest reviewed factual JSON; preserve overrides")
    ingest.add_argument("--data-dir", type=Path, default=Path("data"))
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, default=Path("dist"))
    build.add_argument("--base-path", default="/ai-program-atlas/")
    scrape = sub.add_parser(
        "scrape", help="Fetch and parse into review queue, without changing curated facts"
    )
    scrape.add_argument("ids", nargs="*")
    scrape.add_argument(
        "--force",
        action="store_true",
        help="Refresh expired or current cache within robots/rate limits",
    )
    sub.add_parser("status")
    sub.add_parser("candidates")
    review = sub.add_parser(
        "review", help="Show an extraction candidate against current reviewed fields"
    )
    review.add_argument("candidate_id", type=int)
    sub.add_parser("check")
    override = sub.add_parser("override")
    override.add_argument("program_id")
    override.add_argument("field")
    override.add_argument("value_json")
    override.add_argument("--reason", required=True)
    override.add_argument("--evidence-url", required=True)
    args = parser.parse_args(argv)
    conn = db.connect(args.db)
    db.migrate(conn)
    try:
        if args.command == "init":
            print(f"Initialized {args.db}")
        elif args.command == "ingest":
            changed = ingest_all(conn, args.data_dir)
            print(f"Ingested reviewed data: {changed} changed program records")
        elif args.command == "build":
            from .site import build as build_site

            data = db.export_data(conn)
            if not data["programs"]:
                raise ValueError("No programs imported; run atlas ingest first")
            build_site(data, args.output, args.base_path)
            print(
                f"Built {len(data['programs'])} programs and {len(data['institutions'])} institutions to {args.output}"
            )
        elif args.command == "scrape":
            from .scrape import scrape_all

            results = scrape_all(conn, args.ids, force=args.force)
            print(json.dumps(results, indent=2))
            return 1 if any(r["status"] != "success" for r in results) else 0
        elif args.command == "status":
            print(json.dumps(db.export_data(conn)["meta"], indent=2))
        elif args.command == "candidates":
            rows = conn.execute(
                "SELECT id,program_id,source_url,created_at,status FROM extraction_candidates WHERE status='pending' ORDER BY id"
            ).fetchall()
            print(json.dumps([dict(r) for r in rows], indent=2))
        elif args.command == "review":
            row = conn.execute(
                "SELECT * FROM extraction_candidates WHERE id=?", (args.candidate_id,)
            ).fetchone()
            if not row:
                raise ValueError("Unknown candidate ID")
            observed = json.loads(row["payload_json"])
            current = json.loads(
                conn.execute(
                    "SELECT record_json FROM programs WHERE id=?", (row["program_id"],)
                ).fetchone()[0]
            )
            current = db.resolve_stored_program(conn, current)
            before = json.dumps(
                {k: current.get(k) for k in observed}, indent=2, sort_keys=True
            ).splitlines()
            after = json.dumps(observed, indent=2, sort_keys=True).splitlines()
            print(f"Candidate {row['id']} from {row['source_url']} ({row['created_at']})")
            print(
                "\n".join(
                    difflib.unified_diff(
                        before,
                        after,
                        fromfile="reviewed fields",
                        tofile="observed subset",
                        lineterm="",
                    )
                )
            )
            print(
                "Review against the official source, update the curated JSON, then run atlas ingest. No data was changed."
            )
        elif args.command == "check":
            problems = conn.execute("PRAGMA foreign_key_check").fetchall()
            result = conn.execute("PRAGMA integrity_check").fetchone()[0]
            for row in conn.execute("SELECT record_json FROM programs"):
                program = json.loads(row[0])
                from .family_store import load_family

                family = (
                    load_family(conn, program["family"]["id"]) if program.get("family") else None
                )
                db.validate_program(program, family)
            if problems or result != "ok":
                raise ValueError(f"Integrity failure: {problems}, {result}")
            print("SQLite integrity, foreign keys and requirement trees: OK")
        elif args.command == "override":
            db.set_override(
                conn,
                args.program_id,
                args.field,
                json.loads(args.value_json),
                args.reason,
                args.evidence_url,
            )
            print("Evidence-backed override saved; it will survive reimport")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
