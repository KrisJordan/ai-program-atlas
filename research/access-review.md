# Bounded inaccessible-source review

Reviewed 2026-10-10. This batch revisited the 17 institutions whose latest survey status was inaccessible. It confirms nine additional program identities across five institutions, moves four other institutions to **inspected**, and leaves eight inaccessible rows unchanged. None of these observations establishes institution-wide absence. All nine program inventories remain **pending**: the source pages were actually inspected, but the complete requirements and course metadata have not been mapped. The rerunnable identity adapters do not emit curriculum data or verification timestamps.

The exact program URLs and parent-degree distinctions are recorded in [the discovery manifest](access-review-discoveries.json), program source metadata and adjacent adapter notes. Local official-source replay passed for all nine adapters. Raw HTML stays in ignored cache or `/tmp`; synthetic fixtures are committed.

## Successful source inspections

| Institution | Result and evidence boundary |
| --- | --- |
| MIT | Official [degree charts](https://catalog.mit.edu/degree-charts/) links the readable [AI and Decision Making BS](https://catalog.mit.edu/degree-charts/artifical-intelligence-decision-making-course-6-4/). The canonical path intentionally spells `artifical`; the older correctly spelled candidate returned 404. The degreewide and departmental tables are readable and await extraction. |
| NC State | The [CS department catalog](https://catalog.ncsu.edu/undergraduate/engineering/computer-science/) links the current [AI concentration](https://catalog.ncsu.edu/undergraduate/engineering/computer-science/artificial-intelligence-concentration/), within Computer Science BS. Earlier candidate route returned 404. Current 2026–2027 requirements and elective pools await extraction. |
| Villanova | The official [VSB degree directory](https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html) and live catalog establish Analytics & AI minor/co-major and AI/ML minor. Analytics title applies to Class of 2029 and beyond; this is not treated as a launch date. The co-major is within a BBA and requires another primary major. The production catalog was verified independently; an incidental marketing link to a test catalog was not used. Eligibility, substitution and overlap rules still need mapping. |
| UVA | The official [engineering BSCS page](https://engineering.virginia.edu/department/computer-science/academics/undergraduate-programs/bs-computer-science), read through the web reader, links the university's [CS advising site](https://uvacsadvising.org/ai-concentration.html). Its BSCS and BACS sections establish two distinct formal AI concentrations effective Fall 2026, with different choice rules. This does not promote the older informal AI focal path. The advising page is readable through the default fetcher. |
| Tufts | Official [AI institute undergraduate directory](https://ai.tufts.edu/ai-tufts/programs-and-courses) links [Application of AI](https://engineering.tufts.edu/cs/current-students/undergraduate/minor-application-ai) and [AI Development](https://engineering.tufts.edu/cs/current-students/undergraduate/minor-ai-development) minors. Both department pages say available beginning Fall 2026. They specify different eligibility and course inventories, which await extraction. Enrollment is not independently confirmed; records preserve announced status. The old career-article 429 does not imply institution-wide inaccessibility. |
| Pittsburgh | [SCI undergraduate overview](https://www.sci.pitt.edu/academics/undergraduate) and the linked [degree finder](https://www.academics.pitt.edu/degree-finder-view) are readable. The finder is paginated; inspected first-page results do not constitute an exhaustive inventory. |
| Princeton | The official [Computer Science undergraduate announcement](https://ua.princeton.edu/fields-study/departmental-majors-degree-bachelor-arts/computer-science) was readable through the web reader, although the local fetcher returned 403. The inspected 2026–2027 page covers AB/BSE/CS minor and AI/ML courses; this departmental inspection does not establish absence elsewhere. No blocked local transport was bypassed. |
| Swarthmore | [About Computer Science](https://www.cs.swarthmore.edu/program/about.html) is readable and describes major/minor/honors. This narrow departmental overview is not a complete institutional credential survey. |
| Richmond | The [undergraduate catalog overview](https://catalog.richmond.edu/ug) is readable and identifies undergraduate colleges and academic schools. Program-level inventory still needs inspection. |

## Unresolved access results

These rows remain inaccessible; older evidence is preserved. Restrictions were not bypassed.

| Institution | Current attempt |
| --- | --- |
| UConn | `https://catalog.uconn.edu/undergraduate/programs/`: robots preflight returned HTTP 202. |
| Brandeis | `https://www.brandeis.edu/computer-science/undergraduate/index.html`: robots preflight HTTP 403. |
| Syracuse | Existing catalog AI program candidate: robots preflight HTTP 202. |
| Baylor | Existing catalog data-science/minor candidate: robots preflight HTTP 202. |
| Chicago | `https://collegecatalog.uchicago.edu/thecollege/computerscience/`: connection error at robots preflight; no insecure TLS retry. |
| U.S. Naval Academy | `https://www.usna.edu/Academics/Majors-and-Courses/`: web reader HTTP 403. |
| U.S. Military Academy | `https://www.westpoint.edu/academics/majors-and-minors`: web reader HTTP 403. |
| Colby | `https://www.colby.edu/academics/`: robots preflight HTTP 403. |

Remaining work: map each newly identified program's requirements and policy constraints, add course metadata separately, complete the partially inspected institution inventories, and revisit access failures only through permitted official channels. This batch does not resolve the larger roster's incomplete primary ranking enumeration.
