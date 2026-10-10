# Verification checkpoint — 2026-10-10

## Automated checks

Final local command: `ATLAS_REQUIRE_BROWSER=1 uv run pytest -q` — **200 passed**, none skipped (193 unit/integration, seven Chromium browser tests). The suite covers real extraction fixtures, award/title scope, all-of/choose-N/credit/nested requirement validation, database constraints and rollback, overrides, repeat ingestion, source failures/changes, cache/retry/robots/redirect boundaries, deterministic reconstruction and public rendering.

Browser tests cover filters (including type/evidence), empty states, direct program pages, four-program comparison URLs, reload/back/forward, Pages base paths, no-JavaScript baseline, real database reconstruction, mobile width, and outcome-theme missingness. Desktop/mobile screenshots were inspected during implementation. Public styles/scripts are local assets; there is no runtime server or tracker.

A committed archive was extracted to a fresh temporary checkout, installed through uv, ingested into a fresh SQLite file, integrity-checked and built successfully. The integration suite also builds two independent databases and verifies byte-identical static outputs. GitHub Actions independently performs a clean reconstruction and requires real Chromium.

## Live refresh evidence

All 106 registered program adapters were exercised through the production respectful fetcher. Latest outcomes: **102 success, four access-restricted failure, zero unresolved parse failure**. Repeated identical pilot observations produced no duplicate candidates. Earlier failures are retained in the database run history rather than removed from the audit trail.

The four unattended fetch limitations are:

- Gonzaga AI in Engineering and Applied Science minor: robots endpoint returned 403; page not fetched.
- UC Merced AI BS: robots endpoint returned 403; page not fetched.
- UC Merced CS&E AI emphasis: robots endpoint returned 403; page not fetched.
- Michigan Human-Centered AI minor: source returned 403; no bypass attempted.

These records retain their cited manual research evidence. They do not acquire a new verification claim from a failed refresh. Institutional survey access states and program-refresh states are separate; 17 institutional first-pass access limitations remain documented.

The full run uncovered compressed-response handling and legitimate Courseleaf/hero/directory layout differences. Regression tests and source-specific selectors resolved these while retaining rejection of navigation-only titles, login pages, missing award evidence and unrelated sections. NJIT BS evidence is explicitly corroborated by its official school page. See `parser-refresh.md` and each adapter's NOTES.

## Data integrity and publication boundaries

SQLite integrity check: `ok`; foreign-key violations: zero. Public snapshot: 106 program identities at 51 confirmed institutions within a 174-member loaded roster; 286 program-course records and 86 requirement nodes. Nine curricula are partial and 97 pending. All loaded institutions have a documented attempted first pass, but the full intended ranking cohort is incomplete.

The committed database contains curated facts, original summaries, links, revisions and observation metadata. Raw cached HTML/PDF, credentials and private user context are excluded. No CSRankings numeric dataset or source implementation is redistributed. Program identities and comparisons do not imply admissions, graduation or teaching-quality guarantees.

The expanded research commit `d0733e1` passed [GitHub Actions build and deployment](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38089992250). The public site returned HTTP 200; its independently fetched data.json confirmed 106 programs, 174 loaded institutions, nine partial curricula, 97 pending curricula and cohort_complete=false. Local and remote commit hashes matched. A fresh checkout of this research commit also passed all 200 tests. The only subsequent changes record these verification results in documentation.
