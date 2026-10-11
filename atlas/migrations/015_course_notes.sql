-- Notes were already preserved in canonical snapshots and public JSON. Make
-- them individually queryable without changing any original record/hash.
CREATE TABLE course_notes (
 program_id TEXT NOT NULL,
 course_id TEXT NOT NULL,
 position INTEGER NOT NULL CHECK(position>=0),
 note TEXT NOT NULL CHECK(typeof(note)='text' AND length(trim(note))>0),
 PRIMARY KEY(program_id,course_id,position),
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id) ON DELETE CASCADE
) WITHOUT ROWID;
INSERT INTO course_notes(program_id,course_id,position,note)
 SELECT p.id,json_extract(c.value,'$.id'),n.key,n.value
 FROM programs p,
 json_each(atlas_verified_program_json(p.record_zlib,p.content_hash),'$.courses') c,
 json_each(c.value,'$.notes') n;
