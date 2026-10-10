# AI Program Atlas — current plan and coverage

Updated 2026-10-10. This is a published, working research release, **not a completed survey of the full target cohort**.

## Current local release candidate — families and functional redesign

The maintained SQLite database has **110 program records across 193 institutions**, with **20 complete / 47 partial / 43 pending** requirement inventories. It exports 2,315 program-course records and 2,353 resolved requirement nodes. Metadata includes 154 descriptions, 204 prerequisite statements, 890 known credit amounts with units, five public course-site links and nine syllabus links; repeated observations across programs are included. The roster comprises 108 National Universities and 85 National Liberal Arts Colleges. Institution states: 53 confirmed, 123 inspected, 17 inaccessible, zero pending and zero absence conclusions. Both target cohorts remain incomplete.

The new Carolina-blue/navy, modern sans-serif interface is implemented with responsive filters and explicit program-family expansion. Family schema/resolution, atomic updates, revision history, evidence-backed exclusions/replacements and complete-audit hash checks are committed. The first real family covers Northeastern AI combined degrees with Philosophy, Business Administration and Biology: nine common requirement definitions stored once, 27 ID/provenance bindings, all original resolved requirements and concrete URLs preserved. Other combined degrees remain distinct until their inherited rules are reviewed.

Validation so far: 72 family-model tests, full nonbrowser suite, clean temporary reconstruction/build, SQLite integrity, a zero-change re-ingest, and successful reruns of all three family adapters with zero new candidates or source changes. Real-data browser verification and a clean committed-snapshot CI/Pages release are in progress. **This local candidate is not yet the verified published checkpoint below.**

Active research continues independently on Northeastern family expansion, Buffalo AI+X, WPI degree-wide requirements, Case Western/Northwestern/Rice degrees, and Clemson/FIU/Stevens/Minnesota minors. Program adapter notes identify exact outstanding lists and access limits. Counts in this section describe the maintained database at this checkpoint; newer commits may be awaiting ingestion.

## Project and publication

