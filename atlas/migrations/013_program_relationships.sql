-- Relationships never change an award or infer a parent from a hosting unit.
CREATE TABLE program_major_relationships (
 program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
 kind TEXT NOT NULL CHECK(kind='second_major_only'),
 official_term TEXT NOT NULL CHECK(length(trim(official_term))>0),
 eligibility TEXT NOT NULL CHECK(length(trim(eligibility))>0),
 locator TEXT NOT NULL CHECK(length(trim(locator))>0),
 reviewed_at TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE program_major_relationship_sources (
 program_id TEXT NOT NULL REFERENCES program_major_relationships(program_id) ON DELETE CASCADE,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,source_id),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
CREATE TABLE program_parent_reviews (
 program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
 status TEXT NOT NULL CHECK(status IN ('verified','partial','unknown')),
 reviewed_at TEXT NOT NULL,
 notes_json TEXT NOT NULL CHECK(json_valid(notes_json))
) WITHOUT ROWID;
CREATE TABLE program_parent_review_sources (
 program_id TEXT NOT NULL REFERENCES program_parent_reviews(program_id) ON DELETE CASCADE,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,source_id),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
CREATE TABLE program_parents (
 program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
 id TEXT NOT NULL,
 ordinal INTEGER NOT NULL CHECK(ordinal>=0),
 title TEXT NOT NULL CHECK(length(trim(title))>0),
 award_level TEXT,
 award_label TEXT,
 relationship TEXT NOT NULL CHECK(relationship IN ('concentration','track','specialization','emphasis','immersion')),
 parent_program_id TEXT REFERENCES programs(id) DEFERRABLE INITIALLY DEFERRED,
 eligibility TEXT,
 locator TEXT NOT NULL CHECK(length(trim(locator))>0),
 reviewed_at TEXT NOT NULL,
 PRIMARY KEY(program_id,id),
 UNIQUE(program_id,ordinal),
 CHECK(parent_program_id IS NULL OR parent_program_id!=program_id)
) WITHOUT ROWID;
CREATE TABLE program_parent_sources (
 program_id TEXT NOT NULL,
 parent_id TEXT NOT NULL,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,parent_id,source_id),
 FOREIGN KEY(program_id,parent_id) REFERENCES program_parents(program_id,id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
