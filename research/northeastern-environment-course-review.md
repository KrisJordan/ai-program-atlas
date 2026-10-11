# Northeastern ENVR/EEMB primary description contribution — 2026-10-11

This bounded contribution reviews 51 previously unreviewed represented course identities: 41 ENVR and 10 EEMB. Selection excludes existing manual `category_review` entries and existing shared classification decisions. Cohort assigned this disjoint subset; existing Biology EEMB reviews were not repeated. The companion manifest names 69 exact existing program-course targets: Ecology/Evolutionary Biology 21, Environmental/Sustainability Sciences 39, Environmental Engineering 6, and International Affairs 3. Those are metadata scopes, not independently re-established curriculum roles.

## Actual evidence

All 51 complete official course blocks were read, including descriptions, credit labels, prerequisite and corequisite expressions, and embedded restrictions. Both sources display Academic Catalog 2026–2027:

- [Earth and Environmental Sciences](https://catalog.northeastern.edu/course-descriptions/envr/), normal permitted fetch retained at `.cache/research/degree-audit-northeastern/envr.html`, fetched 2026-10-11 00:07:04 UTC. SHA256 `fbfedd44983555766299154d2b2c230678cce7f48515843cadd22d6088cbeb4a` matches the source index and file.
- [Ecology, Evolution, and Marine Biology](https://catalog.northeastern.edu/course-descriptions/eemb/), cached `eemb.html`, fetched 2026-10-11 00:07:07 UTC. SHA256 `43855e1e1485734e6bd3e42df09a0d942ed39d2292616fa4f070b2e54a730e3e` matches the index and file.

Raw catalog material stays ignored. This is an actual reading of the complete selected blocks from the documented current source captures, not an inference from successful fetches or titles. Existing original summaries in `northeastern_course_metadata.py` were checked against these descriptions and retained where supported. The separate contribution manifest records full-block fingerprints, exact observed titles/credits/prerequisites/corequisites, source guards, explicit target IDs and individual manual classification rationales.

## Subject decisions

Forty identities are applications because they develop substantive ecology, genomics, geology, climate, hydrology, botanical, environmental-management or geospatial practice. The rationale for each course identifies its domain. R programming, mathematical tools, software packages and laboratory work do not automatically turn domain courses into programming foundations, AI, or computing systems. General GIS use in ENVR 3300/5260 is geospatial practice rather than a database/infrastructure course.

Two are mathematics: EEMB 5130 foregrounds model derivation, dynamical analysis, stability, estimation and computational mathematical tools; ENVR 5500 centers on statistical foundations and inference, with machine learning among its topics. This is consistent with the earlier treatment of a mathematically focused population/network course, rather than classification by department.

ENVR 2515 and 5000 are human_context: their descriptions center on sustainable development/social inclusion and public participation/stakeholder deliberation respectively. ENVR 1400/1401 and 5450 are mixed human_context/applications because they explicitly integrate human and environmental research. ENVR 5563 is mixed mathematics/systems/applications: the source combines spatial mathematical models, statistics, information/database theory and geographic representation without establishing a dominant category. None is assigned fractional category counts.

ENVR 4970, 4971 and 4997 remain other/unclassified. Generic honors research, products or supervised theses do not reveal the actual topic. Thus the 51 identities are **40 applications, 2 mathematics, 2 human_context, 4 mixed other and 3 unclassified other**. This is not a whole-degree fixed/options profile; primary owns role and family integration.

## Eligibility and load distinctions

There are 42 four-hour and nine one-hour course observations in the semester catalog. Their distinct identities and source credits are preserved; no overlapping degree requirement totals are added. The 16 explicit reciprocal corequisite statements across eight lecture/lab pairs remain concurrent eligibility evidence. The helper emits notes, never new `all` requirement nodes. For generic laboratory descriptions it also validates the separately read accompanying lecture's full block before supplying the subject summary/category.

ENVR 1201 lists ENVR 1200 as a prerequisite that may be taken concurrently, not a reciprocal corequisite requiring every lecture student to take the lab. Its prose specifically requires the lab for environmental geology/geology majors; that scope is not generalized to every AI combined degree. ENVR 3125 requires a laboratory science course or instructor permission in its prose, despite lacking a labeled prerequisite field; this is preserved in the observed prerequisite summary. ENVR 3300 explicitly allows students lacking prerequisites to seek instructor permission, without guaranteeing approval.

EEMB 5130 preserves concurrent calculus, writing grade thresholds and the graduate-admission alternative exactly. Other graduate-admission alternatives remain alternatives, not evidence that undergraduates are forbidden. ENVR 5563's published prerequisite repeats ENVR 5260 with the same grade threshold; the original expression is retained without inventing two obligations. ENVR 4970/4971 permit unlimited repeats, but that does not create extra fixed identities or alter degree load. The 4970 description's eight-credit honors sequence includes a second course or college-defined equivalent; no arbitrary equivalent pool is invented. ENVR 5260's two lecture and one lab periods per week are contact-pattern evidence, not a credit conversion.

Twenty-seven blocks have no labeled prerequisite field; one of those, ENVR 3125, has the explicit prose condition above. The remaining missing fields stay unknown, never unrestricted registration. The manifest preserves every observed Boolean expression and minimum grade without normalizing equivalent-looking codes.

## Deliverables and verification

- `atlas/adapters/northeastern_environment_course_reviews.json`: source provenance, 51 individually read dispositions, exact facts and 69 target mappings.
- `northeastern_environment_course_reviews.py`: standalone `parse_subject(html, program_id=..., subject=..., codes=...)` for primary integration. It requires the exact heading/version, target scope, all selected full-block fingerprints and relevant lecture evidence. Runtime candidates contain observed metadata and source notes, not `category_review` or full-degree audit claims.
- `tests/test_northeastern_environment_course_reviews.py`: four passing tests cover synthetic changed/missing/duplicate blocks, credits/prerequisites/corequisites, source version and target scope, lecture-dependent labs, exact manual dispositions, and all 69 observations from the optional actual caches. Repeated parsing returns identical output.

The primary owner must integrate manual reviews and register source parsers without replacing unrelated same-subject selections. Shared seeds, family definitions, metadata helper, category file, audit ledger, DB and PLAN were not edited. This contribution does not close degree-wide policies, conditional home-college applicability, role/family checks or independently certify any degree. No selected source block was absent or blocked; remaining work is integration and the primary audits, not an access barrier.

An isolated read-only backup of the maintained publication database also built successfully to `/tmp/ne-environment-build-site` with `/ai-program-atlas/` base path (168 programs, 194 institutions). This is a build compatibility check of the existing publication snapshot, not a claim that the new contribution has already been integrated or visually verified.
