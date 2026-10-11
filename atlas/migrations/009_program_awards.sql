-- Optional reviewed award options preserve exact labels and verified mappings.
-- No existing unusual abbreviation is silently normalized by this migration.
CREATE TABLE program_awards (
 program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
 ordinal INTEGER NOT NULL CHECK(ordinal>=0),
 label TEXT NOT NULL CHECK(length(trim(label))>0),
 normalized TEXT NOT NULL CHECK(normalized IN ('BS','BSE','BA','other')),
 source_id TEXT NOT NULL,
 locator TEXT NOT NULL CHECK(length(trim(locator))>0),
 PRIMARY KEY(program_id,ordinal),
 UNIQUE(program_id,label,normalized),
 FOREIGN KEY(program_id,source_id) REFERENCES sources(program_id,id)
) WITHOUT ROWID;
