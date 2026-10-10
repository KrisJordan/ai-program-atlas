# National Liberal Arts Colleges: preliminary official-source survey

Checked 2026-10-10. This report covers the **80 verified cohort rows currently available in `data/cohort.json`**, not the full intended rank-at-most-100 population. Ranking membership remains incomplete; these counts are not a complete-population denominator.

## Findings

Two qualifying official undergraduate titles were found:

| Institution | Official title | Award | Evidence and limits |
|---|---|---|---|
| Denison University | Machine Learning and Artificial Intelligence | Minor | [Official requirements](https://denison.edu/academics/machine-learning-and-artificial-intelligence/degree-requirements) and [2026–2027 courses](https://denison.edu/academics/machine-learning-and-artificial-intelligence/courses) read. Eight required courses; five ML course credits documented. All eight individual course credits and semester units are now verified; institutional minor policies and several prerequisite expressions remain incomplete. First-offered date unknown. |
| Furman University | Artificial Intelligence | BS major | [Public official directory](https://www.furman.edu/academics/majors-minors-programs/) explicitly lists the title, BS award and undergraduate level. The linked [detail page](https://www.furman.edu/academics/majors-minors-programs/artificial-intelligence-major/) is password protected. Availability, launch date and curriculum unknown; overall record is partial. |

The directory listing is sufficient to confirm Furman's title, but is **not** evidence that students can presently enroll. Its program activity status is deliberately `unknown`.

## Coverage states

`data/surveys/liberal.json` records one row per currently verified LAC cohort institution, each with the attempted official URL, date and scope note:

- 2 `confirmed`: official qualifying title read.
- 73 `inspected`: an official academic overview or directory was opened for preliminary reconnaissance. These are **unfinished** catalog reviews, not no-program determinations.
- 5 `inaccessible`: robot verification (Swarthmore), HTTP 403 (Naval and Military academies), inaccessible consent redirect (Richmond), or zero readable academic-page content (Colby).
- 0 `pending`: the six initially unresolved paths were located through official homepages. Connecticut’s dynamic major-search page exposes no readable listing, so its inspection remains especially limited.
- 0 `no_qualifying_program_found`: no institution has been given an absence conclusion from keyword searches or incomplete department review.

General academics pages are explicitly only preliminary evidence. Degree/minor listings often omit internal concentrations, so a complete title survey needs relevant current catalogs and department requirements. Keyword discovery helped locate Denison but did not create any absence conclusions.

## Exclusions and false positives

- [Harvey Mudd AI Innovation](https://www.hmc.edu/ai/) describes research, labs and courses. Its [formal emphasis list](https://www.hmc.edu/academics/emphases/) lists Data Science and Environmental Analysis. No AI award is inferred from the initiative name; further catalog review remains pending.
- [Rollins Professional Advancement](https://www.rollins.edu/professional-advancement/degree-programs/) lists a Data Analytics with Artificial Intelligence **Certificate**. Certificates fall outside this project's degree/minor/concentration kinds. Other Rollins programs still need catalog review.
- Bucknell's official CS material mentions AI courses and topics. Courses and research interests do not establish a qualifying named concentration.
- Search results about another institution, graduate-only study, general AI policies, and AI research were not promoted to program records.

## Deliverables and remaining work

Reviewed program records are in `data/programs/denison-mlai-minor.json` and `data/programs/furman-ai-bs.json`. Each has an independent adapter under `atlas/adapters/` that reads the supplied HTML and rejects missing identity or required structural evidence. Neither replays a seed nor assigns a fresh verification timestamp. Adapter tests check changed observed courses, a missing degree type, and password-page rejection.

Remaining work: complete ranking membership; revisit the five access failures without bypassing restrictions; conduct full current-catalog and concentration-level review of the 73 preliminary rows; obtain public Furman curriculum and availability evidence; complete Denison institutional minor policies, prerequisite expressions and launch provenance. No raw fetched catalog pages are committed.

## Follow-up verification

All six originally pending paths were resolved via official homepage navigation on 2026-10-10. [Franklin & Marshall](https://www.fandm.edu/fields-of-study/) lists Artificial Intelligence and the Liberal Arts as a certificate. [Saint Anselm](https://www.anselm.edu/academics/majors-minors/applied-artificial-intelligence) explicitly offers Applied Artificial Intelligence as a certificate. Both are documented exclusions. No additional qualifying degree, minor or concentration was confirmed.

Denison’s [academic credit policy](https://catalog.denison.edu/catalog/academic-program/academic-credit-policy/) verifies semester-based credits. Its current catalog supplied the three missing cognate course credits, each four, and their prerequisites. The full program title is authentic official wording; curriculum status remains partial because some policy and prerequisite details are not extracted.

Integration with the completed CLI succeeded in an isolated temporary database: init, ingestion (11 records at this checkpoint), static build (11 program pages; 174 institutions), and SQLite/requirement checks all passed. Generated Denison and Furman HTML contains the correct titles, course/evidence tables, and limitations. After an initial sandbox launch failure, an approved local Chromium run rendered both program pages at 1440px and 390px widths. Headings, base-path asset loading, reloads, document overflow and browser error checks passed. Desktop screenshots were visually inspected: no clipping or layout defect found. Screenshots are temporary at /tmp/denison-mlai-minor.png and /tmp/furman-ai-bs.png. The final isolated build after concurrent records landed contained 83 programs and 174 institutions.

## Expanded roster screening

Fourteen newly verified cohort institutions were screened through their official undergraduate directories on 2026-10-10, bringing the loaded subset to 80 rows (73 preliminary inspections, 2 confirmed titles and 5 inaccessible). No additional qualifying award was confirmed. Allegheny’s [Artificial Intelligence Engineering](https://allegheny.edu/academics/majors-minors/artificial-intelligence-engineering/) is explicitly a **microcredential**, excluded from the present award scope. Randolph-Macon’s directory includes AI as search keywords for other programs; those keywords are not an AI-titled program. Full catalog and concentration review remains unfinished for all preliminary inspections.
