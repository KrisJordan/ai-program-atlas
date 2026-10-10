-- Provenance kind and the type of the statement answer different questions.
-- Existing unclassified statements must not become learning outcomes by inference.
ALTER TABLE outcomes ADD COLUMN statement_type TEXT NOT NULL DEFAULT 'unspecified'
 CHECK(statement_type IN ('learning_outcome','program_aim','career_pathway','unspecified'));
