"""Known zero obligations survive storage; zero-credit choice amounts do not."""
import sqlite3
import pytest
from atlas import db
from tests.test_core_review import conn, program  # noqa: F401


def zero_program(kind="all"):
    p = program()
    p["courses"] = [dict(id="orientation", code="ORI 100", name="Orientation",
        credits=0, credit_unit="semester_hours", source_id="catalog", category="other")]
    p["requirements"] = [dict(id="orientation", parent_id=None, title="Required orientation",
        kind=kind, credits=0, credit_unit="semester_hours", source_id="catalog", course_ids=["orientation"])]
    return p


@pytest.mark.parametrize("kind", ["all", "note", "alternative"])
def test_published_zero_is_not_replaced_by_unknown(conn, kind):
    p = zero_program(kind)
    assert db.ingest_program(conn, p)
    assert not db.ingest_program(conn, p)
    assert conn.execute("SELECT credits FROM requirement_groups").fetchone()[0] == 0
    assert db.export_data(conn)["programs"][0]["requirements"][0]["credits"] == 0
    assert db.export_data(conn)["programs"][0]["courses"][0]["credits"] == 0
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()


def test_credit_selection_must_still_be_positive(conn):
    with pytest.raises(ValueError, match="positive"):
        db.ingest_program(conn, zero_program("choose_credits"))
    db.ingest_program(conn, zero_program())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE requirement_groups SET kind='choose_credits'")


@pytest.mark.parametrize("amount", [-1, True, "0", float("nan"), float("inf")])
def test_invalid_amount_is_rejected_before_replacement(conn, amount):
    p = zero_program()
    db.ingest_program(conn, p)
    p["requirements"][0]["credits"] = amount
    with pytest.raises(ValueError, match="nonnegative"):
        db.ingest_program(conn, p)
    assert conn.execute("SELECT credits FROM requirement_groups").fetchone()[0] == 0