- Dedicated repository: https://github.com/KrisJordan/ai-program-atlas
- Static site: https://krisjordan.github.io/ai-program-atlas/
- Local workspace: `ai-program-atlas/` in the dedicated Codex task directory.
- Curriculum release passed GitHub Actions and Pages deployment: [run 38091092539](https://github.com/KrisJordan/ai-program-atlas/actions/runs/38091092539), commit `78f3973`. Public JSON independently verifies 106 programs / 188 institutions, including eight reviewed-complete requirement inventories. Newer research commits continue locally; the tables below describe this verified published checkpoint.
- Existing personal website and unrelated repositories were not modified. Work was implemented with independent Astra high research/implementation agents and coordinated schema ownership.

## Scope and cohort evidence

Official undergraduate titles containing AI or Artificial Intelligence qualify. Degrees, additional majors, minors, and formally named concentrations/tracks/emphases remain distinct. Ordinary electives, research centers, informal interest areas, graduate credentials and the surveyed certificates are excluded or documented as leads.

The confirmed target is **both** 2027 U.S. News categories, independently: every institution ranked 100 or better, including all cutoff ties. The 2027 edition was released September 22, 2026; older categories must not be silently reused.

| Cohort | Loaded membership | Evidence and remaining limit |
| --- | ---: | --- |
| National Universities | 108 | Secondary table enumeration through rank 100, including nine tied at 100; authoritative primary enumeration remains unverified |
| National Liberal Arts Colleges | 80 | Cited primary/secondary members; the full lower half and cutoff tie remain incomplete |

Every ranking row records category, edition, rank, source and verification status. Both cohort completeness flags remain false. Primary U.S. News category pages are access-restricted to the research tools; no restriction was bypassed. See `research/cohort.md`.

## Current inventory

| Measure | Count |
| --- | ---: |
| Loaded institutions with an attempted first pass | 188 |
| At least one qualifying title confirmed | 51 |
| Partially inspected without an exhaustive conclusion | 120 |
| Institution-level access limitation | 17 |
| Pending among the loaded roster | 0 |
| No-qualifying-program conclusions | 0 |
| Documented program identities | 106 |
| Degrees / minors / concentrations / additional majors | 56 / 33 / 15 / 2 |
| Complete / partial / pending requirement inventories | 8 / 11 / 87 |
| Program-course records / requirement nodes | 667 / 567 |

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

## Published curriculum boundaries

Eight scoped inventories are reviewed complete: CMU AI minor and additional major; Penn AI business and CS concentrations; Denison ML/AI minor; Iowa AI minor; Northwestern AI minor; and Emory AI minor. Each carries a cited review audit. Complete minor/concentration/additional-major coverage does not certify the host degree, and missing course metadata remain separate.

Eleven published curricula remain partial: CMU and Penn standalone degrees; Purdue BS and BA; Penn State minor; Columbia minor; Cornell minor; Georgia Tech Computing/AI minor; and three Northeastern combined degrees. Specific missing lists, linked college policies, ambiguous source rows, and degree-wide gaps appear in the adapter notes and audits. Furman's directory confirms an AI BS but the detail page is password-protected; its activity remains unknown and curriculum pending.

The published inventory has 45 course descriptions, 102 prerequisite statements, 292 known credit amounts with units, five course-site links and nine syllabus links, counted as program-course records (including repeats across related programs). Unknown fields remain null. The remaining 87 curricula are pending at this publication checkpoint. Announced offerings and quarter/semester/unknown calendars remain distinct.

## Verification checkpoint

- **260 tests passed** from a clean checkout of `78f3973`, including nine required Chromium tests, with no skips. Remote CI and deployment passed. Live mobile detail, comparison permalink/reload and JavaScript-error checks passed; public JSON matches the published counts above.
- All 11 initial program adapters succeeded with the production fetcher. Repeated observations added no duplicate candidates.
- The first 94-adapter full run exposed DOM layout mismatches; source-specific repairs fixed 46 of 47 original parse failures using cached permitted HTML. No source body was committed.
- Expanded replay has **102 successful latest adapter runs and four access-restricted failures** across all 106 registered programs. No unresolved parser failures remain. NJIT's BS award is corroborated in a second official source; William & Mary's title layouts have dedicated guarded parsers.
- Source failures and changed layouts preserved all reviewed data. The SQLite integrity check is clean.

## Remaining work and blockers

1. **Cohort completeness blocker:** obtain a permitted authoritative 2027 ranking roster that includes both full cutoff tie groups. Preserve the existing secondary verification labels until resolved; complete missing liberal arts membership and its first-pass research.
2. **CSRankings publication-data blocker:** public numeric import remains held pending permission or qualified reuse review. The site publishes original methodology, source links, explicit missingness, five AI fields, proposed 2016–2025 window, `us` filter and pinned snapshot. No dataset or copied implementation is included. See `research/csrankings.md`.
3. **University access limits:** retain blocked-source states and citations; do not bypass robots, 403s, paywalls or passwords. Four current program-adapter fetches are blocked at Gonzaga, UC Merced (two) and Michigan. Separate institutional survey limitations are documented in the ledger.
4. **Curriculum expansion:** 87 published records still await requirements, courses, credit rules and outcomes; 11 inventories remain partial. Newer local research batches are reducing this queue. This is remaining research work, not a completed deliverable. Preserve alternatives, nested rules and explicit review audits.
5. **Course detail expansion:** most prerequisites, descriptions, public course sites and example syllabi remain unverified. Keep nulls and explicit historical term labels; verify actual course identity before linking.
6. **Institution depth:** complete catalog, minor and concentration searches after first-pass directories. Resolve documented leads such as informal Rutgers guidance, UW's upcoming minor and abbreviations outside the exact title rule. Do not change partial inspection into absence without a documented bounded search.

Use `uv run atlas status`, `uv run atlas candidates`, the adapter notes and the task-specific skills for the next batch. Refreshes collect review candidates; they do not silently replace curated research.

## Active curriculum and cohort continuation

The next sourcing batches are underway (2026-10-10). Complete status now requires a cited, scoped review audit, persisted relationally; scrapers cannot issue this certification. Minor/concentration completeness covers that program's local requirements and policies, while host-degree requirements remain outside scope. Course metadata availability is reported separately.

The first eight complete inventories are published and verified above. Newer commits add Case Western, Northeastern, Santa Clara and Texas A&M minor reviews, more Northeastern degree mappings, and additional metadata. Official-source work continues at William & Mary, Duke, Virginia Tech, Michigan State, Tulane, RIT, Notre Dame, Miami and the two pilot degrees. Counts above remain the published snapshot until the next integration and verified deployment.

The newer committed cohort has 193 institutions, including 85 liberal-arts members. This includes two explicitly edition-inferred ranks and three officially verified top-100 memberships with unknown exact ranks. All additions have a documented first directory pass; this is not exhaustive catalog coverage. Further primary-source ranking upgrades and membership-only top-100 evidence are being checked. The database now supports an unknown exact rank with an evidenced upper bound, and the site explicitly labels it rather than inventing a rank. VMI's supplied page is HTTP 403; the Richmond supplied article also remains inaccessible to this research pass. Neither cohort is complete.
