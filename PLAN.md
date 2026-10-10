# AI Program Atlas — current plan and coverage

Updated 2026-10-10. This is a published, working research release, **not a completed survey of the full target cohort**.

## Project and publication

- Dedicated repository: https://github.com/KrisJordan/ai-program-atlas
- Static site: https://krisjordan.github.io/ai-program-atlas/
- Local workspace: `ai-program-atlas/` in the dedicated Codex task directory.
- Expanded GitHub Actions build and Pages deployment succeeded: [run 38089992250](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38089992250), research commit `d0733e1`. The public JSON was independently fetched and verified at 106 programs / 174 institutions.
- Existing personal website and unrelated repositories were not modified. Work was implemented with independent Astra high research/implementation agents and coordinated schema ownership.

## Scope and cohort evidence

Official undergraduate titles containing AI or Artificial Intelligence qualify. Degrees, additional majors, minors, and formally named concentrations/tracks/emphases remain distinct. Ordinary electives, research centers, informal interest areas, graduate credentials and the surveyed certificates are excluded or documented as leads.

The confirmed target is **both** 2027 U.S. News categories, independently: every institution ranked 100 or better, including all cutoff ties. The 2027 edition was released September 22, 2026; older categories must not be silently reused.

| Cohort | Loaded membership | Evidence and remaining limit |
| --- | ---: | --- |
| National Universities | 108 | Secondary table enumeration through rank 100, including nine tied at 100; authoritative primary enumeration remains unverified |
| National Liberal Arts Colleges | 66 | Cited primary/secondary members; the full lower half and cutoff tie remain incomplete |

Every ranking row records category, edition, rank, source and verification status. Both cohort completeness flags remain false. Primary U.S. News category pages are access-restricted to the research tools; no restriction was bypassed. See `research/cohort.md`.

## Current inventory

| Measure | Count |
| --- | ---: |
| Loaded institutions with an attempted first pass | 174 |
| At least one qualifying title confirmed | 51 |
| Partially inspected without an exhaustive conclusion | 106 |
| Institution-level access limitation | 17 |
| Pending among the loaded roster | 0 |
| No-qualifying-program conclusions | 0 |
| Documented program identities | 106 |
| Degrees / minors / concentrations / additional majors | 56 / 33 / 15 / 2 |
| Partial curriculum records / curriculum pending | 9 / 97 |
| Program-course records / requirement nodes | 286 / 86 |

Course records overlap across related programs and include elective pools. These counts are not unique institution-wide courses, required-course totals, degree completion percentages or quality scores. First-pass inspection does not mean full catalog/concentration coverage. The unknown missing liberal arts membership is outside the loaded denominator, so zero pending does **not** mean the target cohort is complete.

## Delivered

- [x] Document architecture, relational schema, data exchange, research/refresh skills and agent ownership.
- [x] Create isolated uv project with locked dependencies and incremental commits.
- [x] Implement versioned SQLite migrations, foreign keys, requirement-tree checks, evidence, revisions, source hashes, run history, candidate review and evidence-backed manual overrides.
- [x] Implement bounded robots-aware HTTP, per-host pacing, cache, redirect validation, compression handling, Retry-After deferral and failure preservation.
- [x] Research varied CMU, Penn, Purdue, Penn State, Denison and Furman pilots, including BA, BS/BSE, minors, concentrations and additional majors.
- [x] Expand to 106 official-source program identities and registered program-specific adapters, with Markdown notes beside every adapter.
- [x] Attempt a first official-source pass for every loaded institution, without inferring absence from partial searches.
- [x] Build editorial static index, eight search/filter controls, detail pages, coverage ledger and methodology.
- [x] Implement four-program comparison URLs with reload/back/forward and Pages base paths, separate rank-category provenance, exact credit units, course-category profiles and source-linked inferred outcome themes.
- [x] Verify public resources for three pilot courses and two example syllabi; retain term/historical labels and link rather than redistribute.
- [x] Test extraction, nested choices, constraints, rollback, idempotence, manual overrides, source changes/failures, deterministic reconstruction and browser behavior.
- [x] Build a committed snapshot from a clean temporary checkout and verify the initial remote CI and Pages URL (HTTP 200).
- [x] Verify the expanded snapshot in remote CI and GitHub Pages; public JSON confirms current counts and explicit cohort incompleteness.

