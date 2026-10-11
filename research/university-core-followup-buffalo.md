# Buffalo university core follow-up — 2026-10-11

New advising and governance leads leave fixed core judgments at **seven unverified and one partial (Economics)**. No core status was promoted. Whole-degree reviews remain blocked, separately from these bounded dimensions. No program JSON, adapter logic, shared ledger, compiled data or maintained database changed.

## New evidence and limits

The [April 15, 2025 senate minutes](https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_709701498/file.res/FS%204_15_25%20minutes.pdf) (pp. 3–4) explicitly distinguish the department-formation vote from later curriculum approval. They describe an AI-and-ethics course as mandatory across AI+X curricula, but give neither its exact title/code nor applicability to a current cohort. The capture SHA256 is `beda30653d47dbe7051064f32f4b37ad63bf28a78c3735c9ef9331374f890b1f`. This improves the obligation evidence without establishing exact course membership.

Political Science’s public course page independently names “203: AI and Democracy”; field grouping and semester availability do not make it mandatory for Policy Analysis. Advising pages expose contacts and registration guidance, not a binding AI BS course plan. The 2024–25 Senate archive yielded six readable minutes PDFs; two exceeded the unchanged five-megabyte transport bound. Both were later selectively read in the ordinary public Chrome PDF viewer without enlarging the transport limit. Two agenda PDFs yielded public attachment leads; the Background and FAQs target returned UB credential login. Other same-origin attachments were not requested, and no login, alternate download endpoint or API bypass was attempted.

## Proposed core-review rows

The JSON `programs` array contains eight full replacement proposals with current resolved-fact hashes, exact mapped expectations and historical ethics evidence. Economics retains 19 fixed/16 option uncoded titles and choose 1/2/4 rules. Seven siblings retain no mapped exact major sets; zero is graph coverage, not absent requirements. The earlier eight program-specific captures are labeled reused, not fresh reads.

| Program | Fixed status | Resolved-fact SHA256 |
| --- | --- | --- |
| university-at-buffalo-suny-ai-and-geospatial-analytics-bs-degree | unverified | `5bd640ec12c56ff8235b076b352d725fa4b490d5ef9fb0c93abb3d31f51584f8` |
| university-at-buffalo-suny-ai-and-language-and-intercultural-competence-bs-degree | unverified | `c0a40e58f8a7977f8c2b0e30dc96e8fdcb7c681531b40aa0631463797d92b308` |
| university-at-buffalo-suny-ai-and-language-technology-bs-degree | unverified | `45f3cabc3b8936bb460499a599a58a7bb757af04f39d3e1722d564237a7a500e` |
| university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree | unverified | `2bb865ff7db10b698f1c1d47fd38d93eb29b36bdcee958d11618d14361a0ba6d` |
| university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree | unverified | `4ed764ff460cc75f22c50dca96e537a9c84708f9067922314663e47f03898c73` |
| university-at-buffalo-suny-ai-and-policy-analysis-bs-degree | unverified | `f4216e02de00853316f98b6347e271109fe897ef1371388d41e3c6f0ebfc88d8` |
| university-at-buffalo-suny-ai-and-quantitative-economics-bs-degree | partial | `d3282379a23acbb1794f7cbddfa3d788401c213014770c3b0ffa2c047c499ce4` |
| university-at-buffalo-suny-ai-and-responsible-communication-bs-degree | unverified | `5769fe367961c37bd4b3f99b58d958ece761f1770aa5ac0a1e093560643ec538` |

## Exact new source attempts

Dates, raw-body locators, hashes and outcomes are in JSON `source_attempts`. First sandbox attempts failed at robots connectivity before source reads; authorized ordinary guarded reads then succeeded. Two unlinked candidate paths returned 404 and were not repeated. A 200 login response is protected, not readable curriculum.

