-- Independent editorial taxonomy judgments, separate from requirement membership.
CREATE TABLE course_category_reviews (
 program_id TEXT NOT NULL,
 course_id TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('reviewed','mixed','unclassified')),
 taxonomy_version TEXT NOT NULL CHECK(taxonomy_version='1'),
 reviewed_at TEXT NOT NULL,
 locator TEXT NOT NULL CHECK(length(trim(locator))>0),
 rationale TEXT NOT NULL CHECK(length(trim(rationale))>0),
 candidate_categories_json TEXT NOT NULL,
 PRIMARY KEY(program_id,course_id),
 FOREIGN KEY(program_id,course_id) REFERENCES courses(program_id,id) ON DELETE CASCADE
) WITHOUT ROWID;
CREATE TABLE course_category_review_sources (
 program_id TEXT NOT NULL,
 course_id TEXT NOT NULL,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,course_id,source_id),
 FOREIGN KEY(program_id,course_id) REFERENCES course_category_reviews(program_id,course_id) ON DELETE CASCADE,
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