## Detailed pilot boundaries

CMU and Penn contribute 231 program-course records across six credentials, with nested choices and explicit partial coverage. CMU uses the 2026–27 catalog; Penn department pages do not state a catalog edition. Documented launch evidence covers CMU BS Fall 2018, Penn BSE Fall 2024 for existing students (external applicants Fall 2025), and Wharton concentration Fall 2025. Other unverified dates remain null.

Purdue BS contributes 42 courses and 17 requirement nodes; college/general-education logic remains incomplete. The Purdue catalog returns 403, so the separate BA has verified identity and pending curriculum. Penn State's 2026–27 AI Engineering minor has five course records and six nodes; its approved elective list is not expanded. Denison's eight required courses and semester credits are documented; detailed completion policies remain partial. Furman's official directory lists an AI BS, but its detail page is password-protected, so activity is unknown and curriculum pending.

All remaining records are title-level discoveries with current activity, catalog year, launch date, requirements and courses unknown unless separately evidenced. Announced offerings are distinguished, including UMD and Minnesota. Drexel's quarter system is explicitly sourced. See each adapter's `NOTES.md` and the survey reports for interpretations and next checks.

## Verification checkpoint

- **200 tests passed**, comprising 193 unit/integration checks and seven required Chromium browser checks. The same 200 passed from a fresh checkout of the final research commit. No browser tests skipped; remote CI and deployment also passed.
- All 11 initial program adapters succeeded with the production fetcher. Repeated observations added no duplicate candidates.
- The first 94-adapter full run exposed DOM layout mismatches; source-specific repairs fixed 46 of 47 original parse failures using cached permitted HTML. No source body was committed.
- Expanded replay has **102 successful latest adapter runs and four access-restricted failures** across all 106 registered programs. No unresolved parser failures remain. NJIT's BS award is corroborated in a second official source; William & Mary's title layouts have dedicated guarded parsers.
- Source failures and changed layouts preserved all reviewed data. The SQLite integrity check is clean.

## Remaining work and blockers

1. **Cohort completeness blocker:** obtain a permitted authoritative 2027 ranking roster that includes both full cutoff tie groups. Preserve the existing secondary verification labels until resolved; complete missing liberal arts membership and its first-pass research.
2. **CSRankings publication-data blocker:** public numeric import remains held pending permission or qualified reuse review. The site publishes original methodology, source links, explicit missingness, five AI fields, proposed 2016–2025 window, `us` filter and pinned snapshot. No dataset or copied implementation is included. See `research/csrankings.md`.
3. **University access limits:** retain blocked-source states and citations; do not bypass robots, 403s, paywalls or passwords. Four current program-adapter fetches are blocked at Gonzaga, UC Merced (two) and Michigan. Separate institutional survey limitations are documented in the ledger.
4. **Curriculum expansion:** 97 programs still need requirements, courses, credit rules and outcomes extracted; all nine richer pilot curricula still have documented gaps. This is remaining research work, not a completed deliverable. Expand in evidence-reviewed batches, preserving alternatives and nested rules.
5. **Course detail expansion:** most prerequisites, descriptions, public course sites and example syllabi remain unverified. Keep nulls and explicit historical term labels; verify actual course identity before linking.
6. **Institution depth:** complete catalog, minor and concentration searches after first-pass directories. Resolve documented leads such as informal Rutgers guidance, UW's upcoming minor and abbreviations outside the exact title rule. Do not change partial inspection into absence without a documented bounded search.

Use `uv run atlas status`, `uv run atlas candidates`, the adapter notes and the task-specific skills for the next batch. Refreshes collect review candidates; they do not silently replace curated research.