| URL | Outcome | Hash or boundary |
| --- | --- | --- |
| https://www.buffalo.edu/cas/communication/undergraduate/advisement.html | fetch_error | Transport failure: https://www.buffalo.edu/robots.txt: ConnectError |
| https://www.buffalo.edu/facultysenate.html | fetch_error | Transport failure: https://www.buffalo.edu/robots.txt: ConnectError |
| https://www.buffalo.edu/cas/communication/undergraduate/advisement.html | guarded_fetch_200 | `84bb78d5482efd472ebf5077996c8f77870121007a7fb13a3f2576d20434e7e6` |
| https://www.buffalo.edu/facultysenate.html | guarded_fetch_200 | `1b4e4e9928aaf262fdb23115abd086edced3927e8d1a0b9c2aa767789a316b95` |
| https://arts-sciences.buffalo.edu/advising.html | guarded_fetch_200 | `3d2921efee11faeff36d1d22529dcbb0fbf41e66387d58dece9a7edecf9f7265` |
| https://www.buffalo.edu/facultysenate/meetings.html | guarded_fetch_200 | `3aebc5cb8de0df28402f42046e0449439ab273914a48fcefc9d0f62eebf1c52a` |
| https://arts-sciences.buffalo.edu/economics/info-for/current-students/undergraduate.html | guarded_fetch_200 | `c17bc4d7721f3ac96e1091727783fb8585954d0f322064cdc56140dd31ba6c94` |
| https://arts-sciences.buffalo.edu/linguistics/undergraduate/overview.html | guarded_fetch_200 | `26cac40b5cb78481d0270974977da4439eea10ea2cf0d02db24ef5443ae48914` |
| https://www.buffalo.edu/cas/philosophy/undergraduate/overview.html | guarded_fetch_200 | `5d978afd693f496d4a750311e865a967ec131d91e493a5a48ca773f551f5e479` |
| https://arts-sciences.buffalo.edu/philosophy-politics-economics/undergraduate/overview.html | guarded_fetch_200 | `d4e07914fb21a0b19ed9d1b0815398f40fd7e27a4f8383c037c08e755b8764da` |
| https://www.buffalo.edu/cas/geography/undergraduate/overview.html | guarded_fetch_200 | `19b99157e1508053da5fd08687bd7e5998b82ca1ba7bb84c0641b30fd5ce7026` |
| https://www.buffalo.edu/facultysenate/meetings/minutes.html | guarded_fetch_200 | `b168a60c950adcf6c8ac6e796b13faa29a433d97ff87e7d59884c0416bd5ce09` |
| https://www.buffalo.edu/facultysenate/meetings/agendas.html | guarded_fetch_200 | `ed1b1556c8d1ecac644a815921e00cce9b31e006bf93648c86615463583ca7fb` |
| https://arts-sciences.buffalo.edu/advising/academics/find-degree.html | guarded_fetch_200 | `b08b4926c974ea89a323748e642dd0c34a21ef3960f740fff743e2265280ced4` |
| https://arts-sciences.buffalo.edu/advising/current-students.html | guarded_fetch_200 | `af6eb6cfa240ccf592b12370da67d4b6d18707e494cf938304c8026b1d62538c` |
| https://arts-sciences.buffalo.edu/political-science/undergraduate/courses.html | guarded_fetch_200 | `bb3a6793d8ca88e4f18043bde80909441a3851995199ac66db1a763317103e26` |
| https://www.buffalo.edu/facultysenate/meetings/minutes/faculty-senate.html | guarded_fetch_200 | `8b1952d7c80b9905b3b9cf832b9d8cabd54384cbfae4dda35c78b2f83bcdc5ce` |
| https://www.buffalo.edu/facultysenate/meetings/minutes/faculty-senate-executive-committee-minutes.html | guarded_fetch_200 | `18665d9810421ea02e02ddcb7fbd425381de632510ca26aa3f35c3c1a54b10d3` |
| https://www.buffalo.edu/facultysenate/meetings/agendas/archive.html | guarded_fetch_200 | `cd260f52f7a4b524f2ebdf0053ee009a052d22a8ff0e76d33903b553be6dc8d3` |
| https://arts-sciences.buffalo.edu/political-science/info-for/current-students.html | fetch_error | HTTP 404: https://arts-sciences.buffalo.edu/political-science/info-for/current-students.html; no access bypass attempted |
| https://www.buffalo.edu/facultysenate/meetings/presentations.html | fetch_error | HTTP 404: https://www.buffalo.edu/facultysenate/meetings/presentations.html; no access bypass attempted |
| https://www.buffalo.edu/facultysenate/meetings/presentation.html | guarded_fetch_200 | `2f49245b6bb6b18fb0d53a70e723f6a25662890a0ca346fcd3f3e9bbd31e9f06` |
| https://buffalo.box.com/s/lorm43tv7unsf0sb7mo823j4rnqwtpi2 | protected_login_200 | `3f0051eacd30659ad8c233b5e438c951ec941d4a767b3a2f875c2db4b08eea19` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_1009900620/file.res/fs-9-17-24-minutes.pdf | fetch_error | Response exceeds 5000000 bytes: https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_1009900620/file.res/fs-9-17-24-minutes.pdf |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_363966534/file.res/fs-10-22-24-minutes.pdf | guarded_fetch_200_pdf | `705c262ea975052d087f694d2b96397604cb4583656531ddbc77a0c353f6d901` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_538299425/file.res/FS-11-19-24%20minutes.pdf | fetch_error | Response exceeds 5000000 bytes: https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_538299425/file.res/FS-11-19-24%20minutes.pdf |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_1713769732/file.res/fs%2012_17_24%20minutes.pdf | guarded_fetch_200_pdf | `07fec1e96d88beff627aefff642770ab68545bb76df0e921eb8331279e05c5fe` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_241264295/file.res/fs%202_18_25%20minutes.pdf | guarded_fetch_200_pdf | `77905fc7680a892742fd722910cdbb7a504a4bd610eb5a16fa5ac8d8cf97bad9` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_1385449641/file.res/fs%203_25_25%20minutes.pdf | guarded_fetch_200_pdf | `c154b59cf10e79713c92db11d96480eb45e0d9981b7a308df003d063168ca785` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_709701498/file.res/FS%204_15_25%20minutes.pdf | guarded_fetch_200_pdf | `beda30653d47dbe7051064f32f4b37ad63bf28a78c3735c9ef9331374f890b1f` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/minutes/faculty-senate/_jcr_content/root/maincontent/par/collapsible_935818726/container/download_170577090/file.res/FS%205_13_25%20Final%20Minutes.pdf | guarded_fetch_200_pdf | `8812e746b3c6f5a26ceec54021f4780e9fb79f1f22826b5811168d642abf5566` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/agendas/archive/_jcr_content/root/maincontent/par/collapsible_218948001/container/download_1748849766/file.res/FS%20Meeting%203-25-25_Draft%20Agenda%20%283%29.pdf | guarded_fetch_200_pdf | `719dc1c3d20f72592313b2491a656b2cf580885fdf06af21720be4d7969f3d40` |
| https://www.buffalo.edu/content/www/facultysenate/meetings/agendas/archive/_jcr_content/root/maincontent/par/collapsible_218948001/container/download_725357720/file.res/FS%20Meeting%204-15-25_Draft%20Agenda%20w%20links%28002%29.pdf | guarded_fetch_200_pdf | `0bafcce4077cdb97676316c81413897f66ca3f676ed0e77c25b4985412a495c0` |

