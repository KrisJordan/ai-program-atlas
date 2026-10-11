-- Preserve canonical bytes and their existing hashes while removing the large
-- duplicate JSON text. Relational facts, foreign keys, overrides and history are
-- untouched. The temporary default permits SQLite's in-place ADD COLUMN on a
-- populated parent table; application inserts always supply verified payloads.
ALTER TABLE programs ADD COLUMN record_zlib BLOB NOT NULL DEFAULT X'00'
 CHECK(typeof(record_zlib)='blob' AND length(record_zlib)>0);
UPDATE programs SET record_zlib=atlas_compress_revision(record_json,content_hash);
ALTER TABLE programs DROP COLUMN record_json;
