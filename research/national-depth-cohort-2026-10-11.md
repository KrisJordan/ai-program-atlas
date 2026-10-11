# National University discovery depth — cohort research batch, 2026-10-11

Ten previously shallow inspected institutions received bounded official-source follow-up, recorded as **45 source observations/access attempts** in the [survey](../data/surveys/national-depth-cohort-2026-10-11.json). One new qualifying program was confirmed: **Yeshiva College’s Artificial Intelligence concentration within the CS BS**. Nine institutions retain `inspected`; no absence conclusions. No ranking/cohort evidence changed.

| Institution | Additional evidence and limit |
| --- | --- |
| Harvard | College concentration list, detailed CS routes and secondary requirements. AI is a course tag; other departments/special concentrations and announcements remain unreviewed. |
| WashU | 2026–2027 all-school major/minor lists, CS BS and Business/CS BS requirements. AI/ML are Methods options; Business Analytics is a differently titled concentration. Other internal options remain unreviewed. |
| Rutgers Newark | SASN major/minor lists, CS BA, Data Science minor, Newark business concentration taxonomy and MSIS requirements. Campus applicability explicit; other schools remain incomplete. |
| Mines | 2026–2027 CS BS with seven focus areas, including Robotics & Intelligent Systems. CSCI 404 AI is coursework; other departments remain incomplete. |
| Pepperdine | Selected 2026–2027 Seaver catalog program lists and CS/Data Science curricula. AI appears within Data Science. Marketing’s CS/Math BS label differs from current catalog CS BA; no broader catalog audit. |
| TCU | CS BS/minor department catalog and overview. Full course inventory not obtained; Business Analytics entry is graduate. Business suboptions remain incomplete. |
| Yeshiva | New AI concentration, 22 current-catalog course rows and one partial requirement group. Stern CS BA and Sy Syms taxonomy inspected separately. Local completion policies remain unreviewed. |
| Chapman | Fowler major/minor lists, CS overview and Argyros program taxonomy. Finder yielded no records and catalog failed retrieval. Collaborative Intelligence remains outside title scope. |
| Elon | Engineering & Computing program taxonomy and current 2026–2027 CS BS catalog reached through the new school’s links. Old catalog link failed; AI elective direction is not a formal AI award. |
| Saint Louis | 2026–2027 CS BS requires AI or ML coursework; AI Literacy is explicitly a microcredential. Graduate AI pathways remain excluded. |

## New program and reproducibility

The [Yeshiva catalog](https://yu.smartcatalogiq.com/en/current/university-catalog/undergraduate-programs/yeshiva-college/copy-of-computer-science-artificial-intelligence-bs) explicitly names an AI concentration within Computer Science BS and gives a 75-credit table. The [department](https://www.yu.edu/yeshiva-college/ug/computer-science) links this catalog and a [Spring 2026 guide](https://www.yu.edu/sites/default/files/inline-files/Complete-YC-CS-Guide-Spring-2026-v.3.0.5_0.pdf). The guide’s overview comparison says 74 credits, whereas its detailed AI plan and the catalog say 75. The discrepancy remains visible. These 22 courses include shared CS/math major requirements, not merely extra AI electives.

The [seed](../data/programs/yeshiva-cs-ai-concentration.json), [parser](../atlas/adapters/yeshiva-cs-ai-concentration/adapter.py) and [notes](../atlas/adapters/yeshiva-cs-ai-concentration/NOTES.md) were committed as `2a61b07`. The parser reads only the AI table, validates program/college scope, ignores navigation, and rejects ambiguous or changed structural rules. It extracts current table facts rather than replaying a reviewed seed. The ordinary robots-aware Fetcher returned HTTP200 and actual HTML replay passed. Raw material stays ignored. An initial sandbox DNS failure was resolved by approved network access; no publisher restriction was bypassed.

The concentration remains **partial**: declaration, grades/GPA, transfer/residence, overlap and other local completion conditions are unreviewed. All 22 individual course descriptions/prerequisites remain accessible follow-up work. Published numbers retain unknown normalized credit units. The rolling catalog has no visible edition year; launch and assessed program learning outcomes remain unknown. Two concise overview summaries are typed as program aim and career pathway. The record neither certifies the complete host BS nor assigns the concentration to Stern College.

## Boundaries and source interpretation

[Harvard’s CS requirements](https://csadvising.seas.harvard.edu/concentration/requirements/) use AI as a course tag within Basic/Honors/Joint/MBB requirements; [secondary rules](https://csadvising.seas.harvard.edu/secondary/) also use tags. A course-tag label does not establish an AI concentration. [Mines](https://catalog.mines.edu/undergraduate/academics/degrees/bsincomputerscience/) names seven focus areas, including Robotics & Intelligent Systems; that title is not changed to AI. [SLU](https://catalog.slu.edu/colleges-schools/science-engineering/computer-science/ai-literacy-micro/) explicitly identifies its AI Literacy credential as a microcredential.

[Pepperdine’s 2026–2027 PDF](https://seaver.pepperdine.edu/academics/content/seaver-catalog-2026-2027.pdf) was reviewed only at named program-list and computing/data-science sections; no whole-510-page audit. Its current CS BA label differs from the marketing directory’s CS/Mathematics BS entry. No degree record was invented to reconcile that difference. The current catalog’s Data Science AI content does not change its award title.

Elon’s older directory link failed, but normal navigation through its current school program page reached the [2026–2027 CS BS catalog](https://elon.smartcatalogiq.com/en/2026-2027/academic-catalog/academic-programs/school-of-engineering-and-computing/computer-science/computer-science-bs). TCU’s program-search limitation and Chapman’s catalog reader error are retrieval limits, not proven access denial and not negative program evidence. No known denied route was retried. Search queries returned unrelated results and were discarded. Broader institutional announcement archives remain incompletely reviewed for all nine inspected institutions.

## Ownership and finite work queue

This batch owns exactly `harvard-university`, `washington-university-in-st-louis`, `rutgers-university-newark`, `colorado-school-of-mines`, `pepperdine-university`, `texas-christian-university`, `yeshiva-university`, `chapman-university`, `elon-university`, and `saint-louis-university`. Existing NYU/Yale/Dartmouth and national supplement work was not duplicated. Root’s Caltech/Binghamton/UCLA/UCR, frontend’s American/Creighton/Fordham/USD/Rutgers-Camden, and national’s FSU/UMass/RPI/SMU/UIC work were excluded. Root subsequently claimed Princeton, Georgetown, UT Austin, Wisconsin-Madison and Wake Forest; these are not counted as completed here.

Separately, the [final LAC supplement](liberal-depth-supplement3-2026-10-11.md), committed `ab38e4d`, finishes the ordinary loaded-LAC depth queue. Its exact discovery-work partition is now **75 readable bounded-depth records + 3 unresolved-depth attempts + 0 ordinary unreviewed + 1 earlier HWS pass + 4 pre-existing program institutions + 3 previously inaccessible = 86**. The new Lewis & Clark minor belongs within the 75 and must not be counted again among the four pre-existing program institutions. These work categories are not coverage-status totals; bounded depth is not exhaustive discovery and the intended U.S. News cohort remains incomplete.

## Validation

128 focused parser/core/discovery tests passed, including actual cached Yeshiva replay. Fresh temporary full-data ingest preserved all ten statuses/notes; repeat ingest changed zero programs and retained all 296 coverage events. SQLite integrity/foreign-key checks and temporary static build passed. No maintained database, core, PLAN or site source edited.
