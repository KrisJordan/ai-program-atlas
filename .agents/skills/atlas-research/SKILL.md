---
name: atlas-research
description: Research or expand AI Program Atlas institution/program records using official evidence, without confusing partial searches with absence.
---

Read `docs/CONTRACT.md`, the relevant adapter's `NOTES.md`, and `research/cohort.md`. Use the existing canonical institution ID. Both 2027 ranking categories are separate; each row needs edition/category/rank/citation. Membership in a secondary table does not certify the full cohort.

Confirm the official undergraduate title contains AI or Artificial Intelligence. Keep degrees, additional majors, minors and concentrations distinct. For programs found only in a directory, record identity evidence and leave curriculum pending. Only classify no qualifying program found after a documented current catalog and program-directory search; otherwise use inspected, inaccessible or pending.

Research required core, alternatives and elective rules as a tree. A listed option is not necessarily required. Keep credit units and source wording; do not infer prerequisite, launch date, title, outcome or degree total. Source-stated outcomes and analyst taxonomy are separate. Null means not verified. Retain evidence URLs/locators/catalog year and original summaries, not full catalog copies.

Write reviewed JSON in `data/programs/`, a source-specific parser in `atlas/adapters/` with `PROGRAM_ID`, `SOURCES` and `parse(html)`, and adjacent `NOTES.md` explaining scope, interpretations and next checks. Parsers return observed subsets without replayed verification timestamps. Use synthetic extraction fixtures and validate against permitted live sources; keep raw HTML/PDF in ignored cache or temporary directories.

Run targeted tests, `uv run atlas ingest`, `uv run atlas check`, and `uv run atlas build`. Update exact coverage and remaining work in PLAN.md. The owner confirmed permission on 2026-10-11 to use CSRankings data for this educational project. Follow research/csrankings.md: preserve attribution/notices and the exact snapshot, publish only the authorized project integration, and do not imply broader rights or copy upstream implementation. Raw downloads stay ignored; reproducible derived outputs require independent methodology validation.

For AI + discipline families, follow `docs/PROGRAM_FAMILIES.md`: establish membership and relationship with cited evidence, compare each concrete variant's catalog before sharing a rule, and retain discipline-specific choices and integration requirements locally. Family bindings preserve IDs and local provenance. A title match never certifies inheritance. Coordinate shared edits across variant owners and refresh any complete audit's family hash explicitly.

For course subject classification, read the Course taxonomy v1 section in docs/DEGREE_AUDIT.md. AI literacy/tool use belongs in Applications when it is the primary aim; AI/ML needs actual technical-method evidence, and ethics-primary courses belong in Human Context. Record version-specific evidence and rationale; titles alone and keyword triage never certify classification. Preserve manual reviews across scrape observations and queue changed content for review.
