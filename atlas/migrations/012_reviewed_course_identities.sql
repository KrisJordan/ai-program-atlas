-- A reviewed cross-listing preserves every code while counting one offering.
CREATE TABLE course_identity_groups (
 program_id TEXT NOT NULL,
 id TEXT NOT NULL,
 canonical_course_id TEXT NOT NULL,
 relation TEXT NOT NULL CHECK(relation='crosslisted'),
 reviewed_at TEXT NOT NULL,
 locator TEXT NOT NULL CHECK(length(trim(locator))>0),
 rationale TEXT NOT NULL CHECK(length(trim(rationale))>0),
 PRIMARY KEY(program_id,id),
 FOREIGN KEY(program_id,canonical_course_id) REFERENCES courses(program_id,id)
) WITHOUT ROWID;
CREATE TABLE course_identity_members (
 program_id TEXT NOT NULL,
 group_id TEXT NOT NULL,
 course_id TEXT NOT NULL,
 PRIMARY KEY(program_id,group_id,course_id),
 UNIQUE(program_id,course_id),
 FOREIGN KEY(program_id,group_id) REFERENCES course_identity_groups(program_id,id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id)
) WITHOUT ROWID;
CREATE TABLE course_identity_sources (
 program_id TEXT NOT NULL,
 group_id TEXT NOT NULL,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,group_id,source_id),
 FOREIGN KEY(program_id,group_id) REFERENCES course_identity_groups(program_id,id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
