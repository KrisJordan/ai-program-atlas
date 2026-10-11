# Liberal arts discovery depth pass, batch 4 — 2026-10-11

Ten claimed institutions received a bounded follow-up, recorded as **39 official-source observations or access attempts** in the [batch 4 survey](../data/surveys/liberal-depth-batch4-2026-10-11.json). All retain `inspected`; zero qualifying awards were verified and zero institution-wide absence conclusions were made. Eight received additional program-level evidence. Swarthmore's attempt was blocked, while Richmond yielded a college overview but no program-list records; these two remain a separate unresolved-depth bucket. No ranking or cohort fact changed.

| Institution | Evidence and decision |
| --- | --- |
| Swarthmore | Academics and the historically readable CS about route returned robot verification. No new academic content read; historical inspected evidence retained. |
| USAFA | Official directory and AY2026–2027 handbook contents/selected computing sections. CompSci 471 is coursework within broader majors. |
| Washington and Lee | Program directory and CS degree links; linked BA/BS catalog pages returned 403. Formal concentration detail remains unresolved. |
| Richmond | Undergraduate college overview names BSBA majors and mentions concentrations. Program finder returned no records; CS/Robins sites timed out. Deeper review unresolved. |
| Bucknell | 2026–2027 Arts and Sciences/Engineering CS program and course sections. AI/ML coursework and research do not establish a separate award. |
| Franklin & Marshall | AI and the Liberal Arts is explicitly a certificate; excluded from requested scope. CS/Cognitive Science context does not change that type. |
| Union | AI in Business is the Rochester Simon MS portion of a 4+1 pathway. Undergraduate CS page has research interests and unloaded requirement blocks. |
| Connecticut College | CS major and department research reviewed; program finder did not expose records and the catalog course-list link failed retrieval. |
| Sewanee | 2026–2027 catalog names CS/Data Science majors/minors. CSCI 356 is an AI elective. |
| Centre | 2026–2027 program index, CS/DS department sections and Data Science major; linked CS major response instead showed 2025–2026. AI/ML course options are not AI credentials. |

## Evidence and access boundaries

[F&M's certificate overview](https://www.fandm.edu/centers-institutes-and-initiatives/certificates/) explicitly defines the AI offering as a certificate. [Union's pathway page](https://www.union.edu/admissions/business-masters-pathway) explicitly assigns the AI in Business award to a partner master's program. Neither was promoted to an undergraduate degree, minor or formal concentration.

[USAFA's handbook](https://www.usafa.edu/app/uploads/COI.pdf), [Bucknell's catalog](https://coursecatalog.bucknell.edu/collegeofengineeringcurricula/areasofstudy/computersciencecsci/) and [Sewanee's catalog](https://e-catalog.sewanee.edu/arts-sciences/departments-interdisciplinary-programs/mathematics-computer-science/) state 2026–2027. USAFA review was limited to contents and selected computing sections; its full 492-page handbook was not audited. A screenshot call for the CS page was made; no whole-catalog image review is claimed.

Centre's rolling catalog URL returned inconsistent visible editions: [program index](https://centre.smartcatalogiq.com/en/catalog-and-handbooks/catalog/programs-of-study) and [Data Science major](https://centre.smartcatalogiq.com/en/catalog-and-handbooks/catalog/programs-of-study/data-science/data-science-major) showed 2026–2027, while the [CS major](https://centre.smartcatalogiq.com/en/catalog-and-handbooks/catalog/programs-of-study/computer-science/computer-science-major) response showed 2025–2026. No current CS-requirement claim is based on the older response.

Swarthmore's robot challenge and Washington and Lee's 403 pages were not bypassed. Richmond timeouts and empty rendered program lists are distinguished from HTTP denial. F&M, Union and Connecticut's linked catalog failures are retrieval limitations, not proof of missing credentials. Existing successful inspection history is preserved where newer attempts failed. Broader announcement archives and internal pathways remain incompletely examined. Unrelated keyword-search results were discarded, never used as negative evidence.

## Exact finite loaded-LAC queue

Snapshot at this batch's authoring: **86 loaded LAC institutions**; this is not certification of the full U.S. News top-100 cohort. Partition: **48 bounded depth records with readable program evidence**, **2 unresolved-depth attempts** (Swarthmore and Richmond), **28 ordinary shallow records**, **1 earlier bounded HWS pass**, **4 known-program institutions**, and **3 previously inaccessible institutions**. These disjoint buckets total 86. A depth record is not a complete survey or an absence finding.

The prior 40 bounded records remain documented in [batch 3](survey-liberal-depth-batch3-2026-10-11.md); this batch adds eight readable program-level inspections. Swarthmore and Richmond are explicitly not counted as successful deeper directory reviews. Washington and Lee, Union and Connecticut have useful readable content but retain the particular catalog limits above.

### Claimed by the liberal-arts agent (10; not counted complete here)

- `gettysburg-college`
- `wheaton-college-illinois`
- `thomas-aquinas-college`
- `lawrence-university`
- `saint-anselm-college`
- `rollins-college`
- `earlham-college`
- `lewis-and-clark-college`
- `whittier-college`
- `hendrix-college`

Their planned survey is `liberal-depth-supplement2-2026-10-11.json`. Reconcile its committed evidence before counting it complete.

### Unclaimed ordinary queue (18, roster order)

1. `beloit-college`
2. `muhlenberg-college`
3. `berea-college`
4. `hope-college`
5. `saint-marys-college-indiana`
6. `allegheny-college`
7. `lycoming-college`
8. `college-of-saint-benedict`
9. `saint-johns-university-minnesota`
10. `kalamazoo-college`
11. `morehouse-college`
12. `randolph-macon-college`
13. `augustana-college-illinois`
14. `juniata-college`
15. `southwestern-university`
16. `stonehill-college`
17. `college-of-wooster`
18. `washington-college`

### Separate follow-up buckets

- Unresolved new depth attempts: `swarthmore-college` (robot verification; stop route), `university-of-richmond` (dynamic program list and timeouts; ordinary permitted rendering or future public catalog evidence needed).
- Prior bounded HWS pass: `hobart-and-william-smith-colleges`; see `hws.json` for its exact remaining scope.
- Existing qualifying programs: `denison-university`, `furman-university`, `lake-forest-college`, `ursinus-college`. Program maintenance remains distinct from exhaustive institution discovery.
- Previously inaccessible: `united-states-naval-academy`, `united-states-military-academy`, `colby-college`. No denied route was retried.

To maintain the queue, begin with LAC IDs in `data/cohort.json`, subtract the explicit reviewed sets, known-program and inaccessible buckets, and reconcile every new survey's scope rather than treating filename presence as completed depth. A later accessible source can resolve a blocked bucket; elapsed time alone cannot. The original 86-institution roster remains unchanged.

## Validation

116 targeted core/discovery tests passed. Fresh temporary full-data ingest preserved all ten notes; repeat ingest changed zero programs and retained all 258 coverage events. SQLite integrity and foreign-key checks and a temporary static build passed. No maintained database, core, PLAN or site source is edited by this batch.
