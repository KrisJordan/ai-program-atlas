CREATE TABLE curriculum_reviews (
 program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
 scope TEXT NOT NULL CHECK(scope IN ('degree','minor','concentration','additional_major')),
 reviewed_at TEXT NOT NULL,
 sections_json TEXT NOT NULL CHECK(json_valid(sections_json) AND json_type(sections_json)='array' AND json_array_length(sections_json)>0),
 unresolved_json TEXT NOT NULL CHECK(json_valid(unresolved_json) AND json_type(unresolved_json)='array'),
 metadata_gaps_json TEXT NOT NULL CHECK(json_valid(metadata_gaps_json) AND json_type(metadata_gaps_json)='array')
);
CREATE TABLE curriculum_review_sources (
 program_id TEXT NOT NULL REFERENCES curriculum_reviews(program_id) ON DELETE CASCADE,
 source_id TEXT NOT NULL,
 PRIMARY KEY(program_id,source_id),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
);
