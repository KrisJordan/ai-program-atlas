-- Source-known zero credit requirements are facts, not missing values.
-- Credit-selection rules still require a strictly positive amount.
CREATE TABLE saved_requirement_groups AS SELECT * FROM requirement_groups;
CREATE TABLE saved_requirement_courses AS SELECT * FROM requirement_courses;
DROP TABLE requirement_courses;
DROP TABLE requirement_groups;
CREATE TABLE requirement_groups (
 program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,id TEXT NOT NULL,parent_id TEXT,title TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('all','choose_courses','choose_credits','alternative','note')),
 choose_count INTEGER CHECK(choose_count IS NULL OR choose_count>0),credits REAL CHECK(credits IS NULL OR credits>=0) CHECK(kind!='choose_credits' OR (credits IS NOT NULL AND credits>0)),
 credit_unit TEXT NOT NULL,category TEXT NOT NULL,source_id TEXT,source_text TEXT,summary TEXT,
 PRIMARY KEY(program_id,id),FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id),
 CHECK(parent_id IS NULL OR parent_id!=id)
) WITHOUT ROWID;
CREATE TABLE requirement_courses (
 program_id TEXT NOT NULL,requirement_id TEXT NOT NULL,course_id TEXT NOT NULL,
 PRIMARY KEY(program_id,requirement_id,course_id),
 FOREIGN KEY(program_id,requirement_id) REFERENCES requirement_groups(program_id,id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id) ON DELETE CASCADE
) WITHOUT ROWID;
INSERT INTO requirement_groups SELECT * FROM saved_requirement_groups;
INSERT INTO requirement_courses SELECT * FROM saved_requirement_courses;
DROP TABLE saved_requirement_courses;
DROP TABLE saved_requirement_groups;
CREATE INDEX groups_parent ON requirement_groups(program_id,parent_id);

CREATE TABLE saved_family_requirement_groups AS SELECT * FROM family_requirement_groups;
DROP TABLE family_requirement_groups;
CREATE TABLE family_requirement_groups (
 family_id TEXT NOT NULL REFERENCES program_families(id) ON DELETE CASCADE,
 id TEXT NOT NULL, parent_id TEXT, title TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('all','choose_courses','choose_credits','alternative','note')),
 choose_count INTEGER CHECK(choose_count IS NULL OR choose_count>0),
 credits REAL CHECK(credits IS NULL OR credits>=0) CHECK(kind!='choose_credits' OR (credits IS NOT NULL AND credits>0)), credit_unit TEXT NOT NULL,
 category TEXT NOT NULL, source_id TEXT NOT NULL, source_text TEXT, summary TEXT,
 course_codes_json TEXT NOT NULL CHECK(json_valid(course_codes_json) AND json_type(course_codes_json)='array'),
 component TEXT NOT NULL CHECK(component IN ('ai_core','domain','integration','other')),
 ordinal INTEGER NOT NULL,
 PRIMARY KEY(family_id,id),
 FOREIGN KEY(family_id,parent_id) REFERENCES family_requirement_groups(family_id,id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(family_id,source_id) REFERENCES family_sources(family_id,id)
);
INSERT INTO family_requirement_groups SELECT * FROM saved_family_requirement_groups;
DROP TABLE saved_family_requirement_groups;
