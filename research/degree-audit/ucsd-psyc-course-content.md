# UC San Diego PSYC course-content contribution

Reviewed 2026-10-11. This contribution covers exactly **16 represented targets** in `/tmp/ucsd-psyc-targets.json`, and edits only its helper, manifest, tests and note. No seed, shared observer, requirement, identity or audit ledger is changed.

## Source and coverage

The observed [official course index](https://catalog.ucsd.edu/front/courses.html) links the [Psychology chapter](https://catalog.ucsd.edu/courses/PSYC.html). The normal robots-aware Fetcher returned HTTP 200 at `2026-10-11T08:50:40+00:00`; the chapter identifies **General Catalog 2026–27**. Raw source and provenance are private in `/tmp/ucsd-psyc.html`, `/tmp/ucsd-psyc-source-index.json` and the ignored Fetcher cache. The manifest preserves source hash, edition, headings and complete normalized body hashes; descriptions are original summaries.

All **15 exact matching target blocks** were read in full. **Fourteen metadata observations are approved: seven applications, five human-context and two unclassified.** Twelve have a reviewed single category. PSYC 139 has no exact current heading; no replacement or discontinuation is inferred. PSYC 162 is a substantive title/content hold: the pool lists **Environmental Policy**, but the current block is **Psychology and the Law**. Its current mixed candidate analysis remains manifest evidence only, not certification of the unresolved older title.

The section introductions and shared-heading inventory were checked. No additional chapter-wide lower/upper-division enrollment condition is stated there, and none of these targets is represented only by a shared range heading. This does not establish absence of institutional policies elsewhere.

## Actual-content boundaries

- **Applications:** PSYC 2 teaches biological/cognitive relationships; 141 evolutionary explanations of behavior; 168 childhood clinical disorders and assessment/treatment concepts. PSYC 116C explicitly applies clinical research design and laboratory methods; 117 conducts educational research/outreach; 115B designs, executes and analyzes cognitive experiments. PSYC 111B practices data collection, organization, statistical/graphical analysis and scientific reporting; these methods support empirical research rather than establishing a general mathematics course.
- **Human context:** PSYC 127 studies sexual-health inequities through identity and reflexive critique; 131 the history and implementation of scientific racism; 42/185 beliefs, justice, policy and societal action in the climate crisis. Genetics/intelligence keywords in 131 are not genetic-methods or AI instruction. PSYC 164 interprets crime and criminal-justice responses through social, cultural, developmental and personality perspectives, without a stated laboratory or investigative-procedure objective.
- **Unclassified:** PSYC 193L supplies only selected laboratory topics. PSYC 194A supplies a faculty-guided honors proposal/project format without a specific topic or substantive method. The department, laboratory label and research format do not fill those gaps.

## Units and restrictions

PSYC 111B prints **six quarter units**; the other thirteen approved headings print **four**. No range or sequence total is inferred. PSYC 2 and 42 have no prerequisite clause and remain null. The prior PSYC 2 pool record says None; chapter silence is recorded as source-specific unknown, not a new absence or waiver finding.

Important conditions are retained exactly:

- PSYC 127 and 131 are open only to major codes **PC25, PC26, PC28, PC29, PC30, PC31, PC32, PC33, PC34, PC35**. These are not generalized to every psychology major or AI students. PSYC 127 also requires upper-division standing and PSYC 60, 70 and 172; 131 requires upper-division standing.
- PSYC 117, 115B and 193L instead permit **PC26, PC28, PC29, PC30, PC31, PC32, PC33, PC34, CG32**. This different list is preserved without guessing expanded major names.
- PSYC 117’s literal prerequisite suffix is `upper-division standing, PSYC 60 or COGS 14B and PSYC 70 or COGS 14A. Instructor approval.` It may be taken for credit three times.
- PSYC 193L’s literal suffix is `upper-division standing, department approval, and PSYC 60 or COGS 14B or MATH 11 and PSYC 70 or COGS 14A.` It may be taken for credit twice as topics vary. Neither expression is silently rewritten with invented AND/OR precedence.
- PSYC 115B requires upper-division standing, PSYC 115A, instructor approval and department approval; it excludes credit alongside PSYC 115. The exclusion does not certify course identity.
- PSYC 116C is the third clinical-research sequence course and requires 116B. PSYC 111B requires 111A, upper-division standing and instructor/department approval.
- PSYC 111B and 194A state that they must be letter graded **for the Psychology Honors Program**. This purpose is retained rather than converted into a blanket rule for every course use.
- PSYC 194A requires PSYC 110, PSYC 111A-B, department approval, psychology-major status and Honors Program acceptance. Research planned for 194B-C is a subsequent sequence activity, not another already-completed prerequisite.
- Held PSYC 162 recommends PSYC 60 and requires upper-division standing in the current block. The recommendation is not promoted to a requirement, and neither condition is transferred to the unresolved Environmental Policy record.

## Guarded output and validation

`ucsd_psyc_reviews.py` provides metadata-only `parse_observations(html)` and URL-keyed `SOURCE_PARSERS`. It verifies the Psychology heading, edition, every reviewed exact course heading and complete body, including nested and unwrapped conditions. Changes to body text, units, prerequisites, major exclusions, duplicate headings, held identity evidence or a formerly missing exact code require renewed review. Password forms are rejected. Only program identity, course metadata and source dispositions are emitted; manual reviews stay in the manifest.

**14 focused tests passed**, including exact cached replay of all fourteen observations and two dispositions. Tests cover complete-body changes, source/edition guards, six-unit versus four-unit courses, distinct major lists, literal AND/OR wording, conditional letter grading, optional preparation and content boundaries. No full suite or build was run; primary integration and release checks remain with the owner.
