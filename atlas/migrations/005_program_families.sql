CREATE TABLE program_families (
 id TEXT PRIMARY KEY, institution_id TEXT NOT NULL REFERENCES institutions(id),
 name TEXT NOT NULL, description TEXT NOT NULL,
 classification_kind TEXT NOT NULL CHECK(classification_kind IN ('source_stated','analyst_classified')),
 content_hash TEXT NOT NULL, metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE TABLE family_sources (
 family_id TEXT NOT NULL REFERENCES program_families(id) ON DELETE CASCADE,
 id TEXT NOT NULL, url TEXT NOT NULL, title TEXT NOT NULL, fetched_at TEXT,
 source_date TEXT, catalog_year TEXT, locator TEXT, confidence TEXT,
 PRIMARY KEY(family_id,id)
);
CREATE TABLE family_requirement_groups (
 family_id TEXT NOT NULL REFERENCES program_families(id) ON DELETE CASCADE,
 id TEXT NOT NULL, parent_id TEXT, title TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('all','choose_courses','choose_credits','alternative','note')),
 choose_count INTEGER CHECK(choose_count IS NULL OR choose_count>0),
 credits REAL CHECK(credits IS NULL OR credits>0), credit_unit TEXT NOT NULL,
 category TEXT NOT NULL, source_id TEXT NOT NULL, source_text TEXT, summary TEXT,
 course_codes_json TEXT NOT NULL CHECK(json_valid(course_codes_json) AND json_type(course_codes_json)='array'),
 component TEXT NOT NULL CHECK(component IN ('ai_core','domain','integration','other')),
 ordinal INTEGER NOT NULL,
 PRIMARY KEY(family_id,id),
 FOREIGN KEY(family_id,parent_id) REFERENCES family_requirement_groups(family_id,id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(family_id,source_id) REFERENCES family_sources(family_id,id)
);
CREATE TABLE program_family_memberships (
 program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
 family_id TEXT NOT NULL REFERENCES program_families(id),
 variant_label TEXT NOT NULL,
 relationship TEXT NOT NULL CHECK(relationship IN ('ai_plus_x','x_plus_ai','integrated','unknown')),
 classification_kind TEXT NOT NULL CHECK(classification_kind IN ('source_stated','analyst_classified','unknown')),
 UNIQUE(program_id,family_id)
);
CREATE TABLE program_family_disciplines (
 program_id TEXT NOT NULL REFERENCES program_family_memberships(program_id) ON DELETE CASCADE,
 discipline TEXT NOT NULL, PRIMARY KEY(program_id,discipline)
);
CREATE TABLE program_family_sources (
 program_id TEXT NOT NULL REFERENCES program_family_memberships(program_id) ON DELETE CASCADE,
 source_id TEXT NOT NULL, PRIMARY KEY(program_id,source_id),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
CREATE TABLE program_family_hosting_units (
 program_id TEXT NOT NULL REFERENCES program_family_memberships(program_id) ON DELETE CASCADE,
 unit_id INTEGER NOT NULL REFERENCES hosting_units(id), source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,unit_id), FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
CREATE TABLE family_requirement_bindings (
 program_id TEXT NOT NULL, family_id TEXT NOT NULL, shared_id TEXT NOT NULL,
 local_id TEXT NOT NULL, parent_id TEXT, source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,shared_id), UNIQUE(program_id,local_id),
 FOREIGN KEY(program_id,family_id) REFERENCES program_family_memberships(program_id,family_id) ON DELETE CASCADE,
 FOREIGN KEY(family_id,shared_id) REFERENCES family_requirement_groups(family_id,id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
CREATE TABLE family_binding_courses (
 program_id TEXT NOT NULL, shared_id TEXT NOT NULL, course_id TEXT NOT NULL,
 PRIMARY KEY(program_id,shared_id,course_id),
 FOREIGN KEY(program_id,shared_id) REFERENCES family_requirement_bindings(program_id,shared_id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id)
);
CREATE TABLE family_requirement_overrides (
 program_id TEXT NOT NULL, family_id TEXT NOT NULL, shared_id TEXT NOT NULL,
 operation TEXT NOT NULL CHECK(operation IN ('exclude','replace')), reason TEXT NOT NULL, source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,shared_id),
 FOREIGN KEY(program_id,family_id) REFERENCES program_family_memberships(program_id,family_id) ON DELETE CASCADE,
 FOREIGN KEY(family_id,shared_id) REFERENCES family_requirement_groups(family_id,id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
CREATE TABLE family_revisions (
 id INTEGER PRIMARY KEY, family_id TEXT NOT NULL REFERENCES program_families(id),
 content_hash TEXT NOT NULL, record_json TEXT NOT NULL CHECK(json_valid(record_json)), changed_at TEXT NOT NULL,
 UNIQUE(family_id,content_hash)
);
-- A local parent can now be a bound inherited node. The resolved graph is
-- validated atomically in Python; local course/source foreign keys stay intact.
CREATE TABLE saved_requirement_groups AS SELECT * FROM requirement_groups;
CREATE TABLE saved_requirement_courses AS SELECT * FROM requirement_courses;
DROP TABLE requirement_courses;
DROP TABLE requirement_groups;
CREATE TABLE requirement_groups (
 program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,id TEXT NOT NULL,parent_id TEXT,title TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('all','choose_courses','choose_credits','alternative','note')),
 choose_count INTEGER CHECK(choose_count IS NULL OR choose_count>0),credits REAL CHECK(credits IS NULL OR credits>0),
 credit_unit TEXT NOT NULL,category TEXT NOT NULL,source_id TEXT,source_text TEXT,summary TEXT,
 PRIMARY KEY(program_id,id),FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id),
 CHECK(parent_id IS NULL OR parent_id!=id)
);
CREATE TABLE requirement_courses (
 program_id TEXT NOT NULL,requirement_id TEXT NOT NULL,course_id TEXT NOT NULL,
 PRIMARY KEY(program_id,requirement_id,course_id),
 FOREIGN KEY(program_id,requirement_id) REFERENCES requirement_groups(program_id,id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id) ON DELETE CASCADE
);
INSERT INTO requirement_groups SELECT * FROM saved_requirement_groups;
INSERT INTO requirement_courses SELECT * FROM saved_requirement_courses;
DROP TABLE saved_requirement_courses;
DROP TABLE saved_requirement_groups;
CREATE INDEX groups_parent ON requirement_groups(program_id,parent_id);
