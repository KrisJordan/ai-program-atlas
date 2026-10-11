# Independent RIT immersion graph check

Reviewed 2026-10-11 by the cohort research agent, independently of the RIT primary integrator. The bounded subject is eight immersion branches in `rochester-institute-of-technology-artificial-intelligence-bs-degree`, principally the committed performing integration at `431bc00`, followed by the Theatre Arts prose correction at `568dc66`. This is not a full-degree second-pass certification or a new course-description audit.

## Evidence and method

I reread the ordinary public rendered overview, complete curriculum table, displayed 2026–2027 heading, and all route footnotes on these eight pages. No hidden endpoint or restricted source was used:

| Official page | Independently transcribed AI-specific option records | Source rule checked |
| --- | ---: | --- |
| [Music](https://www.rit.edu/study/music-immersion) | 18 | Three course-equivalent entries / nine hours; at least one 300-level course; six ensemble entries each require three one-credit semesters. |
| [Theatre Arts](https://www.rit.edu/study/theatre-arts-immersion) | 20 | Three course-equivalent entries / nine hours; at least one 300-level course; PRFL-220 taken three times; at most one of five dance entries. |
| [Psychology](https://www.rit.edu/study/psychology-immersion) | 19 | Three elective entries / nine hours; separate PSYC-101 or 101H preparation; regular/honors alternatives remain individual choices within their printed entries. |
| [Diversity, Inclusion, and Dialogue](https://www.rit.edu/study/diversity-inclusion-and-dialogue-immersion) | 13 | LEAD-203 and 303 required within this route, plus one elective entry from the direct entry or five printed paired alternatives. |
| [Quantum Information Science and Technology](https://www.rit.edu/study/quantum-information-science-and-technology-immersion) | 12 | One choice from each of quantum, mathematics, and ethics/technology menus; published three-hour allocation per menu and nine total; at least one 300-level course. |
| [Climate Change: An Interdisciplinary Problem](https://www.rit.edu/study/climate-change-interdisciplinary-problem-immersion) | 17 | One choice from each of three separate menus, with three-hour allocations and nine total. |
| [Environmental Studies](https://www.rit.edu/study/environmental-studies-immersion) | 18 | Choose three / nine hours with at least one 300-level course; two literal slash-label rows remain one entry each. |
| [Science, Technology, and Society](https://www.rit.edu/study/science-technology-and-society-immersion) | 17 | Choose three / nine hours with at least one 300-level course; same two literal slash-label rows remain one entry each. |

All eight overviews prohibit overlap with program requirements. I compared that source rule with the published AI-specific exclusions and nesting, rather than treating every source menu item as eligible degree credit. The manual exact code sets are committed in [the independent test](../../tests/test_rit_independent_immersion_check.py), not generated from the production route manifests or profile function.

The two displayed `STSO/WGST-225` and `STSO/WGST-342` links were independently opened on **both** Environmental Studies and STS. Their actual popup headings are `STSO-225` and `STSO-342`. This supports the local displayed-label-to-card associations only. It does not establish separate WGST aliases, add another course per row, or justify a cross-list identity group. I also independently opened the Theatre Arts table's PRFL-220 link and read its full card: one credit, Studio 1 contact hours, no explicit prerequisite field. The absence of that field does not establish unrestricted enrollment.

## Findings

**No structural course-role discrepancy was found in these eight branches.** Every branch sits beneath the immersion alternative. Consequently, even the two `all` courses in Diversity are conditional degree options, not fixed requirements for every AI student. Preparation is not promoted into the nine-hour Psychology elective selection. Overlapping route menus retain shared course IDs and are deduplicated.

The eight manual menus contain **134 route memberships but 118 distinct option codes**. In an isolated graph containing these branches and their actual immersion-alternative parent, the expected profile is zero fixed, 118 options, zero contextual. Adding the separately represented Psychology preparation gives two contextual records (PSYC-101 and 101H) in that isolated graph. In the full degree, the independently fixed PSYC-101 occurrence wins; this isolated check does not claim two new contextual courses or change the degree's aggregate totals. Option breadth is not student workload, and the published counts/credit allocations are not summed across alternative routes.

Specific conditions remain correctly represented:

- **Psychology:** the source closes the immersion to psychology majors and permits the broader PSYC-2xx/3xx criterion. The finite displayed menu is not a complete enumeration of that broader permission. The page's any-order statement does not cancel the separate introductory/200-level prerequisite conditions. No unsupported 300-level minimum is added. AI-fixed PSYC-223 is excluded from immersion use, while the source-listed regular/honors pairs stay alternatives rather than aliases.
- **Diversity:** the route is closed to community development and inclusive leadership majors. Its LEAD/HIST/SOCI paired choices remain ordinary alternatives, with no equivalence inference from related titles.
- **Quantum:** AI-fixed MATH-241 is preserved as a source-listed but excluded immersion choice. MATH-241H and the two MATH-367 variants remain distinct source identities. The three menus remain separate obligations within a selected route.
- **Climate:** the source excludes environmental science and environmental sustainability, health and safety majors. The three identically titled CHEM/ENVS/PUBL-531 entries are not merged from title alone. Published three-hour group allocations remain separate from actual course-card amounts; this review does not normalize four-credit observations down to three.
- **Music:** an ensemble entry is a three-semester, three-one-credit contribution. Its `choose_credits` node and explicit semester condition preserve this distinction. The primary course observations retain 0–1-credit ranges with null scalar amounts; zero-credit enrollment does not earn the three required hours. This bounded review verified the route footnote and stored observation treatment, not a fresh independent reread of all six ensemble cards.
- **Theatre:** PRFL-220 is a one-credit course requiring three enrollments for one three-credit contribution. The optional dance child limits the contribution to at most one of the listed five dance entries; nesting does not make dance mandatory.
- **Environmental Studies and STS:** the independently opened slash labels support exactly two actual STSO card identities in each menu, with no invented extra WGST requirements.

### Corrected wording finding

The original Theatre PRFL-220 bundle summary copied a sentence about music cards permitting 0–1 credits. That sentence was irrelevant and misleading for the independently inspected one-credit Theatre card. I reported it to the primary owner, who corrected the adapter/seed wording and added a regression in **`568dc66`**. The stored one-credit course fact, three-enrollment requirement, parent graph, and profile counts were already correct and did not change. The independent test now rejects recurrence of the copied music-range sentence on that Theatre node.

## Verification and limits

**25 focused tests passed:** the 14 new independent checks plus existing performing, psychology/leadership, science, and combined-label integration tests. The new tests transcribe actual menus, verify separate preparations and paired entries, validate global conditional ancestry, deduplicate route overlap, preserve exact selection counts, and distinguish variable music registration amounts from the fixed Theatre card. No primary seed, shared ledger, queue, database, schema, or UI was modified by this review. The primary coordinator owns full-build and publication verification.

All eight route pages and the five targeted popup interactions were accessible during this review; there was no access blocker in this bounded scope. Psychology's broader published elective criterion remains an open pool, not a failed fetch or an absence conclusion. Other immersion routes, every course's complete prerequisite chain, individual permission decisions, and full-degree/cohort policy closure remain outside this independent check. Route-level constraints in prose are preserved evidence; the profile is not a scheduling or student-eligibility solver.
