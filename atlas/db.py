"""Transactional curated data store. Network observations never replace reviewed facts."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import zlib
from contextlib import contextmanager
from datetime import datetime, timezone
from itertools import count
from pathlib import Path
from urllib.parse import urlparse

from .awards import validate_award_options
from .requirements import validate_curriculum_audit, validate_requirements
from .taxonomy import validate_category_reviews
from .course_identity import validate_course_identities
from .program_relationships import validate_program_relationships, ingest_relationships

STATES = {"pending", "inspected", "confirmed", "no_qualifying_program_found", "inaccessible"}
OVERRIDE_FIELDS = {
    "title",
    "overview",
    "hosting_unit",
    "status",
    "first_offered",
    "catalog_year",
    "notes",
}


_savepoint_ids = count()


@contextmanager
def atomic(conn):
    """Nest safe writes so a family and all changed variants commit together."""
    name = f"atlas_{next(_savepoint_ids)}"
    conn.execute(f"SAVEPOINT {name}")
    try:
        yield
        conn.execute(f"RELEASE SAVEPOINT {name}")
    except Exception:
        conn.execute(f"ROLLBACK TO SAVEPOINT {name}")
        conn.execute(f"RELEASE SAVEPOINT {name}")
        raise


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _compress_revision(text: str, content_hash: str) -> bytes:
    raw = text.encode("utf-8")
    json.loads(text)
    if hashlib.sha256(raw).hexdigest() != content_hash:
        raise ValueError("Canonical content hash mismatch")
    return zlib.compress(raw, level=9)


def _decode_record(row, label) -> dict:
    raw = zlib.decompress(row["record_zlib"])
    if hashlib.sha256(raw).hexdigest() != row["content_hash"]:
        raise ValueError(label + " content hash mismatch")
    return json.loads(raw)


def revision_record(row) -> dict:
    """Decode a revision row and verify its original canonical-content hash."""
    return _decode_record(row, "Revision")


def program_record(row) -> dict:
    """Decode the current canonical snapshot; relational facts remain queryable."""
    if "record_zlib" in row.keys():
        return _decode_record(row, "Program")
    # Upgrade verification may inspect an older database before migrating it.
    # Verify legacy canonical bytes too; never fall back from a corrupt blob.
    raw = row["record_json"].encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != row["content_hash"]:
        raise ValueError("Program content hash mismatch")
    return json.loads(raw)


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    # Used only by transactional snapshot-storage and relational-backfill migrations. The resulting
    # database needs no SQLite extension or custom function for ordinary reads.
    conn.create_function("atlas_compress_revision", 2, _compress_revision)
    conn.create_function("atlas_verified_program_json", 2, lambda payload, fingerprint:
        canonical(_decode_record({"record_zlib": payload, "content_hash": fingerprint}, "Program")))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    conn.commit()
    for file in sorted((Path(__file__).parent / "migrations").glob("*.sql")):
        version = int(file.name.split("_")[0])
        if conn.execute("SELECT 1 FROM schema_migrations WHERE version=?", (version,)).fetchone():
            continue
        try:
            conn.executescript("BEGIN IMMEDIATE;\n" + file.read_text())
            conn.execute("INSERT INTO schema_migrations VALUES (?,?)", (version, now()))
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def upsert_institution(conn, inst):
    conn.execute(
        """INSERT INTO institutions(id,name,calendar,website) VALUES (?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET name=excluded.name,
        calendar=CASE WHEN excluded.calendar='unknown' THEN institutions.calendar ELSE excluded.calendar END,
        website=COALESCE(excluded.website,institutions.website)""",
        (inst["id"], inst["name"], inst.get("calendar", "unknown"), inst.get("website")),
    )
    for alias in inst.get("aliases", []):
        conn.execute("INSERT OR IGNORE INTO institution_aliases VALUES (?,?)", (inst["id"], alias))


def ingest_cohort(conn, cohort):
    cohort_sources = {source["url"]: source for source in cohort.get("sources", [])}
    with atomic(conn):
        conn.execute(
            "INSERT OR REPLACE INTO metadata VALUES (?,?)",
            ("cohort", canonical({k: v for k, v in cohort.items() if k != "institutions"})),
        )
        for inst in cohort["institutions"]:
            upsert_institution(conn, inst)
            for rank in inst.get("rankings", []):
                source = cohort_sources.get(rank["source_url"], {})
                conn.execute(
                    """INSERT INTO rankings(institution_id,publisher,edition,category,rank,source_url,verification_status,source_date,fetched_at,locator,rank_upper_bound)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(institution_id,publisher,edition,category) DO UPDATE SET
                    rank=excluded.rank,source_url=excluded.source_url,verification_status=excluded.verification_status,
                    source_date=excluded.source_date,fetched_at=excluded.fetched_at,locator=excluded.locator,
                    rank_upper_bound=excluded.rank_upper_bound""",
                    (
                        inst["id"],
                        rank.get("publisher", "U.S. News"),
                        str(rank["edition"]),
                        rank["category"],
                        rank["rank"],
                        rank["source_url"],
                        rank.get("verification_status", "secondary_reported"),
                        rank.get("source_date", source.get("source_date")),
                        rank.get("fetched_at", source.get("fetched_at")),
                        rank.get("locator"),
                        rank.get("rank_upper_bound"),
                    ),
                )
            # A cohort reimport must not reset completed inspection work.
            conn.execute(
                "UPDATE institutions SET coverage_note=? WHERE id=? AND coverage_status='pending'",
                (inst.get("coverage_note", ""), inst["id"]),
            )


def validate_program(program, family=None):
    if program.get("family"):
        from .families import resolve_program

        program = resolve_program(program, family)
        if program.get("curriculum_status") == "complete" and program.get(
            "curriculum_audit", {}
        ).get("family_content_hash") != digest(family):
            raise ValueError("Complete family variant needs a current family review hash")
    for key in (
        "id",
        "institution",
        "title",
        "award_level",
        "program_kind",
        "sources",
        "last_verified",
    ):
        if not program.get(key):
            raise ValueError(f"Missing required field: {key}")
    for field in ("id", "title", "award_level", "program_kind", "last_verified"):
        if not isinstance(program[field], str):
            raise ValueError(f"{field} must be a string")
    if not isinstance(program.get("overview", ""), str):
        raise ValueError("overview must be a string")
    if not isinstance(program.get("notes", []), list) or any(
        not isinstance(note, str) for note in program.get("notes", [])
    ):
        raise ValueError("notes must be a list of strings")
    first = program.get("first_offered")
    if first is not None:
        if not isinstance(first, dict) or not all(
            first.get(key) for key in ("value", "precision", "evidence_url")
        ):
            raise ValueError(
                "first_offered must be null or an object with value, precision and evidence_url"
            )
        if urlparse(first["evidence_url"]).scheme not in {"http", "https"}:
            raise ValueError("first_offered requires an HTTP(S) evidence URL")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", program["id"]):
        raise ValueError("Program ID must be a safe slug")
    if not re.search(r"artificial intelligence|\b(?:AI|GenAI|GeoAI)\b", program["title"], re.I):
        raise ValueError("Official title must explicitly contain AI or Artificial Intelligence")
    source_ids = {s["id"] for s in program["sources"]}
    if len(source_ids) != len(program["sources"]):
        raise ValueError("Duplicate source IDs")
    for source in program["sources"]:
        if urlparse(source["url"]).scheme not in {"http", "https"}:
            raise ValueError("Source URL must be HTTP(S)")
    courses = program.get("courses", [])
    if len({c["id"] for c in courses}) != len(courses):
        raise ValueError("Duplicate course IDs")
    for item in courses + program.get("requirements", []):
        if not item.get("source_id"):
            raise ValueError("Curated course and requirement facts need source evidence")
    for item in courses + program.get("requirements", []) + program.get("outcomes", []):
        if item.get("source_id") and item["source_id"] not in source_ids:
            raise ValueError(f"Unknown source {item['source_id']}")
    for course in courses:
        if "notes" in course and (not isinstance(course["notes"], list) or any(
            not isinstance(note, str) or not note.strip() for note in course["notes"]
        )):
            raise ValueError("Course notes must be a list of nonempty strings")
        if course.get("credits") is not None and (
            not isinstance(course["credits"], (int, float)) or course["credits"] < 0
        ):
            raise ValueError("Course credits must be a nonnegative number or null")
    for outcome in program.get("outcomes", []):
        if outcome.get("statement_type", "unspecified") not in {
            "learning_outcome",
            "program_aim",
            "career_pathway",
            "unspecified",
        }:
            raise ValueError("Unknown outcome statement type")
        if outcome["kind"] == "source_stated" and not outcome.get("source_id"):
            raise ValueError("Source-stated outcome needs source evidence")
    validate_requirements(program)
    validate_curriculum_audit(program)
    validate_award_options(program)
    validate_category_reviews(program)
    validate_course_identities(program)
    validate_program_relationships(program)


def ingest_program(conn, program, run_id=None):
    """Replace one complete reviewed record atomically; unchanged records are no-ops."""
    from .family_store import ingest_membership, load_family

    family = load_family(conn, program["family"]["id"]) if program.get("family") else None
    validate_program(program, family)
    fingerprint = digest(program)
    existing = conn.execute(
        "SELECT content_hash FROM programs WHERE id=?", (program["id"],)
    ).fetchone()
    if existing and existing[0] == fingerprint:
        return False
    pid = program["id"]
    with atomic(conn):
        upsert_institution(conn, program["institution"])
        unit_id = None
        if program.get("hosting_unit"):
            conn.execute(
                "INSERT OR IGNORE INTO hosting_units(institution_id,name) VALUES (?,?)",
                (program["institution"]["id"], program["hosting_unit"]),
            )
            unit_id = conn.execute(
                "SELECT id FROM hosting_units WHERE institution_id=? AND name=?",
                (program["institution"]["id"], program["hosting_unit"]),
            ).fetchone()[0]
        storage_column = ("record_zlib" if any(row["name"] == "record_zlib"
                          for row in conn.execute("PRAGMA table_info(programs)")) else "record_json")
        snapshot = canonical(program)
        stored_snapshot = (_compress_revision(snapshot, fingerprint)
                           if storage_column == "record_zlib" else snapshot)
        values = (
            pid,
            program["institution"]["id"],
            unit_id,
            program["title"],
            program["award_level"],
            program["program_kind"],
            program.get("status", "unknown"),
            canonical(program["first_offered"]) if program.get("first_offered") else None,
            program.get("overview", ""),
            program.get("catalog_year"),
            program.get("verification_status", "partial"),
            program.get("curriculum_status", "pending"),
            program["last_verified"],
            fingerprint,
            stored_snapshot,
        )
        conn.execute(
            f"""INSERT INTO programs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
            institution_id=excluded.institution_id,hosting_unit_id=excluded.hosting_unit_id,title=excluded.title,
            award_level=excluded.award_level,program_kind=excluded.program_kind,status=excluded.status,
            first_offered_json=excluded.first_offered_json,overview=excluded.overview,catalog_year=excluded.catalog_year,
            verification_status=excluded.verification_status,curriculum_status=excluded.curriculum_status,
            last_verified=excluded.last_verified,content_hash=excluded.content_hash,{storage_column}=excluded.{storage_column}""",
            values,
        )
        # Optional award mappings must release source FKs before replacing sources.
        # The existence check also permits migration fixtures for older schemas.
        if conn.execute("SELECT 1 FROM sqlite_master WHERE name='program_awards'").fetchone():
            conn.execute("DELETE FROM program_awards WHERE program_id=?", (pid,))
        if conn.execute("SELECT 1 FROM sqlite_master WHERE name='course_identity_groups'").fetchone():
            conn.execute("DELETE FROM course_identity_groups WHERE program_id=?", (pid,))
        if conn.execute("SELECT 1 FROM sqlite_master WHERE name='program_parents'").fetchone():
            for table in ("program_major_relationships", "program_parent_reviews", "program_parents"):
                conn.execute(f"DELETE FROM {table} WHERE program_id=?", (pid,))
        # FK-safe replacement order; overrides and revisions are intentionally untouched.
        for table in (
            "program_family_memberships",
            "curriculum_review_sources",
            "curriculum_reviews",
            "requirement_courses",
            "requirement_groups",
            "courses",
            "outcomes",
            "program_links",
            "sources",
        ):
            conn.execute(f"DELETE FROM {table} WHERE program_id=?", (pid,))
        for s in program["sources"]:
            conn.execute(
                "INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    pid,
                    s["id"],
                    s["url"],
                    s.get("title", s["url"]),
                    s.get("fetched_at"),
                    s.get("source_date"),
                    s.get("catalog_year"),
                    s.get("locator"),
                    s.get("confidence", "medium"),
                ),
            )
        ingest_relationships(conn, program)
        for ordinal, award in enumerate(program.get("award_options", [])):
            conn.execute(
                "INSERT INTO program_awards VALUES (?,?,?,?,?,?)",
                (pid, ordinal, award["label"], award["normalized"],
                 award["source_id"], award["locator"]),
            )
        for link in program.get("links", []):
            conn.execute(
                "INSERT INTO program_links VALUES (?,?,?,?)",
                (pid, link["kind"], link["url"], link.get("label")),
            )
        audit = program.get("curriculum_audit")
        if audit:
            conn.execute(
                "INSERT INTO curriculum_reviews VALUES (?,?,?,?,?,?)",
                (
                    pid,
                    audit["scope"],
                    audit["reviewed_at"],
                    canonical(audit["sections"]),
                    canonical(audit["unresolved_requirements"]),
                    canonical(audit["metadata_gaps"]),
                ),
            )
            conn.executemany(
                "INSERT INTO curriculum_review_sources VALUES (?,?)",
                [(pid, source_id) for source_id in audit["source_ids"]],
            )
        for c in program.get("courses", []):
            conn.execute(
                "INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pid,
                    c["id"],
                    c["code"],
                    c["name"],
                    c.get("description"),
                    c.get("prerequisites"),
                    c.get("credits"),
                    c.get("credit_unit", "unknown"),
                    c.get("category", "other"),
                    c.get("source_id"),
                    c.get("url"),
                    c.get("public_site"),
                    c.get("syllabus"),
                ),
            )
        # Older migration fixtures may intentionally ingest before schema 015.
        if conn.execute("SELECT 1 FROM sqlite_master WHERE name='course_notes'").fetchone():
            conn.executemany("INSERT INTO course_notes VALUES (?,?,?,?)", [
                (pid, course["id"], position, note)
                for course in program.get("courses", [])
                for position, note in enumerate(course.get("notes", []))
            ])
        for group in program.get("course_identity_groups", []):
            conn.execute("INSERT INTO course_identity_groups VALUES (?,?,?,?,?,?,?)", (
                pid, group["id"], group["canonical_course_id"], group["relation"],
                group["reviewed_at"], group["locator"], group["rationale"],
            ))
            conn.executemany("INSERT INTO course_identity_members VALUES (?,?,?)", [
                (pid, group["id"], cid) for cid in group["course_ids"]
            ])
            conn.executemany("INSERT INTO course_identity_sources VALUES (?,?,?)", [
                (pid, group["id"], sid) for sid in group["source_ids"]
            ])
        for course in program.get("courses", []):
            review = course.get("category_review")
            if not review:
                continue
            conn.execute("INSERT INTO course_category_reviews VALUES (?,?,?,?,?,?,?,?)", (
                pid, course["id"], review["status"], review["taxonomy_version"],
                review["reviewed_at"], review["locator"], review["rationale"],
                canonical(review.get("candidate_categories", [])),
            ))
            conn.executemany("INSERT INTO course_category_review_sources VALUES (?,?,?)", [
                (pid, course["id"], sid) for sid in review["source_ids"]
            ])
        for g in program.get("requirements", []):
            conn.execute(
                "INSERT INTO requirement_groups VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pid,
                    g["id"],
                    g.get("parent_id"),
                    g["title"],
                    g["kind"],
                    g.get("count"),
                    g.get("credits"),
                    g.get("credit_unit", "unknown"),
                    g.get("category", "other"),
                    g.get("source_id"),
                    g.get("source_text"),
                    g.get("summary"),
                ),
            )
            for cid in g.get("course_ids", []):
                conn.execute("INSERT INTO requirement_courses VALUES (?,?,?)", (pid, g["id"], cid))
        for n, outcome in enumerate(program.get("outcomes", [])):
            conn.execute(
                "INSERT INTO outcomes(program_id,ordinal,text,kind,source_id,locator,statement_type) VALUES (?,?,?,?,?,?,?)",
                (
                    pid,
                    n,
                    outcome["text"],
                    outcome["kind"],
                    outcome.get("source_id"),
                    outcome.get("locator"),
                    outcome.get("statement_type", "unspecified"),
                ),
            )
        ingest_membership(conn, program)
        conn.execute(
            "INSERT OR IGNORE INTO program_revisions(program_id,content_hash,record_zlib,changed_at,scrape_run_id) VALUES (?,?,?,?,?)",
            (pid, fingerprint, _compress_revision(canonical(program), fingerprint), now(), run_id),
        )
        conn.execute(
            """UPDATE institutions SET coverage_status='confirmed',
            last_inspected=MAX(COALESCE(last_inspected,''),?) WHERE id=?""",
            (program["last_verified"], program["institution"]["id"]),
        )
    return True


def refresh_inspection_dates(conn):
    """Recompute the latest available inspection across every current program and survey.

    This also repairs dates left by earlier last-write-wins imports without
    changing any program, survey evidence, classification or review timestamp.
    """
    conn.execute("""UPDATE institutions SET last_inspected=(
        SELECT MAX(inspected_at) FROM (
            SELECT last_verified AS inspected_at FROM programs
            WHERE institution_id=institutions.id
            UNION ALL
            SELECT checked_at AS inspected_at FROM coverage_events
            WHERE institution_id=institutions.id
        )
    )""")


def ingest_survey(conn, entries):
    with atomic(conn):
        for entry in entries:
            iid = entry["institution_id"]
            if not conn.execute("SELECT 1 FROM institutions WHERE id=?", (iid,)).fetchone():
                raise ValueError(f"Survey institution not in database: {iid}")
            status = entry["status"]
            if status not in STATES:
                raise ValueError(f"Invalid coverage state {status}")
            if status == "pending":
                continue
            sources = entry.get("sources", [])
            if not sources:
                raise ValueError(f"{iid}: inspection must cite a source")
            conn.execute(
                "INSERT OR IGNORE INTO coverage_events(institution_id,status,checked_at,note,sources_json,fingerprint) VALUES (?,?,?,?,?,?)",
                (
                    iid,
                    status,
                    entry["checked_at"],
                    entry["note"],
                    canonical(sources),
                    digest(entry),
                ),
            )
            latest = conn.execute(
                "SELECT MAX(checked_at) FROM coverage_events WHERE institution_id=?",
                (iid,),
            ).fetchone()[0]
            current = entry["checked_at"] >= latest
            # A partial survey cannot downgrade a confirmed existing program.
            has_program = conn.execute(
                "SELECT 1 FROM programs WHERE institution_id=?", (iid,)
            ).fetchone()
            effective = "confirmed" if has_program else status
            if current:
                conn.execute(
                    """UPDATE institutions SET coverage_status=?,coverage_note=?,
                    last_inspected=MAX(COALESCE(last_inspected,''),?) WHERE id=?""",
                    (effective, entry["note"], entry["checked_at"], iid),
                )
            for d in entry.get("discoveries", []):
                # Older evidence can add an unseen lead, but cannot overwrite a
                # later reviewed classification. Same-day corrections still apply.
                conflict = (
                    """DO UPDATE SET
                    kind=COALESCE(excluded.kind,discoveries.kind),
                    award_level=COALESCE(excluded.award_level,discoveries.award_level)"""
                    if current else "DO NOTHING"
                )
                conn.execute(
                    """INSERT INTO discoveries(institution_id,title,kind,award_level,url) VALUES (?,?,?,?,?)
                    ON CONFLICT(institution_id,title,url) """ + conflict,
                    (iid, d["title"], d.get("kind"), d.get("award_level"), d["url"]),
                )


def set_override(conn, program_id, field, value, reason, evidence_url):
    if field not in OVERRIDE_FIELDS:
        raise ValueError(
            f"Override field must be one of {sorted(OVERRIDE_FIELDS)}; edit and review JSON for structural changes"
        )
    if not reason.strip() or urlparse(evidence_url).scheme not in {"http", "https"}:
        raise ValueError("Overrides require a reason and HTTP(S) evidence link")
    row = conn.execute("SELECT * FROM programs WHERE id=?", (program_id,)).fetchone()
    if not row:
        raise ValueError("Unknown program")
    candidate = program_record(row)
    candidate[field] = value
    from .family_store import load_family

    family = load_family(conn, candidate["family"]["id"]) if candidate.get("family") else None
    validate_program(candidate, family)
    if field == "status" and value not in {"active", "announced", "discontinued", "unknown"}:
        raise ValueError("Invalid program status")
    with atomic(conn):
        conn.execute(
            "INSERT OR REPLACE INTO manual_overrides VALUES (?,?,?,?,?,?)",
            (program_id, field, canonical(value), reason, evidence_url, now()),
        )


def initialize_csrankings(conn):
    config = {
        "fields": ["ai", "vision", "mlmining", "nlp", "inforet"],
        "year_start": 2016,
        "year_end": 2025,
        "geographic_filter": "us",
        "method": "Author-adjusted counts per field; geometric mean of (field count + 1), no subtraction; one-decimal rounding before competition ranks. National ranks would be computed before cohort filtering. No values computed or redistributed.",
        "source_snapshot": "5e8a27d68310c728a182b8bb3b6437c39bce0cad",
        "source_url": "https://csrankings.org/faq",
        "status": "not_imported",
    }
    with atomic(conn):
        conn.execute(
            "INSERT OR REPLACE INTO csrankings_config VALUES (1,?,?,?,?,?,?,?,?)",
            (
                canonical(config["fields"]),
                config["year_start"],
                config["year_end"],
                config["geographic_filter"],
                config["method"],
                config["source_snapshot"],
                config["source_url"],
                config["status"],
            ),
        )
        for row in conn.execute("SELECT id FROM institutions").fetchall():
            for field in config["fields"] + ["aggregate"]:
                conn.execute(
                    "INSERT OR IGNORE INTO csrankings_observations VALUES (?,?,NULL,NULL,?,1)",
                    (row["id"], field, "permission_required"),
                )


def resolve_stored_program(conn, record):
    from .families import resolve_program
    from .family_store import load_family

    family = load_family(conn, record["family"]["id"]) if record.get("family") else None
    return resolve_program(record, family)


def export_data(conn):
    from .family_store import export_families

    families = export_families(conn)
    cohort_row = conn.execute("SELECT value_json FROM metadata WHERE key='cohort'").fetchone()
    cohort = (
        json.loads(cohort_row[0])
        if cohort_row
        else {"complete": False, "definition": "Cohort not imported"}
    )
    programs = []
    for row in conn.execute("SELECT * FROM programs ORDER BY id"):
        record = resolve_stored_program(conn, program_record(row))
        overrides = []
        for override in conn.execute(
            "SELECT * FROM manual_overrides WHERE program_id=? ORDER BY field", (row["id"],)
        ):
            record[override["field"]] = json.loads(override["value_json"])
            overrides.append(
                {k: override[k] for k in ("field", "reason", "evidence_url", "updated_at")}
            )
        record["manual_overrides"] = overrides
        record["institution"]["rankings"] = [
            dict(rank)
            for rank in conn.execute(
                "SELECT publisher,edition,category,rank,source_url,verification_status,source_date,fetched_at,locator,rank_upper_bound FROM rankings WHERE institution_id=? ORDER BY category",
                (row["institution_id"],),
            )
        ]
        programs.append(record)
    institutions = []
    summary = {status: 0 for status in sorted(STATES)}
    for row in conn.execute("SELECT * FROM institutions ORDER BY name"):
        inst = dict(row)
        iid = inst["id"]
        inst["aliases"] = [
            a[0]
            for a in conn.execute(
                "SELECT alias FROM institution_aliases WHERE institution_id=? ORDER BY alias",
                (iid,),
            )
        ]
        inst["rankings"] = [
            dict(r)
            for r in conn.execute(
                "SELECT publisher,edition,category,rank,source_url,verification_status,source_date,fetched_at,locator,rank_upper_bound FROM rankings WHERE institution_id=? ORDER BY category",
                (iid,),
            )
        ]
        inst["program_ids"] = [p["id"] for p in programs if p["institution"]["id"] == iid]
        inst["discoveries"] = [
            dict(d)
            for d in conn.execute(
                "SELECT title,kind,award_level,url FROM discoveries WHERE institution_id=? ORDER BY title",
                (iid,),
            )
        ]
        inst["coverage_sources"] = []
        for event in conn.execute(
            "SELECT sources_json FROM coverage_events WHERE institution_id=? ORDER BY checked_at,id",
            (iid,),
        ):
            inst["coverage_sources"].extend(json.loads(event[0]))
        summary[inst["coverage_status"]] += 1
        institutions.append(inst)
    config_row = conn.execute("SELECT * FROM csrankings_config").fetchone()
    config = dict(config_row) if config_row else {"status": "not_imported"}
    if "fields_json" in config:
        config["fields"] = json.loads(config.pop("fields_json"))
    # Stable build date is derived from evidence, never wall clock, so reruns match byte-for-byte.
    dates = [p["last_verified"] for p in programs] + [
        i["last_inspected"] for i in institutions if i["last_inspected"]
    ]
    generated = max(dates, default="Not yet verified")
    summary.update(
        {
            "institutions": len(institutions),
            "programs": len(programs),
            "cohort_complete": cohort.get("complete", False),
            "attempted_total": len(institutions) - summary["pending"],
            "inspected_total": summary["confirmed"]
            + summary["inspected"]
            + summary["no_qualifying_program_found"],
        }
    )
    limitations = [
        "Cohort enumeration and institution searches remain incomplete. Counts describe the loaded research inventory, not the full target cohort.",
        "Confirmed means at least one official qualifying program found; it does not certify a complete institution inventory.",
        "Curriculum records may be partial. Missing courses, dates, prerequisites, outcomes and syllabi are unknown, not absent.",
        "Credit systems and degree structures differ. Course counts are observed records, not degree percentages or quality scores.",
        "CSRankings values are not imported pending reuse permission. Publication rankings do not measure undergraduate teaching quality.",
    ]
    curriculum = {
        status: sum(p.get("curriculum_status", "pending") == status for p in programs)
        for status in ("complete", "partial", "pending")
    }
    course_rows = [course for program in programs for course in program.get("courses", [])]
    curriculum.update(
        {
            "program_course_records": len(course_rows),
            "requirement_nodes": sum(len(p.get("requirements", [])) for p in programs),
            "review_audits": sum(bool(p.get("curriculum_audit")) for p in programs),
            "course_metadata": {
                field: sum(
                    course.get(field) is not None and course.get(field) != ""
                    for course in course_rows
                )
                for field in (
                    "name",
                    "description",
                    "prerequisites",
                    "credits",
                    "public_site",
                    "syllabus",
                )
            },
            "credit_amount_and_unit": sum(
                course.get("credits") is not None
                and course.get("credit_unit", "unknown") != "unknown"
                for course in course_rows
            ),
            "counting_note": "Program-course records include elective pools and repeats across sibling programs. Requirement completeness and course metadata availability are separate; unknown prerequisites do not mean no prerequisites.",
        }
    )
    from .degree_audit import audit_summary
    audit_row = conn.execute("SELECT value_json FROM metadata WHERE key='degree_audit'").fetchone()
    audit = audit_summary(json.loads(audit_row[0]) if audit_row else {}, programs)
    audit_lookup = {e["program_id"]: e for e in audit["programs"]}
    for program in programs:
        if program["id"] in audit_lookup:
            program["degree_audit"] = audit_lookup[program["id"]]
    return {
        "meta": {
            "generated_at": generated,
            "cohort": cohort,
            "coverage_summary": summary,
            "curriculum_summary": curriculum,
            "degree_audit": audit,
            "family_summary": {
                "families": len(families),
                "variants": sum(bool(p.get("family")) for p in programs),
                "ungrouped_programs": sum(not p.get("family") for p in programs),
            },
            "limitations": limitations,
        },
        "institutions": institutions,
        "programs": programs,
        "families": families,
        "rankings": [
            dict(r)
            for r in conn.execute("SELECT * FROM rankings ORDER BY category,rank,institution_id")
        ],
        "csrankings": {
            "methodology": config,
            "observations": [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM csrankings_observations ORDER BY institution_id,field"
                )
            ],
        },
    }
