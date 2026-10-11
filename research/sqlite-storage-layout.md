# SQLite requirement storage

Reviewed 2026-10-11 against the maintained 142-program publication checkpoint. GitHub accepted the database but reported its large-file advisory. Migration 008 changes only the physical layout of `requirement_groups` and `requirement_courses`: each composite primary key is stored once using SQLite `WITHOUT ROWID`, instead of both in a rowid table and a separate unique index. All columns, keys, constraints, source references and the parent lookup index remain available to ordinary SQLite queries. Current program JSON and normalized relational data remain readable without custom extensions.

The migration runs inside the existing transaction wrapper. It saves the two affected tables, rebuilds the parent then child tables, restores every row and recreates the lookup index. Foreign-key enforcement remains enabled. Failure rolls the table definitions and data back together. No data pruning, ranking change or curriculum interpretation is involved.

## Measured copy validation

A copy of the maintained database was 76,468,224 bytes before migration. Vacuum alone produced 71,794,688 bytes. The new layout plus vacuum produced **63,746,048 bytes**, a 16.6% reduction from the original file and 11.2% beyond vacuum alone. Size depends on future data; this is a measured checkpoint, not a universal compression ratio.

Before/after canonical exports matched exactly (SHA-256 `1f2df61563f4b3235c8404ef0e5111d65dda304762f87ef3d388c5ca20c4fc38`). All 615 revision rows and 207 source-snapshot rows were byte-for-byte unchanged. This checkpoint had no manual overrides; a separate synthetic case tests preservation of an active override. Foreign-key and integrity checks passed. Full clean-release tests remain part of publication verification.

106 focused storage, revision-history, family and core tests passed. New tests cover graph and export preservation, idempotence, Unicode/null values, primary/foreign/check constraints, child-link cascade behavior, migration failure rollback and compaction with history/overrides. Existing family checks cover inherited requirements independently of local row layout.

`uv run atlas compact` runs SQLite `VACUUM` to reclaim unused pages after migration/import churn; it does not remove current facts, revisions, candidates or source observations. Table rebuilding temporarily allocates new pages before old pages become reusable, so migration itself is not a promise of immediate file-size reduction. The maintained file is compacted and checked before the next publication commit. Existing Git history is preserved.


## Current canonical snapshots — migration 014

The published database had grown to 89,964,544 bytes as course-description audits expanded. Current canonical JSON duplicated approximately 31 MB of relationally stored facts. Migration 014 compresses that snapshot losslessly while keeping the existing program parent table, IDs, hashes, relational child tables, manual overrides and complete revision history. The migration verifies every original canonical hash before dropping the duplicate text column. A corrupt hash rolls back the whole migration. Ordinary relational reads need no SQLite extension; Python's standard-library zlib decodes current snapshots through `atlas.db.program_record`.

A copy of the exact 531073fe maintained database was migrated and compacted: **61,747,200 bytes**, down from 89,964,544. Its complete canonical public export was byte-identical, and ordered-row hashes for all 45 other nonmigration/nonprogram tables were unchanged. All 168 program snapshots decoded and matched original hashes. Integrity and foreign-key checks passed. This experiment did not overwrite the maintained publication database; that migration is applied at the next frozen integration.

The new regression tests preserve original UTF-8 canonical bytes, child rows, overrides and revision payloads; test repeated migration, hash-corruption rollback and fail-closed decode; and exercise existing family composition, overrides and source-review workflows. No source evidence or research history is deleted to save space.
