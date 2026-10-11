-- Lossless zlib encoding of canonical UTF-8 JSON. Preserve all revision IDs,
-- hashes, timestamps and run associations; the Python migration hook verifies
-- each original hash before encoding it. Current relational facts are unchanged.
ALTER TABLE program_revisions RENAME TO program_revisions_uncompressed;
CREATE TABLE program_revisions (
 id INTEGER PRIMARY KEY,
 program_id TEXT NOT NULL REFERENCES programs(id),
 content_hash TEXT NOT NULL,
 record_zlib BLOB NOT NULL CHECK(typeof(record_zlib)='blob' AND length(record_zlib)>0),
 changed_at TEXT NOT NULL,
 scrape_run_id INTEGER REFERENCES scrape_runs(id),
 UNIQUE(program_id,content_hash)
);
INSERT INTO program_revisions(id,program_id,content_hash,record_zlib,changed_at,scrape_run_id)
SELECT id,program_id,content_hash,atlas_compress_revision(record_json,content_hash),changed_at,scrape_run_id
FROM program_revisions_uncompressed;
DROP TABLE program_revisions_uncompressed;
