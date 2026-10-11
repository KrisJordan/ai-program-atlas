# Liberal arts discovery depth pass, batch 5 — 2026-10-11

Ten claimed institutions received a bounded follow-up, recorded as **42 source observations/access attempts at 37 distinct official URLs** in the [batch 5 survey](../data/surveys/liberal-depth-batch5-2026-10-11.json). Joint CSB/SJU sources were read once and attributed to both institutions only where their applicability was explicit. All ten retain `inspected`; zero additional qualifying awards and zero institution-wide absence conclusions. Nine gained readable program-level evidence. Beloit remains a separate unresolved-depth attempt because both linked program pages returned 403. No ranking, cohort membership or program curriculum changed.

| Institution | Additional evidence and remaining limit |
| --- | --- |
| Beloit | Named directory revisited. CS and Cognitive Science major pages returned 403; no deeper academic content read and no bypass. |
| Muhlenberg | CS overview identifies AI/ML electives and a separate graduate 4+1 pathway. Course blocks remained Loading, program finder exposed only filters, catalog returned 502. |
| Berea | 2026–2027 program directory and CS catalog taxonomy identify all four concentrations; general and CS concentration requirements inspected. Computational Intelligence is a course option. |
| Hope | CS BA, BS and minor named on degree overview. Requirements link loops to overview and catalog failed retrieval; internal formal tracks unresolved. |
| Saint Mary’s Indiana | 2026–2027 index, CS minor, Computing/Applied Mathematics BS and three Neuroscience concentrations reviewed. Other business options and announcements remain incomplete. |
| Allegheny | AI Engineering explicitly remains a microcredential, excluded from requested award scope. CS major/minor overview read; linked catalog failed retrieval. |
| Lycoming | Detailed Applied CS major, computing minors and course list reviewed. CPTR 340 AI is a course; visible catalog edition not established. |
| College of Saint Benedict | Explicit joint program taxonomy and acceptance-to-major criteria reviewed. Catalog supplied no readable academic body; full graduation curriculum remains unresolved. |
| Saint John’s Minnesota | Same independently applicable joint evidence as CSB, retained as a distinct institution; the same catalog limitation applies. |
| Kalamazoo | CS major/minor catalog requirements reviewed. Homepage’s PDF label is 2025–2026 despite an August 2026 update; current HTML edition unresolved. |

## Award and source distinctions

[Berea’s catalog](https://berea.smartcatalogiq.com/en/current/catalog/majors-and-minors/computer-science) names general, Computer Science, Computational Mathematics and Information Systems concentrations. [Its CS concentration requirements](https://berea.smartcatalogiq.com/en/current/catalog/majors-and-minors/computer-science/computer-science-optional-concentration) place CSC 410 Computational Intelligence among course choices. This is finite taxonomy evidence, not an exhaustive review of every institutional program or announcement.

[Allegheny’s AI Engineering page](https://allegheny.edu/academics/majors-minors/artificial-intelligence-engineering/) explicitly labels the offering a microcredential. The three-course structure does not change that credential type. [Muhlenberg’s CS page](https://www.muhlenberg.edu/program/computer-science/) distinguishes advanced electives and a graduate pathway from the undergraduate CS major. Neither produces a qualifying AI award in this batch.

[CSB/SJU’s CS page](https://www.csbsju.edu/computer-science/curriculum/computer-science-major/) and [Data Science curriculum](https://www.csbsju.edu/data-science/curriculum/) explicitly apply to both institutions, but their acceptance-to-major criteria are not full degree requirements. The Data Science page’s reference to establishment with the 2022–2023 catalog is not evidence of the current edition. No graduation inventory or launch-date fact was added.

Berea and Saint Mary’s responses explicitly state 2026–2027. Lycoming’s inspected catalog response did not establish its edition. [Kalamazoo’s catalog homepage](https://www.kzoo.edu/catalog/) labels a 2025–2026 PDF and has a later update date; neither justifies relabeling the reviewed HTML as 2026–2027. Undated marketing pages remain observations on 2026-10-11.

Beloit’s two 403 routes were stopped. Muhlenberg’s 502, Hope/Allegheny reader errors and CSB/SJU’s empty academic body are recorded separately from access denial. Berea’s stale course-list link failed before ordinary catalog navigation exposed the current program pages. A native in-app browser was unavailable for dynamic rendering; no rendered Muhlenberg program inventory is claimed. Unrelated keyword-search results were discarded, never treated as absence evidence. Broader announcements, individualized study and unreviewed departmental suboptions remain limits.

## Exact finite loaded-LAC queue

Snapshot after this batch and the committed [second supplement](liberal-depth-supplement2-2026-10-11.md), commit `78fcba4`: **86 loaded LAC institutions**. The disjoint discovery-work partition is **67 with readable bounded-depth evidence**, **3 unresolved-depth attempts**, **8 ordinary shallow records still assigned**, **1 earlier HWS pass**, **4 pre-existing program institutions maintained separately**, and **3 previously inaccessible institutions**. These total 86. The 67 readable-depth bucket includes the newly confirmed Lewis & Clark AI minor from the supplement; it must not also be counted in the four pre-existing program bucket. These are work-queue categories, not website coverage-status totals or certification of the full U.S. News cohort.

The 67 comprise the prior 40 documented in [batch 3](survey-liberal-depth-batch3-2026-10-11.md), eight from [batch 4](survey-liberal-depth-batch4-2026-10-11.md), ten from the second supplement, and nine here. A readable bounded-depth record is not exhaustive institution discovery. Programs such as Saint Anselm’s certificate remain outside award scope even when the overview is readable and the catalog is blocked.

### Final ordinary queue — claimed by the liberal-arts agent (8)

1. `morehouse-college`
2. `randolph-macon-college`
3. `augustana-college-illinois`
4. `juniata-college`
5. `southwestern-university`
6. `stonehill-college`
7. `college-of-wooster`
8. `washington-college`

No ordinary institution is unclaimed. This list remains pending until its evidence is committed and reconciled; assignment alone does not count as review.

### Separate follow-up buckets

- Unresolved depth: `swarthmore-college` (robot challenge), `university-of-richmond` (dynamic program list/timeouts), `beloit-college` (linked CS/Cognitive Science pages 403). No denied path should be retried or bypassed.
- Earlier bounded HWS pass: `hobart-and-william-smith-colleges`; exact scope remains in `data/surveys/hws.json`.
- Pre-existing program institutions: `denison-university`, `furman-university`, `lake-forest-college`, `ursinus-college`. Their maintenance does not certify exhaustive discovery.
- Previously inaccessible: `united-states-naval-academy`, `united-states-military-academy`, `colby-college`. No denied path retried.

For future queue updates, subtract explicitly recorded institution sets from the LAC roster and reconcile scope/access outcomes. Do not count a failed attempt as readable depth or a confirmed program twice. The roster denominator remains incomplete relative to the intended top-100-with-ties cohort.

## Validation

116 targeted core/discovery tests passed. Fresh temporary full-data ingest preserved all ten current notes; repeat ingest changed zero programs and retained all 278 coverage events. SQLite integrity and foreign-key checks and a temporary static build passed. Only the companion survey and this note are edited; no maintained database, core, PLAN or site source changes.
