# Liberal arts discovery depth pass — 2026-10-11

This bounded pass deepens ten existing `inspected` records. It verifies **zero new qualifying awards** and makes **zero institution-wide absence conclusions**. All ten remain `inspected`. It does not change ranking evidence, cohort membership, program records or requirement graphs.

The [dated survey](../data/surveys/liberal-depth-2026-10-11.json) supplies each institution's exact source URLs, observation date, locators, findings and remaining scope. The earlier `liberal.json` observations remain historical evidence. New observations are dated 2026-10-11; ingest chooses later evidence by date even when filenames sort before the original survey.

## Scope and findings

The selected institutions were Williams, Amherst, Bowdoin, Claremont McKenna, Pomona, Wellesley, Vassar, Hamilton, Wesleyan and Carleton. Each previously had only a directory/department-level inspection. The work followed official catalog/program links and read accessible relevant requirements, with bounded official AI/academic search and follow-up on readable leads. It did not survey every department's internal tracks or every announcement archive.

| Institution | Additional evidence inspected | Decision and remaining scope |
| --- | --- | --- |
| Williams | [2026-27 program index](https://catalog.williams.edu/2627/), [CS catalog PDF](https://catalog.williams.edu/pdf/csci.pdf), [Cognitive Science PDF](https://catalog.williams.edu/pdf/cogs.pdf) | AI is a CS breadth category; Cognitive Science is the formal concentration. The CS text also describes informal nonmajor study, which is not a named AI award. Other internal tracks and announcements remain unreviewed. |
| Amherst | [2026-27 catalog](https://www.amherst.edu/academiclife/college-catalog/2627), linked CS major and departmental/interdisciplinary major rules | A CS AI course is not a separate credential. Individually proposed interdisciplinary majors need approval; the general approval mechanism does not establish a standing AI title. Other departmental tracks and individual approvals remain outside this pass. |
| Bowdoin | [2026-27 program catalog](https://bowdoin-public.courseleaf.com/departments-programs/), CS and Digital and Computational Studies requirements, [Hastings announcement](https://www.bowdoin.edu/news/2026/07/harnessing-ai-for-the-common-good.html) | CS requires an AI elective category; DCS has a coordinate major/minor and AI course options. Hastings Summer Fellows undertake eight-week projects. These do not verify an AI-titled degree, minor or concentration. Other departments/announcements remain unreviewed. |
| Claremont McKenna | [Departments, majors and programs](https://www.cmc.edu/academic/departments-majors-programs), including CS/Data Science sequences, Integrated Sciences focus areas and Financial Economics | None of the reviewed titles is AI. A sequence appearing on a transcript does not make it an AI sequence. Catalog-host challenge paths were not retried; internal tracks and cross-campus approvals remain unverified. |
| Pomona | [Major/minor index](https://catalog.pomona.edu/majorsminors) and linked CS and Linguistics/Cognitive Science catalog overviews | The index is readable; department overview responses expose navigation only. Internal concentrations, requirements and announcements remain unreviewed. This response limitation is not an institutional absence finding. |
| Wellesley | [Program catalog](https://catalog.wellesley.edu/index.php?view=programs), CS major requirements, Cognitive and Linguistic Sciences options, [AI and the Liberal Arts](https://www.wellesley.edu/academics/ai-and-the-liberal-arts) | Cognitive-science concentrations are psychology, linguistics, CS and philosophy. Upskill: AI is a one-week January 2026 experiential offering. It is excluded from degree/minor/concentration inventory. Other tracks remain unreviewed. |
| Vassar | [Major/correlate index](https://www.vassar.edu/academics/majors), CS and Cognitive Science departments | AI is discussed within teaching/program topics. Detailed current catalog review stopped at HTTP 403. Formal internal tracks and broader announcements remain unreviewed. |
| Hamilton | [Areas of study](https://www.hamilton.edu/academics/areas-of-study) and current CS/Data Science catalog requirements | Here “concentration” means a major; reviewed named concentrations are CS and Data Science. AI/ML options do not create an AI concentration. Business is preprofessional advising. Other internal tracks remain unreviewed. |
| Wesleyan | [2026-27 majors](https://catalog.wesleyan.edu/majors/), [minors](https://catalog.wesleyan.edu/minors/), CS requirements and areas of study | No qualifying AI title verified in reviewed scope. Informatics and Modeling is listed as a minor, while CS prose uses certificate wording; no credential reconciliation inferred. Other internal tracks/certificates remain unreviewed. |
| Carleton | [Academic index](https://www.carleton.edu/academics/), CS and Cognitive Science major/minor pages | AI topic/research mentions do not verify a separately named award. Registrar catalog review stopped at browser verification. Detailed formal tracks and announcements remain unreviewed. |

## Access and edition boundaries

- Vassar's `https://catalogue.vassar.edu/` returned HTTP 403. No retry through protected variants, proxy, cache bypass or authenticated access.
- Carleton's linked `https://apps.carleton.edu/campus/registrar/catalog/` presented browser verification/reCAPTCHA. No challenge solving or alternative protected path.
- Known CMC catalog-host challenges were not revisited. The public institutional program directory was independently readable.
- Pomona's linked catalog overviews (`PCSC/overview` and `PLCS/overview`) returned navigation without substantive department text in the reader. This is recorded as unreadable content, not HTTP denial.
- A linked Wellesley Cognitive and Linguistic Sciences catalog endpoint returned 502; the official program description remained readable. Its CS catalog major page was readable. No inference is drawn from the failed endpoint.
- Williams, Amherst, Bowdoin and Wesleyan sources explicitly display 2026-27. Hamilton's `current` endpoint and the other undated live directories are observed as current public sources on the check date, without an invented catalog year.
- Bowdoin's 2026-27 directory says major/minor requirements apply to students matriculating in 2024-25. This mixed applicability wording is preserved as a caveat; no student's applicable curriculum is inferred from the masthead.

## Validation

The survey uses the existing coverage schema and only loaded cohort IDs. Temporary-database ingest verifies that all ten newer notes survive sorted loading of the older ledger, repeat ingest creates no duplicate coverage events, integrity checks pass, and static build succeeds. No production database is modified. Existing core/discovery tests are run for regression coverage; this factual-only survey does not add tautological tests for copied observations.

Validation result: 109 focused core/discovery tests passed; full available suite passed **1,188 tests**, with 17 browser tests skipped by the default local invocation (no frontend behavior changed). A fresh temporary database retained all ten dated notes after full sorted ingestion; repeated ingest changed zero programs and left coverage-event count unchanged. SQLite integrity/foreign-key checks and the static build passed. The maintained database was not touched.
