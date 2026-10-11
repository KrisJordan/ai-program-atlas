"""Relational storage for reviewed common requirements and variant bindings."""

import json

from .families import validate_family


def load_family(conn, family_id):
    row = conn.execute("SELECT * FROM program_families WHERE id=?", (family_id,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown program family: {family_id}")
    # Retain the exact reviewed shape for stable content hashes and optional annotations.
    # Normalized tables provide relational queries and integrity; variants only bind IDs.
    return json.loads(row["metadata_json"])


def ingest_family(conn, family, program_updates=None):
    from . import db

    validate_family(family)
    updates = program_updates or {}
    if any(pid != program.get("id") for pid, program in updates.items()):
        raise ValueError("Program update mapping key must match record id")
    dependents = {
        r["program_id"]: db.program_record(r)
        for r in conn.execute(
            "SELECT m.program_id,p.record_zlib,p.content_hash FROM program_family_memberships m JOIN programs p ON p.id=m.program_id WHERE m.family_id=?",
            (family["id"],),
        )
    }
    dependents.update(
        {pid: p for pid, p in updates.items() if p.get("family", {}).get("id") == family["id"]}
    )
    for pid, previous in dependents.items():
        program = updates.get(pid, previous)
        if program.get("family", {}).get("id") == family["id"]:
            db.validate_program(program, family)
    fingerprint = db.digest(family)
    existing = conn.execute(
        "SELECT content_hash FROM program_families WHERE id=?", (family["id"],)
    ).fetchone()
    changed = not existing or existing[0] != fingerprint
    with db.atomic(conn):
        if not changed:
            for pid in dependents:
                if pid in updates:
                    db.ingest_program(conn, updates[pid])
            return False
        conn.execute(
            """INSERT INTO program_families VALUES (?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
            institution_id=excluded.institution_id,name=excluded.name,description=excluded.description,
            classification_kind=excluded.classification_kind,content_hash=excluded.content_hash,metadata_json=excluded.metadata_json""",
            (
                family["id"],
                family["institution_id"],
                family["name"],
                family.get("description", ""),
                family["classification_kind"],
                fingerprint,
                db.canonical(family),
            ),
        )
        conn.execute("DELETE FROM family_requirement_groups WHERE family_id=?", (family["id"],))
        conn.execute("DELETE FROM family_sources WHERE family_id=?", (family["id"],))
        for source in family["sources"]:
            conn.execute(
                "INSERT INTO family_sources VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    family["id"],
                    source["id"],
                    source["url"],
                    source.get("title", source["url"]),
                    source.get("fetched_at"),
                    source.get("source_date"),
                    source.get("catalog_year"),
                    source.get("locator"),
                    source.get("confidence", "medium"),
                ),
            )
        for index, node in enumerate(family["shared_requirements"]):
            conn.execute(
                "INSERT INTO family_requirement_groups VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    family["id"],
                    node["id"],
                    node.get("parent_id"),
                    node["title"],
                    node["kind"],
                    node.get("count"),
                    node.get("credits"),
                    node.get("credit_unit", "unknown"),
                    node.get("category", "other"),
                    node["source_id"],
                    node.get("source_text"),
                    node.get("summary"),
                    db.canonical(node.get("course_codes", [])),
                    node.get("component", "other"),
                    index,
                ),
            )
        conn.execute(
            "INSERT OR IGNORE INTO family_revisions(family_id,content_hash,record_json,changed_at) VALUES (?,?,?,?)",
            (family["id"], fingerprint, db.canonical(family), db.now()),
        )
        for pid in dependents:
            if pid in updates:
                db.ingest_program(conn, updates[pid])
    return True


def ingest_membership(conn, program):
    """Called within the same transaction as program sources/courses/local nodes."""
    membership = program.get("family")
    if not membership:
        return
    pid, fid = program["id"], membership["id"]
    conn.execute(
        "INSERT INTO program_family_memberships VALUES (?,?,?,?,?)",
        (
            pid,
            fid,
            membership["variant_label"],
            membership.get("relationship", "unknown"),
            membership.get("classification_kind", "unknown"),
        ),
    )
    conn.executemany(
        "INSERT INTO program_family_disciplines VALUES (?,?)",
        [(pid, v) for v in set(membership["disciplines"])],
    )
    conn.executemany(
        "INSERT INTO program_family_sources VALUES (?,?)",
        [(pid, v) for v in set(membership["source_ids"])],
    )
    for unit in membership.get("hosting_units", []):
        conn.execute(
            "INSERT OR IGNORE INTO hosting_units(institution_id,name) VALUES (?,?)",
            (program["institution"]["id"], unit["name"]),
        )
        uid = conn.execute(
            "SELECT id FROM hosting_units WHERE institution_id=? AND name=?",
            (program["institution"]["id"], unit["name"]),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO program_family_hosting_units VALUES (?,?,?)", (pid, uid, unit["source_id"])
        )
    for binding in membership.get("requirement_bindings", []):
        conn.execute(
            "INSERT INTO family_requirement_bindings VALUES (?,?,?,?,?,?)",
            (
                pid,
                fid,
                binding["shared_id"],
                binding["id"],
                binding.get("parent_id"),
                binding["source_id"],
            ),
        )
        conn.executemany(
            "INSERT INTO family_binding_courses VALUES (?,?,?)",
            [(pid, binding["shared_id"], cid) for cid in binding.get("course_ids", [])],
        )
    for override in membership.get("requirement_overrides", []):
        conn.execute(
            "INSERT INTO family_requirement_overrides VALUES (?,?,?,?,?,?)",
            (
                pid,
                fid,
                override["shared_id"],
                override["operation"],
                override["reason"],
                override["source_id"],
            ),
        )


def export_families(conn):
    families = []
    for row in conn.execute("SELECT id FROM program_families ORDER BY id"):
        family = load_family(conn, row["id"])
        family["variant_ids"] = [
            r[0]
            for r in conn.execute(
                "SELECT program_id FROM program_family_memberships WHERE family_id=? ORDER BY program_id",
                (family["id"],),
            )
        ]
        family["disciplines"] = [
            r[0]
            for r in conn.execute(
                "SELECT DISTINCT d.discipline FROM program_family_disciplines d JOIN program_family_memberships m USING(program_id) WHERE m.family_id=? ORDER BY d.discipline",
                (family["id"],),
            )
        ]
        family["shared_course_codes"] = sorted(
            {
                code
                for node in family["shared_requirements"]
                for code in node.get("course_codes", [])
            }
        )
        families.append(family)
    return families
