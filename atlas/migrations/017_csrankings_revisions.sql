CREATE TABLE csrankings_revisions (
    id INTEGER PRIMARY KEY,
    content_hash TEXT NOT NULL UNIQUE,
    source_snapshot TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    artifact_json TEXT NOT NULL CHECK(json_valid(artifact_json))
);
