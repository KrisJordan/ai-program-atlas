# UC San Diego COMM course-content contribution

Reviewed 2026-10-11. The assigned scope is exactly 45 existing identifiers from `/tmp/ucsd-comm-targets.json`, not the whole Communication chapter or degree. No seed, requirement, shared adapter, identity group or audit ledger is edited.

## Source and actual review

The already observed [official course index](https://catalog.ucsd.edu/front/courses.html) links Communication to the [COMM chapter](https://catalog.ucsd.edu/courses/COMM.html). The repository’s normal robots-aware Fetcher returned HTTP 200 at `2026-10-11T08:12:08+00:00`. The page identifies General Catalog **2026–27**. The ignored source is `/tmp/ucsd-comm.html`, with fetch provenance in `/tmp/ucsd-comm-source-index.json` and the standard ignored Fetcher cache. The committed manifest retains the URL, source hash, fetch time, edition, exact headings and normalized full-block hashes. No source body is committed.

All 41 exact matching course blocks were read in full, including their prerequisite, repeat, fieldwork and credit clauses. Four target identifiers have no exact current heading. Two current headings have substantive or unresolved title differences and are withheld from metadata output. This leaves **39 approved observations: 31 human-context, four applications, one mixed and three unclassified**. There are 35 reviewed single-category observations; “mixed” and “unclassified” are separate statuses.

## Individual dispositions

| Target | Disposition |
| --- | --- |
| COMM 140GS | No exact current heading; COMM 140 is not substituted for its GS suffix. |
| COMM 114M | No exact current heading; adjacent law courses do not establish its identity. |
| COMM 106E | No exact current heading; Data Science & Society is not classified from its title alone. |
| COMM 117GS | No exact current heading; no unsuffixed or differently titled substitution is made. |
| COMM 102C | Current title is *MMPP: Practicum in New Media and Community Life*; the pool lists *MMPP: Media and the Design of Social Learning*, with a historical note that HDP 115 crosslisting ended Summer 2015. Current content is recorded but held; the current chapter does not establish the rename or validate that historical cross-list note. |
| COMM 120P | Current title is *AMP: Digital Media in Education*; the pool lists *Digital Media Pedagogy*. The themes are related, but a title/version equivalence is not explicitly established, so current content is recorded but held. |

These are bounded current-source dispositions, not findings that courses are cancelled or absent university-wide. The held 102C and 120P descriptions each support mixed human-context/application candidates, but neither manual review is approved for integration into the older titled record without further identity evidence.

Other title variations are preserved in per-course notes: expanded subtitles (30), introduction wording (40), MMPP/MPL/AMP/CMS/CCP/CSI/LLC series labels, conjunctions and punctuation. COMM 102P’s listed “Television and Analysis and Production” and current “Television Analysis and Production” retain the same specific production subject; the different series wording is disclosed. No taxonomy comes from those series labels.

## Content decisions and material conditions

- COMM 101E teaches practical ethnographic field methods; COMM 102D applies field methods and curriculum development in supervised community laboratories. Both are applications based on the actual practice objectives, not their department or experiential-pool placement.
- COMM 102M and 102P center television production, project formats and cinematographic methods. Critical discussion and attention to content support that applied production focus.
- COMM 124A combines critical political analysis of designed objects with studio work designing a social intervention. Both human context and applications remain mixed candidates.
- COMM 146 and 190 leave their selected topic unspecified. COMM 194 supplies a seminar/research-paper format without its research topic. These three remain unclassified. A research assignment alone does not specify a subject.
- COMM 10’s possible media-making assignments support its introduction to communication history, representation and social interaction. COMM 114I’s group projects and 114D’s narrative production support social-movement/democracy inquiry; no programming or technical human-computer-interaction instruction is inferred. COMM 114J organizes its several perspectives around food justice and political strategy, without a coequal nutrition-science objective. COMM 40 explicitly takes a critical-cultural approach to promotional industries. COMM 50 and 120N teach public speaking and news writing/analysis respectively, communication skills within human context.
- The 39 approved headings contain **36 four-unit and three six-unit courses**. The six-unit courses are 102D, 102M and 102P. Current held 102C also prints six units and held 120P four. All units are quarter hours under the verified UCSD contract; no ranges occur in these matched headings.
- COMM 101E, 102D, 102M, 102P and held 102C may be taken for credit three times. COMM 146 separately permits three credit-bearing enrollments with an instructor-selected quarterly topic.
- COMM 102D explicitly prints no prerequisites and expects supervised participation at one of four San Diego County after-school labs. Held 102C also explicitly prints none. A missing prerequisite statement elsewhere remains null; it is not converted to “none.” Printed conjunctions such as `COMM 10 and COMM 101 or VIS 70N` are preserved without inventing precedence.
- Held COMM 120P requires three fieldwork hours per week. COMM 135 requires some off-campus screenings, especially film festivals. COMM 120N is designed for students doing news or public-information work, without a stated exclusive enrollment rule.
- COMM 190 limits seminars to thirty students, requires a substantial final research product, and excludes credit if taken after 190R. COMM 10 similarly excludes credit after 10R, and 100C after 100CR. These credit exclusions do not certify identity groups.
- COMM 194 explicitly states the same-course relationship with POLI 194, USP 194, HITO 193, SOCI 194 and COGS 194. It is a **four-unit seminar** attached to a separate **six-unit internship**, requiring UCDC participation. The six internship units are not added to course credits. Its unclassified decision agrees with the already reviewed POLI 194 source; group integration remains the primary owner’s responsibility.

## Guard and validation

`ucsd_comm_reviews.py` provides metadata-only `parse_observations(html)` and URL-keyed `SOURCE_PARSERS`. It verifies the Communication H1, catalog edition, every reviewed heading and the complete normalized body up to the next course/section heading. Additional paragraphs and unwrapped text are included in the body guard, even if they lack the usual description class. Duplicate codes, changed prerequisites/units/text, missing exact headings, a formerly absent identifier appearing, or changed held-source content requires new review. Password forms are rejected. Parser output contains only program identity, course observations and source dispositions; `category_review` stays in the manifest for manual integration.

**15 focused tests passed**, including actual cached-source replay of all 39 observations and six dispositions. Tests cover exact prerequisites, fixed units, missing suffixes, title holds, added/deleted/changed complete-block text, edition/heading changes, duplicate headings, access-page rejection, domain/mixed/unknown decisions and separate internship credits. No full suite or build was run; primary integration and release checks remain with the owner.
