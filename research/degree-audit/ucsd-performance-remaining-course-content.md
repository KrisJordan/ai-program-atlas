# UCSD remaining performance and visual-arts content

Reviewed 2026-10-11. This contribution owns exactly the 103 stable identifiers delegated in the code-only performance queue: 27 VIS, 23 MUS and 53 theatre/dance records. The earlier `unclassified` reviews on these records explicitly assessed missing evidence, not course content. This contribution does not certify requirement membership, change any degree graph, or silently reinterpret college eligibility lists as enrollment permission.

## Actual evidence and finite outcome

I read every available assigned course's complete description and adjoining eligibility, repeat, unit and preparation text in the existing permitted public captures. I also read each chapter's heading, 2026–27 disclaimer and section introductions. No new network requests were needed.

| Official source | Existing permitted capture | Assigned identifiers | Content observed |
| --- | --- | ---: | ---: |
| [Music](https://catalog.ucsd.edu/courses/MUS.html) | `/tmp/ucsd-mus.html`, 2026-10-11 08:41:05 UTC | 23 | 22 |
| [Visual Arts](https://catalog.ucsd.edu/courses/VIS.html) | `/tmp/ucsd-vis.html`, 2026-10-11 07:18:03 UTC | 27 | 27 |
| [Theatre and Dance](https://catalog.ucsd.edu/courses/THEA.html) | `/tmp/ucsd-theatre.html`, 2026-10-11 09:18:58 UTC | 53 | 53 |

The manifest retains exact URLs, existing registered source IDs, edition, capture timestamps, full capture hashes, individual full-block hashes, section membership and a hash of chapter/section introductions. The theatre subject scope explicitly includes TDDM, TDHD, TDPW and TDTR as well as the prefixes handled by the earlier contribution; none inherits a category from its prefix.

**102 identifiers have content observations.** MUS 10 has no exact heading in the reviewed current Music chapter; its observation remains code-only with no new content review, title, amount or description. No neighboring MUS 101 course or similar title is substituted. This is a precise current-chapter mismatch, not evidence of discontinuation or university-wide absence. A department/current exact-course statement is needed to resolve it. There are no still-unread available target blocks in this assigned set.

MUS 2A, 2B and 2C are explicitly printed together under a single `MUS 2A-B-C` heading with `4-4-4` units and a shared description. All three sequence members are separately retained with four units each. The shared heading does not collapse their identities, assign twelve credits to each member, or justify imaginary quarter-specific descriptions. The parser recognizes only this specifically reviewed shared heading, rather than expanding arbitrary ranges.

## Individual subject judgments

The manual manifest contains an original concise summary and content-specific rationale for every observed identifier. The 102 observations comprise **52 human-context, 38 applications, 11 mixed and one source-inspected unclassified** review. Mixed and unclassified records retain `category: other`.

- MUS 1A/B/C and 2A/B/C build concrete musical literacy, aural and performance skills, so they are applications. MUS 6 and 7 study electronic works and relationships among music, science and technology; references to computers do not establish implementation instruction. MUS 20 concerns biological/cognitive mechanisms of musical perception, with cultural variation informing that scientific inquiry; it is applications, not AI merely because cognition appears.
- VIS 9 and 60 teach photographic technique, while VIS 83 studies photographic history and cultural change. VIS 41 teaches design-tool craft, not general programming. VIS 32 explicitly studies neuroscience of art. VIS 10 and 159 contextualize computer art critically/historically; neither description establishes algorithmic training.
- VIS 2, 8, 30, 70N and 80 explicitly combine artistic production with substantial theoretical, historical or cultural inquiry and remain mixed. Merely discussing historical context in a predominantly practical class does not automatically make it mixed.
- Acting and movement courses with concrete studio objectives are applications. TDGE 11, 124 and 125 interpret existing films/performances; TDGE 126 analyzes animation's form and storytelling rather than teaching animation production. TDTR 120 analyzes dance films and production history; the source does not explicitly require students to produce films. These are human-context.
- TDDE 1, TDDM 5, TDHT 119 and TDMV 43/148/149 explicitly combine cultural, historical or textual investigation with applied creation/performance; they remain mixed. TDGE 25 and TDPW 1 teach oral communication and creative dramatic writing, respectively, and are human-context rather than being assigned from theatre department membership.
- MUS 80 has unspecified changing summer topics. Its actual description was inspected, but the current topic is not identified, so it remains unclassified. This is a content limitation, not unfinished reading.

### Jazz cross-record discrepancy reported

MUS 127 introduces jazz performers and their styles, then examines production/reception and race, class, gender and sexuality. It does not explicitly teach performance. I classified it human-context and flagged the existing mixed ETHN 179 review to the primary owner. The owner independently reread both full blocks, agreed that techniques are objects of cultural study rather than studio instruction, and accepted a separate correction to ETHN 179. This contribution does not modify that earlier manifest or assert identity. The two records retain their source-specific prerequisites and credit conditions pending complete reciprocal identity review.

The source also explicitly names COGS 20 with MUS 20 and ETHN 178 with MUS 126. These statements are preserved in notes, not converted automatically into identity groups. The primary owner retains responsibility for reciprocal/version checks and any graph-level identity integration.

## Credits and eligibility

There are 101 explicit four-unit observations. MUS 80 prints a 1–4 range, retained as a null scalar amount with the range in notes. Units use the established UCSD quarter-hour normalization; no course amount is derived from a college or route total.

One hundred observed records have explicit prerequisite fields, including fields that explicitly say none. TDDE 1 and TDDR 101 have no such field; their exact prerequisites remain null. TDDR 101's recommended earlier theatre courses remain recommendations, including the literal historical TH prefixes. No general claim of unrestricted enrollment follows from missing text.

Material restrictions were retained individually:

- MUS 2A/B/C require an examination score or instructor consent and must be taken in sequence. Concurrent MUS 2AK/BK/CK is specifically required for music majors; no corresponding obligation is added to every AI student.
- VIS 23 says no prerequisite and then restricts enrollment to art-history majors, with a completion deadline after declaration/transfer. The entire field and the scoped rule are preserved. VIS 60 is open to visual-arts majors/minors; VIS 70N specifies visual/cinematic-arts majors/minors. Inclusion in an AI student's general-education pool does not waive these limitations.
- VIS 80 requires residence at UC San Diego and is required for studio majors/minors, including transfers. The contribution records that institutional scope without making it universally fixed for the AI degree.
- TDHT 119 requires an interview. TDGE 12 limits duplicate credit for the same topic previously taken in TDGE 11, which is not an alias equivalence. Repeat allowances, fees and selected-year or once-yearly offerings remain notes, not promises of availability.
- TDMV 148 and 149 literally reference TDMV 138. They are not silently rewritten to the separately listed TDMV 38. Consent alternatives are preserved where published; permission is not presumed granted.
- VIS 10/ICAM 110, VIS 21A or 21B/VIS 21, VIS 22/22R and VIS 83/83R credit exclusions are retained without inferring identical courses, renumbering or delivery mode from suffixes.

## Rerunnable contribution and validation

Files:

- `atlas/adapters/ucsd_performance_remaining_reviews.py`
- `atlas/adapters/ucsd_performance_remaining_reviews.json`
- `tests/test_ucsd_performance_remaining_reviews.py`

`parse_observations(html, subject='MUS'|'VIS'|'THEA')` returns metadata observations and missing-source dispositions only. It guards the exact chapter, catalog year, section context, headings and complete bodies. Changed content, credits, permission clauses, section membership or context require renewed review. `SOURCE_PARSERS` exposes the three official URLs for primary composition. Manual `category_review` records stay in the manifest and are never emitted as fresh independent reviews by the parser.

**55 focused tests passed**, including 19 new tests and all three earlier subject review suites. All 102 actual cached content observations replay successfully. Synthetic checks cover changed prerequisites/content/credits, wrong source/year, new context restrictions, nested/unwrapped text, access pages, exact shared sequence handling and the appearance of a previously missing identifier. Primary integration, seed/ledger updates and a full build remain with the western owner; this contribution made none of those mutations.
