"""Career possibilities and program aims must not become learning claims."""

import pytest
from atlas import db
from tests.test_core_review import program


@pytest.mark.parametrize(
    "statement_type", ["learning_outcome", "program_aim", "career_pathway", "unspecified", None]
)
def test_statement_type_is_explicit_and_independent_of_provenance(tmp_path, statement_type):
    record = program()
    outcome = {
        "text": "Reviewed source statement",
        "kind": "source_stated",
        "source_id": record["sources"][0]["id"],
        "locator": "Verified section",
    }
    if statement_type is not None:
        outcome["statement_type"] = statement_type
    record["outcomes"] = [outcome]
    conn = db.connect(tmp_path / "atlas.sqlite")
    db.migrate(conn)
    db.ingest_program(conn, record)
    row = conn.execute("SELECT kind,statement_type FROM outcomes").fetchone()
    assert tuple(row) == ("source_stated", statement_type or "unspecified")
    exported = db.export_data(conn)["programs"][0]["outcomes"][0]
    assert exported.get("statement_type", "unspecified") == (statement_type or "unspecified")
    assert not db.ingest_program(conn, record)
    conn.close()


def test_unknown_statement_type_rejected():
    record = program()
    record["outcomes"] = [
        {
            "text": "A claim",
            "kind": "source_stated",
            "source_id": record["sources"][0]["id"],
            "statement_type": "guaranteed_job",
        }
    ]
    with pytest.raises(ValueError, match="statement type"):
        db.validate_program(record)
