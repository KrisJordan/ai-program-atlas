-- A named official course may have no published code. Preserve every existing
-- field and child reference; db.migrate disables FKs before BEGIN and checks
-- the rebuilt graph before commit. Never rename the old referenced table.
CREATE TABLE courses_new (
 program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
 id TEXT NOT NULL,code TEXT,name TEXT,description TEXT,prerequisites TEXT,
 credits REAL CHECK(credits IS NULL OR credits>=0),credit_unit TEXT NOT NULL,
 category TEXT NOT NULL,source_id TEXT,url TEXT,public_site TEXT,syllabus TEXT,
 PRIMARY KEY(program_id,id),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
INSERT INTO courses_new SELECT * FROM courses;
DROP TABLE courses;
ALTER TABLE courses_new RENAME TO courses;
