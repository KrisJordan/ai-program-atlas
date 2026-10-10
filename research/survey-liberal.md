# National Liberal Arts Colleges: preliminary official-source survey

Checked 2026-10-10. This report covers the **66 verified cohort rows currently available in `data/cohort.json`**, not the full intended rank-at-most-100 population. Ranking membership remains incomplete; these counts are not a complete-population denominator.

## Findings

Two qualifying official undergraduate titles were found:

| Institution | Official title | Award | Evidence and limits |
|---|---|---|---|
| Denison University | Machine Learning and Artificial Intelligence | Minor | [Official requirements](https://denison.edu/academics/machine-learning-and-artificial-intelligence/degree-requirements) and [2026–2027 courses](https://denison.edu/academics/machine-learning-and-artificial-intelligence/courses) read. Eight required courses; five ML course credits documented. Three cognate credits, credit-unit normalization and several prerequisite expressions remain incomplete. First-offered date unknown. |
| Furman University | Artificial Intelligence | BS major | [Public official directory](https://www.furman.edu/academics/majors-minors-programs/) explicitly lists the title, BS award and undergraduate level. The linked [detail page](https://www.furman.edu/academics/majors-minors-programs/artificial-intelligence-major/) is password protected. Availability, launch date and curriculum unknown; overall record is partial. |

The directory listing is sufficient to confirm Furman's title, but is **not** evidence that students can presently enroll. Its program activity status is deliberately `unknown`.

## Coverage states

`data/surveys/liberal.json` records one row per currently verified LAC cohort institution, each with the attempted official URL, date and scope note:

- 2 `confirmed`: official qualifying title read.
- 53 `inspected`: an official academic overview or directory was opened for preliminary reconnaissance. These are **unfinished** catalog reviews, not no-program determinations.
- 5 `inaccessible`: robot verification (Swarthmore), HTTP 403 (Naval and Military academies), inaccessible consent redirect (Richmond), or zero readable academic-page content (Colby).
- 6 `pending`: attempted directory paths failed, without enough evidence to characterize institution-wide accessibility (Franklin & Marshall, Union, Connecticut, Centre, Saint Anselm and Whittier).
- 0 `no_qualifying_program_found`: no institution has been given an absence conclusion from keyword searches or incomplete department review.

General academics pages are explicitly only preliminary evidence. Degree/minor listings often omit internal concentrations, so a complete title survey needs relevant current catalogs and department requirements. Keyword discovery helped locate Denison but did not create any absence conclusions.

## Exclusions and false positives

- [Harvey Mudd AI Innovation](https://www.hmc.edu/ai/) describes research, labs and courses. Its [formal emphasis list](https://www.hmc.edu/academics/emphases/) lists Data Science and Environmental Analysis. No AI award is inferred from the initiative name; further catalog review remains pending.
- [Rollins Professional Advancement](https://www.rollins.edu/professional-advancement/degree-programs/) lists a Data Analytics with Artificial Intelligence **Certificate**. Certificates fall outside this project's degree/minor/concentration kinds. Other Rollins programs still need catalog review.
- Bucknell's official CS material mentions AI courses and topics. Courses and research interests do not establish a qualifying named concentration.
- Search results about another institution, graduate-only study, general AI policies, and AI research were not promoted to program records.

## Deliverables and remaining work

Reviewed program records are in `data/programs/denison-mlai-minor.json` and `data/programs/furman-ai-bs.json`. Each has an independent adapter under `atlas/adapters/` that reads the supplied HTML and rejects missing identity or required structural evidence. Neither replays a seed nor assigns a fresh verification timestamp. Adapter tests check changed observed courses, a missing degree type, and password-page rejection.

Remaining work: complete ranking membership; resolve six failed paths through legitimate public directories; revisit the five access failures without bypassing restrictions; conduct full current-catalog and concentration-level review of the 53 preliminary rows; obtain public Furman curriculum and availability evidence; complete Denison cognate credits, prerequisites, credit-unit normalization and launch provenance. No raw fetched catalog pages are committed.