## Remaining evidence

Seven majors need a binding current core inventory, approved alternatives and exact catalog/cohort applicability. Economics needs codes and applicability for its binding title inventory, plus actual content evidence for the unresolved classifications. The historical ethics statement does not resolve any of these. Full-degree policies, complete choices and university-context applicability remain separate blockers.

The finite 14-document 2024/2025 executive minutes queue is now closed by selective action-item and AI-related review. Seven readable captures have full-body SHA256 hashes; seven oversized PDFs were read in the ordinary public Chrome PDF viewer after the web PDF reader failed. The two oversized Senate PDFs were also selectively read there. Browser-only source hashes remain null. Known denied catalog routes and protected Box attachments were not retried. This is exhaustion of this identified queue, not evidence that no public plan exists elsewhere.

Validation: all eight proposal fingerprints and mapped profiles match current resolved program/family facts; readable source bodies were rehashed successfully. All 40 focused Buffalo regression tests passed; these software checks do not certify facts. No ingestion was required because canonical data did not change. Independent acceptance and publication remain with the coordinator.

## Completed executive-minutes continuation

The November 12 executive minutes (pp. 2–3) and November 19 Senate minutes (pp. 7–8) describe a proposal-stage AI department and future undergraduate curricular partnerships. They provide no exact approved required sets. October 29 (p. 2) tabled the AI education opportunity; February 25 (p. 3) discusses SUNY initiatives and a planned general education AI competency, which does not bind these major inventories. Neither finding supports a core-status promotion.

All 14 linked executive documents were selectively checked: September 10 and 24; October 8 and 29; November 12 and 26; December 10, 2024; January 28; February 11 and 25; March 11; April 8 and 22; May 6, 2025. JSON `executive_minutes_queue.document_results` records exact URLs, inspected pages, body hashes or honest nulls. `source_attempts` records each guarded fetch, failed ordinary web-reader attempt and successful browser review separately (65 total attempts across the full follow-up). No item in this finite queue remains unread; protected attachments remain inaccessible leads.
